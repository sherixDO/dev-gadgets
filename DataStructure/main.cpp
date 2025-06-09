#include <iostream>
using namespace std;

enum Color { RED, BLACK };

struct Node {
    int data;
    Color color; // 修改为使用Color枚举类型，确保类型一致性
    Node *left, *right, *parent;

    explicit Node(int data): data(data), color(RED), left(nullptr), right(nullptr), parent(nullptr) {}
};

class RBTree {
private:
    Node *root;

    void leftRotate(Node *x) { // 移除引用，因为我们不修改指针本身
        Node *y = x->right;
        x->right = y->left;
        if (y->left != nullptr)
            y->left->parent = x;

        y->parent = x->parent;

        if (x->parent == nullptr)
            root = y;
        else if (x == x->parent->left)
            x->parent->left = y;
        else
            x->parent->right = y;

        y->left = x;
        x->parent = y;
    }

    void rightRotate(Node *x) { // 移除引用，同上
        Node *y = x->left;
        x->left = y->right;
        if (y->right != nullptr)
            y->right->parent = x;

        y->parent = x->parent;

        if (x->parent == nullptr)
            root = y;
        else if (x == x->parent->right)
            x->parent->right = y;
        else
            x->parent->left = y;

        y->right = x;
        x->parent = y;
    }

    void transplant(Node *u, Node *v) {
        if (u->parent == nullptr)
            root = v;
        else if (u == u->parent->left)
            u->parent->left = v;
        else
            u->parent->right = v;

        if (v != nullptr)
            v->parent = u->parent;
    }

    Node* minimum(Node* x) {
        while (x->left != nullptr)
            x = x->left;
        return x;
    }

    void deleteFixup(Node *x) {
        Node *w;
        while (x != nullptr && x != root && getColor(x) == BLACK) {
            if (x->parent != nullptr && x == x->parent->left) {
                w = x->parent->right;
                if (w == nullptr) {
                    x = x->parent;
                    continue;
                }
                
                if (getColor(w) == RED) {
                    w->color = BLACK;
                    x->parent->color = RED;
                    leftRotate(x->parent);
                    w = x->parent->right;
                }

                if (w == nullptr) {
                    x = x->parent;
                    continue;
                }

                if (getColor(w->left) == BLACK && getColor(w->right) == BLACK) {
                    w->color = RED;
                    x = x->parent;
                } else {
                    if (getColor(w->right) == BLACK) {
                        if (w->left) w->left->color = BLACK;
                        w->color = RED;
                        rightRotate(w);
                        if (x->parent) w = x->parent->right;
                    }

                    if (w) {
                        w->color = x->parent->color;
                        if (x->parent) x->parent->color = BLACK;
                        if (w->right) w->right->color = BLACK;
                        leftRotate(x->parent);
                    }
                    x = root;
                }
            } else if (x->parent != nullptr) {
                w = x->parent->left;
                if (w == nullptr) {
                    x = x->parent;
                    continue;
                }
                
                if (getColor(w) == RED) {
                    w->color = BLACK;
                    x->parent->color = RED;
                    rightRotate(x->parent);
                    if (x->parent) w = x->parent->left;
                }

                if (w == nullptr) {
                    x = x->parent;
                    continue;
                }

                if (getColor(w->right) == BLACK && getColor(w->left) == BLACK) {
                    w->color = RED;
                    x = x->parent;
                } else {
                    if (getColor(w->left) == BLACK) {
                        if (w->right) w->right->color = BLACK;
                        w->color = RED;
                        leftRotate(w);
                        if (x->parent) w = x->parent->left;
                    }

                    if (w) {
                        w->color = x->parent->color;
                        if (x->parent) x->parent->color = BLACK;
                        if (w->left) w->left->color = BLACK;
                        rightRotate(x->parent);
                    }
                    x = root;
                }
            } else {
                x = nullptr;
            }
        }
        if (x) x->color = BLACK;
    }

    Color getColor(Node* node) {
        return node == nullptr ? BLACK : node->color;
    }

public:
    RBTree() : root(nullptr) {}

    void insertFixup(Node *z) {
        while (z != root && z->parent && z->parent->color == RED) {
            if (z->parent == z->parent->parent->left) {
                Node *y = z->parent->parent->right;
                if (y && getColor(y) == RED) {
                    z->parent->color = BLACK;
                    y->color = BLACK;
                    z->parent->parent->color = RED;
                    z = z->parent->parent;
                } else {
                    if (z == z->parent->right) {
                        z = z->parent;
                        leftRotate(z);
                    }
                    if (z->parent) {
                        z->parent->color = BLACK;
                        if (z->parent->parent) {
                            z->parent->parent->color = RED;
                            rightRotate(z->parent->parent);
                        }
                    }
                }
            } else {
                Node *y = z->parent->parent->left;
                if (y && getColor(y) == RED) {
                    z->parent->color = BLACK;
                    y->color = BLACK;
                    z->parent->parent->color = RED;
                    z = z->parent->parent;
                } else {
                    if (z == z->parent->left) {
                        z = z->parent;
                        rightRotate(z);
                    }
                    if (z->parent) {
                        z->parent->color = BLACK;
                        if (z->parent->parent) {
                            z->parent->parent->color = RED;
                            leftRotate(z->parent->parent);
                        }
                    }
                }
            }
        }
        root->color = BLACK;
    }

    void insert(int data) {
        Node *z = new Node(data);
        Node *y = nullptr;
        Node *x = root;

        while (x != nullptr) {
            y = x;
            if (z->data < x->data)
                x = x->left;
            else
                x = x->right;
        }

        z->parent = y;
        if (y == nullptr)
            root = z;
        else if (z->data < y->data)
            y->left = z;
        else
            y->right = z;

        insertFixup(z);
    }

    Node* search(int data) {
        Node *current = root;
        while (current != nullptr) {
            if (data == current->data)
                return current;
            else if (data < current->data)
                current = current->left;
            else
                current = current->right;
        }
        return nullptr;
    }

    void deleteNode(Node *z) {
        Node *y = z;
        Node *x;
        bool yOriginalColor = y->color;

        if (z->left == nullptr) {
            x = z->right;
            transplant(z, z->right);
        } else if (z->right == nullptr) {
            x = z->left;
            transplant(z, z->left);
        } else {
            y = minimum(z->right);
            yOriginalColor = y->color;
            x = y->right;
            if (y->parent == z) {
                if (x) x->parent = y;
            } else {
                transplant(y, y->right);
                y->right = z->right;
                y->right->parent = y;
            }

            transplant(z, y);
            y->left = z->left;
            y->left->parent = y;
            y->color = z->color;
        }

        delete z;

        if (yOriginalColor == BLACK && x != nullptr)
            deleteFixup(x);
    }

    void deleteNode(int data) {
        Node *z = search(data);
        if (z != nullptr)
            deleteNode(z);
    }
};

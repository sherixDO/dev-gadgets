#include <iostream>
#include <string>
#include <limits>

// 引入红黑树实现
#include "main.cpp"

using namespace std;

void printMenu() {
    cout << "\n红黑树操作菜单：" << endl;
    cout << "1. 插入节点" << endl;
    cout << "2. 删除节点" << endl;
    cout << "3. 查找节点" << endl;
    cout << "4. 退出" << endl;
    cout << "请选择操作 (1-4): ";
}

void clearInputBuffer() {
    cin.clear();
    cin.ignore(numeric_limits<streamsize>::max(), '\n');
}

int main() {
    RBTree tree;
    int choice, value;

    cout << "欢迎使用红黑树演示程序!" << endl;

    while (true) {
        printMenu();

        if (!(cin >> choice)) {
            cout << "输入无效，请输入1-4之间的数字。" << endl;
            clearInputBuffer();
            continue;
        }

        switch (choice) {
            case 1: // 插入节点
                cout << "请输入要插入的整数值: ";
                if (cin >> value) {
                    tree.insert(value);
                    cout << "值 " << value << " 已成功插入到红黑树中。" << endl;
                } else {
                    cout << "输入无效，请输入一个整数。" << endl;
                    clearInputBuffer();
                }
                break;

            case 2: // 删除节点
                cout << "请输入要删除的整数值: ";
                if (cin >> value) {
                    Node* node = tree.search(value);
                    if (node) {
                        tree.deleteNode(value);
                        cout << "值 " << value << " 已成功从红黑树中删除。" << endl;
                    } else {
                        cout << "值 " << value << " 不在红黑树中。" << endl;
                    }
                } else {
                    cout << "输入无效，请输入一个整数。" << endl;
                    clearInputBuffer();
                }
                break;

            case 3: // 查找节点
                cout << "请输入要查找的整数值: ";
                if (cin >> value) {
                    Node* node = tree.search(value);
                    if (node) {
                        cout << "值 " << value << " 在红黑树中找到。" << endl;
                        cout << "节点颜色: " << (node->color == RED ? "红色" : "黑色") << endl;
                    } else {
                        cout << "值 " << value << " 不在红黑树中。" << endl;
                    }
                } else {
                    cout << "输入无效，请输入一个整数。" << endl;
                    clearInputBuffer();
                }
                break;

            case 4: // 退出
                cout << "感谢使用红黑树演示程序，再见！" << endl;
                return 0;

            default:
                cout << "选择无效，请输入1-4之间的数字。" << endl;
        }
    }

    return 0;
}

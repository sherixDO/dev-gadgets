import math
import random
import copy
from typing import List, Tuple


# --- 1. 游戏引擎 (GameState Class) ---

class GameState:
    """
    管理游戏的所有状态和规则。
    玩家1: 黑方 (Black)
    玩家2: 白方 (White)
    """

    def __init__(self):
        # 棋盘, 0: 空, 1: 黑方棋子, 2: 白方棋子
        self.board = [[0] * 9 for _ in range(9)]
        # 领地, 0: 无主, 1: 黑方领地, 2: 白方领地
        self.territory = [[0] * 9 for _ in range(9)]
        # 当前玩家
        self.current_player = 1
        # 回合数
        self.turn_count = 0

    def clone(self):
        """深度克隆当前游戏状态，用于MCTS模拟"""
        state = GameState()
        state.board = copy.deepcopy(self.board)
        state.territory = copy.deepcopy(self.territory)
        state.current_player = self.current_player
        state.turn_count = self.turn_count
        return state

    def get_legal_moves(self) -> List[Tuple[int, int]]:
        """获取所有合法落子点"""
        moves = []
        for r in range(9):
            for c in range(9):
                if self.board[r][c] == 0 and \
                        (self.territory[r][c] == 0 or self.territory[r][c] == self.current_player):
                    moves.append((r, c))
        return moves

    def is_terminal(self) -> bool:
        """判断游戏是否结束"""
        return self.turn_count >= 40

    def get_winner(self) -> int:
        """游戏结束时计算胜者。1: 黑胜, 2: 白胜, 0: 平局"""
        if not self.is_terminal():
            return -1  # 游戏未结束

        black_score = sum(row.count(1) for row in self.territory)
        white_score = sum(row.count(2) for row in self.territory)

        if black_score > white_score:
            return 1
        elif white_score > black_score:
            return 2
        else:
            return 0

    def make_move(self, move: Tuple[int, int]):
        """
        执行一步棋，并更新棋盘状态。这是最核心的逻辑。
        """
        r, c = move
        if not (0 <= r < 9 and 0 <= c < 9 and self.board[r][c] == 0):
            # 非法移动，理论上不应发生
            return

        self.board[r][c] = self.current_player

        # 检查是否形成三连
        threes_found = self._check_for_threes(move)

        if threes_found:
            # 首先，识别所有将被移除并转化为领地的棋子
            all_pieces_to_convert_to_territory = set()
            for line_pieces, _ in threes_found:
                for piece_pos in line_pieces:
                    all_pieces_to_convert_to_territory.add(piece_pos)

            # 1. 将这些棋子从棋盘上移除，并将其位置标记为当前玩家的领地
            for pr, pc in all_pieces_to_convert_to_territory:
                self.board[pr][pc] = 0
                self.territory[pr][pc] = self.current_player

            # 2. 为每一个形成的三连分别进行领地扩散
            #    确保扩散仅基于构成该特定三连的棋子
            for line_pieces, line_direction in threes_found:
                self._diffuse_territory(line_pieces, line_direction)

        # 更新回合和玩家
        self.turn_count += 1
        self.current_player = 3 - self.current_player  # 1 -> 2, 2 -> 1

    def _check_for_threes(self, move: Tuple[int, int]) -> List[Tuple[List[Tuple[int, int]], Tuple[int, int]]]:
        """
        以新落的子为中心，检查所有方向是否形成三连。
        返回一个列表，每个元素是 ([三个棋子的坐标], 方向向量)
        """
        r, c = move
        player = self.current_player
        threes = []

        # 定义四个方向：横、竖、主对角线、副对角线
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

        for dr, dc in directions:
            # 在每个方向上，检查以新子为中心的三个可能的三连组合
            for i in range(-2, 1):
                p1 = (r + i * dr, c + i * dc)
                p2 = (r + (i + 1) * dr, c + (i + 1) * dc)
                p3 = (r + (i + 2) * dr, c + (i + 2) * dc)

                line = [p1, p2, p3]
                if all(0 <= pr < 9 and 0 <= pc < 9 and self.board[pr][pc] == player for pr, pc in line):
                    threes.append((line, (dr, dc)))

        return threes

    def _diffuse_territory(self, start_pieces: List[Tuple[int, int]], direction: Tuple[int, int]):
        """
        从一条线段的两端向外扩散领地，确保只在同一直线上扩散
        """
        dr, dc = direction

        # 向正方向扩散
        pos_r, pos_c = max(start_pieces, key=lambda p: p[0] * dr + p[1] * dc)
        self._diffuse_in_one_direction(pos_r, pos_c, dr, dc)

        # 向反方向扩散
        neg_r, neg_c = min(start_pieces, key=lambda p: p[0] * dr + p[1] * dc)
        self._diffuse_in_one_direction(neg_r, neg_c, -dr, -dc)

    def _diffuse_in_one_direction(self, r_start, c_start, dr, dc):
        """
        从起始点沿着指定方向扩散领地，确保只在直线上扩散
        """
        r, c = r_start + dr, c_start + dc

        # 检查是否为斜线方向
        is_diagonal = abs(dr) == 1 and abs(dc) == 1

        while 0 <= r < 9 and 0 <= c < 9:
            # 遇到对方棋子，停止扩散
            if self.board[r][c] == 3 - self.current_player:
                break

            # 转化空格或对方领地
            self.territory[r][c] = self.current_player

            # 更新坐标，继续沿着同一方向扩散
            r, c = r + dr, c + dc

    def display(self):
        """打印棋盘，方便调试"""
        print(" " * 3 + " ".join([str(i) for i in range(9)]))
        print("  " + "-" * 19)
        for r in range(9):
            row_str = f"{r} |"
            for c in range(9):
                if self.board[r][c] == 1:
                    char = "●"  # 黑子
                elif self.board[r][c] == 2:
                    char = "○"  # 白子
                else:
                    if self.territory[r][c] == 1:
                        char = "x"  # 黑地
                    elif self.territory[r][c] == 2:
                        char = "o"  # 白地
                    else:
                        char = "."  # 空地
                row_str += f" {char}"
            print(row_str)
        print("-" * 22)


# --- 2. MCTS 节点 (MCTSNode Class) ---

class MCTSNode:
    def __init__(self, state: GameState, parent=None, move=None):
        self.state = state
        self.parent = parent
        self.move = move
        self.children = []
        self.wins = 0
        self.visits = 0
        self.untried_moves = self.state.get_legal_moves()

    def select_child(self, exploration_constant):
        """使用UCT公式选择最佳子节点"""
        return max(
            self.children,
            key=lambda c: (c.wins / c.visits) + exploration_constant * math.sqrt(math.log(self.visits) / c.visits)
        )

    def expand(self):
        """从未尝试的移动中扩展一个新节点"""
        move = self.untried_moves.pop()
        new_state = self.state.clone()
        new_state.make_move(move)
        child_node = MCTSNode(new_state, parent=self, move=move)
        self.children.append(child_node)
        return child_node


# --- 3. MCTS AI (MCTS_AI Class) ---

class MCTS_AI:
    def __init__(self, exploration_constant=1.414, simulations_per_move=1000):
        self.C = exploration_constant
        self.simulations_per_move = simulations_per_move

    def find_best_move(self, initial_state: GameState):
        root = MCTSNode(state=initial_state)

        for _ in range(self.simulations_per_move):
            node = root
            state = initial_state.clone()

            # 1. 选择 (Selection)
            while node.untried_moves == [] and node.children != []:
                node = node.select_child(self.C)
                state.make_move(node.move)

            # 2. 扩展 (Expansion)
            if node.untried_moves != []:
                node = node.expand()
                state.make_move(node.move)

            # 3. 模拟 (Simulation)
            while not state.is_terminal():
                legal_moves = state.get_legal_moves()
                if not legal_moves: break
                state.make_move(random.choice(legal_moves))

            # 4. 反向传播 (Backpropagation)
            winner = state.get_winner()
            while node is not None:
                node.visits += 1
                # 如果是轮到该节点的玩家赢了，则增加胜利次数
                # 注意：node.state.current_player 是 *下一个* 玩家
                # 所以我们要比较winner和上一个玩家
                if (3 - node.state.current_player) == winner:
                    node.wins += 1
                node = node.parent

        if not root.children:
            # 如果没有合法走法（不太可能发生，除非开局就无路可走）
            return None

        # 选择访问次数最多的子节点，作为最稳健的走法
        best_child = max(root.children, key=lambda c: c.visits)
        return best_child.move


# --- 4. 主游戏循环 ---

if __name__ == "__main__":
    game = GameState()
    ai = MCTS_AI(simulations_per_move=1000)  # 模拟次数越多，AI越强，但耗时越长

    print("AI vs AI 开始！")
    game.display()

    while not game.is_terminal():
        player_name = "Black (●)" if game.current_player == 1 else "White (○)"
        print(f"\n--- 回合 {game.turn_count + 1}, 轮到 {player_name} ---")

        # AI 计算最佳走法
        best_move = ai.find_best_move(game)

        if best_move is None:
            print(f"{player_name} 无棋可下，跳过回合。")
            game.turn_count += 1
            game.current_player = 3 - game.current_player
            continue

        print(f"AI 选择落子在: {best_move}")

        # 执行走法并显示结果
        game.make_move(best_move)
        game.display()

    # 游戏结束，宣布结果
    print("\n--- 游戏结束 ---")
    game.display()

    winner = game.get_winner()
    if winner == 1:
        print("胜利者是: Black (●)")
    elif winner == 2:
        print("胜利者是: White (○)")
    else:
        print("游戏平局!")

    black_score = sum(row.count(1) for row in game.territory)
    white_score = sum(row.count(2) for row in game.territory)
    print(f"最终比分: Black {black_score} vs White {white_score}")

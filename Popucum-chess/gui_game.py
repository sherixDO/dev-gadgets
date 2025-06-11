import tkinter as tk
from tkinter import messagebox, Button, Frame, Canvas, Label, Scale, IntVar
from tkinter import font as tkFont  # 导入tkinter.font
import math # 添加 math 模块导入
from mcts import GameState, MCTS_AI

class GameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("围棋对弈")
        self.root.geometry("750x650")
        self.root.resizable(False, False)
        self.root.configure(bg="#F0F0F0")

        # --- 颜色和字体定义 ---
        self.colors = {
            "board_bg": "#D2B48C",
            "black_stone": "black",
            "white_stone": "white",
            "black_territory": "#707070",
            "white_territory": "#D3D3D3",
            "text_color": "#333333", # 深色文本颜色保持不变
            "button_bg": "#FFFFFF",
            "button_fg": "black",
            "button_active_bg": "#45a049",
            "light_bg": "#F0F0F0" # 定义一个明确的浅色背景供组件使用
        }
        self.fonts = {
            "default": tkFont.Font(family="Arial", size=12),
            "label": tkFont.Font(family="Arial", size=14, weight="bold"),
            "button": tkFont.Font(family="Arial", size=12, weight="bold"),
            "info": tkFont.Font(family="Arial", size=11),
            "rules_title": tkFont.Font(family="Arial", size=13, weight="bold"),
        }
        # ---

        # 游戏状态
        self.game = GameState()
        self.ai_strength = IntVar(value=1000)
        self.ai = MCTS_AI(simulations_per_move=self.ai_strength.get())
        self.ai_player = 2
        self.game_over = False

        # 棋盘尺寸
        self.cell_size = 55  # 稍微增大格子尺寸
        self.board_padding = 35 # 增加棋盘边距
        self.board_size = 9
        self.stone_radius_ratio = 0.4 # 棋子半径占格子大小的比例

        # 创建UI元素
        self.create_widgets()

        # 绘制初始棋盘
        self.draw_board()

        # 如果AI是黑方(先手)，则让AI先走
        if self.ai_player == 1:
            self.root.after(500, self.ai_move)

    def create_widgets(self):
        # --- 主框架 ---
        main_frame = Frame(self.root, bg=self.colors["light_bg"]) # 使用浅色背景
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 左侧面板 - 棋盘
        self.board_frame = Frame(main_frame, bg=self.colors["light_bg"]) # 使用浅色背景
        self.board_frame.pack(side=tk.LEFT, padx=(0,10), pady=0, fill=tk.Y)

        self.canvas = Canvas(
            self.board_frame,
            width=self.cell_size * self.board_size + self.board_padding * 2,
            height=self.cell_size * self.board_size + self.board_padding * 2,
            bg=self.colors["board_bg"],
            highlightthickness=1,
            highlightbackground="black"
        )
        self.canvas.pack(expand=True, fill=tk.BOTH)
        self.canvas.bind("<Button-1>", self.on_board_click)

        # 右侧面板 - 控制和信息
        self.control_frame = Frame(main_frame, width=220, bg=self.colors["light_bg"]) # 使用浅色背景
        self.control_frame.pack(side=tk.RIGHT, padx=(10,0), pady=0, fill=tk.BOTH)
        self.control_frame.pack_propagate(False)

        # --- 游戏信息 ---
        self.info_frame = Frame(self.control_frame, bg=self.colors["light_bg"], relief=tk.RIDGE, borderwidth=2) # 使用浅色背景
        self.info_frame.pack(pady=(0,10), fill=tk.X)

        self.turn_label = Label(self.info_frame, text="回合: 1", font=self.fonts["label"], fg=self.colors["text_color"], bg=self.colors["light_bg"]) # 使用浅色背景
        self.turn_label.pack(pady=8, padx=10, anchor=tk.W)

        self.player_label = Label(
            self.info_frame,
            text="当前玩家: 黑方 (●)",
            font=self.fonts["label"],
            fg=self.colors["text_color"],
            bg=self.colors["light_bg"] # 使用浅色背景
        )
        self.player_label.pack(pady=8, padx=10, anchor=tk.W)

        self.score_label = Label(
            self.info_frame,
            text="比分:\n黑方 0\nvs\n白方 0",
            font=self.fonts["label"],
            fg=self.colors["text_color"],
            bg=self.colors["light_bg"] # 使用浅色背景
        )
        self.score_label.pack(pady=8, padx=10, anchor=tk.W)

        # --- AI强度控制 ---
        self.ai_control_frame = Frame(self.control_frame, bg=self.colors["light_bg"], relief=tk.RIDGE, borderwidth=2) # 使用浅色背景
        self.ai_control_frame.pack(pady=10, fill=tk.X)

        Label(self.ai_control_frame, text="AI 强度:", font=self.fonts["default"], fg=self.colors["text_color"], bg=self.colors["light_bg"]).pack(anchor=tk.W, padx=10, pady=(5,0)) # 使用浅色背景

        self.ai_strength_scale = Scale(
            self.ai_control_frame,
            variable=self.ai_strength,
            from_=500,
            to=10000,
            resolution=500,
            orient=tk.HORIZONTAL,
            length=200,
            command=self.update_ai_strength,
            bg=self.colors["light_bg"], # 使用浅色背景
            fg=self.colors["text_color"],
            troughcolor="#C0C0C0",
            highlightthickness=0
        )
        self.ai_strength_scale.pack(fill=tk.X, padx=10, pady=(0,5))

        self.ai_info_label = Label(
            self.ai_control_frame,
            text=f"当前模拟: {self.ai_strength.get()}",
            font=self.fonts["info"],
            fg=self.colors["text_color"],
            bg=self.colors["light_bg"] # 使用浅色背景
        )
        self.ai_info_label.pack(pady=(0,5))

        # --- 控制按钮 ---
        self.button_frame = Frame(self.control_frame, bg=self.colors["light_bg"]) # 使用浅色背景
        self.button_frame.pack(pady=15, fill=tk.X)

        self.new_game_btn = Button(
            self.button_frame,
            text="新游戏",
            command=self.new_game,
            font=self.fonts["button"],
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            activebackground=self.colors["button_active_bg"],
            activeforeground=self.colors["button_fg"],
            relief=tk.RAISED,
            borderwidth=2,
            width=12
        )
        self.new_game_btn.pack(pady=7, fill=tk.X, padx=10)

        self.switch_btn = Button(
            self.button_frame,
            text="切换先后手",
            command=self.switch_sides,
            font=self.fonts["button"],
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            activebackground=self.colors["button_active_bg"],
            activeforeground=self.colors["button_fg"],
            relief=tk.RAISED,
            borderwidth=2,
            width=12
        )
        self.switch_btn.pack(pady=7, fill=tk.X, padx=10)

        # --- 游戏规则 ---
        self.rules_frame = Frame(self.control_frame, bg=self.colors["light_bg"], relief=tk.RIDGE, borderwidth=2) # 使用浅色背景
        self.rules_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        Label(self.rules_frame, text="游戏规则:", font=self.fonts["rules_title"], fg=self.colors["text_color"], bg=self.colors["light_bg"]).pack(anchor=tk.NW, padx=10, pady=(5,0)) # 使用浅色背景

        rules_text = """1. 玩家轮流在棋盘空格落子。
2. 落子形成三连 (横、竖、斜) 时，
   这三个棋子将被消除，其位置
   变为当前玩家的领地。
3. 领地会向三连的直线方向扩散，
   直到遇到边界或对方棋子。
4. 游戏共40回合。结束时，拥有
   更多领地的玩家获胜。"""

        self.rules_label = Label(
            self.rules_frame,
            text=rules_text,
            font=self.fonts["info"],
            fg=self.colors["text_color"],
            bg=self.colors["light_bg"], # 使用浅色背景
            justify=tk.LEFT,
            wraplength=190
        )
        self.rules_label.pack(pady=5, padx=10, anchor=tk.NW)

    def update_ai_strength(self, _=None):
        strength = self.ai_strength.get()
        self.ai = MCTS_AI(simulations_per_move=strength)
        self.ai_info_label.config(text=f"当前模拟次数: {strength}")

        # 提供一些关于AI强度的反馈
        if strength <= 1000:
            difficulty = "入门"
        elif strength <= 3000:
            difficulty = "简单"
        elif strength <= 6000:
            difficulty = "普通"
        else:
            difficulty = "困难"

        self.ai_info_label.config(text=f"当前模拟: {strength} ({difficulty})", font=self.fonts["info"])

    def draw_board(self):
        self.canvas.delete("all")

        # 绘制棋盘网格线 (board_size x board_size 个格子)
        for i in range(self.board_size + 1):
            # 横线
            y_coord = self.board_padding + i * self.cell_size
            self.canvas.create_line(
                self.board_padding, y_coord,
                self.board_padding + self.board_size * self.cell_size, y_coord,
                fill="black"
            )
            # 竖线
            x_coord = self.board_padding + i * self.cell_size
            self.canvas.create_line(
                x_coord, self.board_padding,
                x_coord, self.board_padding + self.board_size * self.cell_size,
                fill="black"
            )

        # 绘制星位 (仍然在交叉点上作为视觉标记)
        star_points = []
        if self.board_size == 9:
            star_points = [(2, 2), (2, 6), (4, 4), (6, 2), (6, 6)]
        elif self.board_size == 19:
            star_points = [(3,3), (3,9), (3,15), (9,3), (9,9), (9,15), (15,3), (15,9), (15,15)]

        for r_star, c_star in star_points:
            # 星位坐标是交叉点索引，所以直接使用
            x_intersect = self.board_padding + c_star * self.cell_size
            y_intersect = self.board_padding + r_star * self.cell_size
            # 确保星位不会画在最外层边界线上 (如果board_size较小且星位靠近边缘)
            if c_star < self.board_size and r_star < self.board_size :
                 self.canvas.create_oval(
                    x_intersect - 3, y_intersect - 3, x_intersect + 3, y_intersect + 3,
                    fill="black", outline="black"
                )

        # 绘制领地和棋子 (在格内)
        for r in range(self.board_size):
            for c in range(self.board_size):
                # 格子左上角坐标
                x1_cell = self.board_padding + c * self.cell_size
                y1_cell = self.board_padding + r * self.cell_size
                # 格子右下角坐标
                x2_cell = x1_cell + self.cell_size
                y2_cell = y1_cell + self.cell_size
                # 格子中心坐标 (用于棋子)
                x_cell_center = x1_cell + self.cell_size / 2
                y_cell_center = y1_cell + self.cell_size / 2

                stone_radius = self.cell_size * self.stone_radius_ratio

                # 绘制领地 (填充整个格子)
                if self.game.territory[r][c] == 1:  # 黑方领地
                    self.canvas.create_rectangle(
                        x1_cell, y1_cell, x2_cell, y2_cell,
                        fill=self.colors["black_territory"], outline="", tags="territory"
                    )
                elif self.game.territory[r][c] == 2:  # 白方领地
                    self.canvas.create_rectangle(
                        x1_cell, y1_cell, x2_cell, y2_cell,
                        fill=self.colors["white_territory"], outline="", tags="territory"
                    )

                # 绘制棋子 (在格子中心)
                if self.game.board[r][c] == 1:  # 黑棋
                    self.canvas.create_oval(
                        x_cell_center - stone_radius, y_cell_center - stone_radius,
                        x_cell_center + stone_radius, y_cell_center + stone_radius,
                        fill=self.colors["black_stone"], outline=self.colors["black_stone"], tags="piece"
                    )
                elif self.game.board[r][c] == 2:  # 白棋
                    self.canvas.create_oval(
                        x_cell_center - stone_radius, y_cell_center - stone_radius,
                        x_cell_center + stone_radius, y_cell_center + stone_radius,
                        fill=self.colors["white_stone"], outline="black", tags="piece"
                    )

    def on_board_click(self, event):
        if self.game_over or self.game.current_player == self.ai_player:
            return

        # 将点击坐标转换为棋盘格子行列索引
        # (event.x - self.board_padding) 是相对于棋盘网格左上角的坐标
        # 除以 self.cell_size 后取整，得到格子索引
        c = math.floor((event.x - self.board_padding) / self.cell_size)
        r = math.floor((event.y - self.board_padding) / self.cell_size)

        if 0 <= r < self.board_size and 0 <= c < self.board_size:
            if self.game.board[r][c] == 0 and \
               (self.game.territory[r][c] == 0 or self.game.territory[r][c] == self.game.current_player):
                self.game.make_move((r, c))
                self.draw_board()
                self.update_info()

                if self.game.is_terminal():
                    self.end_game()
                elif self.game.current_player == self.ai_player:
                    self.root.after(100, self.ai_move)
            else:
                messagebox.showwarning("无效落子", "此处不能落子！")

    def update_info(self):
        self.turn_label.config(text=f"回合: {self.game.turn_count + 1}", font=self.fonts["label"])
        player_text = "黑方 (●)" if self.game.current_player == 1 else "白方 (○)"
        self.player_label.config(text=f"当前玩家: {player_text}", font=self.fonts["label"])

        black_score = sum(row.count(1) for row in self.game.territory)
        white_score = sum(row.count(2) for row in self.game.territory)
        self.score_label.config(text=f"比分: 黑方 {black_score} vs 白方 {white_score}", font=self.fonts["label"])

    def ai_move(self):
        if self.game_over:
            return

        print(f"AI (Player {self.ai_player}) is thinking...")
        # AI计算最佳走法
        best_move = self.ai.find_best_move(self.game)

        if best_move is None:
            # AI无棋可下，跳过回合
            self.game.turn_count += 1
            self.game.current_player = 3 - self.game.current_player
        else:
            # 执行AI走法
            self.game.make_move(best_move)

        # 重绘棋盘
        self.draw_board()

        # 检查游戏是否结束
        if self.game.is_terminal():
            self.game_over = True
            self.show_game_result()

    def show_game_result(self):
        winner = self.game.get_winner()

        if winner == 1:
            result = "黑方 (●) 获胜!"
        elif winner == 2:
            result = "白方 (○) 获胜!"
        else:
            result = "游戏平局!"

        black_score = sum(row.count(1) for row in self.game.territory)
        white_score = sum(row.count(2) for row in self.game.territory)

        messagebox.showinfo(
            "游戏结束",
            f"{result}\n最终比分: 黑方 {black_score} vs 白方 {white_score}"
        )

    def new_game(self):
        self.game_over = False
        self.game = GameState()
        self.ai = MCTS_AI(simulations_per_move=self.ai_strength.get()) # 重新初始化AI以防强度改变

        # 重绘棋盘
        self.draw_board()

        # 如果AI是先手，则让AI先走
        if not self.game_over and self.game.current_player == self.ai_player:
            self.root.after(100, self.ai_move) # AI先走

    def switch_sides(self):
        if self.game.turn_count > 0:
            if not messagebox.askyesno("确认", "游戏中切换先后手会重置游戏，确定吗？"):
                return

        # 切换AI玩家
        self.ai_player = 3 - self.ai_player

        # 开始新游戏
        self.new_game()

        # 更新信息
        ai_side = "黑方 (●)" if self.ai_player == 1 else "白方 (○)"
        messagebox.showinfo("切换先后手", f"AI现在控制{ai_side}")

    def end_game(self):
        self.game_over = True
        winner = self.game.get_winner()

        if winner == 1:
            result_text = "黑方 (●) 获胜!"
        elif winner == 2:
            result_text = "白方 (○) 获胜!"
        else:
            result_text = "游戏平局!"

        black_score = sum(row.count(1) for row in self.game.territory)
        white_score = sum(row.count(2) for row in self.game.territory)

        # 显示更详细的结果，包括每个玩家的领地
        result_details = f"""
        最终比分:
        黑方: {black_score} 领地
        白方: {white_score} 领地

        {result_text}
        """

        messagebox.showinfo("游戏结束", result_details.strip())

if __name__ == '__main__':
    root = tk.Tk()
    gui = GameGUI(root)
    root.mainloop()

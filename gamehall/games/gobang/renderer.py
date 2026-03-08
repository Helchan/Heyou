"""五子棋游戏渲染器"""

from __future__ import annotations

import tkinter as tk
from typing import Any, TYPE_CHECKING

from ...game.renderer import GameRenderer, RendererRegistry
from .state import GobangState, BOARD_SIZE

if TYPE_CHECKING:
    from ...core import Core


class GobangRenderer(GameRenderer):
    """五子棋游戏渲染器"""
    
    def __init__(self, parent: tk.Widget, core: "Core", room_id: str) -> None:
        super().__init__(parent, core, room_id)
        self._game_state: GobangState | None = None
        self._cell = 36
        self._origin = (20, 20)
        self.canvas: tk.Canvas | None = None
    
    @staticmethod
    def get_game_name() -> str:
        return "gobang"
    
    def create_widget(self) -> tk.Widget:
        """创建五子棋棋盘 Canvas"""
        self.canvas = tk.Canvas(self.parent, bg="#e7cfa5", highlightthickness=0)
        self.canvas.bind("<Button-1>", self.on_player_action)
        self.canvas.bind("<Configure>", lambda _e: self._redraw())
        self._widget = self.canvas
        return self.canvas
    
    def render(self, game_state: Any) -> None:
        """渲染游戏状态"""
        if isinstance(game_state, GobangState):
            self._game_state = game_state
        self._redraw()
    
    def _metrics(self) -> tuple[int, int, int]:
        """计算棋盘布局参数"""
        if self.canvas is None:
            return 20, 20, 36
        w = max(200, int(self.canvas.winfo_width()))
        h = max(200, int(self.canvas.winfo_height()))
        size = min(w, h) - 40
        cell = max(18, size // (BOARD_SIZE - 1))
        ox = (w - cell * (BOARD_SIZE - 1)) // 2
        oy = (h - cell * (BOARD_SIZE - 1)) // 2
        return ox, oy, cell
    
    def _redraw(self) -> None:
        """重绘棋盘"""
        if self.canvas is None:
            return
        
        self.canvas.delete("all")
        ox, oy, cell = self._metrics()
        self._origin = (ox, oy)
        self._cell = cell

        # 绘制网格线
        for i in range(BOARD_SIZE):
            x = ox + i * cell
            y0 = oy
            y1 = oy + (BOARD_SIZE - 1) * cell
            self.canvas.create_line(x, y0, x, y1, fill="#6b4f2a")
        for i in range(BOARD_SIZE):
            y = oy + i * cell
            x0 = ox
            x1 = ox + (BOARD_SIZE - 1) * cell
            self.canvas.create_line(x0, y, x1, y, fill="#6b4f2a")

        # 绘制星位点
        stars = [(3, 3), (11, 3), (7, 7), (3, 11), (11, 11)]
        for sx, sy in stars:
            cx = ox + sx * cell
            cy = oy + sy * cell
            self.canvas.create_oval(cx - 4, cy - 4, cx + 4, cy + 4, fill="#6b4f2a", outline="")

        # 绘制棋子
        if self._game_state is None:
            return
        
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                v = self._game_state.board[y][x]
                if v == 0:
                    continue
                cx = ox + x * cell
                cy = oy + y * cell
                r = max(7, cell // 2 - 2)
                if v == 1:
                    # 黑子
                    self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill="#111827", outline="#f8fafc", width=2)
                else:
                    # 白子
                    self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill="#f8fafc", outline="#334155", width=2)
        
        # 标记最后落子位置
        if self._game_state.last_move:
            lx, ly, _c = self._game_state.last_move
            cx = ox + lx * cell
            cy = oy + ly * cell
            r = max(9, cell // 2 - 1)
            self.canvas.create_rectangle(cx - r, cy - r, cx + r, cy + r, outline="#22c55e", width=2)
    
    def on_player_action(self, event: tk.Event) -> None:
        """处理玩家点击落子"""
        if self._game_state is None:
            return
        
        # 游戏已结束
        if self._game_state.winner_peer_id:
            return
        
        # 检查是否轮到当前玩家
        my_id = self.core.peer_id
        if self._game_state.next_peer_id != my_id:
            return
        
        # 计算点击的棋盘坐标
        ox, oy = self._origin
        cell = self._cell
        x = int(round((event.x - ox) / cell))
        y = int(round((event.y - oy) / cell))
        
        # 检查坐标是否有效
        if not (0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE):
            return
        
        # 发送落子请求
        self.core.play_move(self.room_id, x, y)
    
    def get_status_text(self, game_state: Any, my_peer_id: str, nicknames: dict[str, str]) -> str:
        """获取状态栏文本"""
        if not isinstance(game_state, GobangState):
            return "等待房主开始…"
        
        def name(pid: str) -> str:
            if pid in nicknames:
                return nicknames.get(pid) or pid[:6]
            return pid[:6]
        
        colors = game_state.colors or {}
        my_color = colors.get(my_peer_id)
        
        # 角色文本
        if my_color == 1:
            role = "你是黑"
        elif my_color == 2:
            role = "你是白"
        else:
            role = "观战"
        
        # 对手文本
        opponent = ""
        if my_color in (1, 2):
            for pid, c in colors.items():
                if pid != my_peer_id and c in (1, 2):
                    opponent = name(pid)
                    break
        
        # 回合文本
        is_my_turn = game_state.next_peer_id == my_peer_id
        if game_state.winner_peer_id:
            if game_state.winner_peer_id == my_peer_id:
                turn = "你赢了"
            else:
                turn = f"胜者：{name(game_state.winner_peer_id)}"
        else:
            turn = "轮到你下子" if is_my_turn else f"轮到 {name(game_state.next_peer_id)} 下子"
        
        tail = f" • 对手 {opponent}" if opponent else ""
        return f"{role}{tail} • {turn}"
    
    def destroy(self) -> None:
        """清理资源"""
        self._game_state = None
        super().destroy()


# 注册五子棋渲染器
RendererRegistry.register(GobangRenderer)

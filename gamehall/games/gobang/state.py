"""五子棋游戏状态定义"""

from __future__ import annotations

from dataclasses import dataclass


BOARD_SIZE = 15


@dataclass
class GobangState:
    """五子棋游戏状态"""
    board: list[list[int]]  # 棋盘，0=空, 1=黑, 2=白
    next_peer_id: str  # 下一个落子的玩家
    winner_peer_id: str | None = None  # 获胜者
    last_move: tuple[int, int, int] | None = None  # (x, y, color)
    colors: dict[str, int] | None = None  # peer_id -> color (1=黑, 2=白)

    @staticmethod
    def new(next_peer_id: str) -> "GobangState":
        """创建新的空棋盘状态"""
        return GobangState(
            board=[[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)],
            next_peer_id=next_peer_id,
        )

    def can_place(self, x: int, y: int) -> bool:
        """检查指定位置是否可以落子"""
        return 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE and self.board[y][x] == 0


def check_winner(board: list[list[int]], x: int, y: int) -> int:
    """
    检查是否有玩家获胜
    
    Args:
        board: 棋盘
        x: 最后落子的 x 坐标
        y: 最后落子的 y 坐标
        
    Returns:
        获胜方颜色（1或2），无获胜返回0
    """
    color = board[y][x]
    if color == 0:
        return 0

    def count_dir(dx: int, dy: int) -> int:
        cx, cy = x + dx, y + dy
        c = 0
        while 0 <= cx < BOARD_SIZE and 0 <= cy < BOARD_SIZE and board[cy][cx] == color:
            c += 1
            cx += dx
            cy += dy
        return c

    # 检查四个方向：横、竖、左斜、右斜
    for dx, dy in ((1, 0), (0, 1), (1, 1), (1, -1)):
        total = 1 + count_dir(dx, dy) + count_dir(-dx, -dy)
        if total >= 5:
            return color
    return 0

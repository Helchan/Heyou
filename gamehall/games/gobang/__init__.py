"""五子棋游戏模块

包含五子棋的游戏处理器、状态和渲染器。
"""

from .state import GobangState, BOARD_SIZE, check_winner
from .handler import GobangHandler
from .renderer import GobangRenderer

__all__ = ["GobangState", "GobangHandler", "GobangRenderer", "BOARD_SIZE", "check_winner"]

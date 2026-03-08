"""游戏抽象层 - 提供统一的游戏处理器接口"""

from .base import GameConfig, GameHandler
from .registry import GameRegistry
from .gobang import GobangHandler, GobangState, BOARD_SIZE

__all__ = ["GameConfig", "GameHandler", "GameRegistry", "GobangHandler", "GobangState", "BOARD_SIZE"]

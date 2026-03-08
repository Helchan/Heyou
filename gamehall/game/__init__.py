"""游戏抽象层 - 提供统一的游戏处理器接口"""

from .base import GameConfig, GameHandler
from .registry import GameRegistry
from .renderer import GameRenderer, RendererRegistry

# 触发具体游戏模块的注册（导入 games 模块会自动注册所有游戏）
from .. import games as _games  # noqa: F401

__all__ = [
    "GameConfig",
    "GameHandler",
    "GameRegistry",
    "GameRenderer",
    "RendererRegistry",
]


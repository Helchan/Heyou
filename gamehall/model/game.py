"""通用游戏状态模型"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class GameStateWrapper:
    """
    通用游戏状态包装类
    
    用于 Core 层管理游戏状态，将具体游戏状态与通用元数据分离。
    这样 Core 层不需要了解具体游戏的状态结构。
    """
    game_name: str  # 游戏标识，如 "gobang"
    state: Any  # 具体游戏状态，由 GameHandler 定义
    
    # 通用元数据
    started_ms: int = 0  # 游戏开始时间戳
    last_action_ms: int = 0  # 最后操作时间戳
    
    # 游戏特定的元数据（可选）
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def get_state(self) -> Any:
        """获取游戏状态"""
        return self.state
    
    def update_state(self, new_state: Any, action_ms: int = 0) -> None:
        """
        更新游戏状态
        
        Args:
            new_state: 新的游戏状态
            action_ms: 操作时间戳，如果为 0 则不更新
        """
        self.state = new_state
        if action_ms > 0:
            self.last_action_ms = action_ms

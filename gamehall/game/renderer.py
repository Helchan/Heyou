"""游戏渲染器抽象基类定义"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING
import tkinter as tk

if TYPE_CHECKING:
    from ..core import Core


class GameRenderer(ABC):
    """
    游戏渲染器抽象基类
    
    每种游戏需要实现此接口，负责：
    - 创建游戏特定的 UI 组件
    - 渲染游戏状态
    - 处理玩家输入
    """
    
    def __init__(self, parent: tk.Widget, core: "Core", room_id: str) -> None:
        self.parent = parent
        self.core = core
        self.room_id = room_id
        self._widget: tk.Widget | None = None
    
    @staticmethod
    @abstractmethod
    def get_game_name() -> str:
        """返回对应的游戏标识"""
        pass
    
    @abstractmethod
    def create_widget(self) -> tk.Widget:
        """
        创建游戏 UI 组件
        
        Returns:
            创建的 tkinter 组件
        """
        pass
    
    @abstractmethod
    def render(self, game_state: Any) -> None:
        """
        渲染游戏状态
        
        Args:
            game_state: 游戏状态对象，类型由具体游戏定义
        """
        pass
    
    @abstractmethod
    def on_player_action(self, event: tk.Event) -> None:
        """
        处理玩家输入事件
        
        Args:
            event: tkinter 事件对象
        """
        pass
    
    @abstractmethod
    def get_status_text(self, game_state: Any, my_peer_id: str, nicknames: dict[str, str]) -> str:
        """
        获取状态栏文本
        
        Args:
            game_state: 游戏状态对象
            my_peer_id: 当前玩家的 peer_id
            nicknames: peer_id -> 昵称的映射
            
        Returns:
            状态栏显示文本
        """
        pass
    
    def destroy(self) -> None:
        """清理资源"""
        if self._widget is not None:
            try:
                self._widget.destroy()
            except tk.TclError:
                pass
            self._widget = None


class RendererRegistry:
    """
    游戏渲染器注册器
    
    用于注册和获取各种游戏的渲染器。新游戏只需实现 GameRenderer 接口
    并调用 RendererRegistry.register() 注册即可。
    """
    
    _renderers: dict[str, type[GameRenderer]] = {}
    
    @classmethod
    def register(cls, renderer_class: type[GameRenderer]) -> None:
        """
        注册游戏渲染器
        
        Args:
            renderer_class: 实现了 GameRenderer 接口的游戏渲染器类
        """
        game_name = renderer_class.get_game_name()
        cls._renderers[game_name] = renderer_class
    
    @classmethod
    def get_renderer(cls, game_name: str) -> type[GameRenderer] | None:
        """
        获取游戏渲染器类
        
        Args:
            game_name: 游戏标识，如 "gobang"
            
        Returns:
            GameRenderer 类，如果游戏未注册返回 None
        """
        return cls._renderers.get(game_name)
    
    @classmethod
    def is_registered(cls, game_name: str) -> bool:
        """
        检查渲染器是否已注册
        
        Args:
            game_name: 游戏标识
            
        Returns:
            是否已注册
        """
        return game_name in cls._renderers
    
    @classmethod
    def get_all_renderers(cls) -> list[str]:
        """
        获取所有已注册渲染器的游戏名称
        
        Returns:
            游戏名称列表
        """
        return list(cls._renderers.keys())

"""具体游戏实现模块

此模块包含所有具体游戏的实现。每个游戏都在独立的子目录中，
包含 handler.py（游戏逻辑）、state.py（游戏状态）和 renderer.py（UI 渲染）。

添加新游戏的步骤：
1. 在 games/ 下创建新目录，如 games/chess/
2. 实现 GameHandler 接口（handler.py）
3. 定义游戏状态数据类（state.py）
4. 实现 GameRenderer 接口（renderer.py）
5. 在 __init__.py 中导入新游戏模块

无需修改 Core、GUI 或其他现有代码。
"""

# 导入所有游戏模块，触发自动注册
from . import gobang

__all__ = ["gobang"]

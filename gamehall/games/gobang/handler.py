"""五子棋游戏处理器"""

from __future__ import annotations

import random
from typing import Any

from ...game.base import GameConfig, GameHandler
from ...game.registry import GameRegistry
from .state import GobangState, BOARD_SIZE, check_winner


class GobangHandler(GameHandler):
    """五子棋游戏处理器"""

    @staticmethod
    def get_config() -> GameConfig:
        return GameConfig(
            game_name="gobang",
            game_display_name="五子棋",
            team_size=1,  # 1v1
        )

    def create_game_state(self, team_a: list[str], team_b: list[str]) -> GobangState:
        """创建五子棋游戏状态，随机分配黑白"""
        if not team_a or not team_b:
            raise ValueError("Both teams must have at least one player")
        
        # 五子棋是 1v1，取每方第一个玩家
        player_a = team_a[0]
        player_b = team_b[0]
        
        # 随机分配黑白
        if random.random() < 0.5:
            black, white = player_a, player_b
        else:
            black, white = player_b, player_a
        
        state = GobangState.new(next_peer_id=black)
        state.colors = {black: 1, white: 2}
        return state

    def apply_action(self, state: Any, peer_id: str, action: dict[str, Any]) -> tuple[GobangState, bool]:
        """应用落子操作"""
        if not isinstance(state, GobangState):
            return state, False
        
        # 检查是否轮到该玩家
        if peer_id != state.next_peer_id:
            return state, False
        
        # 检查游戏是否已结束
        if state.winner_peer_id is not None:
            return state, False
        
        # 获取落子位置
        try:
            x = int(action.get("x", -1))
            y = int(action.get("y", -1))
        except (TypeError, ValueError):
            return state, False
        
        # 检查位置是否有效
        if not state.can_place(x, y):
            return state, False
        
        # 获取玩家颜色
        colors = state.colors or {}
        color = colors.get(peer_id)
        if color not in (1, 2):
            return state, False
        
        # 落子
        state.board[y][x] = color
        state.last_move = (x, y, color)
        
        # 检查是否获胜
        win_color = check_winner(state.board, x, y)
        if win_color:
            winner = next((pid for pid, c in colors.items() if c == win_color), None)
            state.winner_peer_id = winner
        else:
            # 切换到另一个玩家
            other = next((pid for pid, c in colors.items() if pid != peer_id), None)
            state.next_peer_id = other or peer_id
        
        return state, True

    def check_game_over(self, state: Any, team_a: list[str], team_b: list[str]) -> tuple[bool, str | None]:
        """检查游戏是否结束"""
        if not isinstance(state, GobangState):
            return False, None
        
        if state.winner_peer_id is None:
            return False, None
        
        # 判断获胜方属于哪个队伍
        if state.winner_peer_id in team_a:
            return True, "team_a"
        elif state.winner_peer_id in team_b:
            return True, "team_b"
        else:
            return True, None

    def get_state_for_broadcast(self, state: Any) -> dict[str, Any]:
        """获取用于广播的状态"""
        if not isinstance(state, GobangState):
            return {}
        
        colors = state.colors or {}
        black = next((pid for pid, c in colors.items() if c == 1), "")
        white = next((pid for pid, c in colors.items() if c == 2), "")
        
        return {
            "board": [cell for row in state.board for cell in row],  # 扁平化
            "next_peer_id": state.next_peer_id,
            "winner_peer_id": state.winner_peer_id,
            "last_move": list(state.last_move) if state.last_move else None,
            "black_peer_id": black,
            "white_peer_id": white,
            "board_size": BOARD_SIZE,
            "colors": colors,
        }

    def restore_from_broadcast(self, data: dict[str, Any]) -> GobangState:
        """从广播数据恢复游戏状态"""
        board_flat = data.get("board", [])
        board_size = data.get("board_size", BOARD_SIZE)
        
        # 重建二维棋盘
        board: list[list[int]] = []
        for y in range(board_size):
            row: list[int] = []
            for x in range(board_size):
                idx = y * board_size + x
                if idx < len(board_flat):
                    try:
                        row.append(int(board_flat[idx]))
                    except (TypeError, ValueError):
                        row.append(0)
                else:
                    row.append(0)
            board.append(row)
        
        # 恢复 colors
        colors_data = data.get("colors")
        if colors_data and isinstance(colors_data, dict):
            colors = {str(k): int(v) for k, v in colors_data.items()}
        else:
            # 兼容旧格式
            black = str(data.get("black_peer_id", ""))
            white = str(data.get("white_peer_id", ""))
            colors = {}
            if black:
                colors[black] = 1
            if white:
                colors[white] = 2
        
        # 恢复 last_move
        last_move_data = data.get("last_move")
        last_move = None
        if isinstance(last_move_data, (list, tuple)) and len(last_move_data) == 3:
            try:
                last_move = (int(last_move_data[0]), int(last_move_data[1]), int(last_move_data[2]))
            except (TypeError, ValueError):
                pass
        
        state = GobangState(
            board=board,
            next_peer_id=str(data.get("next_peer_id", "")),
            winner_peer_id=str(data.get("winner_peer_id")) if data.get("winner_peer_id") else None,
            last_move=last_move,
            colors=colors,
        )
        
        return state

    def get_next_player(self, state: Any) -> str | None:
        """获取下一个应该操作的玩家"""
        if not isinstance(state, GobangState):
            return None
        if state.winner_peer_id is not None:
            return None
        return state.next_peer_id

    def get_winner(self, state: Any) -> str | None:
        """获取获胜玩家"""
        if not isinstance(state, GobangState):
            return None
        return state.winner_peer_id


# 注册五子棋游戏
GameRegistry.register(GobangHandler)

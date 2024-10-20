from othello import Othello
import OthelloEnv
from type import State
import numpy as np


def evaluate_board_nkmr(state: State) -> int:
    result = 0
    n = state[0].sum() + state[1].sum()  # 置かれた石の数
    color = state[2, 0, 0]
    if OthelloEnv.winner(state) == color + 1:
        _, black, white = OthelloEnv.count(state)
        return (black - white) * (1 if color == 1 else -1)
    opp_state = state.copy()
    size = state.shape[1]
    if color == 0:
        opp_state[2] = np.ones((size, size))
    else:
        opp_state[2] = np.zeros((size, size))
    # 相手のおける場所が少ないほうが良い
    result = -len(OthelloEnv.valid_actions(opp_state)) * 5
    # 隅の列全部とったら大加点
    # TODO 確定石は+40点

    for c in range(0, 2):
        e = 0
        if state[c][0].sum() == size:
            e += 100
        if state[c][size - 1].sum() == size:
            e += 100
        state_t = state.T
        if state_t[c][0].sum() == size:
            e += 100
        if state_t[c][size - 1].sum() == size:
            e += 100
        result += e if c == 0 else -e

    board = state[0] + state[1] * 2
    for y in range(size):
        for x in range(size):
            if board[y][x] == 0:
                continue
            e = 1

            # 序盤は数いらない
            if n < 20:
                e -= 3
            # 終盤は数優先
            if n > 40:
                e += 15
            if n >= 60:
                e += 45

            if (
                (x, y) == (0, 0)
                or (x, y) == (0, size - 1)
                or (x, y) == (size - 1, 0)
                or (x, y) == (size - 1, size - 1)
            ):
                e += 200

            # 隅は加点
            if x == 0 or x == size - 1 or y == 0 or y == size - 1:
                e += 15
            # とってない角の隣はペナルティ
            if board[y][x] == 1:
                if board[0][0] != 1 and (
                    (x, y) == (1, 1) or (x, y) == (0, 1) or (x, y) == (1, 0)
                ):
                    e -= 60
                if board[0][size - 1] != 1 and (
                    (x, y) == (1, size - 2)
                    or (x, y) == (1, size - 1)
                    or (x, y) == (0, size - 2)
                ):
                    e -= 60
                if board[size - 1][0] != 1 and (
                    (x, y) == (size - 2, 1)
                    or (x, y) == (size - 2, 0)
                    or (x, y) == (size - 1, 1)
                ):
                    e -= 60
                if board[size - 1][size - 1] != 1 and (
                    (x, y) == (size - 2, size - 1)
                    or (x, y) == (size - 2, size - 2)
                    or (x, y) == (size - 1, size - 2)
                ):
                    e -= 60

            if board[y][x] == 2:
                if board[0][0] != 2 and (
                    (x, y) == (1, 1) or (x, y) == (0, 1) or (x, y) == (1, 0)
                ):
                    e -= 60
                if board[0][size - 1] != 2 and (
                    (x, y) == (1, size - 2)
                    or (x, y) == (1, size - 1)
                    or (x, y) == (0, size - 2)
                ):
                    e -= 60
                if board[size - 1][0] != 2 and (
                    (x, y) == (size - 2, 1)
                    or (x, y) == (size - 2, 0)
                    or (x, y) == (size - 1, 1)
                ):
                    e -= 60
                if board[size - 1][size - 1] != 2 and (
                    (x, y) == (size - 2, size - 1)
                    or (x, y) == (size - 2, size - 2)
                    or (x, y) == (size - 1, size - 2)
                ):
                    e -= 60

            result += e if board[y][x] == 1 else -e
    return result if color == 1 else -result

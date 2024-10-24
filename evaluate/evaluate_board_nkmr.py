from domain.models import *
from domain import OthelloEnv


def evaluate_board_nkmr(state: State) -> int:
    board = state.board
    color = state.color
    result = 0
    n = 0  # 置かれた石の数
    for y in range(SIZE):
        for x in range(SIZE):
            if board[y][x] != 0:
                n += 1
    if OthelloEnv.is_done(state):
        winner = OthelloEnv.winner(state)
        _, b, w = OthelloEnv.count(state)
        if winner == Color.BLACK:
            return (b - w) * 1000
        else:
            return (w - b) * 1000
    # 相手のおける場所が少ないほうが良い
    result = -len(OthelloEnv.valid_actions(state.copy(color=color.reverse()))) * 5
    # 隅の列全部とったら大加点
    # TODO 確定石は+40点

    for c in range(1, 3):
        e = 0
        if board[0].count(c) == SIZE:
            e += 100
        if board[SIZE - 1].count(c) == SIZE:
            e += 100
        c0 = 0
        c7 = 0
        for y in range(SIZE):
            if board[y][0] == c:
                c0 += 1
            if board[y][SIZE - 1] == c:
                c7 += 1
        if c0 == SIZE:
            e += 100
        if c7 == SIZE:
            e += 100
        result += e if c == 1 else -e

    for y in range(SIZE):
        for x in range(SIZE):
            if board[y][x] == 0:
                continue
            e = 1

            # 序盤は数いらない
            if n < 20:
                e -= 3
            # 終盤は数優先
            if n > 40:
                e += 15
            if n >= SIZE - 20:
                e += 45

            if (
                (x, y) == (0, 0)
                or (x, y) == (0, SIZE - 1)
                or (x, y) == (SIZE - 1, 0)
                or (x, y) == (SIZE - 1, SIZE - 1)
            ):
                e += 200

            # 隅は加点
            if x == 0 or x == SIZE - 1 or y == 0 or y == SIZE - 1:
                e += 15
            # とってない角の隣はペナルティ
            if board[y][x] == 1:
                if board[0][0] != 1 and (
                    (x, y) == (1, 1) or (x, y) == (0, 1) or (x, y) == (1, 0)
                ):
                    e -= 60
                if board[0][SIZE - 1] != 1 and (
                    (x, y) == (1, SIZE - 1)
                    or (x, y) == (1, SIZE - 1)
                    or (x, y) == (0, SIZE - 1)
                ):
                    e -= 60
                if board[SIZE - 1][0] != 1 and (
                    (x, y) == (SIZE - 1, 1)
                    or (x, y) == (SIZE - 1, 0)
                    or (x, y) == (SIZE - 1, 1)
                ):
                    e -= 60
                if board[SIZE - 1][SIZE - 1] != 1 and (
                    (x, y) == (SIZE - 1, SIZE - 1)
                    or (x, y) == (SIZE - 1, SIZE - 1)
                    or (x, y) == (SIZE - 1, SIZE - 1)
                ):
                    e -= 60

            if board[y][x] == 2:
                if board[0][0] != 2 and (
                    (x, y) == (1, 1) or (x, y) == (0, 1) or (x, y) == (1, 0)
                ):
                    e -= 60
                if board[0][SIZE - 1] != 2 and (
                    (x, y) == (1, SIZE - 1)
                    or (x, y) == (1, SIZE - 1)
                    or (x, y) == (0, SIZE - 1)
                ):
                    e -= 60
                if board[SIZE - 1][0] != 2 and (
                    (x, y) == (SIZE - 1, 1)
                    or (x, y) == (SIZE - 1, 0)
                    or (x, y) == (SIZE - 1, 1)
                ):
                    e -= 60
                if board[SIZE - 1][SIZE - 1] != 2 and (
                    (x, y) == (SIZE - 1, SIZE - 1)
                    or (x, y) == (SIZE - 1, SIZE - 1)
                    or (x, y) == (SIZE - 1, SIZE - 2)
                ):
                    e -= SIZE - 20

            if x == 0 or x == 2 or x == 5 or x == 7:
                e += 1
            else:
                e -= 1
            if y == 0 or y == 2 or y == 5 or y == 7:
                e += 1
            else:
                e -= 1

            result += e if board[y][x] == 1 else -e
    return result if color == 1 else -result

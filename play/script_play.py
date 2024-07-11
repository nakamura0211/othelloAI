from evaluate_board import evaluate_board
from othello import Othello, fromHistory
from random import choice


def script_play(othello: Othello, color):
    ps = othello.possible_puts(color)
    opp_ps = othello.possible_puts(3 - color)
    scores = []
    mx = -float("inf")

    for x, y in ps:
        o = fromHistory(othello.history + [(x, y)])
        score = evaluate_board(o.board, color)
        # 相手が置けない場所は減点
        if (x, y) not in opp_ps:
            score -= 8
        # 置いた場所の隣に別の石があり、反対が空だと減点
        for dx, dy in Othello.dirs:
            if (
                x + dx in range(8)
                and y + dy in range(8)
                and o.board[y + dy][x + dx] == 3 - color
                and x - dx in range(8)
                and y - dy in range(8)
                and o.board[y - dy][x - dx] == 0
            ):
                score -=20
        scores.append(score)
        mx = max(score, mx)
    r = choice([ps[i] for i in range(len(ps)) if scores[i] == mx])
    return r
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


def evaluate_board(board: list, color) -> int:
    result = 0
    n = 0  # 置かれた石の数
    for y in range(8):
        for x in range(8):
            if board[y][x] != 0:
                n += 1
    oth=Othello()
    oth.board=board
    if oth.winner()==color:
        return 10000
    elif oth.winner==3-color:
        return -10000
    #相手のおける場所が少ないほうが良い
    result=-len(oth.possible_puts(3-color))*5
    # 隅の列全部とったら大加点
    #TODO 確定石は+40点

    for c in range(1, 3):
        e = 0
        if board[0].count(c) == 8:
            e += 100
        if board[7].count(c) == 8:
            e += 100
        c0 = 0
        c7 = 0
        for y in range(8):
            if board[y][0] == c:
                c0 += 1
            if board[y][7] == c:
                c7 += 1
        if c0 == 8:
            e += 100
        if c7 == 8:
            e += 100
        result += e if c == 1 else -e
    
    for y in range(8):
        for x in range(8):
            if board[y][x] == 0:
                continue
            e = 1

            # 序盤は数いらない
            if n < 20:
                e -= 3
            #終盤は数優先
            if n>40:
                e+=15
            if n>=60:
                e+=45

            if (
                (x, y) == (0, 0)
                or (x, y) == (0, 7)
                or (x, y) == (7, 0)
                or (x, y) == (7, 7)
            ):
                e += 200
            
            #隅は加点
            if (x == 0 or x == 7 or y == 0 or y == 7):
                e += 15
            # とってない角の隣はペナルティ
            if board[y][x]==1:
                if board[0][0] != 1 and ((x, y) == (1, 1) or (x, y) == (0, 1) or (x, y) == (1, 0)):
                    e-=60
                if board[0][7] != 1 and ((x, y) == (1, 6) or (x, y) == (1, 7) or (x, y) == (0, 6)):
                    e-=60
                if board[7][0] != 1 and ((x, y) == (6, 1) or (x, y) == (6, 0) or (x, y) == (7, 1)):
                    e-=60
                if board[7][7] != 1 and ((x, y) == (6, 7) or (x, y) == (6, 6) or (x, y) == (7, 6)):
                    e-=60
                
            if board[y][x]==2:
                if board[0][0] != 2 and ((x, y) == (1, 1) or (x, y) == (0, 1) or (x, y) == (1, 0)):
                    e-=60
                if board[0][7] != 2 and ((x, y) == (1, 6) or (x, y) == (1, 7) or (x, y) == (0, 6)):
                    e-=60
                if board[7][0] != 2 and ((x, y) == (6, 1) or (x, y) == (6, 0) or (x, y) == (7, 1)):
                    e-=60
                if board[7][7] != 2 and ((x, y) == (6, 7) or (x, y) == (6, 6) or (x, y) == (7, 6)):
                    e-=60
                
           

            if x ==0 or x==2 or x==5 or x==7:
                e += 1
            else:
                e -= 1
            if y==0 or y==2 or y==5 or y==7:
                e += 1
            else:
                e -= 1

            result += e if board[y][x] == 1 else -e
    return result if color == 1 else -result

import numpy as np
from othello import Othello
from play.alpha_beta_play import alpha_beta_play_depth

def evaluate_board_nkmr_es(filename:str="cma_es"):
    scores=np.loadtxt(f"./es_output/{filename}_score.txt")[::-1]
    means=np.loadtxt(f"./es_output/{filename}_mean.txt")[::-1]
    bestidx=scores.argmax()
    print(bestidx,means[bestidx])
    eval=lambda b,c:evaluate_board_nkmr_es_train(b,c,means[bestidx])
    return alpha_beta_play_depth(3,eval)

def evaluate_board_nkmr_es_train(board: list[list[int]], color:int,gene:np.ndarray[float]) -> int:
    result = 0
    n = 0  # 置かれた石の数
    for y in range(8):
        for x in range(8):
            if board[y][x] != 0:
                n += 1
    oth=Othello()
    oth.board=board
    if oth.winner()==color:
        black=0
        for i in range(8):
            for j in range(8):
                if board[i][j]==1:black+=1
                elif board[i][j]==2:black-=1
        return (black*1000)*(1 if color==1 else -1)
    #相手のおける場所が少ないほうが良い
    result=-len(oth.possible_puts(3-color))*gene[0]
    # 隅の列全部とったら大加点
    #TODO 確定石は+40点

    for c in range(1, 3):
        e = 0
        if board[0].count(c) == 8:
            e += gene[1]
        if board[7].count(c) == 8:
            e += gene[1]
        c0 = 0
        c7 = 0
        for y in range(8):
            if board[y][0] == c:
                c0 += 1
            if board[y][7] == c:
                c7 += 1
        if c0 == 8:
            e += gene[1]
        if c7 == 8:
            e += gene[1]
        result += e if c == 1 else -e
    
    for y in range(8):
        for x in range(8):
            if board[y][x] == 0:
                continue
            e = 1

            # 序盤は数いらない
            if n < 20:
                e -= gene[2]
            #終盤は数優先
            if n>40:
                e+=gene[3]
            if n>=60:
                e+=gene[4]

            if (
                (x, y) == (0, 0)
                or (x, y) == (0, 7)
                or (x, y) == (7, 0)
                or (x, y) == (7, 7)
            ):
                e += gene[5]
            
            #隅は加点
            if (x == 0 or x == 7 or y == 0 or y == 7):
                e += gene[6]
            # とってない角の隣はペナルティ
            if board[y][x]==1:
                if board[0][0] != 1 and ((x, y) == (1, 1) or (x, y) == (0, 1) or (x, y) == (1, 0)):
                    e-=gene[7]
                if board[0][7] != 1 and ((x, y) == (1, 6) or (x, y) == (1, 7) or (x, y) == (0, 6)):
                    e-=gene[7]
                if board[7][0] != 1 and ((x, y) == (6, 1) or (x, y) == (6, 0) or (x, y) == (7, 1)):
                    e-=gene[7]
                if board[7][7] != 1 and ((x, y) == (6, 7) or (x, y) == (6, 6) or (x, y) == (7, 6)):
                    e-=gene[7]
                
            if board[y][x]==2:
                if board[0][0] != 2 and ((x, y) == (1, 1) or (x, y) == (0, 1) or (x, y) == (1, 0)):
                    e-=gene[7]
                if board[0][7] != 2 and ((x, y) == (1, 6) or (x, y) == (1, 7) or (x, y) == (0, 6)):
                    e-=gene[7]
                if board[7][0] != 2 and ((x, y) == (6, 1) or (x, y) == (6, 0) or (x, y) == (7, 1)):
                    e-=gene[7]
                if board[7][7] != 2 and ((x, y) == (6, 7) or (x, y) == (6, 6) or (x, y) == (7, 6)):
                    e-=gene[7]
                
           

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

from othello import Othello
from es_ngn import evaluation_table2,othello_eval

def evaluate_board_ngn2(board, color) :
    
    n = 0  
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

    score = 0
    opponent = 3-color
    
    for y in range(8):
        for x in range(8):
            if board[y][x] == color:
                score += evaluation_table2[y][x]
            elif board[y][x] == opponent:
                score -= evaluation_table2[y][x]
    return score if  color == 1 else -score
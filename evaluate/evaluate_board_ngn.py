from othello import Othello

def evaluate_board_ngn(board, color) :
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
    evaluation_table = [
        [100,10,40,30,30,40,10,100],
        [10,5,8,6,6,8,5,10],
        [40,8,15,10,10,15,8,40],
        [30,6,10,10,10,10,6,30],
        [30,6,10,10,10,10,6,30],
        [40,8,15,10,10,15,8,40],
        [10,5,8,6,6,8,5,10],
        [100,10,40,30,30,40,10,100]
    ]
    score = 0
    opponent = 3-color
    for y in range(8):
        for x in range(8):
            if board[y][x] == color:
                score += evaluation_table[y][x]
            elif board[y][x] == opponent:
                score -= evaluation_table[y][x]
    return score if  color == 1 else -score

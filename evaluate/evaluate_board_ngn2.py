from othello import Othello
evaluation_table2 = [9.309686802648422, -55.228733286729415, -22.841360389475902, -7.891116260892756, 22.57822837847436, -27.68406246097886, 118.59463330412778, 107.08332483333382, -49.993867933880345, 57.4276713400455, -71.17219667234166, -17.566181264443465, -6.302710011742824, -73.75138380531219, -47.830920676357756, 31.044693419323078]

def input_table(individual):
        evaluation_table = [[0]*8 for _ in range(8)]
        for i in range(4):
            for j in range(4):
                evaluation_table[i][j] = individual[i*4+j]
        for i in range(4):
            for j in range(4):
                evaluation_table[i+4][j] = individual[(3-i)*4+j]
        for i in range(4):
            for j in range(4):
                evaluation_table[i][j+4] = individual[4*(i+1)-(j+1)]
        for i in range(4):
            for j in range(4):
                evaluation_table[i+4][j+4] = individual[(3-i) * 4 + (3-j)] 
        return evaluation_table


def evaluate_board_ngn2(board, color) :
    evaluation_table3 = [[0]*8 for _ in range(8)]
    evaluation_table3 = input_table(evaluation_table2)
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
                score += evaluation_table3[y][x]
            elif board[y][x] == opponent:
                score -= evaluation_table3[y][x]
    return score if  color == 1 else -score
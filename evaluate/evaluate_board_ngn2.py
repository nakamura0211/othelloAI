from othello import Othello
from play.alpha_beta_play import alpha_beta_play
from gui_othello import GUI_Othello
def input_table(individual):
        evaluation_table = [[0]*8 for _ in range(8)]
        evaluation_table2 = [[0]*8 for _ in range(8)]
        evaluation_table3 = [[0]*8 for _ in range(8)]
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
        for i in range(4):
            for j in range(4):
                evaluation_table2[i][j] = individual[i*4+j+16]
        for i in range(4):
            for j in range(4):
                evaluation_table2[i+4][j] = individual[(3-i)*4+j+16]
        for i in range(4):
            for j in range(4):
                evaluation_table2[i][j+4] = individual[4*(i+1)-(j+1)+16]
        for i in range(4):
            for j in range(4):
                evaluation_table2[i+4][j+4] = individual[(3-i) * 4 + (3-j)+16] 
        for i in range(4):
            for j in range(4):
                evaluation_table3[i][j] = individual[i*4+j+32]
        for i in range(4):
            for j in range(4):
                evaluation_table3[i+4][j] = individual[(3-i)*4+j+32]
        for i in range(4):
            for j in range(4):
                evaluation_table3[i][j+4] = individual[4*(i+1)-(j+1)+32]
        for i in range(4):
            for j in range(4):
                evaluation_table3[i+4][j+4] = individual[(3-i) * 4 + (3-j)+32] 
        return evaluation_table,evaluation_table2,evaluation_table3

def evaluate_board_ngn(board, color) : 
    individual = [76.32979597875611, 155.02097502448746, 80.21479588730273, -57.11627639363957, 6.368691011774339, 107.90361876092376, -43.315618467197325, 67.37930950146608, -157.71874531078652, -78.04039652208158, -48.95180234112112, 4.28172029886239, -29.25181561254189, -16.47893824725932, 127.23177073845451, -37.93457843823043, -46.26370399397668, -68.35245739870845, -29.36601427006844, -97.62578000985552, 110.69233168511644, -23.98252588862141, -87.95760213953896, 35.1163050337853, -95.68104953627522, -86.38719713713654, -8.181796888333814, -82.23446455537324, -57.58377900135889, -121.28657297804868, 13.70639899168555, 93.00965595761866, 20.236790360342006, 151.3537744955126, 18.595252743216836, -51.97702238189073, 10.770162885042808, 2.0465457203132997, -68.26653115437024, 7.196200893902509, -106.80396974437706, 52.30814625201634, 27.21809030731823, -2.927907751501147, -118.98175181328763, 54.80004027378612, -198.5173970311548, -45.46883001943995, -187.20890983990466, -146.70306121112083]

    evaluation_table, evaluation_table2, evaluation_table3 = input_table(individual[:48])
    side_continous = individual[49]
    move_eval = individual[48]
    n = 0  
    _, b, w = oth.count()
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
    if n <= 10:
        for y in range(8):
            for x in range(8):
                if board[y][x] == color:
                    score += evaluation_table[y][x]
                elif board[y][x] == opponent:
                    score -= evaluation_table[y][x]
    elif n <= 40:
        for y in range(8):
            for x in range(8):
                if board[y][x] == color:
                    score += evaluation_table2[y][x]
                elif board[y][x] == opponent:
                    score -= evaluation_table2[y][x]
                if y == 0 and 1<= x and 6 >=x:
                    if (board[y][x] == color and board[y][x-1] == 3-color) or (board[y][x] == color and board[y][x+1] == 3-color):
                        score += side_continous
                elif y == 7 and 1<= x and 6 >=x:
                    if (board[y][x] == color and board[y][x-1] == 3-color) or (board[y][x] == color and board[y][x+1] == 3-color):
                        score += side_continous
                elif x == 0 and 1 <= y and 6 >= y:
                    if (board[y][x] == color and board[y-1][x] == 3-color) or (board[y][x] == color and board[y+1][x] == 3-color):
                        score += side_continous
                elif x == 7 and 1 <= y and 6 >= y:    
                    if (board[y][x] == color and board[y-1][x] == 3-color) or (board[y][x] == color and board[y+1][x] == 3-color):
                        score += side_continous
                if (x,y) == (0,0) or (x,y) == (7,0) or (x,y) == (0,7) or (x,y) == (7,7):
                    if board[y][x] == color:
                        score+=1000
    else:
        for y in range(8):
            for x in range(8):
                if board[y][x] == color:
                    score += evaluation_table3[y][x]
                elif board[y][x] == opponent:
                    score -= evaluation_table3[y][x]
                if (x,y) == (0,0) or (x,y) == (7,0) or (x,y) == (0,7) or (x,y) == (7,7):
                    if board[y][x] == color:
                        score+=1000
        score -= len(oth.possible_puts(3-color))*(move_eval)
    if b > w :
        score += 1000
    
    return score if  color == 1 else -score

oth = GUI_Othello()
agent = alpha_beta_play(3,evaluate_board_ngn)
a = oth.play(agent)
print(a)
import matplotlib.pyplot as plt
from othello import Othello
from evaluate.evaluate_board_nkmr import evaluate_board_nkmr
from play.alpha_beta_play import alpha_beta_play
from play.script_play import script_play
from play.random_play import random_play
import random
from deap import base, creator, tools,algorithms

# 盤面評価関数
def evaluate_board_ngn(board, color) : 
    #individual = [76.32979597875611, 155.02097502448746, 80.21479588730273, -57.11627639363957, 6.368691011774339, 107.90361876092376, -43.315618467197325, 67.37930950146608, -157.71874531078652, -78.04039652208158, -48.95180234112112, 4.28172029886239, -29.25181561254189, -16.47893824725932, 127.23177073845451, -37.93457843823043, -46.26370399397668, -68.35245739870845, -29.36601427006844, -97.62578000985552, 110.69233168511644, -23.98252588862141, -87.95760213953896, 35.1163050337853, -95.68104953627522, -86.38719713713654, -8.181796888333814, -82.23446455537324, -57.58377900135889, -121.28657297804868, 13.70639899168555, 93.00965595761866, 20.236790360342006, 151.3537744955126, 18.595252743216836, -51.97702238189073, 10.770162885042808, 2.0465457203132997, -68.26653115437024, 7.196200893902509, -106.80396974437706, 52.30814625201634, 27.21809030731823, -2.927907751501147, -118.98175181328763, 54.80004027378612, -198.5173970311548, -45.46883001943995, -187.20890983990466, -146.70306121112083]
    #individual = [100,10,40,30,10,5,8,6,40,8,15,10,30,6,10,10,100,10,40,30,10,5,8,6,40,8,15,10,30,6,10,10,100,10,40,30,10,5,8,6,40,8,15,10,30,6,10,10,-100,50]
    n = 0  
    
    for y in range(8):
        for x in range(8):
            if board[y][x] != 0:
                n += 1
    oth=Othello()
    _, b, w = oth.count()
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
        
        score -= len(oth.possible_puts(3-color))*(move_eval)
        oth.board=board
    return score if  color == 1 else -score

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

# 遺伝的アルゴリズムの適応度評価関数
def othello_eval(individual):
    result = 0
    #print(individual)
    global evaluation_table, evaluation_table2, evaluation_table3
    othello = Othello()
    board = othello.board
    global move_eval
    global side_continous
    side_continous = individual[49]
    move_eval = individual[48]
    agent_1 = alpha_beta_play(0, evaluate_board_nkmr)
    evaluation_table, evaluation_table2, evaluation_table3 = input_table(individual[:48])
    agent_2 = alpha_beta_play(0, evaluate_board_ngn)
    a = othello.play(agent_2, agent_1,do_print = False)
    _, b, w = othello.count()
    result += b-w
    if a == 1:
        b = 0
        for i in range(10):
            agent = alpha_beta_play(0,random_play)
            a = othello.play(agent,agent_2)
            if a == 2:
                b += 1
        if b >= 7:
            result += b*100
            print(individual)
    if board[0][0] == 1:
        result += 5
    if board[7][0] == 1:
        result += 5
    if board[0][7] == 1:
        result += 5
    if board[7][7] == 1:
        result += 5
    return result,

# メイン関数
def main():
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax)

    toolbox = base.Toolbox()
    toolbox.register("attr_int", random.randint, -1000, 1000)  # -100から100の整数を生成
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_int, 50)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("select", tools.selTournament, tournsize=3)
    toolbox.register("mate", tools.cxBlend, alpha=0.3)
    toolbox.register("evaluate", othello_eval)
    toolbox.register("mutate", tools.mutGaussian, mu=[0]*50, sigma=[10]*50, indpb=0.3)
    pop = toolbox.population(n=15)
    num_generations = 100
    
    # 各世代の最高適応度を保存するリスト
    fitness_list = []
    
    for gen in range(num_generations):
        if gen%10 == 0:
            print(gen)
        elite = tools.selBest(pop, 1)
        offspring = toolbox.select(pop, len(pop)-1 )
        offspring = list(map(toolbox.clone, offspring))
        offspring.append(toolbox.clone(elite[0]))


        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < 0.5:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        offspring.extend(list(tools.selBest(pop, 2)))


        for mutant in offspring:
            if random.random() < 0.5:
                toolbox.mutate(mutant)
                del mutant.fitness.values
        fitnesses = list(map(toolbox.evaluate,pop))
        fitness_list.append(max([i for i, in fitnesses]))
        



        for ind, fit in zip(pop, fitnesses):
            ind.fitness.values = fit
        pop[:] = offspring






    best_individual = tools.selBest(pop, 1)[0]
    print("\nBest Evaluation Table:", best_individual)

    plt.plot(range(len(fitness_list)), fitness_list, marker='o', linestyle='-', color='b')
    plt.title("Fitness over Generations")
    plt.xlabel("Generation")
    plt.ylabel("Fitness")
    plt.grid(True)
    plt.show()

    print("Best Evaluation Table:", best_individual)





if __name__ == "__main__":
    main()
        
import matplotlib.pyplot as plt
from othello import Othello
from evaluate.evaluate_board_nkmr import evaluate_board_nkmr
from play.alpha_beta_play import alpha_beta_play
from play.script_play import script_play
import random
from deap import base, creator, tools
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

    score = 0
    opponent = 3-color
    if n <= 20:
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
    else:
        for y in range(8):
            for x in range(8):
                if board[y][x] == color:
                    score += evaluation_table3[y][x]
                elif board[y][x] == opponent:
                    score -= evaluation_table3[y][x]

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


def othello_eval(individual):
    global evaluation_table
    global evaluation_table2
    global evaluation_table3
    othello = Othello()
    agent_1 = alpha_beta_play(0,evaluate_board_nkmr)
    evaluation_table = input_table(individual)[0]
    evaluation_table2 = input_table(individual)[1]
    evaluation_table3 = input_table(individual)[2]
    agent_2 = alpha_beta_play(0,evaluate_board_ngn)
    othello.play(agent_2,agent_1,do_print = False)
    _,b,w=othello.count()
    result = b-w
    return result,



def main():
    fitness_list = []


    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax) 

    toolbox = base.Toolbox()
    toolbox.register("attr_float", random.uniform, -100, 100) 
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_float, 48)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", othello_eval)
    toolbox.register("mate", tools.cxBlend, alpha=0.5)
    toolbox.register("mutate", tools.mutGaussian, mu=[0]*48, sigma=[10]*48, indpb=0.1)
    toolbox.register("select", tools.selTournament, tournsize=4)


    pop = toolbox.population(n = 12)
    num_generations = 10
    for gen in range(num_generations):
        if gen%10 == 0:
            print(gen*10)
        elite = tools.selBest(pop, 1)
        offspring = toolbox.select(pop, len(pop)-1 )
        offspring = list(map(toolbox.clone, offspring))
        offspring.append(toolbox.clone(elite[0]))


        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < 0.2:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        offspring.extend(list(tools.selBest(pop, 1)))


        for mutant in offspring:
            if random.random() < 0.2:
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
        
import matplotlib.pyplot as plt
from othello import Othello
from evaluate.evaluate_board_ngn import evaluate_board_ngn
from evaluate.evaluate_board_ngn import evaluation_table,evaluate_board_ngn
from evaluate.evaluate_board_ngn2 import evaluate_board_ngn2
from evaluate.evaluate_board_ngn2 import evaluation_table2,evaluate_board_ngn2
from evaluate.evaluate_board_nkmr import evaluate_board_nkmr
from play.alpha_beta_play import alpha_beta_play
import random
from deap import base, creator, tools
from deap import algorithms


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

def othello_eval(individual):
    global elite_individual
    global evaluation_table
    global evaluation_table2

    if elite_individual is None:
        ageny = alpha_beta_play(0,evaluate_board_nkmr)
        evaluation_table = input_table(individual)       
        agent = alpha_beta_play(0,evaluate_board_ngn)
        othello = Othello()
        a = othello.play(agent,ageny)
        _,b,w=othello.count()
        res = b-w
        if a == 1:
            return 100+res,
        else:
            return res,
    else:
        othello = Othello()
        evaluation_table2 = input_table(elite_individual)
        agent_1 = alpha_beta_play(0,evaluate_board_ngn2)
        evaluation_table = input_table(individual)        
        agent_2 = alpha_beta_play(0,evaluate_board_ngn)
        a = othello.play(agent_2,agent_1)
        _,b,w=othello.count()
        res = b-w 
        if a == 1:
            return 100+res,
        else:
            return res,

elite_first_element = []
elite_individual = None

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax) 

toolbox = base.Toolbox()
toolbox.register("attr_float", random.uniform, -100, 100) 
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_float, 16)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("evaluate", othello_eval)
toolbox.register("mate", tools.cxBlend, alpha=0.5)
toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=0.5, indpb=0.6)
toolbox.register("select", tools.selTournament, tournsize=3)


population = toolbox.population(n=10)

elite_size = 1

num_generations = 200
for gen in range(num_generations):
    
    elite = tools.selBest(population, elite_size)
    
    if elite_individual is not None:
        elite_first_element.append(elite_individual[0])
    elite_individual = list(elite[0])
    

    
    offspring = toolbox.select(population, len(population) - elite_size)
    offspring = list(map(toolbox.clone, offspring))

    
    for child1, child2 in zip(offspring[::2], offspring[1::2]):
        if random.random() < 0.5:
            toolbox.mate(child1, child2)
            del child1.fitness.values
            del child2.fitness.values

    
    for mutant in offspring:
        if random.random() < 0.8:
            toolbox.mutate(mutant)
            del mutant.fitness.values


    offspring.extend(elite)

    fitnesses = list(map(toolbox.evaluate, offspring))
    for ind, fit in zip(offspring, fitnesses):
        ind.fitness.values = fit

    population[:] = offspring

    
best_individual = tools.selBest(population, 1)[0]
print("\nBest Evaluation Table:", best_individual)

plt.plot(range(len(elite_first_element)), elite_first_element, marker='o', linestyle='-', color='b')
plt.title("First Element of Elite Individuals over Generations")
plt.xlabel("Generation")
plt.ylabel("First Element of Elite Individual")
plt.grid(True)
plt.show()

print("Best Evaluation Table:", best_individual)



          
        
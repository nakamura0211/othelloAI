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
    othello = Othello()
    evaluation_table2 = input_table(elite_individual)
    agent_1 = alpha_beta_play(0,evaluate_board_ngn2)
    evaluation_table = input_table(individual)        
    agent_2 = alpha_beta_play(0,evaluate_board_ngn)
    a = othello.play(agent_2,agent_1,do_print = False)
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


population = toolbox.population(n=5)


num_generations = 20
for gen in range(num_generations):
    
    
    
    if elite_individual is not None:
        elite_first_element.append(elite_individual[0])
    elite_individual = list(tools.selBest(population, 1)[0])
    

    
    offspring = toolbox.select(population, len(population) - 1)
    offspring = list(map(toolbox.clone, offspring))

    
    for child1, child2 in zip(offspring[::2], offspring[1::2]):
        if random.random() < 0.5:
            toolbox.mate(child1, child2)
            del child1.fitness.values
            del child2.fitness.values

    
    for mutant in offspring:
        if random.random() < 0.5:
            toolbox.mutate(mutant)
            del mutant.fitness.values


    offspring.extend(list(tools.selBest(population, 1)))

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


##これで出来上がりました。ざこです
# [9.309686802648422, -55.228733286729415, -22.841360389475902, -7.891116260892756
# , 22.57822837847436, -27.68406246097886, 118.59463330412778, 107.08332483333382
# , -49.993867933880345, 57.4276713400455, -71.17219667234166, -17.566181264443465
# , -6.302710011742824, -73.75138380531219, -47.830920676357756, 31.044693419323078]


          
        
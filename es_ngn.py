import matplotlib.pyplot as plt
from othello import Othello
from evaluate.evaluate_board_ngn import evaluate_board_ngn
from evaluate.evaluate_board_ngn import evaluate_board_ngn
from evaluate.evaluate_board_ngn2 import evaluate_board_ngn2
from evaluate.evaluate_board_ngn2 import evaluate_board_ngn2
from evaluate.evaluate_board_nkmr import evaluate_board_nkmr
from play.alpha_beta_play import alpha_beta_play
from play.script_play import script_play
import random
from deap import base, creator, tools

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
evaluation_table2 = [
    [100,10,40,30,30,40,10,100],
    [10,5,8,6,6,8,5,10],
    [40,8,15,10,10,15,8,40],
    [30,6,10,10,10,10,6,30],
    [30,6,10,10,10,10,6,30],
    [40,8,15,10,10,15,8,40],
    [10,5,8,6,6,8,5,10],
    [100,10,40,30,30,40,10,100]
    ]
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
    resalt = b-w 
    if a == 1:
        fitness = 100+resalt
        
        return fitness,
    else:
        fitness = resalt
        
        return fitness,


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
toolbox.register("mutate", tools.mutGaussian, mu=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], sigma=[20,20,20,20,20,20,20,20,20,20,20,20,20,20,20,20], indpb=0.6)
toolbox.register("select", tools.selTournament, tournsize=3)


pop = toolbox.population(n = 10)
num_generations = 5000
for gen in range(num_generations):
    if gen%100 == 0:
        print(gen*10)
    
    if elite_individual is not None:
        elite_first_element.append(elite_individual[0])
    elite_individual = list(tools.selBest(pop, 1)[0])
    

    
    offspring = toolbox.select(pop, len(pop)-1 )
    offspring = list(map(toolbox.clone, offspring))
    


    for child1, child2 in zip(offspring[::2], offspring[1::2]):
        if random.random() < 0.5:
            toolbox.mate(child1, child2)
            del child1.fitness.values
            del child2.fitness.values
    
    offspring.extend(list(tools.selBest(pop, 1)))

    
    for mutant in offspring:
        if random.random() < 0.5:
            toolbox.mutate(mutant)
            del mutant.fitness.values
    fitnesses = list(map(toolbox.evaluate, offspring))
    
    
    
    for ind, fit in zip(offspring, fitnesses):
        ind.fitness.values = fit

    pop[:] = offspring

    



    
best_individual = tools.selBest(pop, 1)[0]
print("\nBest Evaluation Table:", best_individual)

plt.plot(range(len(elite_first_element)), elite_first_element, marker='o', linestyle='-', color='b')
plt.title("First Element of Elite Individuals over Generations")
plt.xlabel("Generation")
plt.ylabel("First Element of Elite Individual")
plt.grid(True)
plt.show()

print("Best Evaluation Table:", best_individual)





          
        
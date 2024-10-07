from othello import Othello
from evaluate.evaluate_board_ngn import evaluate_board_ngn
from evaluate.evaluate_board_ngn import evaluation_table,evaluate_board_ngn 
from evaluate.evaluate_board_nkmr import evaluate_board_nkmr
from play.alpha_beta_play import alpha_beta_play
import random
from deap import base, creator, tools
from deap import algorithms




individual = [1.0,0.1,0.4,0.3,0.3,0.4,0.1,1.0
              ,0.1,0.05,0.08,0.06,0.06,0.08,0.05,0.1
              ,0.4,0.08,0.15,0.1,0.1,0.15,0.08,0.4
              ,0.3,0.06,0.1,0.1,0.1,0.1,0.06,0.3
              ,0.3,0.06,0.1,0.1,0.1,0.1,0.06,0.3
              ,0.4,0.08,0.15,0.1,0.1,0.15,0.08,0.4
              ,0.1,0.05,0.08,0.06,0.06,0.08,0.05,0.1
              ,1.0,0.1,0.4,0.3,0.3,0.4,0.1,1.0]
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax) 


def othello_eval(individual):
    ageny = alpha_beta_play(3,evaluate_board_nkmr)
    for i in range(8):
        for j in range(8):
            evaluation_table[i][j] = individual[i*8 + j]
    agent = alpha_beta_play(3,evaluate_board_ngn)
    othello = Othello()
    a = othello.play(agent,ageny)
    if a == 1:
        return 1,
    else:
        return 0,

toolbox = base.Toolbox()
toolbox.register("attr_float", random.uniform, -1.0, 1.0) 
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_float, n=64)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
population = toolbox.population(n=100)
toolbox.register("evaluate", othello_eval)
toolbox.register("mate", tools.cxBlend, alpha=0.5)
toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=0.1, indpb=0.2)
toolbox.register("select", tools.selTournament, tournsize=3)
population, log = algorithms.eaSimple(population, toolbox, cxpb=0.5, mutpb=0.2, ngen=7, verbose=True)
best_individual = tools.selBest(population, k=1)[0]
print("Best Evaluation Table:", best_individual)
from domain import OthelloEnv
from domain.models import *
from agent.AlphaBetaAgent import AlphaBetaAgent
from agent.MctsAgent import MctsAgent, McAgent
from agent.RandomAgent import RandomAgent
from agent.StartsWithRandomAgent import StartsWithRandomAgent
from agent.TerminalAgent import TerminalAgent
from time import perf_counter
from tqdm import tqdm
import ray

target_agent = MctsAgent(300)
opp_agent = MctsAgent(300)
simulation_times = 10
black_win = 0
white_win = 0
for i in tqdm(range(1, simulation_times + 1)):
    winner = OthelloEnv.play(target_agent, opp_agent, do_print=False)
    if winner == Color.BLACK:
        black_win += 1
    elif winner == Color.WHITE:
        white_win += 1
print(
    f"target:{black_win/simulation_times*100}({black_win}/{simulation_times}) opp:{white_win/simulation_times*100}({white_win}/{simulation_times}) even:{(simulation_times-black_win-white_win)/simulation_times}({simulation_times-black_win-white_win}/{simulation_times})"
)

black_win = 0
white_win = 0

for i in tqdm(range(1, simulation_times + 1)):
    winner = OthelloEnv.play(opp_agent, target_agent, do_print=False)
    if winner == Color.BLACK:
        black_win += 1
    elif winner == Color.WHITE:
        white_win += 1
print(
    f"\ntarget:{white_win/simulation_times*100}({white_win}/{simulation_times}) opp:{black_win/simulation_times*100}({black_win}/{simulation_times}) even:{(simulation_times-black_win-white_win)/simulation_times}({simulation_times-black_win-white_win}/{simulation_times})"
)

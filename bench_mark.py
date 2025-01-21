from domain import OthelloEnv
from domain.models import *
from agent import *
from time import perf_counter
from tqdm import tqdm
import ray


def bench_mark(target_agent: Agent, opp_agent: Agent, simulation_times: int):
    _bench_mark(target_agent, opp_agent, simulation_times, False)
    _bench_mark(opp_agent, target_agent, simulation_times, True)


def _bench_mark(black: Agent, white: Agent, simulation_times: int, rev: bool):
    black_win = 0
    white_win = 0
    black_time = 0
    white_time = 0
    for i in tqdm(range(1, simulation_times + 1)):
        state = OthelloEnv.reset()
        done = False
        while not done:
            agent = black if state.color == Color.BLACK else white
            start = perf_counter()
            action = agent.act(state)
            t = perf_counter() - start
            if state.color == Color.BLACK:
                black_time += t
            else:
                white_time += t
            state, reward, done = OthelloEnv.step(state, action)
        winner = OthelloEnv.winner(state)
        if winner == Color.BLACK:
            black_win += 1
        elif winner == Color.WHITE:
            white_win += 1
    if rev:
        print(
            f"target:{white_win/simulation_times*100}({white_win}/{simulation_times}) {format(white_time)} opp:{black_win/simulation_times*100}({black_win}/{simulation_times}) {format(black_time)} even:{(simulation_times-black_win-white_win)*100/simulation_times}({simulation_times-black_win-white_win}/{simulation_times})"
        )
    else:
        print(
            f"target:{black_win/simulation_times*100}({black_win}/{simulation_times}) {format(black_time)} opp:{white_win/simulation_times*100}({white_win}/{simulation_times}) {format(white_time)} even:{(simulation_times-black_win-white_win)*100/simulation_times}({simulation_times-black_win-white_win}/{simulation_times})"
        )


def format(seconds: float) -> str:
    minutes = int(seconds) // 60
    remaining_seconds = int(seconds) % 60
    ms = int((seconds - int(seconds)) * 1000)
    return f"{minutes:02}:{remaining_seconds:02}.{ms:03}"


if __name__ == "__main__":
    dqn = DqnAgent(0, 0.2, dueling=True, double=False, name="result/dqn_day3.keras")
    target_agent = AlphaBetaAgent(5, Q_func=dqn.q_values)
    opp_agent = McAgent(800)
    simulation_times = 50
    bench_mark(target_agent, opp_agent, simulation_times)

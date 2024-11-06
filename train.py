from domain import OthelloEnv
from domain.models import *
from agent.DqnAgent import DqnAgent, Memory, Experience, SegmentMemory
from agent.RandomAgent import RandomAgent
from tqdm import tqdm
import ray
from ray.experimental import tqdm_ray
from collections import deque
import tensorflow as tf
import numpy as np
import sys
import gc


def train():
    num_cpus = 7
    ray.init(num_cpus=num_cpus)
    global_memory = SegmentMemory(80000, 4)  # Memory(50000)
    agent = DqnAgent()
    n_episodes = 10000
    each_episodes = 50
    batch_size = 1024
    n_parallel_selfplay = num_cpus
    current_weights = agent.model.get_weights()
    work_in_progresses = [
        self_play.remote(agent.epsilon, current_weights, each_episodes)
        for _ in range(n_parallel_selfplay)
    ]
    for i in tqdm(range(1, n_episodes // 50 + 1), file=sys.stdout):
        for _ in tqdm(range(50), file=sys.stdout):
            finished, work_in_progresses = ray.wait(work_in_progresses, num_returns=1)
            memory = ray.get(finished[0])
            global_memory.add(memory)
            # 120*each_episodes ぐらい追加される
            work_in_progresses.extend(
                [self_play.remote(agent.epsilon, current_weights, each_episodes)]
            )
            if global_memory.length() > batch_size:
                batch = global_memory.sample(batch_size)
                agent.train(batch)
                del current_weights
                gc.collect()
                current_weights = agent.model.get_weights()
        agent.sync_network()
        try:
            agent.model.save(f"/content/drive/My Drive/Colab Notebooks/dqn.keras")
        except:
            pass
        agent.model.save(f"model/dqn{i*50}.keras")


@ray.remote(num_cpus=1)
def self_play(epsilon: int, weights: list, play_num):
    agent = DqnAgent(epsilon=epsilon, weights=weights)
    memory: list[Experience] = []
    for i in range(play_num):
        state = OthelloEnv.reset()
        while True:
            action = agent.act(state)
            next_state, reward, done = OthelloEnv.step(state, action)
            memory.append(Experience(state, action, reward, next_state, done))
            for s, a, s2 in zip(state.turn(), action.turn(), next_state.turn()):
                memory.append(Experience(s, a, reward, s2, done))
            state = next_state
            if done:
                break

    return memory


if __name__ == "__main__":
    train()

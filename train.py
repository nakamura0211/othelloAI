from domain import OthelloEnv
from domain.models import *
from agent.DqnAgent import DqnAgent, Memory, Experience
from agent.RandomAgent import RandomAgent
from tqdm import tqdm
import ray
from ray.experimental import tqdm_ray
from collections import deque
import tensorflow as tf
import numpy as np
import sys


def train():
    num_cpus = 7
    ray.init(num_cpus=num_cpus)
    global_memory = Memory(50000)
    agent = DqnAgent()
    n_episodes = 10000
    each_episodes = 50
    batch_size = 1024
    n_parallel_selfplay = num_cpus
    current_weights = ray.put(agent.model.get_weights())
    work_in_progresses = [
        self_play.remote(agent.epsilon, current_weights, each_episodes)
        for _ in range(n_parallel_selfplay)
    ]
    for i in tqdm(range(1, n_episodes // 50 + 1), file=sys.stdout):
        for _ in tqdm(range(50), file=sys.stdout):
            finished, work_in_progresses = ray.wait(work_in_progresses, num_returns=1)
            memory, td_err = ray.get(finished[0])
            global_memory.add(memory, td_err)
            # 120*each_episodes ぐらい追加される
            work_in_progresses.extend(
                [self_play.remote(agent.epsilon, current_weights, each_episodes)]
            )
            if global_memory.length() > batch_size:
                batch = global_memory.sample(batch_size)
                agent.train(batch)
                current_weights = ray.put(agent.model.get_weights())
        agent.sync_network()
        try:
            agent.model.save(f"/content/drive/My Drive/Colab Notebooks/dqn.keras")
        except:
            pass
        agent.model.save(f"model/dqn{i*50}.keras")


@ray.remote(num_cpus=1, num_gpus=1)
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

    err = []
    for exp in memory:
        _, b, w = OthelloEnv.count(exp.state)
        err.append(b + w)
    return memory, err

    nx_state = []
    cur_state = []
    for exp in memory:
        nx_state.append(exp.next_state.to_image())
        cur_state.append(exp.state.to_image())

    nx_pl = agent.model.predict(np.array(nx_state), verbose=0)
    nx_tgt_pl = agent.target.predict(np.array(nx_state), verbose=0)
    cur_pl = agent.model.predict(np.array(cur_state), verbose=0)

    """td_err = []
    for i in range(len(memory)):
        valid = {a.index for a in OthelloEnv.valid_actions(memory[i].next_state)}

        act = np.argmax([v if i not in valid else -2 for i, v in enumerate(nx_pl[i])])
        if memory[i].state.color == memory[i].next_state.color:
            td_err.append(
                memory[i].reward
                + agent.gamma * nx_tgt_pl[i][act]
                - cur_pl[i][memory[i].action.index]
            )
        else:
            td_err.append(
                memory[i].reward
                - agent.gamma * nx_tgt_pl[i][act]
                - cur_pl[i][memory[i].action.index]
            )"""
    return memory, td_err


if __name__ == "__main__":
    train()

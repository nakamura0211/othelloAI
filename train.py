from domain import OthelloEnv
from domain.models import *
from agent.DqnAgent import (
    DqnAgent,
    Memory,
    Experience,
    SegmentMemory,
    SimpleMemory,
    Experiences,
    SimpleMultiStepMemory,
)
from agent.AlphaBetaAgent import AlphaBetaAgent
from tqdm import tqdm
import ray
from ray.experimental import tqdm_ray
from collections import deque
import tensorflow as tf
import numpy as np
import sys
import gc


double = True
dueling = False
multistep = False
multistep_length = 2


def train():
    num_cpus = 7
    ray.init(num_cpus=num_cpus)
    global_memory = SimpleMemory(80000)  # SegmentMemory(80000, 4)  # Memory(50000)
    agent = DqnAgent(dueling=dueling, double=double, multistep=multistep)
    n_episodes = 10000
    each_episodes = 50
    batch_size = 1024
    n_parallel_selfplay = num_cpus
    current_weights = agent.model.get_weights()
    work_in_progresses = [
        (self_play_multistep if multistep else self_play).remote(
            agent.epsilon, agent.pb_epsilon, current_weights, each_episodes
        )
        for _ in range(n_parallel_selfplay)
    ]
    for i in tqdm(range(1, n_episodes + 1), file=sys.stdout):
        finished, work_in_progresses = ray.wait(work_in_progresses, num_returns=1)
        memory = ray.get(finished[0])
        global_memory.add(memory)
        # 120*each_episodes ぐらい追加される
        work_in_progresses.extend(
            [
                (self_play_multistep if multistep else self_play).remote(
                    agent.epsilon, agent.pb_epsilon, current_weights, each_episodes
                )
            ]
        )
        if global_memory.length() > batch_size:
            batch = global_memory.sample(batch_size)
            agent.train(batch)
            current_weights = agent.model.get_weights()

        if i % 5 == 0:
            agent.sync_network()
        if i % 50 == 0:
            try:
                agent.model.save(f"/content/drive/My Drive/Colab Notebooks/dqn.keras")
            except:
                pass
            e = agent.epsilon
            pe = agent.pb_epsilon
            agent.epsilon = 0
            agent.pb_epsilon = 0
            t, o = bench_mark(agent)
            agent.epsilon = e
            agent.pb_epsilon = pe
            print(f"\nscore: {t-o}")

            agent.model.save(f"model/dqn{i}.keras")


def bench_mark(
    target_agent: Agent,
    opp_agent: Agent = AlphaBetaAgent(0),
    simulation_times=1,
):
    target = 0
    opp = 0
    for i in range(simulation_times):
        _, b, w = OthelloEnv.count(
            OthelloEnv.play(target_agent, opp_agent, do_print=False)
        )
        target += b
        opp += w
    for i in range(simulation_times):
        _, b, w = OthelloEnv.count(
            OthelloEnv.play(opp_agent, target_agent, do_print=False)
        )
        target += w
        opp += b
    return target, opp


@ray.remote(num_cpus=1)
def self_play(epsilon: float, pb_epsilon: float, weights: list, play_num):
    agent = DqnAgent(
        epsilon=epsilon,
        pb_epsilon=pb_epsilon,
        weights=weights,
        dueling=dueling,
        double=double,
        multistep=multistep,
    )
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


@ray.remote(num_cpus=1)
def self_play_multistep(epsilon: float, pb_epsilon: float, weights: list, play_num):
    agent = DqnAgent(
        epsilon=epsilon,
        pb_epsilon=pb_epsilon,
        weights=weights,
        dueling=dueling,
        double=double,
        multistep=multistep,
    )
    memory: list[Experiences] = []
    for i in range(play_num):
        state = OthelloEnv.reset()
        end = False
        while True:
            rewards = []
            states = [state]
            actions = []
            for j in range(multistep_length):
                action = agent.act(state)
                state, reward, done = OthelloEnv.step(state, action)
                if done and j != multistep_length - 1:
                    end = True
                    break
                states.append(state)
                rewards.append(reward)
                actions.append(action)
            if end:
                break
            done = OthelloEnv.is_done(state)
            memory.append(Experiences(multistep_length, states, actions, rewards, done))
            turned_states = ([], [], [])
            for state in states:
                for i, s in enumerate(state.turn()):
                    turned_states[i].append(s)
            turned_actions = ([], [], [])
            for action in actions:
                for i, a in enumerate(action.turn()):
                    turned_actions[i].append(a)
            for j in range(3):
                memory.append(
                    Experiences(
                        multistep_length,
                        turned_states[i],
                        turned_actions[i],
                        rewards,
                        done,
                    )
                )
            if done:
                break

    return memory


if __name__ == "__main__":
    train()

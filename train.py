from domain import OthelloEnv
from agent.DqnAgent import DqnAgent, DqnNetwork
from agent.RandomAgent import RandomAgent
from tqdm import tqdm
import ray
from ray.experimental import tqdm_ray
from collections import deque


def train():
    num_cpus = 8
    ray.init(num_cpus=num_cpus, num_gpus=1)
    agent = DqnAgent()
    n_episodes = 10000
    each_episodes = 50
    batch_size = 1024
    n_parallel_selfplay = num_cpus - 1
    current_weights = agent.model.get_weights()
    work_in_progresses = [
        self_play.remote(agent.epsilon, current_weights, each_episodes)
        for _ in range(n_parallel_selfplay)
    ]
    for i in tqdm(range(1, n_episodes // 50 + 1)):
        for _ in tqdm(range(50)):
            finished, work_in_progresses = ray.wait(work_in_progresses, num_returns=1)
            agent.memory.extend(
                ray.get(finished[0])
            )  # 120*each_episodes ぐらい追加される
            work_in_progresses.extend(
                [self_play.remote(agent.epsilon, current_weights, each_episodes)]
            )
            if len(agent.memory) > batch_size:
                agent.train(batch_size)
                current_weights = agent.model.get_weights()

        agent.model.save(f"model/dqn{i*50}.keras")


@ray.remote(num_cpus=1)
def self_play(epsilon: int, weights: list, play_num):
    agent = DqnAgent(epsilon=epsilon, weights=weights)
    memory = []
    for i in range(play_num):
        state = OthelloEnv.reset()
        while True:
            action = agent.act(state)
            next_state, reward, done = OthelloEnv.step(state, action)
            memory.append((state, action, reward, next_state, done))
            for s, a, s2 in zip(state.turn(), action.turn(), next_state.turn()):
                memory.append((s, a, reward, s2, done))
            state = next_state
            if done:
                break
    return memory


if __name__ == "__main__":
    train()

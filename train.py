from domain import OthelloEnv
from agent.DqnAgent import DqnAgent, DqnNetwork
from agent.RandomAgent import RandomAgent
from tqdm import tqdm
import ray
from collections import deque


def train():
    agent = DqnAgent()
    random_agent = RandomAgent()
    n_episodes = 10000
    each_episodes = 50
    batch_size = 512
    n_parallel_selfplay = 4
    scores = []
    replay_buffer = deque(maxlen=20000)
    n = 0
    current_weights = agent.model.get_weights()
    work_in_progresses = [
        self_play.remote(agent.epsilon, current_weights, each_episodes)
        for _ in range(n_parallel_selfplay)
    ]
    while n < n_episodes:
        print(n)
        for _ in tqdm(range(50)):
            finished, work_in_progresses = ray.wait(work_in_progresses, num_returns=1)
            agent.memory.extend(ray.get(finished[0]))
            work_in_progresses.extend(
                [
                    self_play.remote(agent.epsilon, current_weights, each_episodes)
                ]  # 1500個ぐらい
            )
            n += 1
            if len(agent.memory) > batch_size:
                agent.train(batch_size)
        agent.model.save(f"model/dqn{n}.keras")
        current_weights = agent.model.get_weights()


@ray.remote
def self_play(epsilon: int, weights: list, play_num):
    agent = DqnAgent(epsilon=epsilon, weights=weights)
    memory = []
    for i in range(play_num):
        state = OthelloEnv.reset()
        while True:
            action = agent.act(state)
            next_state, reward, done = OthelloEnv.step(state, action)
            memory.append((state, action, reward, next_state, done))
            state = next_state
            if done:
                break
    return memory


if __name__ == "__main__":
    train()

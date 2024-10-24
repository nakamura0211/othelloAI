from domain import OthelloEnv
from agent.DqnAgent import DqnAgent
from agent.RandomAgent import RandomAgent
from tqdm import tqdm
from typing import Literal

a = Literal["hello"]

agent = DqnAgent()
agent.load("model/dqn_relu500.keras")
random_agent = RandomAgent()
n_episodes = 10000
batch_size = 48
scores = []
# 優先度付きリプレイで、後ろの方から学習させてみたい
for e in tqdm(range(1, n_episodes + 1)):
    state = OthelloEnv.reset()
    while True:
        action = agent.act(state)
        next_state, reward, done = OthelloEnv.step(state, action)
        agent.remember(state, action, reward, next_state, done)
        state = next_state
        if done:
            break

    if e % 100 == 0:
        last_state = OthelloEnv.play(black=agent, white=random_agent, do_print=False)
        _, b, w = OthelloEnv.count(last_state)
        scores.append(b - w)
        print(scores)
        print(agent.epsilon)
        agent.model.save(f"model/dqn_relu{e}.keras")

    if len(agent.memory) > batch_size:
        agent.train(batch_size)

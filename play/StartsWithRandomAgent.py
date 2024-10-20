from type import Agent, State, Action
from play.random_play import RandomAgent


class StartsWithRandomAgent(Agent):
    def __init__(self, agent: Agent, random_num=5):
        self.agent = agent
        self.random_agent = RandomAgent()
        self.random_num = random_num

    def act(self, state: State) -> Action:
        if self.random_num > 0:
            self.random_num -= 1
            return self.random_agent.act(state)
        return self.agent.act(state)

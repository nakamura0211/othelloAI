from domain.models import *
from domain import OthelloEnv
import random


class RandomAgent(Agent):
    def act(self, state: State):
        return random.choice(OthelloEnv.valid_actions(state))

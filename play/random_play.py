from othello import Othello
import random

import OthelloEnv
from type import State, Action, Agent


def random_play(othello: Othello, color: int):
    return random.choice(othello.possible_puts(color))


class RandomAgent(Agent):
    def __call__(self, othello: Othello, color: int):
        return random_play(othello, color)

    def act(self, state: State):
        return random.choice(OthelloEnv.valid_actions(state))

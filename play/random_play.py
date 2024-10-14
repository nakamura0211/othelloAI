from OthelloEnv import decode_state
from othello import Othello
import random

from play.agent import Agent


def random_play(othello: Othello, color:int):
    return random.choice(othello.possible_puts(color))


class RandomAgent(Agent):
    def __call__(self,othello: Othello, color:int):
        return random_play(othello, color)

    def act(self,state):
        othello=decode_state(state)
        return random_play(othello, othello.color)

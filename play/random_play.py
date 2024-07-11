from othello import Othello
import random


def random_play(othello: Othello, color:int):
    return random.choice(othello.possible_puts(color))

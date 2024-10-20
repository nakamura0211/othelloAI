from othello import Othello
import random
from play.random_play import random_play
import math
from play.mcts import MctsNode
import numpy as np
import OthelloEnv
from tqdm import tqdm
from type import Agent, Action, State


def mcts_agent(othello: Othello, color: int):
    root_node = MctsNode([], othello)
    for i in range(1000):
        root_node.search_node_must_be_playouted().playout()
    root_node.print_tree(0)
    return othello.possible_puts(color)[
        np.argmax([child.chosen for child in root_node.children])
    ]


class MctsAgent(Agent):
    def __init__(self, playout_num: int) -> None:
        self.playout_num = playout_num

    def act(self, state: State) -> Action:
        root_node = MctsNode([], state)
        for i in tqdm(range(self.playout_num)):
            root_node.search_node_must_be_playouted().playout()
        root_node.print_tree(0)
        return OthelloEnv.valid_actions(state)[
            np.argmax([child.chosen for child in root_node.children])
        ]


def mc_agent(othello: Othello, color: int):
    puts = othello.possible_puts(color)
    simulation_num = 300
    win_number = [0] * (len(puts))
    chosen = [1] * (len(puts))
    uct_list = [0] * (len(puts))
    chirdren_num = len(puts)
    for i in range(simulation_num):
        for j in range(chirdren_num):
            uct = win_number[j] / chosen[j] + math.sqrt(2 * math.log(i + 1) / chosen[j])
            uct_list[j] = uct
        pon = 0
        uct_max = 0
        for j in range(chirdren_num):
            if uct_max != max(uct_max, uct_list[j]):
                uct_max = uct_list[j]
                pon = j
        put = puts[pon]

        x, y = map(int, put)
        othello_copy = othello.copy()
        othello_copy.put(x, y, color)
        syouhai = othello_copy.play(
            random_play, random_play, first_color=3 - color, do_print=False
        )
        if syouhai == color:
            win_number[pon] += 1
        chosen[pon] += 1
    elit = 0
    elit_index = 0

    for i in range(len(puts)):
        if elit != max(elit, win_number[i] / chosen[i]):
            elit_index = i
            elit = max(elit, win_number[i] / chosen[i])
    return puts[elit_index]

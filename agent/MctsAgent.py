import math
from typing import Self
from copy import copy
from domain.models import *
import domain.OthelloEnv as OthelloEnv
import math
import numpy as np
from domain.models import *
from agent.RandomAgent import RandomAgent
import ray
import tqdm
from ray.experimental import tqdm_ray
from time import perf_counter

if not ray.is_initialized:
    ray.init(num_cpus=4)


class MctsAgent(Agent):
    def __init__(
        self, playout_num: int, verbose: int = 0, use_ray: bool = True
    ) -> None:
        self.playout_num = playout_num
        self.verbose = verbose
        self.use_ray = use_ray

    @staticmethod
    @ray.remote
    def mcts_playout(mcts_node, playout_num: int, verbose: int = 0):
        for _ in (
            tqdm_ray.tqdm(range(playout_num)) if verbose > 0 else range(playout_num)
        ):
            mcts_node.search_node_must_be_playouted().playout()
        return mcts_node

    def act_with_ray(self, state: State) -> Action:
        root_node = MctsNode([], state)
        root_node.expand()

        each_playout_num = self.playout_num // 4
        refs = [
            MctsAgent.mcts_playout.remote(root_node, each_playout_num, self.verbose),
            MctsAgent.mcts_playout.remote(root_node, each_playout_num, self.verbose),
            MctsAgent.mcts_playout.remote(root_node, each_playout_num, self.verbose),
            MctsAgent.mcts_playout.remote(root_node, each_playout_num, self.verbose),
        ]
        # print(root_node, type(root_node))
        nodes: list[MctsNode] = ray.get(refs)
        for node in nodes:
            for i in range(len(node.children)):
                root_node.children[i].chosen += node.children[i].chosen
        return OthelloEnv.valid_actions(state)[
            np.argmax([child.chosen for child in root_node.children])
        ]

    def act_without_ray(self, state: State) -> Action:
        root_node = MctsNode([], state)
        for _ in (
            tqdm.tqdm(range(self.playout_num))
            if self.verbose > 0
            else range(self.playout_num)
        ):
            root_node.search_node_must_be_playouted().playout()
        return OthelloEnv.valid_actions(state)[
            np.argmax([child.chosen for child in root_node.children])
        ]

    def act(self, state: State) -> Action:
        if self.use_ray:
            action = self.act_with_ray(state)
        else:
            action = self.act_without_ray(state)
        return action


class McAgent(Agent):
    random_agent = RandomAgent()

    def __init__(self, playout_num: int, verbose=0):
        self.playout_num = playout_num
        self.verbose = verbose

    def act(self, state: State) -> Action:
        puts = OthelloEnv.valid_actions(state)
        chirdren_num = len(puts)
        win_number = [0] * chirdren_num
        chosen = [1] * chirdren_num
        uct_list = [0] * chirdren_num
        for i in (
            tqdm(range(self.playout_num))
            if self.verbose > 0
            else range(self.playout_num)
        ):
            for j in range(chirdren_num):
                uct = win_number[j] / chosen[j] + math.sqrt(
                    2 * math.log(i + 1) / chosen[j]
                )
                uct_list[j] = uct
            pon = 0
            uct_max = 0
            for j in range(chirdren_num):
                if uct_max != max(uct_max, uct_list[j]):
                    uct_max = uct_list[j]
                    pon = j
            act = puts[pon]

            next_state = OthelloEnv.put(state, act)
            winner = OthelloEnv.winner(
                OthelloEnv.play(
                    McAgent.random_agent,
                    McAgent.random_agent,
                    init_state=next_state,
                    do_print=False,
                )
            )
            if winner == state.color:
                win_number[pon] += 1
            chosen[pon] += 1
        elit = 0
        elit_index = 0

        for i in range(len(puts)):
            if elit != max(elit, win_number[i] / chosen[i]):
                elit_index = i
                elit = max(elit, win_number[i] / chosen[i])
        return puts[elit_index]


class MctsNode:
    random_agent = RandomAgent()

    def __init__(self, parents: list[Self], state: State):
        self.state = state
        self.parents = parents
        self.children: list[Self] = []
        self.chosen = 0
        self.wins = 0

    def __str__(self):
        result = str(self.state)
        result += f"\nwin={self.wins}\nchosen={self.chosen}"
        return result

    def print_tree(self, depth):
        print("  " * depth + f"win={self.wins} chosen={self.chosen}")
        for child in self.children:
            child.print_tree(depth + 1)

    def uct(self):
        N = 1
        for i in range(len(self.parents[-1].children)):
            N += self.parents[-1].children[i].chosen
        return self.wins / (self.chosen + 1) + math.sqrt(
            2 * math.log(N) / (self.chosen + 1)
        )

    def choise_best_child(self) -> Self:
        best_child: Self = None
        best_uct = -1
        for i in range(len(self.children)):
            if best_uct < self.children[i].uct():
                best_uct = self.children[i].uct()
                best_child = self.children[i]
        return best_child

    # self.childrenに子孫追加
    def expand(self):
        new_parents = copy(self.parents)
        new_parents.append(self)
        for action in OthelloEnv.valid_actions(self.state):
            next_state, _, done = OthelloEnv.step(self.state, action)
            child = MctsNode(new_parents, next_state)
            self.children.append(child)

    # tannsaku\お探す
    def search_node_must_be_playouted(self):
        nx_child = self
        while nx_child.children != []:
            nx_child = nx_child.choise_best_child()

        if nx_child.chosen > 20:
            nx_child.expand()
        return nx_child

    # ランダムプレイする
    def playout(self):
        winner = OthelloEnv.winner(
            OthelloEnv.play(
                MctsNode.random_agent,
                MctsNode.random_agent,
                init_state=self.state,
                do_print=False,
            )
        ).reverse()

        self.chosen += 1
        if winner == self.state.color:
            self.wins += 1
        for parent in self.parents:
            if parent.state.color == winner:
                parent.wins += 1
            parent.chosen += 1

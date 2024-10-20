from sys import setrecursionlimit

import OthelloEnv
from othello import Othello, from_history
from evaluate.evaluate_board_nkmr import evaluate_board_nkmr
from math import inf
from type import State, Agent, Action

setrecursionlimit(10**8)


def alpha_beta_play_core(
    state: State,
    depth: int = 3,
    evaluate_board=evaluate_board_nkmr,
):

    ps = OthelloEnv.valid_actions(state)
    best = None
    alpha = -inf

    for action in ps:
        next_state, reward, done = OthelloEnv.step(state, action)
        score = -alpha_beta(
            next_state,
            next_state[2, 0, 0],
            depth,
            -inf,
            -alpha,
            evaluate_board,
        )
        if score > alpha:
            best = action
            alpha = score
    return best


class AlphaBetaAgent(Agent):
    def __init__(self, depth: int = 3, evaluate_board=evaluate_board_nkmr):
        self.depth = depth
        self.evaluate_board = evaluate_board

    def act(self, state: State) -> Action:
        return alpha_beta_play_core(state, self.depth, self.evaluate_board)


def alpha_beta_play(depth: int, evaluate_board=evaluate_board_nkmr):
    return lambda o, c: alpha_beta_play_core(o, c, depth, evaluate_board)


def alpha_beta(
    state: State,
    origin_color: int,
    depth: int,
    alpha: int,
    beta: int,
    evaluate_board,
):
    if OthelloEnv.is_done(state):
        if OthelloEnv.winner(state) - 1 == origin_color:
            return 10000
        else:
            return -10000
    if depth == 0:
        return evaluate_board(state)
    next_actions = OthelloEnv.valid_actions(state)
    for action in next_actions:
        ns, _, _ = OthelloEnv.step(state, action)
        s = -alpha_beta(ns, origin_color, depth - 1, -beta, -alpha, evaluate_board)
        if s > alpha:
            alpha = s
        if alpha >= beta:
            return alpha
    return alpha

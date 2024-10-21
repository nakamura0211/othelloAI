from sys import setrecursionlimit

from evaluate.evaluate_board_nkmr import evaluate_board_nkmr
from math import inf
from domain.models import *
from domain import OthelloEnv
from tqdm import tqdm

setrecursionlimit(10**8)


class AlphaBetaAgent(Agent):
    def __init__(
        self,
        depth: int = 3,
        evaluate_board: EvaluateState = evaluate_board_nkmr,
        verbose=0,
    ):
        self.depth = depth
        self.evaluate_board = evaluate_board
        self.verbose = verbose

    def act(self, state: State) -> Action:
        actions = OthelloEnv.valid_actions(state)
        best = None
        alpha = -inf
        actions.sort(
            key=lambda a: len(OthelloEnv.valid_actions(OthelloEnv.put(state, a))),
            reverse=True,
        )

        for action in tqdm(actions) if self.verbose == 1 else actions:
            next_state, reward, done = OthelloEnv.step(state, action)
            score = -alpha_beta(
                next_state,
                next_state.color,
                self.depth,
                -inf,
                -alpha,
                self.evaluate_board,
            )
            if score > alpha:
                best = action
                alpha = score
        return best


def alpha_beta(
    state: State,
    origin_color: Color,
    depth: int,
    alpha: int,
    beta: int,
    evaluate_board: EvaluateState,
):
    if OthelloEnv.is_done(state):
        if OthelloEnv.winner(state) == origin_color:
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

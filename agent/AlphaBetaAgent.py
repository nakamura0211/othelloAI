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
        V: EvaluateState | None = evaluate_board_nkmr,
        Q_func: Policy | None = None,
        verbose=0,
    ):
        self.depth = depth
        self.V = V
        self.Q_func = Q_func
        self.verbose = verbose

    def act(self, state: State) -> Action:
        if self.Q_func is not None:
            return self.act_by_Q(state)
        else:
            return self.act_by_V(state)

    def act_by_V(self, state: State) -> Action:
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
                self.V,
            )
            if score > alpha:
                best = action
                alpha = score
        return best

    def act_by_Q(self, state: State) -> Action:
        actions = OthelloEnv.valid_actions(state)
        best = None
        alpha = -inf
        q_values = self.Q_func(state)
        mx = max([q_values[a.index] for a in actions])
        filtered_nx = [a for a in actions if q_values[a.index] > mx - 0.2]
        filtered_nx.sort(key=lambda a: q_values[a.index], reverse=True)
        q_values = np.zeros((SIZE * SIZE,))
        if len(filtered_nx) == 1:
            return filtered_nx[0]
        for action in tqdm(filtered_nx[:3]) if self.verbose == 1 else filtered_nx[:3]:
            ns, _, _ = OthelloEnv.step(state, action)
            score = -alpha_beta_Q(
                ns,
                ns.color,
                self.depth,
                -inf,
                -alpha,
                self.Q_func,
                -q_values[action.index],
            )
            if score > alpha:
                best = action
                alpha = score
        return best

    def policy(self, state):
        policy = np.zeros((SIZE * SIZE))
        actions = OthelloEnv.valid_actions(state)
        alpha = -inf
        q_values = np.zeros((SIZE * SIZE,))
        for action in actions:
            ns, _, _ = OthelloEnv.step(state, action)
            score = -alpha_beta_Q(
                ns,
                ns.color,
                self.depth,
                -inf,
                -alpha,
                self.Q_func,
                -q_values[action.index],
            )
            policy[action.index] = score
        return policy


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


def alpha_beta_Q(
    state: State,
    origin_color: Color,
    depth: int,
    alpha: int,
    beta: int,
    Q_func: Policy,
    Q_value: float,
):
    if OthelloEnv.is_done(state):
        return Q_value
    if depth == 0:
        return Q_value
    next_actions = OthelloEnv.valid_actions(state)
    q_values = Q_func(state)
    mx = max([q_values[a.index] for a in next_actions])
    filtered_nx = [a for a in next_actions if q_values[a.index] > mx - 0.2]
    filtered_nx.sort(key=lambda a: q_values[a.index], reverse=True)
    filtered_nx = filtered_nx[:3]
    for action in filtered_nx:
        ns, _, _ = OthelloEnv.step(state, action)
        s = -alpha_beta_Q(
            ns, origin_color, depth - 1, -beta, -alpha, Q_func, -q_values[action.index]
        )
        if s > alpha:
            alpha = s
        if alpha >= beta:
            return alpha
    return alpha

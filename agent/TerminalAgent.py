from domain.models import *
from domain import OthelloEnv


class TerminalAgent(Agent):
    def __call__(self, othello, color: int) -> tuple[int, int]:
        return super().__call__(othello, color)

    def act(self, state: State) -> Action:
        x = -1
        y = -1
        print(state.color)
        while not OthelloEnv.is_valid_action(state, Action(x, y)):
            x, y = map(int, input().split())
        return Action(x, y)

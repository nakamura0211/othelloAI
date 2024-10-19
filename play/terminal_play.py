import OthelloEnv
from type import State, Agent, Action


def terminal_play(othello, color: int):
    x = -1
    y = -1
    print(othello.colors[color])
    while not othello.is_possible_to_put(x, y, color):
        s = input()
        if (
            not len(s) == 3
            or not s[0].isdigit()
            or not s[1] == " "
            or not s[2].isdigit()
        ):
            continue
        x, y = map(int, s.split(" "))

    return x, y


class TerminalAgent(Agent):
    def __call__(self, othello, color: int) -> tuple[int, int]:
        return super().__call__(othello, color)

    def act(self, state: State) -> Action:
        x = -1
        y = -1
        print(state[2][0][0] + 1)
        while not OthelloEnv.is_valid_action(state, (x, y)):
            x, y = map(int, input().split())
        return x, y

    pass

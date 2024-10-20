import numpy as np

from SizedOthello import SizedOthello
from type import State, Action, Agent

dirs = np.array([[0, -1], [1, -1], [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0], [-1, -1]])


def play(black: Agent, white: Agent, init_state: State | None = None, do_print=True):
    if init_state is None:
        init_state = reset(8)
    state = init_state.copy()
    done = is_done(state)
    while not done:
        if do_print:
            print(state_to_str(state, True))
        color = state[2, 0, 0]
        agent = black if color == 0 else white
        action = agent.act(state)
        next_state, reward, done = step(state, action)
        state = next_state
    return winner(state)


def othello_to_state(othello: SizedOthello) -> State:
    state = np.zeros((3, othello.size, othello.size), dtype=np.uint8)
    if othello.color == 1:
        state[2] = np.zeros((othello.size, othello.size), dtype=np.uint8)
    else:
        state[2] = np.ones((othello.size, othello.size), dtype=np.uint8)

    for x in range(othello.size):
        for y in range(othello.size):
            if othello.board[y][x] == 1:
                state[0, y, x] = 1
            elif othello.board[y][x] == 2:
                state[1, y, x] = 1
    return state


def state_to_othello(state: State) -> SizedOthello:
    size = state.shape[2]
    othello = SizedOthello(size)
    color = state[2][0][0]
    othello.color = color
    othello.board = [[0] * size for _ in range(size)]
    for x in range(othello.size):
        for y in range(othello.size):
            if state[0, y, x] == 1:
                othello.board[y][x] = 1
            elif state[1, y, x] == 1:
                othello.board[y][x] = 2
    return othello


def step(
    state: State, action: Action
) -> tuple[State, int, bool]:  # next_state,reward,done
    next_state = put(state, action)
    if next_state is None:
        raise ValueError(
            f"""invalid action
{state_to_str(state)}
tried to put {action_to_cord(state,action)}
valid actions were {[action_to_cord(state,i) for i in valid_actions(state)]}
"""
        )
    if len(valid_actions(next_state)) == 0:
        _, black, white = count(state)
        if black == white:
            return next_state, 0, True
        if (state[2, 0, 0] == 0 and black > white) or (
            state[2, 0, 0] == 1 and white > black
        ):
            return next_state, 1, True
        return next_state, -1, True
    return next_state, 0, False


def put(state: State, action: Action) -> State | None:  # next_state
    rlen = reverse_len(state, action)
    x, y = action_to_cord(state, action)
    size = state.shape[1]
    color = state[2, 0, 0]
    next_state = state.copy()
    if rlen.sum() == 0:
        return None
    for i, l in enumerate(rlen):
        dx, dy = dirs[i]
        for j in range(l + 1):
            next_state[color, y + dy * j, x + dx * j] = 1
            next_state[1 - color, y + dy * j, x + dx * j] = 0
    if color == 0:
        next_state[2] = np.ones((size, size))
    else:
        next_state[2] = np.zeros((size, size))
    return next_state


def action_to_cord(state: State, action: Action) -> Action:
    size = state.shape[1]
    if type(action) is tuple:
        return action
    else:
        return action // size, action % size


def reverse_len(state: State, action: Action) -> np.ndarray[np.uint8]:
    size = state.shape[1]
    result = np.zeros((8,), dtype=np.uint8)
    x, y = action_to_cord(state, action)
    if state[0, y, x] == 1 or state[1, y, x] == 1:
        return result
    color = state[2][0][0]
    opp = 1 - color
    for index, (dx, dy) in enumerate(dirs):
        i = 1
        while (
            y + dy * i in range(size)
            and x + dx * i in range(size)
            and state[opp, y + dy * i, x + dx * i] == 1
            and state[color, y + dy * i, x + dx * i] == 0
        ):
            i += 1
        if (
            i > 1
            and y + dy * i in range(size)
            and x + dx * i in range(size)
            and state[color, y + dy * i, x + dx * i] == 1
            and state[opp, y + dy * i, x + dx * i] == 0
        ):
            result[index] = i - 1
    return result


def count(state: State) -> tuple[int, int, int]:
    size = state.shape[1]
    black = state[0].sum()
    white = state[1].sum()
    blank = size * size - black - white
    return blank, black, white


def is_done(state: State) -> bool:
    if len(valid_actions(state)) == 0:
        return True
    size = state.shape[2]
    new = state.copy()
    if state[2, 0, 0] == 0:
        new[2] = np.ones((size, size), dtype=np.uint8)
    else:
        new[2] = np.zeros((size, size), dtype=np.uint8)
    return len(valid_actions(new)) == 0


def winner(state: State) -> int | None:
    if not is_done(state):
        return None
    _, black, white = count(state)
    if black == white:
        return 0
    elif black > white:
        return 1
    else:
        return 2


def is_valid_action(state: State, action: Action) -> bool:
    return reverse_len(state, action).sum() > 0


def valid_actions(state: State) -> list[Action]:
    result = []
    size = state.shape[1]
    for i in range(size * size):
        if is_valid_action(state, i):
            result.append(i)
    return result


def state_to_str(state: State, guide: bool = True) -> str:
    size = state.shape[1]
    if guide:
        ret = f"  {' '.join([str(i) for i in range(size)])}\n"
        for y in range(size):
            ret += str(y) + " "
            for x in range(size):
                ret += ".xo"[state[0, y, x] + state[1, y, x] * 2] + " "
            ret += "\n"
        return ret
    return f"color={state[2][0][0]+1}\n{state[0] + state[1] * 2}"


def reset(size: int = 8) -> State:
    state = np.zeros((3, size, size), dtype=np.uint8)
    state[0, size // 2 - 1, size // 2 - 1] = 1
    state[0, size // 2, size // 2] = 1
    state[1, size // 2 - 1, size // 2] = 1
    state[1, size // 2, size // 2 - 1] = 1
    return state

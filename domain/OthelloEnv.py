import numpy as np

from domain.models import *

dirs = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]


def play(
    black: Agent, white: Agent, init_state: State | None = None, do_print=True
) -> State:
    if init_state is None:
        init_state = reset()
    state = init_state.copy()
    done = is_done(state)
    while not done:
        if do_print:
            print(state_to_str(state, True))
        agent = black if state.color == Color.BLACK else white
        action = agent.act(state)
        state, reward, done = step(state, action)
    if do_print:
        print(state_to_str(state, True))
    return state


def step(
    state: State, action: Action
) -> tuple[State, float, bool]:  # next_state,reward,done
    next_state = put(state, action)
    if next_state is None:
        raise ValueError(
            f"""invalid action
{state_to_str(state)}
tried to put {action.cord}
valid actions were {[i.cord for i in valid_actions(state)]}
"""
        )
    if is_done(next_state):
        _, black, white = count(state)
        reward = black - white if state.color == Color.BLACK else white - black
        return next_state, reward / SIZE / SIZE, True
    return next_state, 0, False


def put(state: State, action: Action) -> State | None:  # next_state
    rlen = reverse_len(state, action)
    x, y = action.cord
    color = state.color
    next_state = state.copy(color=color.reverse())
    if sum(rlen) == 0:
        return None
    for i, l in enumerate(rlen):
        dx, dy = dirs[i]
        for j in range(l + 1):
            next_state.board[y + dy * j][x + dx * j] = color
    if len(valid_actions(next_state)) == 0:
        next_state.color = next_state.color.reverse()
    return next_state


def reverse_len(state: State, action: Action) -> list[int]:
    result = [0] * 8
    x, y = action.cord
    if state.board[y][x] != 0:
        return result

    color = state.color
    opp = color.reverse()
    for index, (dx, dy) in enumerate(dirs):
        i = 1
        while (
            y + dy * i in range(SIZE)
            and x + dx * i in range(SIZE)
            and state.board[y + dy * i][x + dx * i] == opp
        ):
            i += 1
        if (
            i > 1
            and y + dy * i in range(SIZE)
            and x + dx * i in range(SIZE)
            and state.board[y + dy * i][x + dx * i] == color
        ):
            result[index] = i - 1
    return result


def count(state: State) -> tuple[int, int, int]:
    blank = 0
    black = 0
    white = 0
    for y in range(SIZE):
        for x in range(SIZE):
            if state.board[y][x] == Color.BLANK:
                blank += 1
            elif state.board[y][x] == Color.BLACK:
                black += 1
            elif state.board[y][x] == Color.WHITE:
                white += 1
    return blank, black, white


def is_done(state: State) -> bool:
    return (
        len(valid_actions(state)) == 0
        and len(valid_actions(state.copy(color=state.color.reverse()))) == 0
    )


def winner(state: State) -> Color | None:
    if not is_done(state):
        return None
    _, black, white = count(state)
    if black == white:
        return Color.BLANK
    elif black > white:
        return Color.BLACK
    else:
        return Color.WHITE


def is_valid_action(state: State, action: Action) -> bool:
    return sum(reverse_len(state, action)) > 0


def valid_actions(state: State) -> list[Action]:
    result = []
    for i in range(SIZE * SIZE):
        if is_valid_action(state, Action(i)):
            result.append(Action(i))
    return result


def state_to_str(state: State, guide: bool = True) -> str:
    if guide:
        ret = f"color={state.color}\n  {' '.join([str(i) for i in range(SIZE)])}\n"
        for y in range(SIZE):
            ret += str(y) + " "
            for x in range(SIZE):
                ret += ".xo"[state.board[y][x]] + " "
            ret += "\n"
        return ret
    return f"color={state.color}\n{state.board}"


def reset() -> State:
    board = [[0] * SIZE for _ in range(SIZE)]
    board[SIZE // 2 - 1][SIZE // 2 - 1] = 1
    board[SIZE // 2][SIZE // 2] = 1
    board[SIZE // 2 - 1][SIZE // 2] = 2
    board[SIZE // 2][SIZE // 2 - 1] = 2
    return State(board, Color.BLACK)

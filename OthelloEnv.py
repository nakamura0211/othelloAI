import numpy as np

from SizedOthello import SizedOthello

State = list[list[list[int]]]
SIZE=4

def encode_state(othello:SizedOthello)->State: #8*8*3でのstateのエンコード 1:黒石,2:白石,3:色
        state=[[[0]*SIZE for _ in range(SIZE)],[[0]*SIZE for _ in range(SIZE)],[[othello.color]*SIZE for _ in range(SIZE)]]
        for x in range(othello.size):
            for y in range(othello.size):
                if othello.board[y][x]==1:
                    state[0][y][x]=1
                elif othello.board[y][x]==2:
                    state[1][y][x]=1
        return state

def decode_state(state:State)->SizedOthello:
    othello=SizedOthello(SIZE)
    color=state[2][0][0]
    othello.color=color
    othello.board=[[0]*SIZE for _ in range(SIZE)]
    for x in range(othello.size):
            for y in range(othello.size):
                if state[0][y][x]==1:
                    othello.board[y][x]=1
                elif state[1][y][x]==1:
                    othello.board[y][x]=2
    return othello

def step(state,action:tuple[int,int]|int)->tuple[State,int,bool]: # next_state,reward,done
        if type(action) is int or type(action) is float or type(action) is np.int64:
            action=action//SIZE,action%SIZE
        x,y=action
        othello=decode_state(state)

        if not othello.is_possible_to_put(x,y,othello.color):
            raise ValueError(f"invalid action {x} {y} \n{othello}")
        othello.put(x,y,othello.color)
        othello.history.append((x,y))
        othello.color=3-othello.color
        if not othello.is_possible_to_put_anywhere(othello.color) or not othello.is_possible_to_put_anywhere(3-othello.color):
            reward=1 if othello.color == othello.winner() else -1
            return state,reward,True
        return encode_state(othello),0,False

def valid_actions(state:State)->list[tuple[int,int]]:
    othello=decode_state(state)
    return othello.possible_puts(othello.color)


def reset():
    return encode_state(SizedOthello(SIZE))



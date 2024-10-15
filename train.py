from OthelloEnv import encode_state, decode_state
from SizedOthello import SizedOthello
from othello import Othello
from play.DQNAgent import DqnAgent
from copy import  deepcopy
import OthelloEnv
from play.random_play import RandomAgent, random_play

agent=DqnAgent(OthelloEnv.SIZE)
random_agent=RandomAgent()
n_episodes=10000
batch_size=48
for e in range(1,n_episodes+1):
    state=OthelloEnv.reset()
    while True:
        action=agent.act(state)
        next_state,reward,done=OthelloEnv.step(state,action)
        agent.remember(state,action,reward,next_state,done)
        state=next_state
        #print(decode_state(state))
        if done:
            break

    print(f"episode: {e}/{n_episodes}")
    if e%100==0:
        o=SizedOthello(OthelloEnv.SIZE)
        o.play(black=agent,white=random_agent,do_print=False)
        _,w,b=o.count()
        print(f"score: {w-b}")
        agent.model.save(f"model/dqn_relu{e}.keras")

    if len(agent.memory)>batch_size:
        agent.train(batch_size)



def turn_state(state):
    return deepcopy(state),[[l for l in board[::-1]] for board in state],[[l[::-1] for l in board[::-1]] for board in state],[[l[::-1] for l in board] for board in state]


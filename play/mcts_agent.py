from othello import Othello
import random
from play.random_play import random_play
import math
def mcts_agent(othello:Othello,color:int):
    puts = othello.possible_puts(color)
    simulation_num = 500
    win_number = [0]*(len(puts))
    chosen = [1]*(len(puts))
    uct_list = [0]*(len(puts))
    for i in range(simulation_num):
        for j in range(len(puts)):
            uct = win_number[j]/chosen[j] + math.sqrt(2*math.log(i+1)/chosen[j])
            uct_list[j] = uct
        pon = 0
        uct_max = 0
        for j in range(len(puts)):
            if uct_max != max(uct_max,uct_list[j]):
                uct_max = uct_list[j]
                pon = j 
        put = puts[pon]
        x,y = map(int,put)
        othello_copy = othello.copy()
        othello_copy.put(x,y,color)
        syouhai = othello_copy.play(random_play,random_play,first_color=3-color,do_print=False)
        if syouhai == color:
            win_number[pon] += 1
        chosen[pon] += 1
    elit = 0
    elit_index = 0
    for i in range(len(puts)):
        if elit != max(elit,win_number[i]/chosen[i]):
            elit_index = i
            elit = max(elit,win_number[i]/chosen[i])
    return  puts[elit_index]


        
        


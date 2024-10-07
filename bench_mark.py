from othello import Othello
from play.random_play import random_play
from play.script_play import script_play
from play.alpha_beta_play import alpha_beta_play
from evaluate.evaluate_board_nkmr_es import evaluate_board_nkmr_es
from time import perf_counter




class StartsWithRandom:
            def __init__(self,agent,random_time=5):
                self.agent=agent
                self.random_time=random_time
            def __call__(self, othello,color):
                if self.random_time==0:
                    return self.agent(othello,color)
                self.random_time-=1
                return random_play(othello,color)



j=0
attempt_number=10

target=evaluate_board_nkmr_es()
opponent=StartsWithRandom(alpha_beta_play(2))

start_time=perf_counter()
for i in range(1,attempt_number+1):
  o=Othello()
  if o.play(target,opponent,False,False)==1:
    j+=1
  print(j/i*100)
k=0
print("\n")
print("勝率",j/attempt_number*100)
print("一回あたりの平均実行時間",(perf_counter()-start_time)/attempt_number,"s")
print("change\n")
start_time=perf_counter()
for i in range(1,attempt_number+1):
  o=Othello()
  if o.play(opponent,target,False,False)==2:
    k+=1
  print(k/i*100)
print("勝率",j/attempt_number*100,k/attempt_number*100)
print("一回あたりの平均実行時間",(perf_counter()-start_time)/attempt_number,"s")

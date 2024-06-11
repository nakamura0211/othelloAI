from othello import Othello
from play.random_play import random_play
from play.script_play import script_play
from play.mini_max_play import mini_max_play,mini_max_play_depth
from play.alpha_beta_play import alpha_beta_play,alpha_beta_play_depth
from time import perf_counter


j=0
attempt_number=10
start_time=perf_counter()
for i in range(1,attempt_number+1):
  o=Othello()
  if o.play(alpha_beta_play_depth(2),random_play,False,False)==1:
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
  if o.play(random_play,alpha_beta_play_depth(2),False,False)==2:
    k+=1
  print(k/i*100)
print("勝率",j/attempt_number*100,k/attempt_number*100)
print("一回あたりの平均実行時間",(perf_counter()-start_time)/attempt_number,"s")

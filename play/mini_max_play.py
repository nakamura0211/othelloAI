from sys import setrecursionlimit
from multiprocessing import Pool
from othello import Othello, from_history
from evaluate.evaluate_board_nkmr import evaluate_board_nkmr
from random import choice
from math import inf

setrecursionlimit(10**8)

def _map_fn(t):
    put,othello,color,depth,evaluate=t
    return mini_max(othello.history+[put],3-color,3-color,depth,evaluate)

def mini_max_play_core(othello: Othello, color:int,depth:int=2,evaluate_board=evaluate_board_nkmr):
  ps=othello.possible_puts(color)
  best_score=-inf
  scores=[]
  with Pool(len(ps)) as p:
    scores=p.map(_map_fn,[(put,othello,color,depth,evaluate_board) for put in ps],2)
    best_score=min(scores)
  return choice([ps[i] for i,j in enumerate(scores) if j==best_score])
  
  
def mini_max_play(depth:int,evaluate_board=evaluate_board_nkmr):
  return lambda o,c:mini_max_play_core(o,c,depth,evaluate_board)
  

def mini_max(history:list[tuple[int,int]],origin_color:int,color:int,depth:int,evaluate_board=evaluate_board_nkmr):
  othello=from_history(history)
  if othello.winner() is not None:
    if othello.winner()==origin_color:
      return 10000
    else:
      return -10000
  if not othello.is_possible_to_put_anywhere(color):
    return mini_max(history,origin_color,3-color,depth,evaluate_board)
  if depth==0:
    return evaluate_board(othello.board,color)
  next_puts=othello.possible_puts(color)
  best=-inf
  for put in next_puts:
    s=-mini_max(history+[put],origin_color,3-color,depth-1,evaluate_board)
    if s>best:
      best=s
  return best
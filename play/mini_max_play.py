from sys import setrecursionlimit
from othello import Othello, fromHistory
from play.script_play import evaluate_board
from random import choice
from math import inf

setrecursionlimit(10**8)

def mini_max_play(othello: Othello, color,depth=2):
  ps=othello.possible_puts(color)
  best_score=-inf
  scores=[]
  for put in ps:
    score=-mini_max(othello.history+[put],3-color,3-color,depth)
    if score>best_score:
      best_score=score
    scores.append(score)
  return choice([ps[i] for i,j in enumerate(scores) if j==best_score])

def mini_max_play_depth(depth:int):
  return lambda o,c:mini_max_play(o,c,depth)

  

def mini_max(history,origin_color,color,depth):
  othello=fromHistory(history)
  if othello.winner() is not None:
    if othello.winner()==origin_color:
      return 10000
    else:
      return -10000
  if not othello.is_possible_to_put_anywhere(color):
    return mini_max(history,origin_color,3-color,depth)
  if depth==0:
    return evaluate_board(othello.board,color)
  next_puts=othello.possible_puts(color)
  best=-inf
  for put in next_puts:
    s=-mini_max(history+[put],origin_color,3-color,depth-1)
    if s>best:
      best=s
  return best
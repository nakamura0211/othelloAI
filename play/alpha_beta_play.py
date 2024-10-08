from sys import setrecursionlimit
from othello import Othello, from_history
from evaluate.evaluate_board_nkmr import evaluate_board_nkmr
from math import inf

setrecursionlimit(10**8)


def alpha_beta_play_core(othello: Othello, color:int,depth:int=3,evaluate_board=evaluate_board_nkmr):
  ps=othello.possible_puts(color)
  best=None
  alpha=-inf
  for put in ps:
    score=-alpha_beta(othello.history+[put],3-color,3-color,depth,-inf,-alpha,evaluate_board)
    if score>alpha:
      best=put
      alpha=score
  return best


def alpha_beta_play(depth:int,evaluate_board=evaluate_board_nkmr):
  return lambda o,c:alpha_beta_play_core(o,c,depth,evaluate_board)

def alpha_beta(history:list[tuple[int,int]],origin_color:int,color:int,depth:int,alpha:int,beta:int,evaluate_board):
  othello=from_history(history)
  if othello.winner() is not None:
    if othello.winner()==origin_color:
      return 10000
    else:
      return -10000
  if not othello.is_possible_to_put_anywhere(color):
    return alpha_beta(history,origin_color,3-color,depth,alpha,beta,evaluate_board)
  if depth==0:
    return evaluate_board(othello.board,color)
  next_puts=othello.possible_puts(color)
  for put in next_puts:
    s=-alpha_beta(history+[put],origin_color,3-color,depth-1,-beta,-alpha,evaluate_board)
    if s>alpha:
      alpha=s
    if alpha>=beta:
      return alpha
  return alpha

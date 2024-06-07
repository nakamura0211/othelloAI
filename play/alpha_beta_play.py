from sys import setrecursionlimit
from othello import Othello, fromHistory
from play.script_play import evaluate_board

setrecursionlimit(10**8)

def alpha_beta_play(othello: Othello, color,depth=3):
  ps=othello.possible_puts(color)
  best=None
  alpha=-float("inf")
  for put in ps:
    score=-alpha_beta(othello.history+[put],3-color,3-color,depth,-float("inf"),-alpha)
    if score>alpha:
      best=put
      alpha=score
  return best

def alpha_beta_play_depth(depth):
  return lambda o,c:alpha_beta_play(o,c,depth)

def alpha_beta(history,origin_color,color,depth,alpha,beta):
  othello=fromHistory(history)
  if othello.winner() is not None:
    if othello.winner()==origin_color:
      return 10000
    else:
      return -10000
  if not othello.is_possible_to_put_anywhere(color):
    return -alpha_beta(history,origin_color,3-color,depth,alpha,beta)
  if depth==0:
    return evaluate_board(othello.board,color)
  next_puts=othello.possible_puts(color)
  for put in next_puts:
    s=-alpha_beta(history+[put],origin_color,3-color,depth-1,-beta,-alpha)
    if s>alpha:
      alpha=s
    if alpha>=beta:
      return alpha
  return alpha

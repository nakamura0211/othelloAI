from othello import Othello
import math
from typing import Self
from play.random_play import random_play
from copy import copy

class MctsNode:
    def __init__(self,parents:list[Self],othello:Othello):
        self.state = othello
        self.parents = parents
        self.children :list[Self] = []
        self.chosen = 0
        self.wins = 0
    
    def __str__(self):
        result=str(self.state)
        result+=f"\nwin={self.wins}\nchosen={self.chosen}"
        return result
    
    #def print_tree(self,depth):
        #print("  "*depth+f"win={self.wins} chosen={self.chosen}")
        #for child in self.children:
            #child.print_tree(depth+1)


    def uct(self):
        N = 1
        for i in range(len(self.parents[-1].children)):
            N += self.parents[-1].children[i].chosen
        return self.wins/(self.chosen+1)+ math.sqrt(2*math.log(N)/(self.chosen+1))
    
    def choise_best_child(self)->Self:
        best_child:Self = None
        best_uct = -1
        for i in range(len(self.children)):
            if best_uct < self.children[i].uct():
                best_uct = self.children[i].uct()
                best_child = self.children[i]
        return best_child
    #self.childrenに子孫追加
    def expand(self):
        c = self.state.color
        new_parents=copy(self.parents)
        new_parents.append(self)
        for x,y in self.state.possible_puts(c):
            copy_state = self.state.copy()
            copy_state.color=3-c
            copy_state.put(x,y,c)
            child=MctsNode(new_parents,copy_state)    
            self.children.append(child)
    #tannsaku\お探す
    def search_node_must_be_playouted(self):
        nx_child = self
        while nx_child.children != []:
            nx_child = nx_child.choise_best_child()


        if nx_child.chosen > 5:
            nx_child.expand()
        return nx_child
    #ランダムプレイする
    def playout(self):
        o = self.state.copy()
        winner=o.play(random_play,random_play,first_color=self.state.color,do_print=False)
        self.chosen += 1
        if winner == self.state.color:
            self.wins += 1
        for parent in self.parents:
                if parent.state.color == self.state.color:
                    parent.wins += 1
                parent.chosen += 1
        
        

        


        
 
        






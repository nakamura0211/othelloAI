from os.path import isfile
import numpy as np
from othello import Othello
from play.random_play import random_play
from play.script_play import script_play
from play.alpha_beta_play import alpha_beta_play_depth
from typing import Callable
import matplotlib.pyplot as plt


class CMA_ES(object):
    """CMA Evolution Strategy with CSA"""
    
    def __init__(self, func, init_mean, init_sigma, nsample):
        """コンストラクタ
        
        Parameters
        ----------
        func : callable
            目的関数 (最大化)
        init_mean : ndarray (1D)
            初期平均ベクトル
        init_sigma : float
            初期ステップサイズ
        nsample : int
            サンプル数
        """
        self.func = func
        self.mean = init_mean
        self.sigma = init_sigma
        self.N = self.mean.shape[0]                     # 探索空間の次元数
        self.arx = np.zeros((nsample, self.N)) * np.nan # 候補解
        self.arf = np.zeros(nsample) * np.nan           # 候補解の評価値
        self.D = np.ones(self.N)
        
        self.weights = np.zeros(nsample)
        self.weights[:nsample//4] = 1.0 / (nsample//4)  # 重み．総和が1
        
        # For CSA
        self.ps = np.zeros(self.N)
        self.cs = 4.0 / (self.N + 4.0)
        self.ds = 1.0 + self.cs
        self.chiN = np.sqrt(self.N) * (1.0 - 1.0 / (4.0 * self.N) + 1.0 / (21.0 * self.N * self.N))
        self.mueff = 1.0 / np.sum(self.weights**2)
        
        # For CMA
        self.cmu = self.mueff / (4 * self.N + self.mueff)
        
    def sample(self):
        """候補解を生成する．"""
        self.arx = self.mean + self.sigma * np.random.normal(size=self.arx.shape) * np.sqrt(self.D)
    
    def evaluate(self):
        """候補解を評価する．"""
        for i in range(self.arf.shape[0]):
            self.arf[i] = self.func(self.arx[i])
            print(self.arf)
        
    def update_param(self):
        """パラメータを更新する．"""
        idx = np.argsort(self.arf)[::-1]  # idx[i]は評価値がi番目に良い解のインデックス
        # 進化パスの更新 (平均ベクトル移動量の蓄積)
        self.ps = (1 - self.cs) * self.ps + np.sqrt(self.cs * (2 - self.cs) * self.mueff) * np.dot(self.weights, (self.arx[idx] - self.mean)) / np.sqrt(self.D) / self.sigma
        
        # 共分散行列の対角要素を更新
        self.D = (1 - self.cmu) * self.D + self.cmu * np.dot(self.weights, (self.arx[idx] - self.mean) ** 2) / self.sigma ** 2
        
        # 進化パスの長さが，ランダム関数の下での期待値よりも大きければステップサイズを大きくする．
        self.sigma = self.sigma * np.exp(self.cs / self.ds * (np.linalg.norm(self.ps) / self.chiN - 1))        
        self.mean += np.dot(self.weights, (self.arx[idx] - self.mean))



#(board,color,gene)->(int,int)を渡すとそれを最適化するgeneをファイル出力
def CMA_ES_train(target_agent:Callable[[list[list[int]],int,np.ndarray[float]],tuple[int,int]],output_filename="cma_es"):
    def evaluate(gene):
        depth=1
        def eval(b,c):
            return target_agent(b,c,gene)
        def play(o,c):
            return script_play(o,c,eval)
            #return alpha_beta_play_depth(depth,eval)(o,c)
        N=1
        res=0
        for i in range(N):
            o=Othello()
            o.play(alpha_beta_play_depth(depth),play,False,False)
            _,b,w=o.count()
            res+=w-b
        for i in range(N):
            o=Othello()
            o.play(play,alpha_beta_play_depth(depth),False,False)
            _,b,w=o.count()
            res+=b-w
        return res


    mean_history=[np.ones(8)*100]
    sigma_history=[20]
    score_history=[evaluate(mean_history[-1])] 

    es = CMA_ES(func=evaluate,
           init_mean=np.array(mean_history[-1]),
           init_sigma=sigma_history[-1],
           nsample=12)

    maxiter = 1000
    for i in range(maxiter):
        es.sample()
        es.evaluate()
        es.update_param()
        score=evaluate(es.mean.copy())
        score_history.append(score)
        mean_history.append(es.mean.copy())
        sigma_history.append(es.sigma)
        print("score",score)
        print("mean",es.mean)
        print("sigma",es.sigma)
        
        x=list(range(i+2))
        fig=plt.figure()
        ax=fig.add_subplot(2,1,1)
        ax.plot(x,score_history)
        ax.title.set_text("Evaluated value of mean vector")
        ax=fig.add_subplot(2,1,2)
        ax.title.set_text("sigma")
        ax.plot(x,sigma_history)
        plt.savefig(f"./es_output/{output_filename}_graph")
        plt.close("all")
        np.savetxt(f"./es_output/{output_filename}_score.txt",score_history)
        np.savetxt(f"./es_output/{output_filename}_mean.txt",mean_history)
        np.savetxt(f"./es_output/{output_filename}_sigma.txt",sigma_history)


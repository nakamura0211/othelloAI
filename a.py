#個体の各遺伝子を決めるために使用
import random
#DEAPの中にある必要なモジュールをインポート
from deap import base
from deap import creator
from deap import tools
from deap import algorithms
#最小化問題として設定(-1.0で最小化、1.0で最大化問題)
#面食らうかもしれませんが、目的が最小化の場合は以下のように設定します。
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
#個体の定義（list型と指定しただけで、中身の遺伝子は後で入れる）
#これも面食らうかもしれませんが、個体を準備したと思ってください。
creator.create("Individual", list, fitness=creator.FitnessMin)
#目的関数の定義。必ずreturnの後に,をつける
def obfunc(individual):
    x = individual[0]
    y = individual[1]
    object = (x-1)**2 + (y-2)**2
    #(x,y)=(1,2)で最小になるはず。これを遺伝的アルゴリズムで求める
    return object,
#各種関数の設定を行います
#交叉、選択、突然変異などには、DEAPのToolbox内にある関数を利用
toolbox = base.Toolbox()
#random.uniformの別名をattribute関数として設定。各個体の遺伝子の中身を決める関数(各遺伝子は-50～50のランダムな値)
toolbox.register("attribute", random.uniform, -50,50)
#individualという関数を設定。それぞれの個体に含まれる2個の遺伝子をattributeにより決めるよ、ということ。
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attribute, 2)
#集団の個体数を設定するための関数を準備
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
#トーナメント方式で次世代に子を残す親を選択（tornsizeは各トーナメントに参加する個体の数）
toolbox.register("select", tools.selTournament, tournsize=5)
#交叉関数の設定。ブレンド交叉という手法を採用
toolbox.register("mate", tools.cxBlend,alpha=0.2)
#突然変異関数の設定。indpbは各遺伝子が突然変異を起こす確率。muとsigmaは変異の平均と標準偏差
toolbox.register("mutate", tools.mutGaussian, mu=[0.0, 0.0], sigma=[20.0, 20.0], indpb=0.2)
#評価したい関数の設定（目的関数のこと）
toolbox.register("evaluate", obfunc)
#以下でパラメータの設定
#今回は最も単純な遺伝的アルゴリズムの手法を採用
#乱数を固定
random.seed(64)
#何世代まで行うか
NGEN = 50
#集団の個体数
POP = 80
#交叉確率
CXPB = 0.9
#個体が突然変異を起こす確率
MUTPB = 0.1
#集団は80個体という情報の設定
pop = toolbox.population(n=POP)
#集団内の個体それぞれの適応度（目的関数の値）を計算
for individual in pop:
    individual.fitness.values = toolbox.evaluate(individual)
#パレート曲線上の個体(つまり、良い結果の個体)をhofという変数に格納
hof = tools.ParetoFront()
#今回は最も単純なSimple GAという進化戦略を採用
algorithms.eaSimple(pop, toolbox, cxpb=CXPB, mutpb=MUTPB, ngen=NGEN, halloffame=hof)
#最終的な集団(pop)からベストな個体を1体選出する関数
best_ind = tools.selBest(pop, 1)[0]
#結果表示
print("最も良い個体は %sで、そのときの目的関数の値は %s" % (best_ind, best_ind.fitness.values))
# play/の説明
このディレクトリはエージェント関数の置き場です。  
新たにエージェント関数を作るときはこのディレクトリに作成してください。

## terminal_play
文字通りターミナルから`x y`形式で入力を受け取ってそれを返すエージェントです。人力での入力のほか、全く別の既製AIと標準入出力を用いたやりとりにも使えると思います。

## random_play
置ける場所からランダムに打ちます


## script_play
評価関数に従って評価値が最も高い場所におきます  
評価関数はデフォルトでは`evaluate_board_nkmr`になってますが、次のように変えることができます。

```python
#これで評価関数がsome_evaluate_funcのエージェント関数になる
agent=lambda o,c:script_play(o,c,some_evaluate_func)
othello.play(agent)
```

## mini_max_play
mini-max木探索に従って打つ場所を決めます。  
評価関数と木探索の深さを指定できます。

### 使い方
`mini_max_play(depth:int,evaluate_board=evaluate_board_nkmr)`は木探索の深さと利用する評価関数を受け取って**エージェント関数を返す関数**です。`mini_max_play`自体はエージェント関数でなく、それを呼び出した返り値`mini_max_play(3,evaluate_board_nkmr)`がエージェント関数になります。  
評価関数はデフォルトで`evaluate_board_nkmr`になります

```python
#深さが3と4のミニマックス
othello.play(mini_max_play(3),mini_max_play(4))
```
探索の深さが深いほど強くなりますが、計算量は深さの指数オーダー(らしい)ので急激に計算時間が多くなります。

## alpha_beta_play
alpha-beta木探索に従って打つ場所を決めます。alpha-beta木探索はmini-max木探索を効率化したアルゴリズムなので基本的にはmini_max_playよりalpha_beta_playを使ってください。使い方はmini_max_playと同じです。

## 参照

mini-max木探索,alpha_beta木探索については以下を参照してください


- オセロAIの教科書 https://note.com/nyanyan_cubetech/n/n210cf134b8b1?magazine_key=m54104c8d2f12
- ゼロから教えるゲーム木探索入門 https://qiita.com/thun-c/items/058743a25c37c87b8aa4

def human_play(othello, color: int):
    x = -1
    y = -1
    print(othello.colors[color])
    while not othello.is_possible_to_put(x, y, color):
        s = input()
        if not len(s) == 3 or not s[0].isdigit() or not s[1] == " " or not s[2].isdigit() :
            continue
        t= map(int, s.split(" "))
        lis=list(t)
        x=lis[0]
        y=lis[1]

    return x,y

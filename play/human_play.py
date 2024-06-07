def human_play(othello, color: int):
    x = -1
    y = -1
    print(f"{color}")
    while not othello.is_possible_to_put(x, y, color):
        x, y = map(int, input().split(" "))
    return x, y

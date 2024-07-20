from collections.abc import Callable
from typing import Self
from play.terminal_play import terminal_play


class Othello:
    dirs = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
    colors = ["nothing", "black", "white"]
    def __init__(self) -> None:
        self.board = [[0] * 8 for i in range(8)]
        self.board[3][3] = 2
        self.board[4][4] = 2
        self.board[3][4] = 1
        self.board[4][3] = 1
        self.history = []

    def __str__(self) -> str:
        ret = ""
        for l in self.board:
            for i in l:
                ret += ".xo"[i] + " "
            ret += "\n"
        return ret[:-1]

    def print(self, guide: bool) -> None:
        if not guide:
            print(str(self))
        else:
            ret = "  0 1 2 3 4 5 6 7\n"
            for i, l in enumerate(self.board):
                ret += str(i) + " "
                for i in l:
                    ret += ".xo"[i] + " "
                ret += "\n"
            print(ret)

    def count(self)->tuple[int,int,int]:
        blank=0
        black=0
        white=0
        for y in range(8):
            for x in range(8):
                if self.board[y][x]==0:
                    blank+=1
                elif self.board[y][x]==1:
                    black+=1
                elif self.board[y][x]==2:
                    white+=1
        return blank,black,white



    def put(self, x: int, y: int, color: int) -> bool:  # N=8 O(N^2)
        rlen = self.reverse_len(x, y, color)
        if len([i for i in rlen if i != 0]) == 0:
            return False
        for i, l in enumerate(rlen):
            dx, dy = Othello.dirs[i]
            for j in range(l + 1):
                self.board[y + dy * j][x + dx * j] = color
        return True

    # 各dirの方向にひっくり返せる石の数
    def reverse_len(self, x: int, y: int, color: int) -> list[int]:  # O(N^2)
        result = []
        if self.board[y][x] != 0:
            return [0] * 8
        for dx, dy in self.dirs:
            opp = 3 - color
            i = 1
            while (
                y + dy * i in range(0, 8)
                and x + dx * i in range(0, 8)
                and self.board[y + dy * i][x + dx * i] == opp
            ):
                i += 1
            if (
                i > 1
                and y + dy * i in range(0, 8)
                and x + dx * i in range(0, 8)
                and self.board[y + dy * i][x + dx * i] == color
            ):
                result.append(i - 1)
            else:
                result.append(0)
        return result

    def is_possible_to_put(self, x: int, y: int, color: int) -> bool:  # O(N^2)
        return len([i for i in self.reverse_len(x, y, color) if i != 0]) > 0

    def possible_puts(self, color: int) -> list[tuple[int,int]]:  # O(N^4)
        ret = []
        for y in range(8):
            for x in range(8):
                if self.is_possible_to_put(x, y, color):
                    ret.append((x, y))
        return ret

    def is_possible_to_put_anywhere(self, color: int) -> bool:  # O(N^4)
        return len(self.possible_puts(color)) > 0

    def winner(self) -> int:  # O(N^4)
        if self.is_possible_to_put_anywhere(1) or self.is_possible_to_put_anywhere(2):
            return None
        w = 0
        b = 0
        for y in range(8):
            for x in range(8):
                if self.board[y][x] == 1:
                    b += 1
                elif self.board[y][x] == 2:
                    w += 1
        if b == w:
            return 0
        elif b > w:
            return 1
        else:
            return 2

    def play(
        self,
        black:Callable[[Self, int], tuple[int, int]] = terminal_play,
        white:Callable[[Self, int], tuple[int, int]] = terminal_play,
        print: bool = True,
        guide: bool = True,
    ) -> int:  # O(N^6*player)=2.6*10^6*player
        c = 1
        while self.winner() is None:
            if print:
                self.print(guide)
            if not self.is_possible_to_put_anywhere(c):
                c = 3 - c
            player = black if c == 1 else white
            x, y = player(self, c)
            self.put(x, y, c)
            self.history.append((x, y))
            c = 3 - c
        return self.winner()


def fromHistory(history: list[tuple[int,int]]) -> Othello:  # O(N^6)
    o = Othello()
    c = 1
    for x, y in history:
        if not o.is_possible_to_put_anywhere(c):
            c = 3 - c
        o.put(x, y, c)
        o.history.append((x,y))
        c = 3 - c
    return o

from collections.abc import Callable
from typing import Self

from play.terminal_play import terminal_play


class SizedOthello:
    dirs = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
    colors = ["nothing", "black", "white"]
    def __init__(self,size:int):
        self.history = []
        self.size=size
        self.board=[[0]*size for _ in range(size)]
        self.board[size//2-1][size//2-1]=1
        self.board[size//2][size//2]=1
        self.board[size//2-1][size//2]=2
        self.board[size//2][size//2-1]=2

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
            ret = f"  {' '.join([str(i) for i in range(self.size)])}\n"
            for i, l in enumerate(self.board):
                ret += str(i) + " "
                for i in l:
                    ret += ".xo"[i] + " "
                ret += "\n"
            print(ret)

    def count(self) -> tuple[int,int,int]:
        blank=0
        black=0
        white=0
        for y in range(self.size):
            for x in range(self.size):
                if self.board[y][x] == 0:
                    blank += 1
                elif self.board[y][x] == 1:
                    black += 1
                elif self.board[y][x] == 2:
                    white += 1
        return blank,black,white

    def put(self, x: int, y: int, color: int) -> bool:  # N=8 O(N^2)
        rlen = self.reverse_len(x, y, color)
        if len([i for i in rlen if i != 0]) == 0:
            return False
        for i, l in enumerate(rlen):
            dx, dy = SizedOthello.dirs[i]
            for j in range(l + 1):
                self.board[y + dy * j][x + dx * j] = color
        return True

    def reverse_len(self, x: int, y: int, color: int) -> list[int]:  # O(N^2)
        result = []
        if self.board[y][x] != 0:
            return [0] * 8
        for dx, dy in self.dirs:
            opp = 3 - color
            i = 1
            while (
                    y + dy * i in range(self.size)
                    and x + dx * i in range(self.size)
                    and self.board[y + dy * i][x + dx * i] == opp
            ):
                i += 1
            if (
                    i > 1
                    and y + dy * i in range(self.size)
                    and x + dx * i in range(self.size)
                    and self.board[y + dy * i][x + dx * i] == color
            ):
                result.append(i - 1)
            else:
                result.append(0)
        return result

    def is_possible_to_put(self, x: int, y: int, color: int) -> bool:  # O(N^2)
        return len([i for i in self.reverse_len(x, y, color) if i != 0]) > 0

    def possible_puts(self, color: int) -> list[tuple[int, int]]:  # O(N^4)
        ret = []
        for y in range(self.size):
            for x in range(self.size):
                if self.is_possible_to_put(x, y, color):
                    ret.append((x, y))
        return ret

    def is_possible_to_put_anywhere(self, color: int) -> bool:  # O(N^4)
        return len(self.possible_puts(color)) > 0

    def winner(self) -> int | None:  # O(N^4)
        if self.is_possible_to_put_anywhere(1) or self.is_possible_to_put_anywhere(2):
            return None
        _,b,w = self.count()
        if b == w:
            return 0
        elif b > w:
            return 1
        else:
            return 2

    def play(
            self,
            black: Callable[[Self, int], tuple[int, int]] = terminal_play,
            white: Callable[[Self, int], tuple[int, int]] = terminal_play,
            do_print: bool = True,
            guide: bool = True,
    ) -> int:  # O(N^6*player)=2.6*10^6*player
        c = 1
        while self.winner() is None:
            if do_print:
                self.print(guide)
            if not self.is_possible_to_put_anywhere(c):
                self.history.append(None)
                c = 3 - c
            player = black if c == 1 else white
            x, y = player(self, c)
            self.put(x, y, c)
            self.history.append((x, y))
            c = 3 - c
        return self.winner()

    def copy(self) -> Self:
        o = SizedOthello(self.size)
        for y in range(o.size):
            for x in range(o.size):
                o.board[y][x] = self.board[y][x]
        return o

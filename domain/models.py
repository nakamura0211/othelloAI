import numpy as np
import abc
from typing import Callable
from dataclasses import dataclass
from copy import deepcopy
from enum import IntEnum


class Color(IntEnum):
    BLANK = 0
    BLACK = 1
    WHITE = 2

    def reverse(self):
        if self == Color.BLANK:
            return Color.BLANK
        elif self == Color.BLACK:
            return Color.WHITE
        else:
            return Color.BLACK


SIZE = 6
Board = list[list[Color]]
BoardImage = np.ndarray[np.ndarray[np.ndarray[np.uint8]]]  # (SIZE,SIZE,3)


@dataclass
class State:
    board: Board
    color: Color

    @staticmethod
    def from_image(image: BoardImage, color: Color):
        if color == Color.BLACK:
            return State((image[:, :, 0] + image[:, :, 1] * 2).tolist(), color)
        else:
            return State((image[:, :, 0] * 2 + image[:, :, 1]).tolist(), color)
        board = [[0] * SIZE for _ in range(SIZE)]
        for x in range(SIZE):
            for y in range(SIZE):
                if image[y, x, 0] == 1:
                    board[y][x] = 1
                elif image[y, x, 1] == 1:
                    board[y][x] = 2
        return State(board, image[0, 0, 2])

    def to_image(self) -> BoardImage:
        b = np.array(self.board)
        me = b == self.color
        opp = b == self.color.reverse()
        return np.stack([me, opp], axis=2).astype(np.float32)

        image = np.zeros((SIZE, SIZE, 3))
        for x in range(SIZE):
            for y in range(SIZE):
                if self.board[y][x] == 1:
                    image[y, x, 0] = 1
                elif self.board[y][x] == 2:
                    image[y, x, 1] = 1
                image[y, x, 2] = self.color - 1
        return image

    def copy(self, board=None, color=None):
        return State(
            deepcopy(self.board if board is None else board),
            self.color if color is None else color,
        )

    # 90,180,270度回転したものを返す
    def turn(self):
        return (
            State([l[::-1] for l in self.board], self.color),
            State([l[::-1] for l in self.board[::-1]], self.color),
            State([l[::1] for l in self.board[::-1]], self.color),
        )


class Action:
    def __init__(self, x: int, y: int | None = None):
        if y is None:
            self.index = x
            self.x = x // SIZE
            self.y = x % SIZE
        else:
            self.index = x * SIZE + y
            self.x = x
            self.y = y
        self.cord = (self.x, self.y)

    def turn(self):
        return (
            Action(SIZE - self.x - 1, self.y),
            Action(SIZE - self.x - 1, SIZE - self.y - 1),
            Action(self.x, SIZE - self.y - 1),
        )

    def __str__(self):
        return f"{self.x} {self.y}"


EvaluateState = Callable[[State], float]
EvaluateAction = Callable[[State, Action], float]
Policy = Callable[[State], np.ndarray[np.ndarray[np.float32]]]


class Agent(abc.ABC):
    @abc.abstractmethod
    def act(self, state: State) -> Action:
        pass

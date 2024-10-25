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
        board = image[0].tolist()
        return State(board, color)

    def to_image(self) -> BoardImage:
        image = np.zeros((SIZE, SIZE, 3))
        for x in range(SIZE):
            for y in range(SIZE):
                image[y, x, 0] = self.board[y][x]
                if self.board[y][x] == 1:
                    image[y, x, 1] = 1
                elif self.board[y][x] == 2:
                    image[y, x, 2] = 1
        return image

    def copy(self, board=None, color=None):
        return State(
            deepcopy(self.board if board is None else board),
            self.color if color is None else color,
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


EvaluateState = Callable[[State], float]
EvaluateAction = Callable[[State, Action], float]
Policy = Callable[[State], np.ndarray[np.ndarray[np.float32]]]


class Agent(abc.ABC):
    @abc.abstractmethod
    def act(self, state: State) -> Action:
        pass

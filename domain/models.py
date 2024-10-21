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


SIZE = 8
Board = list[list[Color]]
BoardImage = np.ndarray[np.ndarray[np.ndarray[np.uint8]]]


@dataclass
class State:
    board: Board
    color: Color

    def to_image() -> BoardImage:
        pass

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


class Agent(abc.ABC):
    @abc.abstractmethod
    def act(self, state: State) -> Action:
        pass

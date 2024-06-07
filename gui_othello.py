import sys

import pygame.locals
from othello import Othello
import pygame
from pygame.locals import *
from collections.abc import Callable
import math


class GUI_Othello(Othello):
    def __init__(self) -> None:
        super().__init__()

    def play(
        self,
        black=None,
        white=None,
    ):
        pygame.init()
        screen = pygame.display.set_mode((600, 600))
        color = 1
        pos_puts = self.possible_puts(1)
        winner = -1
        end_flag = False
        while True:
            player = black if color == 1 else white
            screen.fill((0, 155, 0))
            if len(self.history) > 0:
                x, y = self.history[-1]
                pygame.draw.rect(
                    screen,
                    (180, 180, 0),
                    Rect(44 + 64 * x, 44 + 64 * y, 64, 64),
                )
            for i in range(9):
                pygame.draw.line(
                    screen, (0, 0, 0), (i * 64 + 44, 44), (i * 64 + 44, 556), 1
                )
            for i in range(9):
                pygame.draw.line(
                    screen, (0, 0, 0), (44, i * 64 + 44), (556, i * 64 + 44), 1
                )

            for y in range(8):
                for x in range(8):
                    s = self.board[y][x]
                    if s == 0:
                        continue
                    c = (0, 0, 0) if s == 1 else (255, 255, 255)
                    pygame.draw.circle(screen, c, (76 + x * 64, 76 + y * 64), 25)
            pygame.display.update()
            if player is not None:
                x, y = player(self, color)
                self.put(x, y, color)
                self.history.append((x, y))
                color = 3 - color
                if not self.is_possible_to_put_anywhere(color):
                    color = 3 - color
                w = self.winner()
                if w is not None:
                    winner = w
                    break
                pos_puts = self.possible_puts(color)
                pygame.display.update()
                continue

            for e in pygame.event.get():
                if e.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif e.type == MOUSEBUTTONDOWN:
                    x, y = map(lambda x: math.floor((x - 44) / 64), e.pos)
                    if (x, y) in pos_puts:
                        self.put(x, y, color)
                        self.history.append((x, y))
                        color = 3 - color
                        if not self.is_possible_to_put_anywhere(color):
                            color = 3 - color
                        w = self.winner()
                        if w is not None:
                            winner = w
                            end_flag = True
                        pos_puts = self.possible_puts(color)
                elif e.type == MOUSEMOTION:
                    x, y = map(lambda x: math.floor((x - 44) / 64), e.pos)
                    if (x, y) in pos_puts:
                        pygame.mouse.set_cursor(pygame.cursors.diamond)
                    else:
                        pygame.mouse.set_cursor(pygame.cursors.arrow)
            if end_flag:
                break
            pygame.display.update()

        return winner

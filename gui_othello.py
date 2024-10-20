import sys

import pygame.locals
import pygame
from pygame.locals import *
import math
import OthelloEnv
from type import Agent


class GUI_Othello:
    def __init__(self) -> None:
        super().__init__()

    def play(self, black: Agent | None = None, white: Agent | None = None, size=6):
        pygame.init()
        screen = pygame.display.set_mode((600, 600))
        state = OthelloEnv.reset(size)
        pos_puts = [
            OthelloEnv.action_to_cord(state, action)
            for action in OthelloEnv.valid_actions(state)
        ]
        winner = -1
        end_flag = False
        history = []
        color = 0
        # ゲームループ
        while True:
            player = black if color == 0 else white
            screen.fill((0, 155, 0))
            # 一手前の手をハイライト
            if len(history) > 0:
                x, y = history[-1]
                pygame.draw.rect(
                    screen,
                    (180, 180, 0),
                    Rect(44 + 64 * x, 44 + 64 * y, 64, 64),
                )
            # 枠線
            length = 64 * size + 44
            for i in range(size + 1):
                pygame.draw.line(
                    screen, (0, 0, 0), (i * 64 + 44, 44), (i * 64 + 44, length), 1
                )
            for i in range(size + 1):
                pygame.draw.line(
                    screen, (0, 0, 0), (44, i * 64 + 44), (length, i * 64 + 44), 1
                )
            # オセロの石
            for y in range(size):
                for x in range(size):
                    s = state[0, y, x] + state[1, y, x] * 2
                    if s == 0:
                        continue
                    c = (0, 0, 0) if s == 1 else (255, 255, 255)
                    pygame.draw.circle(screen, c, (76 + x * 64, 76 + y * 64), 25)
            # 描画
            pygame.display.update()
            if player is not None:
                action = player.act(state)
                print(color)
                print(action)
                next_state, reward, done = OthelloEnv.step(state, action)
                state = next_state
                x, y = OthelloEnv.action_to_cord(state, action)
                history.append((x, y))
                color = state[2, 0, 0]
                if done:
                    winner = OthelloEnv.winner(state)
                    break
                pos_puts = [
                    OthelloEnv.action_to_cord(state, action)
                    for action in OthelloEnv.valid_actions(state)
                ]
                pygame.display.update()
                continue

            for e in pygame.event.get():
                if e.type == QUIT:
                    pygame.quit()
                    sys.exit()
                # クリックされたとき
                elif e.type == MOUSEBUTTONDOWN:
                    # どのセルがクリックされたのか
                    x, y = map(lambda x: math.floor((x - 44) / 64), e.pos)
                    # 置けるセルなら処理する
                    if (x, y) in pos_puts:
                        next_state, reward, done = OthelloEnv.step(state, (x, y))
                        state = next_state
                        history.append((x, y))
                        color = state[2, 0, 0]
                        if done:
                            winner = OthelloEnv.winner(state)
                            end_flag = True

                        pos_puts = [
                            OthelloEnv.action_to_cord(state, action)
                            for action in OthelloEnv.valid_actions(state)
                        ]
                # マウスが動いたとき
                elif e.type == MOUSEMOTION:
                    # 触っているセルを計算
                    x, y = map(lambda x: math.floor((x - 44) / 64), e.pos)
                    # 置けるセルなら表示を変える
                    if (x, y) in pos_puts:
                        pygame.mouse.set_cursor(pygame.cursors.diamond)
                    else:
                        pygame.mouse.set_cursor(pygame.cursors.arrow)
            if end_flag:
                break
            pygame.display.update()
        while True:
            pass

        return winner

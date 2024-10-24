import sys

import pygame.locals
import pygame
from pygame.locals import *
import math
from domain.models import *
from domain import OthelloEnv


def play(
    black: Agent | None = None,
    white: Agent | None = None,
    size=SIZE,
    get_policy: Policy = None,
):
    pygame.init()
    screen = pygame.display.set_mode((600, 600))
    state = OthelloEnv.reset()
    pos_puts = [action.cord for action in OthelloEnv.valid_actions(state)]
    winner = -1
    end_flag = False
    history = []
    policy_cache = (state, None)
    # ゲームループ
    while True:
        player = black if state.color == Color.BLACK else white
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

        if get_policy is not None:
            if state.color != policy_cache[0] or policy_cache[1] is None:
                policy: np.ndarray = get_policy(state)[0]
                policy = policy - np.average(policy)
                policy = policy / np.max(np.abs(policy)) * 10
                print(policy)
                policy_cache = (state.color, policy)
            else:
                policy = policy_cache[1]

            for y in range(size):
                for x in range(size):
                    p = policy[Action(x, y).index]
                    if p > 0:
                        c = (0, 180, min(p * 255, 255))
                    else:
                        c = (min(-p * 255, 255), 180, 0)
                    # print(c)
                    pygame.draw.rect(screen, c, Rect(44 + 64 * x, 44 + 64 * y, 64, 64))
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
                if state.board[y][x] == 0:
                    continue
                c = (0, 0, 0) if state.board[y][x] == 1 else (255, 255, 255)
                pygame.draw.circle(screen, c, (76 + x * 64, 76 + y * 64), 25)

        # 描画
        pygame.display.update()
        if player is not None:
            action = player.act(state)
            next_state, reward, done = OthelloEnv.step(state, action)
            state = next_state
            x, y = action.cord
            history.append((x, y))
            color = state.color
            if done:
                winner = OthelloEnv.winner(state)
                break
            pos_puts = [action.cord for action in OthelloEnv.valid_actions(state)]
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
                    next_state, reward, done = OthelloEnv.step(state, Action(x, y))
                    state = next_state
                    history.append((x, y))
                    color = state.color
                    if done:
                        winner = OthelloEnv.winner(state)
                        end_flag = True

                    pos_puts = [
                        action.cord for action in OthelloEnv.valid_actions(state)
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
    print(winner)
    while True:
        pygame.display.update()

    return winner

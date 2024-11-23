import sys

import pygame.locals
import pygame
from pygame.locals import *
import math
from domain.models import *
from domain import OthelloEnv
from keras.src.layers import BatchNormalization
from time import sleep


@dataclass
class UiState:
    othello_state: State
    possible_puts: set[tuple[int, int]]
    history: list[tuple[int, int]]
    policy_cache: tuple[int, list] | None


def play(
    black: Agent | None = None,
    white: Agent | None = None,
    get_policy: Policy = None,
):
    pygame.init()
    screen = pygame.display.set_mode((88 + 64 * SIZE, 88 + 64 * SIZE))
    ui_state = UiState(
        OthelloEnv.reset(),
        {action.cord for action in OthelloEnv.valid_actions(OthelloEnv.reset())},
        [],
        None,
    )
    while not OthelloEnv.is_done(ui_state.othello_state):
        player = black if ui_state.othello_state.color == Color.BLACK else white
        _draw(screen, ui_state, get_policy)
        _act_if_npc(ui_state, player)
        _handle_events(ui_state)

    _, b, w = OthelloEnv.count(ui_state.othello_state)
    winner = OthelloEnv.winner(ui_state.othello_state)
    print(f"black: {b} white: {w}")

    while True:
        _draw(screen, ui_state, None)
        _handle_events(ui_state)
        sleep(0.1)


def _draw(
    screen,
    ui_state: UiState,
    policy_func: Policy,
):
    screen.fill((0, 155, 0))
    # 一手前をハイライト
    if len(ui_state.history) > 0:
        x, y = ui_state.history[-1]
        pygame.draw.rect(
            screen,
            (180, 180, 0),
            Rect(44 + 64 * x, 44 + 64 * y, 64, 64),
        )
    # 枠線
    if policy_func is not None:
        if (
            ui_state.policy_cache is None
            or ui_state.othello_state.color != ui_state.policy_cache[0]
        ):
            policy: np.ndarray = policy_func(ui_state.othello_state)
            print(policy.reshape(SIZE, SIZE).T)
            print(policy.mean())
            ui_state.policy_cache = (ui_state.othello_state.color, policy)
        else:
            policy = ui_state.policy_cache[1]
        for y in range(SIZE):
            for x in range(SIZE):
                p = (
                    policy[Action(x, y).index]
                    if (x, y) in ui_state.possible_puts
                    else 0
                )
                if p == 0:
                    c = (0, 180, 0)
                elif p > 0:
                    c = (0, min(180, 80 / p), min(p * 255, 255))
                else:
                    c = (min(-p * 255, 255), min(-80 / p, 180), 0)
                # print(c)
                pygame.draw.rect(screen, c, Rect(44 + 64 * x, 44 + 64 * y, 64, 64))
    length = 64 * SIZE + 44
    for i in range(SIZE + 1):
        pygame.draw.line(screen, (0, 0, 0), (i * 64 + 44, 44), (i * 64 + 44, length), 1)
    for i in range(SIZE + 1):
        pygame.draw.line(screen, (0, 0, 0), (44, i * 64 + 44), (length, i * 64 + 44), 1)
        # オセロの石
    for y in range(SIZE):
        for x in range(SIZE):
            if ui_state.othello_state.board[y][x] == 0:
                continue
            c = (
                (0, 0, 0)
                if ui_state.othello_state.board[y][x] == 1
                else (255, 255, 255)
            )
            pygame.draw.circle(screen, c, (76 + x * 64, 76 + y * 64), 25)
    # 描画
    pygame.display.update()


def _act_if_npc(ui_state: UiState, player: Agent | None):
    if player == None:
        return
    action = player.act(ui_state.othello_state)
    next_state, reward, done = OthelloEnv.step(ui_state.othello_state, action)
    ui_state.othello_state = next_state
    x, y = action.cord
    ui_state.history.append((x, y))
    ui_state.possible_puts = {
        action.cord for action in OthelloEnv.valid_actions(ui_state.othello_state)
    }


def _handle_events(ui_state: UiState):
    for e in pygame.event.get():
        if e.type == QUIT:
            pygame.quit()
            sys.exit()
        # クリックされたとき
        elif e.type == MOUSEBUTTONDOWN:
            # どのセルがクリックされたのか
            x, y = map(lambda x: math.floor((x - 44) / 64), e.pos)
            # 置けるセルなら処理する
            if (x, y) in ui_state.possible_puts:
                next_state, reward, done = OthelloEnv.step(
                    ui_state.othello_state, Action(x, y)
                )
                ui_state.history.append((x, y))
                ui_state.othello_state = next_state
                ui_state.possible_puts = {
                    action.cord for action in OthelloEnv.valid_actions(next_state)
                }
        # マウスが動いたとき
        elif e.type == MOUSEMOTION:
            # 触っているセルを計算
            x, y = map(lambda x: math.floor((x - 44) / 64), e.pos)
            # 置けるセルなら表示を変える
            if (x, y) in ui_state.possible_puts:
                pygame.mouse.set_cursor(pygame.cursors.diamond)
            else:
                pygame.mouse.set_cursor(pygame.cursors.arrow)

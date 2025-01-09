import sys

import pygame.gfxdraw
import pygame.locals
import pygame
from pygame.locals import *
import math
from domain.models import *
from domain import OthelloEnv
import ray
from time import sleep
from concurrent.futures import ThreadPoolExecutor


@dataclass
class UiState:
    othello_state: State
    possible_puts: set[tuple[int, int]]
    history: list[tuple[int, int]]
    policy_cache: tuple[int, np.ndarray] | None
    show_graph: bool
    v_history: list[tuple[int, float]]


class Worker:
    def __init__(self, ui_state: UiState, get_policy: Policy = None):
        self.ui_state = ui_state
        self.executer = ThreadPoolExecutor(max_workers=4)
        self.get_policy = get_policy
        self.is_policy_calcing = False
        self.is_npc_calcing = False

    def calc_policy_func(self):
        if self.is_policy_calcing:
            return
        self.is_policy_calcing = True
        future = self.executer.submit(
            Worker._calc_policy, self.ui_state.othello_state, self.get_policy
        )
        future.add_done_callback(
            lambda x: self.ui_state.__setattr__(
                "policy_cache", (self.ui_state.othello_state.color, x.result())
            )
            or self.__setattr__("is_policy_calcing", False)
        )

    @staticmethod
    def _calc_policy(othello_state, policy_func: Policy):
        return policy_func(othello_state)

    def calc_npc(self, agent: Agent):
        if self.is_npc_calcing:
            return
        self.is_npc_calcing = True
        future = self.executer.submit(agent.act, self.ui_state.othello_state)
        future.add_done_callback(lambda f: self.on_npc_acted(f.result()))

    def on_npc_acted(self, action: Action):
        actor = self.ui_state.othello_state.color
        next_state, reward, done = OthelloEnv.step(self.ui_state.othello_state, action)
        self.ui_state.othello_state = next_state
        x, y = action.cord
        self.ui_state.history.append((x, y))
        if self.ui_state.show_graph:
            if self.ui_state.policy_cache is not None:
                self.ui_state.v_history.append(
                    (actor, self.ui_state.policy_cache[1][action.index])
                )

        self.ui_state.possible_puts = {
            action.cord
            for action in OthelloEnv.valid_actions(self.ui_state.othello_state)
        }
        self.is_npc_calcing = False


pygame.init()
font = pygame.font.SysFont(None, 16)


def play(
    black: Agent | None = None,
    white: Agent | None = None,
    get_policy: Policy = None,
    show_graph: bool = True,
):
    screen = pygame.display.set_mode(
        (88 + 64 * SIZE + 200 * show_graph, 88 + 64 * SIZE)
    )
    ui_state = UiState(
        OthelloEnv.reset(),
        {action.cord for action in OthelloEnv.valid_actions(OthelloEnv.reset())},
        [],
        None,
        show_graph,
        [],
    )
    worker = Worker(ui_state, get_policy)
    while not OthelloEnv.is_done(ui_state.othello_state):
        player = black if ui_state.othello_state.color == Color.BLACK else white
        _draw(screen, ui_state, worker)
        if player is not None:
            worker.calc_npc(player)
        _handle_events(ui_state, worker.is_npc_calcing)
        sleep(0.1)

    _, b, w = OthelloEnv.count(ui_state.othello_state)
    winner = OthelloEnv.winner(ui_state.othello_state)
    ui_state.v_history.append(
        (ui_state.othello_state.color, OthelloEnv.reward(ui_state.othello_state))
    )

    print(f"black: {b} white: {w}")

    while True:
        _draw(screen, ui_state, None)
        _handle_events(ui_state, worker)
        sleep(0.1)


def _draw_graph(screen, ui_state: UiState):
    x_origin = 64 * SIZE + 88
    y_origin = 32 * SIZE + 44
    y_height = 32 * SIZE
    pygame.draw.line(
        screen,
        (0, 0, 0),
        (x_origin, y_origin),
        (x_origin + 32 * 6, y_origin),
    )

    pygame.draw.line(
        screen,
        (0, 0, 0),
        (x_origin, y_origin - 64 * 3),
        (x_origin, y_origin + 64 * 3),
    )
    bs = [(0, 0)]
    ws = [(-0.5, 0)]
    for i, (c, v) in enumerate(ui_state.v_history):
        if c == Color.BLACK:
            bs.append((i, v))
        else:
            ws.append((i, v))

    for j in range(len(bs) - 1):
        i, v = bs[j]
        i2, v2 = bs[j + 1]
        x1 = x_origin + i * 6
        y1 = int(y_origin - v * y_height)
        x2 = x_origin + i2 * 6
        y2 = int(y_origin - v2 * y_height)
        pygame.gfxdraw.line(screen, x1, y1, x2, y2, (0, 0, 0))
        pygame.gfxdraw.aapolygon(screen, [(x1, y1), (x2, y2), (x1, y1)], (0, 0, 0))

    for j in range(len(ws) - 1):
        i, v = ws[j]
        i2, v2 = ws[j + 1]
        x1 = int(x_origin + i * 6 + 3)
        y1 = int(y_origin - v * y_height)
        x2 = x_origin + i2 * 6 + 3
        y2 = int(y_origin - v2 * y_height)
        pygame.gfxdraw.line(screen, x1, y1, x2, y2, (255, 255, 255))
        pygame.gfxdraw.aapolygon(
            screen, [(x1, y1), (x2, y2), (x1, y1)], (255, 255, 255)
        )


def _draw_num_stones(screen, ui_state: UiState):
    x_mid = 32 * SIZE + 44
    y_mid = 64 * SIZE + 66
    _, b, w = OthelloEnv.count(ui_state.othello_state)
    screen.blit(
        font.render(f"{b} vs {w}", False, (0, 0, 0)),
        (x_mid - 16, y_mid),
    )
    done = OthelloEnv.is_done(ui_state.othello_state)
    if done or ui_state.othello_state.color == Color.BLACK:
        pygame.draw.circle(screen, (0, 0, 0), (x_mid - 13, y_mid - 10), 5)
    if done or ui_state.othello_state.color == Color.WHITE:
        pygame.draw.circle(screen, (255, 255, 255), (x_mid + 13, y_mid - 10), 5)


def _draw(screen, ui_state: UiState, worker: Worker):
    screen.fill((0, 155, 0))
    # 一手前をハイライト
    if len(ui_state.history) > 0:
        x, y = ui_state.history[-1]
        pygame.draw.rect(
            screen,
            (180, 180, 0),
            Rect(44 + 64 * x, 44 + 64 * y, 64, 64),
        )
    if worker is not None and worker.get_policy is not None:
        if (
            ui_state.policy_cache is None
            or ui_state.othello_state.color != ui_state.policy_cache[0]
        ):
            # 枠線
            worker.calc_policy_func()
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
                    pygame.draw.rect(screen, c, Rect(44 + 64 * x, 44 + 64 * y, 64, 64))
                    if (x, y) in ui_state.possible_puts:
                        screen.blit(
                            font.render(f"{p:.2f}", False, (0, 0, 0)),
                            (80 + 64 * x, 96 + 64 * y),
                        )
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
    _draw_graph(screen, ui_state)
    _draw_num_stones(screen, ui_state)

    # 描画
    pygame.display.update()


def _handle_events(ui_state: UiState, is_npc_calcing: bool):
    for e in pygame.event.get():
        if e.type == QUIT:
            pygame.quit()
            sys.exit()
        # クリックされたとき
        elif e.type == MOUSEBUTTONDOWN and not is_npc_calcing:
            # どのセルがクリックされたのか
            x, y = map(lambda x: math.floor((x - 44) / 64), e.pos)
            # 置けるセルなら処理する
            if (x, y) in ui_state.possible_puts:
                next_state, reward, done = OthelloEnv.step(
                    ui_state.othello_state, Action(x, y)
                )
                ui_state.history.append((x, y))
                actor = ui_state.othello_state.color
                ui_state.othello_state = next_state
                ui_state.possible_puts = {
                    action.cord for action in OthelloEnv.valid_actions(next_state)
                }
                if ui_state.show_graph:
                    if ui_state.policy_cache is not None:
                        ui_state.v_history.append(
                            (actor, ui_state.policy_cache[1][Action(x, y).index])
                        )
        # マウスが動いたとき
        elif e.type == MOUSEMOTION:
            # 触っているセルを計算
            x, y = map(lambda x: math.floor((x - 44) / 64), e.pos)
            # 置けるセルなら表示を変える
            if (x, y) in ui_state.possible_puts:
                pygame.mouse.set_cursor(pygame.cursors.diamond)
            else:
                pygame.mouse.set_cursor(pygame.cursors.arrow)

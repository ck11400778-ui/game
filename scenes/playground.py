from __future__ import annotations
import pygame
from typing import Any, Dict

def _coerce_build_args(args: tuple, kwargs: dict):
    assets = kwargs.get("assets")
    state  = kwargs.get("state")
    for x in args:
        if isinstance(x, dict):
            state = state or x
        else:
            assets = assets or x
    if state is None:
        state = {}
    return assets, state

def _coerce_loop_args(args: tuple, kwargs: dict):
    screen = kwargs.get("screen")
    state  = kwargs.get("state")
    assets = kwargs.get("assets")
    for x in args:
        try:
            if hasattr(x, "blit") and hasattr(x, "get_width"):
                screen = screen or x
                continue
        except Exception:
            pass
        if isinstance(x, dict):
            state = state or x
        else:
            assets = assets or x
    if screen is None:
        try:
            screen = pygame.display.get_surface()
        except Exception:
            screen = None
    if state is None:
        state = {}
    return screen, state, assets
import pygame
from core.ui import draw_text
from core.config import COLOR, WIDTH, HEIGHT, FPS
from core.input_utils import NAV_UP, NAV_DOWN, CONFIRM, BACK, is_keydown, clear_after_action
from core.dialogue import run_dialogue, run_lines
from core.emotions import add_emotion

TITLE = "操場 Playground"
OPTIONS = [
    ("與張博堯對話（磁場）", "playground_zhangboyao_intro", "stress", 5),
    ("與蔡芷涵對話（加速）", "playground_caizhihan_intro", "trust", 2),
    ("與王老師對話（教官）", "playground_teacher_wang_intro", "familiarity", 2),
]

def _build(assets, state):
    state.setdefault("playground_sel", 0)
    return {}

def build(*args, **kwargs):
    assets, state = _coerce_build_args(args, kwargs)
    return _build(assets, state)

def _loop(screen, state, assets):
    clock = pygame.time.Clock()
    sel = int(state.get("playground_sel", 0)) % len(OPTIONS)
    running = True
    while running and state.get("current") == "playground":
        screen.fill((16,18,22))
        draw_text(screen, TITLE, (48,48), color=COLOR.get("hint",(200,200,120)))
        y0 = 120
        for i,(label, did, emo, delta) in enumerate(OPTIONS):
            y = y0 + i*36
            if i == sel:
                pygame.draw.rect(screen, (60,60,90), pygame.Rect(40, y-4, 760, 28))
            draw_text(screen, label, (48, y), color=COLOR.get("text",(240,240,240)))
        draw_text(screen, "↑↓ 選擇 / Enter 互動 / Esc 返回", (48, HEIGHT-56), color=(180,180,180))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                state["current"]="exit"; running=False; break
            if is_keydown(event, NAV_UP): sel = (sel - 1) % len(OPTIONS)
            elif is_keydown(event, NAV_DOWN): sel = (sel + 1) % len(OPTIONS)
            elif is_keydown(event, BACK): state["current"]="world_map"; running=False; break
            elif is_keydown(event, CONFIRM):
                label, did, emo, delta = OPTIONS[sel]
                if did: run_dialogue(screen, did, state=state)
                if emo and delta: add_emotion(state, emo, delta)
                clear_after_action()
        state["playground_sel"] = sel
        clock.tick(FPS)

def loop(*args, **kwargs):
    screen, state, assets = _coerce_loop_args(args, kwargs)
    return _loop(screen, state, assets)

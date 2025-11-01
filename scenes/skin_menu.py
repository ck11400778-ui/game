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
from core.skins import list_skins, get_current_skin, set_skin
from core.overlay_hook import push_note

def _build(assets, state): return {}

def build(*args, **kwargs):
    assets, state = _coerce_build_args(args, kwargs)
    return _build(assets, state)

def _loop(screen, state, assets):
    clock = pygame.time.Clock()
    items = list_skins()
    try:
        cur_idx = items.index(get_current_skin(state))
    except Exception:
        cur_idx = 0

    running = True
    while running and state.get("current") == "skin_menu":
        screen.fill((18,18,24))
        draw_text(screen, "換圖/風格 Skin", (56,56), color=COLOR.get("hint",(200,200,120)))
        y0 = 120
        for i, name in enumerate(items):
            y = y0 + i*36
            if i == cur_idx:
                pygame.draw.rect(screen, (70,70,105), pygame.Rect(44, y-4, 520, 28))
            draw_text(screen, name, (56, y), color=COLOR.get("text",(240,240,240)))
        draw_text(screen, "↑↓ 選擇 / Enter 套用 / Esc 返回", (56, HEIGHT-56), color=(180,180,180))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                state["current"] = "exit"; running = False; break
            if is_keydown(event, NAV_UP): cur_idx = (cur_idx - 1) % len(items)
            elif is_keydown(event, NAV_DOWN): cur_idx = (cur_idx + 1) % len(items)
            elif is_keydown(event, BACK): state["current"] = "menu"; running = False; break
            elif is_keydown(event, CONFIRM):
                set_skin(state, items[cur_idx])
                push_note(state, f"已套用風格：{items[cur_idx]}")
                clear_after_action()
        clock.tick(FPS)

def loop(*args, **kwargs):
    screen, state, assets = _coerce_loop_args(args, kwargs)
    return _loop(screen, state, assets)

from __future__ import annotations
import pygame
from core.ui import draw_text
from core.config import COLOR, WIDTH, HEIGHT, FPS
from core.dialogue import run_dialogue, run_lines

def build(assets, state=None):
    state = state or {}
    return {}

def loop(screen, state, assets):
    # 一次性播完家中醒來的對話，然後進入 roam
    try:
        run_dialogue(screen, "home_wakeup", state=state)
    except Exception:
        run_lines(screen, [{"speaker":"主角","text":"……早上了。該去學校了。"}], state=state)
    state["area"] = "home_room"
    state["current"] = "roam"

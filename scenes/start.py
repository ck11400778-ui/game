# -*- coding: utf-8 -*-
# Compatibility: assets argument is optional.
from __future__ import annotations
import pygame
from typing import Dict, Any, List
from core.ui import draw_text
from core.config import COLOR, WIDTH, HEIGHT, FPS
from core.save import save_state, load_state
from core.overlay_hook import push_note
from core.storyflow import run_flow

MENU: List[str] = ["繼續 Continue", "新遊戲 New Game", "離開 Exit"]

def _reset_state(state: Dict[str, Any], assets=None):
    state.clear()
    state["assets"] = assets
    state["skin"] = "default"
    state["calendar"] = {"week":1, "day":1}
    state["ap_max"] = 3
    state["ap"] = 3
    state["flags"] = {}
    state["current"] = "start"

def build(assets=None, state=None):
    state = state or {}
    state.setdefault("start_sel", 0)
    return {}

def _play_cinematic(screen, state):
    # 第一章 → 第二章（前半）→ 觸火 → 第二章（後半）→ 第三章 → 回家過夜 → 自由探索
    run_flow(screen, state, "ch1_awaken_before")
    run_flow(screen, state, "ch2_fire_shadow_part1")
    state["current"]="touch_fire_trial"
    import scenes.touch_fire_trial as trial
    trial.build(state.get("assets"), state)
    trial.loop(screen, state, state.get("assets"))
    run_flow(screen, state, "ch2_fire_shadow_part2")
    run_flow(screen, state, "ch3_first_match")
    state["current"]="home_return"
    import scenes.home_return as hr
    hr.build(state.get("assets"), state)
    hr.loop(screen, state, state.get("assets"))
    state.setdefault("flags", {})["cinematic_chain_complete"] = True
    state.setdefault("area","home_room")
    state["current"]="roam"

def loop(screen, state, assets=None):
    assets = state.get("assets") if assets is None else assets
    clock = pygame.time.Clock()
    sel = int(state.get("start_sel", 0)) % len(MENU)
    running = True
    while running and state.get("current","start") == "start":
        screen.fill((16, 18, 28))
        draw_text(screen, "校園異能 RPG", (64, 70), color=COLOR.get("hint",(200,200,160)))
        for i, label in enumerate(MENU):
            y = 180 + i*40
            if i == sel:
                pygame.draw.rect(screen, (60,80,120), pygame.Rect(56, y-6, 360, 30))
            draw_text(screen, label, (64, y), color=COLOR.get("text",(240,240,240)))
        draw_text(screen, "↑↓ 選擇  Enter 確認", (64, 360), color=(180,180,180))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                state["current"] = "exit"; running=False; break
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    sel = (sel - 1) % len(MENU)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    sel = (sel + 1) % len(MENU)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    label = MENU[sel]
                    if label.startswith("繼續"):
                        loaded = load_state(slot=0)
                        if loaded:
                            loaded["assets"] = assets
                            state.clear(); state.update(loaded)
                            if not state.get("current"): state["current"]="roam"
                            if state.get("current")=="menu": state["current"]="roam"
                            state.setdefault("flags", {})["cinematic_chain_complete"] = True
                            push_note(state, "已讀取存檔")
                            return
                        else:
                            push_note(state, "沒有存檔可讀取")
                    elif label.startswith("新遊戲"):
                        _reset_state(state, assets)
                        _play_cinematic(screen, state)
                        return
                    elif label.startswith("離開"):
                        state["current"] = "exit"; return
        state["start_sel"] = sel
        clock.tick(FPS)

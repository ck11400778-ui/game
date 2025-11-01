# -*- coding: utf-8 -*-
# Compatibility: assets argument is optional.
from __future__ import annotations
import pygame
from core.dialogue import run_dialogue, run_lines

try:
    from core.overlay_hook import end_day
except Exception:
    def end_day(state):
        cal = state.setdefault("calendar", {"week":1,"day":1})
        d = int(cal.get("day",1)) + 1
        w = int(cal.get("week",1))
        if d > 7: d = 1; w += 1
        cal["day"] = d; cal["week"] = w

def build(assets=None, state=None):
    return {}

def loop(screen, state, assets=None):
    try:
        run_dialogue(screen,"home_after_three_chapters",state=state)
    except Exception:
        run_lines(screen,[{"speaker":"系統","text":"你回到家，長夜無語。"}],state=state)
    end_day(state)
    state.setdefault("flags", {})["cinematic_chain_complete"] = True
    state["area"]="home_room"
    state["current"]="roam"

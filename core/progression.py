# project/core/progression.py
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, Any
try:
    from core.config import ACTION_POINTS_PER_DAY
except Exception:
    ACTION_POINTS_PER_DAY = 3
from core.emotions import ensure_emotions, get_emotion

@dataclass
class Calendar:
    week: int = 1   # 1..4
    day: int = 1    # 1..7  (可依需要調整；設計書用「每月4週」)
    month: int = 1  # 之後可擴充多月

@dataclass
class ActionPoints:
    max_ap: int = ACTION_POINTS_PER_DAY
    ap: int = ACTION_POINTS_PER_DAY

def ensure_progression_state(state: Dict[str, Any]) -> None:
    state.setdefault("calendar", asdict(Calendar()))
    state.setdefault("ap", asdict(ActionPoints()))

def spend_ap(state: Dict[str, Any], cost: int = 1) -> bool:
    ensure_progression_state(state)
    ap = state["ap"]
    if ap["ap"] >= cost:
        ap["ap"] -= cost
        return True
    return False

def ap_left(state: Dict[str, Any]) -> int:
    ensure_progression_state(state)
    return state["ap"]["ap"]

def end_day(state: Dict[str, Any]) -> None:
    ensure_progression_state(state)
    cal = state["calendar"]
    cal["day"] += 1
    if cal["day"] > 7:
        cal["day"] = 1
        cal["week"] += 1
        if cal["week"] > 4:
            cal["week"] = 1
            cal["month"] += 1
    # reset AP
    ap = state["ap"]
    ap["ap"] = ap["max_ap"]
    # 夢境觸發條件：壓力過高（>=50）或特定旗標
    ensure_emotions(state)
    if get_emotion(state, 'stress') >= 50:
        state['current'] = 'dream_trial'
    state.setdefault("flags", {})
    state["flags"].setdefault("night_count", 0)
    state["flags"]["night_count"] += 1

def debug_label(state: Dict[str, Any]) -> str:
    ensure_progression_state(state)
    c = state["calendar"]; ap = state["ap"]
    return f"W{c['week']} D{c['day']}  AP:{ap['ap']}/{ap['max_ap']}"

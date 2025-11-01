from __future__ import annotations
import pygame
from typing import Dict, List
from core.dialogue import run_dialogue
from core.overlay_hook import push_note

def _ensure_flags(state: Dict):
    return state.setdefault("flags", {})

def play_intro(screen, state: Dict) -> None:
    """在教室播放序章到『火種子』，不會卡住。"""
    flags = _ensure_flags(state)
    seq: List[str] = [
        "intro_wakeup",
        "intro_class_bell",
        "seed_of_fire",  # 火種子
    ]
    for did in seq:
        try:
            run_dialogue(screen, did, state=state)
        except Exception:
            # 即使缺檔也不中斷：顯示一行代替，避免卡死
            from core.dialogue import run_lines
            run_lines(screen, [{"speaker":"系統","text":f"(缺少對話檔 {did}.json，已跳過)"}], state=state)
        # 記錄進度
        flags["story_last"] = did
        if did == "seed_of_fire":
            flags["got_seed_of_fire"] = True
    push_note(state, "序章完成：獲得『火種子』")

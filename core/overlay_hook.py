# project/core/overlay_hook.py
from __future__ import annotations
import time
import pygame
from typing import Dict, Any
try:
    from core.ui import draw_text
except Exception:
    def draw_text(surface, txt, pos, color=(240,240,240), small=False):
        font = pygame.font.SysFont(None, 20 if small else 24)
        surface.blit(font.render(str(txt), True, color), pos)

try:
    from core.config import COLOR
except Exception:
    COLOR = {"text":(240,240,240), "panel":(32,32,36), "hint":(200,200,120)}

def _get_ui(state: Dict[str, Any]) -> Dict[str, Any]:
    return state.setdefault("ui", {})

def push_note(state: Dict[str, Any], text: str, ttl: float = 1.5) -> None:
    ui = _get_ui(state)
    notes = ui.setdefault("notes", [])
    notes.append({"text": text, "until": time.time() + ttl})

def _draw_notes(screen, state):
    ui = _get_ui(state)
    now = time.time()
    notes = ui.get("notes", [])
    notes[:] = [n for n in notes if n.get("until",0) > now]
    y = 10
    for n in notes:
        draw_text(screen, f"★ {n['text']}", (10, y), color=(255,215,0), small=False)
        y += 26

def _draw_calendar(screen, state):
    # show W?/D?/AP and emotions brief
    c = state.get("calendar", {})
    ap = state.get("ap", {})
    label = f"W{c.get('week','?')} D{c.get('day','?')}  AP:{ap.get('ap','?')}/{ap.get('max_ap','?')}"
    draw_text(screen, label, (10, screen.get_height()-30), color=COLOR.get("hint",(200,200,120)))
    # emotions line if exists
    emo = state.get("emotions")
    if isinstance(emo, dict) and emo:
        txt = "  ".join(f"{k}:{int(v)}" for k,v in emo.items())
        draw_text(screen, txt, (10, screen.get_height()-56), color=COLOR.get("text",(240,240,240)), small=False)

def _update_caption(state):
    c = state.get("calendar", {})
    ap = state.get("ap", {})
    pygame.display.set_caption(f"Game  W{c.get('week','?')} D{c.get('day','?')}  AP:{ap.get('ap','?')}/{ap.get('max_ap','?')}")

def install_flip_hook(state: Dict[str, Any]) -> None:
    """Wrap pygame.display.flip so我們能在任何場景結束前畫 HUD/日曆/通知。"""
    if getattr(pygame.display, "_vispatched", False):
        return
    _orig = pygame.display.flip
    def _flip():
        try:
            surf = pygame.display.get_surface()
            if surf:
                _draw_notes(surf, state)
                _draw_calendar(surf, state)
                _update_caption(state)
        except Exception:
            pass
        _orig()
    pygame.display.flip = _flip
    pygame.display._vispatched = True

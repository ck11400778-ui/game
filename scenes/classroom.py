from __future__ import annotations
import pygame
from core.ui import draw_text
from core.config import COLOR, WIDTH, HEIGHT, FPS
from core.input_utils import NAV_UP, NAV_DOWN, CONFIRM, BACK, is_keydown, clear_after_action
from core.dialogue import run_dialogue, run_lines
from core.emotions import add_emotion

TITLE = "教室 Classroom"
OPTIONS = [
    ("與林思妍對話（空間）", "classroom_linsiyan_intro", "trust", +3),
    ("與阿澤對話（摯友）", "classroom_aze_intro", "familiarity", +5),
    ("與陳敬豪對話（電子）", "classroom_chenjinghao_intro", "stress", -3),
]

def _ensure_flags(state):
    return state.setdefault("flags", {})

def build(assets, state=None):
    state = state or {}
    state.setdefault("classroom_sel", 0)
    return {}

def _maybe_play_intro(screen, state):
    flags = _ensure_flags(state)
    if not flags.get("got_seed_of_fire") or state.get("story_mode") == "intro":
        try:
            from core.story import play_intro
            play_intro(screen, state)
            state["story_mode"] = None
            flags["intro_done"] = True
        except Exception as e:
            from core.dialogue import run_lines
            run_lines(screen, [{"speaker":"系統","text":f"（序章無法播放：{e}）"}], state=state)

def loop(screen, state, assets):
    _maybe_play_intro(screen, state)
    clock = pygame.time.Clock()
    sel = int(state.get("classroom_sel", 0)) % len(OPTIONS)
    running = True
    while running and state.get("current") == "classroom":
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
        state["classroom_sel"] = sel
        clock.tick(FPS)

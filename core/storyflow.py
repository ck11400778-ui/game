from __future__ import annotations
import json, pygame
from typing import Dict, Any, List, Optional
from pathlib import Path

# Dialogue fallbacks
try:
    from core.dialogue import run_dialogue, run_lines
except Exception:
    def run_lines(screen, lines, **kw):
        import pygame
        font = pygame.font.SysFont(None, 22)
        screen.fill((0,0,0))
        y = 40
        for ln in lines:
            t = (ln.get("speaker","") + "：" if ln.get("speaker") else "") + ln.get("text","")
            surf = font.render(t, True, (230,230,230))
            screen.blit(surf, (40, y)); y += 28
        pygame.display.flip()
        clk = pygame.time.Clock()
        t=0
        while t < 800:
            for e in pygame.event.get():
                if e.type==pygame.KEYDOWN or e.type==pygame.MOUSEBUTTONDOWN: return
            clk.tick(60); t += clk.get_time()
    def run_dialogue(screen, dialogue_id: str, **kw):
        run_lines(screen, [{"speaker":"系統","text":f"(對話 {dialogue_id} 缺失，占位顯示)"}])

# Notes fallback
try:
    from core.overlay_hook import push_note
except Exception:
    def push_note(state, text, ttl=1.2): 
        print("[NOTE]", text)

# Resolve data directories relative to project root
def _guess_root() -> Path:
    # this file: core/storyflow.py -> project root is parent of 'core'
    here = Path(__file__).resolve()
    for p in [here.parent, here.parent.parent, here.parent.parent.parent]:
        if (p/"data").exists():
            return p
    return here.parent.parent

ROOT = _guess_root()
STORY_DIR = ROOT / "data" / "story"
DIALOGUE_DIR = ROOT / "data" / "dialogues"

def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

def load_flow(flow_id: str) -> Dict[str, Any]:
    p = STORY_DIR / f"{flow_id}.json"
    return _load_json(p)

def _effects_apply(state: Dict[str,Any], eff: Dict[str,Any]):
    if "set_flag" in eff:
        state.setdefault("flags", {})[eff["set_flag"]] = True
    if "unset_flag" in eff:
        state.setdefault("flags", {}).pop(eff["unset_flag"], None)
    if "ap_cost" in eff:
        ap = int(state.get("ap", 0)); need = int(eff["ap_cost"])
        state["ap"] = max(0, ap - need)
    if "emotion" in eff:
        try:
            from core.emotions import add_emotion
            var = eff["emotion"].get("var","familiarity")
            delta = int(eff["emotion"].get("delta", 0))
            add_emotion(state, var, delta)
        except Exception:
            pass

def _eligible(state: Dict[str,Any], node: Dict[str,Any]) -> bool:
    flags = state.setdefault("flags", {})
    for f in node.get("require_flags", []):
        if not flags.get(f): return False
    for f in node.get("forbid_flags", []):
        if flags.get(f): return False
    if "require_ap" in node and state.get("ap",0) < int(node["require_ap"]):
        return False
    return True

def _choice_menu(screen, choices: List[Dict[str,Any]], state: Dict[str,Any]) -> Optional[Dict[str,Any]]:
    WIDTH = screen.get_width(); HEIGHT = screen.get_height()
    font = pygame.font.SysFont(None, 24)
    sel = 0
    clk = pygame.time.Clock()
    while True:
        panel = pygame.Surface((int(WIDTH*0.7), int(HEIGHT*0.5)))
        panel.fill((24,24,30))
        pygame.draw.rect(panel, (0,0,0), panel.get_rect(), 2)
        y = 16
        title = font.render("選擇：", True, (230,230,180))
        panel.blit(title,(16,y)); y += 28
        visible = [ch for ch in choices if _eligible(state, ch)]
        if not visible:
            return None
        for i,ch in enumerate(visible):
            txt = ch.get("text","(無)")
            if i==sel:
                pygame.draw.rect(panel, (60,60,90), pygame.Rect(12, y-4, panel.get_width()-24, 26))
            img = font.render(txt, True, (235,235,235))
            panel.blit(img,(20,y)); y += 30
        screen.blit(panel, (int(WIDTH*0.15), int(HEIGHT*0.25)))
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return None
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_UP, pygame.K_w): sel = (sel-1) % len(visible)
                elif e.key in (pygame.K_DOWN, pygame.K_s): sel = (sel+1) % len(visible)
                elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    return visible[sel]
                elif e.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                    return None
        clk.tick(60)

def run_flow(screen, state: Dict[str,Any], flow_id: str) -> str:
    flow = load_flow(flow_id)
    key = flow.get("start")
    visited = 0
    while key:
        node = flow["nodes"].get(key, {})
        did = node.get("dialogue")
        if did:
            try:
                run_dialogue(screen, did, state=state)
            except Exception:
                run_lines(screen, [{"speaker":"系統","text":f"(缺少對話 {did})"}], state=state)
        for eff in node.get("effects", []):
            _effects_apply(state, eff)
        if node.get("move_to"):
            state["current"] = node["move_to"]
            return key
        if node.get("choices"):
            sel = _choice_menu(screen, node["choices"], state)
            if sel is None:
                break
            for eff in sel.get("effects", []):
                _effects_apply(state, eff)
            key = sel.get("next")
            visited += 1
            continue
        key = node.get("next")
        visited += 1
        if visited > 999:
            break
    push_note(state, f"劇情完成：{flow.get('title',flow_id)}")
    return "END"

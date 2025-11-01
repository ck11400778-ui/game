from __future__ import annotations
import json, pygame
from typing import Dict, Any

try:
    from core.ui import draw_text
except Exception:
    def draw_text(surface, txt, pos, color=(240,240,240), small=False):
        font = pygame.font.SysFont(None, 20 if small else 24)
        surface.blit(font.render(str(txt), True, color), pos)

try:
    from core.config import COLOR, WIDTH, HEIGHT
except Exception:
    COLOR = {"text":(240,240,240), "panel":(32,32,36), "hint":(200,200,120)}
    WIDTH, HEIGHT = 960, 540
try:
    from core.config import DIALOGUE_BOX_HEIGHT, DIALOGUE_PORTRAIT_SIZE
except Exception:
    DIALOGUE_BOX_HEIGHT = 160
    DIALOGUE_PORTRAIT_SIZE = (96,96)

from core.resource import proj_path
from core.skins import resolve_portrait_path
DIALOGUE_FOLDER = proj_path("data","dialogues")

_PORTRAIT_MAP_CACHE = None
def _load_portrait_map():
    global _PORTRAIT_MAP_CACHE
    if _PORTRAIT_MAP_CACHE is not None:
        return _PORTRAIT_MAP_CACHE
    p = proj_path("data","portraits_map.json")
    if p.exists():
        try:
            _PORTRAIT_MAP_CACHE = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            _PORTRAIT_MAP_CACHE = {}
    else:
        _PORTRAIT_MAP_CACHE = {}
    return _PORTRAIT_MAP_CACHE

def _resolve_portrait_name(speaker: str, portrait: str|None) -> str|None:
    if portrait and str(portrait).strip():
        return str(portrait).strip()
    m = _load_portrait_map()
    if speaker and speaker in m:
        return m[speaker]
    return speaker if speaker else None

def _load_portrait_surface(state: Dict[str, Any], speaker: str, portrait: str|None) -> pygame.Surface:
    size = DIALOGUE_PORTRAIT_SIZE
    resolved = _resolve_portrait_name(speaker, portrait)
    surf = None
    if resolved:
        path = resolve_portrait_path(state or {}, resolved)
        if path.exists():
            try:
                img = pygame.image.load(str(path)).convert_alpha()
                surf = pygame.transform.smoothscale(img, size)
            except Exception:
                surf = None
    if surf is None:
        surf = pygame.Surface(size, pygame.SRCALPHA)
        col = COLOR.get("hint",(200,200,120)) if speaker else (180,180,180)
        pygame.draw.circle(surf, col, (size[0]//2, size[1]//2), min(size)//2)
        pygame.draw.circle(surf, (0,0,0), (size[0]//2, size[1]//2), min(size)//2, 2)
        try:
            ch = (speaker or "NPC")[:1]
            font = pygame.font.SysFont(None, 28)
            img = font.render(ch, True, (30,30,30))
            rect = img.get_rect(center=(size[0]//2, size[1]//2))
            surf.blit(img, rect)
        except Exception:
            pass
    return surf

def _load_dialogue_json(dialogue_id: str) -> Dict[str, Any]:
    path = (DIALOGUE_FOLDER / f"{dialogue_id}.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    lines = data.get("lines", [])
    norm = []
    for ln in lines:
        if isinstance(ln, str):
            norm.append({"speaker":"", "text":ln})
        else:
            norm.append({"speaker":ln.get("speaker",""), "text":ln.get("text",""), "portrait":ln.get("portrait"), "side":ln.get("side","left")})
    return {"id": data.get("id", dialogue_id), "lines": norm}

def run_dialogue(screen: pygame.Surface, dialogue_id: str, *, state: Dict[str, Any]=None, box_height:int=None, margin:int=24) -> None:
    data = _load_dialogue_json(dialogue_id)
    lines = data["lines"]
    clock = pygame.time.Clock()
    if box_height is None: box_height = DIALOGUE_BOX_HEIGHT
    idx = 0; running = True
    box_rect = pygame.Rect(0, HEIGHT - box_height, WIDTH, box_height)
    name_color = COLOR.get("hint",(200,200,120))
    text_color = COLOR.get("text",(240,240,240))
    panel_color = COLOR.get("panel",(32,32,36))
    border_color = (0,0,0)

    while running:
        pygame.draw.rect(screen, panel_color, box_rect)
        pygame.draw.rect(screen, border_color, box_rect, 2)
        if 0 <= idx < len(lines):
            rec = lines[idx]
            speaker = rec.get("speaker",""); text = rec.get("text","")
            portrait_key = rec.get("portrait"); side = rec.get("side","left").lower()
            portrait = _load_portrait_surface(state or {}, speaker, portrait_key)
            px, py = (box_rect.x + margin, box_rect.y + margin)
            if side == "right":
                px = box_rect.right - margin - portrait.get_width()
            screen.blit(portrait, (px, py))
            text_x = box_rect.x + margin
            if side == "left":
                text_x += portrait.get_width() + 16
            name_y = box_rect.y + margin
            text_y = name_y + 28 if speaker else name_y
            if speaker: draw_text(screen, f"{speaker}", (text_x, name_y), color=name_color)
            draw_text(screen, text, (text_x, text_y), color=text_color)

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False; break
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER):
                    idx += 1
                    if idx >= len(lines): running = False; break
                elif event.key == pygame.K_ESCAPE:
                    running = False; break
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                idx += 1
                if idx >= len(lines): running = False; break
        clock.tick(60)

def run_lines(screen: pygame.Surface, lines: list, *, state: Dict[str, Any]=None, box_height:int=None, margin:int=24) -> None:
    data = {"id":"inline","lines":[]}
    for ln in lines:
        if isinstance(ln, str):
            data["lines"].append({"speaker":"", "text":ln})
        elif isinstance(ln, dict):
            data["lines"].append({"speaker":ln.get("speaker",""), "text":ln.get("text",""), "portrait":ln.get("portrait"), "side":ln.get("side","left")})
    path = proj_path("data","dialogues","_inline_temp.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    run_dialogue(screen, "_inline_temp", state=state, box_height=box_height, margin=margin)

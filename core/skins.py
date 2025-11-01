from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Any

try:
    from core.resource import proj_path
except Exception:
    proj_path = lambda *parts: Path(__file__).resolve().parents[1].joinpath(*parts)

SKINS_DIR = proj_path("assets","skins")

def list_skins() -> List[str]:
    if not SKINS_DIR.exists():
        return ["default"]
    names = ["default"]
    for p in SKINS_DIR.iterdir():
        if p.is_dir():
            names.append(p.name)
    return sorted(set(names))

def get_current_skin(state: Dict[str, Any]) -> str:
    return state.get("skin","default")

def set_skin(state: Dict[str, Any], name: str) -> None:
    if name not in list_skins():
        name = "default"
    state["skin"] = name

def resolve_portrait_path(state: Dict[str, Any], filename: str) -> Path:
    base = filename if filename.lower().endswith(".png") else filename + ".png"
    skin = get_current_skin(state)
    if skin and skin != "default":
        cand = SKINS_DIR / skin / "portraits" / base
        if cand.exists():
            return cand
    return proj_path("assets","portraits", base)

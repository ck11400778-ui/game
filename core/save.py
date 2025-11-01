# project/core/save.py  (overlay aware)
from __future__ import annotations
import json, time
from copy import deepcopy
from pathlib import Path
from typing import Dict, Any, Optional, List
try:
    from core.resource import proj_path, ensure_dir
except Exception:
    from pathlib import Path
    def proj_path(*parts): return Path(__file__).resolve().parents[1].joinpath(*parts)
    def ensure_dir(p: Path): p.mkdir(parents=True, exist_ok=True)

try:
    from core.models import Personality
except Exception:
    Personality = None  # type: ignore

SAVE_DIR = proj_path("data", "save")

def _slot_path(slot:int=0) -> Path:
    return SAVE_DIR / f"slot{slot}.json"

def _personality_to_dict(p) -> Dict[str, Any]:
    return {
        "name": getattr(p, "name", ""),
        "max_hp": getattr(p, "max_hp", 0),
        "hp": getattr(p, "hp", 0),
        "base_atk": getattr(p, "base_atk", 0),
        "atk_bonus": getattr(p, "atk_bonus", 0),
        "alive": getattr(p, "alive", True),
        "sacrificed_times": getattr(p, "sacrificed_times", 0),
    }

def _personality_from_dict(d: Dict[str, Any]):
    if Personality is None:
        return d
    p = Personality(d.get("name",""), d.get("max_hp",0), d.get("base_atk",0))
    p.hp = d.get("hp", p.max_hp)
    p.atk_bonus = d.get("atk_bonus", 0)
    p.alive = d.get("alive", True)
    p.sacrificed_times = d.get("sacrificed_times", 0)
    return p

def _sanitize_for_save(state: Dict[str, Any]) -> Dict[str, Any]:
    s = {}
    for k, v in state.items():
        if k in ("assets", "scenes"):
            continue
        s[k] = v
    if isinstance(s.get("personalities"), list):
        new_list: List[Any] = []
        for item in s["personalities"]:
            if hasattr(item, "__dict__") or hasattr(item, "name"):
                new_list.append(_personality_to_dict(item))
            else:
                new_list.append(item)
        s["personalities"] = new_list
    return s

def _restore_after_load(state: Dict[str, Any]) -> Dict[str, Any]:
    if isinstance(state.get("personalities"), list):
        rebuilt = []
        for item in state["personalities"]:
            if isinstance(item, dict):
                rebuilt.append(_personality_from_dict(item))
            else:
                rebuilt.append(item)
        state["personalities"] = rebuilt
    return state

def save_state(state: Dict[str, Any], slot:int=0) -> Path:
    ensure_dir(SAVE_DIR)
    # 記錄 UI 提示時間
    state.setdefault("ui", {})["last_saved_at"] = time.time()
    payload = _sanitize_for_save(state)
    p = _slot_path(slot)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return p

def load_state(slot:int=0) -> Optional[Dict[str, Any]]:
    p = _slot_path(slot)
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return _restore_after_load(data)
    except Exception:
        return None

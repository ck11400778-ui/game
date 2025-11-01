from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional
import json

# 路徑相容：優先使用 core.resource.proj_path，沒有就用相對路徑
try:
    from core.resource import proj_path
except Exception:
    from pathlib import Path as _P
    def proj_path(*p): 
        return _P(".".join([])).absolute().parent.joinpath(*p) if p else _P(".")

# 可選：提示面板
try:
    from core.overlay_hook import push_note
except Exception:
    def push_note(state, text, ttl=1.2): 
        print("[NOTE]", text)

# 對話播放（若專案沒有，退化為簡訊）
try:
    from core.dialogue import run_dialogue, run_lines
except Exception:
    def run_lines(screen, lines, **kw):
        # 簡單備援：在 console 印出
        print("\n".join([(ln.get("speaker","")+"：" if ln.get("speaker") else "") + ln.get("text","") for ln in lines]))
    def run_dialogue(screen, dialogue_id: str, **kw):
        run_lines(screen, [{"speaker":"系統","text":f"(對話 {dialogue_id} 缺失，占位顯示)"}])

NPCS_PATH = proj_path("data","npcs.json")

@dataclass
class NPC:
    id: str
    name: str
    title: str = ""
    area: str = ""
    traits: str = ""
    dialogue_id: Optional[str] = None
    effects: Optional[List[Dict[str, Any]]] = None

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "NPC":
        return NPC(
            id=d.get("id",""),
            name=d.get("name",""),
            title=d.get("title",""),
            area=d.get("area",""),
            traits=d.get("traits",""),
            dialogue_id=d.get("dialogue_id"),
            effects=d.get("effects") or []
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    # 播放首段對話（或指定ID），然後套用效果
    def talk(self, screen, state: Dict, dialogue_id: Optional[str] = None):
        did = dialogue_id or self.dialogue_id or f"npc_{self.id}_intro"
        try:
            run_dialogue(screen, did, state=state)
        except Exception:
            run_lines(screen, [{"speaker":"系統","text":f"(缺少對話 {did}，顯示占位)"}], state=state)
        _apply_effects(state, self.effects or [])

def _apply_effects(state: Dict, effects: List[Dict[str, Any]]):
    # 屬性加成：支援 {'affinity': {'水':1, '火':-1}}；旗標：{'flag': {'key': True}}
    try:
        from core.affinity import ensure as ensure_affinity, add as add_affinity
        ensure_affinity(state)
    except Exception:
        def add_affinity(_s,_k,_d): pass
    for eff in effects or []:
        if "affinity" in eff:
            changes = eff["affinity"] or {}
            for k, d in changes.items():
                try:
                    add_affinity(state, k, int(d))
                except Exception:
                    pass
            txt = "、".join([f"{k}+{v}" if int(v)>0 else f"{k}{v}" for k,v in changes.items()])
            if txt:
                push_note(state, f"屬性變化：{txt}")
        if "flag" in eff:
            flags = state.setdefault("flags", {})
            for fk, val in (eff["flag"] or {}).items():
                flags[fk] = bool(val)

def _load_json(path) -> List[Dict[str, Any]]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if isinstance(data, list): 
            return data
        if isinstance(data, dict) and "npcs" in data:
            return data["npcs"]
        return []
    except Exception:
        return []

# ---- 公開 API（維持與舊版相容） ----

def load_npcs() -> List[NPC]:
    """載入 NPC 清單（dataclass 形式）。"""
    raw = _load_json(NPCS_PATH)
    return [NPC.from_dict(d) for d in raw]

def list_at(area: str) -> List[NPC]:
    """列出某地區的 NPC。"""
    return [n for n in load_npcs() if n.area == area]

def get_npc_by_id(npc_id: str) -> Optional[NPC]:
    for n in load_npcs():
        if n.id == npc_id:
            return n
    return None

def interact(screen, state: Dict, npc_id: str):
    """與 NPC 互動（播放對話 → 套用效果）。"""
    npc = get_npc_by_id(npc_id)
    if not npc:
        run_lines(screen, [{"speaker":"系統","text":f"(找不到 NPC: {npc_id})"}], state=state)
        return
    npc.talk(screen, state)

# 舊名相容（有些專案會 from core.npc import NPCS, get_npcs 之類的）
def get_npcs() -> List[NPC]:
    return load_npcs()

NPCS = None  # 不再使用全域緩存，保留名稱避免 ImportError

__all__ = ["NPC","load_npcs","list_at","get_npc_by_id","interact","get_npcs","NPCS"]

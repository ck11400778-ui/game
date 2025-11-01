from __future__ import annotations
from typing import Dict

# --- 標準鍵與對應（支援中文/英文） ---
KEYMAP = {
    "火":"fire","水":"water","土":"earth","木":"wood","金":"metal","風":"wind",
    "光":"light","暗":"dark","陰沉":"gloom","理性":"reason","幻想":"fantasy",
    "霧":"mist","混沌":"chaos",
    # 英文自身映射（保險）
    "fire":"fire","water":"water","earth":"earth","wood":"wood","metal":"metal","wind":"wind",
    "light":"light","dark":"dark","gloom":"gloom","reason":"reason","fantasy":"fantasy","mist":"mist","chaos":"chaos",
}

DEFAULT_KEYS = ["fire","water","earth","wood","metal","wind","light","dark",
                "gloom","reason","fantasy","mist","chaos"]

def normalize(key: str) -> str:
    return KEYMAP.get(key, key)

def ensure(state: Dict):
    """確保 state['affinity'] 存在並含所有鍵。"""
    aff = state.setdefault("affinity", {})
    for k in DEFAULT_KEYS:
        aff.setdefault(k, 0)
    return aff

# --- 新版 API ---
def add(state: Dict, key: str, delta: int):
    """增加某屬性值（支援中文鍵）。回傳最新值。"""
    aff = ensure(state)
    k = normalize(key)
    aff[k] = aff.get(k, 0) + int(delta)
    return aff[k]

def adds(state: Dict, changes: Dict[str, int]):
    """批次增加，例如 {'水':+1,'火':-1}"""
    for k, d in (changes or {}).items():
        add(state, k, d)

def get(state: Dict, key: str) -> int:
    """取得某屬性值（支援中文鍵）。"""
    aff = ensure(state)
    return int(aff.get(normalize(key), 0))

# --- 舊版相容 API（你的專案可能在用） ---
def get_value(state: Dict, key: str) -> int:
    """相容舊程式：等同於 get(state, key)。"""
    return get(state, key)

def set_value(state: Dict, key: str, value: int):
    """相容舊程式：直接設定某屬性值。"""
    aff = ensure(state)
    aff[normalize(key)] = int(value)

def incr(state: Dict, key: str, delta: int = 1) -> int:
    """相容別名：等同於 add(state, key, delta)。"""
    return add(state, key, delta)

# 也提供幾個常見別名，避免 ImportError
get_affinity = get
add_affinity = add
ensure_affinity = ensure

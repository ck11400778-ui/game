# project/core/emotions.py
from __future__ import annotations
from typing import Dict, Any

DEFAULT_KEYS = ["familiarity", "trust", "stress"]

def ensure_emotions(state: Dict[str, Any]) -> None:
    em = state.setdefault("emotions", {})
    for k in DEFAULT_KEYS:
        em.setdefault(k, 0)

def add_emotion(state: Dict[str, Any], key: str, delta: int|float) -> None:
    ensure_emotions(state)
    em = state["emotions"]
    em[key] = em.get(key, 0) + float(delta)

def get_emotion(state: Dict[str, Any], key: str) -> float:
    ensure_emotions(state)
    return float(state["emotions"].get(key, 0))

def summarize_emotions(state: Dict[str, Any]) -> str:
    ensure_emotions(state)
    em = state["emotions"]
    return " / ".join(f"{k}:{int(v)}" for k,v in em.items())

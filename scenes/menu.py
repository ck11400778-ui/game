# -*- coding: utf-8 -*-
# Compatibility: assets argument is optional.
from __future__ import annotations
import pygame

def build(assets=None, state=None):
    return {}

def loop(screen, state, assets=None):
    flags = state.setdefault("flags", {})
    if flags.get("cinematic_chain_complete") or flags.get("ch3_done"):
        state.setdefault("area","home_room")
        state["current"] = "roam"
        return
    state["current"] = "start"

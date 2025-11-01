# -*- coding: utf-8 -*-
# Legacy scene redirect stub.
# 任何進入舊場景（世界地圖/校園/心靈中樞/舊選單），一律改導向到新版流程。
from __future__ import annotations

def build(assets=None, state=None):
    return {}

def loop(screen, state, assets=None):
    flags = state.setdefault("flags", {})
    # 已跑完三章或有結束旗標 ⇒ 直接進自由探索
    if flags.get("cinematic_chain_complete") or flags.get("ch3_done"):
        state.setdefault("area", "home_room")
        state["current"] = "roam"
    else:
        # 未完成 ⇒ 回新版開場
        state["current"] = "start"

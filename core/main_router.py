# -*- coding: utf-8 -*-
# core/main_router.py  (boot guard + legacy redirect + illegal scene guard)
#
# 放進專案後，在 main.py 每次載入場景前呼叫 route_before_scene(state)。
# 作用：
#  1) 第一次啟動，一律進入 start 選單（避免直接掉到任意場景）。
#  2) 任何舊場景 world_map/campus/mind_hub/menu_text/legacy_menu/story_sence/menu
#     會被導回新版流程（已跑完三章→roam；未跑完→start）。
#  3) 非法直跳觸火教學（touch_fire_trial）時，若沒準備旗標則改回 start，避免一開機進灰底教學。

LEGACY = {"world_map","campus","mind_hub","menu_text","legacy_menu","story_sence","menu"}
ALLOWED = {"start","roam","touch_fire_trial","home_return"}

def route_before_scene(state):
    flags = state.setdefault("flags", {})
    cur = state.get("current")

    # 1) Boot guard：第一次必進 start
    if not flags.get("_boot_forced_once"):
        flags["_boot_forced_once"] = True
        state["current"] = "start"
        return state["current"]

    # 2) 若沒有 current，預設 start
    if not cur:
        state["current"] = "start"
        return state["current"]

    # 3) 直接跳進教學小關卡的保護：需要前置旗標
    if cur == "touch_fire_trial" and not flags.get("ch2_borrow_fire_trial_ready"):
        state["current"] = "start"
        return state["current"]

    # 4) 舊場景一律改導
    if cur in LEGACY:
        if flags.get("cinematic_chain_complete") or flags.get("ch3_done"):
            state.setdefault("area","home_room")
            state["current"] = "roam"
        else:
            state["current"] = "start"
        return state["current"]

    # 5) 其他情況：保持現狀
    return state["current"]

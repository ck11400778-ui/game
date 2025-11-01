from __future__ import annotations
from typing import Dict, List, Tuple

Graph = Dict[str, List[str]]

NODES: Graph = {}

def _link(a: str, b: str):
    NODES.setdefault(a, [])
    NODES.setdefault(b, [])
    if b not in NODES[a]: NODES[a].append(b)
    if a not in NODES[b]: NODES[b].append(a)

def register_default():
    # 家與校門
    _link("home_room","home_street")
    _link("home_street","gate")
    _link("gate","avenue")

    # 校園主幹
    _link("avenue","corridor")
    _link("avenue","playground")
    _link("avenue","library")
    _link("avenue","admin_building")
    _link("avenue","club_building")
    _link("avenue","canteen")
    _link("avenue","garden")
    _link("avenue","dorm")
    _link("avenue","convenience_store")
    _link("avenue","gym")
    _link("avenue","auditorium")

    # 建築內部
    _link("corridor","classroom_veranda")
    _link("corridor","infirmary")

    _link("club_building","music_club")
    _link("club_building","photo_club")
    _link("club_building","drama_club")

    _link("canteen","canteen_back")

    _link("admin_building","lab")
    _link("admin_building","computer_room")
    _link("lab","computer_room")

def neighbors(area: str) -> List[str]:
    return NODES.get(area, [])

def has(area: str) -> bool:
    return area in NODES

# 自動註冊一次
register_default()

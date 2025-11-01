from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Iterable

BOARD_W = 6
BOARD_H = 6

TEAM_PLAYER = "player"
TEAM_ENEMY  = "enemy"

@dataclass
class Unit:
    id: int
    name: str
    team: str
    hp: int
    atk: int
    x: int
    y: int
    acted: bool = False

class Grid:
    def __init__(self):
        self.w = BOARD_W
        self.h = BOARD_H
        self.cells: List[List[Optional[int]]] = [[None for _ in range(self.w)] for _ in range(self.h)]
        self.units: Dict[int, Unit] = {}
        self.next_uid = 1

    def in_bounds(self, x:int, y:int) -> bool:
        return 0 <= x < self.w and 0 <= y < self.h

    def unit_at(self, x:int, y:int) -> Optional[Unit]:
        if not self.in_bounds(x, y): return None
        uid = self.cells[y][x]
        return self.units.get(uid) if uid is not None else None

    def add_unit(self, name:str, team:str, hp:int, atk:int, x:int, y:int) -> int:
        assert self.in_bounds(x,y) and self.cells[y][x] is None
        uid = self.next_uid; self.next_uid += 1
        u = Unit(uid, name, team, hp, atk, x, y)
        self.units[uid] = u
        self.cells[y][x] = uid
        return uid

    def move_unit(self, uid:int, dx:int, dy:int) -> bool:
        u = self.units[uid]
        nx, ny = u.x + dx, u.y + dy
        if not self.in_bounds(nx, ny): return False
        if self.cells[ny][nx] is not None: return False
        self.cells[u.y][u.x] = None
        u.x, u.y = nx, ny
        self.cells[ny][nx] = uid
        return True

    def push_unit(self, uid:int, dx:int, dy:int, steps:int=1) -> int:
        moved = 0
        for _ in range(steps):
            u = self.units.get(uid)
            if not u: break
            nx, ny = u.x + dx, u.y + dy
            if not self.in_bounds(nx, ny): break
            if self.cells[ny][nx] is not None: break
            self.cells[u.y][u.x] = None
            u.x, u.y = nx, ny
            self.cells[ny][nx] = uid
            moved += 1
        return moved

    def damage_unit(self, uid:int, dmg:int):
        u = self.units.get(uid)
        if not u: return
        u.hp -= max(0, dmg)
        if u.hp <= 0:
            self.cells[u.y][u.x] = None
            del self.units[uid]

    def all_units(self) -> Iterable[Unit]:
        return list(self.units.values())

    def team_units(self, team:str) -> List[Unit]:
        return [u for u in self.units.values() if u.team == team]

    def reset_round(self):
        for u in self.units.values():
            u.acted = False

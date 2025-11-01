from typing import List, Tuple

SKILLS = {
    "slash": {
        "damage": 10,
        "range_offsets": [(1, 0)],
        "knockback": (1, 0),
    },
    "pierce": {
        "damage": 7,
        "range_offsets": [(1, 0), (2, 0)],
        "knockback": (0, 0),
    },
    "shockwave": {
        "damage": 6,
        "range_offsets": [(1, -1), (1, 0), (1, 1)],
        "knockback": (1, 0),
    },
    "blast": {
        "damage": 8,
        "range_offsets": [(1,0),(1,1),(2,0),(2,1)],
        "knockback": (0, 0),
    },
}

def forwardize(facing:int, offs:Tuple[int,int])->Tuple[int,int]:
    ox, oy = offs
    return (ox * facing, oy)

def affected_cells(board, attacker, skill_name)->List[Tuple[int,int]]:
    s = SKILLS[skill_name]
    cells = []
    for offs in s["range_offsets"]:
        dx, dy = forwardize(attacker.facing, offs)
        x = attacker.x + dx
        y = attacker.y + dy
        if board.in_bounds(x, y):
            cells.append((x, y))
    return cells

def cast_skill(board, attacker, skill_name):
    s = SKILLS[skill_name]
    dmg = s["damage"]
    kdx, kdy = forwardize(attacker.facing, s["knockback"])

    hit_any = False
    for (x, y) in affected_cells(board, attacker, skill_name):
        unit = board.get_unit(x, y)
        if unit and unit.team != attacker.team and unit.alive:
            unit.take_damage(dmg + attacker.atk)
            if kdx or kdy:
                unit.knockback(board, kdx, kdy)
            hit_any = True

    attacker.acted_this_turn = True
    return hit_any

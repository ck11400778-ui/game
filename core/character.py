from dataclasses import dataclass, field

@dataclass
class Character:
    name: str
    team: str                 # "ally" or "enemy"
    x: int
    y: int
    hp: int = 30
    atk: int = 8
    defense: int = 2
    speed: int = 1
    facing: int = 1          # ally: +1, enemy: -1
    skills: list = field(default_factory=lambda: ["slash"])
    moved_this_turn: bool = False
    acted_this_turn: bool = False
    alive: bool = True

    def reset_turn(self):
        self.moved_this_turn = False
        self.acted_this_turn = False

    def try_move(self, board, dx: int, dy: int) -> bool:
        if self.moved_this_turn or not self.alive:
            return False
        if abs(dx) + abs(dy) != 1:
            return False
        tx, ty = self.x + dx, self.y + dy
        if board.in_bounds(tx, ty) and not board.get_unit(tx, ty):
            board.move_unit(self, tx, ty)
            self.moved_this_turn = True
            return True
        return False

    def take_damage(self, amount: int):
        if not self.alive:
            return
        real = max(0, amount - self.defense)
        self.hp -= real
        if self.hp <= 0:
            self.alive = False

    def knockback(self, board, kdx: int, kdy: int):
        if not self.alive:
            return
        tx, ty = self.x + kdx, self.y + kdy
        if not board.in_bounds(tx, ty):  # hit wall
            return
        if board.get_unit(tx, ty):       # blocked by unit
            return
        board.move_unit(self, tx, ty)

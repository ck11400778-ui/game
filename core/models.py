class Personality:
    def __init__(self, name, hp, atk):
        self.name = name; self.max_hp = hp; self.hp = hp
        self.base_atk = atk; self.atk_bonus = 0
        self.alive = True
        self.sacrificed_times = 0
    @property
    def atk(self): return max(0, self.base_atk + self.atk_bonus)
    def take(self, dmg):
        self.hp -= max(0, int(dmg))
        if self.hp <= 0: self.hp = 0; self.alive = False
    def heal(self, n): self.hp = min(self.max_hp, self.hp + int(n))

def build_initial_state(assets):
    return {
        "current":"menu",
        "assets": assets,
        "personalities":[
            Personality("勇氣", 60, 12),
            Personality("冷靜", 48, 9),
            Personality("衝動", 42, 15),
        ],
        "scenes": {}
    }

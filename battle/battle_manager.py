import pygame
from dataclasses import dataclass
from core.character import Character
from core.skills import SKILLS, affected_cells, cast_skill

BATTLE_CELL = 56
GRID_W = 6
GRID_H = 6

class Board:
    def __init__(self, ox: int, oy: int):
        self.ox = ox
        self.oy = oy
        self.units = {}

    def in_bounds(self, x, y):
        return 0 <= x < GRID_W and 0 <= y < GRID_H

    def get_unit(self, x, y):
        return self.units.get((x, y))

    def add_unit(self, unit: Character):
        self.units[(unit.x, unit.y)] = unit

    def move_unit(self, unit: Character, tx:int, ty:int):
        if (unit.x, unit.y) in self.units:
            del self.units[(unit.x, unit.y)]
        unit.x, unit.y = tx, ty
        self.units[(tx, ty)] = unit

    def remove_dead(self):
        for pos, u in list(self.units.items()):
            if not u.alive:
                del self.units[pos]

    def to_screen(self, gx, gy):
        return self.ox + gx * BATTLE_CELL, self.oy + gy * BATTLE_CELL

    def from_screen(self, px, py):
        gx = (px - self.ox) // BATTLE_CELL
        gy = (py - self.oy) // BATTLE_CELL
        return int(gx), int(gy)

    def draw_grid(self, surf, color=(70, 90, 120)):
        for x in range(GRID_W):
            for y in range(GRID_H):
                rx, ry = self.to_screen(x, y)
                pygame.draw.rect(surf, color, (rx, ry, BATTLE_CELL, BATTLE_CELL), 1)

@dataclass
class TurnState:
    team: str = "ally"
    index: int = 0

class BattleManager:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        w, h = screen.get_size()
        gap = 48
        self.ally_board  = Board(ox = w//2 - gap - GRID_W*BATTLE_CELL, oy = 60)
        self.enemy_board = Board(ox = w//2 + gap,                       oy = 60)

        self.cursor_board = "ally"
        self.cursor = [0, 0]

        self.allies = [
            Character("Hero", "ally", 0, 2, skills=["slash","shockwave"], facing=+1),
            Character("Mage", "ally", 1, 3, skills=["blast","pierce"], facing=+1),
        ]
        self.enemies = [
            Character("Gob", "enemy", 5, 2, skills=["slash"], facing=-1),
            Character("Orc", "enemy", 4, 3, skills=["pierce"], facing=-1),
        ]
        for u in self.allies:  self.ally_board.add_unit(u)
        for u in self.enemies: self.enemy_board.add_unit(u)

        self.turn = TurnState(team="ally", index=0)
        self.selected_skill = "slash"

    def current_team_list(self):
        return self.allies if self.turn.team == "ally" else self.enemies

    def current_board(self):
        return self.ally_board if self.turn.team == "ally" else self.enemy_board

    def enemy_board_of(self, unit):
        return self.enemy_board if unit.team == "ally" else self.ally_board

    def current_unit(self):
        team = self.current_team_list()
        while self.turn.index < len(team) and not team[self.turn.index].alive:
            self.turn.index += 1
        if self.turn.index >= len(team):
            return None
        return team[self.turn.index]

    def end_turn_if_done(self):
        u = self.current_unit()
        if not u: return self.next_turn()
        if u.moved_this_turn and u.acted_this_turn:
            self.next_turn()

    def next_turn(self):
        team = self.current_team_list()
        self.turn.index += 1
        if self.turn.index >= len(team):
            self.turn.team = "enemy" if self.turn.team == "ally" else "ally"
            self.turn.index = 0
            for u in self.current_team_list():
                if u.alive:
                    u.reset_turn()

    def move_cursor(self, dx, dy):
        board = self.ally_board if self.cursor_board == "ally" else self.enemy_board
        cx, cy = self.cursor
        nx, ny = max(0, min(GRID_W-1, cx+dx)), max(0, min(GRID_H-1, cy+dy))
        self.cursor = [nx, ny]

    def click_board(self, mouse_pos, button):
        board = self.ally_board if self.cursor_board == "ally" else self.enemy_board
        gx, gy = board.from_screen(*mouse_pos)
        if not board.in_bounds(gx, gy): return
        self.cursor = [gx, gy]
        u = self.current_unit()
        if not u: return
        my_board = self.current_board()

        if button == 1:
            dx = gx - u.x; dy = gy - u.y
            if abs(dx) + abs(dy) == 1:
                u.try_move(my_board, dx, dy)
        elif button == 3:
            enemy_board = self.enemy_board_of(u)
            cast_skill(enemy_board, u, self.selected_skill)
        self.end_turn_if_done()

    def key_action(self, key):
        u = self.current_unit()
        if not u: return
        my_board = self.current_board()
        enemy_board = self.enemy_board_of(u)

        if key == pygame.K_SPACE:
            cx, cy = self.cursor
            dx = cx - u.x; dy = cy - u.y
            if abs(dx) + abs(dy) == 1:
                u.try_move(my_board, dx, dy)

        if pygame.K_1 <= key <= pygame.K_9:
            i = key - pygame.K_1
            if i < len(u.skills):
                self.selected_skill = u.skills[i]

        if key == pygame.K_RETURN:
            if cast_skill(enemy_board, u, self.selected_skill):
                self.end_turn_if_done()

    def draw(self):
        surf = self.screen
        surf.fill((18, 22, 28))
        self.ally_board.draw_grid(surf, color=(60, 100, 140))
        self.enemy_board.draw_grid(surf, color=(140, 80, 80))

        u = self.current_unit()
        if u:
            eboard = self.enemy_board_of(u)
            for (gx, gy) in affected_cells(eboard, u, self.selected_skill):
                rx, ry = eboard.to_screen(gx, gy)
                pygame.draw.rect(surf, (255, 230, 120), (rx, ry, BATTLE_CELL, BATTLE_CELL), 0)

        def draw_unit(board, unit, color):
            rx, ry = board.to_screen(unit.x, unit.y)
            rect = pygame.Rect(rx+4, ry+4, BATTLE_CELL-8, BATTLE_CELL-8)
            pygame.draw.rect(surf, color, rect, 0)
            maxw = BATTLE_CELL-8
            ratio = max(0, unit.hp)/30
            pygame.draw.rect(surf, (40,40,40), (rx+4, ry+2, maxw, 4))
            pygame.draw.rect(surf, (80,220,80), (rx+4, ry+2, int(maxw*ratio), 4))

        for uu in self.allies:
            if uu.alive: draw_unit(self.ally_board, uu, (70, 160, 255))
        for uu in self.enemies:
            if uu.alive: draw_unit(self.enemy_board, uu, (255, 120, 120))

        board = self.ally_board if self.cursor_board == "ally" else self.enemy_board
        rx, ry = board.to_screen(*self.cursor)
        pygame.draw.rect(surf, (255,255,255), (rx, ry, BATTLE_CELL, BATTLE_CELL), 2)

        font = pygame.font.SysFont(None, 20)
        u = self.current_unit()
        tip = f"[{self.turn.team}] {u.name if u else ''} HP:{u.hp if u else ''} Skill:{self.selected_skill}  (←→↑↓/空白/Enter/1~9，Tab換盤)"
        surf.blit(font.render(tip, True, (230,230,230)), (16, 16))

    def update(self, dt):
        self.ally_board.remove_dead()
        self.enemy_board.remove_dead()

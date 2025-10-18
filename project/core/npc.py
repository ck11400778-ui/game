import pygame
from core.ui import draw_text
from core.config import COLOR, TILE

class NPC:
    def __init__(self, name, x, y, color, lines):
        self.name = name
        self.rect = pygame.Rect(x*TILE, y*TILE, TILE, TILE)
        self.color = color
        self.lines = list(lines) if lines else []
        self._talking = False
        self._idx = 0

    def start_or_advance(self):
        if not self.lines:
            self._talking = False
            self._idx = 0
            return
        if not self._talking:
            self._talking = True
            self._idx = 0
        else:
            self._idx += 1
            if self._idx >= len(self.lines):
                # 結束對話
                self._talking = False
                self._idx = 0

    def is_talking(self):
        return self._talking

    def draw(self, screen, cam):
        pygame.draw.rect(screen, self.color,
                         (self.rect.x - cam.x, self.rect.y - cam.y, self.rect.w, self.rect.h))

    def draw_dialog(self, screen):
        if not self._talking: return
        # 簡單對話框
        pygame.draw.rect(screen, (0,0,0), (20, 20, 640, 90))
        pygame.draw.rect(screen, (255,255,255), (20, 20, 640, 90), 2)
        draw_text(screen, f"{self.name}：{self.lines[self._idx]}", (30, 30), COLOR["text"])
        draw_text(screen, "(Enter 繼續，最後一句後自動結束)", (30, 70), (200,200,200))

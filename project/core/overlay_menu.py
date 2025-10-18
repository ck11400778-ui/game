import pygame
from core.config import WIDTH, HEIGHT, COLOR
from core.ui import draw_text

class OverlayMenu:
    def __init__(self):
        self.active = False
    def toggle(self): self.active = not self.active
    def handle_events(self, events, state):
        for e in events:
            if e.type == pygame.KEYDOWN and e.key in (pygame.K_TAB, pygame.K_ESCAPE):
                self.toggle()
    def draw(self, screen, state):
        if not self.active: return
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((0,0,0,160))
        screen.blit(s,(0,0))
        draw_text(screen, "選單（示意）TAB 關閉", (40,40), (255,230,120))

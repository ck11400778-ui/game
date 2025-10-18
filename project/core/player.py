import pygame
from core.config import TILE

class Player:
    def __init__(self, x, y, img, speed=3):
        self.rect = pygame.Rect(x, y, 42, 56)
        self.speed = speed
        self.img = img

    def _collide_tile(self, tilemap, pad=2):
        for px, py in [
            (self.rect.left + pad,  self.rect.top + pad),
            (self.rect.right-1 - pad, self.rect.top + pad),
            (self.rect.left + pad,  self.rect.bottom-1 - pad),
            (self.rect.right-1 - pad, self.rect.bottom-1 - pad)
        ]:
            tx, ty = px // TILE, py // TILE
            if tilemap.is_blocked(tx, ty):
                return True
        return False

    def move_tilemap(self, dx, dy, tilemap):
        if dx != 0:
            self.rect.x += dx * self.speed
            if self._collide_tile(tilemap):
                if dx > 0:
                    tx = (self.rect.right-1) // TILE
                    self.rect.right = tx * TILE - 1
                else:
                    tx = (self.rect.left) // TILE
                    self.rect.left = (tx + 1) * TILE
        if dy != 0:
            self.rect.y += dy * self.speed
            if self._collide_tile(tilemap):
                if dy > 0:
                    ty = (self.rect.bottom-1) // TILE
                    self.rect.bottom = ty * TILE - 1
                else:
                    ty = (self.rect.top) // TILE
                    self.rect.top = (ty + 1) * TILE

    def move_free(self, dx, dy, limit_w, limit_h):
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        self.rect.x = max(0, min(self.rect.x, limit_w - self.rect.w))
        self.rect.y = max(0, min(self.rect.y, limit_h - self.rect.h))

    def draw(self, surface, camera=None):
        x = self.rect.x if camera is None else self.rect.x - camera.x
        y = self.rect.y if camera is None else self.rect.y - camera.y
        surface.blit(self.img, (x, y))

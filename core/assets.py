import os, pygame
from core.resource import proj_path
from core.config import TILE, COLOR

ASSET_DIR = str(proj_path("assets","images"))

def _fallback(color, size):
    surf = pygame.Surface(size, pygame.SRCALPHA)
    surf.fill(color)
    pygame.draw.rect(surf, (0,0,0), surf.get_rect(), 1)
    return surf

def load_image(name, fallback_color, size=(TILE, TILE)):
    path = os.path.join(ASSET_DIR, name)
    if os.path.exists(path):
        try:
            img = pygame.image.load(path).convert_alpha()
            if size: img = pygame.transform.smoothscale(img, size)
            return img
        except Exception:
            pass
    return _fallback(fallback_color, size)

def load_assets():
    return {
        "player": load_image("player.png", COLOR["player"], (42,56)),
        "tile_grass": load_image("tile_grass.png", COLOR["grass"]),
        "tile_wall": load_image("tile_wall.png", COLOR["wall"]),
        "door_purple": load_image("door_purple.png", COLOR["door"]),
        "npc_teacher": load_image("npc_teacher.png", COLOR["teacher"]),
        "npc_peer": load_image("npc_peer.png", COLOR["peer"]),
        "enemy_negation": load_image("enemy_negation.png", COLOR["enemy"], (200,200)),
    }

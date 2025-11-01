import pygame
from core.config import WIDTH, HEIGHT, COLOR, TILE
from core.camera import Camera
from core.tilemap import TileMap
from core.player import Player
from core.ui import draw_text

def build(assets):
    cols, rows = 60, 40
    safe = [(1,1, cols-2, rows-2)]
    tilemap = TileMap(cols, rows, assets, seed=20250813, wall_ratio=0.03, safe_areas=safe)
    scene = {
        "name":"campus",
        "tilemap": tilemap,
        "camera": Camera(WIDTH, HEIGHT),
        "player": Player(3*TILE, 3*TILE, assets["player"]),
    }
    return scene

def loop(screen, state, assets):
    scene = state["scenes"]["campus"]
    tilemap, cam, player = scene["tilemap"], scene["camera"], scene["player"]

    pressed = pygame.key.get_pressed()
    dx = int(pressed[pygame.K_RIGHT] or pressed[pygame.K_d]) - int(pressed[pygame.K_LEFT] or pressed[pygame.K_a])
    dy = int(pressed[pygame.K_DOWN]  or pressed[pygame.K_s]) - int(pressed[pygame.K_UP]   or pressed[pygame.K_w])

    for e in pygame.event.get():
        if e.type == pygame.QUIT: raise SystemExit
        elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            state["current"]="menu"

    player.move_tilemap(dx, dy, tilemap)
    cam.follow(player.rect, tilemap.width, tilemap.height)

    screen.fill(COLOR["bg"])
    tilemap.draw(screen, cam)
    player.draw(screen, cam)
    draw_text(screen, "校園：WASD/方向鍵移動；ESC 回主選單", (16, 10), COLOR["hint"])

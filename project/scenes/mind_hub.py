import pygame
from core.config import COLOR, WIDTH, HEIGHT
from core.player import Player
from core.ui import draw_text

class Door:
    def __init__(self, x,y,img):
        self.rect = pygame.Rect(x,y, img.get_width(), img.get_height())
        self.img = img
    def draw(self, screen):
        screen.blit(self.img, (self.rect.x, self.rect.y))

def build(assets):
    return {
        "name":"mind_hub",
        "player": Player(140, 240, assets["player"]),
        "door": Door(760, 220, assets["door_purple"])  # Enter 進格鬥
    }

def loop(screen, state, assets):
    scene = state["scenes"]["mind_hub"]
    pressed = pygame.key.get_pressed()
    dx = int(pressed[pygame.K_RIGHT] or pressed[pygame.K_d]) - int(pressed[pygame.K_LEFT] or pressed[pygame.K_a])
    dy = int(pressed[pygame.K_DOWN]  or pressed[pygame.K_s]) - int(pressed[pygame.K_UP]   or pressed[pygame.K_w])

    for e in pygame.event.get():
        if e.type == pygame.QUIT: raise SystemExit
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                state["current"]="menu"
            elif e.key == pygame.K_RETURN and scene["player"].rect.colliderect(scene["door"].rect.inflate(24,24)):
                # 修復：移除不存在的 start_grid 調用
                try:
                    from scenes.battle_grid import build as build_battle_grid
                    if "battle_grid" not in state["scenes"]:
                        state["scenes"]["battle_grid"] = build_battle_grid(assets)
                    state["current"]="battle_grid"
                    print("成功進入戰鬥場景！")
                except Exception as ex:
                    print(f"進入戰鬥失敗: {ex}")

    scene["player"].move_free(dx, dy, WIDTH, HEIGHT)

    screen.fill((120,80,140))
    scene["door"].draw(screen)
    scene["player"].draw(screen)
    
    # 顯示提示訊息
    draw_text(screen, "心房：WASD/方向鍵移動；靠近門 Enter 進格鬥；ESC 回主選單", (16,10), COLOR["text"])
    
    # 當玩家靠近門時顯示額外提示
    if scene["player"].rect.colliderect(scene["door"].rect.inflate(24,24)):
        draw_text(screen, "按 Enter 進入戰鬥！", (scene["door"].rect.x - 30, scene["door"].rect.y - 30), (255, 255, 100))
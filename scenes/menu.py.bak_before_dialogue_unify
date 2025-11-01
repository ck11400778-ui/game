import pygame
from core.config import WIDTH, HEIGHT, COLOR
from core.ui import draw_text
from scenes.world_places import build_place

MENU_ITEMS = [
    ("回到校園", "campus"),
    ("劇情模式", "story"),
    ("教學樓",   "teaching"),
    ("操場",     "playground"),
    ("中庭花園", "garden"),
    ("圖書館",   "library"),
    ("便利商店", "convenience"),
    ("馬路旁街道", "street"),
    ("練武場",   "dojo"),
    ("活動中心", "activity"),
    ("魔法訓練室", "magic"),
    ("格鬥訓練室", "fight_training"),
    ("副本集散地", "hub"),
    ("心房（選單進入）", "mind_hub"),
]

def build(assets):
    return {"name":"menu", "index":0}

def loop(screen, state):
    scene = state["scenes"]["menu"]
    for e in pygame.event.get():
        if e.type == pygame.QUIT: raise SystemExit
        elif e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_UP, pygame.K_w):
                scene["index"] = (scene["index"] - 1) % len(MENU_ITEMS)
            elif e.key in (pygame.K_DOWN, pygame.K_s):
                scene["index"] = (scene["index"] + 1) % len(MENU_ITEMS)
            elif e.key == pygame.K_RETURN:
                _, key = MENU_ITEMS[scene["index"]]
                if key == "campus":
                    state["current"] = "campus"
                elif key == "mind_hub":
                    state["current"] = "mind_hub"
                elif key == "story":
                    state["current"] = "story"
                else:
                    if key not in state["scenes"]:
                        state["scenes"][key] = build_place(key, state["assets"])
                    state["current"] = key

    screen.fill((30,30,40))
    draw_text(screen, "主選單（Enter 進入，ESC 在場景內回到這裡）", (40, 40), (255,230,120))
    y = 100
    for i,(label,_) in enumerate(MENU_ITEMS):
        col = (255,255,255) if i!=scene["index"] else (255,230,120)
        draw_text(screen, label, (80, y), col)
        y += 28

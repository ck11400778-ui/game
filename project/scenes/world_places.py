import pygame
from core.config import WIDTH, HEIGHT, COLOR, TILE
from core.camera import Camera
from core.ui import draw_text
from core.npc import NPC

# === 場景資料 ===
# 注意：portals 與 npcs 一律是「list」，不要用 set。
PLACES = {
    "teaching": {
        "name": "教學樓",
        "bg": (180, 200, 220),
        "npcs": [
            ("導師", 6, 5, (255,220,120), ["今天上的是心靈防禦。", "記得去操場練習。"]),
        ],
        "portals": [
            {"to": "playground", "rect": (28*TILE, 4*TILE, 2*TILE, 2*TILE), "label": "到操場 →", "spawn": (3*TILE, 6*TILE)},
            {"to": "garden",     "rect": (2*TILE,  10*TILE, 2*TILE, 2*TILE), "label": "← 到中庭花園", "spawn": (20*TILE, 8*TILE)},
        ],
        "spawn": (4*TILE, 6*TILE),
    },
    "playground": {
        "name": "操場",
        "bg": (210, 190, 150),
        "npcs": [
            ("教練", 5, 8, (255,170,120), ["記得熱身。", "跑兩圈！"]),
        ],
        "portals": [
            {"to": "teaching", "rect": (2*TILE, 2*TILE, 2*TILE, 2*TILE), "label": "← 回教學樓", "spawn": (26*TILE, 4*TILE)},
            {"to": "garden",   "rect": (28*TILE, 10*TILE, 2*TILE, 2*TILE), "label": "到中庭花園 →", "spawn": (3*TILE, 10*TILE)},
        ],
        "spawn": (4*TILE, 8*TILE),
    },
    "garden": {
        "name": "中庭花園",
        "bg": (170, 220, 170),
        "npcs": [
            ("園丁", 12, 8, (120,200,120), ["花要耐心照顧。"]),
        ],
        "portals": [
            {"to": "library",   "rect": (26*TILE, 2*TILE, 2*TILE, 2*TILE), "label": "到圖書館 →", "spawn": (3*TILE, 4*TILE)},
            {"to": "playground","rect": (2*TILE, 10*TILE, 2*TILE, 2*TILE), "label": "← 回操場", "spawn": (26*TILE, 10*TILE)},
            {"to": "teaching",  "rect": (2*TILE, 4*TILE, 2*TILE, 2*TILE), "label": "← 回教學樓", "spawn": (26*TILE, 10*TILE)},
        ],
        "spawn": (12*TILE, 8*TILE),
    },
    "library": {
        "name": "圖書館",
        "bg": (200, 210, 230),
        "npcs": [
            ("學長", 8, 6, (180,180,255), ["書香能讓心沉靜。"]),
        ],
        "portals": [
            {"to": "garden", "rect": (2*TILE, 2*TILE, 2*TILE, 2*TILE), "label": "← 回中庭花園", "spawn": (24*TILE, 3*TILE)},
            {"to": "magic",  "rect": (28*TILE, 10*TILE, 2*TILE, 2*TILE), "label": "到魔法訓練室 →", "spawn": (3*TILE, 6*TILE)},
        ],
        "spawn": (6*TILE, 6*TILE),
    },
    "convenience": {
        "name": "便利商店",
        "bg": (240, 240, 200),
        "npcs": [
            ("店員", 10, 6, (255,200,200), ["今天有特價飯糰。"]),
        ],
        "portals": [
            {"to": "street", "rect": (28*TILE, 6*TILE, 2*TILE, 2*TILE), "label": "到馬路旁街道 →", "spawn": (3*TILE, 6*TILE)},
            {"to": "hub",    "rect": (2*TILE,  10*TILE, 2*TILE, 2*TILE), "label": "← 副本集散地", "spawn": (24*TILE, 8*TILE)},
        ],
        "spawn": (8*TILE, 6*TILE),
    },
    "street": {
        "name": "馬路旁街道",
        "bg": (200, 200, 200),
        "npcs": [
            ("路人", 7, 9, (200,200,200), ["今天風好大。"]),
        ],
        "portals": [
            {"to": "convenience", "rect": (2*TILE, 6*TILE, 2*TILE, 2*TILE), "label": "← 回便利商店", "spawn": (24*TILE, 6*TILE)},
        ],
        "spawn": (6*TILE, 10*TILE),
    },
    "dojo": {
        "name": "練武場",
        "bg": (210, 180, 150),
        "npcs": [
            ("師傅", 6, 6, (255,180,120), ["拳要沉、腳要穩。"]),
        ],
        "portals": [
            {"to": "activity", "rect": (28*TILE, 8*TILE, 2*TILE, 2*TILE), "label": "到活動中心 →", "spawn": (3*TILE, 8*TILE)},
        ],
        "spawn": (4*TILE, 8*TILE),
    },
    "activity": {
        "name": "活動中心",
        "bg": (220, 180, 220),
        "npcs": [
            ("社長", 10, 9, (220,160,220), ["今晚排練，不要遲到。"]),
        ],
        "portals": [
            {"to": "dojo",        "rect": (2*TILE, 8*TILE, 2*TILE, 2*TILE), "label": "← 回練武場", "spawn": (26*TILE, 8*TILE)},
            {"to": "fight_training","rect": (28*TILE, 12*TILE, 2*TILE, 2*TILE), "label": "到格鬥訓練室 →", "spawn": (3*TILE, 10*TILE)},
        ],
        "spawn": (6*TILE, 10*TILE),
    },
    "magic": {
        "name": "魔法訓練室",
        "bg": (180, 160, 220),
        "npcs": [
            ("見習法師", 12, 6, (200,160,255), ["魔力來自內心的秩序。"]),
        ],
        "portals": [
            {"to": "library", "rect": (2*TILE, 6*TILE, 2*TILE, 2*TILE), "label": "← 回圖書館", "spawn": (26*TILE, 6*TILE)},
        ],
        "spawn": (6*TILE, 6*TILE),
    },
    "fight_training": {
        "name": "格鬥訓練室",
        "bg": (160, 160, 160),
        "npcs": [
            ("訓練師", 8, 8, (200,200,200), ["想實戰？到心房練習看看。"]),
        ],
        "portals": [
            {"to": "activity", "rect": (2*TILE, 12*TILE, 2*TILE, 2*TILE), "label": "← 回活動中心", "spawn": (26*TILE, 10*TILE)},
        ],
        "spawn": (8*TILE, 8*TILE),
    },
    "hub": {
        "name": "副本集散地",
        "bg": (150, 150, 220),
        "npcs": [
            ("接待員", 10, 6, (160,160,255), ["挑個副本吧。"]),
        ],
        "portals": [
            {"to": "convenience", "rect": (28*TILE, 8*TILE, 2*TILE, 2*TILE), "label": "到便利商店 →", "spawn": (3*TILE, 8*TILE)},
            # 更多副本入口可在此追加
        ],
        "spawn": (10*TILE, 8*TILE),
    },
}

def build_place(key, assets):
    if key not in PLACES:
        # 若選單給了未知 key，建一個臨時空場
        PLACES[key] = {"name": key, "bg": (120,120,120), "npcs": [], "portals": [], "spawn": (4*TILE,6*TILE)}
    data = PLACES[key]
    cam = Camera(WIDTH, HEIGHT)
    # 建 NPC 物件
    npcs = [NPC(name, x, y, color, lines) for (name,x,y,color,lines) in data.get("npcs", [])]
    # 傳送門矩形
    portals = []
    for p in data.get("portals", []):
        rect = pygame.Rect(p["rect"])
        portals.append({"to": p["to"], "rect": rect, "label": p.get("label","傳送門"), "spawn": p.get("spawn",(2*TILE,2*TILE))})
    # 玩家出生點
    spawn = data.get("spawn", (4*TILE, 6*TILE))
    return {
        "key": key,
        "name": data["name"],
        "bg": data.get("bg",(180,180,180)),
        "camera": cam,
        "player": {"rect": pygame.Rect(spawn[0], spawn[1], 42, 56)},
        "npcs": npcs,
        "portals": portals,
    }

def loop_place(screen, state, assets):
    scene = state["scenes"][state["current"]]
    cam = scene["camera"]
    player_rect = scene["player"]["rect"]

    # 輸入
    pressed = pygame.key.get_pressed()
    dx = int(pressed[pygame.K_RIGHT] or pressed[pygame.K_d]) - int(pressed[pygame.K_LEFT] or pressed[pygame.K_a])
    dy = int(pressed[pygame.K_DOWN]  or pressed[pygame.K_s]) - int(pressed[pygame.K_UP]   or pressed[pygame.K_w])

    for e in pygame.event.get():
        if e.type == pygame.QUIT: raise SystemExit
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                state["current"] = "menu"
            elif e.key == pygame.K_RETURN:
                # 先看 NPC 對話
                for npc in scene["npcs"]:
                    if player_rect.colliderect(npc.rect.inflate(8,8)):
                        npc.start_or_advance()
                        break
                else:
                    # 再看傳送門
                    for p in scene["portals"]:
                        if player_rect.colliderect(p["rect"].inflate(16,16)):
                            target = p["to"]
                            if target not in state["scenes"]:
                                state["scenes"][target] = build_place(target, assets)
                            state["scenes"][target]["player"]["rect"].topleft = p["spawn"]
                            state["current"] = target
                            break

    # 移動（簡單自由移動）
    speed = 3
    player_rect.x += dx * speed
    player_rect.y += dy * speed
    player_rect.x = max(0, min(player_rect.x, WIDTH - player_rect.w))
    player_rect.y = max(0, min(player_rect.y, HEIGHT - player_rect.h))

    # 繪製
    screen.fill(scene["bg"])
    # 傳送門
    for p in scene["portals"]:
        pygame.draw.rect(screen, (60,60,60), p["rect"], 0)
        pygame.draw.rect(screen, (255,255,120), p["rect"], 2)
        draw_text(screen, p["label"], (p["rect"].x+4, p["rect"].y-20), (255,255,120))
    # NPC
    for npc in scene["npcs"]:
        npc.draw(screen, cam)
        if player_rect.colliderect(npc.rect.inflate(8,8)) and not npc.is_talking():
            draw_text(screen, "Enter 對話", (npc.rect.x, npc.rect.y-20), (255,255,255))
        npc.draw_dialog(screen)

    # 玩家
    pygame.draw.rect(screen, (120,200,255), player_rect)
    draw_text(screen, f"{scene['name']}（ESC 回選單）", (16, 10), COLOR["text"])

# 讓主程式也能 from scenes.world_places import loop
def loop(screen, state, assets):
    loop_place(screen, state, assets)

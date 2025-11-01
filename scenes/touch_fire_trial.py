from __future__ import annotations
import pygame
from core.ui import draw_text

# 不依賴 core.config，直接從畫面讀尺寸，避免解析度不一致導致元素跑出畫面
SPEED = 4

def build(assets=None, state=None):
    state = state or {}
    return {}

def loop(screen, state, assets=None):
    try:
        from core.overlay_hook import push_note
    except Exception:
        def push_note(_s, msg, ttl=1.2): print("[NOTE]", msg)
    try:
        from core.affinity import add as add_affinity
    except Exception:
        def add_affinity(_s,_k,_d): pass

    W, H = screen.get_width(), screen.get_height()
    player = pygame.Rect(int(W*0.2), int(H*0.5), 28, 28)
    fire   = pygame.Rect(int(W*0.6), int(H*0.5)-12, 32, 32)  # 放在畫面正中偏右，變大更顯眼

    clock = pygame.time.Clock()
    touched = False
    running = True

    while running and state.get("current") == "touch_fire_trial":
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                state["current"]="exit"; running=False; break
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running=False; break

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: player.x -= SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: player.x += SPEED
        if keys[pygame.K_UP] or keys[pygame.K_w]: player.y -= SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: player.y += SPEED
        player.clamp_ip(pygame.Rect(0,0,W,H))

        if player.colliderect(fire):
            touched = True
            running = False

        # 背景與裝飾：灰到黑的漸層，避免看起來「空白」
        for i in range(0, H, 6):
            shade = 12 + int(8*(i/H))
            pygame.draw.rect(screen, (shade,shade,shade+4), pygame.Rect(0,i,W,6))

        # 火焰更顯眼
        glow = pygame.Surface((90,90), pygame.SRCALPHA)
        pygame.draw.circle(glow,(255,140,30,95),(45,45),42)
        screen.blit(glow,(fire.x-28, fire.y-30))
        pygame.draw.rect(screen,(245,110,35),fire, border_radius=8)
        # 玩家
        pygame.draw.rect(screen,(230,230,240),player, border_radius=4)

        draw_text(screen, "借物成形：移動到火焰上以『吸取』力量。 (Esc 跳過)",
                  (int(W*0.08), int(H*0.12)))
        draw_text(screen, "提示：如果你只看到灰底＋可移動方塊，這就是教學關卡，火焰在畫面中央偏右。",
                  (int(W*0.08), int(H*0.12)+28))

        pygame.display.flip()
        clock.tick(60)

    if touched:
        add_affinity(state,"火",1)
        state.setdefault("flags",{})["borrowed_fire_done"]=True
        push_note(state,"你『借了火』，首次凝聚成功。")

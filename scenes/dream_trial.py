# project/scenes/dream_trial.py
from __future__ import annotations
import pygame
from core.ui import draw_text
from core.config import COLOR, WIDTH, HEIGHT, FPS
from core.affinity import get_value
from core.emotions import ensure_emotions, get_emotion, add_emotion
from core.dialogue import run_dialogue

def build(assets, state):
    ensure_emotions(state)
    # 可在此根據情緒建立本次試煉參數
    return {"resolved": False}

def loop(screen, state, assets):
    clock = pygame.time.Clock()
    # 進場對話（只跑一次）
    flags = state.setdefault("flags", {})
    if not flags.get("dream_intro_done"):
        run_dialogue(screen, "dream_intro")
        flags["dream_intro_done"] = True

    # 利用熟悉度/壓力決定難度（示範：x=stress/100，y=曲線值）
    stress = min(max(get_emotion(state, "stress"), 0), 100)
    x = stress/100.0
    try:
        difficulty = get_value("動態曲線版_Sheet1", x)  # 若不存在，except fallback
    except Exception:
        difficulty = x  # 簡易 fallback

    # 簡單互動：按空白鍵釋放力量（受難度影響），Enter 結算
    power = 0.0
    running = True
    while running:
        screen.fill((0,0,0))
        draw_text(screen, "【夢境試煉】", (40, 40), color=COLOR.get("hint",(200,200,120)))
        draw_text(screen, f"壓力:{int(stress)}  難度:{difficulty:.2f}", (40, 80))
        draw_text(screen, "按空白累積能量、Enter 結算、Esc 返回基地", (40, 120))
        draw_text(screen, f"能量：{power:.0f}", (40, 160))
        # 簡單條狀顯示
        bar_w = int(min(600, power))
        pygame.draw.rect(screen, (80,80,180), pygame.Rect(40, 200, bar_w, 24))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                state["current"] = "menu"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    state["current"] = "mind_hub"  # 試煉後回 hub
                elif event.key == pygame.K_SPACE:
                    # 難度越高，單次累積越慢
                    inc = max(1.0, 10.0*(1.0 - difficulty))
                    power += inc
                elif event.key == pygame.K_RETURN:
                    # 結算：能量>門檻 -> 降低壓力，否則增加壓力
                    threshold = 100.0 * (0.5 + 0.5*difficulty)
                    if power >= threshold:
                        add_emotion(state, "stress", -15)
                        add_emotion(state, "familiarity", +10)
                        outcome = "success"
                    else:
                        add_emotion(state, "stress", +10)
                        outcome = "fail"
                    # 結果對話
                    try:
                        run_dialogue(screen, f"dream_result_{outcome}")
                    except Exception:
                        pass
                    # 回到 hub
                    state["current"] = "mind_hub"
                    running = False
        clock.tick(FPS)

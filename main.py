from core.save import save_state, load_state
from core.overlay_hook import install_flip_hook, push_note
import pygame, sys
from core.config import WIDTH, HEIGHT, FPS
from core.assets import load_assets
from core.models import build_initial_state
from core.ui import init_fonts
from scenes.menu import build as build_menu, loop as menu_loop
from scenes.campus import build as build_campus, loop as campus_loop
from scenes.mind_hub import build as build_mind_hub, loop as mind_hub_loop
from scenes.story_scene import build as build_story, loop as story_loop
from scenes.dream_trial import build as build_dream, loop as dream_loop
from core.progression import ensure_progression_state, end_day, ap_left, spend_ap
from core.emotions import ensure_emotions
HAS_STORY = True
# 可選戰鬥
try:
    from scenes.battle_grid import build as build_battle_grid, loop as battle_grid_loop
    HAS_BATTLE_GRID = True
except Exception:
    HAS_BATTLE_GRID = False

# 世界場景（多地點）
from scenes.world_places import build_place, loop_place as place_loop

# 你可以在這裡列出所有 world place 的 key；也可由 menu 發出時動態建立
WORLD_KEYS = [
    "teaching","playground","garden","library","convenience","street",
    "dojo","activity","magic","fight_training","hub"
]

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("心靈之域")
    clock = pygame.time.Clock()
    init_fonts()
    assets = load_assets()

    state = build_initial_state(assets)
    state["assets"] = assets
    install_flip_hook(state)
    ensure_progression_state(state)  # 讓其他模組可從 state 拿到 assets
    ensure_emotions(state)
    # 基本場景
    state["scenes"] = {
        "menu": build_menu(assets),
        "campus": build_campus(assets),
        "mind_hub": build_mind_hub(assets),
    }
    if HAS_BATTLE_GRID:
        state["scenes"]["battle_grid"] = build_battle_grid(assets)

    # 初始當前場景
    state["current"] = "menu"

    while True:
        clock.tick(FPS)
        cur = state["current"]
        # 依場景型別分發
        if cur == "menu":
            menu_loop(screen, state)
        elif cur == "campus":
            campus_loop(screen, state, assets)
        elif cur == "mind_hub":
            mind_hub_loop(screen, state, assets)
        elif cur == "battle_grid" and HAS_BATTLE_GRID:
            battle_grid_loop(screen, state, assets)
        elif cur == "story":
            story_loop(screen, state, assets)
        elif cur == "dream_trial":
            dream_loop(screen, state, assets)
            story_loop(screen, state, assets)
        else:
            # 其餘一律視為 world_places 類型
            if cur not in state["scenes"]:
                # 如果還沒建，就動態建立
                state["scenes"][cur] = build_place(cur, assets)
            place_loop(screen, state, assets)
        pygame.display.flip()

if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        pass
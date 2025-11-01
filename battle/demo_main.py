# battle/demo_main.py
import pygame, sys
from battle.battle_manager import BattleManager
from battle.battle_input import handle_battle_input

def main():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((1200, 720))
    clock = pygame.time.Clock()
    bm = BattleManager(screen)

    running = True
    while running:
        dt = clock.tick(60) / 1000
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            handle_battle_input(bm, e)
        bm.update(dt)
        bm.draw()
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

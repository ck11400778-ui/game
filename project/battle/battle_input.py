import pygame

def handle_battle_input(bm, event):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_LEFT:  bm.move_cursor(-1, 0)
        if event.key == pygame.K_RIGHT: bm.move_cursor(+1, 0)
        if event.key == pygame.K_UP:    bm.move_cursor(0, -1)
        if event.key == pygame.K_DOWN:  bm.move_cursor(0, +1)
        if event.key == pygame.K_TAB:
            bm.cursor_board = "enemy" if bm.cursor_board == "ally" else "ally"
        bm.key_action(event.key)
    elif event.type == pygame.MOUSEBUTTONDOWN:
        bm.click_board(event.pos, event.button)

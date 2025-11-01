from __future__ import annotations
import pygame
NAV_UP    = {pygame.K_UP,    pygame.K_w}
NAV_DOWN  = {pygame.K_DOWN,  pygame.K_s}
NAV_LEFT  = {pygame.K_LEFT,  pygame.K_a}
NAV_RIGHT = {pygame.K_RIGHT, pygame.K_d}
CONFIRM   = {pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE}
BACK      = {pygame.K_ESCAPE, pygame.K_BACKSPACE}
def is_keydown(event, keys:set[int]) -> bool:
    return (event.type == pygame.KEYDOWN) and (event.key in keys)
def clear_after_action():
    pygame.event.clear()
def drain_all():
    pygame.event.clear()

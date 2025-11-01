# -*- coding: utf-8 -*-
# Compatibility: assets argument is optional.
from __future__ import annotations
import pygame
from typing import Dict
from core.ui import draw_text
from core.config import COLOR, WIDTH, HEIGHT, FPS
from core.portals import neighbors
from core.npc import list_at, interact

def build(assets=None, state=None):
    state = state or {}
    state.setdefault("area", "home_room")
    state.setdefault("roam_sel_neighbor", 0)
    state.setdefault("roam_sel_npc", 0)
    state.setdefault("roam_focus", "npc")  # npc 或 portal
    return {}

def _draw_panel(screen, rect, title):
    pygame.draw.rect(screen, (28,30,38), rect)
    pygame.draw.rect(screen, (0,0,0), rect, 2)
    draw_text(screen, title, (rect.x+10, rect.y+8), color=COLOR.get("hint",(200,200,160)))

def loop(screen, state, assets=None):
    clock = pygame.time.Clock()
    running = True
    while running and state.get("current") == "roam":
        screen.fill((18,18,24))
        area = state.get("area","home_room")
        draw_text(screen, f"區域：{area}", (24, 24), color=COLOR.get("text",(240,240,240)))
        draw_text(screen, "TAB切換面板，方向鍵選擇，Enter確認，Esc回主選單", (24, 54), color=(180,180,180))

        # neighbors
        nb = neighbors(area)
        nb_rect = pygame.Rect(24, 90, WIDTH-48, 120)
        _draw_panel(screen, nb_rect, "傳送門（雙向）")
        x = nb_rect.x + 16; y = nb_rect.y + 44
        for i, dest in enumerate(nb):
            sel = (i == state.get("roam_sel_neighbor",0))
            if sel and state.get("roam_focus")=="portal":
                pygame.draw.rect(screen, (60,60,90), pygame.Rect(x-8, y-4, 200, 26))
            draw_text(screen, f"→ {dest}", (x, y), color=COLOR.get("text",(230,230,230)))
            x += 220

        # npcs
        npc_rect = pygame.Rect(24, 230, WIDTH-48, HEIGHT-260)
        _draw_panel(screen, npc_rect, "此區NPC")
        npcs = list_at(area)
        y = npc_rect.y + 44
        for i, it in enumerate(npcs):
            sel = (i == state.get("roam_sel_npc",0))
            if sel and state.get("roam_focus")=="npc":
                pygame.draw.rect(screen, (70,70,105), pygame.Rect(npc_rect.x+10, y-4, npc_rect.width-20, 26))
            draw_text(screen, f"{it.name}（{it.title}）", (npc_rect.x+16, y))
            draw_text(screen, f"特質：{it.traits}", (npc_rect.x+360, y))
            y += 30

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                state["current"]="exit"; running=False; break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    state["roam_focus"] = "portal" if state.get("roam_focus")=="npc" else "npc"
                elif state.get("roam_focus")=="portal":
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        state["roam_sel_neighbor"] = (state.get("roam_sel_neighbor",0)-1) % max(1,len(nb))
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        state["roam_sel_neighbor"] = (state.get("roam_sel_neighbor",0)+1) % max(1,len(nb))
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                        if nb:
                            state["area"] = nb[state.get("roam_sel_neighbor",0)]
                else:  # npc focus
                    if event.key in (pygame.K_UP, pygame.K_w):
                        state["roam_sel_npc"] = (state.get("roam_sel_npc",0)-1) % max(1,len(npcs))
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        state["roam_sel_npc"] = (state.get("roam_sel_npc",0)+1) % max(1,len(npcs))
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                        if npcs:
                            npc = npcs[state.get("roam_sel_npc",0)]
                            interact(screen, state, npc.id)
                if event.key == pygame.K_ESCAPE:
                    state["current"]="start"; running=False; break

        clock.tick(FPS)

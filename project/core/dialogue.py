import os, json, pygame
from core.config import WIDTH, HEIGHT, COLOR
from core.ui import draw_text

DIALOGUE_DIR = os.path.join("data", "dialogues")

class DialogueRunner:
    def __init__(self, assets):
        self.assets = assets
        self.active = False
        self.nodes = {}
        self.cur = None
        self.queue_effects = []
        self.typing = 0
        self.fast = False
        self.portrait_cache = {}

    def start(self, dialogue_id):
        path = os.path.join(DIALOGUE_DIR, f"{dialogue_id}.json")
        if not os.path.exists(path):
            return False
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.nodes = {n["id"]: n for n in data["nodes"]}
        first = data.get("start", data["nodes"][0]["id"])
        self.cur = self.nodes[first]
        self.active = True
        self.queue_effects = []
        self.typing = 0
        return True

    def handle_event(self, event, state):
        if not self.active: return
        if event.type != pygame.KEYDOWN: return

        node = self.cur
        if node["type"] == "line":
            full = node.get("text","")
            # 快轉
            if event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                self.typing = len(full); return
            if getattr(self, "typing", 0) < len(full):
                self.typing = len(full)
            else:
                self._advance()
        elif node["type"] == "choice":
            if pygame.K_1 <= event.key <= pygame.K_9:
                idx = event.key - pygame.K_1
                choices = node.get("choices", [])
                if 0 <= idx < len(choices):
                    ch = choices[idx]
                    effs = ch.get("effects", [])
                    if effs: self.queue_effects.extend(effs)
                    nxt = ch.get("next")
                    if nxt: self._advance(nxt)
                    else: self.active=False; self.apply_effects(state)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                # 選擇題按 Enter 無動作
                pass
        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            if node["type"]=="line":
                full = node.get("text","")
                if self.typing < len(full): self.typing = len(full)
                else: self._advance()
        if not self.active:
            self.apply_effects(state)

    def _advance(self, next_id=None):
        nid = next_id if next_id is not None else self.cur.get("next")
        if not nid: self.active=False; return
        self.cur = self.nodes[nid]; self.typing = 0

    def update(self):
        if not self.active: return
        if self.cur["type"] == "line":
            txt = self.cur.get("text","")
            self.typing = min(len(txt), getattr(self, "typing", 0) + 1)

    def draw(self, screen):
        if not self.active: return
        import pygame
        box_h = 170
        pygame.draw.rect(screen, (0,0,0,160), (0, HEIGHT - box_h, WIDTH, box_h))
        pygame.draw.rect(screen, (255,255,255), (10, HEIGHT - box_h + 10, WIDTH-20, box_h-20), 2)
        node = self.cur
        x = 30; y = HEIGHT - box_h + 20
        if node.get("speaker"):
            draw_text(screen, node["speaker"], (x, y), COLOR["hint"])
        if node["type"] == "line":
            full = node.get("text","")
            shown = full[:getattr(self, "typing", 0)]
            draw_text(screen, shown, (x, y+28))
            draw_text(screen, "Enter/Space 繼續", (WIDTH-200, HEIGHT-28), (200,200,200), small=True)
        else:
            draw_text(screen, "選擇：", (x, y+6))
            cy = y + 34
            for i, ch in enumerate(node.get("choices", []), start=1):
                draw_text(screen, f"[{i}] {ch.get('text','')}", (x, cy))
                cy += 26

    def apply_effects(self, state):
        if not self.queue_effects: return
        for eff in self.queue_effects:
            t = eff.get("type")
            if t == "add_personality":
                from core.models import Personality
                name = eff["name"]; hp = eff["hp"]; atk = eff["atk"]
                if any(p.name == name for p in state["personalities"]): 
                    continue
                state["personalities"].append(Personality(name, hp, atk))
            elif t == "heal_all":
                n = eff.get("amount", 2)
                for p in state["personalities"]:
                    if p.alive: p.heal(n)
            elif t == "set_flag":
                scope = eff.get("scope"); key = eff.get("key"); val = eff.get("value", True)
                if scope and key is not None:
                    state.setdefault("flags", {}).setdefault(scope, {})
                    state["flags"][scope][key] = val
        self.queue_effects = []

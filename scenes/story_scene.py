from core.dialogue import run_dialogue
# scenes/story_scene.py
# 完整劇情系統 - 心靈覺醒劇情

import pygame
import json
import os
from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass, field

try:
    from core.config import WIDTH, HEIGHT
except ImportError:
    WIDTH, HEIGHT = 1200, 700

class DialogType(Enum):
    """對話類型"""
    NORMAL = "normal"           # 普通對話
    NARRATION = "narration"     # 旁白
    THOUGHT = "thought"         # 內心獨白
    CHOICE = "choice"           # 選擇
    SYSTEM = "system"           # 系統提示

class EffectType(Enum):
    """特效類型"""
    NONE = "none"
    SCREEN_SHAKE = "screen_shake"     # 畫面震動
    SCREEN_BLUR = "screen_blur"       # 畫面模糊
    FLASH = "flash"                   # 閃光
    FADE_TO_BLACK = "fade_to_black"   # 黑屏
    HEARTBEAT = "heartbeat"           # 心跳音效
    MIRROR_FLASH = "mirror_flash"     # 鏡子閃現

@dataclass
class DialogChoice:
    """對話選項"""
    text: str
    next_node: str
    flag_set: str = ""  # 設置標記

@dataclass
class DialogNode:
    """對話節點"""
    id: str
    type: DialogType
    speaker: str = ""
    text: str = ""
    background: str = ""
    character_image: str = ""
    position: str = "center"  # left, center, right
    next_node: str = ""
    choices: List[DialogChoice] = field(default_factory=list)
    effect: EffectType = EffectType.NONE
    sound: str = ""
    auto_advance: float = 0.0
    condition: str = ""  # 顯示條件

@dataclass
class Chapter:
    """章節"""
    id: str
    title: str
    description: str
    start_node: str
    nodes: Dict[str, DialogNode] = field(default_factory=dict)

class StoryManager:
    """劇情管理器"""
    
    def __init__(self, assets):
        self.assets = assets
        self.chapters: Dict[str, Chapter] = {}
        self.current_chapter: Optional[Chapter] = None
        self.current_node: Optional[DialogNode] = None
        self.story_flags: set = set()  # 劇情標記
        
        # UI設定
        self.text_speed = 50  # 字符/秒
        self.current_char = 0
        self.text_timer = 0.0
        self.waiting_for_input = False
        self.choice_cursor = 0
        
        # 特效
        self.effect_timer = 0.0
        self.shake_intensity = 0
        self.blur_amount = 0
        self.flash_alpha = 0
        self.fade_alpha = 0
        
        # 字體
        try:
            self.font = pygame.font.SysFont("Microsoft JhengHei", 18)
            self.big_font = pygame.font.SysFont("Microsoft JhengHei", 24)
            self.title_font = pygame.font.SysFont("Microsoft JhengHei", 32)
        except:
            self.font = pygame.font.Font(None, 18)
            self.big_font = pygame.font.Font(None, 24)
            self.title_font = pygame.font.Font(None, 32)
        
        # 顏色
        self.colors = {
            "bg": (20, 25, 35),
            "dialog_bg": (0, 0, 0, 200),
            "text": (255, 255, 255),
            "narration": (200, 200, 150),
            "thought": (150, 200, 255),
            "system": (255, 200, 100),
            "choice_bg": (40, 40, 80, 220),
            "choice_hover": (80, 80, 160, 220),
            "choice_border": (120, 120, 200),
        }
        
        # 載入劇情
        self._load_chapters()
    
    def _load_chapters(self):
        """載入劇情章節"""
        # 第一章：覺醒之前
        chapter1 = self._create_chapter1()
        self.chapters[chapter1.id] = chapter1
        
        # 第二章：火焰的影子
        chapter2 = self._create_chapter2()
        self.chapters[chapter2.id] = chapter2
        
        # 第三章：第一場比試
        chapter3 = self._create_chapter3()
        self.chapters[chapter3.id] = chapter3
    
    def _create_chapter1(self) -> Chapter:
        """第一章：覺醒之前"""
        chapter = Chapter(
            id="chapter1",
            title="第一章：覺醒之前",
            description="在靈氣復甦的時代，主角卻是唯一還沒覺醒的人...",
            start_node="scene1_1"
        )
        
        # 場景一：校園操場
        chapter.nodes["scene1_1"] = DialogNode(
            id="scene1_1",
            type=DialogType.NARRATION,
            text="黃昏的操場上，一群學生圍成一圈。",
            background="playground",
            next_node="scene1_2",
            auto_advance=2.0
        )
        
        chapter.nodes["scene1_2"] = DialogNode(
            id="scene1_2",
            type=DialogType.NARRATION,
            text="有人正操縱金屬棒將它扭成花形，另一個女生瞬移到籃框上坐著，笑聲引來驚呼。",
            next_node="scene1_3",
            effect=EffectType.FLASH
        )
        
        chapter.nodes["scene1_3"] = DialogNode(
            id="scene1_3",
            type=DialogType.NORMAL,
            speaker="同學甲",
            text="哇靠！真的扭成了！這就是覺醒者嗎？",
            next_node="scene1_4"
        )
        
        chapter.nodes["scene1_4"] = DialogNode(
            id="scene1_4",
            type=DialogType.NORMAL,
            speaker="同學乙",
            text="聽說靈氣復甦之後，幾乎每個人都會有異能……",
            next_node="scene1_5"
        )
        
        chapter.nodes["scene1_5"] = DialogNode(
            id="scene1_5",
            type=DialogType.NORMAL,
            speaker="同學丙",
            text="還有人還沒覺醒呢……比如他。",
            next_node="scene1_6"
        )
        
        chapter.nodes["scene1_6"] = DialogNode(
            id="scene1_6",
            type=DialogType.THOUGHT,
            speaker="主角",
            text="又來了……大家都在往前跑，我卻像被拋在原地一樣。",
            next_node="scene1_7",
            effect=EffectType.SCREEN_BLUR
        )
        
        # 場景二：走廊
        chapter.nodes["scene1_7"] = DialogNode(
            id="scene1_7",
            type=DialogType.NARRATION,
            text="主角走在回教室的走廊，聽見幾個同學在背後議論。",
            background="corridor",
            next_node="scene1_8"
        )
        
        chapter.nodes["scene1_8"] = DialogNode(
            id="scene1_8",
            type=DialogType.NORMAL,
            speaker="同學甲",
            text="萬一有些人一輩子都覺醒不了，不就廢了？",
            next_node="scene1_9"
        )
        
        chapter.nodes["scene1_9"] = DialogNode(
            id="scene1_9",
            type=DialogType.NORMAL,
            speaker="同學乙",
            text="說不定他就是那種人。",
            next_node="scene1_10"
        )
        
        chapter.nodes["scene1_10"] = DialogNode(
            id="scene1_10",
            type=DialogType.THOUGHT,
            speaker="主角",
            text="我真的……什麼都沒有嗎？",
            next_node="scene1_11",
            effect=EffectType.HEARTBEAT
        )
        
        # 場景三：昏迷
        chapter.nodes["scene1_11"] = DialogNode(
            id="scene1_11",
            type=DialogType.NARRATION,
            text="主角突然頭一陣暈眩，眼前一黑。",
            next_node="scene1_12",
            effect=EffectType.SCREEN_SHAKE
        )
        
        chapter.nodes["scene1_12"] = DialogNode(
            id="scene1_12",
            type=DialogType.NARRATION,
            text="黑暗夢境，四周被火焰般的裂縫劃開。",
            background="dream",
            next_node="scene1_13",
            effect=EffectType.FADE_TO_BLACK
        )
        
        chapter.nodes["scene1_13"] = DialogNode(
            id="scene1_13",
            type=DialogType.NORMAL,
            speaker="模糊聲音",
            text="憤怒……你終於感受到……",
            next_node="scene1_14",
            sound="whisper"
        )
        
        chapter.nodes["scene1_14"] = DialogNode(
            id="scene1_14",
            type=DialogType.NORMAL,
            speaker="主角",
            text="誰？你是誰？",
            next_node="scene1_15"
        )
        
        chapter.nodes["scene1_15"] = DialogNode(
            id="scene1_15",
            type=DialogType.NARRATION,
            text="模糊人影輪廓在火焰中晃動，但看不清臉。",
            next_node="scene1_16",
            effect=EffectType.SCREEN_SHAKE
        )
        
        # 場景四：保健室
        chapter.nodes["scene1_16"] = DialogNode(
            id="scene1_16",
            type=DialogType.NARRATION,
            text="主角在保健室醒來，天色已暗。",
            background="infirmary",
            next_node="scene1_17"
        )
        
        chapter.nodes["scene1_17"] = DialogNode(
            id="scene1_17",
            type=DialogType.NORMAL,
            speaker="阿澤",
            text="你剛才嚇死我了！怎麼突然暈倒？",
            character_image="azhe",
            next_node="scene1_18"
        )
        
        chapter.nodes["scene1_18"] = DialogNode(
            id="scene1_18",
            type=DialogType.NORMAL,
            speaker="主角",
            text="……可能是太累了吧。",
            next_node="scene1_19"
        )
        
        chapter.nodes["scene1_19"] = DialogNode(
            id="scene1_19",
            type=DialogType.NORMAL,
            speaker="阿澤",
            text="別太在意……每個人覺醒的時機不同，你一定也會的。",
            next_node="scene1_20"
        )
        
        chapter.nodes["scene1_20"] = DialogNode(
            id="scene1_20",
            type=DialogType.THOUGHT,
            speaker="主角",
            text="可是……我看到的，真的只是夢嗎？",
            next_node="scene1_21"
        )
        
        chapter.nodes["scene1_21"] = DialogNode(
            id="scene1_21",
            type=DialogType.NARRATION,
            text="主角走到鏡子前，鏡面一閃，短暫映出「火焰人影」站在身後，隨即消散。",
            next_node="scene1_22",
            effect=EffectType.MIRROR_FLASH
        )
        
        chapter.nodes["scene1_22"] = DialogNode(
            id="scene1_22",
            type=DialogType.NORMAL,
            speaker="低語",
            text="很快……",
            next_node="scene1_end",
            sound="whisper"
        )
        
        chapter.nodes["scene1_end"] = DialogNode(
            id="scene1_end",
            type=DialogType.SYSTEM,
            text="情緒是力量的種子。當種子裂開，會誕生什麼樣的存在？",
            next_node="end"
        )
        
        return chapter
    
    def _create_chapter2(self) -> Chapter:
        """第二章：火焰的影子"""
        chapter = Chapter(
            id="chapter2",
            title="第二章：火焰的影子",
            description="主角開始探索自己的力量...",
            start_node="scene2_1"
        )
        
        # 場景一：校園後山
        chapter.nodes["scene2_1"] = DialogNode(
            id="scene2_1",
            type=DialogType.NARRATION,
            text="主角課後一個人躲到校園後山的小徑，想嘗試昨晚的幻象。",
            background="mountain",
            next_node="scene2_2"
        )
        
        chapter.nodes["scene2_2"] = DialogNode(
            id="scene2_2",
            type=DialogType.THOUGHT,
            speaker="主角",
            text="昨天不是幻覺……一定有什麼東西在我體內。只要……集中……",
            next_node="scene2_3"
        )
        
        chapter.nodes["scene2_3"] = DialogNode(
            id="scene2_3",
            type=DialogType.SYSTEM,
            text="嘗試召喚力量...",
            next_node="scene2_4",
            effect=EffectType.FLASH
        )
        
        chapter.nodes["scene2_4"] = DialogNode(
            id="scene2_4",
            type=DialogType.NARRATION,
            text="模糊的火焰輪廓出現，卻立刻消散。",
            next_node="scene2_5",
            effect=EffectType.SCREEN_SHAKE
        )
        
        chapter.nodes["scene2_5"] = DialogNode(
            id="scene2_5",
            type=DialogType.THOUGHT,
            speaker="主角",
            text="果然……沒那麼容易。",
            next_node="scene2_6"
        )
        
        # 場景二：夢境試煉
        chapter.nodes["scene2_6"] = DialogNode(
            id="scene2_6",
            type=DialogType.NARRATION,
            text="夜裡，主角再度夢見裂縫般的火焰世界。",
            background="dream",
            next_node="scene2_7",
            effect=EffectType.FADE_TO_BLACK
        )
        
        chapter.nodes["scene2_7"] = DialogNode(
            id="scene2_7",
            type=DialogType.NORMAL,
            speaker="火人格",
            text="你的怒火，還不夠純粹。",
            next_node="scene2_8"
        )
        
        chapter.nodes["scene2_8"] = DialogNode(
            id="scene2_8",
            type=DialogType.NORMAL,
            speaker="主角",
            text="我該怎麼做？！",
            next_node="scene2_9"
        )
        
        chapter.nodes["scene2_9"] = DialogNode(
            id="scene2_9",
            type=DialogType.NORMAL,
            speaker="火人格",
            text="逼自己……直面壓抑。",
            next_node="scene2_10"
        )
        
        chapter.nodes["scene2_10"] = DialogNode(
            id="scene2_10",
            type=DialogType.SYSTEM,
            text="進入火焰走廊試煉...",
            next_node="scene2_11"
        )
        
        # 場景三：現實中的小事件
        chapter.nodes["scene2_11"] = DialogNode(
            id="scene2_11",
            type=DialogType.NARRATION,
            text="走廊上，控水同學失控，水流暴衝。",
            background="corridor",
            next_node="scene2_12",
            effect=EffectType.SCREEN_SHAKE
        )
        
        chapter.nodes["scene2_12"] = DialogNode(
            id="scene2_12",
            type=DialogType.NARRATION,
            text="主角驚慌，想召喚火人格，但徒手凝聚的火焰很模糊。",
            next_node="scene2_13"
        )
        
        chapter.nodes["scene2_13"] = DialogNode(
            id="scene2_13",
            type=DialogType.SYSTEM,
            text="地上有一個煙蒂仍在冒煙...",
            next_node="scene2_14"
        )
        
        chapter.nodes["scene2_14"] = DialogNode(
            id="scene2_14",
            type=DialogType.NARRATION,
            text="火人格吸收那點火焰，成功凝型揮拳，蒸乾水流！",
            next_node="scene2_15",
            effect=EffectType.FLASH
        )
        
        chapter.nodes["scene2_15"] = DialogNode(
            id="scene2_15",
            type=DialogType.NORMAL,
            speaker="阿澤",
            text="你……不是沒有覺醒嗎？",
            character_image="azhe",
            next_node="scene2_16"
        )
        
        chapter.nodes["scene2_16"] = DialogNode(
            id="scene2_16",
            type=DialogType.NORMAL,
            speaker="主角",
            text="我……借了火。",
            next_node="scene2_17"
        )
        
        # 場景四：第二次夢境
        chapter.nodes["scene2_17"] = DialogNode(
            id="scene2_17",
            type=DialogType.NARRATION,
            text="主角再度夢到火焰世界，這一次火人格終於清晰完整。",
            background="dream",
            next_node="scene2_18",
            effect=EffectType.FADE_TO_BLACK
        )
        
        chapter.nodes["scene2_18"] = DialogNode(
            id="scene2_18",
            type=DialogType.NORMAL,
            speaker="火人格",
            text="終於……能好好見面了。",
            next_node="scene2_19"
        )
        
        chapter.nodes["scene2_19"] = DialogNode(
            id="scene2_19",
            type=DialogType.NORMAL,
            speaker="主角",
            text="你……就是我？",
            next_node="scene2_20"
        )
        
        chapter.nodes["scene2_20"] = DialogNode(
            id="scene2_20",
            type=DialogType.NORMAL,
            speaker="火人格",
            text="我是你壓抑的怒火，你的戰意。從今以後，我會和你並肩。",
            next_node="scene2_21"
        )
        
        chapter.nodes["scene2_21"] = DialogNode(
            id="scene2_21",
            type=DialogType.SYSTEM,
            text="火人格·解鎖！",
            next_node="scene2_end",
            effect=EffectType.FLASH
        )
        
        chapter.nodes["scene2_end"] = DialogNode(
            id="scene2_end",
            type=DialogType.SYSTEM,
            text="情緒化為形，形化為力。這只是開始——更多的情緒，正在深處蠢蠢欲動。",
            next_node="end"
        )
        
        return chapter
    
    def _create_chapter3(self) -> Chapter:
        """第三章：第一場比試"""
        chapter = Chapter(
            id="chapter3",
            title="第三章：第一場比試",
            description="主角的力量首次在眾人面前展現...",
            start_node="scene3_1"
        )
        
        chapter.nodes["scene3_1"] = DialogNode(
            id="scene3_1",
            type=DialogType.NARRATION,
            text="校園比試大會，主角第一場對手就是班上的王牌：張博堯。",
            background="arena",
            next_node="scene3_2"
        )
        
        chapter.nodes["scene3_2"] = DialogNode(
            id="scene3_2",
            type=DialogType.NORMAL,
            speaker="張博堯",
            text="兄弟，別怪我手下不留情，這可是比試。",
            character_image="zhang",
            next_node="scene3_3"
        )
        
        chapter.nodes["scene3_3"] = DialogNode(
            id="scene3_3",
            type=DialogType.SYSTEM,
            text="戰鬥開始！",
            next_node="scene3_4",
            effect=EffectType.FLASH
        )
        
        chapter.nodes["scene3_4"] = DialogNode(
            id="scene3_4",
            type=DialogType.NARRATION,
            text="張博堯用磁場操控金屬製造障礙、壓迫。",
            next_node="scene3_5",
            effect=EffectType.SCREEN_SHAKE
        )
        
        chapter.nodes["scene3_5"] = DialogNode(
            id="scene3_5",
            type=DialogType.NORMAL,
            speaker="阿澤",
            text="就是現在！用你真正的力量！",
            next_node="scene3_6"
        )
        
        chapter.nodes["scene3_6"] = DialogNode(
            id="scene3_6",
            type=DialogType.NARRATION,
            text="主角情緒被逼到極限——火人格燃燒得更旺，首次爆發技能「炎衝擊」！",
            next_node="scene3_7",
            effect=EffectType.FLASH
        )
        
        chapter.nodes["scene3_7"] = DialogNode(
            id="scene3_7",
            type=DialogType.NARRATION,
            text="金屬被蒸得滾燙，張博堯不得不停止操控。",
            next_node="scene3_8",
            effect=EffectType.SCREEN_SHAKE
        )
        
        chapter.nodes["scene3_8"] = DialogNode(
            id="scene3_8",
            type=DialogType.SYSTEM,
            text="勝者——主角！",
            next_node="scene3_9"
        )
        
        chapter.nodes["scene3_9"] = DialogNode(
            id="scene3_9",
            type=DialogType.NORMAL,
            speaker="張博堯",
            text="真是的……你藏得比誰都深。",
            next_node="scene3_10"
        )
        
        chapter.nodes["scene3_10"] = DialogNode(
            id="scene3_10",
            type=DialogType.NORMAL,
            speaker="林思妍",
            text="人格化的異能……前所未見。",
            next_node="scene3_11"
        )
        
        chapter.nodes["scene3_11"] = DialogNode(
            id="scene3_11",
            type=DialogType.NORMAL,
            speaker="周子齊",
            text="黑炎使者！這名字不錯吧！",
            next_node="scene3_12"
        )
        
        chapter.nodes["scene3_12"] = DialogNode(
            id="scene3_12",
            type=DialogType.THOUGHT,
            speaker="主角",
            text="第一次……在所有人面前，承認了這股力量。可是……這只是開始。",
            next_node="scene3_end"
        )
        
        chapter.nodes["scene3_end"] = DialogNode(
            id="scene3_end",
            type=DialogType.SYSTEM,
            text="主角的力量，與眾不同。既是武器，也是枷鎖。而校園比試，只是更大風暴的前奏……",
            next_node="end"
        )
        
        return chapter
    
    def start_chapter(self, chapter_id: str):
        """開始章節"""
        if chapter_id in self.chapters:
            self.current_chapter = self.chapters[chapter_id]
            start_node_id = self.current_chapter.start_node
            if start_node_id in self.current_chapter.nodes:
                self.current_node = self.current_chapter.nodes[start_node_id]
                self._reset_text()
                return True
        return False
    
    def _reset_text(self):
        """重置文字顯示"""
        self.current_char = 0
        self.text_timer = 0.0
        self.waiting_for_input = False
        self.choice_cursor = 0
    
    def handle_input(self, keys_just_pressed):
        """處理輸入"""
        import pygame
        
        if not self.current_node:
            return None
        
        # 選擇對話
        if self.current_node.type == DialogType.CHOICE:
            if self.current_node.choices:
                if pygame.K_UP in keys_just_pressed:
                    self.choice_cursor = max(0, self.choice_cursor - 1)
                elif pygame.K_DOWN in keys_just_pressed:
                    self.choice_cursor = min(len(self.current_node.choices) - 1, self.choice_cursor + 1)
                elif pygame.K_SPACE in keys_just_pressed or pygame.K_RETURN in keys_just_pressed:
                    choice = self.current_node.choices[self.choice_cursor]
                    if choice.flag_set:
                        self.story_flags.add(choice.flag_set)
                    self._advance_to_node(choice.next_node)
        else:
            # 普通對話
            if pygame.K_SPACE in keys_just_pressed or pygame.K_RETURN in keys_just_pressed:
                if self.current_char >= len(self.current_node.text):
                    self._advance_node()
                else:
                    # 快速顯示完整文字
                    self.current_char = len(self.current_node.text)
        
        # ESC退出
        if pygame.K_ESCAPE in keys_just_pressed:
            return "exit"
        
        return None
    
    def _advance_node(self):
        """推進劇情"""
        if self.current_node.next_node:
            self._advance_to_node(self.current_node.next_node)
        elif self.current_node.next_node == "end":
            self.current_node = None
            return "chapter_end"
    
    def _advance_to_node(self, node_id: str):
        """前進到指定節點"""
        if node_id == "end":
            self.current_node = None
            return
        
        if self.current_chapter and node_id in self.current_chapter.nodes:
            self.current_node = self.current_chapter.nodes[node_id]
            self._reset_text()
    
    def update(self, dt: float):
        """更新"""
        if not self.current_node:
            return
        
        # 更新文字顯示
        if self.current_char < len(self.current_node.text):
            self.text_timer += dt
            chars_to_show = int(self.text_timer * self.text_speed)
            self.current_char = min(chars_to_show, len(self.current_node.text))
        
        # 自動前進
        if self.current_node.auto_advance > 0 and self.current_char >= len(self.current_node.text):
            self.effect_timer += dt
            if self.effect_timer >= self.current_node.auto_advance:
                self.effect_timer = 0.0
                self._advance_node()
        
        # 更新特效
        self._update_effects(dt)
    
    def _update_effects(self, dt: float):
        """更新特效"""
        effect = self.current_node.effect if self.current_node else EffectType.NONE
        
        if effect == EffectType.SCREEN_SHAKE:
            self.shake_intensity = max(0, self.shake_intensity - dt * 10)
            if self.shake_intensity == 0:
                self.shake_intensity = 5
        elif effect == EffectType.SCREEN_BLUR:
            self.blur_amount = min(10, self.blur_amount + dt * 20)
        elif effect == EffectType.FLASH:
            self.flash_alpha = 255
        else:
            self.shake_intensity = 0
            self.blur_amount = max(0, self.blur_amount - dt * 30)
            self.flash_alpha = max(0, self.flash_alpha - dt * 500)
    
    def draw(self, screen):
        """繪製劇情"""
        if not self.current_node:
            return
        
        # 背景
        screen.fill(self.colors["bg"])
        
        # 應用畫面震動
        shake_x = shake_y = 0
        if self.shake_intensity > 0:
            import random
            shake_x = random.randint(-int(self.shake_intensity), int(self.shake_intensity))
            shake_y = random.randint(-int(self.shake_intensity), int(self.shake_intensity))
        
        # 創建繪製表面
        draw_surface = pygame.Surface((WIDTH, HEIGHT))
        draw_surface.fill(self.colors["bg"])
        
        # 繪製背景圖片（如果有）
        if self.current_node.background:
            # TODO: 載入背景圖片
            pass
        
        # 繪製角色圖片（如果有）
        if self.current_node.character_image:
            # TODO: 載入角色立繪
            pass
        
        # 繪製對話框
        self._draw_dialog_box(draw_surface)
        
        # 繪製選項
        if self.current_node.type == DialogType.CHOICE:
            self._draw_choices(draw_surface)
        
        # 應用模糊效果
        if self.blur_amount > 0:
            # 簡單模糊效果
            for i in range(int(self.blur_amount)):
                draw_surface.set_alpha(200)
        
        # 繪製到主螢幕（應用震動）
        screen.blit(draw_surface, (shake_x, shake_y))
        
        # 閃光效果
        if self.flash_alpha > 0:
            flash_surface = pygame.Surface((WIDTH, HEIGHT))
            flash_surface.fill((255, 255, 255))
            flash_surface.set_alpha(int(self.flash_alpha))
            screen.blit(flash_surface, (0, 0))
    
    def _draw_dialog_box(self, surface):
        """繪製對話框"""
        # 對話框位置
        box_height = 200
        box_y = HEIGHT - box_height - 20
        box_rect = pygame.Rect(20, box_y, WIDTH - 40, box_height)
        
        # 半透明背景
        dialog_surf = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
        dialog_surf.fill(self.colors["dialog_bg"])
        surface.blit(dialog_surf, box_rect)
        
        # 邊框
        pygame.draw.rect(surface, (200, 200, 200), box_rect, 2)
        
        # 說話者名字
        if self.current_node.speaker:
            name_bg = pygame.Rect(box_rect.x, box_rect.y - 35, 150, 35)
            name_surf = pygame.Surface((name_bg.width, name_bg.height), pygame.SRCALPHA)
            name_surf.fill((40, 40, 60, 220))
            surface.blit(name_surf, name_bg)
            
            name_text = self.big_font.render(self.current_node.speaker, True, self.colors["text"])
            surface.blit(name_text, (name_bg.x + 10, name_bg.y + 5))
        
        # 對話文字
        displayed_text = self.current_node.text[:self.current_char]
        text_color = self._get_text_color()
        
        # 文字換行
        words = displayed_text
        max_width = box_rect.width - 60
        lines = []
        current_line = ""
        
        for char in words:
            test_line = current_line + char
            text_width = self.font.size(test_line)[0]
            
            if text_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = char
        
        if current_line:
            lines.append(current_line)
        
        # 繪製文字
        text_y = box_rect.y + 20
        for line in lines[:6]:  # 最多6行
            text_surf = self.font.render(line, True, text_color)
            surface.blit(text_surf, (box_rect.x + 30, text_y))
            text_y += 28
        
        # 繼續提示
        if self.current_char >= len(self.current_node.text):
            if self.current_node.next_node and self.current_node.type != DialogType.CHOICE:
                prompt = "按空白鍵繼續..."
                prompt_surf = self.font.render(prompt, True, (150, 150, 150))
                surface.blit(prompt_surf, (box_rect.right - 150, box_rect.bottom - 30))
    
    def _draw_choices(self, surface):
        """繪製選擇選項"""
        if not self.current_node.choices:
            return
        
        choice_height = 50
        total_height = len(self.current_node.choices) * choice_height
        start_y = HEIGHT // 2 - total_height // 2
        
        for i, choice in enumerate(self.current_node.choices):
            y = start_y + i * choice_height
            choice_rect = pygame.Rect(100, y, WIDTH - 200, choice_height - 10)
            
            # 背景
            bg_color = self.colors["choice_hover"] if i == self.choice_cursor else self.colors["choice_bg"]
            choice_surf = pygame.Surface((choice_rect.width, choice_rect.height), pygame.SRCALPHA)
            choice_surf.fill(bg_color)
            surface.blit(choice_surf, choice_rect)
            
            # 邊框
            pygame.draw.rect(surface, self.colors["choice_border"], choice_rect, 2)
            
            # 選項文字
            prefix = "► " if i == self.choice_cursor else "  "
            text = f"{prefix}{choice.text}"
            text_surf = self.font.render(text, True, self.colors["text"])
            text_pos = (choice_rect.x + 20, choice_rect.y + 12)
            surface.blit(text_surf, text_pos)
    
    def _get_text_color(self) -> tuple:
        """獲取文字顏色"""
        type_colors = {
            DialogType.NORMAL: self.colors["text"],
            DialogType.NARRATION: self.colors["narration"],
            DialogType.THOUGHT: self.colors["thought"],
            DialogType.SYSTEM: self.colors["system"],
        }
        return type_colors.get(self.current_node.type, self.colors["text"])
    
    def is_active(self) -> bool:
        """檢查劇情是否進行中"""
        return self.current_node is not None


# 場景類別（用於整合到主遊戲）
class StoryScene:
    def __init__(self, assets):
        self.story_manager = StoryManager(assets)
        self.assets = assets
    
    def start_chapter(self, chapter_id: str):
        """開始章節"""
        return self.story_manager.start_chapter(chapter_id)
    
    def handle_input(self, keys_just_pressed, state):
        """處理輸入"""
        result = self.story_manager.handle_input(keys_just_pressed)
        
        if result == "exit":
            state["current"] = "menu"
        elif result == "chapter_end":
            state["current"] = "menu"
    
    def update(self, dt: float):
        """更新"""
        self.story_manager.update(dt)
    
    def draw(self, screen):
        """繪製"""
        self.story_manager.draw(screen)


# 構建和循環函數（用於主遊戲整合）
def build(assets):
    """構建劇情場景"""
    return StoryScene(assets)


def loop(screen, state, assets):
    """劇情場景主循環"""
    scene = state["scenes"].get("story")
    
    if not scene:
        # 第一次進入，創建場景
        scene = build(assets)
        state["scenes"]["story"] = scene
        # 開始第一章
        scene.start_chapter("chapter1")
    
    # 處理輸入
    keys_just_pressed = []
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            keys_just_pressed.append(event.key)
    
    scene.handle_input(keys_just_pressed, state)
    
    # 更新
    scene.update(1/60)
    
    # 繪製
    scene.draw(screen)


# 快速測試函數
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("劇情測試")
    clock = pygame.time.Clock()
    # 一次性播放開場故事（使用 state flag 避免重複）
    if not state.get('flags', {}).get('opening_story_done'):
        _play_opening_story(screen, assets, state)
        state.setdefault('flags', {})['opening_story_done'] = True
    
    story = StoryManager(None)
    story.start_chapter("chapter1")
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        
        keys_just_pressed = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                keys_just_pressed.append(event.key)
        
        result = story.handle_input(keys_just_pressed)
        if result == "exit":
            running = False
        
        story.update(dt)
        story.draw(screen)
        
        pygame.display.flip()
    
    pygame.quit()

# Unified dialogue call injected by patch
def _play_opening_story(screen, assets, state):
    # 調用統一對話系統，對應 data/dialogues/opening_story.json
    run_dialogue(screen, 'opening_story')
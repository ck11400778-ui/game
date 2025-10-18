import pygame
import json
import os
from enum import Enum
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from copy import deepcopy

try:
    from core.config import WIDTH, HEIGHT
except ImportError:
    WIDTH, HEIGHT = 1200, 700

class BattleState(Enum):
    """戰鬥狀態"""
    TURN_START = "turn_start"              # 回合開始
    CHOOSING_ACTION = "choosing_action"    # 選擇行動（移動/技能）
    MOVING = "moving"                      # 移動中
    AFTER_MOVE = "after_move"             # 移動後（可再移動或攻擊）
    SELECTING_SKILL = "selecting_skill"    # 選擇技能
    SELECTING_TARGETS = "selecting_targets" # 選擇目標範圍
    EXECUTING_SKILL = "executing_skill"    # 執行技能
    ANIMATING = "animating"                # 動畫播放
    TURN_END = "turn_end"                  # 回合結束
    BATTLE_END = "battle_end"              # 戰鬥結束

class ActionType(Enum):
    """行動類型"""
    MOVE = "move"          # 移動
    SKILL = "skill"        # 技能
    END_TURN = "end_turn"  # 結束回合

class SkillType(Enum):
    """技能類型"""
    DAMAGE = "damage"                    # 純傷害
    DISPLACEMENT = "displacement"        # 純位移
    DAMAGE_DISPLACEMENT = "damage_displacement"  # 傷害+位移
    SELF_TELEPORT = "self_teleport"     # 自己瞬移
    ALLY_FORMATION = "ally_formation"    # 己方陣型改變

class SkillRange(Enum):
    """技能範圍類型"""
    SINGLE = "single"          # 單體
    LINE = "line"              # 直線
    CROSS = "cross"            # 十字
    AREA = "area"              # 範圍圓形
    CUSTOM = "custom"          # 自定義形狀
    ALL_ENEMIES = "all_enemies" # 全體敵人
    ALL_ALLIES = "all_allies"   # 全體友軍

class Territory(Enum):
    """領地類型"""
    PLAYER_ZONE = "player_zone"    # 玩家陣地 (左側)
    BUFFER_ZONE = "buffer_zone"    # 緩衝區 (中間)
    ENEMY_ZONE = "enemy_zone"      # 敵人陣地 (右側)

@dataclass
class Position:
    """位置"""
    x: int
    y: int
    
    def __add__(self, other):
        return Position(self.x + other.x, self.y + other.y)
    
    def __eq__(self, other):
        if not isinstance(other, Position):
            return False
        return self.x == other.x and self.y == other.y
    
    def __hash__(self):
        return hash((self.x, self.y))
    
    def distance_to(self, other) -> int:
        """曼哈頓距離"""
        return abs(self.x - other.x) + abs(self.y - other.y)
    
    def __repr__(self):
        return f"Pos({self.x},{self.y})"

@dataclass
class Skill:
    """技能資料"""
    id: str
    name: str
    description: str
    mp_cost: int
    skill_type: SkillType
    range_type: SkillRange
    
    # 傷害相關
    damage: int = 0
    
    # 位移相關
    displacement_distance: int = 0  # 位移距離
    displacement_direction: str = "away"  # 位移方向: away(遠離), toward(靠近), custom
    
    # 範圍相關
    range_distance: int = 3         # 技能射程
    effect_area: int = 1            # 效果範圍大小
    custom_pattern: List[Tuple[int, int]] = field(default_factory=list)  # 自定義形狀
    
    # 特殊效果
    self_teleport_positions: List[Tuple[int, int]] = field(default_factory=list)  # 自己可傳送位置
    formation_pattern: List[Tuple[int, int]] = field(default_factory=list)  # 陣型模式
    
    # 視覺
    icon_name: str = ""
    animation: str = "default"
    
    def can_use(self, user, grid) -> bool:
        """檢查是否可使用"""
        if user.current_mp < self.mp_cost:
            return False
        return True

@dataclass
class Character:
    """角色資料"""
    id: str
    name: str
    max_hp: int
    current_hp: int
    max_mp: int
    current_mp: int
    attack: int
    defense: int
    speed: int
    position: Position
    sprite_name: str
    skills: List[Skill] = field(default_factory=list)
    is_player: bool = True
    
    # 戰鬥狀態
    has_moved: bool = False         # 本回合是否移動過
    move_count: int = 0             # 本回合移動次數
    has_acted: bool = False         # 本回合是否行動過
    in_enemy_territory: bool = False  # 是否在敵方領地
    
    # 特殊狀態標記
    is_taunting: bool = False       # 是否處於嘲諷狀態
    is_blocking_cursor: bool = False  # 是否阻擋游標
    
    status_effects: Dict[str, int] = field(default_factory=dict)
    facing: str = "right"
    
    def reset_turn(self):
        """重置回合狀態"""
        self.has_moved = False
        self.move_count = 0
        self.has_acted = False
    
    def can_move(self) -> bool:
        """是否可以移動"""
        return self.move_count < 2 and not self.has_acted
    
    def can_act(self) -> bool:
        """是否可以行動（使用技能）"""
        return not self.has_acted

class BattleGrid:
    """戰鬥格子系統 - 15x7格 (7+1+7)"""
    
    def __init__(self):
        self.width = 15   # 7(玩家) + 1(緩衝) + 7(敵人)
        self.height = 7
        
        # 領地劃分
        self.player_zone = (0, 6)      # x: 0-6
        self.buffer_zone = 7            # x: 7
        self.enemy_zone = (8, 14)      # x: 8-14
        
        # 角色位置
        self.characters: Dict[Position, Character] = {}
        
        # 視覺效果
        self.effects: Dict[Position, dict] = {}
    
    def get_territory(self, pos: Position) -> Territory:
        """獲取位置所屬領地"""
        if self.player_zone[0] <= pos.x <= self.player_zone[1]:
            return Territory.PLAYER_ZONE
        elif pos.x == self.buffer_zone:
            return Territory.BUFFER_ZONE
        else:
            return Territory.ENEMY_ZONE
    
    def is_valid_position(self, pos: Position) -> bool:
        """檢查位置是否有效"""
        return 0 <= pos.x < self.width and 0 <= pos.y < self.height
    
    def is_occupied(self, pos: Position) -> bool:
        """檢查位置是否被佔用"""
        return pos in self.characters
    
    def get_character_at(self, pos: Position) -> Optional[Character]:
        """獲取指定位置的角色"""
        return self.characters.get(pos)
    
    def is_in_enemy_territory(self, char: Character, pos: Position) -> bool:
        """檢查角色在該位置是否處於敵方領地"""
        territory = self.get_territory(pos)
        if char.is_player:
            return territory == Territory.ENEMY_ZONE
        else:
            return territory == Territory.PLAYER_ZONE
    
    def get_valid_moves(self, pos: Position, char: Character) -> List[Position]:
        """獲取角色可移動的位置"""
        valid_moves = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # 上下左右
        
        for dx, dy in directions:
            new_pos = Position(pos.x + dx, pos.y + dy)
            if self.is_valid_position(new_pos) and not self.is_occupied(new_pos):
                valid_moves.append(new_pos)
        
        return valid_moves
    
    def get_skill_targets(self, caster: Character, skill: Skill, target_pos: Position) -> List[Position]:
        """根據技能類型獲取所有受影響的位置"""
        targets = []
        caster_pos = caster.position
        
        if skill.range_type == SkillRange.SINGLE:
            if self.is_valid_position(target_pos):
                targets.append(target_pos)
        
        elif skill.range_type == SkillRange.LINE:
            # 直線攻擊
            dx = target_pos.x - caster_pos.x
            dy = target_pos.y - caster_pos.y
            if dx != 0:
                step = 1 if dx > 0 else -1
                for i in range(abs(dx) + 1):
                    pos = Position(caster_pos.x + i * step, caster_pos.y)
                    if self.is_valid_position(pos):
                        targets.append(pos)
            elif dy != 0:
                step = 1 if dy > 0 else -1
                for i in range(abs(dy) + 1):
                    pos = Position(caster_pos.x, caster_pos.y + i * step)
                    if self.is_valid_position(pos):
                        targets.append(pos)
        
        elif skill.range_type == SkillRange.HORIZONTAL_SWEEP:
            # 橫掃：整個橫排
            for x in range(self.width):
                pos = Position(x, target_pos.y)
                if self.is_valid_position(pos):
                    targets.append(pos)
        
        elif skill.range_type == SkillRange.VERTICAL_SWEEP:
            # 豎掃：整個豎列
            for y in range(self.height):
                pos = Position(target_pos.x, y)
                if self.is_valid_position(pos):
                    targets.append(pos)
        
        elif skill.range_type == SkillRange.CROSS:
            # 十字攻擊
            for i in range(-skill.effect_area, skill.effect_area + 1):
                pos1 = Position(target_pos.x + i, target_pos.y)
                if self.is_valid_position(pos1):
                    targets.append(pos1)
                pos2 = Position(target_pos.x, target_pos.y + i)
                if self.is_valid_position(pos2):
                    targets.append(pos2)
        
        elif skill.range_type == SkillRange.AREA:
            # 菱形範圍
            for dx in range(-skill.effect_area, skill.effect_area + 1):
                for dy in range(-skill.effect_area, skill.effect_area + 1):
                    if abs(dx) + abs(dy) <= skill.effect_area:
                        pos = Position(target_pos.x + dx, target_pos.y + dy)
                        if self.is_valid_position(pos):
                            targets.append(pos)
        
        elif skill.range_type == SkillRange.CIRCLE:
            # 真圓形（使用歐幾里得距離）
            radius = skill.effect_area
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    if dx*dx + dy*dy <= radius*radius:
                        pos = Position(target_pos.x + dx, target_pos.y + dy)
                        if self.is_valid_position(pos):
                            targets.append(pos)
        
        elif skill.range_type == SkillRange.CONE:
            # 扇形（朝向目標方向）
            dx = target_pos.x - caster_pos.x
            dy = target_pos.y - caster_pos.y
            
            # 確定主要方向
            if abs(dx) > abs(dy):
                # 水平扇形
                direction = 1 if dx > 0 else -1
                for dist in range(1, skill.effect_area + 1):
                    for spread in range(-dist, dist + 1):
                        pos = Position(caster_pos.x + direction * dist, caster_pos.y + spread)
                        if self.is_valid_position(pos):
                            targets.append(pos)
            else:
                # 垂直扇形
                direction = 1 if dy > 0 else -1
                for dist in range(1, skill.effect_area + 1):
                    for spread in range(-dist, dist + 1):
                        pos = Position(caster_pos.x + spread, caster_pos.y + direction * dist)
                        if self.is_valid_position(pos):
                            targets.append(pos)
        
        elif skill.range_type == SkillRange.CUSTOM:
            # 自定義形狀
            for dx, dy in skill.custom_pattern:
                pos = Position(target_pos.x + dx, target_pos.y + dy)
                if self.is_valid_position(pos):
                    targets.append(pos)
        
        elif skill.range_type == SkillRange.ALL_ENEMIES:
            for pos, char in self.characters.items():
                if char.is_player != caster.is_player:
                    targets.append(pos)
        
        elif skill.range_type == SkillRange.ALL_ALLIES:
            for pos, char in self.characters.items():
                if char.is_player == caster.is_player:
                    targets.append(pos)
        
        return list(set(targets))
    
    def move_character(self, from_pos: Position, to_pos: Position) -> bool:
        """移動角色"""
        if not self.is_valid_position(to_pos) or self.is_occupied(to_pos):
            return False
        
        if from_pos in self.characters:
            char = self.characters.pop(from_pos)
            char.position = to_pos
            
            # 檢查是否進入敵方領地
            char.in_enemy_territory = self.is_in_enemy_territory(char, to_pos)
            
            self.characters[to_pos] = char
            return True
        
        return False

class TacticalBattleScene:
    """戰術戰鬥場景"""
    
    def __init__(self, assets):
        self.assets = assets
        self.state = BattleState.TURN_START
        self.grid = BattleGrid()
        
        # 視覺設定
        self.cell_size = 50
        self.grid_offset_x = 50
        self.grid_offset_y = 150
        
        # 游標
        self.cursor_x = 0
        self.cursor_y = 0
        self.action_cursor = 0
        self.skill_cursor = 0
        
        # 戰鬥狀態
        self.current_turn = 0
        self.turn_order: List[Character] = []
        self.current_character: Optional[Character] = None
        self.selected_action: Optional[ActionType] = None
        self.selected_skill: Optional[Skill] = None
        self.selected_move_pos: Optional[Position] = None
        
        # 行動選單
        self.action_menu = [
            ("移動", ActionType.MOVE),
            ("技能", ActionType.SKILL),
            ("結束回合", ActionType.END_TURN)
        ]
        
        # 可移動/攻擊位置高亮
        self.valid_moves: List[Position] = []
        self.skill_range: List[Position] = []
        
        # 字體
        try:
            self.font = pygame.font.SysFont("Microsoft JhengHei", 14)
            self.big_font = pygame.font.SysFont("Microsoft JhengHei", 20)
            self.small_font = pygame.font.SysFont("Microsoft JhengHei", 12)
        except:
            self.font = pygame.font.Font(None, 14)
            self.big_font = pygame.font.Font(None, 20)
            self.small_font = pygame.font.Font(None, 12)
        
        # 顏色
        self.colors = {
            "bg": (20, 25, 35),
            "player_zone": (50, 80, 120),
            "enemy_zone": (120, 50, 50),
            "buffer_zone": (70, 70, 70),
            "grid_line": (100, 100, 120),
            "cursor": (255, 255, 100),
            "valid_move": (100, 255, 100, 100),
            "skill_range": (255, 200, 100, 100),
            "hp_bar_bg": (60, 60, 60),
            "hp_bar": (100, 200, 100),
            "mp_bar": (100, 100, 200),
            "text": (255, 255, 255),
            "selected": (255, 200, 50),
            "panel_bg": (40, 40, 50),
            "panel_border": (80, 80, 100),
            "debuff": (255, 50, 50)
        }
        
        # 載入精靈
        self.sprite_cache = {}
        self._load_sprites()
    
    def _load_sprites(self):
        """載入精靈圖像"""
        try:
            tileset_path = os.path.join("assets", "tileset_pixel.png")
            index_path = os.path.join("assets", "tileset_index_pixel.json")
            
            if os.path.exists(tileset_path) and os.path.exists(index_path):
                tileset = pygame.image.load(tileset_path).convert_alpha()
                with open(index_path, "r", encoding="utf-8") as f:
                    index = json.load(f)
                
                for name, (cx, cy) in index.items():
                    rect = pygame.Rect(cx * 64, cy * 64, 64, 64)
                    sprite = tileset.subsurface(rect).copy()
                    self.sprite_cache[name] = pygame.transform.scale(sprite, (self.cell_size, self.cell_size))
        except Exception as e:
            print(f"載入 tileset 失敗: {e}")
        
        # === 自動載入角色動畫 ===
        # 從 assets/characters/ 資料夾載入角色圖片
        characters_folder = os.path.join("assets", "characters")
        
        # 確保資料夾存在
        if not os.path.exists(characters_folder):
            try:
                os.makedirs(characters_folder)
                print(f"已創建角色資料夾: {characters_folder}")
                print("請在此資料夾放入角色圖片！")
            except:
                pass
        
        # 載入角色圖片
        if os.path.exists(characters_folder):
            # 支援的屬性名稱
            character_names = ["wind", "fire", "water", "earth", "wood", "shadow", 
                             "light", "chaos", "metal", "mist", "dream", "law"]
            
            for char_name in character_names:
                # 嘗試載入動畫幀（4幀）
                for frame in range(4):
                    # 動畫檔案名稱: wind_0.png, wind_1.png, ...
                    anim_path = os.path.join(characters_folder, f"{char_name}_{frame}.png")
                    if os.path.exists(anim_path):
                        try:
                            img = pygame.image.load(anim_path).convert_alpha()
                            img = pygame.transform.scale(img, (self.cell_size, self.cell_size))
                            cache_name = f"{char_name}_frame{frame}"
                            self.sprite_cache[cache_name] = img
                            print(f"✓ 載入動畫: {char_name} 第 {frame} 幀")
                        except Exception as e:
                            print(f"✗ 載入 {anim_path} 失敗: {e}")
                
                # 嘗試載入靜態圖片: wind.png
                static_path = os.path.join(characters_folder, f"{char_name}.png")
                if os.path.exists(static_path):
                    try:
                        img = pygame.image.load(static_path).convert_alpha()
                        img = pygame.transform.scale(img, (self.cell_size, self.cell_size))
                        # 如果有靜態圖，也作為所有幀使用
                        for frame in range(4):
                            cache_name = f"{char_name}_frame{frame}"
                            if cache_name not in self.sprite_cache:
                                self.sprite_cache[cache_name] = img
                        print(f"✓ 載入靜態圖: {char_name}")
                    except Exception as e:
                        print(f"✗ 載入 {static_path} 失敗: {e}")
        
        # 動畫系統初始化
        self.animation_frames = {}
        self.animation_timer = 0.0
        self.animation_speed = 0.1  # 每幀時間（秒）
    
    def get_character_sprite(self, char: Character, frame: int = 0) -> Optional[pygame.Surface]:
        """
        獲取角色精靈（自動支持動畫）
        
        會自動尋找：
        1. assets/characters/屬性名_0.png（動畫）
        2. assets/characters/屬性名.png（靜態）
        3. tileset 中的圖片
        4. 預設方塊
        """
        # 從角色ID提取屬性名
        char_id = char.id.lower()
        
        # 嘗試不同的命名方式
        possible_names = [
            f"{char_id}_frame{frame}",      # 例如: wind_frame0
            char_id,                         # 例如: wind
            char.sprite_name,                # tileset 名稱
            f"{char.sprite_name}_frame{frame}"
        ]
        
        for name in possible_names:
            if name in self.sprite_cache:
                return self.sprite_cache[name]
        
        # 都找不到，返回 None（會繪製預設方塊）
        return None
    
    def update_animations(self, dt: float):
        """更新動畫（在主循環中調用）"""
        self.animation_timer += dt
        
        # 每隔一段時間更新動畫幀
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0.0
            
            # 更新所有角色的動畫幀
            for char_id, current_frame in list(self.animation_frames.items()):
                # 循環 4 幀待機動畫 (0-3)
                self.animation_frames[char_id] = (current_frame + 1) % 4
    
    def start_turn(self):
        """開始新回合"""
        if not self.turn_order:
            return
        
        self.current_character = self.turn_order[self.current_turn]
        self.current_character.reset_turn()
        self.state = BattleState.CHOOSING_ACTION
        self.action_cursor = 0
        
        # 重置游標到當前角色位置
        self.cursor_x = self.current_character.position.x
        self.cursor_y = self.current_character.position.y
    
    def handle_input(self, keys_pressed, keys_just_pressed):
        """處理輸入"""
        if self.state == BattleState.TURN_START:
            self.start_turn()
        
        elif self.state == BattleState.CHOOSING_ACTION:
            self._handle_action_choice(keys_just_pressed)
        
        elif self.state == BattleState.MOVING:
            self._handle_movement(keys_just_pressed)
        
        elif self.state == BattleState.AFTER_MOVE:
            self._handle_after_move(keys_just_pressed)
        
        elif self.state == BattleState.SELECTING_SKILL:
            self._handle_skill_selection(keys_just_pressed)
        
        elif self.state == BattleState.SELECTING_TARGETS:
            self._handle_target_selection(keys_just_pressed)
    
    def _handle_action_choice(self, keys):
        """處理行動選擇"""
        import pygame
        
        if pygame.K_UP in keys:
            self.action_cursor = max(0, self.action_cursor - 1)
        elif pygame.K_DOWN in keys:
            self.action_cursor = min(len(self.action_menu) - 1, self.action_cursor + 1)
        elif pygame.K_SPACE in keys or pygame.K_RETURN in keys:
            _, action = self.action_menu[self.action_cursor]
            
            if action == ActionType.MOVE:
                if self.current_character.can_move():
                    self.selected_action = ActionType.MOVE
                    self.valid_moves = self.grid.get_valid_moves(
                        self.current_character.position, self.current_character
                    )
                    self.state = BattleState.MOVING
            
            elif action == ActionType.SKILL:
                if self.current_character.can_act() and self.current_character.skills:
                    self.state = BattleState.SELECTING_SKILL
                    self.skill_cursor = 0
            
            elif action == ActionType.END_TURN:
                self._end_turn()
        
        elif pygame.K_ESCAPE in keys:
            return "exit_battle"
    
    def _handle_movement(self, keys):
        """處理移動選擇"""
        import pygame
        
        # WASD移動游標
        if pygame.K_w in keys:
            self.cursor_y = max(0, self.cursor_y - 1)
        elif pygame.K_s in keys:
            self.cursor_y = min(self.grid.height - 1, self.cursor_y + 1)
        elif pygame.K_a in keys:
            self.cursor_x = max(0, self.cursor_x - 1)
        elif pygame.K_d in keys:
            self.cursor_x = min(self.grid.width - 1, self.cursor_x + 1)
        
        elif pygame.K_SPACE in keys or pygame.K_RETURN in keys:
            target_pos = Position(self.cursor_x, self.cursor_y)
            if target_pos in self.valid_moves:
                # 執行移動
                self.grid.move_character(self.current_character.position, target_pos)
                self.current_character.move_count += 1
                self.current_character.has_moved = True
                self.selected_move_pos = target_pos
                
                # 移動後選擇
                self.state = BattleState.AFTER_MOVE
                self.valid_moves = []
        
        elif pygame.K_ESCAPE in keys:
            self.state = BattleState.CHOOSING_ACTION
            self.valid_moves = []
    
    def _handle_after_move(self, keys):
        """處理移動後的選擇"""
        import pygame
        
        # 顯示可選項：再移動 / 使用技能 / 結束回合
        if pygame.K_1 in keys and self.current_character.can_move():
            # 再移動一次
            self.valid_moves = self.grid.get_valid_moves(
                self.current_character.position, self.current_character
            )
            self.state = BattleState.MOVING
        
        elif pygame.K_2 in keys and self.current_character.skills:
            # 使用技能
            self.state = BattleState.SELECTING_SKILL
            self.skill_cursor = 0
        
        elif pygame.K_3 in keys or pygame.K_RETURN in keys:
            # 結束回合
            self._end_turn()
    
    def _handle_skill_selection(self, keys):
        """處理技能選擇"""
        import pygame
        
        skills = self.current_character.skills
        
        if pygame.K_UP in keys:
            self.skill_cursor = max(0, self.skill_cursor - 1)
        elif pygame.K_DOWN in keys:
            self.skill_cursor = min(len(skills) - 1, self.skill_cursor + 1)
        elif pygame.K_SPACE in keys or pygame.K_RETURN in keys:
            skill = skills[self.skill_cursor]
            if skill.can_use(self.current_character, self.grid):
                self.selected_skill = skill
                self.state = BattleState.SELECTING_TARGETS
                
                # 初始化技能範圍預覽
                initial_target = Position(self.cursor_x, self.cursor_y)
                self.skill_range = self.grid.get_skill_targets(
                    self.current_character, skill, initial_target
                )
                
                # 如果是自我傳送或陣型技能，設置游標到合適位置
                if skill.skill_type == SkillType.SELF_TELEPORT:
                    print("選擇傳送目標位置")
                elif skill.skill_type == SkillType.ALLY_FORMATION:
                    print("選擇陣型中心位置")
                    
        elif pygame.K_ESCAPE in keys:
            if self.current_character.has_moved:
                self.state = BattleState.AFTER_MOVE
            else:
                self.state = BattleState.CHOOSING_ACTION
    
    def _handle_target_selection(self, keys):
        """處理目標選擇"""
        import pygame
        
        # WASD移動游標
        if pygame.K_w in keys:
            self.cursor_y = max(0, self.cursor_y - 1)
        elif pygame.K_s in keys:
            self.cursor_y = min(self.grid.height - 1, self.cursor_y + 1)
        elif pygame.K_a in keys:
            self.cursor_x = max(0, self.cursor_x - 1)
        elif pygame.K_d in keys:
            self.cursor_x = min(self.grid.width - 1, self.cursor_x + 1)
        
        # 更新技能範圍預覽
        if self.selected_skill:
            target_pos = Position(self.cursor_x, self.cursor_y)
            self.skill_range = self.grid.get_skill_targets(self.current_character, self.selected_skill, target_pos)
        
        if pygame.K_SPACE in keys or pygame.K_RETURN in keys:
            target_pos = Position(self.cursor_x, self.cursor_y)
            self._execute_skill(self.selected_skill, target_pos)
            self._end_turn()
        
        elif pygame.K_ESCAPE in keys:
            self.state = BattleState.SELECTING_SKILL
            self.selected_skill = None
            self.skill_range = []
    
    def _execute_skill(self, skill: Skill, target_pos: Position):
        """執行技能"""
        caster = self.current_character
        
        # 扣除MP
        caster.current_mp -= skill.mp_cost
        
        # 獲取受影響的位置
        affected_positions = self.grid.get_skill_targets(caster, skill, target_pos)
        
        # 根據技能類型執行效果
        if skill.skill_type in [SkillType.DAMAGE, SkillType.DAMAGE_DISPLACEMENT]:
            for pos in affected_positions:
                target = self.grid.get_character_at(pos)
                if target and target != caster:
                    # 計算傷害
                    damage = max(1, skill.damage - target.defense)
                    
                    # 如果目標在敵方領地，傷害x3
                    if target.in_enemy_territory:
                        damage *= 3
                    
                    target.current_hp = max(0, target.current_hp - damage)
                    print(f"{caster.name} 對 {target.name} 造成 {damage} 點傷害")
        
        # 執行位移效果
        if skill.skill_type in [SkillType.DISPLACEMENT, SkillType.DAMAGE_DISPLACEMENT]:
            self._apply_displacement(caster, skill, affected_positions, target_pos)
        
        # 執行自我傳送
        if skill.skill_type == SkillType.SELF_TELEPORT:
            self._apply_self_teleport(caster, target_pos)
        
        # 執行陣型變換
        if skill.skill_type == SkillType.ALLY_FORMATION:
            self._apply_formation(caster, skill, target_pos)
        
        caster.has_acted = True
    
    def _apply_displacement(self, caster: Character, skill: Skill, affected_positions: List[Position], center_pos: Position):
        """執行位移效果（各種擊退方式）"""
        for pos in affected_positions:
            target = self.grid.get_character_at(pos)
            if target and target != caster:
                # 根據技能的自定義擊退邏輯
                if skill.custom_knockback == "explosion":
                    # 爆炸：從中心向外擊退
                    direction = self._calculate_explosion_direction(center_pos, pos)
                elif skill.custom_knockback == "gravity":
                    # 重力：向下擊退
                    direction = (0, 1)
                elif skill.custom_knockback == "vortex":
                    # 漩渦：向中心拉
                    direction = self._calculate_pull_direction(center_pos, pos)
                else:
                    # 一般方向
                    if skill.displacement_direction == "away":
                        direction = self._calculate_push_direction(caster.position, pos)
                    elif skill.displacement_direction == "toward":
                        direction = self._calculate_pull_direction(caster.position, pos)
                    elif skill.displacement_direction == "down":
                        direction = (0, 1)
                    elif skill.displacement_direction == "up":
                        direction = (0, -1)
                    elif skill.displacement_direction == "left":
                        direction = (-1, 0)
                    elif skill.displacement_direction == "right":
                        direction = (1, 0)
                    else:
                        continue
                
                # 執行位移
                new_pos = self._push_character(target, pos, direction, skill.displacement_distance)
                if new_pos != pos:
                    print(f"{target.name} 被擊退到 {new_pos}")
    
    def _calculate_explosion_direction(self, center: Position, target: Position) -> Tuple[int, int]:
        """計算爆炸擊退方向（從中心向外）"""
        dx = target.x - center.x
        dy = target.y - center.y
        
        if dx == 0 and dy == 0:
            return (0, 0)
        
        # 正規化方向
        if abs(dx) > abs(dy):
            return (1 if dx > 0 else -1, 0)
        elif abs(dy) > abs(dx):
            return (0, 1 if dy > 0 else -1)
        else:
            return (1 if dx > 0 else -1, 1 if dy > 0 else -1)
    
    def _calculate_push_direction(self, from_pos: Position, to_pos: Position) -> Tuple[int, int]:
        """計算推開方向（遠離）"""
        dx = to_pos.x - from_pos.x
        dy = to_pos.y - from_pos.y
        
        # 正規化方向
        if abs(dx) > abs(dy):
            return (1 if dx > 0 else -1, 0)
        elif abs(dy) > abs(dx):
            return (0, 1 if dy > 0 else -1)
        else:
            # 對角線，選擇主要方向
            return (1 if dx > 0 else -1, 1 if dy > 0 else -1)
    
    def _calculate_pull_direction(self, from_pos: Position, to_pos: Position) -> Tuple[int, int]:
        """計算拉近方向"""
        dx, dy = self._calculate_push_direction(from_pos, to_pos)
        return (-dx, -dy)
    
    def _push_character(self, char: Character, current_pos: Position, direction: Tuple[int, int], distance: int) -> Position:
        """推動角色指定距離"""
        dx, dy = direction
        final_pos = current_pos
        
        # 逐格推動，直到撞牆或撞到其他角色
        for i in range(distance):
            new_x = final_pos.x + dx
            new_y = final_pos.y + dy
            new_pos = Position(new_x, new_y)
            
            # 檢查是否有效且未被佔用
            if not self.grid.is_valid_position(new_pos):
                break
            if self.grid.is_occupied(new_pos):
                break
            
            final_pos = new_pos
        
        # 執行移動
        if final_pos != current_pos:
            self.grid.move_character(current_pos, final_pos)
        
        return final_pos
    
    def _apply_self_teleport(self, caster: Character, target_pos: Position):
        """執行自我傳送"""
        if self.grid.is_valid_position(target_pos) and not self.grid.is_occupied(target_pos):
            self.grid.move_character(caster.position, target_pos)
            print(f"{caster.name} 傳送到 {target_pos}")
    
    def _apply_formation(self, caster: Character, skill: Skill, center_pos: Position):
        """執行陣型變換"""
        # 收集所有友軍
        allies = [char for char in self.turn_order if char.is_player == caster.is_player]
        
        if len(allies) > len(skill.formation_pattern):
            print("陣型位置不足以容納所有友軍")
            return
        
        # 計算新位置
        new_positions = []
        for dx, dy in skill.formation_pattern:
            new_pos = Position(center_pos.x + dx, center_pos.y + dy)
            if self.grid.is_valid_position(new_pos):
                new_positions.append(new_pos)
        
        # 移動友軍到新位置
        for i, ally in enumerate(allies):
            if i < len(new_positions):
                old_pos = ally.position
                new_pos = new_positions[i]
                
                # 如果目標位置被佔用，跳過
                if self.grid.is_occupied(new_pos) and new_pos != old_pos:
                    continue
                
                if old_pos != new_pos:
                    self.grid.move_character(old_pos, new_pos)
                    print(f"{ally.name} 移動到陣型位置 {new_pos}")
    
    def _end_turn(self):
        """結束回合"""
        self.current_turn = (self.current_turn + 1) % len(self.turn_order)
        self.state = BattleState.TURN_START
        
        # 檢查戰鬥是否結束
        self._check_battle_end()
    
    def _check_battle_end(self):
        """檢查戰鬥結束"""
        players_alive = any(char.current_hp > 0 for char in self.turn_order if char.is_player)
        enemies_alive = any(char.current_hp > 0 for char in self.turn_order if not char.is_player)
        
        if not players_alive or not enemies_alive:
            self.state = BattleState.BATTLE_END
    
    def draw(self, screen):
        """繪製戰鬥場景"""
        screen.fill(self.colors["bg"])
        
        # 繪製格子和領地
        self._draw_grid(screen)
        
        # 繪製角色
        self._draw_characters(screen)
        
        # 繪製UI
        self._draw_ui(screen)
        
        # 繪製游標和高亮
        self._draw_highlights(screen)
    
    def _draw_grid(self, screen):
        """繪製戰鬥格子"""
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                # 確定格子顏色（根據領地）
                pos = Position(x, y)
                territory = self.grid.get_territory(pos)
                
                if territory == Territory.PLAYER_ZONE:
                    color = self.colors["player_zone"]
                elif territory == Territory.ENEMY_ZONE:
                    color = self.colors["enemy_zone"]
                else:
                    color = self.colors["buffer_zone"]
                
                rect = pygame.Rect(
                    self.grid_offset_x + x * self.cell_size,
                    self.grid_offset_y + y * self.cell_size,
                    self.cell_size, self.cell_size
                )
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, self.colors["grid_line"], rect, 1)
        
        # 繪製領地分界線
        buffer_x = self.grid_offset_x + 6 * self.cell_size
        pygame.draw.line(screen, (255, 255, 100),
                        (buffer_x, self.grid_offset_y),
                        (buffer_x, self.grid_offset_y + self.grid.height * self.cell_size), 3)
    
    def _draw_characters(self, screen):
        """繪製角色（支持動畫）"""
        for pos, char in self.grid.characters.items():
            x = self.grid_offset_x + pos.x * self.cell_size
            y = self.grid_offset_y + pos.y * self.cell_size
            
            # 初始化角色動畫幀
            if char.id not in self.animation_frames:
                self.animation_frames[char.id] = 0
            
            # 獲取當前幀
            current_frame = self.animation_frames[char.id]
            
            # 獲取角色精靈（支持動畫）
            sprite = self.get_character_sprite(char, current_frame)
            
            if sprite:
                # 使用精靈圖像
                screen.blit(sprite, (x, y))
            else:
                # 預設：繪製彩色方塊（方便您之後替換）
                # 這裡使用簡單的方塊，您可以輕鬆替換成動畫
                color = self._get_character_color(char)
                
                # 繪製角色方塊（添加簡單動畫效果）
                offset = int(abs((current_frame - 1.5)) * 2)  # 上下浮動效果
                char_rect = pygame.Rect(x + 5, y + 5 + offset, self.cell_size - 10, self.cell_size - 10)
                pygame.draw.rect(screen, color, char_rect, border_radius=5)
                
                # 繪製角色邊框
                border_color = (255, 255, 255) if char == self.current_character else (150, 150, 150)
                pygame.draw.rect(screen, border_color, char_rect, 2, border_radius=5)
                
                # 繪製角色名稱縮寫
                name_initial = char.name[0] if char.name else "?"
                name_text = self.font.render(name_initial, True, (255, 255, 255))
                name_rect = name_text.get_rect(center=char_rect.center)
                screen.blit(name_text, name_rect)
            
            # Debuff標記
            if char.in_enemy_territory:
                pygame.draw.circle(screen, self.colors["debuff"], 
                                 (x + self.cell_size - 10, y + 10), 5)
            
            # 特殊狀態標記
            if char.is_taunting:
                # 嘲諷標記
                pygame.draw.circle(screen, (255, 200, 0), 
                                 (x + 10, y + 10), 5)
            
            if char.is_blocking_cursor:
                # 游標阻擋標記
                pygame.draw.rect(screen, (200, 100, 255), 
                               (x + self.cell_size - 15, y + self.cell_size - 15, 10, 10))
            
            # 血條
            self._draw_health_bar(screen, char, x, y - 8)
    
    def _get_character_color(self, char: Character) -> tuple:
        """根據角色屬性獲取顏色（方便識別）"""
        # 根據角色ID或名稱決定顏色
        color_map = {
            "wind": (150, 255, 200),    # 淺綠
            "fire": (255, 100, 100),    # 紅色
            "water": (100, 150, 255),   # 藍色
            "earth": (200, 150, 100),   # 棕色
            "wood": (100, 200, 100),    # 綠色
            "shadow": (100, 100, 150),  # 暗紫
            "light": (255, 255, 150),   # 亮黃
            "chaos": (200, 100, 200),   # 紫色
            "metal": (180, 180, 180),   # 灰色
            "mist": (200, 200, 255),    # 淡藍
            "dream": (255, 180, 255),   # 粉色
            "law": (255, 200, 100),     # 金色
        }
        
        # 根據角色ID找顏色
        for key, color in color_map.items():
            if key in char.id.lower():
                return color
        
        # 預設顏色
        return (100, 200, 255) if char.is_player else (255, 100, 100)
    
    def _draw_health_bar(self, screen, char, x, y):
        """繪製血條"""
        bar_width = self.cell_size - 4
        bar_height = 5
        
        bg_rect = pygame.Rect(x + 2, y, bar_width, bar_height)
        pygame.draw.rect(screen, self.colors["hp_bar_bg"], bg_rect)
        
        hp_ratio = char.current_hp / char.max_hp if char.max_hp > 0 else 0
        hp_width = int(bar_width * hp_ratio)
        if hp_width > 0:
            hp_rect = pygame.Rect(x + 2, y, hp_width, bar_height)
            pygame.draw.rect(screen, self.colors["hp_bar"], hp_rect)
    
    def _draw_highlights(self, screen):
        """繪製高亮顯示"""
        # 技能範圍預覽（選擇目標時）
        if self.skill_range:
            for pos in self.skill_range:
                x = self.grid_offset_x + pos.x * self.cell_size
                y = self.grid_offset_y + pos.y * self.cell_size
                s = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
                
                # 判斷這個位置有沒有角色，顯示不同顏色
                char = self.grid.get_character_at(pos)
                if char:
                    # 有角色的格子用紅色（會被攻擊）
                    s.fill((255, 100, 100, 120))
                else:
                    # 空格子用黃色
                    s.fill(self.colors["skill_range"])
                
                screen.blit(s, (x, y))
                
                # 範圍邊框
                pygame.draw.rect(screen, (255, 200, 100), 
                               pygame.Rect(x, y, self.cell_size, self.cell_size), 2)
        
        # 可移動位置
        for pos in self.valid_moves:
            x = self.grid_offset_x + pos.x * self.cell_size
            y = self.grid_offset_y + pos.y * self.cell_size
            s = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
            s.fill(self.colors["valid_move"])
            screen.blit(s, (x, y))
            
            # 移動範圍邊框
            pygame.draw.rect(screen, (100, 255, 100), 
                           pygame.Rect(x, y, self.cell_size, self.cell_size), 2)
        
        # 游標（最上層）
        cursor_x = self.grid_offset_x + self.cursor_x * self.cell_size
        cursor_y = self.grid_offset_y + self.cursor_y * self.cell_size
        cursor_rect = pygame.Rect(cursor_x, cursor_y, self.cell_size, self.cell_size)
        pygame.draw.rect(screen, self.colors["cursor"], cursor_rect, 4)
        
        # 游標中心點
        center_x = cursor_x + self.cell_size // 2
        center_y = cursor_y + self.cell_size // 2
        pygame.draw.circle(screen, self.colors["cursor"], (center_x, center_y), 3)
    
    def _draw_ui(self, screen):
        """繪製UI"""
        if self.state == BattleState.CHOOSING_ACTION:
            self._draw_action_menu(screen)
        elif self.state == BattleState.AFTER_MOVE:
            self._draw_after_move_menu(screen)
        elif self.state == BattleState.SELECTING_SKILL:
            self._draw_skill_menu(screen)
        
        # 當前角色信息
        self._draw_character_info(screen)
        
        # 領地說明
        self._draw_territory_info(screen)
    
    def _draw_action_menu(self, screen):
        """繪製行動選單"""
        panel_rect = pygame.Rect(WIDTH - 250, 50, 240, 120)
        pygame.draw.rect(screen, self.colors["panel_bg"], panel_rect)
        pygame.draw.rect(screen, self.colors["panel_border"], panel_rect, 2)
        
        y = panel_rect.y + 10
        for i, (name, action) in enumerate(self.action_menu):
            color = self.colors["selected"] if i == self.action_cursor else self.colors["text"]
            
            # 檢查是否可用
            if action == ActionType.MOVE and not self.current_character.can_move():
                color = (100, 100, 100)
            elif action == ActionType.SKILL and not self.current_character.can_act():
                color = (100, 100, 100)
            
            prefix = "> " if i == self.action_cursor else "  "
            text = self.font.render(f"{prefix}{name}", True, color)
            screen.blit(text, (panel_rect.x + 10, y))
            y += 30
    
    def _draw_after_move_menu(self, screen):
        """繪製移動後選單"""
        panel_rect = pygame.Rect(WIDTH - 250, 50, 240, 140)
        pygame.draw.rect(screen, self.colors["panel_bg"], panel_rect)
        pygame.draw.rect(screen, self.colors["panel_border"], panel_rect, 2)
        
        y = panel_rect.y + 10
        
        # 標題
        title = self.font.render("移動後選擇：", True, self.colors["text"])
        screen.blit(title, (panel_rect.x + 10, y))
        y += 25
        
        # 選項
        options = [
            ("1 - 再移動一格", self.current_character.can_move()),
            ("2 - 使用技能", len(self.current_character.skills) > 0),
            ("3 - 結束回合", True)
        ]
        
        for text, enabled in options:
            color = self.colors["text"] if enabled else (100, 100, 100)
            surface = self.font.render(text, True, color)
            screen.blit(surface, (panel_rect.x + 10, y))
            y += 25
    
    def _draw_skill_menu(self, screen):
        """繪製技能選單"""
        skills = self.current_character.skills
        if not skills:
            return
        
        panel_rect = pygame.Rect(WIDTH - 350, 50, 340, min(400, len(skills) * 80 + 30))
        pygame.draw.rect(screen, self.colors["panel_bg"], panel_rect)
        pygame.draw.rect(screen, self.colors["panel_border"], panel_rect, 2)
        
        y = panel_rect.y + 10
        
        for i, skill in enumerate(skills):
            selected = i == self.skill_cursor
            can_use = skill.can_use(self.current_character, self.grid)
            
            # 技能名稱
            name_color = self.colors["selected"] if selected else self.colors["text"]
            if not can_use:
                name_color = (100, 100, 100)
            
            prefix = "► " if selected else "  "
            name_text = self.font.render(f"{prefix}{skill.name}", True, name_color)
            screen.blit(name_text, (panel_rect.x + 10, y))
            y += 20
            
            # MP消耗
            mp_color = self.colors["text"] if can_use else (150, 150, 150)
            mp_text = self.small_font.render(f"MP: {skill.mp_cost}", True, mp_color)
            screen.blit(mp_text, (panel_rect.x + 10, y))
            y += 18
            
            # 技能說明
            desc_text = self.small_font.render(skill.description[:40], True, (180, 180, 180))
            screen.blit(desc_text, (panel_rect.x + 10, y))
            y += 18
            
            # 技能類型
            type_text = self.small_font.render(f"類型: {skill.skill_type.value}", True, (150, 200, 150))
            screen.blit(type_text, (panel_rect.x + 10, y))
            y += 24
    
    def _draw_character_info(self, screen):
        """繪製當前角色信息"""
        if not self.current_character:
            return
        
        panel_rect = pygame.Rect(10, HEIGHT - 120, 350, 110)
        pygame.draw.rect(screen, self.colors["panel_bg"], panel_rect)
        pygame.draw.rect(screen, self.colors["panel_border"], panel_rect, 2)
        
        char = self.current_character
        y = panel_rect.y + 10
        
        # 名稱
        name = self.big_font.render(char.name, True, self.colors["text"])
        screen.blit(name, (panel_rect.x + 10, y))
        y += 30
        
        # HP
        hp_text = f"HP: {char.current_hp}/{char.max_hp}"
        hp_surf = self.font.render(hp_text, True, self.colors["text"])
        screen.blit(hp_surf, (panel_rect.x + 10, y))
        y += 20
        
        # MP
        mp_text = f"MP: {char.current_mp}/{char.max_mp}"
        mp_surf = self.font.render(mp_text, True, self.colors["text"])
        screen.blit(mp_surf, (panel_rect.x + 10, y))
        y += 20
        
        # 狀態
        status = f"移動: {char.move_count}/2  行動: {'已使用' if char.has_acted else '可用'}"
        status_surf = self.font.render(status, True, self.colors["text"])
        screen.blit(status_surf, (panel_rect.x + 10, y))
    
    def _draw_territory_info(self, screen):
        """繪製領地說明"""
        panel_rect = pygame.Rect(10, 10, 500, 80)
        pygame.draw.rect(screen, self.colors["panel_bg"], panel_rect)
        pygame.draw.rect(screen, self.colors["panel_border"], panel_rect, 2)
        
        y = panel_rect.y + 10
        
        title = self.big_font.render("戰鬥規則", True, self.colors["text"])
        screen.blit(title, (panel_rect.x + 10, y))
        y += 25
        
        info1 = self.small_font.render("• 藍色區域：玩家陣地(7x7)  紅色區域：敵方陣地(7x7)  灰色：緩衝區", True, (200, 200, 200))
        screen.blit(info1, (panel_rect.x + 10, y))
        y += 18
        
        info2 = self.small_font.render("• 進入敵方領地：無法主動攻擊 & 受到傷害x3", True, (255, 150, 150))
        screen.blit(info2, (panel_rect.x + 10, y))


# ===== 角色選擇系統 =====

class CharacterSelectScene:
    """角色選擇場景"""
    def __init__(self, assets):
        self.assets = assets
        self.selected_indices = [0, 1, 2, 3, 4]  # 預設選擇前5個
        self.cursor = 0
        self.max_select = 5
        
        try:
            self.font = pygame.font.SysFont("Microsoft JhengHei", 18)
            self.big_font = pygame.font.SysFont("Microsoft JhengHei", 24)
        except:
            self.font = pygame.font.Font(None, 18)
            self.big_font = pygame.font.Font(None, 24)
        
        self.colors = {
            "bg": (20, 25, 35),
            "panel": (40, 40, 50),
            "selected": (100, 200, 100),
            "unselected": (60, 60, 70),
            "cursor": (255, 255, 100),
            "text": (255, 255, 255),
        }
    
    def handle_input(self, keys_just_pressed):
        """處理輸入"""
        import pygame
        
        if pygame.K_UP in keys_just_pressed:
            self.cursor = max(0, self.cursor - 1)
        elif pygame.K_DOWN in keys_just_pressed:
            self.cursor = min(len(ALL_PLAYER_CHARACTERS) - 1, self.cursor + 1)
        elif pygame.K_SPACE in keys_just_pressed:
            # 切換選擇狀態
            if self.cursor in self.selected_indices:
                self.selected_indices.remove(self.cursor)
            elif len(self.selected_indices) < self.max_select:
                self.selected_indices.append(self.cursor)
        elif pygame.K_RETURN in keys_just_pressed:
            if len(self.selected_indices) >= 1:
                return "start_battle"
        elif pygame.K_ESCAPE in keys_just_pressed:
            return "back"
    
    def draw(self, screen):
        """繪製選擇界面"""
        screen.fill(self.colors["bg"])
        
        # 標題
        title = self.big_font.render("選擇出戰角色 (最多5個)", True, self.colors["text"])
        screen.blit(title, (50, 30))
        
        # 操作提示
        hint = self.font.render("↑↓選擇  空白切換  Enter確認  ESC返回", True, (200, 200, 200))
        screen.blit(hint, (50, 70))
        
        # 角色列表
        y = 120
        for i, char in enumerate(ALL_PLAYER_CHARACTERS):
            is_selected = i in self.selected_indices
            is_cursor = i == self.cursor
            
            # 背景
            bg_color = self.colors["selected"] if is_selected else self.colors["unselected"]
            panel_rect = pygame.Rect(50, y, 400, 50)
            pygame.draw.rect(screen, bg_color, panel_rect)
            
            if is_cursor:
                pygame.draw.rect(screen, self.colors["cursor"], panel_rect, 3)
            
            # 角色信息
            prefix = "✓ " if is_selected else "  "
            name_text = self.font.render(f"{prefix}{char.name}", True, self.colors["text"])
            screen.blit(name_text, (60, y + 5))
            
            stats_text = self.font.render(
                f"HP:{char.max_hp} MP:{char.max_mp} 攻:{char.attack} 防:{char.defense} 速:{char.speed}",
                True, (220, 220, 220)
            )
            screen.blit(stats_text, (60, y + 28))
            
            y += 60
        
        # 已選擇數量
        count_text = self.big_font.render(
            f"已選擇: {len(self.selected_indices)}/{self.max_select}",
            True, self.colors["cursor"]
        )
        screen.blit(count_text, (500, 120))


def build_with_selection(assets, selected_indices=None):
    """根據選擇構建戰鬥（可從外部調用）"""
    if selected_indices is None:
        selected_indices = [0, 1, 2, 3, 4]
    
    scene = TacticalBattleScene(assets)
    
    # 根據選擇的索引創建隊伍
    import copy
    start_positions = [
        Position(2, 2), Position(3, 3), Position(2, 4),
        Position(1, 3), Position(3, 2),
    ]
    
    player_team = []
    for i, idx in enumerate(selected_indices[:5]):
        char = copy.deepcopy(ALL_PLAYER_CHARACTERS[idx])
        char.position = start_positions[i]
        player_team.append(char)
    
    # 敵方隊伍
    enemy_positions = [
        Position(11, 2), Position(12, 3), Position(11, 4),
        Position(10, 3), Position(12, 2),
    ]
    
    enemy_templates = [FIRE_CHARACTER, EARTH_CHARACTER, SHADOW_CHARACTER, CHAOS_CHARACTER, METAL_CHARACTER]
    enemy_team = []
    for i, char_template in enumerate(enemy_templates[:5]):
        char = copy.deepcopy(char_template)
        char.position = enemy_positions[i]
        char.is_player = False
        char.name = f"敵{char.name}"
        enemy_team.append(char)
    
    # 放置角色
    for char in player_team:
        scene.grid.characters[char.position] = char
    for char in enemy_team:
        scene.grid.characters[char.position] = char
    
    # 回合順序
    all_chars = player_team + enemy_team
    scene.turn_order = sorted(all_chars, key=lambda c: c.speed, reverse=True)
    
    return scene


# ===== 十二屬性角色設計 =====

# 風屬性角色
WIND_CHARACTER = Character(
    "wind", "風行者", 90, 90, 60, 60, 22, 8, 20,
    Position(2, 3), "npc_r0_c0",
    [
        Skill("wind_blade", "風刃斬", "高速連續攻擊，擊退敵人", 
              mp_cost=8, skill_type=SkillType.DAMAGE_DISPLACEMENT, range_type=SkillRange.LINE,
              damage=18, displacement_distance=1, displacement_direction="away", 
              range_distance=5, icon_name="battle_r0_c0"),
        Skill("gale_step", "疾風步", "瞬移到遠處", 
              mp_cost=10, skill_type=SkillType.SELF_TELEPORT, range_type=SkillRange.CUSTOM,
              range_distance=6, icon_name="battle_r0_c1"),
    ], True
)

# 火屬性角色
FIRE_CHARACTER = Character(
    "fire", "炎術士", 85, 85, 70, 70, 32, 6, 12,
    Position(3, 3), "npc_r0_c1",
    [
        Skill("inferno", "地獄烈焰", "大範圍火焰攻擊", 
              mp_cost=18, skill_type=SkillType.DAMAGE, range_type=SkillRange.AREA,
              damage=40, range_distance=5, effect_area=2, icon_name="battle_r0_c2"),
        Skill("fire_wall", "火牆術", "十字形火焰障壁", 
              mp_cost=12, skill_type=SkillType.DAMAGE, range_type=SkillRange.CROSS,
              damage=28, range_distance=4, effect_area=2, icon_name="battle_r0_c3"),
    ], True
)

# 水屬性角色
WATER_CHARACTER = Character(
    "water", "水之賢者", 110, 110, 55, 55, 20, 12, 14,
    Position(1, 3), "npc_r0_c2",
    [
        Skill("tidal_wave", "潮汐波", "水流衝擊，擊退大範圍敵人", 
              mp_cost=15, skill_type=SkillType.DAMAGE_DISPLACEMENT, range_type=SkillRange.AREA,
              damage=22, displacement_distance=2, displacement_direction="away",
              range_distance=4, effect_area=2, icon_name="battle_r1_c0"),
        Skill("water_prison", "水牢術", "拉近敵人困住", 
              mp_cost=12, skill_type=SkillType.DISPLACEMENT, range_type=SkillRange.SINGLE,
              displacement_distance=3, displacement_direction="toward",
              range_distance=5, icon_name="battle_r1_c1"),
    ], True
)

# 土屬性角色
EARTH_CHARACTER = Character(
    "earth", "大地守衛", 140, 140, 40, 40, 25, 20, 8,
    Position(2, 2), "npc_r1_c2",
    [
        Skill("earthquake", "地震波", "震退周圍所有敵人", 
              mp_cost=14, skill_type=SkillType.DAMAGE_DISPLACEMENT, range_type=SkillRange.AREA,
              damage=20, displacement_distance=2, displacement_direction="away",
              range_distance=3, effect_area=1, icon_name="battle_r1_c3"),
        Skill("earth_spike", "岩刺穿", "直線穿刺攻擊", 
              mp_cost=10, skill_type=SkillType.DAMAGE, range_type=SkillRange.LINE,
              damage=35, range_distance=6, icon_name="battle_r1_c4"),
    ], True
)

# 木屬性角色
WOOD_CHARACTER = Character(
    "wood", "森林守護者", 105, 105, 50, 50, 18, 15, 13,
    Position(3, 4), "npc_r2_c0",
    [
        Skill("vine_bind", "藤蔓纏繞", "拉近並困住敵人", 
              mp_cost=11, skill_type=SkillType.DISPLACEMENT, range_type=SkillRange.CROSS,
              displacement_distance=2, displacement_direction="toward",
              range_distance=5, effect_area=1, icon_name="battle_r2_c1"),
        Skill("nature_wrath", "自然之怒", "範圍攻擊", 
              mp_cost=13, skill_type=SkillType.DAMAGE, range_type=SkillRange.AREA,
              damage=26, range_distance=4, effect_area=2, icon_name="battle_r2_c2"),
    ], True
)

# 陰屬性角色
SHADOW_CHARACTER = Character(
    "shadow", "暗影刺客", 80, 80, 65, 65, 35, 5, 18,
    Position(1, 2), "npc_r2_c3",
    [
        Skill("shadow_strike", "暗影突襲", "傳送到敵人身後攻擊", 
              mp_cost=12, skill_type=SkillType.SELF_TELEPORT, range_type=SkillRange.CUSTOM,
              range_distance=7, icon_name="battle_r2_c4"),
        Skill("dark_pulse", "暗黑脈衝", "十字暗能量", 
              mp_cost=10, skill_type=SkillType.DAMAGE, range_type=SkillRange.CROSS,
              damage=30, range_distance=5, effect_area=1, icon_name="battle_r3_c0"),
    ], True
)

# 光屬性角色
LIGHT_CHARACTER = Character(
    "light", "聖光使者", 95, 95, 75, 75, 28, 10, 15,
    Position(2, 4), "npc_r3_c1",
    [
        Skill("divine_beam", "神聖光束", "穿透直線攻擊", 
              mp_cost=13, skill_type=SkillType.DAMAGE, range_type=SkillRange.LINE,
              damage=32, range_distance=7, icon_name="battle_r3_c2"),
        Skill("light_formation", "光之陣", "重組友軍為防禦陣型", 
              mp_cost=18, skill_type=SkillType.ALLY_FORMATION, range_type=SkillRange.ALL_ALLIES,
              formation_pattern=[(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)],
              icon_name="battle_r3_c3"),
    ], True
)

# 混沌屬性角色
CHAOS_CHARACTER = Character(
    "chaos", "混沌魔導師", 88, 88, 80, 80, 30, 7, 11,
    Position(3, 2), "npc_r3_c4",
    [
        Skill("chaos_explosion", "混沌爆發", "隨機範圍大爆炸", 
              mp_cost=20, skill_type=SkillType.DAMAGE, range_type=SkillRange.AREA,
              damage=45, range_distance=6, effect_area=3, icon_name="battle_r4_c0"),
        Skill("void_swap", "虛空置換", "與目標位置互換", 
              mp_cost=15, skill_type=SkillType.SELF_TELEPORT, range_type=SkillRange.CUSTOM,
              range_distance=8, icon_name="battle_r4_c1"),
    ], True
)

# 金屬性角色
METAL_CHARACTER = Character(
    "metal", "鋼鐵戰士", 125, 125, 45, 45, 30, 18, 10,
    Position(1, 4), "npc_r4_c2",
    [
        Skill("metal_storm", "金屬風暴", "周圍範圍攻擊並擊退", 
              mp_cost=14, skill_type=SkillType.DAMAGE_DISPLACEMENT, range_type=SkillRange.AREA,
              damage=25, displacement_distance=1, displacement_direction="away",
              range_distance=3, effect_area=1, icon_name="battle_r4_c3"),
        Skill("iron_spear", "鐵矛貫穿", "強力直線攻擊", 
              mp_cost=11, skill_type=SkillType.DAMAGE, range_type=SkillRange.LINE,
              damage=38, range_distance=5, icon_name="battle_r4_c4"),
    ], True
)

# 霧屬性角色
MIST_CHARACTER = Character(
    "mist", "迷霧行者", 82, 82, 68, 68, 20, 9, 17,
    Position(2, 5), "npc_r5_c0",
    [
        Skill("mist_veil", "迷霧帷幕", "籠罩大範圍，輕微傷害", 
              mp_cost=12, skill_type=SkillType.DAMAGE, range_type=SkillRange.AREA,
              damage=15, range_distance=6, effect_area=3, icon_name="battle_r5_c1"),
        Skill("phantom_step", "幻影步", "多段瞬移", 
              mp_cost=10, skill_type=SkillType.SELF_TELEPORT, range_type=SkillRange.CUSTOM,
              range_distance=5, icon_name="battle_r5_c2"),
    ], True
)

# 夢屬性角色
DREAM_CHARACTER = Character(
    "dream", "夢境編織者", 92, 92, 85, 85, 24, 8, 14,
    Position(3, 5), "npc_r5_c3",
    [
        Skill("dream_shatter", "碎夢", "對單體造成巨大傷害", 
              mp_cost=16, skill_type=SkillType.DAMAGE, range_type=SkillRange.SINGLE,
              damage=50, range_distance=6, icon_name="battle_r5_c4"),
        Skill("nightmare_swap", "夢魘置換", "改變友軍陣型", 
              mp_cost=17, skill_type=SkillType.ALLY_FORMATION, range_type=SkillRange.ALL_ALLIES,
              formation_pattern=[(-1, -1), (1, -1), (0, 0), (-1, 1), (1, 1)],
              icon_name="battle_r6_c0"),
    ], True
)

# 律屬性角色
LAW_CHARACTER = Character(
    "law", "秩序執行者", 115, 115, 60, 60, 26, 14, 12,
    Position(1, 5), "npc_r6_c1",
    [
        Skill("judgment_ray", "裁決之光", "十字審判", 
              mp_cost=14, skill_type=SkillType.DAMAGE, range_type=SkillRange.CROSS,
              damage=28, range_distance=6, effect_area=2, icon_name="battle_r6_c2"),
        Skill("order_formation", "秩序陣型", "整齊排列友軍", 
              mp_cost=15, skill_type=SkillType.ALLY_FORMATION, range_type=SkillRange.ALL_ALLIES,
              formation_pattern=[(0, 0), (1, 0), (2, 0), (0, 1), (1, 1)],
              icon_name="battle_r6_c3"),
    ], True
)

# 所有可選角色列表
ALL_PLAYER_CHARACTERS = [
    WIND_CHARACTER,
    FIRE_CHARACTER,
    WATER_CHARACTER,
    EARTH_CHARACTER,
    WOOD_CHARACTER,
    SHADOW_CHARACTER,
    LIGHT_CHARACTER,
    CHAOS_CHARACTER,
    METAL_CHARACTER,
    MIST_CHARACTER,
    DREAM_CHARACTER,
    LAW_CHARACTER,
]
    # 傷害技能
[    Skill(
        "fire_blast", "火焰爆破", "範圍火焰攻擊，對範圍內敵人造成傷害",
        mp_cost=10, skill_type=SkillType.DAMAGE, range_type=SkillRange.AREA,
        damage=30, range_distance=5, effect_area=2, icon_name="battle_r0_c0"
    ),
    
    # 傷害+位移技能
    Skill(
        "shockwave", "衝擊波", "造成傷害並擊退敵人",
        mp_cost=15, skill_type=SkillType.DAMAGE_DISPLACEMENT, range_type=SkillRange.CROSS,
        damage=25, displacement_distance=2, displacement_direction="away",
        range_distance=4, effect_area=1, icon_name="battle_r0_c1"
    ),
    
    # 純位移技能
    Skill(
        "force_push", "力場推動", "將範圍內所有單位推開",
        mp_cost=12, skill_type=SkillType.DISPLACEMENT, range_type=SkillRange.AREA,
        displacement_distance=3, displacement_direction="away",
        range_distance=3, effect_area=2, icon_name="battle_r0_c2"
    ),
    
    # 自我傳送
    Skill(
        "teleport", "瞬間移動", "傳送到指定位置",
        mp_cost=8, skill_type=SkillType.SELF_TELEPORT, range_type=SkillRange.CUSTOM,
        range_distance=5, icon_name="battle_r0_c3"
    ),
    
    # 陣型變換
    Skill(
        "formation_v", "V字陣型", "將己方重組為V字陣型",
        mp_cost=20, skill_type=SkillType.ALLY_FORMATION, range_type=SkillRange.ALL_ALLIES,
        formation_pattern=[(-1, 1), (0, 0), (1, 1), (-1, -1), (1, -1)],
        icon_name="battle_r0_c4"
    ),
    
    # 直線穿刺
    Skill(
        "pierce", "穿刺攻擊", "直線貫穿傷害",
        mp_cost=8, skill_type=SkillType.DAMAGE, range_type=SkillRange.LINE,
        damage=20, range_distance=6, icon_name="battle_r1_c0"
    ),
]


# 場景構建函數
def build(assets):
    """構建戰術戰鬥場景"""
    scene = TacticalBattleScene(assets)
    
    # 從12個角色中選擇5個（可自定義選擇邏輯）
    # 這裡先用前5個作為預設隊伍
    import random
    selected_characters = random.sample(ALL_PLAYER_CHARACTERS, 5)
    
    # 設置初始位置（分散在我方陣地）
    start_positions = [
        Position(2, 2),
        Position(3, 3),
        Position(2, 4),
        Position(1, 3),
        Position(3, 2),
    ]
    
    player_team = []
    for i, char_template in enumerate(selected_characters):
        # 深拷貝角色並設置位置
        import copy
        char = copy.deepcopy(char_template)
        char.position = start_positions[i]
        player_team.append(char)
    
    # 創建敵方隊伍（使用部分角色作為敵人）
    enemy_positions = [
        Position(11, 2),
        Position(12, 3),
        Position(11, 4),
        Position(10, 3),
        Position(12, 2),
    ]
    
    enemy_team = []
    # 選擇一些角色作為敵人（修改為敵方）
    enemy_templates = [FIRE_CHARACTER, EARTH_CHARACTER, SHADOW_CHARACTER, CHAOS_CHARACTER, METAL_CHARACTER]
    for i, char_template in enumerate(enemy_templates[:5]):
        import copy
        char = copy.deepcopy(char_template)
        char.position = enemy_positions[i]
        char.is_player = False
        char.name = f"敵{char.name}"
        enemy_team.append(char)
    
    # 放置角色
    for char in player_team:
        scene.grid.characters[char.position] = char
    
    for char in enemy_team:
        scene.grid.characters[char.position] = char
    
    # 設定回合順序（依速度排序）
    all_chars = player_team + enemy_team
    scene.turn_order = sorted(all_chars, key=lambda c: c.speed, reverse=True)
    
    return scene


def loop(screen, state, assets):
    """戰鬥場景主循環"""
    scene = state["scenes"]["battle_grid"]
    
    # 處理輸入
    keys_pressed = pygame.key.get_pressed()
    keys_just_pressed = []
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            keys_just_pressed.append(event.key)
    
    result = scene.handle_input(keys_pressed, keys_just_pressed)
    
    # 退出戰鬥
    if result == "exit_battle":
        state["current"] = "mind_hub"
        return
    
    # 更新動畫（重要！）
    scene.update_animations(1/60)  # 假設60 FPS
    
    # 檢查戰鬥結束
    if scene.state == BattleState.BATTLE_END:
        players_alive = any(c.current_hp > 0 for c in scene.turn_order if c.is_player)
        if players_alive:
            print("玩家勝利！")
        else:
            print("玩家失敗！")
        state["current"] = "mind_hub"
        return
    
    # 繪製
    scene.draw(screen)
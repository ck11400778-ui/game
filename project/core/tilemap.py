import random
from core.config import TILE

class TileMap:
    def __init__(self, cols, rows, assets, seed=1234, wall_ratio=0.06,
                 safe_areas=None, path_pairs=None):
        """
        safe_areas: list of (x,y,w,h) rectangles to force-clear
        path_pairs: list of ((sx,sy),(tx,ty)) pairs; will carve a Manhattan path
        """
        self.cols = cols; self.rows = rows
        self.width = cols*TILE; self.height = rows*TILE
        self.grid = [[0 for _ in range(cols)] for _ in range(rows)]
        self.assets = assets
        self.seed = seed
        self.wall_ratio = wall_ratio
        self.safe_areas = safe_areas or []
        self.path_pairs = path_pairs or []
        self._make()

    def _make(self):
        rnd = random.Random(self.seed)
        # 1) outer walls
        for r in range(self.rows):
            for c in range(self.cols):
                self.grid[r][c] = 1 if (r in (0,self.rows-1) or c in (0,self.cols-1)) else 0
        # 2) scatter walls
        for _ in range(int(self.cols*self.rows*self.wall_ratio)):
            r = rnd.randrange(1, self.rows-1)
            c = rnd.randrange(1, self.cols-1)
            self.grid[r][c] = 1
        # 3) clear safe rectangles
        for (x,y,w,h) in self.safe_areas:
            for r in range(y, y+h):
                for c in range(x, x+w):
                    if 0 <= r < self.rows and 0 <= c < self.cols:
                        self.grid[r][c] = 0
        # 4) carve Manhattan paths between given points (guaranteed connectivity)
        for (sx,sy),(tx,ty) in self.path_pairs:
            x, y = sx, sy
            self.grid[y][x] = 0
            while x != tx:
                x += 1 if tx > x else -1
                self.grid[y][x] = 0
            while y != ty:
                y += 1 if ty > y else -1
                self.grid[y][x] = 0

    def is_blocked(self, tx, ty):
        if tx<0 or ty<0 or tx>=self.cols or ty>=self.rows: return True
        return self.grid[ty][tx]==1

    def draw(self, surface, camera):
        start_c = max(0, camera.x // TILE)
        start_r = max(0, camera.y // TILE)
        end_c = min(self.cols, (camera.x + camera.w)//TILE + 2)
        end_r = min(self.rows, (camera.y + camera.h)//TILE + 2)
        grass = self.assets["tile_grass"]; wall = self.assets["tile_wall"]
        for r in range(start_r, end_r):
            for c in range(start_c, end_c):
                img = grass if self.grid[r][c]==0 else wall
                surface.blit(img, (c*TILE - camera.x, r*TILE - camera.y))

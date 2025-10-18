class Camera:
    def __init__(self, w, h):
        self.x = 0; self.y = 0; self.w = w; self.h = h
    def follow(self, rect, world_w, world_h):
        self.x = int(rect.centerx - self.w/2)
        self.y = int(rect.centery - self.h/2)
        self.x = max(0, min(self.x, world_w - self.w))
        self.y = max(0, min(self.y, world_h - self.h))

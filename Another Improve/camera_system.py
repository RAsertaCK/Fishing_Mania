class Camera:
    def __init__(self):
        self.offset_y = 0
        self.mode = "explore"  # or "minigame"
        self.follow_target = 0  # Y-coordinate that will be followed

    def set_mode(self, mode):
        self.mode = mode

    def update(self, target_y):
        if self.mode == "minigame":
            # Camera follows the fishing rod, giving distance upwards
            self.offset_y = max(0, int(target_y - 200))
        else:
            self.offset_y = 0

    def apply(self, pos):
        x, y = pos
        return (x, y - self.offset_y)

    def apply_rect(self, rect):
        return rect.move(0, -self.offset_y)

    def get_offset_y(self):
        return self.offset_y
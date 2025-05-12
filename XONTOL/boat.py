from config import Config
import os
import pygame

class Boat:
    UPGRADE_LEVELS = {
        "speed": [200, 250, 300, 400, 500],
        "capacity": [10, 15, 20, 30, 50],
        "sonar": [0, 1, 2, 3]
    }

    def __init__(self, game_map):
        self.game_map = game_map
        self.type = game_map.name.lower()
        self.base_image = Config.load_image(os.path.join(Config.BOAT_PATH, f"boat_{self.type}.png"), 0.7)
        self.upgrades = {"speed": 0, "capacity": 0, "sonar": 0}
        self.speed = self.UPGRADE_LEVELS["speed"][0]
        self.rect = self.base_image.get_rect(midbottom=(Config.SCREEN_WIDTH//2, Config.SCREEN_HEIGHT-50))

    def get_upgrade_cost(self, upgrade_type):
        level = self.upgrades[upgrade_type]
        if level >= len(self.UPGRADE_LEVELS[upgrade_type]) - 1:
            return None
        return (level + 1) * 100

    def upgrade(self, upgrade_type):
        cost = self.get_upgrade_cost(upgrade_type)
        if cost is None:
            return False
        self.upgrades[upgrade_type] += 1
        if upgrade_type == "speed":
            self.speed = self.UPGRADE_LEVELS["speed"][self.upgrades[upgrade_type]]
        return True

    def update(self, dt, keys):
        move = self.speed * dt
        if keys[pygame.K_LEFT]: self.rect.x -= move
        if keys[pygame.K_RIGHT]: self.rect.x += move
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(Config.SCREEN_WIDTH, self.rect.right)

    def render(self, surface):
        surface.blit(self.base_image, self.rect)

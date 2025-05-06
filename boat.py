# boat.py
from config import Config
import os
import pygame

class Boat:
    UPGRADE_LEVELS = {
        "speed": [200, 250, 300, 400, 500],
        "capacity": [10, 15, 20, 30, 50],
        "sonar": [0, 1, 2, 3]  # Sonar levels
    }
    
    def __init__(self, game_map):
        self.game_map = game_map
        self.type = game_map.name.lower()
        
        # Load boat sprite based on location
        self.base_image = Config.load_image(
            os.path.join(Config.BOAT_PATH, f"boat_{self.type}.png"), 
            scale=0.7
        )
        
        # Upgrades
        self.upgrades = {
            "speed": 0,
            "capacity": 0,
            "sonar": 0
        }
        
        self.rect = self.base_image.get_rect(
            midbottom=(Config.SCREEN_WIDTH//2, Config.SCREEN_HEIGHT-50)
        )
        self.speed = self.UPGRADE_LEVELS["speed"][0]
        self.fish_hold = []
        
    def get_upgrade_cost(self, type):
        current_level = self.upgrades[type]
        if current_level >= len(self.UPGRADE_LEVELS[type]) - 1:
            return None  # Max level
        
        return (current_level + 1) * 100  # 100, 200, 300...
        
    def upgrade(self, type):
        cost = self.get_upgrade_cost(type)
        if cost is None:
            return False
            
        self.upgrades[type] += 1
        if type == "speed":
            self.speed = self.UPGRADE_LEVELS["speed"][self.upgrades[type]]
            
        return True
        
    def update(self, dt, keys):
        # Movement
        move_amount = self.speed * dt
        
        if keys[pygame.K_LEFT]:
            self.rect.x -= move_amount
        if keys[pygame.K_RIGHT]:
            self.rect.x += move_amount
            
        # Keep within screen bounds
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(Config.SCREEN_WIDTH, self.rect.right)
        
    def render(self, surface):
        surface.blit(self.base_image, self.rect)
        
        # Render upgrades visually
        if self.upgrades["sonar"] > 0:
            sonar_img = Config.load_image(
                os.path.join(Config.UI_PATH, "sonar.png"),
                scale=0.5
            )
            surface.blit(sonar_img, (self.rect.right-30, self.rect.top-20))
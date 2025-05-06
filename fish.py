# fish.py
import pygame
import random
import os
import math
from config import Config

class Fish:
    RARITY_COLORS = {
        "common": Config.COLORS["common"],
        "rare": Config.COLORS["rare"],
        "legendary": Config.COLORS["legendary"]
    }
    
    def __init__(self, fish_data, pos):
        self.name = fish_data["name"]
        self.rarity = fish_data["rarity"]
        self.value = fish_data["value"]
        self.pos = list(pos)
        
        # Load appropriate fish image based on rarity
        fish_filename = f"fish_{self.rarity}_{self.name.lower().replace(' ', '_')}.png"
        self.image = Config.load_image(os.path.join(Config.FISH_PATH, fish_filename), 0.5)
        
        # Animation properties
        self.swim_speed = random.uniform(20, 80)
        self.swim_direction = random.choice([-1, 1])
        self.wobble_amount = random.uniform(0.5, 2.0)
        self.wobble_speed = random.uniform(0.5, 1.5)
        self.time = 0
        
        # Fishing properties
        self.escape_chance = {
            "common": 0.1,
            "rare": 0.3,
            "legendary": 0.5
        }[self.rarity]
        
        self.rect = self.image.get_rect(center=pos)
        self.caught = False
        
    def update(self, dt):
        self.time += dt
        
        if not self.caught:
            # Natural swimming movement
            self.pos[0] += self.swim_direction * self.swim_speed * dt
            self.pos[1] += math.sin(self.time * self.wobble_speed) * self.wobble_amount
            
            # Random direction change
            if random.random() < 0.01:
                self.swim_direction *= -1
        else:
            # Hooked movement - struggling!
            self.pos[1] -= 50 * dt  # Move upward
            if random.random() < self.escape_chance * dt:
                return "escaped"
                
        self.rect.center = self.pos
        return None
        
    def render(self, surface):
        # Flip image based on direction
        if self.swim_direction < 0:
            img = pygame.transform.flip(self.image, True, False)
        else:
            img = self.image
            
        # Add rarity border if legendary
        if self.rarity == "legendary":
            pygame.draw.rect(surface, self.RARITY_COLORS[self.rarity], 
                           self.rect.inflate(10, 10), 2)
            
        surface.blit(img, self.rect)
        
        # Debug info
        if Config.DEBUG:
            pygame.draw.rect(surface, (255, 0, 0), self.rect, 1)
            font = pygame.font.SysFont(None, 20)
            text = font.render(f"{self.name}", True, (255, 255, 255))
            surface.blit(text, self.rect.bottomleft)
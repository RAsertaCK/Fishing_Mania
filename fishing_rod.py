# fishing_rod.py
import pygame
from config import Config
import random
import math
import os
from fish import Fish  # Import the Fish class from the fish module

class FishingRod:
    def __init__(self, player):
        self.player = player
        self.cast_distance = 0
        self.max_cast = 300
        self.cast_speed = 150
        self.reel_speed = 200
        self.state = "idle"  # idle, casting, reeling, hooked
        
        # Visual components
        self.rod_img = Config.load_image(
            os.path.join(Config.ASSET_PATH, "fishing_rod.png"),
            scale=0.5
        )
        self.line_start = (0, 0)
        self.line_end = (0, 0)
        self.hook_pos = (0, 0)
        
        # Fishing spot
        self.fish_spot = None
        self.current_fish = None
        
    def update(self, dt, keys):
        # Update based on state
        if self.state == "casting":
            self.cast_distance += self.cast_speed * dt
            if self.cast_distance >= self.max_cast:
                self.cast_distance = self.max_cast
                self.find_fishing_spot()
                
        elif self.state == "reeling":
            self.cast_distance -= self.reel_speed * dt
            if self.cast_distance <= 0:
                self.cast_distance = 0
                self.state = "idle"
                
        elif self.state == "hooked" and self.current_fish:
            result = self.current_fish.update(dt)
            if result == "escaped":
                self.state = "reeling"
                self.current_fish = None
                return "fish_escaped"
                
        # Update positions
        self.line_start = (
            self.player.rect.centerx,
            self.player.rect.bottom - 10
        )
        
        angle = math.radians(30)  # 30 degree cast angle
        self.line_end = (
            self.line_start[0] + math.sin(angle) * self.cast_distance,
            self.line_start[1] + math.cos(angle) * self.cast_distance
        )
        
        self.hook_pos = self.line_end
        
    def find_fishing_spot(self):
        # Check if we found a fish
        if random.random() < 0.3:  # 30% chance to find a spot
            self.state = "hooked"
            fish_data = self.player.game_map.get_random_fish()
            self.current_fish = Fish(fish_data, self.hook_pos)
            return "fish_hooked"
        else:
            self.state = "reeling"
            return "nothing_caught"
            
    def render(self, surface):
        # Draw fishing line
        pygame.draw.line(
            surface, 
            (200, 200, 200), 
            self.line_start, 
            self.line_end, 
            2
        )
        
        # Draw hook
        pygame.draw.circle(surface, (100, 100, 100), self.hook_pos, 5)
        
        # Draw fish if hooked
        if self.state == "hooked" and self.current_fish:
            self.current_fish.render(surface)
import pygame
import random
import os
import math
from config import Config

class Fish:
    RARITY_COLORS = Config.COLORS

    def __init__(self, fish_data, pos):
        self.name = fish_data["name"]
        self.rarity = fish_data["rarity"]
        self.value = fish_data["value"]
        self.pos = list(pos)
        filename = f"fish_{self.rarity}_{self.name.lower().replace(' ', '_')}.png"
        self.image = Config.load_image(os.path.join(Config.FISH_PATH, filename), 0.5)
        self.swim_speed = random.uniform(20, 80)
        self.swim_direction = random.choice([-1, 1])
        self.wobble_amount = random.uniform(0.5, 2.0)
        self.wobble_speed = random.uniform(0.5, 1.5)
        self.time = 0
        self.escape_chance = {"common": 0.1, "rare": 0.3, "legendary": 0.5}[self.rarity]
        self.rect = self.image.get_rect(center=pos)
        self.caught = False

    def update(self, dt):
        self.time += dt
        if not self.caught:
            self.pos[0] += self.swim_direction * self.swim_speed * dt
            self.pos[1] += math.sin(self.time * self.wobble_speed) * self.wobble_amount
            if random.random() < 0.01:
                self.swim_direction *= -1
        else:
            self.pos[1] -= 50 * dt
            if random.random() < self.escape_chance * dt:
                return "escaped"
        self.rect.center = self.pos
        return None

    def render(self, surface):
        img = pygame.transform.flip(self.image, True, False) if self.swim_direction < 0 else self.image
        surface.blit(img, self.rect)
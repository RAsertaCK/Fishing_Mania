import pygame
import random
from fish import Fish

class FishingSystem:
    def __init__(self, player):
        self.player = player
        self.state = "idle"
        self.depth = 0
        self.max_depth = 300
        self.speed = 200
        self.fish = None
        self.line_color = (180, 180, 180)

    def update(self, dt, keys):
        if self.state == "casting":
            self.depth += self.speed * dt
            if self.depth >= self.max_depth:
                self.depth = self.max_depth
                self.try_hook_fish()
        elif self.state == "reeling":
            self.depth -= self.speed * dt
            if self.depth <= 0:
                self.depth = 0
                self.state = "idle"

        if self.fish:
            result = self.fish.update(dt)
            if result == "escaped":
                self.fish = None
                self.state = "reeling"

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
            if self.state == "idle":
                self.state = "casting"
        elif event.type == pygame.KEYUP and event.key == pygame.K_DOWN:
            if self.state == "casting":
                self.state = "reeling"

    def try_hook_fish(self):
        if random.random() < 0.3:
            fish_data = self.player.boat.game_map.get_random_fish()
            if fish_data:
                self.fish = Fish(fish_data, self.get_hook_pos())
                self.fish.caught = True
                self.state = "reeling"
        else:
            self.state = "reeling"

    def get_hook_pos(self):
        return (self.player.rect.centerx, self.player.rect.bottom + self.depth)

    def render(self, screen):
        start = (self.player.rect.centerx, self.player.rect.bottom)
        end = (self.player.rect.centerx, self.player.rect.bottom + self.depth)
        pygame.draw.line(screen, self.line_color, start, end, 2)
        pygame.draw.circle(screen, (100, 100, 100), end, 5)
        if self.fish:
            self.fish.render(screen)
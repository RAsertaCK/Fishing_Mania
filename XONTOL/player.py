import pygame
from config import Config
from fishing_system import FishingSystem

class Player:
    def __init__(self, boat, game):
        self.boat = boat
        self.game = game
        self.image = Config.load_image("sprites/player.png", 0.7)
        self.rect = self.image.get_rect(midbottom=boat.rect.midtop)
        self.fishing = FishingSystem(self)

    def update(self, dt, keys):
        self.rect.centerx = self.boat.rect.centerx
        self.fishing.update(dt, keys)
        if self.fishing.fish and self.fishing.depth <= 10:
            self.game.inventory.add(self.fishing.fish)
            self.game.wallet += self.fishing.fish.value
            self.fishing.fish = None

    def handle_event(self, event):
        self.fishing.handle_event(event)

    def render(self, screen):
        screen.blit(self.image, self.rect)
        self.fishing.render(screen)

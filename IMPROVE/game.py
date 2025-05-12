import pygame
from config import Config
from boat import Boat
from player import Player
from inventory import Inventory
from market import MarketMenu

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.state = "playing"
        self.wallet = 50

        # dummy map with name attribute
        class DummyMap:
            def __init__(self):
                self.name = "Coast"

            def get_random_fish(self):
                import random
                return random.choice([
                    {"name": "Sea Bass", "rarity": "common", "value": 10},
                    {"name": "Tuna", "rarity": "rare", "value": 40},
                    {"name": "Shark", "rarity": "legendary", "value": 200}
                ])

        self.map = DummyMap()
        self.boat = Boat(self.map)
        self.player = Player(self.boat, self)
        self.inventory = Inventory()
        self.market_menu = MarketMenu(self)

    def set_state(self, state):
        self.state = state
        if state == "market":
            self.market_menu.toggle()

    def handle_event(self, event):
        if self.state == "market":
            self.market_menu.handle_event(event)
        else:
            self.player.handle_event(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    self.set_state("market")

    def update(self, dt):
        if self.state == "playing":
            keys = pygame.key.get_pressed()
            self.boat.update(dt, keys)
            self.player.update(dt, keys)

    def render(self):
        if self.state == "market":
            self.market_menu.render(self.screen)
        else:
            self.screen.fill((0, 100, 200))  # Laut
            self.boat.render(self.screen)
            self.player.render(self.screen)
            font = pygame.font.SysFont(None, 30)
            wallet_text = font.render(f"Coins: {self.wallet}", True, (255, 255, 0))
            self.screen.blit(wallet_text, (10, 10))

        pygame.display.flip()
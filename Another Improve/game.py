import pygame
from player import Player
from inventory import Inventory

class Boat:
    def __init__(self, game_map):
        self.map = game_map
        self.position = [0, 0]

    def update(self, dt, keys):
        # Example movement logic
        if keys[pygame.K_UP]:
            self.position[1] -= 1
        if keys[pygame.K_DOWN]:
            self.position[1] += 1
        if keys[pygame.K_LEFT]:
            self.position[0] -= 1
        if keys[pygame.K_RIGHT]:
            self.position[0] += 1

    def render(self, screen):
        pygame.draw.rect(screen, (255, 255, 255), (*self.position, 20, 20))

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
        
        class Player:
            def __init__(self, boat, game):
                self.boat = boat
                self.game = game
        
            def handle_event(self, event):
                pass  # Add event handling logic here
        
            def update(self, dt, keys):
                pass  # Add update logic here
        
            def render(self, screen):
                pass  # Add rendering logic here
                self.inventory = Inventory()
        
        class Inventory:
            def __init__(self):
                self.items = []
        
            def add_item(self, item):
                self.items.append(item)
        
            def remove_item(self, item):
                if item in self.items:
                    self.items.remove(item)
        
            def list_items(self):
                return self.items
                self.market_menu = MarketMenu(self)
        
        class MarketMenu:
            def __init__(self, game):
                self.game = game
                self.active = False
        
            def toggle(self):
                self.active = not self.active
        
            def handle_event(self, event):
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.game.set_state("playing")
        
            def render(self, screen):
                font = pygame.font.SysFont(None, 50)
                text = font.render("Market Menu", True, (255, 255, 255))
                screen.fill((0, 0, 0))  # Black background
                screen.blit(text, (100, 100))

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
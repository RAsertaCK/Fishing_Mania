import pygame
import random
from config import Config

class Boat:
    def __init__(self, game_map):
        self.game_map = game_map
        self.image = Config.load_image(f"sprites/boat_{game_map.name.lower()}.png", 0.8)
        self.rect = self.image.get_rect(midbottom=(Config.SCREEN_WIDTH//2, Config.SCREEN_HEIGHT-50))
        self.speed = 300
        self.upgrades = {"speed": 1, "capacity": 1}

    def update(self, dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed * dt * self.upgrades["speed"]
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed * dt * self.upgrades["speed"]
        
        # Keep boat on screen
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(Config.SCREEN_WIDTH, self.rect.right)

    def render(self, screen):
        screen.blit(self.image, self.rect)

class Player:
    def __init__(self, boat, game):
        self.boat = boat
        self.game = game
        self.image = Config.load_image("sprites/player.png", 0.7)
        self.rect = self.image.get_rect(midbottom=boat.rect.midtop)
        self.hook = Hook(self)

    def update(self, dt):
        self.rect.centerx = self.boat.rect.centerx
        if self.hook.fish_caught:
            self.hook.fish_caught.update(dt)
            if self.hook.fish_caught.rect.top <= self.rect.bottom:
                value = self.game.collection.add_fish(self.hook.fish_caught)
                self.game.wallet += value
                self.hook.fish_caught = None

    def handle_event(self, event):
        self.hook.handle_event(event)

    def render(self, screen):
        screen.blit(self.image, self.rect)
        self.hook.render(screen)

class Hook:
    def __init__(self, player):
        self.player = player
        self.rect = pygame.Rect(0, 0, 5, 30)
        self.rect.midtop = player.rect.midbottom
        self.extending = False
        self.retracting = False
        self.depth = 0
        self.max_depth = 300
        self.speed = 200
        self.fish_caught = None
        self.line_color = (100, 100, 100)

    def update(self, dt):
        self.rect.centerx = self.player.rect.centerx
        
        if self.extending and self.depth < self.max_depth:
            self.depth += self.speed * dt
        elif (not self.extending or self.fish_caught) and self.depth > 0:
            self.depth -= self.speed * dt
            if self.fish_caught:
                self.fish_caught.rect.y -= self.speed * dt
        
        # Random fish catch when at max depth
        if self.depth >= self.max_depth and not self.fish_caught:
            if random.random() < 0.05:  # 5% chance per frame
                fish_data = random.choice(self.player.boat.game_map.available_fish)
                if fish_data:
                    self.fish_caught = Fish(*fish_data, (self.rect.centerx, self.rect.bottom + self.depth))

        self.rect.height = 30 + int(self.depth)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
            self.extending = True
            self.retracting = False
        elif event.type == pygame.KEYUP and event.key == pygame.K_DOWN:
            self.extending = False
            self.retracting = True

    def render(self, screen):
        # Draw fishing line
        start_pos = (self.rect.centerx, self.player.rect.bottom)
        end_pos = (self.rect.centerx, self.rect.bottom)
        pygame.draw.line(screen, self.line_color, start_pos, end_pos, 2)
        
        # Draw hook
        pygame.draw.rect(screen, Config.BLACK, self.rect)
        
        if self.fish_caught:
            self.fish_caught.render(screen)

    def reset(self):
        self.depth = 0
        self.fish_caught = None

class Fish:
    def __init__(self, kind, rarity, pos):
        self.kind = kind
        self.rarity = rarity
        self.image = Config.load_image(f"sprites/fish_{rarity}.png", 0.5)
        self.rect = self.image.get_rect(center=pos)
        self.swim_speed = random.uniform(20, 50)
        self.swim_direction = random.choice([-1, 1])

    def update(self, dt):
        if not hasattr(self, 'caught'):
            # Random swimming before caught
            self.rect.x += self.swim_direction * self.swim_speed * dt
            if random.random() < 0.02:  # 2% chance to change direction
                self.swim_direction *= -1
        else:
            # Movement when caught
            pass

    def render(self, screen):
        screen.blit(self.image, self.rect)
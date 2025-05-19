import pygame
import sys
import random
import os

# --- CONFIG ---
class Config:
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    FPS = 60
    ASSET_PATH = "assets"
    COLORS = {
        "common": (100, 200, 100),
        "rare": (100, 100, 255),
        "legendary": (255, 215, 0),
        "text": (255, 255, 255)
    }

    @staticmethod
    def load_image(path, scale=1.0):
        try:
            image = pygame.image.load(path).convert_alpha()
            if scale != 1.0:
                size = (int(image.get_width() * scale), int(image.get_height() * scale))
                image = pygame.transform.scale(image, size)
            return image
        except:
            surface = pygame.Surface((32, 32), pygame.SRCALPHA)
            surface.fill((255, 0, 255))
            return surface

# --- MENU ---
class Menu:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.SysFont(None, 48)
        self.options = []
        self.selected = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                _, action = self.options[self.selected]
                action()

    def render(self, screen):
        screen.fill((0, 0, 50))
        for i, (label, _) in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected else (255, 255, 255)
            text = self.font.render(label, True, color)
            rect = text.get_rect(center=(screen.get_width() // 2, 200 + i * 60))
            screen.blit(text, rect)

class MainMenu(Menu):
    def __init__(self, game):
        super().__init__(game)
        self.options = [
            ("Start Game", lambda: self.game.set_state("explore")),
            ("Go to Market", lambda: self.game.set_state("market")),
            ("Quit", lambda: pygame.event.post(pygame.event.Event(pygame.QUIT)))
        ]

# --- MARKET ---
class MarketMenu:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.SysFont(None, 36)
        self.active = False

    def toggle(self):
        self.active = not self.active

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                total = self.game.inventory.sell_all()
                self.game.wallet += total

    def render(self, screen):
        if not self.active:
            return
        screen.fill((30, 30, 30))
        text = self.font.render("Press ENTER to sell all fish", True, (255, 255, 0))
        screen.blit(text, (screen.get_width()//2 - text.get_width()//2, 100))
        self.game.inventory.render(screen, self.font)

# --- INVENTORY ---
class Inventory:
    def __init__(self):
        self.fish = []

    def add_fish(self, fish):
        self.fish.append(fish)

    def sell_all(self):
        total = sum(f.value for f in self.fish)
        self.fish.clear()
        return total

    def render(self, screen, font):
        screen.blit(font.render("Inventory:", True, (255, 255, 255)), (10, 200))
        for i, fish in enumerate(self.fish[-10:]):
            text = font.render(f"{fish.name} ({fish.rarity}) - {fish.value}", True, (200, 200, 200))
            screen.blit(text, (10, 230 + i * 25))

# --- FISH ---
class Fish:
    def __init__(self, data, pos):
        self.name = data["name"]
        self.rarity = data["rarity"]
        self.value = data["value"]
        self.pos = pos

# --- GAME MAP ---
class GameMap:
    LOCATIONS = {
        "Coast": {
            "fish": [
                {"name": "Sea Bass", "rarity": "common", "value": 10},
                {"name": "Red Snapper", "rarity": "common", "value": 15},
                {"name": "Crab", "rarity": "rare", "value": 40}
            ],
            "depth_range": (10, 30),
            "color": Config.COLORS["common"]
        },
        "Sea": {
            "fish": [
                {"name": "Tuna", "rarity": "rare", "value": 80},
                {"name": "Swordfish", "rarity": "rare", "value": 100},
                {"name": "Shark", "rarity": "legendary", "value": 250}
            ],
            "depth_range": (50, 100),
            "color": Config.COLORS["rare"]
        },
        "Ocean": {
            "fish": [
                {"name": "Blue Marlin", "rarity": "legendary", "value": 500},
                {"name": "Whale", "rarity": "legendary", "value": 1000}
            ],
            "depth_range": (100, 200),
            "color": Config.COLORS["legendary"]
        }
    }

    def __init__(self, name):
        self.name = name
        self.data = self.LOCATIONS.get(name, self.LOCATIONS["Coast"])
        bg_filename = f"bg_{name.lower()}.png"
        self.background = Config.load_image(os.path.join(Config.ASSET_PATH, "Background", bg_filename))

    def render(self, screen):
        screen.blit(self.background, (0, 0))

    def get_random_fish(self):
        fish_pool = self.data["fish"]
        weights = [0.7 if f["rarity"] == "common" else 0.25 if f["rarity"] == "rare" else 0.05 for f in fish_pool]
        return random.choices(fish_pool, weights=weights, k=1)[0]

# --- MAP EXPLORE ---
class MapExplorer:
    def __init__(self):
        self.bg_color = (50, 120, 200)
        self.player_pos = [100, 100]
        self.player_speed = 200
        self.player_size = 32

        self.font = pygame.font.SysFont(None, 28)
        self.spot_rects = [
            pygame.Rect(400, 150, 50, 50),
            pygame.Rect(700, 400, 50, 50),
            pygame.Rect(200, 500, 50, 50),
        ]
        self.spot_names = ["Coast", "Sea", "Ocean"]
        self.trigger_zone = None

    def update(self, dt, keys):
        if keys[pygame.K_LEFT]: self.player_pos[0] -= self.player_speed * dt
        if keys[pygame.K_RIGHT]: self.player_pos[0] += self.player_speed * dt
        if keys[pygame.K_UP]: self.player_pos[1] -= self.player_speed * dt
        if keys[pygame.K_DOWN]: self.player_pos[1] += self.player_speed * dt

        player_rect = pygame.Rect(self.player_pos[0], self.player_pos[1], self.player_size, self.player_size)
        self.trigger_zone = None
        for i, spot in enumerate(self.spot_rects):
            if player_rect.colliderect(spot):
                self.trigger_zone = self.spot_names[i]

    def render(self, screen):
        screen.fill(self.bg_color)
        for i, rect in enumerate(self.spot_rects):
            pygame.draw.rect(screen, (0, 255, 100), rect)
            label = self.font.render(self.spot_names[i], True, (255, 255, 255))
            screen.blit(label, (rect.x, rect.y - 25))

        pygame.draw.rect(screen, (255, 255, 0), (*self.player_pos, self.player_size, self.player_size))

        if self.trigger_zone:
            msg = f"Press ENTER to fish at {self.trigger_zone}"
            text = self.font.render(msg, True, (255, 255, 255))
            screen.blit(text, (self.player_pos[0] - 50, self.player_pos[1] - 40))

    def get_selected_location(self):
        return self.trigger_zone

# --- FISHING MINIGAME ---
class FishingSkillChallenge:
    def __init__(self):
        self.result = None
        self.timer = 0
        self.duration = 3000  # ms
        self.challenge_active = False

    def start(self):
        self.challenge_active = True
        self.timer = pygame.time.get_ticks()
        self.result = None

    def update(self):
        if not self.challenge_active:
            return
        current = pygame.time.get_ticks()
        if current - self.timer >= self.duration:
            if pygame.key.get_pressed()[pygame.K_SPACE]:
                self.result = "caught"
            else:
                self.result = "failed"
            self.challenge_active = False

    def update_events(self, event):
        pass  # Not needed for this simple minigame

    def render(self, screen):
        if not self.challenge_active:
            return
        font = pygame.font.SysFont(None, 48)
        text = font.render("PRESS SPACE!", True, (255, 0, 0))
        rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        screen.blit(text, rect)

# --- UI ---
class UI:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.SysFont(None, 32)
        self.small_font = pygame.font.SysFont(None, 24)

    def render(self, screen):
        screen.blit(self.font.render(f"Coins: {self.game.wallet}", True, (255, 255, 0)), (10, 10))
        if hasattr(self.game, 'inventory'):
            screen.blit(self.small_font.render(f"Fish in inventory: {len(self.game.inventory.fish)}", True, (255, 255, 255)), (10, 40))

# --- MAIN GAME CLASS ---
class Game:
    def __init__(self, screen):
        self.screen = screen
        self.state = "menu"
        self.wallet = 0

        self.inventory = Inventory()
        self.map = GameMap("Coast")
        self.ui = UI(self)
        self.map_explorer = MapExplorer()
        self.fishing_minigame = None
        self.active_location = None

        self.main_menu = MainMenu(self)
        self.market_menu = MarketMenu(self)

        try:
            self.sound_success = pygame.mixer.Sound("assets/sounds/catch.wav")
        except:
            self.sound_success = None
        try:
            self.sound_fail = pygame.mixer.Sound("assets/sounds/fail.wav")
        except:
            self.sound_fail = None

    def set_state(self, state):
        self.state = state
        if state == "market":
            self.market_menu.toggle()
        elif state == "menu":
            self.main_menu.selected = 0

    def handle_event(self, event):
        if self.state == "menu":
            self.main_menu.handle_event(event)
        elif self.state == "market":
            self.market_menu.handle_event(event)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.set_state("explore")
        elif self.state == "explore":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    self.set_state("market")
                elif event.key == pygame.K_ESCAPE:
                    self.set_state("menu")
                elif event.key == pygame.K_RETURN:
                    location = self.map_explorer.get_selected_location()
                    if location:
                        self.active_location = location
                        self.map = GameMap(location)
                        self.fishing_minigame = FishingSkillChallenge()
                        self.fishing_minigame.start()
                        self.set_state("minigame")
        elif self.state == "minigame":
            if hasattr(self.fishing_minigame, "update_events"):
                self.fishing_minigame.update_events(event)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.set_state("explore")

    def update(self, dt):
        keys = pygame.key.get_pressed()
        if self.state == "menu":
            pass
        elif self.state == "market":
            pass
        elif self.state == "explore":
            self.map_explorer.update(dt, keys)
        elif self.state == "minigame":
            self.fishing_minigame.update()
            if self.fishing_minigame.result is not None:
                if self.fishing_minigame.result == "caught":
                    fish_data = self.map.get_random_fish()
                    fish = Fish(fish_data, (0, 0))
                    self.inventory.add_fish(fish)
                    self.wallet += fish_data["value"]
                    if self.sound_success:
                        self.sound_success.play()
                else:
                    if self.sound_fail:
                        self.sound_fail.play()
                self.set_state("explore")

    def render(self):
        if self.state == "menu":
            self.main_menu.render(self.screen)
        elif self.state == "market":
            self.market_menu.render(self.screen)
        elif self.state == "explore":
            self.map_explorer.render(self.screen)
            self.ui.render(self.screen)
        elif self.state == "minigame":
            self.screen.fill((0, 0, 30))
            self.fishing_minigame.render(self.screen)
            self.ui.render(self.screen)
        pygame.display.flip()

# --- MAIN LOOP ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
    pygame.display.set_caption("Fishing Mania")
    clock = pygame.time.Clock()
    game = Game(screen)
    running = True

    while running:
        dt = clock.tick(Config.FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game.handle_event(event)

        game.update(dt)
        game.render()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
import pygame
from config import Config

class Menu:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.SysFont(None, Config.FONT_MEDIUM)
        self.title_font = pygame.font.SysFont(None, Config.FONT_LARGE)
        self.options = []
        self.selected_index = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                self.select_option()

    def render(self, screen):
        screen.fill(Config.BLUE)
        title = self.title_font.render(self.title, True, Config.WHITE)
        screen.blit(title, (Config.SCREEN_WIDTH//2 - title.get_width()//2, 100))

        for i, (text, action) in enumerate(self.options):
            color = Config.WHITE if i == self.selected_index else (200, 200, 200)
            option_text = self.font.render(text, True, color)
            screen.blit(option_text, (Config.SCREEN_WIDTH//2 - option_text.get_width()//2, 200 + i * 50))

class MainMenu(Menu):
    def __init__(self, game):
        super().__init__(game)
        self.title = "Fishing Mania"
        self.options = [
            ("Start Game", lambda: self.game.set_state("playing")),
            ("Settings", lambda: self.game.set_state("settings")),
            ("Shop", lambda: self.game.set_state("shop")),
            ("Quit", lambda: pygame.event.post(pygame.event.Event(pygame.QUIT)))
        ]

class SettingsMenu(Menu):
    def __init__(self, game):
        super().__init__(game)
        self.title = "Settings"
        self.options = [
            ("Back", lambda: self.game.set_state("main_menu"))
        ]

class ShopMenu(Menu):
    def __init__(self, game):
        super().__init__(game)
        self.title = "Boat Shop"
        self.options = [
            ("Upgrade Speed (Cost: 100)", self.upgrade_speed),
            ("Upgrade Capacity (Cost: 150)", self.upgrade_capacity),
            ("Back", lambda: self.game.set_state("main_menu"))
        ]

    def upgrade_speed(self):
        if self.game.wallet >= 100:
            self.game.wallet -= 100
            self.game.boat.upgrades["speed"] += 0.2

    def upgrade_capacity(self):
        if self.game.wallet >= 150:
            self.game.wallet -= 150
            self.game.boat.upgrades["capacity"] += 1
import pygame
from menu import MainMenu, SettingsMenu, ShopMenu
from game_map import GameMap
from entity import Boat, Player
from ui import UI
from collection import Collection
from config import Config

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.state = "main_menu"
        self.wallet = 50
        self.main_menu = MainMenu(self)
        self.settings = SettingsMenu(self)
        self.shop = ShopMenu(self)
        self.collection = Collection()
        self.set_map("Coast")

    def set_map(self, map_name):
        self.map = GameMap(map_name)
        self.boat = Boat(self.map)
        self.player = Player(self.boat, self)
        self.ui = UI(self)

    def set_state(self, state):
        self.state = state
        if state == "playing":
            self.player.hook.reset()

    def handle_event(self, event):
        if self.state == "main_menu":
            self.main_menu.handle_event(event)
        elif self.state == "settings":
            self.settings.handle_event(event)
        elif self.state == "shop":
            self.shop.handle_event(event)
        else:
            self.player.handle_event(event)

    def update(self, dt):
        if self.state == "playing":
            self.map.update(dt)
            self.boat.update(dt)
            self.player.update(dt)

    def render(self):
        if self.state == "main_menu":
            self.main_menu.render(self.screen)
        elif self.state == "settings":
            self.settings.render(self.screen)
        elif self.state == "shop":
            self.shop.render(self.screen)
        else:
            self.map.render(self.screen)
            self.boat.render(self.screen)
            self.player.render(self.screen)
            self.ui.render(self.screen)
        
        pygame.display.flip()
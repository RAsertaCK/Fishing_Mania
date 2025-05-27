import pygame
from fishing_challenge import FishingSkillChallenge
from map_explore import MapExplorer
from inventory import Inventory
from fish import Fish
from game_map import GameMap
from ui import UI
from config import Config

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.state = "explore"
        self.wallet = 0

        self.inventory = Inventory()
        self.map = GameMap("Coast")
        self.ui = UI(self)
        self.map_explorer = MapExplorer()
        self.fishing_minigame = None
        self.active_location = None


    def set_state(self, state):
        self.state = state

    def handle_event(self, event):
        if self.state == "explore":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                location = self.map_explorer.get_selected_location()
                if location:
                    self.active_location = location
                    self.map = GameMap(location)
                    self.fishing_minigame = FishingSkillChallenge()
                    self.fishing_minigame.start()
                    self.set_state("minigame")

        elif self.state == "minigame":
            self.fishing_minigame.update_events(event) if hasattr(self.fishing_minigame, "update_events") else None

    def update(self, dt):
        keys = pygame.key.get_pressed()

        if self.state == "explore":
            self.map_explorer.update(dt, keys)

        elif self.state == "minigame":
            self.fishing_minigame.update()
            if self.fishing_minigame.result is not None:
                if self.fishing_minigame.result == "caught":
                    fish_data = self.map.get_random_fish()
                    fish = Fish(fish_data, (0, 0))
                    self.inventory.add_fish(fish)
                    self.wallet += fish_data["value"]
                    self.sound_success.play()
                else:
                    self.sound_fail.play()
                self.set_state("explore")

    def render(self):
        if self.state == "explore":
            self.map_explorer.render(self.screen)
            self.ui.render(self.screen)

        elif self.state == "minigame":
            self.screen.fill((0, 0, 30))
            self.fishing_minigame.render(self.screen)
            self.ui.render(self.screen)

        pygame.display.flip()
import pygame
from config import Config

class Menu:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.SysFont(None, 48)
        self.options = []
        self.selected = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                _, action = self.options[self.selected]
                action()

    def render(self, screen):
        screen.fill((0, 0, 50))
        for i, (label, _) in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected else (255, 255, 255)
            text = self.font.render(label, True, color)
            screen.blit(text, (Config.SCREEN_WIDTH // 2 - text.get_width() // 2, 200 + i * 60))

class MainMenu(Menu):
    def __init__(self, game):
        super().__init__(game)
        self.options = [
            ("Start Game", lambda: self.game.set_state("playing")),
            ("Go to Market", lambda: self.game.set_state("market")),
            ("Quit", lambda: pygame.event.post(pygame.event.Event(pygame.QUIT)))
        ]
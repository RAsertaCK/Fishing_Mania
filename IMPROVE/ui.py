import pygame

class UI:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.SysFont(None, 32)
        self.small_font = pygame.font.SysFont(None, 24)

    def render(self, screen):
        screen.blit(self.font.render(f"Coins: {self.game.wallet}", True, (255, 255, 0)), (10, 10))
        if hasattr(self.game, 'player') and self.game.player.fishing.fish:
            fish = self.game.player.fishing.fish
            screen.blit(self.small_font.render(f"Caught: {fish.name} ({fish.rarity})", True, (255, 255, 255)), (10, 40))
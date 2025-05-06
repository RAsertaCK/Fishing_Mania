import pygame
from config import Config

class UI:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.SysFont(None, Config.FONT_MEDIUM)
        self.small_font = pygame.font.SysFont(None, Config.FONT_SMALL)

    def render(self, screen):
        coins_text = self.font.render(f"Coins: {self.game.wallet}", True, (255, 255, 0))
        screen.blit(coins_text, (10, 10))

        location_text = self.small_font.render(f"Location: {self.game.map.name}", True, Config.WHITE)
        screen.blit(location_text, (10, 50))

        depth_percent = self.game.player.hook.depth / self.game.player.hook.max_depth
        pygame.draw.rect(screen, Config.WHITE, (Config.SCREEN_WIDTH - 120, 10, 100, 20), 1)
        pygame.draw.rect(screen, (0, 100, 200), (Config.SCREEN_WIDTH - 120, 10, 100 * depth_percent, 20))

        if self.game.player.hook.fish_caught:
            fish = self.game.player.hook.fish_caught
            fish_text = self.font.render(f"Caught: {fish.kind} ({fish.rarity})", True, Config.WHITE)
            screen.blit(fish_text, (Config.SCREEN_WIDTH//2 - fish_text.get_width()//2, 50))

        controls = self.small_font.render("Controls: Arrows to move, DOWN to cast", True, Config.WHITE)
        screen.blit(controls, (Config.SCREEN_WIDTH//2 - controls.get_width()//2, Config.SCREEN_HEIGHT - 30))
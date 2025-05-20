import pygame

class MarketMenu:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.SysFont(None, 36)
        self.active = False

    def toggle(self):
        self.active = not self.active
        if not self.active:
            self.game.set_state("playing")

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
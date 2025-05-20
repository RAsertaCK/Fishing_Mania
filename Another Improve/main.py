import pygame
import sys
from game_logic_integration import Game  # Use the integrated logic
from config import Config
pygame.font.init()  # Initialize fonts

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
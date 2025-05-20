import pygame
from sprites import *
from config import *
import sys

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.camera = pygame.Vector2(0, 0)  # Initialize camera offset

        self.character_spritesheet = spritesheet('assets/player.png')

        # Group for storing all blocks
        self.blocks = pygame.sprite.Group()

    def createTilemap(self):
        for i, row in enumerate(tilemap):
            for j, column in enumerate(row):
                Ground(self, j, i)
                if column == "B":
                    block = Block(self, j, i)
                    self.blocks.add(block)  # Add block to blocks group
                if column == "P":
                    self.player = Player(self, j, i)  # Store reference to player

    def new(self):
        self.playing = True
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.block = pygame.sprite.LayeredUpdates()

        self.createTilemap()

    def event(self):
        # game loop event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False

    def update(self):
        # game loop update
        self.all_sprites.update()

    def update_camera(self):
        # Center the camera on the player
        self.camera.x = self.player.rect.centerx - WIN_WIDTH // 2
        self.camera.y = self.player.rect.centery - WIN_HEIGHT // 2

    def draw(self):
        # game loop draw
        self.screen.fill(BLUE)
        for sprite in self.all_sprites:
            # Adjust the position of each sprite based on the camera offset
            self.screen.blit(sprite.image, sprite.rect.topleft - self.camera)
        self.clock.tick(FPS)
        pygame.display.update()

    def main(self):
        while self.playing:
            self.event()
            self.update()
            self.update_camera()  # Update camera position
            self.draw()
            self.running = False

    def game_over(self):
        pass

    def intro_screen(self):
        pass

g = Game()
g.intro_screen()
g.new()
while g.running:
    g.main()
    g.game_over()

pygame.quit()
sys.exit() 


import pygame
from config import *
import math
import random

class spritesheet:
    def __init__(self, file):
        self.sheet = pygame.image.load(file).convert_alpha()  # gunakan convert_alpha untuk transparansi

    def get_sprite(self, x, y, width, height):
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)
        sprite.blit(self.sheet, (0, 0), (x, y, width, height))
        return sprite
    
class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = PLAYER_LAYER
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        self.x_change = 0
        self.y_change = 0

        self.facing = 'down'
        self.animation_loop = 1

        self.image = self.game.character_spritesheet.get_sprite(0, 118, 34, 42)

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        
    def collide_blocks(self, direction):
        if direction == 'x':
            hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
            if hits:
                for hit in hits:
                    if self.x_change > 0:  
                        self.rect.right = hit.rect.left  
                    if self.x_change < 0:  
                        self.rect.left = hit.rect.right  

        if direction == 'y':
            hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
            if hits:
                for hit in hits:
                    if self.y_change > 0:  
                        self.rect.bottom = hit.rect.top  
                    if self.y_change < 0:  
                        self.rect.top = hit.rect.bottom  

    def animate(self):
        right_animations = [self.game.character_spritesheet.get_sprite(0, 80, 34, 34),
                            self.game.character_spritesheet.get_sprite(0, 0, 32, 40),
                            self.game.character_spritesheet.get_sprite(34, 0, 32, 40),
                            self.game.character_spritesheet.get_sprite(68, 0, 32, 40),
                            self.game.character_spritesheet.get_sprite(98, 0, 32, 40),
                            self.game.character_spritesheet.get_sprite(128, 0, 32, 40),
                            self.game.character_spritesheet.get_sprite(162, 0, 32, 40),
                            self.game.character_spritesheet.get_sprite(196, 0, 32, 40),
                            self.game.character_spritesheet.get_sprite(226, 0, 32, 40)]

        left_animations = [self.game.character_spritesheet.get_sprite(36, 82, 34, 34),
                           self.game.character_spritesheet.get_sprite(224, 42, 32, 40),
                           self.game.character_spritesheet.get_sprite(190, 44, 32, 40),
                           self.game.character_spritesheet.get_sprite(160, 42, 32, 40),
                           self.game.character_spritesheet.get_sprite(130, 40, 32, 40),
                           self.game.character_spritesheet.get_sprite(96, 42, 32, 40),
                           self.game.character_spritesheet.get_sprite(62, 44, 32, 40),
                           self.game.character_spritesheet.get_sprite(32, 42, 32, 40),
                           self.game.character_spritesheet.get_sprite(0, 40, 32, 40)]
        
        up_animation = [self.game.character_spritesheet.get_sprite(70, 82, 34, 34),
                        self.game.character_spritesheet.get_sprite(104, 82, 34, 34),
                        self.game.character_spritesheet.get_sprite(140, 82, 34, 34),]
        
        down_animation = [self.game.character_spritesheet.get_sprite(0, 118, 34, 34),
                          self.game.character_spritesheet.get_sprite(34, 118, 34, 34),
                          self.game.character_spritesheet.get_sprite(66, 118, 34, 34),]

        def get_index(loop, max_len):
                index = math.floor(loop)
                return min(index, max_len - 1)

        if self.facing == 'right':
                if self.x_change == 0:
                    self.image = self.game.character_spritesheet.get_sprite(0, 80, 34, 34)
                else:
                    index = get_index(self.animation_loop, len(right_animations))
                    self.image = right_animations[index]
                    self.animation_loop += 0.1
                    if self.animation_loop >= len(right_animations):
                        self.animation_loop = 0

        elif self.facing == 'left':
                if self.x_change == 0:
                    self.image = self.game.character_spritesheet.get_sprite(36, 81, 34, 34)
                else:
                    index = get_index(self.animation_loop, len(left_animations))
                    self.image = left_animations[index]
                    self.animation_loop += 0.1
                    if self.animation_loop >= len(left_animations):
                        self.animation_loop = 0

        elif self.facing == 'up':
                if self.y_change == 0:
                    self.image = self.game.character_spritesheet.get_sprite(70, 82, 34, 34)
                else:
                    index = get_index(self.animation_loop, len(up_animation))
                    self.image = up_animation[index]
                    self.animation_loop += 0.1
                    if self.animation_loop >= len(up_animation):
                        self.animation_loop = 0

        elif self.facing == 'down':
                if self.y_change == 0:
                    self.image = self.game.character_spritesheet.get_sprite(0, 118, 34, 34)
                else:
                    index = get_index(self.animation_loop, len(down_animation))
                    self.image = down_animation[index]
                    self.animation_loop += 0.1
                    if self.animation_loop >= len(down_animation):
                        self.animation_loop = 0
        
    def update(self):
        self.movements()
        self.animate()

        self.rect.x += self.x_change
        self.collide_blocks('x')
        self.rect.y += self.y_change
        self.collide_blocks('y')

        self.x_change = 0
        self.y_change = 0

    def movements(self):
        keys = pygame.key.get_pressed()
        if keys [pygame.K_a]:
            for sprite in self.game.all_sprites:
                sprite.rect.x += PLAYER_SPEED
            self.x_change -= PLAYER_SPEED
            self.facing = 'left'
        if keys [pygame.K_d]:
            for sprite in self.game.all_sprites:
                sprite.rect.x -= PLAYER_SPEED
            self.x_change += PLAYER_SPEED
            self.facing = 'right'
        if keys [pygame.K_w]:
            for sprite in self.game.all_sprites:
                sprite.rect.y += PLAYER_SPEED
            self.y_change -= PLAYER_SPEED
            self.facing = 'up'
        if keys [pygame.K_s]:
            for sprite in self.game.all_sprites:
                sprite.rect.y -= PLAYER_SPEED
            self.y_change += PLAYER_SPEED
            self.facing = 'down'

class Block(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        
        self.game = game
        self._layer = BLOCK_LAYER
        self.groups = self.game.all_sprites, self.game.block
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        self.image = pygame.Surface((self.width, self.height)) 
        self.image.fill((BLUE))

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

class Ground(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = GROUND_LAYER
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        # Muat gambar yang sudah diunggah sebagai tile tanah
        self.image = pygame.image.load('assets/Sand 1.png').convert()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))  # Ubah ukuran gambar sesuai TILESIZE

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

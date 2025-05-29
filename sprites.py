# sprites.py
import pygame
import math
import random
import os
from config import Config

class Spritesheet:
    def __init__(self, file):
        self.sheet = pygame.image.load(file).convert_alpha()

    def get_sprite(self, x, y, width, height):
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)
        sprite.blit(self.sheet, (0, 0), (x, y, width, height))
        return sprite
    
class Player(pygame.sprite.Sprite): # Ini adalah LandPlayer
    def __init__(self, game, x, y):
        self.game = game
        self._layer = Config.PLAYER_LAYER
        pygame.sprite.Sprite.__init__(self)

        self.x = x * Config.TILESIZE
        self.y = y * Config.TILESIZE
        
        self.x_change = 0
        self.y_change = 0

        self.facing = 'down'
        self.animation_loop = 1

        # --- SOLUSI SEMENTARA: Gunakan lingkaran merah solid untuk karakter ---
        # Ini akan memastikan karakter terlihat dan bisa digerakkan,
        # mengisolasi masalah ke spritesheet asli.
        placeholder_size = int(34 * Config.PLAYER_SPRITE_SCALE) # Ukuran placeholder, misal 68x68
        self.image = pygame.Surface((placeholder_size, placeholder_size), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0)) # Buat transparan sepenuhnya
        pygame.draw.circle(self.image, Config.COLORS["red"], (placeholder_size // 2, placeholder_size // 2), placeholder_size // 2) # Gambar lingkaran merah
        print(f"--- Player: Menggunakan lingkaran merah solid sebagai placeholder. Ukuran: {self.image.get_size()} ---")
        # --- AKHIR SOLUSI SEMENTARA ---

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        
    def collide_blocks(self, direction):
        hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
        if hits:
            for hit in hits:
                if direction == 'x':
                    if self.x_change > 0:  
                        self.rect.right = hit.rect.left  
                    if self.x_change < 0:  
                        self.rect.left = hit.rect.right  
                elif direction == 'y':
                    if self.y_change > 0:  
                        self.rect.bottom = hit.rect.top  
                    if self.y_change < 0:  
                        self.rect.top = hit.rect.bottom  

    def animate(self):
        # Saat menggunakan placeholder solid, animasi tidak diperlukan.
        pass

    def update(self):
        self.movements()

        self.rect.x += self.x_change
        self.rect.y += self.y_change
        
        self.collide_blocks('x')
        self.collide_blocks('y')

        # self.animate() # Jangan panggil animate() saat menggunakan placeholder solid

        self.x_change = 0
        self.y_change = 0


    def movements(self):
        keys = pygame.key.get_pressed()
        self.x_change = 0
        self.y_change = 0

        if keys [pygame.K_a]:
            self.x_change -= Config.PLAYER_SPEED
            self.facing = 'left'
        if keys [pygame.K_d]:
            self.x_change += Config.PLAYER_SPEED
            self.facing = 'right'
        if keys [pygame.K_w]:
            self.y_change -= Config.PLAYER_SPEED
            self.facing = 'up'
        if keys [pygame.K_s]:
            self.y_change += Config.PLAYER_SPEED
            self.facing = 'down'

class Block(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = Config.BLOCK_LAYER
        pygame.sprite.Sprite.__init__(self)

        self.x = x * Config.TILESIZE
        self.y = y * Config.TILESIZE
        self.width = Config.TILESIZE
        self.height = Config.TILESIZE

        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(Config.COLORS["blue"])

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

class Ground(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = Config.GROUND_LAYER
        pygame.sprite.Sprite.__init__(self)

        self.x = x * Config.TILESIZE
        self.y = y * Config.TILESIZE
        self.width = Config.TILESIZE
        self.height = Config.TILESIZE

        ground_image_path = os.path.join(Config.ASSET_PATH, "backgrounds", "Grass 1.png")
        try:
            if os.path.exists(ground_image_path):
                self.image = Config.load_image(ground_image_path, use_alpha=False)
                self.image = pygame.transform.scale(self.image, (self.width, self.height))
            else:
                print(f"--- Ground: PERINGATAN - Tile gambar '{ground_image_path}' tidak ditemukan. Menggunakan warna hijau solid.")
                self.image = pygame.Surface((self.width, self.height))
                self.image.fill(Config.COLORS["green"])
        except Exception as e:
            print(f"--- Ground: ERROR memuat tile gambar '{ground_image_path}': {e}. Menggunakan warna hijau solid.")
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill(Config.COLORS["green"])

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
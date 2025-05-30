import pygame
import math
import random
import os

class Spritesheet:
    def __init__(self, file_path):
        try:
            self.sheet = pygame.image.load(file_path).convert_alpha()
        except pygame.error as e:
            print(f"ERROR: Tidak dapat memuat spritesheet dari {file_path}: {e}")
            self.sheet = pygame.Surface((1,1), pygame.SRCALPHA) # Fallback

    def get_sprite(self, x, y, width, height):
        if self.sheet.get_width() <= 1: # Cek jika sheet utama gagal dimuat
            sprite = pygame.Surface((width, height), pygame.SRCALPHA)
            sprite.fill((255,0,255,100)) # Warna magenta sebagai indikator error
            return sprite

        sprite = pygame.Surface((width, height), pygame.SRCALPHA)
        sprite.blit(self.sheet, (0, 0), (x, y, width, height))
        return sprite
    
class Player(pygame.sprite.Sprite): # Ini adalah LandPlayer
    def __init__(self, game, x, y):
        self.game = game
        self._layer = self.game.config.PLAYER_LAYER
        
        # Pastikan grup sprite ada di game instance
        if not hasattr(self.game, 'all_sprites'): self.game.all_sprites = pygame.sprite.Group()
        self.groups = self.game.all_sprites 
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * self.game.config.TILESIZE 
        self.y = y * self.game.config.TILESIZE 
        
        self.x_change = 0
        self.y_change = 0

        self.facing = 'down'
        self.animation_loop = 0 
        self.animation_speed = 0.1 

        self._load_frames() # Memuat semua frame animasi

        # Set gambar awal setelah frame dimuat
        self.image = self.animations[self.facing]['idle']
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)
        
    def _load_frames(self):
        self.animations = {
            'down': {'idle': None, 'walk': []}, 'up': {'idle': None, 'walk': []},
            'left': {'idle': None, 'walk': []}, 'right': {'idle': None, 'walk': []}
        }
        
        if not hasattr(self.game, 'character_spritesheet') or self.game.character_spritesheet is None:
            print("ERROR: LandPlayer - self.game.character_spritesheet tidak ada atau None!")
            scale = self.game.config.PLAYER_SPRITE_SCALE
            dummy_surface = pygame.Surface((int(32*scale), int(32*scale)), pygame.SRCALPHA)
            dummy_surface.fill(self.game.config.COLORS.get("red", (255,0,0)))
            for direction in self.animations:
                self.animations[direction]['idle'] = dummy_surface
                self.animations[direction]['walk'] = [dummy_surface]
            return

        ss = self.game.character_spritesheet 
        scale = self.game.config.PLAYER_SPRITE_SCALE

        def get_scaled_sprite(x, y, w, h):
            original = ss.get_sprite(x,y,w,h)
            return pygame.transform.scale(original, (int(w*scale), int(h*scale)))

        # Koordinat berdasarkan file sprites.py asli Anda
        self.animations['down']['idle'] = get_scaled_sprite(1, 128, 30, 32)
        self.animations['down']['walk'] = [get_scaled_sprite(1, 128, 30, 32), 
                                           get_scaled_sprite(33, 128, 30, 32), 
                                           get_scaled_sprite(65, 128, 30, 32)]
        
        self.animations['up']['idle'] = get_scaled_sprite(69, 83, 33, 37)
        self.animations['up']['walk'] = [get_scaled_sprite(69, 83, 33, 37), 
                                         get_scaled_sprite(103, 83, 33, 37), 
                                         get_scaled_sprite(137, 83, 33, 37)]
        
        self.animations['right']['idle'] = get_scaled_sprite(1, 83, 32, 38)
        self.animations['right']['walk'] = [get_scaled_sprite(1, 0, 32, 38),
                                            get_scaled_sprite(32, 0, 32, 38), 
                                            get_scaled_sprite(67, 0, 32, 38), 
                                            get_scaled_sprite(97, 0, 32, 38), 
                                            get_scaled_sprite(127, 0, 32, 38),
                                            get_scaled_sprite(163, 0, 32, 38), 
                                            get_scaled_sprite(195, 0, 32, 38), 
                                            get_scaled_sprite(225, 0, 32, 38)]
        
        self.animations['left']['idle'] = get_scaled_sprite(36, 81, 30, 40) 
        self.animations['left']['walk'] = [get_scaled_sprite(224, 42, 30, 40), 
                                           get_scaled_sprite(190, 44, 30, 40), 
                                           get_scaled_sprite(160, 42, 30, 40), 
                                           get_scaled_sprite(130, 40, 30, 40), 
                                           get_scaled_sprite(96, 42, 30, 40), 
                                           get_scaled_sprite(62, 44, 30, 40), 
                                           get_scaled_sprite(32, 42, 30, 40), 
                                           get_scaled_sprite(0, 40, 30, 40)]

    def animate(self): 
        is_moving = self.x_change != 0 or self.y_change != 0
        if self.facing not in self.animations: self.facing = 'down' 
        current_anim_set = self.animations[self.facing]

        if is_moving:
            current_walk_frames = current_anim_set['walk']
            if not current_walk_frames: self.image = current_anim_set['idle']; return
            self.animation_loop = (self.animation_loop + self.animation_speed) % len(current_walk_frames)
            self.image = current_walk_frames[math.floor(self.animation_loop)]
        else: 
            self.image = current_anim_set['idle']
            self.animation_loop = 0 
        
    def movements(self): 
        keys = pygame.key.get_pressed()
        speed = self.game.config.PLAYER_SPEED 
        self.x_change = 0; self.y_change = 0
        
        if keys [pygame.K_a] or keys [pygame.K_LEFT]: 
            self.x_change -= speed
            self.facing = 'left'
        elif keys [pygame.K_d] or keys [pygame.K_RIGHT]: 
            self.x_change += speed
            self.facing = 'right'
        
        if keys [pygame.K_w] or keys [pygame.K_UP]: 
            self.y_change -= speed
            self.facing = 'up'
        elif keys [pygame.K_s] or keys [pygame.K_DOWN]: 
            self.y_change += speed
            self.facing = 'down'
            
    def update(self): 
        self.movements()
        self.animate() # PASTIKAN INI DIPANGGIL

        self.rect.x += self.x_change
        self.rect.y += self.y_change

# KELAS Block DAN Ground (tetap ada tapi Player tidak berinteraksi langsung dengannya)
class Block(pygame.sprite.Sprite): #
    def __init__(self, game, x, y): 
        self.game = game
        self._layer = self.game.config.BLOCK_LAYER 
        
        if not hasattr(self.game, 'all_sprites'): self.game.all_sprites = pygame.sprite.Group()
        if not hasattr(self.game, 'blocks'): self.game.blocks = pygame.sprite.Group()
            
        self.groups = self.game.all_sprites, self.game.blocks 
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * self.game.config.TILESIZE 
        self.y = y * self.game.config.TILESIZE 
        self.width = self.game.config.TILESIZE 
        self.height = self.game.config.TILESIZE 

        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(self.game.config.COLORS.get("blue", (0,0,255))) 

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

class Ground(pygame.sprite.Sprite): #
    def __init__(self, game, x, y): 
        self.game = game
        self._layer = self.game.config.GROUND_LAYER 
        
        if not hasattr(self.game, 'all_sprites'): self.game.all_sprites = pygame.sprite.Group()
        self.groups = self.game.all_sprites 
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * self.game.config.TILESIZE 
        self.y = y * self.game.config.TILESIZE 
        self.width = self.game.config.TILESIZE 
        self.height = self.game.config.TILESIZE 

        ground_image_path = os.path.join(self.game.config.ASSET_PATH, "backgrounds", "Grass 1.png") 
        default_color = self.game.config.COLORS.get("green", (0,255,0))
        try:
            if os.path.exists(ground_image_path):
                if hasattr(self.game.config, 'load_image'):
                     temp_image = self.game.config.load_image(ground_image_path, scale=1.0, use_alpha=False) 
                     self.image = pygame.transform.scale(temp_image, (self.width, self.height))
                else: 
                     loaded_image = pygame.image.load(ground_image_path).convert()
                     self.image = pygame.transform.scale(loaded_image, (self.width, self.height))
            else:
                print(f"--- Ground: PERINGATAN - Tile gambar '{ground_image_path}' tidak ditemukan. Menggunakan warna hijau solid.")
                self.image = pygame.Surface((self.width, self.height))
                self.image.fill(default_color) 
        except Exception as e:
            print(f"--- Ground: ERROR memuat tile gambar '{ground_image_path}': {e}. Menggunakan warna hijau solid.")
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill(default_color) 

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
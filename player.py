# player.py
import pygame
import os
from config import Config

class Player: # Ini adalah PlayerBoat
    def __init__(self, boat, game_instance):
        self.boat = boat
        self.game = game_instance
        self.config = self.game.config

        # --- PERBAIKAN DI SINI: Menggunakan karakter.png sebagai spritesheet ---
        # Kita akan mengambil frame tertentu dari karakter.png
        # Asumsi: karakter.png sudah dimuat ke self.game.character_spritesheet
        
        # Pilih frame dari karakter.png yang sesuai untuk pemain di perahu.
        # Misalnya, frame idle down (0, 114, 34, 34) yang kita gunakan untuk LandPlayer.
        # Atau mungkin ada frame duduk atau frame idle yang lebih kecil yang Anda inginkan.
        # Untuk contoh ini, saya akan menggunakan frame idle down LandPlayer.
        
        sprite_x = 0
        sprite_y = 114 # Y-coordinate untuk idle down (Row 4) dari karakter.png
        sprite_width = 34
        sprite_height = 34

        try:
            # Pastikan self.game.character_spritesheet sudah diinisialisasi
            if self.game.character_spritesheet and hasattr(self.game.character_spritesheet, 'get_sprite'):
                self.image = self.game.character_spritesheet.get_sprite(sprite_x, sprite_y, sprite_width, sprite_height)
                # Skala gambar pemain di perahu jika diperlukan
                scaled_width = int(sprite_width * 0.7) # Skala 0.7 seperti yang sebelumnya
                scaled_height = int(sprite_height * 0.7)
                self.image = pygame.transform.scale(self.image, (scaled_width, scaled_height))
                
                if self.image.get_width() <= 1: # Jika hasil pengambilan sprite sangat kecil
                    print(f"PERINGATAN Player (perahu): Sprite dari karakter.png sangat kecil ({self.image.get_size()}). Menggunakan placeholder darurat.")
                    self.image = pygame.Surface((30, 50), pygame.SRCALPHA)
                    self.image.fill(self.config.COLORS.get("player_map_avatar", (255,0,0, 200)))
            else:
                raise Exception("character_spritesheet tidak ditemukan atau belum dimuat di Game.")

        except Exception as e:
            print(f"ERROR Player (perahu): Tidak bisa memuat sprite dari karakter.png untuk pemain perahu: {e}. Menggunakan placeholder.")
            self.image = pygame.Surface((30, 50), pygame.SRCALPHA)
            self.image.fill(self.config.COLORS.get("player_map_avatar", (255,0,0, 200)))

        self.rect = self.image.get_rect()
        if self.boat and self.boat.rect:
            self.rect.midbottom = self.boat.rect.midtop
        else:
            self.rect.center = (self.config.SCREEN_WIDTH // 2, self.config.SCREEN_HEIGHT // 2)
        
    def update(self, dt):
        if self.boat and self.boat.rect:
            self.rect.centerx = self.boat.rect.centerx
            self.rect.midbottom = self.boat.rect.midtop
        pass

    def handle_event(self, event):
        pass

    def render(self, screen):
        if self.image and self.rect:
            screen.blit(self.image, self.rect)
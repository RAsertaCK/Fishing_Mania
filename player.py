# player.py
import pygame
import os

class Player: 
    def __init__(self, boat, game_instance):
        self.boat = boat 
        self.game = game_instance 
        self.config = self.game.config 

        sprite_x = 0 
        sprite_y = 200 # Y-koordinat sprite pada spritesheet
        sprite_width = 34 
        sprite_height = 34 

        try:
            if self.game.character_spritesheet and hasattr(self.game.character_spritesheet, 'get_sprite'): 
                self.image_original = self.game.character_spritesheet.get_sprite(sprite_x, sprite_y, sprite_width, sprite_height) 
                # Skala sprite pemancing (misal 0.7x dari ukuran asli di spritesheet)
                scaled_width = int(sprite_width * 0.7) 
                scaled_height = int(sprite_height * 0.7) 
                self.image = pygame.transform.scale(self.image_original, (scaled_width, scaled_height)) 
                
                if self.image.get_width() <= 1: 
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
        self.update_position() 
        
    def update_position(self):
        if self.boat and self.boat.rect: 
            self.rect.centerx = self.boat.rect.centerx 
            
            # --- PERUBAHAN DI SINI untuk menurunkan pemancing relatif terhadap perahu ---
            # Ambil posisi midtop perahu
            boat_midtop_x, boat_midtop_y = self.boat.rect.midtop
            
            # Tambahkan offset Y untuk menurunkan pemancing
            # Nilai positif akan menurunkan pemancing. Sesuaikan angka 10 ini.
            y_offset_on_boat = 20
            
            
            self.rect.midbottom = (boat_midtop_x, boat_midtop_y + y_offset_on_boat)
            # --- Akhir Perubahan ---
            
        elif not self.boat: 
            if self.rect is None and self.image: 
                 self.rect = self.image.get_rect()
            if self.rect:
                self.rect.center = (self.config.SCREEN_WIDTH // 2, self.config.SCREEN_HEIGHT // 2)

    def update(self, dt):
        self.update_position() # Pastikan posisi selalu update relatif terhadap perahu

    def handle_event(self, event): 
        pass 

    def render_with_camera(self, screen, camera):
        if self.image and self.rect: 
            screen.blit(self.image, camera.apply(self.rect))
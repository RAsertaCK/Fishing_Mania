# IMPROVE/player.py
import pygame
import os # Untuk os.path.join
from config import Config
# Hapus impor FishingSystem karena Player tidak akan mengelolanya lagi

class Player:
    def __init__(self, boat, game_instance): # Menerima boat dan instance Game
        self.boat = boat
        self.game = game_instance # Simpan referensi ke game jika diperlukan (misalnya untuk akses config)
        self.config = self.game.config # Akses config melalui game instance

        # Path ke aset pemain, pastikan "single.png" ada di assets/player/ atau sesuaikan path
        # Jika "single.png" ada langsung di "assets/", maka path_gambar = os.path.join(self.config.ASSET_PATH, "single.png")
        # Jika ada subfolder "player" di dalam "assets":
        player_image_path = os.path.join(self.config.ASSET_PATH, "player", "single.png")
        # Atau jika memang "single.png" ada di root folder "assets":
        # player_image_path = os.path.join(self.config.ASSET_PATH, "single.png")
        # Untuk sekarang, asumsikan ada folder "player" di dalam "assets"
        # Jika tidak, Anda perlu membuat placeholder atau memastikan pathnya benar.
        # Mari kita coba path yang lebih umum jika "single.png" ada di root "assets"
        # atau jika Anda punya path spesifik di config.
        
        # Coba muat gambar pemain, dengan fallback jika tidak ada
        # Ganti "player_sprite.png" dengan nama file sprite pemain Anda jika berbeda
        # dan pastikan ada di dalam self.config.ASSET_PATH (misalnya assets/player_sprite.png)
        default_player_image_name = "player_sprite.png" # Ganti dengan nama file Anda
        path_gambar_pemain = os.path.join(self.config.ASSET_PATH, default_player_image_name)
        
        # Jika Anda punya path spesifik di Config untuk player:
        # path_gambar_pemain = os.path.join(self.config.PLAYER_SPRITE_PATH, "nama_file.png")

        try:
            self.image = self.config.load_image(path_gambar_pemain, scale=0.7)
            if self.image.get_width() <= 1: # Jika load_image mengembalikan placeholder error
                 print(f"PERINGATAN Player: Gagal memuat gambar pemain dari '{path_gambar_pemain}'. Menggunakan placeholder darurat.")
                 self.image = pygame.Surface((30, 50), pygame.SRCALPHA) # Placeholder darurat
                 self.image.fill(self.config.COLORS.get("player_map_avatar", (255,0,0, 200))) # Warna dari config atau merah
        except Exception as e:
            print(f"ERROR Player: Tidak bisa memuat gambar pemain '{path_gambar_pemain}': {e}. Menggunakan placeholder.")
            self.image = pygame.Surface((30, 50), pygame.SRCALPHA)
            self.image.fill(self.config.COLORS.get("player_map_avatar", (255,0,0, 200)))


        self.rect = self.image.get_rect()
        if self.boat and self.boat.rect: # Pastikan boat dan rect-nya ada
            self.rect.midbottom = self.boat.rect.midtop
        else: # Posisi default jika boat belum siap
            self.rect.center = (self.config.SCREEN_WIDTH // 2, self.config.SCREEN_HEIGHT // 2)
        
        # Player tidak lagi menginisialisasi atau mengelola self.fishing secara langsung
        # print("--- Player: Instance Player dibuat. ---")

    def update(self, dt): # Parameter keys dihapus jika tidak digunakan di sini
        # Update posisi pemain berdasarkan perahu
        if self.boat and self.boat.rect:
            self.rect.centerx = self.boat.rect.centerx
            self.rect.midbottom = self.boat.rect.midtop # Jaga pemain tetap di atas perahu
        # Logika lain untuk update pemain (misalnya animasi) bisa ditambahkan di sini

    def handle_event(self, event):
        # Player mungkin tidak perlu menangani event secara langsung di sini
        # Event yang relevan dengan aksi pemain (seperti memancing) akan ditangani oleh FishingSystem
        # atau state game yang aktif.
        pass

    def render(self, screen):
        # Gambar pemain di layar
        if self.image and self.rect:
            screen.blit(self.image, self.rect)

# IMPROVE/config.py
import pygame
import os

class Config:
    # Display
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    FPS = 60
    DEBUG = True

    # Paths
    ASSET_PATH = "assets/" 
    BACKGROUND_PATH = os.path.join(ASSET_PATH, "backgrounds/") # pastikan ini 'backgrounds'
    BOAT_PATH = os.path.join(ASSET_PATH, "boats/")
    FISH_PATH = os.path.join(ASSET_PATH, "fish/")
    UI_PATH = os.path.join(ASSET_PATH, "ui/")
    FONT_PATH = os.path.join(ASSET_PATH, "fonts/") 
    SOUND_PATH = os.path.join(ASSET_PATH, "sounds/") 
    EFFECTS_PATH = os.path.join(ASSET_PATH, "effects/")

    # Colors
    COLORS = {
        "white": (255, 255, 255),
        "black": (0, 0, 0),
        "blue": (0, 0, 139), # Warna fallback background menu (DarkBlue)
        "text_default": (255, 255, 255),
        "text_selected": (255, 255, 0), 
        "text_inactive": (180, 180, 180),
        "water_deep": (5, 30, 56),
        "water_shallow": (24, 132, 217),
        "common": (100, 200, 100),
        "rare": (100, 100, 255),
        "legendary": (255, 215, 0),
        "player_map_avatar": (255, 0, 0) 
    }

    # Font Settings
    FONT_NAME = None 
    FONT_SIZES = {
        'small': 18, 
        'medium': 30, # Ukuran font untuk opsi menu
        'large': 50,  # Ukuran font untuk judul menu (digunakan jika 'title' tidak ada)
        'title': 60   # Ukuran font spesifik untuk judul menu utama
    }

    @staticmethod
    def load_image(path, scale=1.0, use_alpha=True):
        # print(f"  Mencoba memuat gambar: {path}") 
        try:
            if not os.path.exists(path):
                print(f"  ERROR Config: File gambar tidak ditemukan di path: {path}")
                image = pygame.Surface((50, 50), pygame.SRCALPHA) 
                image.fill((255, 0, 255, 128)) 
                pygame.draw.line(image, (0,0,0), (0,0), (49,49), 1)
                pygame.draw.line(image, (0,0,0), (0,49), (49,0), 1)
                return image

            if use_alpha:
                image = pygame.image.load(path).convert_alpha()
            else:
                image = pygame.image.load(path).convert()

            if scale != 1.0:
                new_size = (int(image.get_width() * scale), int(image.get_height() * scale))
                image = pygame.transform.scale(image, new_size)
            return image
        except pygame.error as e:
            print(f"  ERROR Config saat memuat gambar {path}: {e}")
            image = pygame.Surface((50, 50), pygame.SRCALPHA)
            image.fill((255, 0, 0, 128)) 
            return image

    @staticmethod
    def load_sound(path):
        if not os.path.exists(path):
            print(f"  PERINGATAN Config: File suara tidak ditemukan di path: {path}")
            return None
        try:
            sound = pygame.mixer.Sound(path)
            return sound
        except pygame.error as e:
            print(f"  ERROR Config saat memuat suara {path}: {e}")
            return None

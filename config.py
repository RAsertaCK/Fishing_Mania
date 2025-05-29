# IMPROVE/config.py
import pygame
import os

class Config:
    # ... (Definisi konstanta lainnya tetap sama) ...
    # Display
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    FPS = 60
    DEBUG = True 

    # Paths
    ASSET_PATH = "assets/"
    BACKGROUND_PATH = os.path.join(ASSET_PATH, "backgrounds/") 
    BOAT_PATH = os.path.join(ASSET_PATH, "boats/")
    FISH_PATH = os.path.join(ASSET_PATH, "fish/")
    UI_PATH = os.path.join(ASSET_PATH, "ui/")
    FONT_PATH = os.path.join(ASSET_PATH, "fonts/")
    SOUND_PATH = os.path.join(ASSET_PATH, "sounds/")
    EFFECTS_PATH = os.path.join(ASSET_PATH, "effects/")
    PLAYER_SPRITESHEET_PATH = os.path.join(ASSET_PATH, "player", "karakter.png") 

    # Colors
    COLORS = {
        "white": (255, 255, 255),
        "black": (0, 0, 0),
        "blue": (0, 0, 139), 
        "text_default": (255, 255, 255),
        "text_selected": (255, 255, 0),
        "text_inactive": (180, 180, 180),
        "water_deep": (5, 30, 56), 
        "water_shallow": (24, 132, 217),
        "common": (100, 200, 100),
        "rare": (100, 100, 255),
        "legendary": (255, 215, 0),
        "player_map_avatar": (255, 0, 0),
        "deep_ocean_blue": (25, 33, 70) 
    }
    COLORS["red"] = (255, 0, 0)
    COLORS["green"] = (0, 255, 0)
    COLORS["player_color"] = (100, 100, 255) 

    # Font Settings
    FONT_NAME = None 
    FONT_SIZES = { 'small': 18, 'medium': 30, 'large': 50, 'title': 60 }

    # Game Constants
    TILESIZE = 32 
    PLAYER_LAYER = 2 
    BLOCK_LAYER = 3 
    GROUND_LAYER = 1 
    PLAYER_SPEED = 3 
    PLAYER_SPRITE_SCALE = 2.0

    @staticmethod
    def create_placeholder_surface(width=50, height=50, color=(255, 0, 255, 128)):
        """Membuat surface placeholder standar."""
        image = pygame.Surface((width, height), pygame.SRCALPHA)
        image.fill(color)
        if width >= 2 and height >= 2: # Hanya gambar garis jika cukup besar
             pygame.draw.line(image, (0,0,0), (0,0), (width-1, height-1), 1)
             pygame.draw.line(image, (0,0,0), (0,height-1), (width-1,0), 1)
        return image

    @staticmethod
    def load_image(path, scale=1.0, use_alpha=True):
        # print(f"  Config.load_image: Mencoba memuat gambar: {path}")
        try:
            if not os.path.exists(path):
                # print(f"  ERROR Config: File gambar tidak ditemukan di path: {path}")
                # Kembalikan placeholder jika file tidak ada, JANGAN coba tambah atribut
                return Config.create_placeholder_surface()

            loaded_image = pygame.image.load(path)
            if use_alpha:
                image = loaded_image.convert_alpha()
            else:
                image = loaded_image.convert()

            if scale != 1.0:
                new_size = (int(image.get_width() * scale), int(image.get_height() * scale))
                if new_size[0] <= 0 or new_size[1] <= 0:
                    # print(f"  PERINGATAN Config.load_image: Penskalaan menghasilkan ukuran tidak valid untuk {path}. Menggunakan placeholder error.")
                    return Config.create_placeholder_surface(10, 10, (255,0,0,150)) # Placeholder error skala
                image = pygame.transform.scale(image, new_size)
            
            return image
        except pygame.error as e:
            # print(f"  ERROR Config (pygame error) saat memuat {path}: {e}")
            # Kembalikan placeholder jika ada error pygame, JANGAN coba tambah atribut
            return Config.create_placeholder_surface(color=(255,0,0,128)) # Merah untuk error pygame
        except Exception as ex: # Tangkap error umum lainnya
            # print(f"  ERROR Config (umum) saat memuat {path}: {ex}")
            return Config.create_placeholder_surface(color=(200,200,0,128)) # Kuning untuk error lain

    @staticmethod
    def load_sound(path):
        # ... (kode load_sound tetap sama) ...
        if not os.path.exists(path):
            # print(f"  PERINGATAN Config: File suara tidak ditemukan di path: {path}")
            return None
        try:
            sound = pygame.mixer.Sound(path)
            return sound
        except pygame.error as e:
            # print(f"  ERROR Config saat memuat suara {path}: {e}")
            return None
# config.py
import pygame
import os

class Config:
    # Display
    SCREEN_WIDTH = 1290
    SCREEN_HEIGHT = 720
    FPS = 60
    DEBUG = False # <--- UBAH INI MENJADI FALSE

    # Paths
    # ... (sisa path tetap sama) ...
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
    # ... (warna tetap sama) ...
    COLORS = {
        "white": (255, 255, 255), "black": (0, 0, 0), "blue": (0, 0, 139),
        "text_default": (255, 255, 255), "text_selected": (255, 255, 0),
        "text_inactive": (180, 180, 180), "water_deep": (5, 30, 56), 
        "water_shallow": (24, 132, 217), "common": (100, 200, 100),
        "rare": (100, 100, 255), "legendary": (255, 215, 0),
        "player_map_avatar": (255, 0, 0), "deep_ocean_blue": (25, 33, 70),
        "red": (255,0,0), "green": (0,255,0), "player_color": (100,100,255),
        "yellow": (255,255,0) # Tambahkan jika belum ada, untuk debug rect objek interaktif
    }

    # Font Settings
    FONT_NAME = None 
    FONT_SIZES = { 'small': 18, 'medium': 30, 'large': 50, 'title': 60 }

    # Game Constants
    TILESIZE = 32 
    PLAYER_LAYER = 2 
    BLOCK_LAYER = 3 
    GROUND_LAYER = 1 
    PLAYER_SPEED = 3 # Anda bisa coba naikkan ini jika ingin pemain bergerak lebih cepat/kamera terasa lebih responsif
    PLAYER_SPRITE_SCALE = 1.5

    @staticmethod
    def create_placeholder_surface(width=50, height=50, color=(255, 0, 255, 128)):
        image = pygame.Surface((width, height), pygame.SRCALPHA)
        image.fill(color)
        if width >= 2 and height >= 2: 
             pygame.draw.line(image, (0,0,0,180), (0,0), (width-1, height-1), 1)
             pygame.draw.line(image, (0,0,0,180), (0,height-1), (width-1,0), 1)
        return image

    @staticmethod
    def load_image(path, scale=1.0, use_alpha=True):
        try:
            if not os.path.exists(path):
                # print(f"  ERROR Config: File gambar tidak ditemukan: {path}") # Kurangi print
                return Config.create_placeholder_surface()
            loaded_image = pygame.image.load(path)
            image = loaded_image.convert_alpha() if use_alpha else loaded_image.convert()
            if scale != 1.0:
                original_width, original_height = image.get_size()
                new_width, new_height = int(original_width * scale), int(original_height * scale)
                if new_width <= 0 or new_height <= 0:
                    # print(f"  PERINGATAN Config: Penskalaan '{path}' invalid. Placeholder.") # Kurangi print
                    return Config.create_placeholder_surface(10, 10, (255,0,0,200))
                image = pygame.transform.scale(image, (new_width, new_height))
            return image
        except pygame.error as e:
            # print(f"  ERROR Config (pygame) load '{path}': {e}") # Kurangi print
            return Config.create_placeholder_surface(color=(255,0,0,128))
        except Exception as ex: 
            # print(f"  ERROR Config (umum) load '{path}': {ex}") # Kurangi print
            return Config.create_placeholder_surface(color=(200,200,0,128))
    
    @staticmethod
    def load_sound(path):
        if not os.path.exists(path):
            # print(f"  PERINGATAN Config: File suara tidak ditemukan: {path}") # Kurangi print
            return None
        try: return pygame.mixer.Sound(path)
        except pygame.error as e:
            # print(f"  ERROR Config load suara '{path}': {e}") # Kurangi print
            return None
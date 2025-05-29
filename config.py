# IMPROVE/config.py
import pygame
import os

class Config:
    # Display
    SCREEN_WIDTH = 1290
    SCREEN_HEIGHT = 720
    FPS = 60
    DEBUG = True 

    # Paths
    ASSET_PATH = "assets/" # Pastikan ini adalah direktori utama aset Anda
    BACKGROUND_PATH = os.path.join(ASSET_PATH, "backgrounds/") 
    BOAT_PATH = os.path.join(ASSET_PATH, "boats/") # Tidak terpakai saat ini, tapi path didefinisikan
    FISH_PATH = os.path.join(ASSET_PATH, "fish/")
    UI_PATH = os.path.join(ASSET_PATH, "ui/")
    FONT_PATH = os.path.join(ASSET_PATH, "fonts/")
    SOUND_PATH = os.path.join(ASSET_PATH, "sounds/")
    EFFECTS_PATH = os.path.join(ASSET_PATH, "effects/") # Tidak terpakai saat ini
    PLAYER_SPRITESHEET_PATH = os.path.join(ASSET_PATH, "player", "karakter.png") 

    # Colors
    COLORS = {
        "white": (255, 255, 255),
        "black": (0, 0, 0),
        "blue": (0, 0, 139), # Biru tua solid
        "text_default": (255, 255, 255),
        "text_selected": (255, 255, 0), # Kuning
        "text_inactive": (180, 180, 180), # Abu-abu
        "water_deep": (5, 30, 56), 
        "water_shallow": (24, 132, 217),
        "common": (100, 200, 100), # Hijau muda untuk rarity common
        "rare": (100, 100, 255),   # Biru muda untuk rarity rare
        "legendary": (255, 215, 0), # Emas untuk rarity legendary
        "player_map_avatar": (255, 0, 0), # Merah untuk avatar pemain di peta (jika gambar gagal)
        "deep_ocean_blue": (25, 33, 70) # Warna latar untuk state fishing
    }
    # Tambahan warna jika diperlukan langsung
    COLORS["red"] = (255, 0, 0)
    COLORS["green"] = (0, 255, 0)
    COLORS["player_color"] = (100, 100, 255) # Contoh warna pemain

    # Font Settings
    FONT_NAME = None # Jika None atau string kosong, akan menggunakan SysFont atau pygame.font.Font(None,...)
    FONT_SIZES = { 'small': 18, 'medium': 30, 'large': 50, 'title': 60 }

    # Game Constants (untuk LandExplorer, jika masih relevan)
    TILESIZE = 32 
    PLAYER_LAYER = 2 
    BLOCK_LAYER = 3 
    GROUND_LAYER = 1 
    PLAYER_SPEED = 3 # Kecepatan pemain di darat
    PLAYER_SPRITE_SCALE = 2.0 # Skala sprite pemain di darat

    @staticmethod
    def create_placeholder_surface(width=50, height=50, color=(255, 0, 255, 128)): # Magenta semi-transparan
        """Membuat surface placeholder standar dengan transparansi."""
        image = pygame.Surface((width, height), pygame.SRCALPHA) # Penting: SRCALPHA untuk transparansi
        image.fill(color)
        if width >= 2 and height >= 2: 
             pygame.draw.line(image, (0,0,0,180), (0,0), (width-1, height-1), 1) # Garis silang transparan
             pygame.draw.line(image, (0,0,0,180), (0,height-1), (width-1,0), 1)
        return image

    @staticmethod
    def load_image(path, scale=1.0, use_alpha=True):
        # print(f"  Config.load_image: Mencoba memuat gambar: {path}, skala: {scale}, alpha: {use_alpha}")
        try:
            if not os.path.exists(path):
                print(f"  ERROR Config: File gambar tidak ditemukan di path: {path}")
                return Config.create_placeholder_surface() # Placeholder magenta standar

            loaded_image = pygame.image.load(path)
            if use_alpha:
                # Ini adalah baris kunci untuk transparansi gambar PNG
                image = loaded_image.convert_alpha() 
            else:
                image = loaded_image.convert()

            if scale != 1.0:
                original_width = image.get_width()
                original_height = image.get_height()
                new_width = int(original_width * scale)
                new_height = int(original_height * scale)
                
                if new_width <= 0 or new_height <= 0:
                    print(f"  PERINGATAN Config.load_image: Penskalaan untuk '{path}' menghasilkan ukuran tidak valid ({new_width}x{new_height}). Menggunakan placeholder error skala.")
                    return Config.create_placeholder_surface(10, 10, (255,0,0,200)) # Placeholder merah kecil semi-transparan
                
                # print(f"    Config.load_image: Menskalakan '{os.path.basename(path)}' dari {original_width}x{original_height} ke {new_width}x{new_height}")
                image = pygame.transform.scale(image, (new_width, new_height))
            
            # print(f"    Config.load_image: Berhasil memuat dan memproses '{os.path.basename(path)}'. Ukuran akhir: {image.get_size()}")
            return image
        except pygame.error as e:
            print(f"  ERROR Config (pygame error) saat memuat '{path}': {e}")
            return Config.create_placeholder_surface(color=(255,0,0,128)) # Placeholder merah semi-transparan untuk error pygame
        except Exception as ex: 
            print(f"  ERROR Config (umum) saat memuat '{path}': {ex}")
            return Config.create_placeholder_surface(color=(200,200,0,128)) # Placeholder kuning semi-transparan untuk error lain
    
    @staticmethod
    def load_sound(path):
        if not os.path.exists(path):
            print(f"  PERINGATAN Config: File suara tidak ditemukan di path: {path}")
            return None
        try:
            sound = pygame.mixer.Sound(path)
            return sound
        except pygame.error as e:
            print(f"  ERROR Config saat memuat suara '{path}': {e}")
            return None
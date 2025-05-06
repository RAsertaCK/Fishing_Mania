# config.py
import pygame
import os

class Config:
    # Display
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    FPS = 60
    
    # Paths
    ASSET_PATH = "assets/"
    BG_PATH = os.path.join(ASSET_PATH, "backgrounds/")
    BOAT_PATH = os.path.join(ASSET_PATH, "boats/")
    FISH_PATH = os.path.join(ASSET_PATH, "fish/")
    UI_PATH = os.path.join(ASSET_PATH, "ui/")
    EFFECTS_PATH = os.path.join(ASSET_PATH, "effects/")
    
    # Colors
    COLORS = {
        "water_deep": (5, 30, 56),
        "water_shallow": (24, 132, 217),
        "text": (255, 255, 255),
        "text_shadow": (0, 0, 0),
        "common": (100, 200, 100),
        "rare": (100, 100, 255),
        "legendary": (255, 215, 0)
    }
    
    @staticmethod
    def load_image(path, scale=1.0):
        try:
            image = pygame.image.load(path).convert_alpha()
            if scale != 1.0:
                new_size = (int(image.get_width() * scale), int(image.get_height() * scale))
                image = pygame.transform.scale(image, new_size)
            return image
        except:
            print(f"Failed to load image: {path}")
            # Return blank surface as fallback
            surf = pygame.Surface((32, 32), pygame.SRCALPHA)
            surf.fill((255, 0, 255))  # Magenta as error color
            return surf
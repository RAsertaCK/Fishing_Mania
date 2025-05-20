import os  # Import the os module
import pygame

class Config:
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    FPS = 60

    ASSET_PATH = "assets"
    BOAT_PATH = os.path.join(ASSET_PATH, "Boat")
    FISH_PATH = os.path.join(ASSET_PATH, "Fish")
    UI_PATH = os.path.join(ASSET_PATH, "UI")
    BACKGROUND_PATH = os.path.join(ASSET_PATH, "Background")
    SOUND_PATH = os.path.join(ASSET_PATH, "sounds")

    COLORS = {
        "common": (100, 200, 100),
        "rare": (100, 100, 255),
        "legendary": (255, 215, 0),
        "text": (255, 255, 255)
    }

    @staticmethod
    def load_image(path, scale=1.0):
        try:
            image = pygame.image.load(path).convert_alpha()
            if scale != 1.0:
                size = (int(image.get_width() * scale), int(image.get_height() * scale))
                image = pygame.transform.scale(image, size)
            return image
        except Exception as e:
            print(f"Failed to load image: {path}. Error: {e}")
            surface = pygame.Surface((32, 32), pygame.SRCALPHA)
            surface.fill((255, 0, 255))
            return surface
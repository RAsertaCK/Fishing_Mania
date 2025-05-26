import os
import random
from config import Config  # Ensure 'Config' is defined in a module named 'config'

from boat import Boat  # Ensure 'Boat' is defined in a module named 'boat'

class GameMap:
    def __init__(self, name):
        self.name = name
        self.data = {
            "name": name,
            "color": Config.COLORS["common"]  # Use Config.COLORS
        }
    
    # self.boat initialization moved to the __init__ method
    
    LOCATIONS = {
        "Coast": {
            "fish": [
                {"name": "Sea Bass", "rarity": "common", "value": 10},
                {"name": "Red Snapper", "rarity": "common", "value": 15},
                {"name": "Crab", "rarity": "rare", "value": 40}
            ],
            "depth_range": (10, 30),
            "color": Config.COLORS["common"]
        },
        "Sea": {
            "fish": [
                {"name": "Tuna", "rarity": "rare", "value": 80},
                {"name": "Swordfish", "rarity": "rare", "value": 100},
                {"name": "Shark", "rarity": "legendary", "value": 250}
            ],
            "depth_range": (50, 100),
            "color": Config.COLORS["rare"]
        },
        "Ocean": {
            "fish": [
                {"name": "Blue Marlin", "rarity": "legendary", "value": 500},
                {"name": "Whale", "rarity": "legendary", "value": 1000}
            ],
            "depth_range": (100, 200),
            "color": Config.COLORS["legendary"]
        }
    }
    
    def __init__(self, name):
        self.map = name  # Initialize self.map
        self.boat = Boat(self.map)  # Pass game_map to Boat
        self.map = name  # Initialize self.map
        self.name = name
        self.boat = Boat(self.map)  # Pass game_map to Boat
        self.data = self.LOCATIONS.get(name, self.LOCATIONS["Coast"])
        bg_filename = f"bg_{name.lower()}.png"
        self.background = Config.load_image(os.path.join(Config.ASSET_PATH, "Background", bg_filename))

    def render(self, screen):
        screen.blit(self.background, (0, 0))

    def get_random_fish(self):
        fish_pool = self.data["fish"]
        weights = [0.7 if f["rarity"] == "common" else 0.25 if f["rarity"] == "rare" else 0.05 for f in fish_pool]
        return random.choices(fish_pool, weights=weights, k=1)[0]
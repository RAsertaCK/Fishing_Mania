# game_map.py
from config import Config
import random
import os

class GameMap:
    LOCATIONS = {
        "Coast": {
            "fish": [
                {"name": "Sea Bass", "rarity": "common", "value": 15},
                {"name": "Red Snapper", "rarity": "common", "value": 20},
                {"name": "Blue Crab", "rarity": "rare", "value": 50}
            ],
            "depth_range": (10, 30),
            "color": Config.COLORS["water_shallow"]
        },
        "Sea": {
            "fish": [
                {"name": "Tuna", "rarity": "rare", "value": 80},
                {"name": "Swordfish", "rarity": "rare", "value": 100},
                {"name": "Mako Shark", "rarity": "legendary", "value": 250}
            ],
            "depth_range": (50, 100),
            "color": Config.COLORS["water_deep"]
        },
        "Ocean": {
            "fish": [
                {"name": "Blue Marlin", "rarity": "legendary", "value": 500},
                {"name": "Sailfish", "rarity": "rare", "value": 150},
                {"name": "Whale Shark", "rarity": "legendary", "value": 1000}
            ],
            "depth_range": (100, 200),
            "color": (3, 4, 94)  # Deep ocean blue
        }
    }

    def __init__(self, name):
        self.name = name
        self.data = self.LOCATIONS[name]
        self.background = Config.load_image(os.path.join(Config.BG_PATH, f"bg_{name.lower()}.png"))
        
        # Dynamic fishing difficulty based on time
        self.time_of_day = "day"  # Can change to 'night' for different fish
        self.weather = "sunny"   # Can affect fish behavior
        
    def get_random_fish(self):
        # Weighted random selection based on rarity
        weights = {
            "common": 0.7,
            "rare": 0.25,
            "legendary": 0.05
        }
        
        fish_pool = []
        for fish in self.data["fish"]:
            fish_pool.append((fish, weights[fish["rarity"]]))
        
        # Random selection with weights
        fish = random.choices(
            [f[0] for f in fish_pool],
            weights=[f[1] for f in fish_pool],
            k=1
        )[0]
        
        return fish
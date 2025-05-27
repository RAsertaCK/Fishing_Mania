# IMPROVE/game_map.py
import pygame 
import os
import random

class GameMap:
    LOCATIONS = {
        "Coast": { 
            "display_name": "Pantai Lokal", 
            "fish_data_list": [ 
                {"name": "Ikan Teri", "rarity": "common", "value": 10, "image_suffix": "teri"},
                {"name": "Ikan Kembung", "rarity": "common", "value": 15, "image_suffix": "kembung"},
                {"name": "Kepiting Kecil", "rarity": "rare", "value": 40, "image_suffix": "kepiting_kecil"}
            ],
            "background_file": "bg_coast.png", 
            "depth_range": (50, 150), 
            "music": "coast_theme.ogg" 
        },
        "Sea": {
            "display_name": "Laut Lepas",
            "fish_data_list": [
                {"name": "Tuna Sirip Kuning", "rarity": "rare", "value": 75, "image_suffix": "tuna_kuning"},
                {"name": "Ikan Todak", "rarity": "rare", "value": 120, "image_suffix": "todak"},
                {"name": "Hiu Karang", "rarity": "legendary", "value": 280, "image_suffix": "hiu_karang"}
            ],
            "background_file": "bg_sea.png",
            "depth_range": (100, 300),
            "music": "sea_theme.ogg"
        },
        "Ocean": {
            "display_name": "Samudra Dalam",
            "fish_data_list": [
                {"name": "Marlin Biru", "rarity": "legendary", "value": 550, "image_suffix": "marlin_biru"},
                {"name": "Gurita Raksasa", "rarity": "legendary", "value": 700, "image_suffix": "gurita_raksasa"},
                {"name": "Paus Bungkuk (Anakan)", "rarity": "legendary", "value": 1200, "image_suffix": "paus_bungkuk_anakan"}
            ],
            "background_file": "bg_ocean.png", 
            "depth_range": (200, 500),
            "music": "ocean_theme.ogg"
        }
    }

    def __init__(self, location_map_name, config_instance): 
        self.config = config_instance
        self.name = location_map_name 
        
        if location_map_name not in self.LOCATIONS:
            print(f"    ERROR: Lokasi '{location_map_name}' tidak ditemukan di GameMap.LOCATIONS!")
            fallback_location = next(iter(self.LOCATIONS), None)
            if not fallback_location:
                raise ValueError("Tidak ada lokasi yang terdefinisi di GameMap.LOCATIONS")
            self.name = fallback_location
        
        self.data = self.LOCATIONS[self.name]
        self.display_name = self.data.get("display_name", self.name) 
        
        default_map_color = self.config.COLORS.get('water_deep', (10,20,70))
        self.map_color = self.data.get('color', default_map_color) 

        bg_filename = self.data.get("background_file", f"bg_{self.name.lower().replace(' ', '_')}.png")
        bg_path = os.path.join(self.config.BACKGROUND_PATH, bg_filename)
        try:
            self.background_image = self.config.load_image(bg_path)
            if self.background_image.get_size() != (self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT):
                self.background_image = pygame.transform.scale(self.background_image, (self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT))
        except Exception as e:
            print(f"    ERROR memuat background untuk GameMap {self.name}: {e}. Menggunakan warna solid.")
            self.background_image = pygame.Surface((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT))
            self.background_image.fill(self.map_color)

    def get_random_fish_data(self):
        fish_pool = self.data.get("fish_data_list", [])
        if not fish_pool:
            return None

        weights = []
        for fish_d in fish_pool:
            rarity = fish_d.get("rarity", "common")
            if rarity == "common": weights.append(70)
            elif rarity == "rare": weights.append(25)
            elif rarity == "legendary": weights.append(5)
            else: weights.append(10) 
        
        if not weights or sum(weights) == 0 : 
            return random.choice(fish_pool) if fish_pool else None

        chosen_fish_data = random.choices(fish_pool, weights=weights, k=1)[0]
        return chosen_fish_data

    def play_music(self):
        music_file = self.data.get("music")
        if music_file:
            music_path = os.path.join(self.config.SOUND_PATH, music_file)
            if os.path.exists(music_path):
                try:
                    pygame.mixer.music.load(music_path)
                    pygame.mixer.music.play(-1, fade_ms=1000) 
                    # print(f"Memainkan musik: {music_file}")
                except pygame.error as e:
                    print(f"Error memainkan musik {music_file}: {e}")
            # else:
                # print(f"File musik tidak ditemukan: {music_path}")
        # else:
            # pygame.mixer.music.fadeout(1000) 
            # print("Musik dihentikan (tidak ada musik untuk lokasi ini).")
            pass

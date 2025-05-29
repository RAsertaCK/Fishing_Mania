# Fishing_Mania-master/game_map.py
import pygame
import os
import random

class GameMap:
    LOCATIONS = {
        "Coast": {
            "display_name": "Pantai Lokal",
            "fish_data_list": [
                {"name": "Red Snapper", "rarity": "common", "value": 25, "image_suffix": "red_snapper"},
                {"name": "Sea Bass", "rarity": "common", "value": 30, "image_suffix": "sea_bass"},
            ],
            "background_file": "Pantai.png", 
            "depth_range": (50, 150), 
            "music": "coast_theme.ogg" 
        },
        "Sea": {
            "display_name": "Laut Lepas",
            "fish_data_list": [
                {"name": "Ikan Trout", "rarity": "rare", "value": 60, "image_suffix": "ikan_trout"},
                {"name": "Tuna", "rarity": "rare", "value": 100, "image_suffix": "tuna"}, 
                {"name": "Swordfish", "rarity": "rare", "value": 150, "image_suffix": "swordfish"}, 
            ],
            "background_file": "Lautan.png", 
            "depth_range": (100, 300), 
            "music": "sea_theme.ogg" 
        },
        "Ocean": {
            "display_name": "Samudra Dalam",
            "fish_data_list": [
                {"name": "Blue Marlin", "rarity": "legendary", "value": 550, "image_suffix": "blue_marlin"}, 
                {"name": "Shark", "rarity": "legendary", "value": 400, "image_suffix": "shark"}, 
                {"name": "Whale", "rarity": "legendary", "value": 1000, "image_suffix": "whale"} 
            ],
            "background_file": "Samudra.png", 
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
        
        default_map_color = self.config.COLORS.get('water_deep', (10,20,70)) #
        self.map_color = self.data.get('color', default_map_color) 

        bg_filename = self.data.get("background_file") 
        if not bg_filename: 
            print(f"    PERINGATAN: background_file tidak didefinisikan untuk lokasi {self.name}. Menggunakan default.") 
            bg_filename = f"default_background_{self.name.lower()}.png" 
            
        bg_path = os.path.join(self.config.BACKGROUND_PATH, bg_filename) #
        
        self.background_image_original = None 
        self.background_image = None # Ini akan menjadi versi yang diskalakan dengan benar

        placeholder_surface = pygame.Surface((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT)) #
        placeholder_surface.fill(self.map_color) 

        try:
            # Muat gambar asli tanpa penskalaan awal di Config.load_image (jika memungkinkan)
            # Jika Config.load_image selalu menskalakan, kita perlu gambar asli
            self.background_image_original = self.config.load_image(bg_path, scale=1.0) #

            if hasattr(self.background_image_original, '_debug_load_error_message') or \
               (self.background_image_original.get_width() <= 1 and not os.path.exists(bg_path)): # Cek jika ini placeholder dari load_image
                print(f"    ERROR GameMap: Gagal memuat background original '{bg_path}'. Menggunakan warna solid.")
                self.background_image_original = placeholder_surface
                self.background_image = placeholder_surface
            else:
                # ---- PENYESUAIAN SKALA GAMBAR LATAR ----
                original_width = self.background_image_original.get_width()
                original_height = self.background_image_original.get_height()

                # Skalakan agar PAS DENGAN LEBAR LAYAR, jaga aspek rasio
                if original_width != self.config.SCREEN_WIDTH: #
                    aspect_ratio = original_height / original_width
                    scaled_height = int(self.config.SCREEN_WIDTH * aspect_ratio) #
                    self.background_image = pygame.transform.scale(self.background_image_original, (self.config.SCREEN_WIDTH, scaled_height)) #
                    print(f"    GameMap: BG '{bg_filename}' diskalakan ke ({self.config.SCREEN_WIDTH}, {scaled_height}) menjaga aspek rasio lebar.") #
                else:
                    # Jika lebar sudah pas, cek apakah tingginya juga pas atau perlu diskalakan
                    # Untuk tampilan seperti di screenshot, kita ingin background mengisi layar.
                    # Jika tingginya berbeda dari SCREEN_HEIGHT, kita bisa skala agar pas tinggi juga,
                    # atau biarkan dan potong/letterbox. Untuk sekarang, jika lebar pas, gunakan apa adanya.
                    self.background_image = self.background_image_original 
                
                # Jika setelah penskalaan (atau tidak ada penskalaan) tingginya masih beda jauh dari SCREEN_HEIGHT,
                # mungkin perlu strategi lain, tapi untuk sekarang ini akan mengisi lebar.
                # Jika ingin background selalu pas SCREEN_WIDTH x SCREEN_HEIGHT (mungkin stretch):
                # self.background_image = pygame.transform.scale(self.background_image_original, (self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT))


        except Exception as e:
            print(f"    ERROR memuat background untuk GameMap {self.name}: {e}. Menggunakan warna solid.") 
            self.background_image_original = placeholder_surface # Fallback
            self.background_image = placeholder_surface

    def get_random_fish_data(self):
        # ... (kode get_random_fish_data tetap sama) ...
        fish_pool = self.data.get("fish_data_list", []) 
        if not fish_pool: 
            print(f"PERINGATAN: Tidak ada ikan di fish_pool untuk lokasi {self.name}")
            return None 

        weights = [] 
        for fish_d in fish_pool: 
            rarity = fish_d.get("rarity", "common") 
            if rarity == "common": weights.append(70) 
            elif rarity == "rare": weights.append(25) 
            elif rarity == "legendary": weights.append(5) 
            else: weights.append(10)
        
        if not weights or sum(weights) == 0 : 
            if fish_pool:
                print(f"PERINGATAN: Bobot tidak valid atau nol untuk fish_pool di {self.name}, memilih secara acak.")
                return random.choice(fish_pool)
            return None

        chosen_fish_data = random.choices(fish_pool, weights=weights, k=1)[0] 
        return chosen_fish_data 


    def play_music(self):
        # ... (kode play_music tetap sama) ...
        music_file = self.data.get("music") 
        if music_file: 
            music_path = os.path.join(self.config.SOUND_PATH, music_file) #
            if os.path.exists(music_path): 
                try:
                    pygame.mixer.music.load(music_path) 
                    pygame.mixer.music.play(-1, fade_ms=1000) 
                except pygame.error as e: 
                    print(f"Error memainkan musik {music_file}: {e}")
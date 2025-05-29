import json
import os

class GameData:
    def __init__(self, game_instance, save_file_name="save_game.json"):
        self.game = game_instance # Referensi ke instance Game utama
        # Path untuk file save game, misalnya di folder 'saves'
        self.save_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saves", save_file_name)
        
        self.data = self._get_initial_data()
        self._ensure_save_directory_exists()

        print(f"--- GameData: Inisialisasi dengan save file: {self.save_file_path} ---")

    def _get_initial_data(self):
        """Mengembalikan struktur data default untuk game baru."""
        return {
            "coins": 100, # Koin awal game
            "boat_upgrades": {
                "speed": 0,
                "capacity": 0,
                "line_length": 0
            },
            "unlocked_locations": {
                "Coast": True,  # Pantai Lokal selalu terbuka
                "Sea": False,
                "Ocean": False
            },
            "collected_fish": [], # Contoh: [{"name": "Red Snapper", "rarity": "common", "value": 25, "image_suffix": "red_snapper"}, ...]
            "player_map_position": {"x": self.game.config.SCREEN_WIDTH * 0.6, "y": self.game.config.SCREEN_HEIGHT * 0.65}, # Posisi default kapal di map_explore
            "current_game_state": "main_menu" # State terakhir saat save (opsional)
        }

    def _ensure_save_directory_exists(self):
        """Memastikan direktori untuk file save game ada."""
        save_dir = os.path.dirname(self.save_file_path)
        if save_dir and not os.path.exists(save_dir):
            try:
                os.makedirs(save_dir)
                print(f"--- GameData: Direktori save game dibuat: {save_dir} ---")
            except OSError as e:
                print(f"--- GameData ERROR: Gagal membuat direktori save game {save_dir}: {e} ---")

    def save_game(self):
        """
        Menyimpan data game saat ini ke file JSON.
        Data diambil dari atribut game utama.
        """
        self.data["coins"] = self.game.wallet
        
        if self.game.boat and hasattr(self.game.boat, 'upgrades'):
            self.data["boat_upgrades"] = self.game.boat.upgrades
        
        if self.game.unlocked_locations:
            self.data["unlocked_locations"] = self.game.unlocked_locations
        
        if self.game.inventory and hasattr(self.game.inventory, 'fish_list'):
            # Simpan data dasar ikan, bukan objek Fish itu sendiri
            self.data["collected_fish"] = [fish.get_data() for fish in self.game.inventory.fish_list]
        
        if self.game.current_state_name == 'map_explore' and self.game.map_explorer and hasattr(self.game.map_explorer, 'player_map_rect'):
            player_map_rect = self.game.map_explorer.player_map_rect
            if player_map_rect:
                self.data["player_map_position"] = {"x": player_map_rect.centerx, "y": player_map_rect.centery}
        
        self.data["current_game_state"] = self.game.current_state_name # Simpan state terakhir

        try:
            with open(self.save_file_path, 'w') as f:
                json.dump(self.data, f, indent=4)
            print(f"--- GameData: Game berhasil disimpan ke: {self.save_file_path} ---")
            return True
        except IOError as e:
            print(f"--- GameData ERROR: Gagal menyimpan game ke {self.save_file_path}: {e} ---")
            return False

    def load_game(self):
        """
        Memuat data game dari file JSON dan menerapkan ke atribut game utama.
        """
        if not os.path.exists(self.save_file_path):
            print(f"--- GameData: File save game tidak ditemukan di {self.save_file_path}. Tidak ada yang dimuat. ---")
            return False

        try:
            with open(self.save_file_path, 'r') as f:
                loaded_data = json.load(f)
                
                # Memastikan semua kunci yang diharapkan ada di data yang dimuat.
                # Ini penting untuk kompatibilitas jika struktur data berubah.
                default_data = self._get_initial_data()
                for key, default_value in default_data.items():
                    if key not in loaded_data:
                        loaded_data[key] = default_value
                
                self.data = loaded_data # Update internal data

                # Terapkan data yang dimuat ke instance Game
                self.game.wallet = self.data.get("coins", default_data["coins"])
                print(f"--- GameData: Koin dimuat: {self.game.wallet} ---")

                if self.game.boat and hasattr(self.game.boat, 'upgrades'):
                    upgrades_to_load = self.data.get("boat_upgrades", default_data["boat_upgrades"])
                    self.game.boat.upgrades = upgrades_to_load
                    # Pastikan nilai speed, capacity, line_length diupdate sesuai level upgrade
                    for upgrade_type, level in self.game.boat.upgrades.items():
                        if upgrade_type in self.game.boat.UPGRADE_LEVELS and level < len(self.game.boat.UPGRADE_LEVELS[upgrade_type]):
                            if upgrade_type == "speed":
                                self.game.boat.current_speed_value = self.game.boat.UPGRADE_LEVELS["speed"][level]
                            elif upgrade_type == "capacity":
                                self.game.boat.current_capacity_value = self.game.boat.UPGRADE_LEVELS["capacity"][level]
                            elif upgrade_type == "line_length":
                                self.game.boat.current_line_length_value = self.game.boat.UPGRADE_LEVELS["line_length"][level]
                    print(f"--- GameData: Upgrade kapal dimuat: {self.game.boat.upgrades} ---")

                if self.game.unlocked_locations:
                    self.game.unlocked_locations = self.data.get("unlocked_locations", default_data["unlocked_locations"])
                    print(f"--- GameData: Lokasi terbuka dimuat: {self.game.unlocked_locations} ---")

                if self.game.inventory:
                    from fish import Fish # Impor Fish di sini untuk menghindari circular import jika Fish mengimpor GameData
                    self.game.inventory.fish_list.clear() # Kosongkan inventaris sebelum memuat
                    collected_fish_data = self.data.get("collected_fish", default_data["collected_fish"])
                    for fish_dict in collected_fish_data:
                        # Buat ulang objek Fish dari data yang disimpan
                        # Perhatikan: pos (0,0) adalah dummy karena ikan di inventaris tidak punya posisi di dunia
                        self.game.inventory.add_fish_from_data(fish_dict)
                    print(f"--- GameData: Koleksi ikan dimuat: {len(self.game.inventory.fish_list)} ikan ---")
                
                # Posisi pemain di peta dunia (Map Explorer)
                player_map_pos = self.data.get("player_map_position", default_data["player_map_position"])
                if self.game.map_explorer and hasattr(self.game.map_explorer, 'player_map_rect'):
                    self.game.map_explorer.player_map_rect.centerx = player_map_pos["x"]
                    self.game.map_explorer.player_map_rect.centery = player_map_pos["y"]
                    print(f"--- GameData: Posisi pemain di peta dimuat: ({player_map_pos['x']:.0f}, {player_map_pos['y']:.0f}) ---")
                
                # State game terakhir (bisa digunakan untuk melanjutkan game)
                self.game.current_state_name = self.data.get("current_game_state", default_data["current_game_state"])
                print(f"--- GameData: State game terakhir dimuat: {self.game.current_state_name} ---")

            print(f"--- GameData: Game berhasil dimuat dari: {self.save_file_path} ---")
            return True
        except FileNotFoundError:
            print(f"--- GameData ERROR: File save game tidak ditemukan di {self.save_file_path}. ---")
            return False
        except json.JSONDecodeError as e:
            print(f"--- GameData ERROR: Kesalahan saat membaca file JSON '{self.save_file_path}': {e}. File mungkin rusak. ---")
            return False
        except Exception as e:
            print(f"--- GameData ERROR: Terjadi kesalahan tidak terduga saat memuat game: {e} ---")
            return False

    def reset_game_data(self):
        """Mengatur ulang semua data game ke nilai awal dan menyimpannya."""
        print("--- GameData: Mereset semua data game ke nilai awal. ---")
        self.data = self._get_initial_data()
        self.save_game() # Simpan data yang direset
        # Terapkan juga ke game instance saat ini
        self.game.wallet = self.data["coins"]
        if self.game.boat and hasattr(self.game.boat, 'upgrades'):
            self.game.boat.upgrades = self.data["boat_upgrades"]
            # Perbarui nilai atribut boat juga
            self.game.boat.current_speed_value = self.game.boat.UPGRADE_LEVELS["speed"][self.game.boat.upgrades["speed"]]
            self.game.boat.current_capacity_value = self.game.boat.UPGRADE_LEVELS["capacity"][self.game.boat.upgrades["capacity"]]
            self.game.boat.current_line_length_value = self.game.boat.UPGRADE_LEVELS["line_length"][self.game.boat.upgrades["line_length"]]
        
        self.game.unlocked_locations = self.data["unlocked_locations"]
        if self.game.inventory:
            self.game.inventory.fish_list.clear() # Kosongkan inventaris
        if self.game.map_explorer and hasattr(self.game.map_explorer, 'player_map_rect'):
            self.game.map_explorer.player_map_rect.centerx = self.data["player_map_position"]["x"]
            self.game.map_explorer.player_map_rect.centery = self.data["player_map_position"]["y"]
        self.game.current_state_name = self.data["current_game_state"]
# game_data.py
import json
import os
import traceback 

class GameData:
    def __init__(self, game_instance, save_file_name="save_game.json"):
        # print("--- DEBUG GameData: __init__ MULAI ---") # Kurangi DEBUG jika sudah stabil
        self.game = game_instance
        self.save_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saves", save_file_name)
        
        self.data = self._get_initial_data() 
        self._ensure_save_directory_exists()
        # print(f"--- GameData: Inisialisasi dengan save file: {self.save_file_path} ---") # Kurangi DEBUG
        # print("--- DEBUG GameData: __init__ SELESAI ---")

    def _get_initial_data(self):
        # print("--- DEBUG GameData: _get_initial_data DIPANGGIL ---") # Kurangi DEBUG
        screen_width_default = 1280 
        screen_height_default = 720
        current_game_ref = getattr(self, 'game', None)
        current_config_ref = getattr(current_game_ref, 'config', None)
        if current_config_ref:
            screen_width_default = getattr(current_config_ref, 'SCREEN_WIDTH', screen_width_default)
            screen_height_default = getattr(current_config_ref, 'SCREEN_HEIGHT', screen_height_default)
        initial_data_struct = {
            "coins": 100, # Nilai default untuk reset penuh
            "boat_upgrades": {"speed": 0, "capacity": 0, "line_length": 0},
            "unlocked_locations": {"Coast": True, "Sea": False, "Ocean": False},
            "collected_fish": [], 
            "player_map_position": {"x": screen_width_default * 0.6, "y": screen_height_default * 0.65}, 
            "current_game_state": "main_menu"
        }
        return initial_data_struct

    def _ensure_save_directory_exists(self):
        save_dir = os.path.dirname(self.save_file_path)
        if save_dir and not os.path.exists(save_dir):
            try: os.makedirs(save_dir); print(f"--- GameData: Direktori save game dibuat: {save_dir} ---")
            except OSError as e: print(f"--- GameData ERROR: Gagal membuat direktori save game {save_dir}: {e} ---")

    def save_game(self):
        # print(f"--- DEBUG GameData: save_game DIPANGGIL. self.game.wallet: {getattr(getattr(self, 'game', None), 'wallet', 'N/A')} ---")
        if hasattr(self.game, 'wallet'): self.data["coins"] = self.game.wallet
        if hasattr(self.game, 'boat') and self.game.boat and hasattr(self.game.boat, 'upgrades'): self.data["boat_upgrades"] = self.game.boat.upgrades.copy()
        if hasattr(self.game, 'unlocked_locations'): self.data["unlocked_locations"] = self.game.unlocked_locations.copy()
        if hasattr(self.game, 'inventory') and self.game.inventory and hasattr(self.game.inventory, 'fish_list'):
            self.data["collected_fish"] = [fish.get_data() for fish in self.game.inventory.fish_list if hasattr(fish, 'get_data')]
        player_map_pos_to_save = None
        if hasattr(self.game, 'map_explorer') and self.game.map_explorer:
            if hasattr(self.game.map_explorer, 'player_map_rect') and self.game.map_explorer.player_map_rect:
                player_map_pos_to_save = {"x": self.game.map_explorer.player_map_rect.centerx, "y": self.game.map_explorer.player_map_rect.centery}
            elif hasattr(self.game.map_explorer, 'player_world_pos'):
                 player_map_pos_to_save = {"x": self.game.map_explorer.player_world_pos[0], "y": self.game.map_explorer.player_world_pos[1]}
        if player_map_pos_to_save: self.data["player_map_position"] = player_map_pos_to_save
        if hasattr(self.game, 'current_state_name'): self.data["current_game_state"] = self.game.current_state_name
        # print(f"--- DEBUG GameData: save_game - Data yang AKAN DISIMPAN: Koin={self.data.get('coins')} ---")
        try:
            with open(self.save_file_path, 'w') as f: json.dump(self.data, f, indent=4)
            print(f"--- GameData: Game berhasil disimpan. Koin DISIMPAN: {self.data.get('coins')}. Ke: {self.save_file_path} ---")
            return True
        except Exception as e: print(f"--- GameData ERROR: Kesalahan saat menyimpan game: {e} ---"); traceback.print_exc(); return False

    def load_game(self):
        # print(f"--- DEBUG GameData: load_game DIPANGGIL: {self.save_file_path} ---")
        if not os.path.exists(self.save_file_path):
            print(f"--- GameData: File save tidak ditemukan. Menggunakan data default. ---")
            self.data = self._get_initial_data()
            self._apply_data_to_game_instance(self.data, "file_not_found_init")
            return False
        try:
            with open(self.save_file_path, 'r') as f: loaded_data_from_file = json.load(f)
            default_data_template = self._get_initial_data()
            final_loaded_data = default_data_template.copy(); final_loaded_data.update(loaded_data_from_file)
            self.data = final_loaded_data
            self._apply_data_to_game_instance(self.data, "load_success")
            print(f"--- GameData: Game berhasil dimuat dari: {self.save_file_path} ---")
            return True
        except Exception as e:
            print(f"--- GameData ERROR: Gagal memuat game: {e}. Menggunakan data default. ---"); traceback.print_exc()
            self.data = self._get_initial_data(); self._apply_data_to_game_instance(self.data, "load_exception_fallback"); return False

    def _apply_data_to_game_instance(self, data_to_apply, call_source="unknown"):
        # print(f"--- DEBUG GameData: _apply_data_to_game_instance DIPANGGIL dari '{call_source}'. Menerapkan Koin: {data_to_apply.get('coins')} ---")
        default_template = self._get_initial_data()
        if hasattr(self.game, 'wallet'): self.game.wallet = data_to_apply.get("coins", default_template["coins"])
        if hasattr(self.game, 'boat') and self.game.boat:
            boat_upgrades_data = data_to_apply.get("boat_upgrades", default_template["boat_upgrades"])
            self.game.boat.upgrades = boat_upgrades_data.copy()
            speed_level=min(boat_upgrades_data.get("speed",0),len(self.game.boat.UPGRADE_LEVELS["speed"])-1)
            capacity_level=min(boat_upgrades_data.get("capacity",0),len(self.game.boat.UPGRADE_LEVELS["capacity"])-1)
            line_length_level=min(boat_upgrades_data.get("line_length",0),len(self.game.boat.UPGRADE_LEVELS["line_length"])-1)
            self.game.boat.current_speed_value = self.game.boat.UPGRADE_LEVELS["speed"][speed_level]
            self.game.boat.current_capacity_value = self.game.boat.UPGRADE_LEVELS["capacity"][capacity_level]
            self.game.boat.current_line_length_value = self.game.boat.UPGRADE_LEVELS["line_length"][line_length_level]
        if hasattr(self.game, 'unlocked_locations'): self.game.unlocked_locations = data_to_apply.get("unlocked_locations", default_template["unlocked_locations"]).copy()
        if hasattr(self.game, 'inventory') and self.game.inventory:
            self.game.inventory.fish_list.clear()
            collected_fish_data = data_to_apply.get("collected_fish", default_template["collected_fish"])
            if collected_fish_data:
                try:
                    from fish import Fish
                    for fish_dict in collected_fish_data: self.game.inventory.add_fish_from_data(fish_dict)
                except Exception as e_fish: print(f"--- GameData ERROR: Gagal proses data ikan: {e_fish}")
        map_pos_data = data_to_apply.get("player_map_position", default_template["player_map_position"])
        if hasattr(self.game, 'map_explorer') and self.game.map_explorer:
            if hasattr(self.game.map_explorer, 'player_map_rect') and self.game.map_explorer.player_map_rect:
                self.game.map_explorer.player_map_rect.centerx = map_pos_data["x"]; self.game.map_explorer.player_map_rect.centery = map_pos_data["y"]
            elif hasattr(self.game.map_explorer, 'player_world_pos'):
                 self.game.map_explorer.player_world_pos[0] = map_pos_data["x"]; self.game.map_explorer.player_world_pos[1] = map_pos_data["y"]
        if hasattr(self.game, 'current_state_name'):
            self.game.current_state_name = data_to_apply.get("current_game_state", default_template.get("current_game_state"))
        # print(f"--- DEBUG GameData: _apply_data SELESAI. self.game.wallet: {getattr(getattr(self, 'game', None), 'wallet', 'N/A')} ---")

    def reset_game_data(self): # Ini adalah RESET TOTAL (HARD RESET)
        """Mengatur ulang SEMUA data game ke nilai awal, menerapkan ke game, dan menyimpannya."""
        print("--- GameData: Melakukan RESET TOTAL (reset_game_data)... ---")
        initial_data = self._get_initial_data() # Mendapatkan koin=100, upgrade=0, dll.
        self._apply_data_to_game_instance(initial_data, "reset_game_data (hard_reset)")
        self.data = initial_data.copy()
        self.save_game()
        print(f"--- GameData: RESET TOTAL selesai. Koin game sekarang: {self.game.wallet if hasattr(self.game, 'wallet') else 'N/A'} ---")

    # --- METODE BARU UNTUK "MULAI PETUALANGAN" ---
    def reset_for_new_adventure(self):
        """
        Mereset aspek game untuk petualangan baru, TAPI MEMPERTAHANKAN KOIN saat ini.
        Mereset: posisi pemain, ikan di inventaris, upgrade perahu (ke level 0), lokasi terbuka (ke default).
        """
        print("--- GameData: Mereset untuk PETUALANGAN BARU (koin dipertahankan)... ---")
        
        current_coins = 0
        if hasattr(self.game, 'wallet'):
            current_coins = self.game.wallet
        print(f"--- GameData: reset_for_new_adventure - Koin saat ini yang akan dipertahankan: {current_coins} ---")

        # Dapatkan struktur data awal yang bersih (ini akan memiliki koin=100, upgrade=0, dll.)
        data_for_new_adventure = self._get_initial_data() 
        
        # --- Modifikasi data awal ini ---
        # 1. Atur koin ke nilai koin saat ini yang sudah disimpan
        data_for_new_adventure["coins"] = current_coins
        
        # 2. Aspek lain akan menggunakan nilai default dari _get_initial_data():
        #    - "boat_upgrades" akan menjadi {"speed": 0, "capacity": 0, "line_length": 0}
        #    - "unlocked_locations" akan menjadi {"Coast": True, "Sea": False, "Ocean": False}
        #    - "collected_fish" akan menjadi []
        #    - "player_map_position" akan menjadi posisi awal default
        #    - "current_game_state" dari _get_initial_data adalah "main_menu", ini akan diset di game instance
        #      tapi pemanggil (MainMenu.start_new_game) akan mengubah state ke 'land_explore'.

        print(f"--- GameData: reset_for_new_adventure - Data yang akan diterapkan: Koin={data_for_new_adventure['coins']}, Upgrades={data_for_new_adventure['boat_upgrades']} ---")

        # Terapkan data yang sudah dimodifikasi ini ke instance Game (self.game)
        self._apply_data_to_game_instance(data_for_new_adventure, "reset_for_new_adventure (soft_reset)")
        
        # Update self.data internal GameData agar konsisten dengan apa yang baru saja diterapkan dan akan disimpan.
        self.data = data_for_new_adventure.copy()
        
        # Simpan game dengan kondisi "petualangan baru" ini
        self.save_game()
        
        print(f"--- GameData: Reset untuk PETUALANGAN BARU selesai. Koin game sekarang: {self.game.wallet if hasattr(self.game, 'wallet') else 'N/A'} ---")
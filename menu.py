# menu.py
import pygame
import os

class Menu:
    def __init__(self, game, background_image_filename=None):
        self.game = game
        self.config = self.game.config
        self.selected_index = 0
        self.options = []
        self.title = "Default Menu Title"
        self.background_image = None
        self.fallback_background_color = self.config.COLORS.get('blue', (0,0,139))

        if background_image_filename:
            bg_path = os.path.join(self.config.BACKGROUND_PATH, background_image_filename)
            if os.path.exists(bg_path):
                try:
                    loaded_image = self.config.load_image(bg_path, use_alpha=False)
                    if loaded_image.get_width() > 1 and loaded_image.get_height() > 1:
                        self.background_image = pygame.transform.scale(loaded_image, (self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT))
                except Exception as e:
                    # print(f"--- Menu ({self.__class__.__name__}): ERROR latar belakang: {e}") # Untuk debug
                    pass
        
        font_name_to_load = self.config.FONT_NAME
        actual_font_path = None
        if font_name_to_load and font_name_to_load.strip() != "" and font_name_to_load.lower() != 'none':
            if os.path.isabs(font_name_to_load) and os.path.exists(font_name_to_load):
                actual_font_path = font_name_to_load
            else:
                potential_path = os.path.join(self.config.FONT_PATH, font_name_to_load)
                if os.path.exists(potential_path):
                    actual_font_path = potential_path
        
        medium_size = self.config.FONT_SIZES.get('medium', 30)
        title_size_key = 'title' if 'title' in self.config.FONT_SIZES else 'large'
        title_size = self.config.FONT_SIZES.get(title_size_key, 50)
        small_size = self.config.FONT_SIZES.get('small', 18)

        try:
            if actual_font_path:
                self.font = pygame.font.Font(actual_font_path, medium_size)
                self.title_font = pygame.font.Font(actual_font_path, title_size)
                self.small_font = pygame.font.Font(actual_font_path, small_size)
            elif font_name_to_load and font_name_to_load.strip() != "" and font_name_to_load.lower() != 'none':
                self.font = pygame.font.SysFont(font_name_to_load, medium_size)
                self.title_font = pygame.font.SysFont(font_name_to_load, title_size)
                self.small_font = pygame.font.SysFont(font_name_to_load, small_size)
            else:
                self.font = pygame.font.Font(None, medium_size)
                self.title_font = pygame.font.Font(None, title_size)
                self.small_font = pygame.font.Font(None, small_size)
        except Exception as e:
            # print(f"--- Menu ({self.__class__.__name__}): ERROR FONT - {e}") # Untuk debug
            self.font = pygame.font.Font(None, medium_size)
            self.title_font = pygame.font.Font(None, title_size)
            self.small_font = pygame.font.Font(None, small_size)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if not self.options: return False
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.options)
                return True
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.options)
                return True
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if 0 <= self.selected_index < len(self.options):
                    option_text, action = self.options[self.selected_index]
                    if action: action(); return True
            elif event.key == pygame.K_ESCAPE:
                if hasattr(self, 'go_back_action') and callable(self.go_back_action):
                    self.go_back_action(); return True
        return False

    def render(self, screen):
        if self.background_image:
            screen.blit(self.background_image, (0,0))
        else:
            screen.fill(self.fallback_background_color)

        if hasattr(self, 'title_font') and self.title_font:
            title_surface = self.title_font.render(self.title, True, self.config.COLORS.get('white', (255,255,255)))
            title_rect = title_surface.get_rect(center=(self.config.SCREEN_WIDTH // 2, self.config.SCREEN_HEIGHT // 4 - 20))
            screen.blit(title_surface, title_rect)
            option_start_y = title_rect.bottom + 70
        else:
            option_start_y = self.config.SCREEN_HEIGHT // 3

        if hasattr(self, 'font') and self.font:
            line_height = self.font.get_height() + 25
            for i, (text, action) in enumerate(self.options):
                color_key = 'text_selected' if i == self.selected_index else 'text_default'
                color = self.config.COLORS.get(color_key, (255,255,0) if i == self.selected_index else (255,255,255))
                option_surface = self.font.render(text, True, color)
                shadow_color = self.config.COLORS.get('black', (0,0,0))
                shadow_offset = 2 
                shadow_surface = self.font.render(text, True, shadow_color)
                option_rect = option_surface.get_rect(center=(self.config.SCREEN_WIDTH // 2, option_start_y + i * line_height ))
                screen.blit(shadow_surface, (option_rect.x + shadow_offset, option_rect.y + shadow_offset)) 
                screen.blit(option_surface, option_rect) 

        if hasattr(self.game, 'wallet') and hasattr(self, 'small_font') and self.small_font:
            coins_text_surface = self.small_font.render(f"Koin: {self.game.wallet}", True, self.config.COLORS.get('text_selected', (255,255,0)))
            coins_text_rect = coins_text_surface.get_rect(topright=(self.config.SCREEN_WIDTH - 10, 10))
            screen.blit(coins_text_surface, coins_text_rect)

class MainMenu(Menu):
    def __init__(self, game):
        super().__init__(game, background_image_filename="TampilanAwal.png") 
        self.title = "Fishing Mania" 
        self.update_options()

    def update_options(self):
        options_list = []
        # Opsi "Lanjutkan Petualangan" bisa ditambahkan di sini jika save file ada
        # has_save_game = os.path.exists(self.game.game_data_manager.save_file_path)
        # if has_save_game:
        #    options_list.append(("Lanjutkan Petualangan", self.continue_game))
        
        options_list.extend([
            ("Mulai Petualangan", self.start_new_game), # Ini sekarang berfungsi sebagai reset yang mempertahankan koin
            ("Toko Perahu", lambda: self.game.change_state('shop')), 
            ("Lihat Koleksi Ikan", lambda: self.game.change_state('inventory_screen')),
            ("Jual Ikan", lambda: self.game.change_state('market_screen')),
            # OPSI "Reset Data Game" DIHAPUS DARI SINI
            ("Keluar", self.quit_game)
        ])
        self.options = options_list
        if self.selected_index >= len(self.options):
             self.selected_index = 0

    def start_new_game(self):
        """
        Memulai petualangan baru: mereset posisi, inventaris, upgrade kapal, dan lokasi,
        TAPI MEMPERTAHANKAN KOIN saat ini.
        """
        print("--- MainMenu: Memulai petualangan baru (koin dipertahankan)... ---")
        # Pastikan game_data_manager memiliki metode reset_for_new_adventure()
        if hasattr(self.game.game_data_manager, 'reset_for_new_adventure'):
            self.game.game_data_manager.reset_for_new_adventure() 
        else:
            # Fallback ke reset total jika metode spesifik tidak ada (seharusnya ada dari perbaikan sebelumnya)
            print("--- MainMenu: PERINGATAN - reset_for_new_adventure() tidak ditemukan, melakukan reset total sebagai fallback.")
            self.game.game_data_manager.reset_game_data()
        self.game.change_state('land_explore')

    # METODE perform_full_game_reset() DIHAPUS KARENA OPSINYA SUDAH DIHILANGKAN
    # def perform_full_game_reset(self): 
    #     print("--- MainMenu: Opsi 'Reset Data Game' dipilih. Melakukan RESET TOTAL... ---")
    #     self.game.game_data_manager.reset_game_data()
    #     print("--- MainMenu: Data game telah direset total. Kembali ke Menu Utama. ---")
    #     self.game.change_state('main_menu') 

    def continue_game(self):
        print("--- MainMenu: Melanjutkan petualangan dari save game. ---")
        initial_state_after_load = self.game.game_data_manager.data.get("current_game_state", "main_menu")
        # Jika state terakhir adalah menu, atau tidak ada, mulai dari land_explore
        if not initial_state_after_load or initial_state_after_load == "main_menu":
            self.game.change_state('land_explore')
        else:
            self.game.change_state(initial_state_after_load)

    def quit_game(self):
        print("--- MainMenu: Aksi Keluar dipilih. ---")
        self.game.running = False

# ... (Kelas SettingsMenu, ShopMenu, MarketScreen, InventoryScreen tetap sama seperti di file Anda)
# Pastikan kelas SettingsMenu ada jika masih diimpor di game.py, atau hapus impornya di game.py
# Berdasarkan error sebelumnya, Anda mungkin sudah menghapus SettingsMenu dari game.py

class SettingsMenu(Menu): # Jika Anda masih mempertahankan definisi ini
    def __init__(self, game):
        super().__init__(game, background_image_filename="TampilanAwal.png")
        self.title = "Pengaturan"
        self.options = [ ("Kembali", lambda: self.game.change_state('main_menu')) ]
        self.go_back_action = lambda: self.game.change_state('main_menu')

class ShopMenu(Menu):
    def __init__(self, game):
        super().__init__(game, background_image_filename="TampilanAwal.png")
        self.title = "Toko Perahu"
        self.update_options()
        self.go_back_action = lambda: self.game.change_state('main_menu')

    def update_options(self):
        if not self.game.boat or not hasattr(self.game.boat, 'UPGRADE_LEVELS'):
             self.options = [ ("Perahu Belum Siap", None), ("Kembali", lambda: self.game.change_state('main_menu')) ]
             return

        options_list = []
        upgrade_types = ["speed", "capacity", "line_length"] 
        for upgrade_type in upgrade_types:
            cost = self.game.boat.get_upgrade_cost(upgrade_type) if hasattr(self.game.boat, 'get_upgrade_cost') else "N/A"
            current_level = self.game.boat.upgrades.get(upgrade_type, 0) if hasattr(self.game.boat, 'upgrades') else 0
            # Perbaikan: Pastikan UPGRADE_LEVELS[upgrade_type] ada dan tidak kosong
            max_level_boat = 0
            if upgrade_type in self.game.boat.UPGRADE_LEVELS and self.game.boat.UPGRADE_LEVELS[upgrade_type]:
                 max_level_boat = len(self.game.boat.UPGRADE_LEVELS[upgrade_type]) -1 
            else: # Fallback jika data upgrade tidak ada
                self.options = [ (f"Data Upgrade '{upgrade_type}' Bermasalah", None), ("Kembali", lambda: self.game.change_state('main_menu')) ]
                return


            display_name = upgrade_type.capitalize()
            if upgrade_type == "line_length": 
                display_name = "Panjang Tali Pancing"

            if cost != "N/A" and cost is not None and current_level < max_level_boat : 
                text = f"Upgrade {display_name} (Lvl {current_level+1}) - Koin: {cost}" 
                action = lambda ut=upgrade_type: self.attempt_upgrade(ut)
            else: 
                text = f"{display_name} (Lvl {current_level if current_level <= max_level_boat else max_level_boat}) - MAX" 
                action = None 
            options_list.append((text, action))
        options_list.append(("Kembali", lambda: self.game.change_state('main_menu')))
        self.options = options_list

    def attempt_upgrade(self, upgrade_type):
        if not self.game.boat or not hasattr(self.game.boat, 'get_upgrade_cost') or not hasattr(self.game.boat, 'upgrade'): return

        cost = self.game.boat.get_upgrade_cost(upgrade_type)
        if cost is not None and self.game.wallet >= cost:
            self.game.wallet -= cost
            if self.game.boat.upgrade(upgrade_type): 
                pass # print(f"    {upgrade_type.capitalize()} berhasil di-upgrade!")
            else: 
                self.game.wallet += cost 
        self.update_options() 

class MarketScreen(Menu): 
    def __init__(self, game):
        super().__init__(game, background_image_filename="TampilanAwal.png") 
        self.title = "Pasar Ikan"
        self.update_options()
        self.go_back_action = lambda: self.game.change_state('main_menu') 

    def update_options(self):
        total_value = 0; num_fish = 0
        if self.game.inventory and hasattr(self.game.inventory, 'fish_list') and isinstance(self.game.inventory.fish_list, list): 
            for fish_item in self.game.inventory.fish_list: 
                if hasattr(fish_item, 'value'): total_value += fish_item.value 
                elif isinstance(fish_item, dict) and 'value' in fish_item: total_value += fish_item['value']
            num_fish = len(self.game.inventory.fish_list)
        
        sell_all_text = f"Jual Semua Ikan ({num_fish} ikan) - Nilai: {total_value}"
        self.options = [
            (sell_all_text, self.sell_all_fish if num_fish > 0 else None), 
            ("Kembali", lambda: self.game.change_state('main_menu'))
        ]

    def sell_all_fish(self):
        if self.game.market and self.game.inventory and hasattr(self.game.market, 'sell_all_fish_from_inventory'): 
            sold_value = self.game.market.sell_all_fish_from_inventory() 
        self.update_options() 

class InventoryScreen(Menu): 
    def __init__(self, game):
        super().__init__(game, background_image_filename="TampilanAwal.png") 
        self.title = "Koleksi Ikanku"
        self.update_options()
        self.go_back_action = lambda: self.game.change_state('main_menu') 

    def update_options(self):
        self.options = []
        if self.game.inventory and hasattr(self.game.inventory, 'fish_list') and isinstance(self.game.inventory.fish_list, list):
            if not self.game.inventory.fish_list: 
                self.options.append(("Inventaris Kosong", None))
            else:
                for fish_item in self.game.inventory.fish_list[:8]: 
                    name = "Ikan Misterius"; rarity = "N/A"; value_str = ""
                    if hasattr(fish_item, 'name'): name = fish_item.name
                    elif isinstance(fish_item, dict) and 'name' in fish_item: name = fish_item['name']
                    if hasattr(fish_item, 'rarity'): rarity = fish_item.rarity
                    elif isinstance(fish_item, dict) and 'rarity' in fish_item: rarity = fish_item['rarity']
                    if hasattr(fish_item, 'value'): value_str = f" - Nilai: {fish_item.value}"
                    elif isinstance(fish_item, dict) and 'value' in fish_item: value_str = f" - Nilai: {fish_item['value']}"
                    fish_display_text = f"{name} ({rarity}){value_str}"
                    self.options.append((fish_display_text, None)) 
                if len(self.game.inventory.fish_list) > 8:
                    self.options.append(("...dan lainnya...", None))
        else: 
            self.options.append(("Inventaris Tidak Tersedia", None))
        self.options.append(("Kembali", lambda: self.game.change_state('main_menu')))
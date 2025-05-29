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
            print(f"--- Menu ({self.__class__.__name__}): Mencoba memuat latar belakang: {bg_path} ---")
            if os.path.exists(bg_path):
                try:
                    loaded_image = self.config.load_image(bg_path, use_alpha=False)
                    if loaded_image.get_width() > 1 and loaded_image.get_height() > 1: # Cek bukan placeholder error
                        self.background_image = pygame.transform.scale(loaded_image, (self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT))
                        print(f"--- Menu ({self.__class__.__name__}): Latar belakang '{background_image_filename}' BERHASIL dimuat.")
                    else:
                        print(f"--- Menu ({self.__class__.__name__}): Gagal memuat '{bg_path}', gambar placeholder dikembalikan oleh load_image. Menggunakan warna fallback.")
                except Exception as e:
                    print(f"--- Menu ({self.__class__.__name__}): ERROR saat memuat atau menskalakan latar belakang '{bg_path}': {e}. Menggunakan warna fallback.")
            else:
                print(f"--- Menu ({self.__class__.__name__}): PERINGATAN - File latar belakang '{bg_path}' tidak ditemukan. Menggunakan warna fallback.")
        else:
            print(f"--- Menu ({self.__class__.__name__}): Tidak ada background_image_filename. Menggunakan warna fallback.")

        # Inisialisasi Font
        font_name_to_load = self.config.FONT_NAME
        actual_font_path = None
        if font_name_to_load and font_name_to_load.strip() != "" and font_name_to_load.lower() != 'none':
            if os.path.isabs(font_name_to_load) and os.path.exists(font_name_to_load): # Jika path absolut
                actual_font_path = font_name_to_load
            else: # Jika hanya nama file, gabungkan dengan FONT_PATH
                potential_path = os.path.join(self.config.FONT_PATH, font_name_to_load)
                if os.path.exists(potential_path):
                    actual_font_path = potential_path
        
        medium_size = self.config.FONT_SIZES.get('medium', 30)
        title_size_key = 'title' if 'title' in self.config.FONT_SIZES else 'large' # Cek apakah 'title' ada
        title_size = self.config.FONT_SIZES.get(title_size_key, 50)
        small_size = self.config.FONT_SIZES.get('small', 18) # Untuk teks koin

        try:
            if actual_font_path: # Jika path font valid ditemukan
                self.font = pygame.font.Font(actual_font_path, medium_size)
                self.title_font = pygame.font.Font(actual_font_path, title_size)
                self.small_font = pygame.font.Font(actual_font_path, small_size) # Inisialisasi small_font
                print(f"--- Menu ({self.__class__.__name__}): Font '{actual_font_path}' berhasil dimuat.")
            elif font_name_to_load and font_name_to_load.strip() != "" and font_name_to_load.lower() != 'none': # Coba sebagai SysFont
                self.font = pygame.font.SysFont(font_name_to_load, medium_size)
                self.title_font = pygame.font.SysFont(font_name_to_load, title_size)
                self.small_font = pygame.font.SysFont(font_name_to_load, small_size) # Inisialisasi small_font
                print(f"--- Menu ({self.__class__.__name__}): Menggunakan SysFont '{font_name_to_load}'.")
            else: # Fallback absolut jika FONT_NAME None atau kosong
                self.font = pygame.font.Font(None, medium_size) # Default Pygame font
                self.title_font = pygame.font.Font(None, title_size) # Default Pygame font
                self.small_font = pygame.font.Font(None, small_size) # Default Pygame font
                print(f"--- Menu ({self.__class__.__name__}): Menggunakan pygame.font.Font(None, size) default.")
        except Exception as e:
            print(f"--- Menu ({self.__class__.__name__}): ERROR FONT - {e}. Menggunakan default absolut pygame.font.Font(None, size).")
            self.font = pygame.font.Font(None, medium_size)
            self.title_font = pygame.font.Font(None, title_size)
            self.small_font = pygame.font.Font(None, small_size) # Fallback small_font


    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if not self.options: # Jika tidak ada opsi, tidak ada yang bisa dilakukan
                return False

            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.options)
                return True
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.options)
                return True
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if 0 <= self.selected_index < len(self.options):
                    option_text, action = self.options[self.selected_index]
                    print(f"--- Menu ({self.title}): Opsi '{option_text}' dipilih. ---")
                    if action: # Jika ada fungsi aksi yang terkait
                        action() # Panggil fungsi aksi
                        return True
            elif event.key == pygame.K_ESCAPE: # Tombol ESC untuk kembali (jika ada go_back_action)
                if hasattr(self, 'go_back_action') and callable(self.go_back_action):
                    print(f"--- Menu ({self.title}): ESC ditekan, go_back_action dipanggil. ---")
                    self.go_back_action()
                    return True
        return False # Event tidak ditangani oleh menu ini


    def render(self, screen):
        # Gambar latar belakang
        if self.background_image:
            screen.blit(self.background_image, (0,0))
        else:
            screen.fill(self.fallback_background_color) # Warna fallback jika gambar tidak ada

        # Gambar judul menu
        if hasattr(self, 'title_font') and self.title_font: # Pastikan title_font ada
            title_surface = self.title_font.render(self.title, True, self.config.COLORS.get('white', (255,255,255)))
            title_rect = title_surface.get_rect(center=(self.config.SCREEN_WIDTH // 2, self.config.SCREEN_HEIGHT // 4 - 20)) # Posisi judul
            screen.blit(title_surface, title_rect)
            option_start_y = title_rect.bottom + 70 # Posisi Y awal untuk opsi menu
        else: # Fallback jika title_font tidak ada
            option_start_y = self.config.SCREEN_HEIGHT // 3


        # Gambar opsi-opsi menu
        if hasattr(self, 'font') and self.font: # Pastikan font ada
            line_height = self.font.get_height() + 25 # Jarak antar opsi
            for i, (text, action) in enumerate(self.options):
                # Tentukan warna teks (berbeda jika terpilih)
                color_key = 'text_selected' if i == self.selected_index else 'text_default'
                color = self.config.COLORS.get(color_key, (255,255,0) if i == self.selected_index else (255,255,255))

                option_surface = self.font.render(text, True, color)
                # Tambahkan bayangan sederhana untuk teks
                shadow_color = self.config.COLORS.get('black', (0,0,0))
                shadow_offset = 2 # Jarak bayangan
                shadow_surface = self.font.render(text, True, shadow_color)
                
                option_rect = option_surface.get_rect(center=(self.config.SCREEN_WIDTH // 2, option_start_y + i * line_height ))
                
                # Gambar bayangan dulu, lalu teks utama
                screen.blit(shadow_surface, (option_rect.x + shadow_offset, option_rect.y + shadow_offset)) 
                screen.blit(option_surface, option_rect) 

        # --- Tampilkan Koin di Semua Menu (Posisi Kanan Atas) ---
        if hasattr(self.game, 'wallet') and hasattr(self, 'small_font') and self.small_font: # Pastikan game.wallet dan small_font ada
            coins_text_surface = self.small_font.render(f"Koin: {self.game.wallet}", True, self.config.COLORS.get('text_selected', (255,255,0)))
            coins_text_rect = coins_text_surface.get_rect(topright=(self.config.SCREEN_WIDTH - 10, 10))
            screen.blit(coins_text_surface, coins_text_rect)


class MainMenu(Menu):
    def __init__(self, game):
        super().__init__(game, background_image_filename="TampilanAwal.png") 
        self.title = "Fishing Mania" 
        self.options = [
            # Aksi "Mulai Petualangan" sekarang ke 'land_explore'
            ("Mulai Petualangan", lambda: self.game.change_state('land_explore')), 
            # HAPUS BARIS INI UNTUK MENGHAPUS PENGATURAN
            # ("Pengaturan", lambda: self.game.change_state('settings')),
            ("Toko Perahu", lambda: self.game.change_state('shop')),
            ("Lihat Koleksi Ikan", lambda: self.game.change_state('inventory_screen')),
            ("Jual Ikan", lambda: self.game.change_state('market_screen')),
            ("Keluar", self.quit_game)
        ]

    def quit_game(self):
        print("--- MainMenu: Aksi Keluar dipilih. ---")
        self.game.running = False

class SettingsMenu(Menu):
    # KARENA OPSI PENGATURAN DIHAPUS, KELAS INI MUNGKIN TIDAK DIPERLUKAN LAGI
    # TAPI KITA BISA BIARKAN UNTUK SAAT INI JIKA MUNGKIN ADA REFERENSI LAIN.
    # Jika Anda ingin menghapus sepenuhnya, pastikan untuk menghapus inisialisasi SettingsMenu di game.py
    def __init__(self, game):
        super().__init__(game, background_image_filename="TampilanAwal.png")
        self.title = "Pengaturan"
        self.options = [ ("Kembali", lambda: self.game.change_state('main_menu')) ]
        self.go_back_action = lambda: self.game.change_state('main_menu') # Aksi untuk tombol ESC

class ShopMenu(Menu):
    def __init__(self, game):
        super().__init__(game, background_image_filename="TampilanAwal.png")
        self.title = "Toko Perahu"
        self.update_options() # Panggil update_options untuk mengisi opsi awal
        self.go_back_action = lambda: self.game.change_state('main_menu')

    def update_options(self):
        if not self.game.boat or not hasattr(self.game.boat, 'UPGRADE_LEVELS'):
             self.options = [ ("Perahu Belum Siap", None), ("Kembali", lambda: self.game.change_state('main_menu')) ]
             return

        options_list = []
        # Perbarui upgrade_types untuk menyertakan 'line_length' dan menghapus 'sonar'
        upgrade_types = ["speed", "capacity", "line_length"] 
        for upgrade_type in upgrade_types:
            cost = self.game.boat.get_upgrade_cost(upgrade_type) if hasattr(self.game.boat, 'get_upgrade_cost') else "N/A"
            current_level = self.game.boat.upgrades.get(upgrade_type, 0) if hasattr(self.game.boat, 'upgrades') else 0
            max_level_boat = len(self.game.boat.UPGRADE_LEVELS.get(upgrade_type, [])) -1 

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
                print(f"    {upgrade_type.capitalize()} berhasil di-upgrade!")
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
                if hasattr(fish_item, 'value'): 
                    total_value += fish_item.value 
                elif isinstance(fish_item, dict) and 'value' in fish_item: 
                    total_value += fish_item['value']
            num_fish = len(self.game.inventory.fish_list)
        
        sell_all_text = f"Jual Semua Ikan ({num_fish} ikan) - Nilai: {total_value}"
        self.options = [
            (sell_all_text, self.sell_all_fish if num_fish > 0 else None), 
            ("Kembali", lambda: self.game.change_state('main_menu'))
        ]

    def sell_all_fish(self):
        if self.game.market and self.game.inventory and hasattr(self.game.market, 'sell_all_fish_from_inventory'): 
            sold_value = self.game.market.sell_all_fish_from_inventory() 
            print(f"    Semua ikan terjual! Dapat {sold_value} koin.")
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
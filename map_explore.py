# TES/map_explore.py
import pygame
import os

class MapExplorer:
    def __init__(self, game):
        print("--- MapExplorer: Memulai __init__()... ---")
        self.game = game
        self.config = self.game.config # Mengambil config dari game

        # Load Font
        font_name_to_load = None
        small_font_size = 20 # Default

        if hasattr(self.config, 'DEFAULT_FONT_NAME'):
            font_name_to_load = self.config.DEFAULT_FONT_NAME
        if hasattr(self.config, 'FONT_SIZES'):
            small_font_size = self.config.FONT_SIZES.get('small', small_font_size)
        
        actual_font_path = None
        if font_name_to_load and font_name_to_load.strip().lower() != 'none':
            if os.path.isabs(font_name_to_load) and os.path.exists(font_name_to_load):
                actual_font_path = font_name_to_load
            elif hasattr(self.config, 'FONT_PATH'): # Pastikan FONT_PATH ada di config
                potential_path = os.path.join(self.config.FONT_PATH, font_name_to_load)
                if os.path.exists(potential_path):
                    actual_font_path = potential_path
        
        try:
            if actual_font_path:
                self.font = pygame.font.Font(actual_font_path, small_font_size)
                print(f"--- MapExplorer: Font '{actual_font_path}' berhasil dimuat.")
            elif font_name_to_load and font_name_to_load.strip().lower() != 'none':
                self.font = pygame.font.SysFont(font_name_to_load, small_font_size)
                print(f"--- MapExplorer: Menggunakan SysFont '{font_name_to_load}'.")
            else:
                self.font = pygame.font.Font(None, small_font_size)
                print(f"--- MapExplorer: Menggunakan pygame.font.Font(None, {small_font_size}) default.")
        except Exception as e:
            print(f"--- MapExplorer: ERROR saat memuat font: {e}. Menggunakan default pygame.font.Font(None, 24). ---")
            self.font = pygame.font.Font(None, 24)


        # Load World Map Background
        self.world_map_image = None
        self.world_map_rect = None
        world_map_path = ""
        if hasattr(self.config, 'BACKGROUND_PATH'):
            try:
                world_map_path = os.path.join(self.config.BACKGROUND_PATH, "Peta Lautan.png")
                print(f"--- MapExplorer: Mencoba memuat gambar peta dunia: {world_map_path} ---")
                
                if not os.path.exists(world_map_path):
                    print(f"--- MapExplorer: PERINGATAN - File peta '{world_map_path}' TIDAK DITEMUKAN. Akan menggunakan warna solid.")
                else:
                    loaded_map_image = self.config.load_image(world_map_path) # Asumsi load_image ada di config
                    # Cek apakah placeholder dikembalikan (berdasarkan ukuran default placeholder di Config.load_image)
                    is_placeholder_from_load_image = (loaded_map_image.get_width() == 50 and loaded_map_image.get_height() == 50 and \
                                                    hasattr(loaded_map_image, '_debug_load_error_message'))

                    if is_placeholder_from_load_image:
                         print(f"--- MapExplorer: PERINGATAN - load_image untuk '{world_map_path}' mengembalikan placeholder. Akan menggunakan warna solid.")
                    else: 
                        self.world_map_image = loaded_map_image
                        self.world_map_rect = self.world_map_image.get_rect(topleft=(0,0))
                        print(f"--- MapExplorer: Gambar peta dunia '{world_map_path}' dimuat. Ukuran asli: {self.world_map_image.get_size()} ---")
                        
                        if self.world_map_image.get_size() != (self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT):
                            print(f"--- MapExplorer: Menyesuaikan skala gambar peta ke {self.config.SCREEN_WIDTH}x{self.config.SCREEN_HEIGHT} ---")
                            self.world_map_image = pygame.transform.scale(self.world_map_image, (self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT))
                            self.world_map_rect = self.world_map_image.get_rect(topleft=(0,0))

            except Exception as e:
                print(f"--- MapExplorer: ERROR tidak bisa memuat gambar peta dunia '{world_map_path}': {e}. Akan menggunakan warna solid. ---")
        else:
            print("--- MapExplorer: PERINGATAN - self.config tidak memiliki BACKGROUND_PATH. Tidak bisa memuat peta.")
        
        if not self.world_map_image:
            self.world_map_image = pygame.Surface((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT))
            self.world_map_image.fill(self.config.COLORS.get("black", (0,0,0)) if hasattr(self.config, 'COLORS') else (0,0,0) )
            self.world_map_rect = self.world_map_image.get_rect(topleft=(0,0))
            print(f"--- MapExplorer: Menggunakan latar belakang warna solid karena peta tidak termuat.")

        # Player (Boat) Initialization
        self.player_world_pos = [self.config.SCREEN_WIDTH * 0.6, self.config.SCREEN_HEIGHT * 0.65]
        self.player_speed = 200 # Kecepatan pemain di peta
        self.player_boat_image = None
        self.player_map_rect = None # Ini akan menjadi rect untuk kapal di peta
        player_boat_image_path = ""

        # --- PERBAIKAN: Gunakan self.config.ASSETS_PATH ---
        if hasattr(self.config, 'ASSETS_PATH'):
            try:
                player_asset_folder = os.path.join(self.config.ASSETS_PATH, "Player")
                player_boat_image_path = os.path.join(player_asset_folder, "kapal laut.png")
                print(f"--- MapExplorer: Mencoba memuat sprite kapal pemain peta: {player_boat_image_path} ---")
                
                if not os.path.exists(player_boat_image_path):
                    print(f"--- MapExplorer: PERINGATAN - File sprite kapal '{player_boat_image_path}' TIDAK DITEMUKAN. Akan menggunakan placeholder kotak.")
                else:
                    loaded_boat_image = self.config.load_image(player_boat_image_path, scale=0.6)
                    is_placeholder_boat = (loaded_boat_image.get_width() == 50 and loaded_boat_image.get_height() == 50 and \
                                           hasattr(loaded_boat_image, '_debug_load_error_message'))

                    if is_placeholder_boat:
                         print(f"--- MapExplorer: PERINGATAN - load_image untuk '{player_boat_image_path}' mengembalikan placeholder. Akan menggunakan placeholder kotak.")
                    else:
                        self.player_boat_image = loaded_boat_image
                        self.player_map_rect = self.player_boat_image.get_rect(center=self.player_world_pos)
                        print(f"--- MapExplorer: Sprite kapal pemain peta BERHASIL dimuat. Ukuran: {self.player_boat_image.get_size()} ---")

            except Exception as e:
                print(f"--- MapExplorer: ERROR saat memuat sprite kapal pemain '{player_boat_image_path}': {e}. Akan menggunakan placeholder kotak. ---")
        else:
            print("--- MapExplorer: PERINGATAN - self.config tidak memiliki ASSETS_PATH. Tidak bisa memuat sprite kapal.")
        
        if not self.player_boat_image:
            self.player_map_rect = pygame.Rect(0, 0, 25, 25)
            self.player_map_rect.center = self.player_world_pos
            print(f"--- MapExplorer: Menggunakan placeholder kotak untuk kapal. Rect: {self.player_map_rect} ---")

        print(f"--- MapExplorer: Player (kapal) rect awal (setelah init): {self.player_map_rect} ---")

        spot_interaction_width, spot_interaction_height = 200, 80
        self.fishing_spots_data = {
            "Pantai Lokal": { 
                'pos': (self.config.SCREEN_WIDTH * 0.55, self.config.SCREEN_HEIGHT * 0.6), 
                'rect_area': pygame.Rect(0,0, spot_interaction_width, spot_interaction_height),
                'map_name': "Coast",
                'unlock_cost': 0, # Gratis
                'display_name': "Pantai Lokal" # <--- Tambahkan display_name di sini
            },
            "Laut Lepas": { 
                'pos': (self.config.SCREEN_WIDTH * 0.30, self.config.SCREEN_HEIGHT * 0.40), 
                'rect_area': pygame.Rect(0,0, spot_interaction_width, spot_interaction_height),
                'map_name': "Sea",
                'unlock_cost': 800, # Biaya untuk Laut Lepas
                'display_name': "Laut Lepas" # <--- Tambahkan display_name di sini
            },
            "Samudra Dalam": { 
                'pos': (self.config.SCREEN_WIDTH * 0.12, self.config.SCREEN_HEIGHT * 0.15), 
                'rect_area': pygame.Rect(0,0, spot_interaction_width, spot_interaction_height),
                'map_name': "Ocean",
                'unlock_cost': 3500, # Biaya untuk Samudra Dalam
                'display_name': "Samudra Dalam" # <--- Tambahkan display_name di sini
            },
        }
        for spot_name, data in self.fishing_spots_data.items():
            data['rect_area'].center = data['pos']

        self.land_return_spot_data = {
            'pos': (self.config.SCREEN_WIDTH * 0.85, self.config.SCREEN_HEIGHT * 0.85),
            'rect_area': pygame.Rect(0,0, 200, 80),
            'label': "Kembali ke Daratan",
            'target_state': 'land_explore'
        }
        self.land_return_spot_data['rect_area'].center = self.land_return_spot_data['pos']
        
        self.active_target_state_name = None
        self.active_prompt_text = None
        self.active_spot_map_name = None # Menambahkan ini untuk UI
        self.locked_spot_message = None # Pesan jika lokasi terkunci

        print(f"--- MapExplorer: Fishing spots data (setelah penyesuaian): {self.fishing_spots_data} ---")
        
        self.sea_limit_right = self.config.SCREEN_WIDTH * 0.95 
        self.sea_limit_bottom = self.config.SCREEN_HEIGHT * 0.95
        self.sea_limit_left = self.config.SCREEN_WIDTH * 0.01  
        self.sea_limit_top = self.config.SCREEN_HEIGHT * 0.01   
        print(f"--- MapExplorer: Batas laut diatur ke L:{self.sea_limit_left}, T:{self.sea_limit_top}, R:{self.sea_limit_right}, B:{self.sea_limit_bottom} ---")

        print("--- MapExplorer: __init__() selesai. ---")

    def setup_scene(self): # Tambahkan metode ini jika belum ada
        print(f"--- MapExplorer: setup_scene() dipanggil ---")
        # Logika setup spesifik untuk MapExplorer, misalnya menambahkan player_map_rect ke grup sprite jika perlu
        # atau mengatur fokus kamera.
        # Untuk sekarang, hanya print.
        if self.game and hasattr(self.game, 'all_sprites') and self.player_map_rect and not self.player_boat_image: # Jika menggunakan placeholder rect
            # Anda mungkin ingin membuat sprite placeholder jika player_boat_image tidak ada
            # agar bisa ditambahkan ke all_sprites dan dirender oleh loop utama game.
            # Contoh:
            # placeholder_sprite = pygame.sprite.Sprite()
            # placeholder_sprite.image = pygame.Surface(self.player_map_rect.size, pygame.SRCALPHA)
            # placeholder_sprite.image.fill(self.config.COLORS.get("player_map_avatar", (255,0,0)))
            # placeholder_sprite.rect = self.player_map_rect.copy()
            # self.game.all_sprites.add(placeholder_sprite)
            pass


    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if self.active_target_state_name:
                    # Logika untuk kembali ke daratan (tidak perlu biaya)
                    if self.active_target_state_name == 'land_explore':
                        print(f"--- MapExplorer: Pemain memilih untuk kembali ke daratan. ---")
                        self.game.change_state('land_explore')
                        return True
                    # Logika untuk masuk ke lokasi memancing (perlu cek biaya)
                    elif self.active_target_state_name in ["Coast", "Sea", "Ocean"]:
                        selected_spot_data = None
                        # Cari data spot berdasarkan map_name yang aktif
                        for name, sd in self.fishing_spots_data.items():
                            if sd.get('map_name') == self.active_target_state_name:
                                selected_spot_data = sd
                                break
                        
                        if selected_spot_data:
                            unlock_cost = selected_spot_data.get('unlock_cost', 0)
                            # Cek apakah lokasi adalah Pantai Lokal (gratis) atau memiliki cukup koin
                            if self.active_target_state_name == "Coast" or \
                               self.game.wallet >= unlock_cost:
                                # Jika lokasi Laut Lepas/Samudra Dalam, kurangi koin
                                if self.active_target_state_name in ["Sea", "Ocean"] and unlock_cost > 0:
                                    self.game.wallet -= unlock_cost
                                    print(f"--- MapExplorer: {selected_spot_data['display_name']} terbuka! Koin berkurang {unlock_cost}. Sisa koin: {self.game.wallet} ---")
                                    # Simpan status "terbuka" jika diperlukan (misal: di data save game)
                                    # Untuk demo ini, kita hanya kurangi koin saat masuk
                                
                                print(f"--- MapExplorer: Pemain memilih lokasi memancing: {self.active_target_state_name} ---")
                                self.game.change_state('fishing', data={'location_name': self.active_target_state_name})
                                self.locked_spot_message = None # Reset pesan setelah berhasil masuk
                                return True
                            else:
                                # Lokasi terkunci dan tidak punya cukup koin
                                self.locked_spot_message = f"Tidak cukup koin! Butuh {unlock_cost} untuk {selected_spot_data['display_name']}." # <--- Perbaikan di sini
                                print(self.locked_spot_message)
                                return True # Event ditangani, tapi lokasi tidak terbuka
        
            elif event.key == pygame.K_ESCAPE:
                 print("--- MapExplorer: Tombol ESC ditekan, kembali ke land_explore ---")
                 self.game.change_state('land_explore')
                 return True
        return False

    def update(self, dt):
        keys = pygame.key.get_pressed()
        move_x, move_y = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move_x -= self.player_speed * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move_x += self.player_speed * dt
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            move_y -= self.player_speed * dt
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            move_y += self.player_speed * dt

        if self.player_map_rect:
            self.player_map_rect.x += move_x
            self.player_map_rect.y += move_y

            if self.player_map_rect.left < self.sea_limit_left:
                self.player_map_rect.left = self.sea_limit_left
            if self.player_map_rect.top < self.sea_limit_top:
                self.player_map_rect.top = self.sea_limit_top
            if self.player_map_rect.right > self.sea_limit_right:
                self.player_map_rect.right = self.sea_limit_right
            if self.player_map_rect.bottom > self.sea_limit_bottom:
                self.player_map_rect.bottom = self.sea_limit_bottom
            
            if self.world_map_rect:
                self.player_map_rect.clamp_ip(self.world_map_rect)
            
            self.active_target_state_name = None
            self.active_prompt_text = None
            self.locked_spot_message = None # Reset pesan setiap update untuk membersihkan jika pemain menjauh

            for display_name_key, spot_data in self.fishing_spots_data.items(): # Iterasi dengan kunci display_name_key
                if self.player_map_rect.colliderect(spot_data['rect_area']):
                    self.active_target_state_name = spot_data['map_name']
                    self.active_spot_map_name = spot_data['map_name'] # Untuk UI Koin
                    
                    unlock_cost = spot_data.get('unlock_cost', 0)
                    display_name_for_prompt = spot_data.get('display_name', display_name_key) # Gunakan display_name dari data
                    
                    if self.game.wallet < unlock_cost and spot_data['map_name'] != "Coast": # Pantai Lokal selalu gratis
                        self.active_prompt_text = f"Terkunci! Butuh {unlock_cost} Koin"
                        self.locked_spot_message = f"Tidak cukup koin! Butuh {unlock_cost} untuk {display_name_for_prompt}."
                    else:
                        self.active_prompt_text = f"memancing di {display_name_for_prompt}"
                        if unlock_cost > 0: # Jika ada biaya, tambahkan ke prompt
                            self.active_prompt_text += f" (Biaya: {unlock_cost} Koin)"
                    break 

            if not self.active_target_state_name:
                if self.player_map_rect.colliderect(self.land_return_spot_data['rect_area']):
                    self.active_target_state_name = self.land_return_spot_data['target_state']
                    self.active_prompt_text = f"{self.land_return_spot_data['label']}"
        else:
            # print("--- MapExplorer WARN: player_map_rect is None in update(), tidak bisa gerakkan pemain ---")
            pass


    def render(self, screen):
        if self.world_map_image and self.world_map_rect:
            screen.blit(self.world_map_image, self.world_map_rect.topleft) # Selalu gambar peta dari topleft (0,0) jika statis
        
        # Render Fishing Spots (label teks)
        for display_name_key, spot_data in self.fishing_spots_data.items(): # Iterasi dengan kunci display_name_key
            is_active = (spot_data['map_name'] == self.active_target_state_name)
            
            # Perbarui warna dan teks berdasarkan status terkunci
            unlock_cost = spot_data.get('unlock_cost', 0)
            is_locked = (self.game.wallet < unlock_cost and spot_data['map_name'] != "Coast") # Pantai Lokal selalu gratis
            
            color_key = 'text_selected' if is_active and not is_locked else 'text_default'
            if is_locked:
                color_key = 'text_inactive' # Warna abu-abu atau merah untuk terkunci
            
            # Pastikan config dan COLORS ada sebelum mengakses
            default_color_val = (255,255,0) if is_active else (255,255,255)
            if is_locked:
                default_color_val = self.config.COLORS.get('red', (255,100,100)) # Warna merah untuk terkunci
            
            color_val = default_color_val
            if hasattr(self.config, 'COLORS'):
                 color_val = self.config.COLORS.get(color_key, default_color_val)
            
            spot_label_text = spot_data.get('display_name', display_name_key) # Ambil display_name dari data
            if is_locked:
                spot_label_text += f" (Terkunci: {unlock_cost} Koin)"

            spot_label = self.font.render(spot_label_text, True, color_val)
            # Posisi label relatif terhadap layar, bukan dunia game jika peta tidak scroll
            label_rect = spot_label.get_rect(center=spot_data['pos'])
            screen.blit(spot_label, label_rect)

        # Render Titik Kembali ke Daratan
        is_land_spot_active = (self.land_return_spot_data['target_state'] == self.active_target_state_name)
        land_color_key = 'text_selected' if is_land_spot_active else 'text_default'
        land_default_color_val = (255,255,0) if is_land_spot_active else (255,255,255)
        land_color_val = land_default_color_val
        if hasattr(self.config, 'COLORS'):
            land_color_val = self.config.COLORS.get(land_color_key, land_default_color_val)

        land_label_surface = self.font.render(self.land_return_spot_data['label'], True, land_color_val)
        land_label_rect = land_label_surface.get_rect(center=self.land_return_spot_data['pos'])
        screen.blit(land_label_surface, land_label_rect)

        # Render Player (kapal di peta)
        if self.player_boat_image and self.player_map_rect:
            screen.blit(self.player_boat_image, self.player_map_rect) # Gambar kapal di posisi rect-nya
        elif self.player_map_rect:
            player_color_val = (255,0,0)
            if hasattr(self.config, 'COLORS'):
                 player_color_val = self.config.COLORS.get("player_map_avatar", (255,0,0))
            pygame.draw.rect(screen, player_color_val, self.player_map_rect)

        if self.active_prompt_text:
            interaction_text_str = f"Tekan ENTER untuk {self.active_prompt_text}"
            text_color_val = (255,255,255)
            
            # Jika ada pesan terkunci, gunakan warna berbeda dan tambahkan ke prompt
            if self.locked_spot_message:
                interaction_text_str = self.locked_spot_message
                text_color_val = self.config.COLORS.get('red', (255,100,100)) # Merah untuk pesan error
            elif hasattr(self.config, 'COLORS'):
                text_color_val = self.config.COLORS.get("white",(255,255,255))

            interaction_text_surface = self.font.render(interaction_text_str, True, text_color_val)
            text_rect = interaction_text_surface.get_rect(midbottom=(self.config.SCREEN_WIDTH // 2, self.config.SCREEN_HEIGHT - 20))
            screen.blit(interaction_text_surface, text_rect)
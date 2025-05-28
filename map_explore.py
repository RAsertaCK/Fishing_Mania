# TES/map_explore.py
import pygame
import os

class MapExplorer:
    def __init__(self, game):
        print("--- MapExplorer: Memulai __init__()... ---")
        self.game = game
        self.config = self.game.config

        # Load Font
        try:
            font_name_to_load = self.config.FONT_NAME
            actual_font_path = None
            if font_name_to_load and font_name_to_load.strip() != "" and font_name_to_load.lower() != 'none':
                if os.path.isabs(font_name_to_load) and os.path.exists(font_name_to_load):
                    actual_font_path = font_name_to_load
                else:
                    potential_path = os.path.join(self.config.FONT_PATH, font_name_to_load)
                    if os.path.exists(potential_path):
                        actual_font_path = potential_path
            
            small_font_size = self.config.FONT_SIZES.get('small', 20) 

            if actual_font_path:
                self.font = pygame.font.Font(actual_font_path, small_font_size)
                print(f"--- MapExplorer: Font '{actual_font_path}' berhasil dimuat.")
            elif font_name_to_load and font_name_to_load.strip() != "" and font_name_to_load.lower() != 'none':
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
        try:
            world_map_path = os.path.join(self.config.UI_PATH, "map.png") 
            print(f"--- MapExplorer: Mencoba memuat gambar peta dunia: {world_map_path} ---")
            
            if not os.path.exists(world_map_path):
                print(f"--- MapExplorer: PERINGATAN - File peta '{world_map_path}' TIDAK DITEMUKAN. Akan menggunakan warna solid.")
            else:
                loaded_map_image = self.config.load_image(world_map_path)
                is_placeholder_from_load_image = (loaded_map_image.get_width() == 50 and loaded_map_image.get_height() == 50)
                
                if is_placeholder_from_load_image and os.path.exists(world_map_path):
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
        
        if not self.world_map_image: 
            self.world_map_image = pygame.Surface((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT))
            self.world_map_image.fill(self.config.COLORS.get("black", (0,0,0))) 
            self.world_map_rect = self.world_map_image.get_rect(topleft=(0,0))
            print(f"--- MapExplorer: Menggunakan latar belakang warna solid karena peta tidak termuat.")

        # Player (Boat) Initialization
        self.player_world_pos = [self.config.SCREEN_WIDTH * 0.6, self.config.SCREEN_HEIGHT * 0.65] 
        self.player_speed = 200
        self.player_boat_image = None 
        self.player_map_rect = None
        player_boat_image_path = "" 

        try:
            player_asset_folder = os.path.join(self.config.ASSET_PATH, "Player") 
            player_boat_image_path = os.path.join(player_asset_folder, "kapal laut.png") 
            print(f"--- MapExplorer: Mencoba memuat sprite kapal pemain peta: {player_boat_image_path} ---")
            
            if not os.path.exists(player_boat_image_path):
                print(f"--- MapExplorer: PERINGATAN - File sprite kapal '{player_boat_image_path}' TIDAK DITEMUKAN. Akan menggunakan placeholder kotak.")
            else:
                loaded_boat_image = self.config.load_image(player_boat_image_path, scale=0.6) 
                is_placeholder_boat = (loaded_boat_image.get_width() == 50 and loaded_boat_image.get_height() == 50 and \
                                       "ERROR Config: File gambar tidak ditemukan" in getattr(loaded_boat_image, '_debug_load_error_message', ""))

                if is_placeholder_boat and os.path.exists(player_boat_image_path):
                     print(f"--- MapExplorer: PERINGATAN - load_image untuk '{player_boat_image_path}' mengembalikan placeholder. Akan menggunakan placeholder kotak.")
                else:
                    self.player_boat_image = loaded_boat_image
                    self.player_map_rect = self.player_boat_image.get_rect(center=self.player_world_pos)
                    print(f"--- MapExplorer: Sprite kapal pemain peta BERHASIL dimuat. Ukuran: {self.player_boat_image.get_size()} ---")

        except Exception as e:
            print(f"--- MapExplorer: ERROR saat memuat sprite kapal pemain '{player_boat_image_path}': {e}. Akan menggunakan placeholder kotak. ---")
        
        if not self.player_boat_image: 
            self.player_map_rect = pygame.Rect(0, 0, 25, 25) 
            self.player_map_rect.center = self.player_world_pos
            print(f"--- MapExplorer: Menggunakan placeholder kotak untuk kapal. Rect: {self.player_map_rect} ---")

        print(f"--- MapExplorer: Player (kapal) rect awal (setelah init): {self.player_map_rect} ---")

        # Fishing Spots Data - PENYESUAIAN KOORDINAT (x, y) untuk teks nama wilayah
        spot_interaction_width, spot_interaction_height = 200, 80 

        self.fishing_spots_data = {
            "Pantai Lokal": { 
                'pos': (self.config.SCREEN_WIDTH * 0.55, self.config.SCREEN_HEIGHT * 0.6), 
                'rect_area': pygame.Rect(0,0, spot_interaction_width, spot_interaction_height),
                'map_name': "Coast"
            },
            "Laut Lepas": { 
                'pos': (self.config.SCREEN_WIDTH * 0.30, self.config.SCREEN_HEIGHT * 0.40), 
                'rect_area': pygame.Rect(0,0, spot_interaction_width, spot_interaction_height),
                'map_name': "Sea"
            },
            "Samudra Dalam": { 
                'pos': (self.config.SCREEN_WIDTH * 0.12, self.config.SCREEN_HEIGHT * 0.15), 
                'rect_area': pygame.Rect(0,0, spot_interaction_width, spot_interaction_height),
                'map_name': "Ocean"
            },
        }
        for spot_name, data in self.fishing_spots_data.items():
            data['rect_area'].center = data['pos']

        self.active_spot_map_name = None
        print(f"--- MapExplorer: Fishing spots data (setelah penyesuaian): {self.fishing_spots_data} ---")
        
        # PERUBAHAN: Definisikan batas area laut agar lebih luas lagi, lebih mendekati tepi visual daratan
        # Anda perlu menyesuaikan nilai-nilai ini dengan sangat hati-hati berdasarkan visual peta Anda.
        self.sea_limit_right = self.config.SCREEN_WIDTH * 0.95  # Izinkan lebih ke kanan sebelum batas
        self.sea_limit_bottom = self.config.SCREEN_HEIGHT * 0.95 # Izinkan lebih ke bawah sebelum batas
        self.sea_limit_left = self.config.SCREEN_WIDTH * 0.01   
        self.sea_limit_top = self.config.SCREEN_HEIGHT * 0.01    
        print(f"--- MapExplorer: Batas laut diatur ke L:{self.sea_limit_left}, T:{self.sea_limit_top}, R:{self.sea_limit_right}, B:{self.sea_limit_bottom} ---")

        print("--- MapExplorer: __init__() selesai. ---")

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if self.active_spot_map_name:
                    print(f"--- MapExplorer: Pemain memilih lokasi (map_name): {self.active_spot_map_name} ---")
                    self.game.change_state('fishing', data={'location_name': self.active_spot_map_name})
                    return True
            elif event.key == pygame.K_ESCAPE:
                 print("--- MapExplorer: Tombol ESC ditekan, kembali ke main_menu ---")
                 # PERUBAHAN: Kembali ke land_explorer dari map_explore
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

            # Terapkan batas laut kustom TERLEBIH DAHULU
            if self.player_map_rect.left < self.sea_limit_left:
                self.player_map_rect.left = self.sea_limit_left
            if self.player_map_rect.top < self.sea_limit_top:
                self.player_map_rect.top = self.sea_limit_top
            if self.player_map_rect.right > self.sea_limit_right:
                self.player_map_rect.right = self.sea_limit_right
            if self.player_map_rect.bottom > self.sea_limit_bottom:
                self.player_map_rect.bottom = self.sea_limit_bottom
            
            # Kemudian, clamp ke batas layar keseluruhan (jika batas laut lebih besar dari layar, ini akan menjaganya)
            if self.world_map_rect: 
                self.player_map_rect.clamp_ip(self.world_map_rect)
            
            self.active_spot_map_name = None
            for display_name, spot_data in self.fishing_spots_data.items():
                if self.player_map_rect.colliderect(spot_data['rect_area']):
                    self.active_spot_map_name = spot_data['map_name']
                    break
        else:
            print("--- MapExplorer WARN: player_map_rect is None in update(), tidak bisa gerakkan pemain ---")

    def render(self, screen):
        if self.world_map_image and self.world_map_rect:
            screen.blit(self.world_map_image, self.world_map_rect)
        
        for display_name, spot_data in self.fishing_spots_data.items():
            is_active = (spot_data['map_name'] == self.active_spot_map_name)
            color_key = 'text_selected' if is_active else 'text_default'
            default_color = self.config.COLORS.get('text_selected', (255,255,0)) if is_active else self.config.COLORS.get('text_default', (255,255,255))
            color = self.config.COLORS.get(color_key, default_color)
            
            spot_label = self.font.render(display_name, True, color)
            label_rect = spot_label.get_rect(center=spot_data['pos'])
            screen.blit(spot_label, label_rect)

        if self.player_boat_image and self.player_map_rect:
            screen.blit(self.player_boat_image, self.player_map_rect)
        elif self.player_map_rect: 
            player_color = self.config.COLORS.get("player_map_avatar", (255,0,0)) 
            pygame.draw.rect(screen, player_color, self.player_map_rect)
        else:
            print("--- MapExplorer ERROR: player_map_rect is None in render(), tidak bisa gambar pemain ---")

        if self.active_spot_map_name:
            interaction_display_name = ""
            for dn, sd in self.fishing_spots_data.items():
                if sd['map_name'] == self.active_spot_map_name:
                    interaction_display_name = dn
                    break
            interaction_text_str = f"Tekan ENTER untuk memancing di {interaction_display_name}"
            interaction_text_surface = self.font.render(interaction_text_str, True, self.config.COLORS.get("white",(255,255,255)))
            text_rect = interaction_text_surface.get_rect(midbottom=(self.config.SCREEN_WIDTH // 2, self.config.SCREEN_HEIGHT - 20))
            screen.blit(interaction_text_surface, text_rect)

# IMPROVE/map_explore.py
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
                potential_path = os.path.join(self.config.FONT_PATH, font_name_to_load)
                if os.path.exists(potential_path):
                    actual_font_path = potential_path
            
            small_font_size = self.config.FONT_SIZES.get('small', 18)

            if actual_font_path:
                self.font = pygame.font.Font(actual_font_path, small_font_size)
            elif font_name_to_load and font_name_to_load.strip() != "" and font_name_to_load.lower() != 'none':
                self.font = pygame.font.SysFont(font_name_to_load, small_font_size)
            else:
                self.font = pygame.font.Font(None, small_font_size)
            print("--- MapExplorer: Font berhasil dimuat/fallback. ---")
        except Exception as e:
            print(f"--- MapExplorer: ERROR saat memuat font: {e}. Menggunakan default. ---")
            self.font = pygame.font.Font(None, 24) # Ukuran fallback jika ada error

        # Load World Map Background
        try:
            world_map_path = os.path.join(self.config.BACKGROUND_PATH, "world_map_background.png")
            print(f"--- MapExplorer: Mencoba memuat gambar peta dunia: {world_map_path} ---")
            self.world_map_image = self.config.load_image(world_map_path)
            # Jika load_image mengembalikan placeholder karena file tidak ada, ukurannya akan kecil (misal 50x50)
            # Kita tetap set rect-nya, tapi visualnya akan placeholder
            if self.world_map_image.get_width() <= 50 and self.world_map_image.get_height() <= 50 : # Cek ukuran placeholder dari config.load_image
                 print(f"--- MapExplorer: PERINGATAN - 'world_map_background.png' tidak ditemukan atau terlalu kecil. Ukuran: {self.world_map_image.get_size()}. Menggunakan placeholder dari config.")
            else:
                 print(f"--- MapExplorer: Gambar peta dunia dimuat. Ukuran: {self.world_map_image.get_size()} ---")
            self.world_map_rect = self.world_map_image.get_rect(topleft=(0,0))

        except Exception as e:
            print(f"--- MapExplorer: ERROR tidak bisa memuat gambar peta dunia: {e}. Menggunakan warna solid. ---")
            self.world_map_image = pygame.Surface((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT))
            self.world_map_image.fill(self.config.COLORS.get("black", (0,0,0)))
            self.world_map_rect = self.world_map_image.get_rect(topleft=(0,0))

        # Player (Boat) Initialization
        self.player_world_pos = [self.config.SCREEN_WIDTH // 4, self.config.SCREEN_HEIGHT // 2]
        self.player_speed = 200

        # Load player boat sprite
        try:
            # Anda perlu menyediakan gambar 'map_boat_icon.png' di folder 'assets/boats/'
            # atau sesuaikan nama file dan path-nya.
            player_boat_image_path = os.path.join(self.config.BOAT_PATH, "map_boat_icon.png")
            print(f"--- MapExplorer: Mencoba memuat sprite kapal pemain peta: {player_boat_image_path} ---")
            # Berikan skala yang sesuai, misalnya 0.5 jika gambar aslinya besar
            self.player_boat_image = self.config.load_image(player_boat_image_path, scale=0.3) 
            if self.player_boat_image.get_width() <= 1: # Placeholder dari load_image jika error
                print(f"--- MapExplorer: PERINGATAN - Sprite kapal '{player_boat_image_path}' tidak ditemukan. Menggunakan placeholder merah.")
                # Buat placeholder manual jika load_image mengembalikan sesuatu yang tidak diinginkan
                self.player_boat_image = pygame.Surface((40, 25), pygame.SRCALPHA) # Ukuran placeholder
                self.player_boat_image.fill(self.config.COLORS.get("player_map_avatar", (255,0,0, 180))) # Merah transparan
            else:
                 print(f"--- MapExplorer: Sprite kapal pemain peta BERHASIL dimuat. Ukuran: {self.player_boat_image.get_size()} ---")

            self.player_map_rect = self.player_boat_image.get_rect(center=self.player_world_pos)
        except Exception as e:
            print(f"--- MapExplorer: ERROR saat memuat sprite kapal pemain: {e}. Menggunakan placeholder kotak. ---")
            self.player_boat_image = None # Tidak ada gambar, akan digambar sebagai kotak
            self.player_map_rect = pygame.Rect(self.player_world_pos[0] - 16, self.player_world_pos[1] - 16, 32, 32) # Ukuran default

        print(f"--- MapExplorer: Player (kapal) rect awal: {self.player_map_rect} ---")

        # Fishing Spots Data
        self.fishing_spots_data = {
            "Pantai Lokal": {'rect': pygame.Rect(self.config.SCREEN_WIDTH * 0.2, self.config.SCREEN_HEIGHT * 0.3, 150, 70), 'map_name': "Coast"},
            "Laut Lepas": {'rect': pygame.Rect(self.config.SCREEN_WIDTH * 0.5, self.config.SCREEN_HEIGHT * 0.5, 150, 70), 'map_name': "Sea"},
            "Samudra Dalam": {'rect': pygame.Rect(self.config.SCREEN_WIDTH * 0.3, self.config.SCREEN_HEIGHT * 0.7, 150, 70), 'map_name': "Ocean"},
        }
        self.active_spot_map_name = None
        print(f"--- MapExplorer: Fishing spots data: {self.fishing_spots_data} ---")
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
                 self.game.change_state('main_menu')
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

        self.player_map_rect.x += move_x
        self.player_map_rect.y += move_y

        # Batasi gerakan pemain agar tetap di dalam peta dunia
        if self.world_map_rect: # Pastikan world_map_rect sudah diinisialisasi
            self.player_map_rect.clamp_ip(self.world_map_rect)

        self.active_spot_map_name = None
        for display_name, spot_data in self.fishing_spots_data.items():
            if self.player_map_rect.colliderect(spot_data['rect']):
                self.active_spot_map_name = spot_data['map_name']
                break

    def render(self, screen):
        # Gambar latar belakang peta dunia
        if self.world_map_image and self.world_map_rect:
            screen.blit(self.world_map_image, self.world_map_rect)
        else: # Fallback jika peta dunia gagal dimuat
            screen.fill(self.config.COLORS.get("black", (0,0,0)))


        # Gambar fishing spots
        for display_name, spot_data in self.fishing_spots_data.items():
            spot_rect = spot_data['rect']
            is_active = (spot_data['map_name'] == self.active_spot_map_name)
            
            color_key = 'text_selected' if is_active else 'text_default'
            # Warna fallback jika key tidak ada di COLORS
            default_color = (255,255,0) if is_active else (255,255,255)
            color = self.config.COLORS.get(color_key, default_color)
            
            pygame.draw.rect(screen, color, spot_rect, 3) # Kotak penanda
            spot_label = self.font.render(display_name, True, color)
            label_rect = spot_label.get_rect(center=spot_rect.center)
            screen.blit(spot_label, label_rect)

        # Gambar kapal pemain
        if self.player_boat_image and self.player_map_rect:
            screen.blit(self.player_boat_image, self.player_map_rect)
        elif self.player_map_rect: # Jika gambar kapal gagal dimuat, gambar kotak sebagai fallback
            player_color = self.config.COLORS.get("player_map_avatar", (255,0,0))
            pygame.draw.rect(screen, player_color, self.player_map_rect)


        # Tampilkan teks interaksi jika pemain berada di atas spot memancing
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

# TES/land_explorer.py
import pygame
import os
from camera_system import Camera
from sprites import Player as LandPlayer, Spritesheet, Block, Ground
from config import Config

class LandExplorer:
    def __init__(self, game):
        print("--- LandExplorer: Memulai __init__()... ---")
        self.game = game
        self.config = self.game.config

        self.FRAME_WIDTH = 16
        self.FRAME_HEIGHT = 32
        self.NUM_FRAMES_PER_ANIMATION = 8
        self.ANIMATION_SPEED = 0.1
        self.PLAYER_SPRITE_SCALE = 2.0

        # Load Font (untuk debugging teks)
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
            
            small_font_size = self.config.FONT_SIZES.get('small', 18)
            medium_font_size = self.config.FONT_SIZES.get('medium', 22)

            if actual_font_path:
                self.font = pygame.font.Font(actual_font_path, small_font_size)
                self.label_font = pygame.font.Font(actual_font_path, medium_font_size)
                self.debug_font = pygame.font.Font(actual_font_path, 16)
            elif font_name_to_load and font_name_to_load.strip() != "" and font_name_to_load.lower() != 'none':
                self.font = pygame.font.SysFont(font_name_to_load, small_font_size)
                self.label_font = pygame.font.SysFont(font_name_to_load, medium_font_size)
                self.debug_font = pygame.font.SysFont(font_name_to_load, 16)
            else:
                self.font = pygame.font.Font(None, small_font_size)
                self.label_font = pygame.font.Font(None, medium_font_size)
                self.debug_font = pygame.font.Font(None, 16)
        except Exception as e:
            print(f"--- LandExplorer: ERROR saat memuat font: {e}. Menggunakan default. ---")
            self.font = pygame.font.Font(None, 24)
            self.label_font = pygame.font.Font(None, 30)
            self.debug_font = pygame.font.Font(None, 16)


        self.land_background_image = None
        self.land_background_rect = None
        background_path = os.path.join(self.config.BACKGROUND_PATH, "bg_baru.webp")
        try:
            if not os.path.exists(background_path):
                print(f"--- LandExplorer: PERINGATAN - File latar daratan '{background_path}' TIDAK DITEMUKAN. Menggunakan warna solid.")
                self.world_width = self.config.SCREEN_WIDTH
                self.world_height = self.config.SCREEN_HEIGHT
                self.land_background_image = pygame.Surface((self.world_width, self.world_height))
                self.land_background_image.fill((255, 0, 255))
                self.land_background_rect = self.land_background_image.get_rect(topleft=(0,0))
            else:
                loaded_bg_image = self.config.load_image(background_path, use_alpha=False)
                if loaded_bg_image.get_width() <= 1 or loaded_bg_image.get_height() <= 1:
                    print(f"--- LandExplorer: PERINGATAN - load_image untuk '{background_path}' mengembalikan placeholder. Menggunakan warna solid.")
                    self.world_width = self.config.SCREEN_WIDTH
                    self.world_height = self.config.SCREEN_HEIGHT
                    self.land_background_image = pygame.Surface((self.world_width, self.world_height))
                    self.land_background_image.fill((255, 0, 255))
                    self.land_background_rect = self.land_background_image.get_rect(topleft=(0,0))
                else:
                    # --- MODIFIKASI DIMULAI DI SINI ---
                    # Skalakan gambar latar belakang agar pas dengan SCREEN_WIDTH dan SCREEN_HEIGHT
                    self.land_background_image = pygame.transform.scale(loaded_bg_image, (self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT))
                    self.world_width = self.land_background_image.get_width()
                    self.world_height = self.land_background_image.get_height()
                    self.land_background_rect = self.land_background_image.get_rect(topleft=(0,0))
                    print(f"--- LandExplorer: Latar daratan '{background_path}' dimuat dan diskalakan ke layar {self.world_width}x{self.world_height}.")
                    # --- MODIFIKASI BERAKHIR DI SINI ---

        except Exception as e:
            print(f"--- LandExplorer: ERROR tidak bisa memuat gambar latar daratan '{background_path}': {e}. Menggunakan warna solid. ---")
            self.world_width = self.config.SCREEN_WIDTH
            self.world_height = self.config.SCREEN_HEIGHT
            self.land_background_image = pygame.Surface((self.world_width, self.world_height))
            self.land_background_image.fill((255, 0, 255))
            self.land_background_rect = self.land_background_image.get_rect(topleft=(0,0))

        self.player = self.game.land_player

        # === PENYESUAIAN BATAS DARATAN ===
        # Jika Anda menskalakan background agar pas dengan layar,
        # maka batas daratan juga perlu disesuaikan dengan ukuran layar.
        # Atau, jika Anda ingin tetap menggunakan proporsi asli,
        # proporsi ini akan diterapkan pada SCREEN_WIDTH dan SCREEN_HEIGHT.
        land_rect_left_abs = int(self.config.SCREEN_WIDTH * 0.19) # Mengacu ke SCREEN_WIDTH
        land_rect_top_abs = int(self.config.SCREEN_HEIGHT * 0.10) # Mengacu ke SCREEN_HEIGHT
        land_rect_right_abs = int(self.config.SCREEN_WIDTH * 0.84) # Mengacu ke SCREEN_WIDTH
        land_rect_bottom_abs = int(self.config.SCREEN_HEIGHT * 0.86) # Mengacu ke SCREEN_HEIGHT

        land_rect_width_abs = land_rect_right_abs - land_rect_left_abs
        land_rect_height_abs = land_rect_bottom_abs - land_rect_top_abs

        if land_rect_width_abs <= 0 or land_rect_height_abs <= 0:
            print(f"--- LandExplorer: PERINGATAN - Perhitungan batas daratan tidak valid. Menggunakan fallback ke seluruh dunia.")
            self.land_bounds_rect = pygame.Rect(0, 0, self.world_width, self.world_height)
        else:
            self.land_bounds_rect = pygame.Rect(land_rect_left_abs, land_rect_top_abs, land_rect_width_abs, land_rect_height_abs)
        
        print(f"--- LandExplorer: Batas daratan diatur ke Rect: {self.land_bounds_rect} ---")
        
        # Interactive Objects on Land
        # Posisi objek interaktif juga perlu disesuaikan dengan SCREEN_WIDTH/HEIGHT
        rumah_pos_x = self.config.SCREEN_WIDTH * 0.50
        rumah_pos_y = self.config.SCREEN_HEIGHT * 0.48
        
        kapal_pos_x = self.config.SCREEN_WIDTH * 0.60
        kapal_pos_y = self.config.SCREEN_HEIGHT * 0.83

        self.interactive_objects = {
            "Rumah": {'pos': (rumah_pos_x, rumah_pos_y), 'rect_area': pygame.Rect(0,0,170,140), 'action': self.go_to_main_menu, 'label': "Rumah" },
            "Kapal": {'pos': (kapal_pos_x, kapal_pos_y), 'rect_area': pygame.Rect(0,0,130,90), 'action': self.go_to_sea_map, 'label': "" }
        }
        for obj_name, data in self.interactive_objects.items():
            data['rect_area'].center = data['pos']

        self.active_object_data = None
        self.interaction_prompt = ""

        # Camera kini akan menggunakan world_width dan world_height yang sama dengan screen_width/height
        self.camera = Camera(self.world_width, self.world_height, self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT)
        
        # --- PERBAIKAN DI SINI: Atur posisi awal pemain darat di tengah area daratan ---
        if self.player and self.player.rect:
            initial_player_world_x = self.land_bounds_rect.centerx
            initial_player_world_y = self.land_bounds_rect.centery
            self.player.rect.center = (initial_player_world_x, initial_player_world_y)
            
            self.player.rect.clamp_ip(self.land_bounds_rect)
            self.camera.update(self.player.rect)
            print(f"--- LandExplorer: Player diatur ke posisi dunia: {self.player.rect.center} ---")
        else:
            print("--- LandExplorer: PERINGATAN - LandPlayer atau rect-nya tidak tersedia saat inisialisasi LandExplorer. ---")
        # --- AKHIR PERBAIKAN ---


        print("--- LandExplorer: __init__() selesai. ---")

    def setup_scene(self):
        print("--- LandExplorer: Menyiapkan scene daratan... ---")
        # Ini adalah baris yang membersihkan grup. Jika log mengatakan 1, ini bekerja.
        self.game.all_sprites.empty()
        self.game.blocks.empty()

        # Tambahkan pemain ke grup all_sprites
        if self.player:
            self.player.add(self.game.all_sprites)
            print(f"--- LandExplorer: Menambahkan player ke all_sprites. Player rect: {self.player.rect} ---")
        
        # --- DEBUGGING: Cetak jumlah sprite dalam grup setelah setup ---
        print(f"--- LandExplorer: Jumlah sprite dalam all_sprites setelah setup: {len(self.game.all_sprites)} ---")
        # --- AKHIR DEBUGGING ---

        print("--- LandExplorer: Scene daratan siap. ---")

    def go_to_main_menu(self):
        print("--- LandExplorer: Pemain berinteraksi dengan Rumah. Kembali ke Menu Utama. ---")
        self.game.change_state('main_menu')

    def go_to_sea_map(self):
        print("--- LandExplorer: Pemain berinteraksi dengan Kapal. Pindah ke map_explore (peta laut). ---")
        self.game.change_state('map_explore')

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if self.active_object_data and self.active_object_data['action']:
                    self.active_object_data['action']()
                    return True
            elif event.key == pygame.K_ESCAPE:
                 print("--- LandExplorer: Tombol ESC ditekan, kembali ke main_menu ---")
                 self.game.change_state('main_menu')
                 return True
        return False

    def update(self, dt):
        if self.player and self.player.rect:
            self.camera.update(self.player.rect)
            
            self.active_object_data = None
            current_prompt = ""
            for name, data in self.interactive_objects.items():
                if self.player.rect.colliderect(data['rect_area']):
                    self.active_object_data = data
                    if data['action']:
                        if name == "Kapal":
                            current_prompt = "OTW  Mancing"
                        elif name == "Rumah":
                            current_prompt = "Masuk Rumah Mase"
                    break
            self.interaction_prompt = current_prompt
        else:
            print("--- LandExplorer WARN: player is None or player.rect is None in update() ---")

    def render(self, screen):
        # Menggambar latar belakang daratan (gambar utama)
        if self.land_background_image and self.land_background_rect:
            # Karena background sudah diskalakan ke ukuran layar, tidak perlu kamera.apply untuk background statis
            screen.blit(self.land_background_image, (0,0))
        else:
            screen.fill(self.config.COLORS.get("magenta", (255,0,255)))
        
        # --- PENGGAMBARAN SEMUA SPRITE DENGAN DEBUGGING VISUAL ---
        if self.game.all_sprites:
            for sprite in self.game.all_sprites:
                sprite_screen_rect = self.camera.apply(sprite.rect)
                
                # Cek jika sprite adalah pemain dan tampilkan debug khusus
                if sprite == self.player:
                    # Gambar sprite pemain yang sebenarnya
                    if hasattr(sprite, 'image') and sprite.image:
                        screen.blit(sprite.image, sprite_screen_rect)
                        # Tampilkan koordinat pemain di layar untuk debugging
                        debug_text_player_coords = self.debug_font.render(f"P: ({sprite.rect.x},{sprite.rect.y}) S: ({sprite_screen_rect.x},{sprite_screen_rect.y})", True, self.config.COLORS["white"])
                        screen.blit(debug_text_player_coords, (sprite_screen_rect.x, sprite_screen_rect.y + sprite_screen_rect.height + 5))
                    else: # Fallback jika sprite.image entah bagaimana kosong
                        pygame.draw.rect(screen, self.config.COLORS.get("red"), sprite_screen_rect)
                        debug_text_player = self.debug_font.render(f"PLAYER_MISSING_IMAGE: {sprite.rect.topleft}", True, self.config.COLORS["red"])
                        screen.blit(debug_text_player, (sprite_screen_rect.x, sprite_screen_rect.y - 20))
                else:
                    # Gambar sprite lain
                    screen.blit(sprite.image, sprite_screen_rect)
        # --- AKHIR PENGGAMBARAN SPRITE ---

        # Menggambar label objek interaktif
        for name, data in self.interactive_objects.items():
            if data['label']:
                label_surface = self.label_font.render(data['label'], True, self.config.COLORS.get("white", (255,255,255)))
                label_world_rect = label_surface.get_rect(midbottom=data['rect_area'].midtop)
                screen.blit(label_surface, self.camera.apply(label_world_rect))
                
        # Menggambar prompt interaksi
        if self.interaction_prompt:
            prompt_surface = self.label_font.render(self.interaction_prompt, True, self.config.COLORS.get("yellow",(255,255,0)))
            prompt_rect = prompt_surface.get_rect(midbottom=(self.config.SCREEN_WIDTH // 2, self.config.SCREEN_HEIGHT - 20))
            screen.blit(prompt_surface, prompt_rect)
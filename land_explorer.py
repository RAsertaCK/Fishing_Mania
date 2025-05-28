# TES/land_explorer.py
import pygame
import os
from camera_system import Camera 

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
            
            small_font_size = self.config.FONT_SIZES.get('small', 18) 
            medium_font_size = self.config.FONT_SIZES.get('medium', 22) 

            if actual_font_path:
                self.font = pygame.font.Font(actual_font_path, small_font_size) 
                self.label_font = pygame.font.Font(actual_font_path, medium_font_size)
            elif font_name_to_load and font_name_to_load.strip() != "" and font_name_to_load.lower() != 'none':
                self.font = pygame.font.SysFont(font_name_to_load, small_font_size)
                self.label_font = pygame.font.SysFont(font_name_to_load, medium_font_size)
            else:
                self.font = pygame.font.Font(None, small_font_size) 
                self.label_font = pygame.font.Font(None, medium_font_size)
        except Exception as e:
            print(f"--- LandExplorer: ERROR saat memuat font: {e}. Menggunakan default. ---")
            self.font = pygame.font.Font(None, 24) 
            self.label_font = pygame.font.Font(None, 30) 

        # Load Land Background
        self.land_background_image = None
        self.land_background_rect = None
        self.world_width = self.config.SCREEN_WIDTH # Default, akan diupdate jika gambar dimuat
        self.world_height = self.config.SCREEN_HEIGHT # Default, akan diupdate jika gambar dimuat
        background_path = ""
        try:
            background_path = os.path.join(self.config.BACKGROUND_PATH, "TESTING.png") 
            if not os.path.exists(background_path):
                print(f"--- LandExplorer: PERINGATAN - File latar daratan '{background_path}' TIDAK DITEMUKAN.")
            else:
                loaded_bg_image = self.config.load_image(background_path) 
                is_placeholder = (loaded_bg_image.get_width() == 50 and loaded_bg_image.get_height() == 50 and "ERROR Config: File gambar tidak ditemukan" in getattr(loaded_bg_image, '_debug_load_error_message', ""))

                if is_placeholder and os.path.exists(background_path): # Double check if it's a real placeholder
                     print(f"--- LandExplorer: PERINGATAN - load_image untuk '{background_path}' mengembalikan placeholder meskipun file ada. Periksa path atau file.")
                elif not is_placeholder : 
                    self.land_background_image = loaded_bg_image
                    self.world_width = self.land_background_image.get_width()
                    self.world_height = self.land_background_image.get_height()
                    self.land_background_rect = self.land_background_image.get_rect(topleft=(0,0))
                    print(f"--- LandExplorer: Latar daratan '{background_path}' dimuat. Ukuran dunia: {self.world_width}x{self.world_height}")
                else: # Is a placeholder, and file might not exist or is invalid
                    print(f"--- LandExplorer: Gagal memuat gambar valid dari '{background_path}'. Menggunakan fallback.")

        except Exception as e:
            print(f"--- LandExplorer: ERROR tidak bisa memuat gambar latar daratan '{background_path}': {e}.")
        
        if not self.land_background_image: 
            self.land_background_image = pygame.Surface((self.world_width, self.world_height))
            self.land_background_image.fill((255, 0, 255)) # Magenta fallback
            self.land_background_rect = self.land_background_image.get_rect(topleft=(0,0))
            print(f"--- LandExplorer: Latar belakang diisi dengan warna MAGENTA fallback. Ukuran dunia: {self.world_width}x{self.world_height}")

        # Player on Land Initialization
        self.player_pos = [self.world_width * 0.4, self.world_height * 0.5] 
        self.player_speed = 200 
        
        self.spritesheet = None
        self.walk_right_frames = []
        self.walk_left_frames = []

        self.current_animation_frames = []
        self.current_frame_index = 0
        self.animation_timer = 0.0
        self.player_direction = 'right' 
        self.is_moving = False

        self.player_image = None 
        self.player_rect = None 
        
        self.load_player_sprites() 

        if not self.player_image or not self.player_rect : 
            print(f"--- LandExplorer: Gagal memuat sprite pemain dari spritesheet. Menggunakan placeholder BIRU.")
            placeholder_width = int(self.FRAME_WIDTH * self.PLAYER_SPRITE_SCALE)
            placeholder_height = int(self.FRAME_HEIGHT * self.PLAYER_SPRITE_SCALE)
            temp_surface = pygame.Surface((placeholder_width, placeholder_height), pygame.SRCALPHA) 
            temp_surface.fill(self.config.COLORS.get("blue", (0, 0, 255, 180))) 
            self.player_image = temp_surface
            self.player_rect = self.player_image.get_rect(center=self.player_pos)
            self.current_animation_frames = [self.player_image] 
            self.walk_right_frames = [self.player_image]
            self.walk_left_frames = [self.player_image]
        
        # Interactive Objects on Land
        # Pastikan posisi objek interaktif berada di dalam land_bounds_rect yang baru
        rumah_pos_x = self.world_width * 0.60 
        rumah_pos_y = self.world_height * 0.45
        
        kapal_pos_x = self.world_width * 0.70 
        kapal_pos_y = self.world_height * 0.83  # Ini mungkin perlu disesuaikan agar di dalam batas bawah baru

        self.interactive_objects = {
            "Rumah": {'pos': (rumah_pos_x, rumah_pos_y), 'rect_area': pygame.Rect(0,0,170,140), 'action': self.go_to_main_menu, 'label': "Rumah" },
            "Kapal": {'pos': (kapal_pos_x, kapal_pos_y), 'rect_area': pygame.Rect(0,0,130,90), 'action': self.go_to_sea_map, 'label': "" }
        }
        for obj_name, data in self.interactive_objects.items():
            data['rect_area'].center = data['pos']

        self.active_object_data = None 
        self.interaction_prompt = "" 

        # === PENYESUAIAN BATAS DARATAN ===
        # Nilai-nilai ini adalah perkiraan berdasarkan screenshot.
        # Anda HARUS menyesuaikannya dengan gambar TESTING.png Anda.
        # Cara terbaik: Buka TESTING.png di editor gambar, catat koordinat piksel
        # untuk area daratan yang diinginkan, lalu masukkan ke sini.

        # Asumsi self.world_width dan self.world_height sudah benar dari gambar latar.
        # Jika gambar latar Anda 1280x720, nilai absolut ini bisa bekerja.
        # Jika tidak, Anda mungkin perlu menggunakan persentase lagi atau menghitung ulang.
        
        # Perkiraan batas kiri daratan (setelah sungai/jembatan)
        land_rect_left_abs = int(self.world_width * 0.19)  # Sekitar 243px jika world_width 1280
        # Perkiraan batas atas daratan
        land_rect_top_abs = int(self.world_height * 0.10) # Sekitar 72px jika world_height 720
        # Perkiraan batas kanan daratan (sebelum laut, termasuk area kapal)
        land_rect_right_abs = int(self.world_width * 0.84) # Sekitar 1075px jika world_width 1280
        # Perkiraan batas bawah daratan (termasuk area kapal)
        land_rect_bottom_abs = int(self.world_height * 0.86) # Sekitar 619px jika world_height 720

        # Hitung lebar dan tinggi area daratan
        land_rect_width_abs = land_rect_right_abs - land_rect_left_abs
        land_rect_height_abs = land_rect_bottom_abs - land_rect_top_abs

        if land_rect_width_abs <= 0 or land_rect_height_abs <= 0:
            print(f"--- LandExplorer: PERINGATAN - Perhitungan batas daratan tidak valid (lebar/tinggi <=0). Menggunakan fallback ke seluruh dunia.")
            self.land_bounds_rect = pygame.Rect(0, 0, self.world_width, self.world_height)
        else:
            self.land_bounds_rect = pygame.Rect(land_rect_left_abs, land_rect_top_abs, land_rect_width_abs, land_rect_height_abs)
        
        print(f"--- LandExplorer: Batas daratan diatur ke Rect: {self.land_bounds_rect} ---")
        print(f"--- LandExplorer: Berdasarkan world_width={self.world_width}, world_height={self.world_height} ---")
        
        # Pastikan posisi Kapal masih dalam batas baru, jika tidak, sesuaikan kapal_pos_y
        if not self.land_bounds_rect.collidepoint(kapal_pos_x, kapal_pos_y):
            print(f"--- LandExplorer: PERINGATAN - Posisi Kapal ({kapal_pos_x}, {kapal_pos_y}) di luar land_bounds_rect baru. Mungkin perlu penyesuaian.")
            # Contoh penyesuaian sederhana jika kapal terlalu rendah:
            if kapal_pos_y > self.land_bounds_rect.bottom - self.interactive_objects["Kapal"]['rect_area'].height / 2:
                 new_kapal_y = self.land_bounds_rect.bottom - self.interactive_objects["Kapal"]['rect_area'].height / 2 - 5 # sedikit offset
                 print(f"--- LandExplorer: Menyesuaikan posisi Y Kapal ke {new_kapal_y}")
                 self.interactive_objects["Kapal"]['pos'] = (kapal_pos_x, new_kapal_y)
                 self.interactive_objects["Kapal"]['rect_area'].center = self.interactive_objects["Kapal"]['pos']


        self.camera = Camera(self.world_width, self.world_height, self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT)
        if self.player_rect: 
            # Pastikan posisi awal pemain ada di dalam land_bounds_rect
            self.player_rect.clamp_ip(self.land_bounds_rect)
            self.player_pos = list(self.player_rect.center) # Update self.player_pos juga
            self.camera.update(self.player_rect)


        print("--- LandExplorer: __init__() selesai. ---")

    def get_frames_from_spritesheet(self, sheet, row_index, frame_width, frame_height, num_frames, scale_factor):
        frames = []
        for i in range(num_frames):
            x = i * frame_width
            y = row_index * frame_height
            source_rect = pygame.Rect(x, y, frame_width, frame_height)
            try:
                frame_image = sheet.subsurface(source_rect)
                frame_surface = frame_image.copy() 
            except ValueError as e:
                print(f"ERROR LandExplorer: Gagal mengambil subsurface pada {source_rect} dari sheet ukuran {sheet.get_size()}: {e}")
                frame_surface = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                frame_surface.fill((255, 0, 255, 128)) # Magenta transparan untuk error
            
            if scale_factor != 1.0:
                new_width = int(frame_width * scale_factor)
                new_height = int(frame_height * scale_factor)
                frame_surface = pygame.transform.scale(frame_surface, (new_width, new_height))
            frames.append(frame_surface)
        return frames

    def load_player_sprites(self):
        player_sprite_filename = "karakter.png" 
        player_asset_folder = os.path.join(self.config.ASSET_PATH, "Player") # Pastikan folder "Player" ada
        spritesheet_path = os.path.join(player_asset_folder, player_sprite_filename)
        
        if not os.path.exists(spritesheet_path):
            print(f"--- LandExplorer: PERINGATAN - Spritesheet '{spritesheet_path}' TIDAK DITEMUKAN.")
            self.player_image = None 
            self.player_rect = None
            return 

        try:
            self.spritesheet = pygame.image.load(spritesheet_path).convert_alpha()
            
            self.walk_right_frames = self.get_frames_from_spritesheet(self.spritesheet, 0, 
                                                                    self.FRAME_WIDTH, self.FRAME_HEIGHT, 
                                                                    self.NUM_FRAMES_PER_ANIMATION, self.PLAYER_SPRITE_SCALE)
            self.walk_left_frames = self.get_frames_from_spritesheet(self.spritesheet, 1, 
                                                                   self.FRAME_WIDTH, self.FRAME_HEIGHT, 
                                                                   self.NUM_FRAMES_PER_ANIMATION, self.PLAYER_SPRITE_SCALE)
            
            if not self.walk_right_frames or not self.walk_left_frames:
                print("--- LandExplorer: ERROR - Gagal memuat frame animasi dari spritesheet (list kosong).")
                self.player_image = None 
                self.player_rect = None
                return

            if self.player_direction == 'right':
                self.current_animation_frames = self.walk_right_frames
            else: 
                self.current_animation_frames = self.walk_left_frames
            
            if self.current_animation_frames: 
                self.player_image = self.current_animation_frames[0] 
                self.player_rect = self.player_image.get_rect(center=self.player_pos)
            else:
                print("--- LandExplorer: ERROR - current_animation_frames kosong setelah mencoba load.")
                self.player_image = None
                self.player_rect = None
        except Exception as e:
            print(f"--- LandExplorer: ERROR saat memuat atau memproses spritesheet '{spritesheet_path}': {e}")
            import traceback; traceback.print_exc()
            self.spritesheet = None
            self.player_image = None
            self.player_rect = None

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
        keys = pygame.key.get_pressed()
        move_x, move_y = 0, 0
        
        new_direction = self.player_direction 
        self.is_moving = False 

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move_x -= self.player_speed * dt
            new_direction = 'left'
            self.is_moving = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]: 
            move_x += self.player_speed * dt
            new_direction = 'right'
            self.is_moving = True
        
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            move_y -= self.player_speed * dt
            self.is_moving = True 
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]: 
            move_y += self.player_speed * dt
            self.is_moving = True 

        if new_direction != self.player_direction:
            self.player_direction = new_direction
            self.current_frame_index = 0 
            if self.player_direction == 'left' and self.walk_left_frames:
                self.current_animation_frames = self.walk_left_frames
            elif self.player_direction == 'right' and self.walk_right_frames:
                self.current_animation_frames = self.walk_right_frames
            
            if self.current_animation_frames and self.current_frame_index < len(self.current_animation_frames): # Tambah cek batas index
                 self.player_image = self.current_animation_frames[self.current_frame_index]
            elif self.current_animation_frames: # Jika index salah, fallback ke frame 0
                 self.player_image = self.current_animation_frames[0]


        if self.player_rect:
            self.player_rect.x += move_x
            self.player_rect.y += move_y

            if self.land_bounds_rect:
                self.player_rect.clamp_ip(self.land_bounds_rect)
            else: 
                self.player_rect.left = max(0, self.player_rect.left)
                self.player_rect.right = min(self.world_width, self.player_rect.right)
                self.player_rect.top = max(0, self.player_rect.top)
                self.player_rect.bottom = min(self.world_height, self.player_rect.bottom)
            
            self.player_pos = list(self.player_rect.center) # Sinkronkan self.player_pos

            if self.current_animation_frames and self.player_image: 
                if self.is_moving:
                    self.animation_timer += dt
                    if self.animation_timer >= self.ANIMATION_SPEED:
                        self.animation_timer = 0
                        self.current_frame_index = (self.current_frame_index + 1) % len(self.current_animation_frames)
                        self.player_image = self.current_animation_frames[self.current_frame_index]
                else: 
                    self.current_frame_index = 0 
                    if self.player_direction == 'left' and self.walk_left_frames:
                        self.player_image = self.walk_left_frames[0]
                    elif self.player_direction == 'right' and self.walk_right_frames: 
                        self.player_image = self.walk_right_frames[0]
            
            if self.player_image and self.player_rect.size != self.player_image.get_size():
                current_center = self.player_rect.center
                self.player_rect = self.player_image.get_rect(center=current_center)

            self.active_object_data = None 
            current_prompt = "" 
            for name, data in self.interactive_objects.items():
                if self.player_rect.colliderect(data['rect_area']):
                    self.active_object_data = data 
                    if data['action']: 
                        if name == "Kapal": 
                            current_prompt = "Tekan ENTER untuk Berlayar"
                        elif name == "Rumah": 
                            current_prompt = "Tekan ENTER untuk Masuk Rumah"
                    break 
            self.interaction_prompt = current_prompt 

            self.camera.update(self.player_rect)
        else:
            print("--- LandExplorer WARN: player_rect is None in update() ---")

    def render(self, screen):
        if self.land_background_image and self.land_background_rect: # Pastikan rect juga ada
            screen.blit(self.land_background_image, self.camera.apply(self.land_background_rect)) 
        
        for name, data in self.interactive_objects.items():
            if data['label']:
                label_surface = self.label_font.render(data['label'], True, self.config.COLORS.get("white", (255,255,255)))
                # Dapatkan rect area interaksi dalam koordinat dunia
                world_interaction_rect = data['rect_area']
                # Buat rect untuk label di atas area interaksi (misalnya, di atas tengah)
                label_world_rect = label_surface.get_rect(midbottom=world_interaction_rect.midtop)
                
                screen.blit(label_surface, self.camera.apply(label_world_rect))


        if self.player_image and self.player_rect:
            screen.blit(self.player_image, self.camera.apply(self.player_rect)) 
        
        if self.interaction_prompt: 
            prompt_surface = self.label_font.render(self.interaction_prompt, True, self.config.COLORS.get("yellow",(255,255,0)))
            prompt_rect = prompt_surface.get_rect(midbottom=(self.config.SCREEN_WIDTH // 2, self.config.SCREEN_HEIGHT - 20))
            screen.blit(prompt_surface, prompt_rect)

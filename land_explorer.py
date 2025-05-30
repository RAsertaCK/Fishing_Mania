# land_explorer.py
import pygame
import os
from camera_system import Camera 
from sprites import Player as LandPlayer

class LandExplorer:
    def __init__(self, game):
        # print("--- LandExplorer: Memulai __init__()... ---") # Kurangi print jika sudah stabil
        self.game = game
        self.config = self.game.config

        # Load Font (versi ringkas)
        try:
            font_name = self.config.FONT_NAME
            font_path_abs = None
            if font_name and os.path.isabs(font_name) and os.path.exists(font_name): font_path_abs = font_name
            elif font_name:
                 potential = os.path.join(self.config.FONT_PATH, font_name)
                 if os.path.exists(potential): font_path_abs = potential
            sm, md, dbg_sz = self.config.FONT_SIZES.get('small',18), self.config.FONT_SIZES.get('medium',22), 16
            if font_path_abs:
                self.font,self.label_font,self.debug_font = pygame.font.Font(font_path_abs,sm),pygame.font.Font(font_path_abs,md),pygame.font.Font(font_path_abs,dbg_sz)
            elif font_name and font_name.strip().lower() != 'none':
                self.font,self.label_font,self.debug_font = pygame.font.SysFont(font_name,sm),pygame.font.SysFont(font_name,md),pygame.font.SysFont(font_name,dbg_sz)
            else: raise ValueError("No valid font specified")
        except Exception:
            # print(f"--- LandExplorer: ERROR font. Fallback.") # Kurangi print
            sm, md, dbg_sz = 18, 22, 16
            self.font,self.label_font,self.debug_font = pygame.font.Font(None,sm),pygame.font.Font(None,md),pygame.font.Font(None,dbg_sz)

        # Load Background Image
        self.land_background_image = None; self.land_background_rect = None
        background_path = os.path.join(self.config.BACKGROUND_PATH, "bg_baru.webp")
        try:
            if not os.path.exists(background_path): raise FileNotFoundError(f"BG file not found: {background_path}")
            loaded_bg_image = self.config.load_image(background_path, use_alpha=False)
            if loaded_bg_image.get_width() <= 1: raise ValueError("Loaded BG is placeholder.")
            self.world_width = loaded_bg_image.get_width()
            self.world_height = loaded_bg_image.get_height()
            self.land_background_image = loaded_bg_image
            self.land_background_rect = self.land_background_image.get_rect(topleft=(0,0))
            # print(f"--- LandExplorer: Latar '{background_path}'. Ukuran Dunia: {self.world_width}x{self.world_height}.") # Kurangi print
        except Exception as e:
            # print(f"--- LandExplorer: ERROR load BG '{background_path}': {e}. Fallback warna solid. ---") # Kurangi print
            self.world_width=self.config.SCREEN_WIDTH; self.world_height=self.config.SCREEN_HEIGHT
            self.land_background_image=pygame.Surface((self.world_width,self.world_height)); self.land_background_image.fill(self.config.COLORS.get("green",(0,100,0)))
            self.land_background_rect = self.land_background_image.get_rect(topleft=(0,0))

        self.player = self.game.land_player
        self.camera = Camera(self.world_width, self.world_height, self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT)
        
        self.land_bounds_rect = pygame.Rect(0, 0, self.world_width, self.world_height) # Selebar dunia
        # print(f"--- LandExplorer: Batas daratan diatur selebar dunia: {self.land_bounds_rect} ---") # Kurangi print
        
        # Sesuaikan posisi objek interaktif berdasarkan koordinat absolut di peta besar Anda jika perlu
        rumah_pos_x = self.world_width * 0.50; rumah_pos_y = self.world_height * 0.48
        kapal_pos_x = self.world_width * 0.60; kapal_pos_y = self.world_height * 0.83
        self.interactive_objects = {
            "Rumah": {'pos':(rumah_pos_x,rumah_pos_y),'rect_area':pygame.Rect(0,0,170,140),'action':self.go_to_main_menu,'label':"Rumah"},
            "Kapal": {'pos':(kapal_pos_x,kapal_pos_y),'rect_area':pygame.Rect(0,0,130,90),'action':self.go_to_sea_map,'label':"Pergi Memancing"}
        }
        for _, data in self.interactive_objects.items(): data['rect_area'].center = data['pos']
        self.active_object_data = None; self.interaction_prompt = ""
        if self.player and self.player.rect:
            self.player.rect.center = self.land_bounds_rect.center 
            self.player.rect.clamp_ip(self.land_bounds_rect) 
            if self.camera: self.camera.update(self.player.rect)
        # print("--- LandExplorer: __init__() selesai. ---") # Kurangi print

    def setup_scene(self):
        # print("--- LandExplorer: Menyiapkan scene daratan... ---") # Kurangi print
        self.game.all_sprites.empty(); self.game.blocks.empty()
        if self.player: self.player.add(self.game.all_sprites)
        # print(f"--- LandExplorer: Scene daratan siap. ---") # Kurangi print

    def go_to_main_menu(self): self.game.change_state('main_menu')
    def go_to_sea_map(self): self.game.change_state('map_explore')

    def handle_event(self, event): # Sama seperti sebelumnya
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if self.active_object_data and self.active_object_data.get('action'):
                    self.active_object_data['action'](); return True
            elif event.key == pygame.K_ESCAPE: self.game.change_state('main_menu'); return True
        return False

    def update(self, dt): # Sama seperti sebelumnya, kamera diupdate di sini
        if self.player and self.player.rect and self.camera:
            self.player.rect.clamp_ip(self.land_bounds_rect)
            self.camera.update(self.player.rect)
            self.active_object_data = None; current_prompt = ""
            player_interaction_point = self.player.rect.midbottom 
            for name, data in self.interactive_objects.items():
                if data['rect_area'].collidepoint(player_interaction_point):
                    self.active_object_data = data
                    current_prompt = data.get('label', f"Interaksi dg {name}?")
                    break
            self.interaction_prompt = current_prompt

    def render(self, screen): # render() sudah disesuaikan sebelumnya untuk DEBUG flag
        if self.land_background_image and self.land_background_rect and self.camera:
            screen.blit(self.land_background_image, self.camera.apply(self.land_background_rect))
        else: screen.fill(self.config.COLORS.get("green", (0,100,0)))
        
        if self.game.all_sprites and self.camera:
            for sprite in self.game.all_sprites:
                if hasattr(sprite,'image') and sprite.image and hasattr(sprite,'rect') and sprite.rect:
                    screen.blit(sprite.image, self.camera.apply(sprite.rect))
                    # Hapus atau comment out bagian debug posisi pemain jika tidak diperlukan lagi
                    # if sprite == self.player and self.config.DEBUG and hasattr(self, 'debug_font'):
                    #     # ... kode debug posisi pemain ...

        if self.camera and hasattr(self, 'label_font'):
            for name, data in self.interactive_objects.items():
                if data.get('label'):
                    label_surface = self.label_font.render(data['label'], True, (255,255,255))
                    label_world_rect = label_surface.get_rect(midbottom=data['rect_area'].midtop); label_world_rect.y -= 5 
                    screen.blit(label_surface, self.camera.apply(label_world_rect))
                if self.config.DEBUG: # Ini akan menyembunyikan rect jika DEBUG=False
                    pygame.draw.rect(screen, self.config.COLORS.get("yellow",(255,255,0)), self.camera.apply(data['rect_area']), 1)
            if self.config.DEBUG: # Ini juga akan menyembunyikan rect jika DEBUG=False
                 pygame.draw.rect(screen, self.config.COLORS.get("red",(255,0,0)), self.camera.apply(self.land_bounds_rect), 2)

        if self.interaction_prompt and hasattr(self, 'label_font'):
            prompt_surface = self.label_font.render(self.interaction_prompt, True, (255,255,0))
            prompt_rect = prompt_surface.get_rect(midbottom=(self.config.SCREEN_WIDTH//2, self.config.SCREEN_HEIGHT-20))
            screen.blit(prompt_surface, prompt_rect)

        # Teks FPS & State (UI non-global)
        # Jika DEBUG = False, ini juga bisa disembunyikan atau dibuat tergantung flag lain
        if self.config.DEBUG and hasattr(self, 'font'): # Tampilkan hanya jika DEBUG true
             y_offset_debug = 10; line_h = 0
             if hasattr(self.game,'ui') and self.game.ui.font and self.game.ui.small_font:
                 y_offset_debug += self.game.ui.font.get_height() + 15
                 y_offset_debug += self.game.ui.small_font.get_height() + 5; y_offset_debug += 10
             if hasattr(self.font, 'get_height'): line_h = self.font.get_height()

             fps_surf = self.font.render(f"FPS: {int(self.game.current_fps)}", True, (255,255,255))
             state_surf = self.font.render(f"State: {self.game.current_state_name}", True, (255,255,255))
             screen.blit(fps_surf, (10, y_offset_debug))
             screen.blit(state_surf, (10, y_offset_debug + line_h + 5))
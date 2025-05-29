# fishing_system.py
import pygame
import os
import random

class FishingSystem:
    def __init__(self, game_instance):
        self.game = game_instance
        self.config = self.game.config
        
        self.is_casting = False
        self.is_reeling = False
        self.fish_on_line_awaiting_pull = False
        
        self.hook_depth = 0
        
        # Ambil max_hook_depth dari nilai upgrade kapal
        if self.game.boat and hasattr(self.game.boat, 'current_line_length_value'):
            self.max_hook_depth = self.game.boat.current_line_length_value
        elif self.game.current_game_map and hasattr(self.game.current_game_map, 'data') and \
           'depth_range' in self.game.current_game_map.data:
            self.max_hook_depth = self.game.current_game_map.data['depth_range'][1]
        else:
            self.max_hook_depth = 200
        
        self.cast_speed = 150
        self.reel_speed = 180

        self.current_hooked_fish_data = None
        self.hooked_fish_sprite = None
        
        self.hook_color = self.config.COLORS.get("white", (255,255,255))
        self.line_color = self.config.COLORS.get("text_inactive", (180,180,180))
        self.hook_sprite_width = 10
        self.hook_sprite_height = 10
        
        self.hook_collider_rect = pygame.Rect(0, 0, self.hook_sprite_width, self.hook_sprite_height)

    def _get_line_origin_world_position(self):
        if not self.game.boat or not self.game.boat.rect:
            return self.config.SCREEN_WIDTH // 2, self.config.SCREEN_HEIGHT // 2
        
        # Sesuaikan offset Y ini agar pas dengan sprite kapal Anda
        line_origin_x = self.game.boat.rect.centerx
        # Misal, tali pancing keluar dari sedikit di atas tengah vertikal kapal
        line_origin_y = self.game.boat.rect.top + (self.game.boat.rect.height * 0.3)
        return line_origin_x, line_origin_y

    def _get_hook_tip_world_position(self):
        line_origin_x, line_origin_y = self._get_line_origin_world_position()
        hook_tip_world_x = line_origin_x
        hook_tip_world_y = line_origin_y + self.hook_depth
        return hook_tip_world_x, hook_tip_world_y

    def start_cast(self):
        if not self.is_casting and not self.is_reeling and not self.fish_on_line_awaiting_pull:
            print("--- FishingSystem: Memulai lemparan (cast). ---")
            self.is_casting = True
            self.is_reeling = False
            self.fish_on_line_awaiting_pull = False
            self.current_hooked_fish_data = None
            self.hooked_fish_sprite = None
            self.hook_depth = 0

    def start_reel_in(self, triggered_by_player_pull=False):
        print(f"--- FishingSystem: Memulai gulungan (reel in). Player pull: {triggered_by_player_pull} ---")
        self.is_reeling = True
        self.is_casting = False
        self.fish_on_line_awaiting_pull = False

        if not triggered_by_player_pull and self.hooked_fish_sprite:
            print(f"--- FishingSystem: Ikan '{self.hooked_fish_sprite.name}' lepas karena tidak ditarik (reel tanpa pull). ---")
            if self.hooked_fish_sprite:
                 self.hooked_fish_sprite.is_secured_on_hook = False
            self.hooked_fish_sprite = None
            self.current_hooked_fish_data = None

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if self.fish_on_line_awaiting_pull and self.hooked_fish_sprite:
                    print(f"--- FishingSystem: Pemain MENARIK ikan '{self.hooked_fish_sprite.name}'! ---")
                    self.hooked_fish_sprite.is_secured_on_hook = True
                    self.current_hooked_fish_data = self.hooked_fish_sprite.get_data()
                    self.fish_on_line_awaiting_pull = False
                    self.is_casting = False
                    if not self.is_reeling:
                        self.start_reel_in(triggered_by_player_pull=True)
                    return True
                elif not self.is_casting and not self.is_reeling and not self.fish_on_line_awaiting_pull:
                    self.start_cast()
                    return True
                elif self.is_casting and not self.fish_on_line_awaiting_pull:
                    print("--- FishingSystem: Lemparan dibatalkan, menggulung kail kosong. ---")
                    self.is_casting = False
                    self.start_reel_in(triggered_by_player_pull=False)
                    return True
        return False

    def update(self, dt):
        hook_tip_world_x, hook_tip_world_y = self._get_hook_tip_world_position()
        self.hook_collider_rect.center = (hook_tip_world_x, hook_tip_world_y)

        if self.is_casting:
            self.hook_depth += self.cast_speed * dt
            
            if not self.fish_on_line_awaiting_pull:
                for fish_sprite in self.game.visible_fish_sprites:
                    if not fish_sprite.is_secured_on_hook and self.hook_collider_rect.colliderect(fish_sprite.rect):
                        print(f"--- FishingSystem: Kail menyentuh ikan '{fish_sprite.name}'! Menunggu tarikan pemain. ---")
                        self.hooked_fish_sprite = fish_sprite
                        self.fish_on_line_awaiting_pull = True
                        # is_casting bisa tetap true sampai pemain menekan SPACE atau kail ditarik paksa
                        break 

            if self.hook_depth >= self.max_hook_depth:
                self.hook_depth = self.max_hook_depth
                if self.is_casting:
                    self.is_casting = False
                    print(f"--- FishingSystem: Kail mencapai kedalaman maks. Otomatis menggulung. ---")
                    self.start_reel_in(triggered_by_player_pull=False)

        elif self.fish_on_line_awaiting_pull:
            # Ikan terkait, kail diam menunggu input pemain.
            # Bisa ditambahkan timer di sini agar ikan lepas jika tidak ditarik
            pass

        elif self.is_reeling:
            self.hook_depth -= self.reel_speed * dt
            
            if self.hooked_fish_sprite and self.hooked_fish_sprite.is_secured_on_hook:
                self.hooked_fish_sprite.follow_hook(hook_tip_world_x, hook_tip_world_y)

            if self.hook_depth <= 0:
                self.hook_depth = 0
                self.is_reeling = False
                
                if self.current_hooked_fish_data and self.hooked_fish_sprite and self.hooked_fish_sprite.is_secured_on_hook:
                    fish_name = self.current_hooked_fish_data.get('name', 'Misterius')
                    print(f"--- FishingSystem: Ikan {fish_name} berhasil ditarik ke perahu! ---")
                    
                    if self.game.inventory and hasattr(self.game.inventory, 'add_fish_from_data'):
                        self.game.inventory.add_fish_from_data(self.current_hooked_fish_data)
                    
                    # HAPUS BARIS INI UNTUK MENGHENTIKAN PENAMBAHAN KOIN LANGSUNG
                    # if hasattr(self.game, 'wallet'):
                    #     fish_value = self.current_hooked_fish_data.get('value', 0)
                    #     self.game.wallet += fish_value
                    #     print(f"    Koin bertambah {fish_value}. Total koin: {self.game.wallet}")
                    
                    self.game.visible_fish_sprites.remove(self.hooked_fish_sprite)
                    self.game.spawn_visible_fish(amount=1)

                elif self.hooked_fish_sprite and not self.hooked_fish_sprite.is_secured_on_hook:
                    print(f"--- FishingSystem: Ikan {self.hooked_fish_sprite.name} lepas saat proses gulung (tidak di-secure). ---")
                else:
                    print("--- FishingSystem: Gulungan kosong selesai. ---")
                
                self.current_hooked_fish_data = None
                self.hooked_fish_sprite = None

    def render_with_camera(self, screen, camera):
        if not (self.is_casting or self.is_reeling or self.fish_on_line_awaiting_pull or self.hook_depth > 0.1):
            return

        if not self.game.boat or not self.game.boat.rect:
            return

        line_origin_world_x, line_origin_world_y = self._get_line_origin_world_position()
        hook_tip_world_x, hook_tip_world_y = self._get_hook_tip_world_position()
        
        line_start_on_screen_x, line_start_on_screen_y = camera.apply_to_point(line_origin_world_x, line_origin_world_y)
        hook_end_on_screen_x, hook_end_on_screen_y = camera.apply_to_point(hook_tip_world_x, hook_tip_world_y)

        pygame.draw.line(screen, self.line_color,
                         (line_start_on_screen_x, line_start_on_screen_y),
                         (hook_end_on_screen_x, hook_end_on_screen_y), 2)

        hook_visual_screen_rect = camera.apply(self.hook_collider_rect)
        pygame.draw.ellipse(screen, self.hook_color, hook_visual_screen_rect)

        if self.fish_on_line_awaiting_pull and self.hooked_fish_sprite:
            font_to_use = self.game.debug_font
            if hasattr(self.game.ui, 'small_font') and self.game.ui.small_font:
                 font_to_use = self.game.ui.small_font

            prompt_text = font_to_use.render("SPACE!", True, self.config.COLORS.get('legendary', (255,215,0)))
            prompt_rect = prompt_text.get_rect(midbottom=hook_visual_screen_rect.midtop)
            prompt_rect.y -= 5
            screen.blit(prompt_text, prompt_rect)
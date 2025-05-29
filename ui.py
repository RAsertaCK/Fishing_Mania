# IMPROVE/ui.py
import pygame
import os 

class UI:
    def __init__(self, game):
        self.game = game
        self.config = self.game.config
        
        try:
            font_name_to_load = self.config.FONT_NAME
            medium_font_size = self.config.FONT_SIZES.get('medium', 30)
            small_font_size = self.config.FONT_SIZES.get('small', 18)

            if font_name_to_load and os.path.exists(font_name_to_load):
                self.font = pygame.font.Font(font_name_to_load, medium_font_size)
                self.small_font = pygame.font.Font(font_name_to_load, small_font_size)
            else:
                if font_name_to_load and font_name_to_load.lower() != 'none':
                     pass
                fallback_font_name_ui = "arial"
                if font_name_to_load and font_name_to_load.lower() != 'none' and font_name_to_load != "":
                    fallback_font_name_ui = font_name_to_load
                
                self.font = pygame.font.SysFont(fallback_font_name_ui, medium_font_size)
                self.small_font = pygame.font.SysFont(fallback_font_name_ui, small_font_size)
        except Exception as e:
            self.font = pygame.font.Font(None, 30)
            self.small_font = pygame.font.Font(None, 18)

    def render(self, screen):
        # Tampilkan Koin
        coins_text_surface = self.font.render(f"Koin: {self.game.wallet}", True, self.config.COLORS.get('text_selected', (255,255,0)))
        screen.blit(coins_text_surface, (10, 10))

        # Tampilkan Lokasi
        current_location_name = "N/A"
        if self.game.current_state_name == 'fishing' and self.game.current_game_map and hasattr(self.game.current_game_map, 'display_name'):
            current_location_name = self.game.current_game_map.display_name
        elif self.game.current_state_name == 'map_explore' and self.game.map_explorer:
            active_spot_map_name = getattr(self.game.map_explorer, 'active_spot_map_name', None)
            if active_spot_map_name:
                for dn, sd in self.game.map_explorer.fishing_spots_data.items():
                    if sd.get('map_name') == active_spot_map_name:
                        current_location_name = f"Dekat: {dn}"
                        break
            if current_location_name == "N/A":
                 current_location_name = "Peta Dunia"
        elif self.game.current_state_name == 'land_explore': # --- PENAMBAHAN DI SINI ---
            current_location_name = "Daratan"
        
        if current_location_name != "N/A":
            location_text_surface = self.small_font.render(f"Lokasi: {current_location_name}", True, self.config.COLORS.get('white', (255,255,255)))
            screen.blit(location_text_surface, (10, self.font.get_height() + 15))

        # Tampilkan info ikan yang terkait
        # Akses dengan aman, pastikan fishing_system ada dan punya atributnya
        if self.game.current_state_name == 'fishing' and \
           self.game.fishing_system and \
           hasattr(self.game.fishing_system, 'current_hooked_fish_data') and \
           self.game.fishing_system.current_hooked_fish_data:
            
            hooked_fish_data = self.game.fishing_system.current_hooked_fish_data
            fish_name = hooked_fish_data.get('name', 'Ikan Misterius') if isinstance(hooked_fish_data, dict) else getattr(hooked_fish_data, 'name', 'Ikan Misterius')
            fish_rarity = hooked_fish_data.get('rarity', 'N/A') if isinstance(hooked_fish_data, dict) else getattr(hooked_fish_data, 'rarity', 'N/A')
            
            fish_info_text = f"TERKAIT: {fish_name} ({fish_rarity})"
            fish_info_surface = self.font.render(fish_info_text, True, self.config.COLORS.get('legendary'))
            fish_info_rect = fish_info_surface.get_rect(midtop=(self.config.SCREEN_WIDTH // 2, 10))
            screen.blit(fish_info_surface, fish_info_rect)

        # Tampilkan bar kedalaman kail
        if self.game.current_state_name == 'fishing' and \
           self.game.fishing_system and \
           hasattr(self.game.fishing_system, 'hook_depth') and \
           hasattr(self.game.fishing_system, 'max_hook_depth'):
            
            if self.game.fishing_system.max_hook_depth > 0:
                depth_percent = self.game.fishing_system.hook_depth / self.game.fishing_system.max_hook_depth
                depth_percent = max(0, min(1, depth_percent))

                bar_width = 120
                bar_height = 15
                bar_x = self.config.SCREEN_WIDTH - bar_width - 10
                bar_y = 10
                
                pygame.draw.rect(screen, self.config.COLORS.get('white'), (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4), 2)
                fill_width = bar_width * depth_percent
                pygame.draw.rect(screen, self.config.COLORS.get('blue'), (bar_x, bar_y, fill_width, bar_height))
                
                depth_text_surface = self.small_font.render("Kedalaman", True, self.config.COLORS.get('white'))
                screen.blit(depth_text_surface, (bar_x + bar_width // 2 - depth_text_surface.get_width() // 2, bar_y + bar_height + 3))
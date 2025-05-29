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
        self.is_waiting_for_bite = False 
        self.hook_depth = 0 
        
        if self.game.current_game_map and hasattr(self.game.current_game_map, 'data') and \
           'depth_range' in self.game.current_game_map.data: 
            self.max_hook_depth = self.game.current_game_map.data['depth_range'][1] 
        else:
            self.max_hook_depth = 200 
        
        self.cast_speed = 150 
        self.reel_speed = 180 

        self.current_hooked_fish_data = None 
        self.challenge_active = False 
        
        self.hook_color = self.config.COLORS.get("white", (255,255,255)) 
        self.line_color = self.config.COLORS.get("text_inactive", (180,180,180)) 
        self.hook_width = 6 
        self.hook_tip_height = 12 

        self.bite_timer_start = 0 
        self.current_wait_time_for_bite = 0 

    def start_cast(self):
        if not self.is_casting and not self.is_reeling and not self.current_hooked_fish_data and not self.challenge_active: 
            print("--- FishingSystem: Memulai lemparan (cast). ---") 
            self.is_casting = True 
            self.is_reeling = False 
            self.is_waiting_for_bite = False 
            self.current_hooked_fish_data = None 
            self.hook_depth = 0 

    def start_reel_in(self, from_challenge_resolve=False):
        print(f"--- FishingSystem: Memulai gulungan (reel in). From challenge: {from_challenge_resolve} ---") 
        self.is_reeling = True 
        self.is_casting = False 
        self.is_waiting_for_bite = False 
        if not from_challenge_resolve and self.current_hooked_fish_data and not self.challenge_active: 
            self.start_fishing_challenge(self.current_hooked_fish_data) 

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN: 
            if event.key == pygame.K_SPACE: 
                if self.challenge_active and self.game.fishing_challenge: 
                    pass 
                elif not self.is_casting and not self.is_reeling and not self.current_hooked_fish_data: 
                    self.start_cast() 
                    return True 
                elif self.is_casting or self.is_waiting_for_bite: 
                    self.start_reel_in() 
                    return True 
        return False 

    def update(self, dt):
        if self.is_casting: 
            self.hook_depth += self.cast_speed * dt 
            if self.hook_depth >= self.max_hook_depth: 
                self.hook_depth = self.max_hook_depth 
                self.is_casting = False 
                self.is_waiting_for_bite = True 
                self.bite_timer_start = pygame.time.get_ticks() 
                self.current_wait_time_for_bite = random.randint(2000, 5000) 
                print(f"--- FishingSystem: Kail mencapai kedalaman maks. Menunggu gigitan selama {self.current_wait_time_for_bite/1000}s. ---") 

        elif self.is_waiting_for_bite: 
            if pygame.time.get_ticks() - self.bite_timer_start >= self.current_wait_time_for_bite: 
                self.is_waiting_for_bite = False 
                print("--- FishingSystem: Waktu tunggu habis. Cek gigitan... ---") 
                if self.game.current_game_map and hasattr(self.game.current_game_map, 'get_random_fish_data'): 
                    fish_data = self.game.current_game_map.get_random_fish_data() 
                    if fish_data: 
                        print(f"--- FishingSystem: IKAN TERKAIT! Data: {fish_data['name']} ---") 
                        self.current_hooked_fish_data = fish_data 
                        self.start_fishing_challenge(self.current_hooked_fish_data) 
                    else: 
                        print("--- FishingSystem: Tidak ada ikan yang menggigit. Menggulung... ---") 
                        self.start_reel_in() 
                else: 
                    self.start_reel_in() 

        elif self.is_reeling: 
            reel_speed_actual = self.reel_speed 
            self.hook_depth -= reel_speed_actual * dt 
            if self.hook_depth <= 0: 
                self.hook_depth = 0 
                self.is_reeling = False 
                if self.current_hooked_fish_data and not self.challenge_active: 
                    print(f"--- FishingSystem: Ikan {self.current_hooked_fish_data.get('name', 'Misterius')} berhasil ditarik ke perahu (setelah challenge)! ---") 
                elif not self.current_hooked_fish_data: 
                    print("--- FishingSystem: Gulungan kosong selesai. ---") 
                self.current_hooked_fish_data = None 

        if self.challenge_active and self.game.fishing_challenge: 
            if hasattr(self.game.fishing_challenge, 'update'): 
                 self.game.fishing_challenge.update() 
            
            challenge_result_status = getattr(self.game.fishing_challenge, 'result', None) 
            if challenge_result_status is not None: 
                self.resolve_fishing_challenge(challenge_result_status == "caught") 

    def start_fishing_challenge(self, fish_data_hooked):
        if self.game.fishing_challenge and hasattr(self.game.fishing_challenge, 'start'): 
            print(f"--- FishingSystem: Memulai fishing challenge untuk {fish_data_hooked.get('name')} ---") 
            self.game.fishing_challenge.start() 
            self.challenge_active = True 
            self.is_casting = False 
            self.is_waiting_for_bite = False 
            if not self.is_reeling: self.is_reeling = True 


    def resolve_fishing_challenge(self, success):
        print(f"--- FishingSystem: Menyelesaikan fishing challenge. Sukses: {success} ---") 
        self.challenge_active = False 
        if self.game.fishing_challenge: 
            self.game.fishing_challenge.result = None 

        hooked_fish_name = self.current_hooked_fish_data.get('name', 'Ikan Misterius') if self.current_hooked_fish_data else "Ikan Tak Dikenal" 

        if success and self.current_hooked_fish_data: 
            print(f"    SELAMAT! Ikan {hooked_fish_name} berhasil ditangkap!") 
            if self.game.inventory and hasattr(self.game.inventory, 'add_fish_from_data'): 
                self.game.inventory.add_fish_from_data(self.current_hooked_fish_data) 
            else: 
                print(f"    ERROR: Tidak bisa menambahkan ikan {hooked_fish_name} ke inventaris.") 
            
            if hasattr(self.game, 'wallet'): 
                fish_value = self.current_hooked_fish_data.get('value', 0) 
                self.game.wallet += fish_value 
                print(f"    Koin bertambah {fish_value}. Total koin: {self.game.wallet}") 

        else: 
            print(f"    SAYANG SEKALI, ikan {hooked_fish_name} lepas!") 
        
        self.current_hooked_fish_data = None 

        if not self.is_reeling and self.hook_depth > 0 : 
            self.start_reel_in(from_challenge_resolve=True) 
        elif self.hook_depth <= 0: 
            self.is_reeling = False 


    def render_with_camera(self, screen, camera):
        if not (self.is_casting or self.is_reeling or self.is_waiting_for_bite or self.challenge_active) or \
           not self.game.boat or not self.game.boat.rect:
            return
            
        boat_screen_rect = camera.apply(self.game.boat.rect)

        line_start_x = boat_screen_rect.centerx
        line_start_y = boat_screen_rect.top + 10 

        water_surface_y_on_screen = boat_screen_rect.bottom - 25 
        hook_end_y_on_screen = water_surface_y_on_screen + self.hook_depth
        hook_end_x_on_screen = line_start_x 

        pygame.draw.line(screen, self.line_color, 
                         (line_start_x, line_start_y), 
                         (hook_end_x_on_screen, hook_end_y_on_screen), 2)

        hook_visual_rect = pygame.Rect(hook_end_x_on_screen - self.hook_width // 2, 
                                       hook_end_y_on_screen - self.hook_tip_height // 2, 
                                       self.hook_width, self.hook_tip_height)
        pygame.draw.ellipse(screen, self.hook_color, hook_visual_rect)

        if self.current_hooked_fish_data and not self.challenge_active: 
            fish_name_text = self.current_hooked_fish_data.get('name', 'Fish?') 
            rarity_text = self.current_hooked_fish_data.get('rarity', '') 
            
            rarity_color_key = rarity_text.lower() if rarity_text else 'common' 
            text_color = self.config.COLORS.get(rarity_color_key, self.config.COLORS.get('white')) 

            if hasattr(self.game, 'debug_font'): 
                fish_label = self.game.debug_font.render(f"~{fish_name_text}~ ({rarity_text})", True, text_color) 
                screen.blit(fish_label, (hook_visual_rect.centerx + 10, hook_visual_rect.centery - fish_label.get_height()//2))
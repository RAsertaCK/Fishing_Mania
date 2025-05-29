# TES/game.py
import pygame
import sys
import os
import random 

from config import Config
from menu import MainMenu, SettingsMenu, ShopMenu, MarketScreen, InventoryScreen
from camera_system import Camera 
from player import Player as PlayerBoat
from boat import Boat
from game_map import GameMap
from ui import UI
from inventory import Inventory
from market import Market
from map_explore import MapExplorer
from fishing_system import FishingSystem
from fishing_challenge import FishingSkillChallenge
from land_explorer import LandExplorer
from sprites import Player as LandPlayer, Spritesheet

class Game:
    def __init__(self, screen):
        print("--- Game: Memulai Game.__init__()... ---")
        self.screen = screen
        self.config = Config()
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_fps = 0

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

            if actual_font_path:
                self.debug_font = pygame.font.Font(actual_font_path, small_font_size)
            elif font_name_to_load and font_name_to_load.strip() != "" and font_name_to_load.lower() != 'none':
                 self.debug_font = pygame.font.SysFont(font_name_to_load, small_font_size)
            else:
                self.debug_font = pygame.font.SysFont("arial", small_font_size)
            print("--- Game: Debug font berhasil dimuat/fallback. ---")
        except Exception as e:
            print(f"--- Game: ERROR saat memuat debug font: {e}. Menggunakan default absolut. ---")
            self.debug_font = pygame.font.Font(None, 24)

        self.current_state_name = 'main_menu'
        self.wallet = 100

        self.inventory = Inventory()
        self.market = Market(self)

        class InitialDummyMap: 
            def __init__(self):
                self.name = "initial_setup"
                self.data = {'depth_range': (10, 100)} 
                self.background_image_original = pygame.Surface((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT)) 
                self.background_image = self.background_image_original 
        
        self.fishing_world_rect = pygame.Rect(0, 0, self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT)
        # Nilai ini akan di-override di change_state, tapi baik untuk punya default
        self.water_top_y = self.config.SCREEN_HEIGHT * 0.60  
        self.water_bottom_y = self.config.SCREEN_HEIGHT * 0.95 

        self.boat = Boat(InitialDummyMap(), self.config, self.fishing_world_rect) 

        self.main_menu = MainMenu(self)
        self.settings_menu = SettingsMenu(self)
        self.shop_menu = ShopMenu(self)
        self.market_screen = MarketScreen(self)
        self.inventory_screen = InventoryScreen(self)
        
        self.all_sprites = pygame.sprite.Group() 
        self.blocks = pygame.sprite.Group() 

        try:
            self.character_spritesheet = Spritesheet(self.config.PLAYER_SPRITESHEET_PATH) #
            print(f"--- Game: Spritesheet karakter '{self.config.PLAYER_SPRITESHEET_PATH}' dimuat. ---") #
        except Exception as e:
            print(f"--- Game: ERROR memuat spritesheet karakter: {e}. Player darat mungkin tidak tampil. ---") #
            self.character_spritesheet = None

        self.land_player = None
        if self.character_spritesheet:
            self.land_player = LandPlayer(self, 10, 10) #
            print(f"--- Game: LandPlayer (pemain darat) berhasil diinisialisasi. ---") #
        else:
            print("--- Game: LandPlayer tidak dapat diinisialisasi karena spritesheet gagal dimuat. ---") #

        self.land_explorer = LandExplorer(self) #
        self.map_explorer = MapExplorer(self) #

        self.current_game_map = None
        self.player = None # PlayerBoat

        self.fishing_system = None #
        self.fishing_challenge = None #
        
        self.fishing_camera = Camera(self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT, self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT) #
        self.visible_fish_sprites = pygame.sprite.Group()

        self.ui = UI(self) #
        print("--- Game: Game.__init__() selesai. ---")

    def change_state(self, new_state_name, data=None):
        print(f"--- Game: Mengubah state dari {self.current_state_name} ke {new_state_name} dengan data: {data} ---") #
        
        self.all_sprites.empty() #
        self.blocks.empty() #

        if self.current_state_name not in ['main_menu', 'settings'] and \
           new_state_name not in ['fishing', 'map_explore', 'land_explore']: #
             if pygame.mixer.music.get_busy(): #
                pygame.mixer.music.fadeout(500) #

        old_state = self.current_state_name #
        self.current_state_name = new_state_name #

        if new_state_name == 'land_explore':
            print("--- Game: Memproses state land_explore ---") #
            if self.land_explorer: #
                self.land_explorer.setup_scene() #

        elif new_state_name == 'map_explore':
            print("--- Game: Memproses state map_explore (laut) ---") #

        elif new_state_name == 'fishing':
            print("--- Game: Memproses state fishing ---") #
            if data and 'location_name' in data: #
                location_name = data['location_name'] #
                print(f"--- Game: Data lokasi diterima: {location_name} ---") #
                try:
                    self.current_game_map = GameMap(location_name, self.config) #
                    if hasattr(self.current_game_map, 'play_music'): self.current_game_map.play_music() #
                    
                    fishing_world_width = int(self.config.SCREEN_WIDTH * 1.5) 
                    fishing_world_height = self.config.SCREEN_HEIGHT
                    self.fishing_world_rect = pygame.Rect(0, 0, fishing_world_width, fishing_world_height)

                    self.fishing_camera.world_width = fishing_world_width
                    self.fishing_camera.world_height = fishing_world_height
                    
                    # Atur posisi X kamera agar perahu di tengah view horizontal
                    if self.boat and self.boat.rect:
                        # Posisikan perahu di tengah dunia dulu sebelum set kamera
                        self.boat.rect.centerx = self.fishing_world_rect.centerx 
                        self.fishing_camera.offset_x = - (self.boat.rect.centerx - self.config.SCREEN_WIDTH // 2)
                    else: # Jika boat belum ada (seharusnya tidak terjadi jika alur benar)
                        self.fishing_camera.offset_x = - (self.fishing_world_rect.centerx - self.config.SCREEN_WIDTH // 2)
                    
                    self.fishing_camera.offset_y = 0 # Kamera tidak bergerak vertikal di map fishing
                    
                    # === PENENTUAN POSISI VERTIKAL KAPAL & AIR ===
                    # Berdasarkan screenshot Anda (misal Screenshot 2025-05-29 072946.png),
                    # kapal berada di bagian bawah layar.
                    # Kita tentukan Y untuk bagian bawah kapal.
                    # **PENTING: SESUAIKAN NILAI INI AGAR PAS DENGAN VISUAL LATAR ANDA**
                    target_boat_bottom_y = self.config.SCREEN_HEIGHT * 0.88 # Contoh: 88% dari atas layar
                                                                        # (0.88 * 720 = ~Y=633)
                    
                    # Zona air untuk ikan berenang akan berada di bawah kapal.
                    # water_top_y kini menjadi batas atas area renang ikan, sedikit di bawah kapal.
                    self.water_top_y = target_boat_bottom_y + 5 # Ikan mulai berenang sedikit di bawah dasar kapal
                    self.water_bottom_y = self.config.SCREEN_HEIGHT * 0.98 # Dasar area renang ikan, hampir di bawah layar
                    
                    if self.water_bottom_y <= self.water_top_y: # Fallback
                        self.water_top_y = self.config.SCREEN_HEIGHT * 0.70
                        self.water_bottom_y = self.config.SCREEN_HEIGHT * 0.95
                    print(f"--- Game: Posisi target bawah kapal Y: {target_boat_bottom_y} ---")
                    print(f"--- Game: Batas air (ikan) dunia diatur ke Y: {self.water_top_y} - {self.water_bottom_y} ---")
                    # === AKHIR PENENTUAN POSISI VERTIKAL ===

                    if self.boat:
                        self.boat.change_map(self.current_game_map, self.fishing_world_rect) 
                        if self.boat.rect:
                             self.boat.rect.centerx = self.fishing_world_rect.centerx 
                             self.boat.rect.bottom = target_boat_bottom_y # Set posisi Y kapal
                             print(f"--- Game: Posisi aktual perahu diatur ke bottom Y: {self.boat.rect.bottom} ---")
                    else: 
                        self.boat = Boat(self.current_game_map, self.config, self.fishing_world_rect)
                        if self.boat.rect: 
                             self.boat.rect.centerx = self.fishing_world_rect.centerx
                             self.boat.rect.bottom = target_boat_bottom_y

                    if not self.player:
                        self.player = PlayerBoat(self.boat, self) #
                    else:
                        if hasattr(self.player, 'boat'): self.player.boat = self.boat #
                    
                    if self.player: self.player.update_position()
                    
                    if self.boat and self.boat.rect: self.fishing_camera.update(self.boat.rect)

                    self.fishing_system = FishingSystem(self) #
                    self.fishing_challenge = FishingSkillChallenge() #
                    
                    self.visible_fish_sprites.empty()
                    self.spawn_visible_fish(amount=random.randint(5, 8)) 
                    
                    print(f"--- Game: Setup untuk state fishing lokasi '{location_name}' selesai. Dunia: {fishing_world_width}x{fishing_world_height} ---") #
                except Exception as e:
                    print(f"--- Game: ERROR saat setup state fishing: {e} ---") #
                    import traceback #
                    traceback.print_exc() #
                    self.change_state('map_explore') #
                    return
            else:
                print("--- Game: ERROR - Tidak ada location_name untuk state fishing! Kembali ke map_explore. ---") #
                self.change_state('map_explore') #
                return
        elif new_state_name == 'shop': 
            if self.shop_menu and hasattr(self.shop_menu, 'update_options'):
                self.shop_menu.update_options()
        elif new_state_name == 'market_screen': 
            if self.market_screen and hasattr(self.market_screen, 'update_options'):
                self.market_screen.update_options()
        elif new_state_name == 'inventory_screen': 
            if self.inventory_screen and hasattr(self.inventory_screen, 'update_options'):
                self.inventory_screen.update_options()
        elif new_state_name == 'main_menu': 
            pass

    def spawn_visible_fish(self, amount=5):
        if not self.current_game_map or not self.fishing_camera:
            return
        
        if not hasattr(self, 'water_top_y') or not hasattr(self, 'water_bottom_y'):
            print("PERINGATAN Game.spawn_visible_fish: Batas air (water_top_y/water_bottom_y) belum diinisialisasi!")
            # **PENTING: SESUAIKAN NILAI FALLBACK INI JUGA JIKA PERLU**
            self.water_top_y = self.config.SCREEN_HEIGHT * 0.70 # Contoh Fallback
            self.water_bottom_y = self.config.SCREEN_HEIGHT * 0.95 # Contoh Fallback

        from fish import Fish 
        print(f"--- Game: Spawning {amount} visible fish... ---")

        for _ in range(amount):
            fish_data = self.current_game_map.get_random_fish_data() #
            if fish_data: 
                spawn_x = random.randint(0, self.fishing_world_rect.width)
                # Ikan spawn di antara batas atas (water_top_y) dan bawah air (water_bottom_y)
                min_spawn_y = int(self.water_top_y + 5) # +5 agar tidak pas di batas atas ikan
                max_spawn_y = int(self.water_bottom_y - 5) # -5 agar tidak pas di batas bawah ikan
                
                if max_spawn_y <= min_spawn_y: 
                    max_spawn_y = min_spawn_y + 20 
                    if max_spawn_y > self.water_bottom_y: 
                        max_spawn_y = int(self.water_bottom_y)
                
                if min_spawn_y >= max_spawn_y:
                    spawn_y = (self.water_top_y + self.water_bottom_y) / 2
                else:
                    spawn_y = random.randint(min_spawn_y, max_spawn_y)
                
                new_fish = Fish(fish_data, (spawn_x, spawn_y), self.config) #
                self.visible_fish_sprites.add(new_fish)
            else:
                print("--- Game.spawn_visible_fish: get_random_fish_data() mengembalikan None, ikan tidak di-spawn ---")
        print(f"--- Game: Spawned {len(self.visible_fish_sprites)} fish. ---")


    def play_music_file(self, music_path, loop=-1):
        if os.path.exists(music_path): #
            try:
                pygame.mixer.music.load(music_path) #
                pygame.mixer.music.play(loop, fade_ms=1000) #
                print(f"--- Game: Memainkan musik: {music_path} ---") #
            except pygame.error as e:
                print(f"--- Game: Error memainkan musik {music_path}: {e} ---") #
        else:
            print(f"--- Game: File musik tidak ditemukan: {music_path} ---") #

    def run(self):
        print("--- Game: Memulai Game.run()... ---") #
        if self.current_state_name == 'main_menu': #
            pass 

        print("--- Game: Memasuki game loop utama. ---") #
        while self.running: #
            dt = self.clock.tick(self.config.FPS) / 1000.0 #
            if dt > 0.1 : dt = 0.1 #
            self.current_fps = self.clock.get_fps() #

            for event in pygame.event.get(): #
                if event.type == pygame.QUIT: #
                    print("--- Game: Event pygame.QUIT diterima. Menghentikan game. ---") #
                    self.running = False #
                
                if self.running: #
                    self.handle_state_specific_event(event) #

            if not self.running: #
                break

            try:
                self.update_current_state(dt) #
            except Exception as e:
                print(f"--- ERROR DI DALAM UPDATE STATE ({self.current_state_name}) ---") #
                print(f"Detail Error: {e}") #
                import traceback #
                traceback.print_exc() #
                self.running = False #

            if not self.running: break #

            try:
                self.render_current_state() #
            except Exception as e:
                print(f"--- ERROR DI DALAM RENDER STATE ({self.current_state_name}) ---") #
                print(f"Detail Error: {e}") #
                import traceback #
                traceback.print_exc() #
                self.running = False #
        
        print("--- Game: Keluar dari game loop utama. ---") #
        self.quit_game() #

    def handle_state_specific_event(self, event):
        active_handler = None #
        handled_by_specific_logic = False #

        if self.current_state_name == 'fishing': #
            if self.fishing_system and hasattr(self.fishing_system, 'challenge_active') and self.fishing_system.challenge_active: #
                pass
            
            if not handled_by_specific_logic and self.fishing_system and hasattr(self.fishing_system, 'handle_event'): #
                if self.fishing_system.handle_event(event): #
                    handled_by_specific_logic = True #
            
            if not handled_by_specific_logic and event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: #
                self.change_state('map_explore') #
                handled_by_specific_logic = True #
        
        if handled_by_specific_logic: #
            return

        if self.current_state_name == 'main_menu': active_handler = self.main_menu #
        elif self.current_state_name == 'settings': active_handler = self.settings_menu #
        elif self.current_state_name == 'shop': active_handler = self.shop_menu #
        elif self.current_state_name == 'market_screen': active_handler = self.market_screen #
        elif self.current_state_name == 'inventory_screen': active_handler = self.inventory_screen #
        elif self.current_state_name == 'land_explore': active_handler = self.land_explorer #
        elif self.current_state_name == 'map_explore': active_handler = self.map_explorer #
        
        if active_handler and hasattr(active_handler, 'handle_event'): #
            active_handler.handle_event(event) #


    def update_current_state(self, dt):
        if self.current_state_name == 'land_explore': #
            if self.land_explorer and hasattr(self.land_explorer, 'update'): #
                self.land_explorer.update(dt) #
            if self.land_player: #
                self.land_player.update() #
        elif self.current_state_name == 'map_explore': #
            if self.map_explorer and hasattr(self.map_explorer, 'update'): #
                self.map_explorer.update(dt) #
        elif self.current_state_name == 'fishing': #
            if self.boat and hasattr(self.boat, 'update'): #
                self.boat.update(dt, pygame.key.get_pressed()) #
            if self.player and hasattr(self.player, 'update'): #
                self.player.update(dt) #
            
            for fish_sprite in self.visible_fish_sprites:
                fish_sprite.update(dt) #
                if self.fishing_world_rect: 
                    # Batas horizontal dunia
                    if fish_sprite.rect.left < self.fishing_world_rect.left and fish_sprite.swim_direction < 0:
                        fish_sprite.swim_direction *= -1
                        fish_sprite.rect.left = self.fishing_world_rect.left
                    elif fish_sprite.rect.right > self.fishing_world_rect.right and fish_sprite.swim_direction > 0:
                        fish_sprite.swim_direction *= -1
                        fish_sprite.rect.right = self.fishing_world_rect.right
                    
                    # Batas vertikal ikan menggunakan self.water_top_y dan self.water_bottom_y
                    if hasattr(self, 'water_top_y') and hasattr(self, 'water_bottom_y'):
                        # Ikan harus berenang DI BAWAH kapal, jadi batas atasnya adalah water_top_y + sedikit
                        min_fish_y_for_render = self.water_top_y + 5 # Ikan mulai sedikit di bawah permukaan air kapal
                        
                        if fish_sprite.rect.top < min_fish_y_for_render:
                            fish_sprite.rect.top = min_fish_y_for_render
                            if fish_sprite.pos: fish_sprite.pos[1] = min_fish_y_for_render + (fish_sprite.rect.height / 2) + random.uniform(0,2) 
                        if fish_sprite.rect.bottom > self.water_bottom_y:
                            fish_sprite.rect.bottom = self.water_bottom_y
                            if fish_sprite.pos: fish_sprite.pos[1] = self.water_bottom_y - (fish_sprite.rect.height / 2) - random.uniform(0,2) 
                    else: 
                         min_y_fallback = self.config.SCREEN_HEIGHT * 0.68 
                         max_y_fallback = self.config.SCREEN_HEIGHT * 0.95
                         if fish_sprite.rect.top < min_y_fallback : fish_sprite.rect.top = min_y_fallback
                         if fish_sprite.rect.bottom > max_y_fallback : fish_sprite.rect.bottom = max_y_fallback


            if self.fishing_system and hasattr(self.fishing_system, 'update'): #
                self.fishing_system.update(dt) #
            
            if self.boat and self.boat.rect and self.fishing_camera: #
                self.fishing_camera.update(self.boat.rect) #
        
    def render_current_state(self):
        self.screen.fill(self.config.COLORS.get('black', (0,0,0))) #

        active_renderer = None
        if self.current_state_name == 'main_menu': active_renderer = self.main_menu #
        elif self.current_state_name == 'settings': active_renderer = self.settings_menu #
        elif self.current_state_name == 'shop': active_renderer = self.shop_menu # Perbaikan dari active_handler ke active_renderer
        elif self.current_state_name == 'market_screen': active_renderer = self.market_screen #
        elif self.current_state_name == 'inventory_screen': active_renderer = self.inventory_screen #
        
        if self.current_state_name == 'land_explore': #
            if self.land_explorer and hasattr(self.land_explorer, 'render'): #
                self.land_explorer.render(self.screen) #
        elif self.current_state_name == 'map_explore': #
            if self.map_explorer and hasattr(self.map_explorer, 'render'): #
                self.map_explorer.render(self.screen) #
        elif self.current_state_name == 'fishing': #
            # Render latar belakang statis
            if self.current_game_map and hasattr(self.current_game_map, 'background_image'): #
                self.screen.blit(self.current_game_map.background_image, (0,0)) # Latar statis
            else: #
                self.screen.fill(self.config.COLORS.get('water_deep', (5,30,56))) #
            
            # Render ikan yang terlihat (dengan kamera)
            if self.fishing_camera: 
                for fish_sprite in self.visible_fish_sprites:
                    if fish_sprite.image and fish_sprite.rect:
                        img_to_render = pygame.transform.flip(fish_sprite.image, True, False) if fish_sprite.swim_direction < 0 else fish_sprite.image 
                        self.screen.blit(img_to_render, self.fishing_camera.apply(fish_sprite.rect))

            # Render perahu (dengan kamera)
            if self.boat and hasattr(self.boat, 'render_with_camera') and self.fishing_camera: #
                 self.boat.render_with_camera(self.screen, self.fishing_camera) 
            
            # Render pemain di perahu (dengan kamera)
            if self.player and hasattr(self.player, 'render_with_camera') and self.fishing_camera: #
                 self.player.render_with_camera(self.screen, self.fishing_camera) 

            # Render sistem pancing (dengan kamera)
            if self.fishing_system and hasattr(self.fishing_system, 'render_with_camera') and self.fishing_camera: #
                self.fishing_system.render_with_camera(self.screen, self.fishing_camera) #
            
            # Render fishing challenge (overlay, tanpa kamera)
            if self.fishing_system and hasattr(self.fishing_system, 'challenge_active') and self.fishing_system.challenge_active: #
                if self.fishing_challenge and hasattr(self.fishing_challenge, 'render'): #
                    self.fishing_challenge.render(self.screen) #
        
        if active_renderer and hasattr(active_renderer, 'render'): 
            active_renderer.render(self.screen) 

        if self.ui and hasattr(self.ui, 'render') and self.current_state_name in ['land_explore', 'map_explore', 'fishing']: #
            self.ui.render(self.screen) #

        if self.config.DEBUG: 
            # ... (kode debug info sama seperti sebelumnya) ...
            debug_text_y = self.config.SCREEN_HEIGHT - self.debug_font.get_height() - 5 
            fps_text_surface = self.debug_font.render(f"FPS: {int(self.current_fps)}", True, self.config.COLORS.get('white', (255,255,255))) 
            self.screen.blit(fps_text_surface, (10, debug_text_y )) 
            
            state_text_surface = self.debug_font.render(f"State: {self.current_state_name}", True, self.config.COLORS.get('white', (255,255,255))) 
            state_text_x = fps_text_surface.get_width() + 20 
            self.screen.blit(state_text_surface, (state_text_x, debug_text_y)) 

            if self.current_state_name == 'fishing' and self.fishing_camera:
                cam_info = f"Cam Offset: ({int(self.fishing_camera.offset_x)}, {int(self.fishing_camera.offset_y)})"
                cam_text = self.debug_font.render(cam_info, True, self.config.COLORS.get('white'))
                self.screen.blit(cam_text, (state_text_x + state_text_surface.get_width() + 20, debug_text_y))
                if self.boat and self.boat.rect:
                    boat_info = f"Boat World: ({self.boat.rect.x}, {self.boat.rect.y})"
                    boat_text = self.debug_font.render(boat_info, True, self.config.COLORS.get('white'))
                    self.screen.blit(boat_text, (state_text_x + state_text_surface.get_width() + 20, debug_text_y - self.debug_font.get_height() - 2))


        pygame.display.flip() 

    def quit_game(self):
        print("--- Game: Menutup game (quit_game dipanggil)... ---") 
        pygame.quit() 
        sys.exit()
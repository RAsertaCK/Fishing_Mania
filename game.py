# game.py
import pygame
import sys
import os
import random
import traceback

from config import Config
from menu import MainMenu, ShopMenu, MarketScreen, InventoryScreen # SettingsMenu sudah kita asumsikan tidak dipakai
from camera_system import Camera
from player import Player as PlayerBoat
from boat import Boat
from game_map import GameMap
from ui import UI
from inventory import Inventory
from market import Market
from map_explore import MapExplorer
from fishing_system import FishingSystem
from land_explorer import LandExplorer
from sprites import Player as LandPlayer, Spritesheet
from game_data import GameData

class Game:
    def __init__(self, screen):
        print("--- Game: Memulai Game.__init__()... ---")
        self.screen = screen
        self.config = Config() 
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_fps = 0

        # 1. Inisialisasi atribut dasar Game dengan nilai default Python
        #    Ini penting agar _apply_data_to_game_instance (dipanggil oleh load_game)
        #    tidak error saat mencoba mengisi atribut yang belum ada.
        self.wallet = 0 
        self.current_state_name = "main_menu" 
        self.unlocked_locations = {"Coast": True, "Sea": False, "Ocean": False}
        self.current_music_file = None # Atribut untuk melacak musik

        # 2. Inisialisasi komponen game yang mungkin dibutuhkan oleh GameData
        #    atau yang datanya akan diisi/diupdate oleh GameData.load_game()
        self.inventory = Inventory(self)
        self.market = Market(self)

        class InitialDummyMap:
            def __init__(self_map, parent_game_instance): # Menggunakan self_map untuk inner class
                self_map.name = "initial_dummy_map_for_boat"
                self_map.data = {'depth_range': (10,100)}
                self_map.background_image = pygame.Surface(
                    (parent_game_instance.config.SCREEN_WIDTH, parent_game_instance.config.SCREEN_HEIGHT)
                )
                self_map.background_image.fill((0,0,50))
        
        self.fishing_world_rect = pygame.Rect(0,0,self.config.SCREEN_WIDTH,self.config.SCREEN_HEIGHT)
        self.boat = Boat(InitialDummyMap(self), self.config, self.fishing_world_rect)

        # --- URUTAN DIPERBAIKI ---
        # 3. Inisialisasi GameData SEKARANG.
        #    MapExplorer dan komponen lain mungkin membutuhkan game_data_manager.
        self.game_data_manager = GameData(self) 
        
        # 4. SEKARANG baru inisialisasi MapExplorer dan LandExplorer,
        #    karena mereka mungkin mengakses self.game.game_data_manager atau self.game.config.
        self.map_explorer = MapExplorer(self)
        
        try: 
            self.character_spritesheet = Spritesheet(self.config.PLAYER_SPRITESHEET_PATH) 
        except Exception as e: 
            print(f"--- Game: ERROR memuat spritesheet karakter: {e}. ---")
            self.character_spritesheet = None
            
        self.land_player = None # land_player dibuat sebelum LandExplorer jika LandExplorer membutuhkannya
        if self.character_spritesheet:
            self.land_player = LandPlayer(self,5,5) # Posisi awal x,y dalam tile jika relevan
        else:
            print("--- Game: PERINGATAN - Tidak bisa membuat LandPlayer karena character_spritesheet gagal dimuat.")
        self.land_explorer = LandExplorer(self) # LandExplorer akan menggunakan self.land_player yang sudah ada (atau None)
        # -------------------------

        # 5. Panggil load_game SETELAH semua komponen utama yang mungkin diakses
        #    oleh _apply_data_to_game_instance (via load_game) sudah ada.
        try:
            print("--- Game: Memanggil self.game_data_manager.load_game()... ---")
            self.game_data_manager.load_game() 
            print("--- Game: Selesai memanggil self.game_data_manager.load_game(). ---")
            # Atribut seperti self.wallet, self.current_state_name, self.boat.upgrades, 
            # self.unlocked_locations, self.inventory.fish_list, 
            # dan self.map_explorer.player_map_rect.centerx/y
            # seharusnya sudah diisi dengan benar oleh _apply_data_to_game_instance
            # yang dipanggil dari dalam load_game().
        except Exception as e:
            print(f"--- Game.__init__: ERROR saat self.game_data_manager.load_game(): {e} ---")
            traceback.print_exc()
            print("--- Game.__init__: Mencoba reset data karena load_game gagal. ---")
            if hasattr(self, 'game_data_manager'):
                self.game_data_manager.reset_game_data()
            else:
                print("--- Game.__init__: FATAL - game_data_manager tidak ada. Tidak bisa reset.")


        # 6. Inisialisasi Font Debug (bisa dipindah lebih awal jika perlu, tapi setelah config)
        try:
            font_name_to_load = self.config.FONT_NAME
            actual_font_path = None
            if font_name_to_load and font_name_to_load.strip().lower() != 'none':
                if os.path.isabs(font_name_to_load) and os.path.exists(font_name_to_load):
                    actual_font_path = font_name_to_load
                else: 
                    potential_path = os.path.join(self.config.FONT_PATH, font_name_to_load)
                    if os.path.exists(potential_path): actual_font_path = potential_path
            small_font_size = self.config.FONT_SIZES.get('small', 18)
            if actual_font_path: self.debug_font = pygame.font.Font(actual_font_path, small_font_size)
            elif font_name_to_load and font_name_to_load.strip().lower() != 'none': self.debug_font = pygame.font.SysFont(font_name_to_load, small_font_size)
            else: self.debug_font = pygame.font.SysFont("arial", 18)
        except Exception as e:
            print(f"--- Game: ERROR debug font: {e}. Menggunakan default pygame.font.Font(None, 24). ---")
            self.debug_font = pygame.font.Font(None, 24)

        # 7. Sisa inisialisasi komponen game
        self.desired_waterline_on_screen_y = 400
        self.water_top_y_world = 10 
        self.water_bottom_y_world = 30
        
        self.main_menu = MainMenu(self)
        self.shop_menu = ShopMenu(self)
        self.market_screen = MarketScreen(self)
        self.inventory_screen = InventoryScreen(self)
        
        self.all_sprites=pygame.sprite.Group() # Untuk LandExplorer
        self.blocks=pygame.sprite.Group()    # Untuk LandExplorer
        
        self.current_game_map=None # Akan diisi saat masuk state 'fishing'
        self.player=None # PlayerBoat, akan diisi saat masuk state 'fishing'
        self.fishing_system=None # Akan diisi saat masuk state 'fishing'
        
        self.fishing_camera=Camera(self.config.SCREEN_WIDTH,self.config.SCREEN_HEIGHT,self.config.SCREEN_WIDTH,self.config.SCREEN_HEIGHT) 
        self.visible_fish_sprites=pygame.sprite.Group()
        
        self.ui=UI(self)
        
        # Update menu setelah semua data game (termasuk yang di-load) siap
        self.main_menu.update_options()
        self.shop_menu.update_options()
        self.market_screen.update_options()
        self.inventory_screen.update_options()
        
        print(f"--- Game: Game.__init__() selesai. Wallet akhir init: {self.wallet}, State awal: {self.current_state_name} ---")

    def _play_music(self, filename):
        """Metode terpusat untuk memutar, menghentikan, dan mengubah musik."""
        # Jika tidak ada nama file, hentikan musik yang sedang diputar.
        if not filename:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.fadeout(500) # Fade out halus
            self.current_music_file = None
            return

        # Jangan restart jika musik yang benar sudah diputar
        if self.current_music_file == filename and pygame.mixer.music.get_busy():
            return
        
        # Jika musik berbeda atau tidak ada yang diputar, muat dan mainkan yang baru.
        self.current_music_file = filename
        full_path = os.path.join(self.config.SOUND_PATH, filename)

        if os.path.exists(full_path):
            try:
                pygame.mixer.music.load(full_path)
                pygame.mixer.music.play(-1, fade_ms=500) # -1 untuk loop, fade_ms untuk fade in
                print(f"--- Game Music: Memutar '{filename}' ---")
            except pygame.error as e:
                print(f"--- Game Music ERROR: Tidak dapat memutar musik '{full_path}': {e} ---")
                self.current_music_file = None
        else:
            print(f"--- Game Music WARNING: File musik tidak ditemukan: '{full_path}' ---")
            self.current_music_file = None

    def run(self):
        print("--- Game: Memulai Game.run()... ---")
        print(f"--- Game: Memasuki game loop utama. State awal dari __init__: {self.current_state_name} ---")
        
        initial_game_state_to_run = self.current_state_name if self.current_state_name else 'main_menu'
        self.change_state(initial_game_state_to_run, initial_setup=True)

        while self.running:
            dt = self.clock.tick(self.config.FPS)/1000.0
            dt=min(dt,0.1) 
            self.current_fps = self.clock.get_fps()

            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    self.running = False
                    if hasattr(self, 'game_data_manager'): self.game_data_manager.save_game() 
                if self.running: self.handle_state_specific_event(event)
            
            if not self.running: break
            try: self.update_current_state(dt)
            except Exception as e: 
                print(f"--- ERROR DALAM UPDATE ({self.current_state_name}): {e} ---"); traceback.print_exc(); self.running=False
            if not self.running: break
            try: self.render_current_state()
            except Exception as e: 
                print(f"--- ERROR DALAM RENDER ({self.current_state_name}): {e} ---"); traceback.print_exc(); self.running=False
                
        print("--- Game: Keluar dari game loop utama. ---")
        self.quit_game()

    def handle_state_specific_event(self, event):
        active_handler=None; handled=False
        if self.current_state_name == 'fishing':
            if self.fishing_system and self.fishing_system.handle_event(event): handled=True 
            if not handled and event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE: self.change_state('map_explore'); handled=True
        if handled: return
        handlers = {'main_menu':self.main_menu, 'shop':self.shop_menu, 'market_screen':self.market_screen,
                    'inventory_screen':self.inventory_screen, 'land_explore':self.land_explorer,'map_explore':self.map_explorer}
        active_handler = handlers.get(self.current_state_name)
        if active_handler and hasattr(active_handler,'handle_event') and active_handler.handle_event(event): return

    def render_current_state(self):
        deep_sea_fill_color = self.config.COLORS.get('deep_ocean_blue', (20, 25, 60)); self.screen.fill(deep_sea_fill_color)
        active_renderer = None
        if self.current_state_name == 'main_menu': active_renderer = self.main_menu
        elif self.current_state_name == 'shop': active_renderer = self.shop_menu
        elif self.current_state_name == 'market_screen': active_renderer = self.market_screen
        elif self.current_state_name == 'inventory_screen': active_renderer = self.inventory_screen
        if active_renderer and hasattr(active_renderer, 'render'): active_renderer.render(self.screen)
        elif self.current_state_name == 'land_explore': 
            if self.land_explorer: self.land_explorer.render(self.screen) 
        elif self.current_state_name == 'map_explore': 
            if self.map_explorer: self.map_explorer.render(self.screen) 
        elif self.current_state_name == 'fishing':
            if self.current_game_map and self.current_game_map.background_image and self.fishing_camera: 
                bg_img = self.current_game_map.background_image; bg_img_width = bg_img.get_width(); bg_img_height = bg_img.get_height()
                if bg_img_width > 0 and self.boat and self.boat.rect: 
                    waterline_world_y = self.boat.rect.bottom; horizon_offset_in_bg_image = bg_img_height * 0.78 
                    background_top_world_y = waterline_world_y - horizon_offset_in_bg_image
                    camera_world_left_x = self.fishing_camera.camera_rect.left 
                    start_tile_index = int(camera_world_left_x // bg_img_width) -1
                    tiles_on_screen_approx = int(self.config.SCREEN_WIDTH // bg_img_width) + 3 
                    for i in range(start_tile_index, start_tile_index + tiles_on_screen_approx):
                        tile_world_x = self.fishing_world_rect.left + (i * bg_img_width)
                        tile_bg_world_rect = pygame.Rect(tile_world_x, background_top_world_y, bg_img_width, bg_img_height)
                        screen_pos = self.fishing_camera.apply(tile_bg_world_rect).topleft 
                        self.screen.blit(bg_img, screen_pos)
            if self.fishing_camera: 
                for fish_sprite in self.visible_fish_sprites:
                    if fish_sprite.image and fish_sprite.rect: 
                        img_to_render = pygame.transform.flip(fish_sprite.image, fish_sprite.swim_direction > 0, False) 
                        self.screen.blit(img_to_render, self.fishing_camera.apply(fish_sprite.rect)) 
            if self.boat and hasattr(self.boat, 'render_with_camera') and self.fishing_camera: self.boat.render_with_camera(self.screen, self.fishing_camera) 
            if self.player and hasattr(self.player, 'render_with_camera') and self.fishing_camera: self.player.render_with_camera(self.screen, self.fishing_camera) 
            if self.fishing_system and hasattr(self.fishing_system, 'render_with_camera') and self.fishing_camera: self.fishing_system.render_with_camera(self.screen, self.fishing_camera) 
        if self.ui and hasattr(self.ui, 'render') and self.current_state_name in ['land_explore', 'map_explore', 'fishing']: self.ui.render(self.screen) 
        
        if self.config.DEBUG and hasattr(self, 'debug_font'): 
            debug_start_y = self.config.SCREEN_HEIGHT - (self.debug_font.get_height() + 3) * 7 
            texts = [f"FPS: {int(self.current_fps)}", f"State: {self.current_state_name}"]
            if self.current_state_name == 'fishing' and self.fishing_camera and self.fishing_system and self.boat and self.boat.rect: 
                texts.append(f"CamOff(X:{int(self.fishing_camera.offset_x)},Y:{int(self.fishing_camera.offset_y)})") 
                boat_bottom_screen_y = self.boat.rect.bottom + self.fishing_camera.offset_y 
                texts.append(f"Boat Btm(W):{self.boat.rect.bottom:.0f} | BtmLayarPx:{boat_bottom_screen_y:.0f} (TrgtScrPx:{self.desired_waterline_on_screen_y:.0f})") 
                if self.fishing_system: _, hook_y_w = self.fishing_system._get_hook_tip_world_position(); texts.append(f"HookY(W):{hook_y_w:.0f} Dpt:{self.fishing_system.hook_depth:.0f}") 
                texts.append(f"WaterY(W):{self.water_top_y_world:.0f}-{self.water_bottom_y_world:.0f}")
                texts.append(f"Boat Speed: {self.boat.current_speed_value}, Line: {self.boat.current_line_length_value}, Cap: {self.boat.current_capacity_value}")
            for i, text in enumerate(texts): self.screen.blit(self.debug_font.render(text, True, self.config.COLORS.get('white')), (10, debug_start_y + i * (self.debug_font.get_height() + 3))) 
            if self.current_state_name == 'fishing' and self.fishing_system: 
                active_fish_info = f"Hooked: {'Yes' if self.fishing_system.hooked_fish_sprite else 'No'}" 
                afs = self.debug_font.render(active_fish_info, True, self.config.COLORS.get('white')); self.screen.blit(afs, (self.config.SCREEN_WIDTH - afs.get_width() - 10, 10)) 
        pygame.display.flip()

    def quit_game(self):
        print("--- Game: Menyimpan game sebelum keluar... ---")
        if hasattr(self, 'game_data_manager'): self.game_data_manager.save_game() 
        pygame.quit(); sys.exit()
    
    def change_state(self, new_state_name, data=None, initial_setup=False):
        should_save = not initial_setup
        if self.current_state_name == new_state_name and not initial_setup and new_state_name == 'main_menu':
             should_save = True # Simpan jika kembali ke main_menu setelah aksi (misal, reset)

        print(f"--- Game: State: {self.current_state_name} -> {new_state_name} (InitialSetup: {initial_setup}, ShouldSave: {should_save}) ---")
        
        current_wallet_before_save = self.wallet if hasattr(self, 'wallet') else 'N/A (wallet belum ada)'
        print(f"--- DEBUG Game.change_state: Wallet SEBELUM save: {current_wallet_before_save} ---")

        if should_save and hasattr(self, 'game_data_manager'):
             print(f"--- Game: Menyimpan game karena perubahan state dari {self.current_state_name} ke {new_state_name} ---")
             self.game_data_manager.save_game() # save_game akan print nilai koin yang disimpan
        
        self.all_sprites.empty(); self.blocks.empty()
        
        self.current_state_name = new_state_name
        
        current_wallet_after_save = self.wallet if hasattr(self, 'wallet') else 'N/A (wallet belum ada)'
        print(f"--- DEBUG Game.change_state: Wallet SETELAH save & state name diubah: {current_wallet_after_save} ---")

        if new_state_name == 'main_menu':
            for menu_attr in ['main_menu', 'shop_menu', 'market_screen', 'inventory_screen']:
                if hasattr(self, menu_attr) and getattr(self, menu_attr): getattr(self, menu_attr).update_options()
        elif new_state_name == 'land_explore':
            if self.land_explorer: self.land_explorer.setup_scene()
        elif new_state_name == 'map_explore':
            if self.map_explorer and hasattr(self.map_explorer,'setup_scene'): pass 
        elif new_state_name == 'fishing':
            if data and 'location_name' in data:
                location_name = data['location_name']
                try:
                    self.current_game_map = GameMap(location_name, self.config) 
                    fishing_world_width = int(self.config.SCREEN_WIDTH*1.2); fishing_world_height = int(self.config.SCREEN_HEIGHT*2.0) 
                    self.fishing_world_rect.size = (fishing_world_width, fishing_world_height)
                    self.fishing_camera.world_width = fishing_world_width; self.fishing_camera.world_height = fishing_world_height
                    target_boat_bottom_y_world = self.desired_waterline_on_screen_y; initial_boat_world_x = self.fishing_world_rect.centerx
                    if not self.boat: self.boat = Boat(self.current_game_map, self.config, self.fishing_world_rect) 
                    else: self.boat.change_map(self.current_game_map, self.fishing_world_rect)
                    if self.boat.rect: self.boat.rect.centerx = initial_boat_world_x; self.boat.rect.bottom = target_boat_bottom_y_world 
                    self.water_top_y_world = self.boat.rect.bottom + 1 
                    self.water_bottom_y_world = min(self.boat.rect.bottom + (self.config.SCREEN_HEIGHT*0.7), fishing_world_height - 20)
                    if self.water_top_y_world >= self.water_bottom_y_world: self.water_bottom_y_world = min(self.water_top_y_world + self.config.SCREEN_HEIGHT//3, fishing_world_height - 20)
                    if not self.player: self.player = PlayerBoat(self.boat, self) 
                    else: self.player.boat = self.boat
                    if self.player: self.player.update_position()
                    if self.boat and self.boat.rect: 
                         target_focus_y_world = self.boat.rect.bottom - (self.desired_waterline_on_screen_y-(self.config.SCREEN_HEIGHT/2))                        
                         initial_focus_rect = pygame.Rect(0,0,1,1); initial_focus_rect.center = (self.boat.rect.centerx, target_focus_y_world) 
                         self.fishing_camera.update(initial_focus_rect)
                    self.fishing_system = FishingSystem(self); self.visible_fish_sprites.empty(); self.spawn_visible_fish(amount=random.randint(8,12))
                except Exception as e: print(f"--- Game: ERROR setup fishing state: {e} ---"); traceback.print_exc(); self.change_state('map_explore')
            else: print("--- Game: PERINGATAN - Pindah ke 'fishing' tanpa data lokasi."); self.change_state('map_explore')
        elif new_state_name == 'shop': 
            if self.shop_menu: self.shop_menu.update_options() 
        elif new_state_name == 'market_screen': 
            if self.market_screen: self.market_screen.update_options() 
        elif new_state_name == 'inventory_screen': 
            if self.inventory_screen: self.inventory_screen.update_options() 
        if self.ui: self.ui.update_display_info()
        
        # --- LOGIKA MUSIK BARU ---
        target_music_file = None
        if new_state_name == 'land_explore':
            target_music_file = 'Land.ogg'
        elif new_state_name in ['main_menu', 'map_explore']: # <-- PERUBAHAN DI SINI
            target_music_file = 'Wave.ogg' # <-- PERUBAHAN DI SINI
        elif new_state_name == 'fishing':
            if self.current_game_map and self.current_game_map.data:
                target_music_file = self.current_game_map.data.get('music')
        
        # Panggil metode pemutar musik terpusat.
        # Ini akan menangani penghentian, perubahan, dan pemutaran musik.
        self._play_music(target_music_file)
        # --- AKHIR LOGIKA MUSIK BARU ---


    def spawn_visible_fish(self, amount=5):
        if not self.current_game_map or not self.fishing_camera or self.current_state_name!='fishing': return 
        if not hasattr(self,'water_top_y_world') or not hasattr(self,'water_bottom_y_world') or self.water_top_y_world>=self.water_bottom_y_world: return 
        try: from fish import Fish
        except ImportError: print("--- Game.spawn_visible_fish: ERROR - Gagal impor Fish."); return
        spawn_count = 0
        for _ in range(amount): 
            fish_data = self.current_game_map.get_random_fish_data() 
            if fish_data: 
                world_left = self.fishing_world_rect.left + 50; world_right = self.fishing_world_rect.right - 50
                if world_left >= world_right: continue
                spawn_x = random.randint(int(world_left), int(world_right)) 
                spawn_y = random.randint(int(self.water_top_y_world), int(self.water_bottom_y_world)) 
                new_fish_sprite = Fish(fish_data, (spawn_x, spawn_y), self.config)
                if new_fish_sprite.image: self.visible_fish_sprites.add(new_fish_sprite); spawn_count +=1
    
    def update_current_state(self, dt):
        if self.current_state_name == 'land_explore': 
            if self.land_explorer: self.land_explorer.update(dt) 
            if self.land_player: self.land_player.update()
        elif self.current_state_name == 'map_explore': 
            if self.map_explorer: self.map_explorer.update(dt) 
        elif self.current_state_name == 'fishing':
            if self.boat: self.boat.update(dt, pygame.key.get_pressed()) 
            if self.player: self.player.update(dt) 
            for fish_sprite in list(self.visible_fish_sprites): fish_sprite.update(dt) 
            if self.fishing_world_rect: 
                for fish_sprite in list(self.visible_fish_sprites):
                    fish_sprite.rect.left=max(self.fishing_world_rect.left,fish_sprite.rect.left)
                    fish_sprite.rect.right=min(self.fishing_world_rect.right,fish_sprite.rect.right)
                    if (fish_sprite.rect.left==self.fishing_world_rect.left and fish_sprite.swim_direction<0) or \
                       (fish_sprite.rect.right==self.fishing_world_rect.right and fish_sprite.swim_direction>0):
                        fish_sprite.swim_direction *= -1
                    fish_sprite.pos[0]=fish_sprite.rect.centerx
                    if hasattr(self,'water_top_y_world') and hasattr(self,'water_bottom_y_world'):
                        fish_sprite.rect.top=max(self.water_top_y_world,fish_sprite.rect.top)
                        fish_sprite.rect.bottom=min(self.water_bottom_y_world,fish_sprite.rect.bottom)
                        fish_sprite.pos[1]=fish_sprite.rect.centery
            if self.fishing_system: self.fishing_system.update(dt) 
            if self.boat and self.boat.rect and self.fishing_camera and self.fishing_system: 
                hook_world_x, hook_tip_world_y = self.fishing_system._get_hook_tip_world_position() 
                camera_target_x = self.boat.rect.centerx 
                is_fishing_action = any([self.fishing_system.is_casting, self.fishing_system.is_reeling, 
                                         self.fishing_system.fish_on_line_awaiting_pull, self.fishing_system.hook_depth > 10]) 
                if is_fishing_action: camera_target_y = hook_tip_world_y 
                else: camera_target_y = self.boat.rect.bottom-(self.desired_waterline_on_screen_y-(self.config.SCREEN_HEIGHT/2)) 
                focus_rect = pygame.Rect(0,0,1,1); focus_rect.center = (camera_target_x, camera_target_y)
                self.fishing_camera.update(focus_rect)
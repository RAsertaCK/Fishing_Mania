# TES/game.py
import pygame
import sys
import os
import random
import traceback

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
from land_explorer import LandExplorer
from sprites import Player as LandPlayer, Spritesheet
from game_data import GameData # <--- TAMBAHKAN INI

class Game:
    def __init__(self, screen):
        print("--- Game: Memulai Game.__init__()... ---")
        self.screen = screen
        self.config = Config()
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_fps = 0

        # Inisialisasi GameData SEBELUM komponen lain yang bergantung pada data load.
        self.game_data_manager = GameData(self) #

        try:
            font_name_to_load = self.config.FONT_NAME
            actual_font_path = None
            if font_name_to_load and font_name_to_load.strip().lower() != 'none':
                if os.path.isabs(font_name_to_load) and os.path.exists(font_name_to_load):
                    actual_font_path = font_name_to_load
                else: 
                    potential_path = os.path.join(self.config.FONT_PATH, font_name_to_load)
                    if os.path.exists(potential_path):
                        actual_font_path = potential_path
            small_font_size = self.config.FONT_SIZES.get('small', 18)
            if actual_font_path: self.debug_font = pygame.font.Font(actual_font_path, small_font_size)
            elif font_name_to_load and font_name_to_load.strip().lower() != 'none': self.debug_font = pygame.font.SysFont(font_name_to_load, small_font_size)
            else: self.debug_font = pygame.font.SysFont("arial", small_font_size)
        except Exception as e:
            print(f"--- Game: ERROR debug font: {e}. ---"); self.debug_font = pygame.font.Font(None, 24)

        # Muat data game dari GameData manager
        self.game_data_manager.load_game() #

        # Inisialisasi properti game dengan data yang dimuat atau default dari GameData
        self.wallet = self.game_data_manager.data["coins"] #
        self.current_state_name = self.game_data_manager.data["current_game_state"] #

        self.inventory = Inventory(self)
        self.market = Market(self)
        class InitialDummyMap:
            def __init__(self): self.name = "initial"; self.data = {'depth_range': (10,100)}; self.background_image = pygame.Surface((Config.SCREEN_WIDTH,Config.SCREEN_HEIGHT)); self.background_image.fill((0,0,50)) #
        self.fishing_world_rect = pygame.Rect(0,0,self.config.SCREEN_WIDTH,self.config.SCREEN_HEIGHT) #
        
        # ---- TARGET POSISI GARIS AIR DI LAYAR (Y dari atas layar) ----
        self.desired_waterline_on_screen_y = 432
        self.water_top_y_world = 0
        self.water_bottom_y_world = 0
        
        self.boat = Boat(InitialDummyMap(), self.config, self.fishing_world_rect) #
        # Terapkan upgrade yang dimuat ke kapal setelah inisialisasi boat
        self.boat.upgrades = self.game_data_manager.data["boat_upgrades"] #
        self.boat.current_speed_value = self.boat.UPGRADE_LEVELS["speed"][self.boat.upgrades["speed"]] #
        self.boat.current_capacity_value = self.boat.UPGRADE_LEVELS["capacity"][self.boat.upgrades["capacity"]] #
        self.boat.current_line_length_value = self.boat.UPGRADE_LEVELS["line_length"][self.boat.upgrades["line_length"]] #


        self.main_menu=MainMenu(self); self.settings_menu=SettingsMenu(self); self.shop_menu=ShopMenu(self)
        self.market_screen=MarketScreen(self); self.inventory_screen=InventoryScreen(self)
        self.all_sprites=pygame.sprite.Group(); self.blocks=pygame.sprite.Group()
        try: self.character_spritesheet=Spritesheet(self.config.PLAYER_SPRITESHEET_PATH) #
        except Exception as e: print(f"--- Game: ERROR spritesheet: {e}. ---"); self.character_spritesheet=None
        self.land_player=None
        if self.character_spritesheet: self.land_player=LandPlayer(self,5,5) #
        self.land_explorer=LandExplorer(self); self.map_explorer=MapExplorer(self)
        self.current_game_map=None; self.player=None; self.fishing_system=None
        self.fishing_camera=Camera(self.config.SCREEN_WIDTH,self.config.SCREEN_HEIGHT,self.config.SCREEN_WIDTH,self.config.SCREEN_HEIGHT) #
        self.visible_fish_sprites=pygame.sprite.Group()
        self.ui=UI(self); print("--- Game: Game.__init__() selesai. ---")

        # ---- Menggunakan data yang dimuat untuk unlocked_locations ----
        self.unlocked_locations = self.game_data_manager.data["unlocked_locations"] #

        # Panggil load data inventory setelah inventory diinisialisasi
        if self.game_data_manager.data["collected_fish"]: #
            from fish import Fish # Impor di sini untuk menghindari circular dependency
            for fish_dict in self.game_data_manager.data["collected_fish"]: #
                self.inventory.add_fish_from_data(fish_dict) #
            print(f"--- Game: Inventaris dimuat dengan {len(self.inventory.fish_list)} ikan. ---") #
        
        # Panggil update_options untuk menu yang relevan setelah data dimuat
        self.shop_menu.update_options()
        self.market_screen.update_options()
        self.inventory_screen.update_options()

        # Atur posisi awal kapal di map explorer setelah data dimuat
        if self.map_explorer and hasattr(self.map_explorer, 'player_map_rect'):
            player_map_pos = self.game_data_manager.data["player_map_position"]
            self.map_explorer.player_map_rect.centerx = player_map_pos["x"]
            self.map_explorer.player_map_rect.centery = player_map_pos["y"]
            print(f"--- Game: Posisi map_explorer dimuat: {self.map_explorer.player_map_rect.center} ---")
        
        # Jika game dimulai dari state selain main_menu, pastikan setup scene dilakukan
        if self.current_state_name != 'main_menu': #
            # HACK: change_state perlu dipanggil setelah semua inisialisasi
            # Karena change_state memanggil setup_scene dan memuat ulang objek
            # yang mungkin memerlukan semua dependensi (boat, map_explorer, dll)
            # yang sudah terinisialisasi dan terisi data dari game_data_manager.
            # Namun, memanggilnya di sini bisa menyebabkan masalah re-initialization.
            # Solusi yang lebih baik adalah memindahkan logika setup_scene ke dalam __init__
            # untuk setiap kelas state, atau memastikan change_state cukup cerdas.
            # Untuk demo ini, kita akan biarkan seperti ini dan asumsikan game dimulai dari menu utama
            # atau secara manual mengarahkan ke state yang dimuat setelah menu utama.
            pass


    def change_state(self, new_state_name, data=None):
        print(f"--- Game: State: {self.current_state_name} -> {new_state_name} ---")
        # Simpan game setiap kali state berubah (atau saat keluar)
        self.game_data_manager.save_game() #

        self.all_sprites.empty(); self.blocks.empty()
        if self.current_state_name not in ['main_menu','settings','shop','market_screen','inventory_screen'] and \
           new_state_name in ['main_menu','settings','shop','market_screen','inventory_screen']:
             if pygame.mixer.music.get_busy(): pygame.mixer.music.fadeout(500)
        self.current_state_name = new_state_name

        if new_state_name == 'land_explore':
            if self.land_explorer: self.land_explorer.setup_scene()
        elif new_state_name == 'map_explore':
            if self.map_explorer and hasattr(self.map_explorer,'setup_scene'): self.map_explorer.setup_scene()
        elif new_state_name == 'fishing':
            if data and 'location_name' in data:
                location_name = data['location_name']
                try:
                    self.current_game_map = GameMap(location_name, self.config) #
                    if hasattr(self.current_game_map,'play_music'): self.current_game_map.play_music() #
                    
                    fishing_world_width = int(self.config.SCREEN_WIDTH * 1.2) #
                    fishing_world_height = int(self.config.SCREEN_HEIGHT * 2.0) #
                    
                    self.fishing_world_rect.size = (fishing_world_width, fishing_world_height)
                    self.fishing_camera.world_width = fishing_world_width
                    self.fishing_camera.world_height = fishing_world_height
                    
                    # Y DUNIA untuk bagian BAWAH kapal akan sama dengan Y LAYAR yang diinginkan untuk garis air.
                    target_boat_bottom_y_world = self.desired_waterline_on_screen_y

                    initial_boat_world_x = self.fishing_world_rect.centerx
                    
                    if not self.boat: self.boat = Boat(self.current_game_map, self.config, self.fishing_world_rect) #
                    else: self.boat.change_map(self.current_game_map, self.fishing_world_rect)

                    if self.boat.rect: #
                         self.boat.rect.centerx = initial_boat_world_x #
                         self.boat.rect.bottom = target_boat_bottom_y_world #
                         print(f"--- Game (cs): Kapal (W) X:{self.boat.rect.centerx:.0f}, BtmY:{self.boat.rect.bottom:.0f} (Target Garis Air Layar: {self.desired_waterline_on_screen_y:.0f}) ---") #
                    
                    self.water_top_y_world = self.boat.rect.bottom + 1 # Ikan mulai tepat di bawah garis air
                    self.water_bottom_y_world = self.boat.rect.bottom + (self.config.SCREEN_HEIGHT * 0.7) # Area renang ikan lebih dangkal
                    self.water_bottom_y_world = min(self.water_bottom_y_world, fishing_world_height - 20)
                    if self.water_top_y_world >= self.water_bottom_y_world: # Validasi
                        self.water_bottom_y_world = self.water_top_y_world + self.config.SCREEN_HEIGHT // 3; #
                        self.water_bottom_y_world = min(self.water_bottom_y_world, fishing_world_height - 20)

                    print(f"--- Game: FW: {self.fishing_world_rect.size}. FishSwimY(W): {self.water_top_y_world:.0f}-{self.water_bottom_y_world:.0f} ---")
                    
                    if not self.player: self.player = PlayerBoat(self.boat, self) #
                    else: self.player.boat = self.boat
                    if self.player: self.player.update_position()
                    
                    if self.boat and self.boat.rect: #
                         # Target Y kamera agar self.boat.rect.bottom (Y dunia) muncul di self.desired_waterline_on_screen_y
                         target_focus_y_world = self.boat.rect.bottom - (self.desired_waterline_on_screen_y - (self.config.SCREEN_HEIGHT / 2)) #
                                                  
                         initial_focus_rect = pygame.Rect(0,0,1,1)
                         initial_focus_rect.center = (self.boat.rect.centerx, target_focus_y_world) #
                         self.fishing_camera.update(initial_focus_rect)
                         print(f"--- Game (cs): Cam init. FokusY(W):{target_focus_y_world:.0f} (agar btm kapal di layar ~{self.desired_waterline_on_screen_y:.0f}), OffsetY:{self.fishing_camera.offset_y:.0f}")

                    self.fishing_system = FishingSystem(self) #
                    self.visible_fish_sprites.empty()
                    self.spawn_visible_fish(amount=random.randint(8, 12))
                    print(f"--- Game: Setup state fishing '{location_name}' selesai.")
                except Exception as e: print(f"--- Game: ERROR setup fishing: {e} ---"); traceback.print_exc(); self.change_state('map_explore')
            else: self.change_state('map_explore')
        
        elif new_state_name == 'shop': #
            if self.shop_menu: self.shop_menu.update_options() #
        elif new_state_name == 'market_screen': #
            if self.market_screen: self.market_screen.update_options() #
        elif new_state_name == 'inventory_screen': #
            if self.inventory_screen: self.inventory_screen.update_options() #
            
        # Perbarui tampilan UI jika berubah ke state menu
        self.ui.update_display_info() #
        
    def spawn_visible_fish(self, amount=5):
        # ... (Sama seperti sebelumnya) ...
        if not self.current_game_map or not self.fishing_camera: return 
        if not hasattr(self, 'water_top_y_world') or not hasattr(self, 'water_bottom_y_world') or \
           self.water_top_y_world >= self.water_bottom_y_world: return 
        from fish import Fish 
        for _ in range(amount): 
            fish_data = self.current_game_map.get_random_fish_data() 
            if fish_data: 
                spawn_x = random.randint(self.fishing_world_rect.left + 20, self.fishing_world_rect.right - 20) 
                spawn_y = random.randint(int(self.water_top_y_world), int(self.water_bottom_y_world)) 
                self.visible_fish_sprites.add(Fish(fish_data, (spawn_x, spawn_y), self.config)) 

    def play_music_file(self, music_path, loop=-1):
        # ... (Sama seperti sebelumnya) ...
        if os.path.exists(music_path):
            try: pygame.mixer.music.load(music_path); pygame.mixer.music.play(loop, fade_ms=1000)
            except pygame.error as e: print(f"--- Game: Error musik {music_path}: {e} ---")


    def run(self):
        # ... (Sama seperti sebelumnya) ...
        print("--- Game: Memulai Game.run()... ---"); print("--- Game: Memasuki game loop utama. ---")
        # Panggil change_state awal untuk mengatur scene yang dimuat
        self.change_state(self.current_state_name) #

        while self.running:
            dt = self.clock.tick(self.config.FPS)/1000.0; dt=min(dt,0.1) #
            self.current_fps = self.clock.get_fps()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    self.running = False
                    self.game_data_manager.save_game() # # Simpan saat game ditutup
                if self.running: self.handle_state_specific_event(event)
            if not self.running: break
            try: self.update_current_state(dt)
            except Exception as e: print(f"--- ERR UPDATE({self.current_state_name}): {e} ---"); traceback.print_exc(); self.running=False
            if not self.running: break
            try: self.render_current_state()
            except Exception as e: print(f"--- ERR RENDER({self.current_state_name}): {e} ---"); traceback.print_exc(); self.running=False
        print("--- Game: Keluar dari game loop utama. ---"); self.quit_game()


    def handle_state_specific_event(self, event):
        # ... (Sama seperti sebelumnya) ...
        active_handler=None; handled=False
        if self.current_state_name == 'fishing':
            if self.fishing_system and self.fishing_system.handle_event(event): handled=True #
            if not handled and event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE: self.change_state('map_explore'); handled=True
        if handled: return
        handlers = {'main_menu':self.main_menu,'settings':self.settings_menu,'shop':self.shop_menu,
                    'market_screen':self.market_screen,'inventory_screen':self.inventory_screen,
                    'land_explore':self.land_explorer,'map_explore':self.map_explorer}
        active_handler = handlers.get(self.current_state_name)
        if active_handler and hasattr(active_handler,'handle_event'): active_handler.handle_event(event)

    def update_current_state(self, dt):
        if self.current_state_name == 'land_explore': #
            if self.land_explorer: self.land_explorer.update(dt) #
            if self.land_player: self.land_player.update() #
        elif self.current_state_name == 'map_explore': #
            if self.map_explorer: self.map_explorer.update(dt) #
        elif self.current_state_name == 'fishing':
            if self.boat: self.boat.update(dt, pygame.key.get_pressed()) #
            if self.player: self.player.update(dt) #
            for fish_sprite in self.visible_fish_sprites: fish_sprite.update(dt) #
            if self.fishing_world_rect: # Batas ikan
                for fish_sprite in self.visible_fish_sprites:
                    fish_sprite.rect.left=max(self.fishing_world_rect.left, fish_sprite.rect.left)
                    fish_sprite.rect.right=min(self.fishing_world_rect.right, fish_sprite.rect.right)
                    if fish_sprite.rect.left==self.fishing_world_rect.left and fish_sprite.swim_direction<0: fish_sprite.swim_direction*=-1
                    elif fish_sprite.rect.right==self.fishing_world_rect.right and fish_sprite.swim_direction>0: fish_sprite.swim_direction*=-1
                    fish_sprite.pos[0]=fish_sprite.rect.centerx
                    if hasattr(self,'water_top_y_world') and hasattr(self,'water_bottom_y_world'):
                        fish_sprite.rect.top=max(self.water_top_y_world,fish_sprite.rect.top)
                        fish_sprite.rect.bottom=min(self.water_bottom_y_world,fish_sprite.rect.bottom)
                        fish_sprite.pos[1]=fish_sprite.rect.centery
            if self.fishing_system: self.fishing_system.update(dt) #
            
            if self.boat and self.boat.rect and self.fishing_camera and self.fishing_system: #
                hook_world_x, hook_tip_world_y = self.fishing_system._get_hook_tip_world_position() #
                camera_target_x = self.boat.rect.centerx #
                
                is_fishing_action = any([self.fishing_system.is_casting, self.fishing_system.is_reeling, #
                                         self.fishing_system.fish_on_line_awaiting_pull, self.fishing_system.hook_depth > 10]) #
                
                if is_fishing_action:
                    camera_target_y = hook_tip_world_y # Fokus pada kail saat memancing
                else:
                    # Saat idle, pertahankan agar BAWAH kapal muncul di self.desired_waterline_on_screen_y
                    camera_target_y = self.boat.rect.bottom - (self.desired_waterline_on_screen_y - (self.config.SCREEN_HEIGHT / 2)) #
                
                focus_rect = pygame.Rect(0,0,1,1); focus_rect.center = (camera_target_x, camera_target_y)
                self.fishing_camera.update(focus_rect) #

    def render_current_state(self):
        deep_sea_fill_color = self.config.COLORS.get('deep_ocean_blue', (20, 25, 60)) #
        self.screen.fill(deep_sea_fill_color)

        active_renderer = None
        if self.current_state_name == 'main_menu': active_renderer = self.main_menu
        # ... (dst)
        elif self.current_state_name == 'settings': active_renderer = self.settings_menu
        elif self.current_state_name == 'shop': active_renderer = self.shop_menu
        elif self.current_state_name == 'market_screen': active_renderer = self.market_screen
        elif self.current_state_name == 'inventory_screen': active_renderer = self.inventory_screen

        if active_renderer and hasattr(active_renderer, 'render'):
            active_renderer.render(self.screen)
        
        elif self.current_state_name == 'land_explore': #
            if self.land_explorer: self.land_explorer.render(self.screen) #
        elif self.current_state_name == 'map_explore': #
            if self.map_explorer: self.map_explorer.render(self.screen) #
        elif self.current_state_name == 'fishing':
            if self.current_game_map and self.current_game_map.background_image and self.fishing_camera: #
                bg_img = self.current_game_map.background_image #
                bg_img_width = bg_img.get_width()
                bg_img_height = bg_img.get_height()

                if bg_img_width > 0 and self.boat and self.boat.rect: #
                    # ---- PENEMPATAN BACKGROUND LANGIT/CAKRAWALA ----
                    # Y dunia untuk garis air (di mana bawah kapal berada) adalah self.boat.rect.bottom
                    waterline_world_y = self.boat.rect.bottom #
                    
                    # Tempatkan bagian ATAS gambar background (langit) agar bagian BAWAHNYA (misal, cakrawala di gambar)
                    # berada sedikit DI ATAS atau SEJAJAR dengan waterline_world_y kapal.
                    # Asumsi cakrawala di gambar background Anda ada di sekitar 70-80% dari ATAS gambar background itu sendiri.
                    horizon_offset_in_bg_image = bg_img_height * 0.78 # Misal, cakrawala di 78% tinggi gambar BG. SESUAIKAN INI!
                    
                    background_top_world_y = waterline_world_y - horizon_offset_in_bg_image
                    
                    camera_world_left_x = self.fishing_camera.camera_rect.left #
                    start_tile_index = int(camera_world_left_x // bg_img_width) -1
                    tiles_on_screen_approx = int(self.config.SCREEN_WIDTH // bg_img_width) + 3 #

                    for i in range(start_tile_index, start_tile_index + tiles_on_screen_approx):
                        tile_world_x = self.fishing_world_rect.left + (i * bg_img_width)
                        tile_bg_world_rect = pygame.Rect(tile_world_x, background_top_world_y, bg_img_width, bg_img_height)
                        screen_pos = self.fishing_camera.apply(tile_bg_world_rect).topleft #
                        self.screen.blit(bg_img, screen_pos)
            
            # ... (Render ikan, kapal, player, fishing_system sama seperti sebelumnya) ...
            if self.fishing_camera: #
                for fish_sprite in self.visible_fish_sprites:
                    if fish_sprite.image and fish_sprite.rect:
                        # PERBAIKAN MOONWALK: Asumsi sprite ikan asli menghadap KIRI.
                        # Jika sprite asli menghadap KANAN, ubah 'fish_sprite.swim_direction > 0' menjadi 'fish_sprite.swim_direction < 0'
                        img_to_render = pygame.transform.flip(fish_sprite.image, fish_sprite.swim_direction > 0, False) #
                        self.screen.blit(img_to_render, self.fishing_camera.apply(fish_sprite.rect)) #
            if self.boat and hasattr(self.boat, 'render_with_camera') and self.fishing_camera: #
                 self.boat.render_with_camera(self.screen, self.fishing_camera) #
            if self.player and hasattr(self.player, 'render_with_camera') and self.fishing_camera: #
                 self.player.render_with_camera(self.screen, self.fishing_camera) #
            if self.fishing_system and hasattr(self.fishing_system, 'render_with_camera') and self.fishing_camera: #
                self.fishing_system.render_with_camera(self.screen, self.fishing_camera) #

        if self.ui and hasattr(self.ui, 'render') and \
           self.current_state_name in ['land_explore', 'map_explore', 'fishing']: #
            self.ui.render(self.screen) #

        if self.config.DEBUG: #
            debug_start_y = self.config.SCREEN_HEIGHT - (self.debug_font.get_height() + 3) * 6  #
            texts = [f"FPS: {int(self.current_fps)}", f"State: {self.current_state_name}"]
            if self.current_state_name == 'fishing' and self.fishing_camera and self.fishing_system and self.boat and self.boat.rect: #
                texts.append(f"CamOff(X:{int(self.fishing_camera.offset_x)},Y:{int(self.fishing_camera.offset_y)})") #
                boat_bottom_screen_y = self.boat.rect.bottom + self.fishing_camera.offset_y #
                boat_screen_y_percent = (boat_bottom_screen_y / self.config.SCREEN_HEIGHT) * 100 if self.config.SCREEN_HEIGHT > 0 else 0 #
                texts.append(f"Boat Btm(W):{self.boat.rect.bottom:.0f} | BtmLayarPx:{boat_bottom_screen_y:.0f} (TrgtScrPx:{self.desired_waterline_on_screen_y:.0f})") #
                _, hook_y_w = self.fishing_system._get_hook_tip_world_position(); texts.append(f"HookY(W):{hook_y_w:.0f} Dpt:{self.fishing_system.hook_depth:.0f}") #
                texts.append(f"WaterY(W):{self.water_top_y_world:.0f}-{self.water_bottom_y_world:.0f}")
            for i, text in enumerate(texts):
                self.screen.blit(self.debug_font.render(text, True, self.config.COLORS.get('white')), (10, debug_start_y + i * (self.debug_font.get_height() + 3))) #
            if self.current_state_name == 'fishing' and self.fishing_system: #
                active_fish_info = f"Hooked: {'Yes' if self.fishing_system.hooked_fish_sprite else 'No'}" #
                afs = self.debug_font.render(active_fish_info, True, self.config.COLORS.get('white')); self.screen.blit(afs, (self.config.SCREEN_WIDTH - afs.get_width() - 10, 10)) #

        pygame.display.flip()

    def quit_game(self):
        """Menyimpan game sebelum keluar."""
        print("--- Game: Menyimpan game sebelum keluar... ---")
        self.game_data_manager.save_game() #
        pygame.quit()
        sys.exit()
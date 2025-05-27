# IMPROVE/game.py
import pygame
import sys
import os

# Pastikan semua impor ini sesuai dengan nama file Anda di folder IMPROVE
from config import Config
from menu import MainMenu, SettingsMenu, ShopMenu, MarketScreen, InventoryScreen
from player import Player
from boat import Boat
from game_map import GameMap
from ui import UI
from inventory import Inventory
from market import Market
from map_explore import MapExplorer
from fishing_system import FishingSystem
from fishing_challenge import FishingSkillChallenge

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
            small_font_size = self.config.FONT_SIZES.get('small', 18)
            if font_name_to_load and os.path.exists(os.path.join(self.config.FONT_PATH, font_name_to_load)): # Cek di FONT_PATH
                self.debug_font = pygame.font.Font(os.path.join(self.config.FONT_PATH, font_name_to_load), small_font_size)
            elif font_name_to_load and font_name_to_load.lower() != 'none' and font_name_to_load != "":
                 self.debug_font = pygame.font.SysFont(font_name_to_load, small_font_size)
            else: # Fallback absolut jika FONT_NAME None atau path tidak valid
                self.debug_font = pygame.font.SysFont("arial", small_font_size)
            print("--- Game: Debug font berhasil dimuat/fallback. ---")
        except Exception as e:
            print(f"--- Game: ERROR saat memuat debug font: {e}. Menggunakan default absolut. ---")
            self.debug_font = pygame.font.Font(None, 24) # Font default pygame jika semua gagal

        self.current_state_name = 'main_menu' # State awal
        self.wallet = 100

        self.inventory = Inventory()
        self.market = Market(self) # Market butuh instance game

        # Inisialisasi Boat dengan dummy map dulu, akan diubah saat masuk state fishing
        class InitialDummyMap:
            def __init__(self): self.name = "initial_setup"
        self.boat = Boat(InitialDummyMap(), self.config)

        # Inisialisasi semua menu dan screen UI
        self.main_menu = MainMenu(self)
        self.settings_menu = SettingsMenu(self)
        self.shop_menu = ShopMenu(self)
        self.market_screen = MarketScreen(self)
        self.inventory_screen = InventoryScreen(self)
        
        self.map_explorer = None # Akan diinisialisasi saat state 'map_explore'

        # Komponen untuk state 'fishing', akan diinisialisasi saat state tersebut aktif
        self.current_game_map = None
        self.player = None
        self.fishing_system = None
        self.fishing_challenge = None # Akan menjadi instance FishingSkillChallenge

        self.ui = UI(self) # UI global
        print("--- Game: Game.__init__() selesai. ---")

    def change_state(self, new_state_name, data=None):
        print(f"--- Game: Mengubah state dari {self.current_state_name} ke {new_state_name} dengan data: {data} ---")
        
        # Hentikan musik jika pindah dari state yang mungkin punya musik, kecuali ke fishing
        if self.current_state_name not in ['main_menu', 'settings'] and new_state_name != 'fishing':
             if pygame.mixer.music.get_busy():
                pygame.mixer.music.fadeout(500)

        old_state = self.current_state_name
        self.current_state_name = new_state_name

        if new_state_name == 'map_explore':
            print("--- Game: Memproses state map_explore ---")
            if not self.map_explorer:
                print("--- Game: Menginisialisasi MapExplorer untuk pertama kali... ---")
                try:
                    self.map_explorer = MapExplorer(self)
                    print("--- Game: MapExplorer berhasil diinisialisasi. ---")
                except Exception as e:
                    print(f"--- Game: ERROR saat menginisialisasi MapExplorer: {e} ---")
                    import traceback; traceback.print_exc()
                    self.current_state_name = old_state
                    if old_state != 'main_menu': self.change_state('main_menu')
                    else: self.running = False # Jika sudah di main_menu dan gagal, baru keluar
                    return
            # Logika musik untuk map_explore (jika ada)
            # map_music_path = os.path.join(self.config.SOUND_PATH, "map_explore_theme.ogg")
            # self.play_music_file(map_music_path)


        elif new_state_name == 'fishing':
            print("--- Game: Memproses state fishing ---")
            if data and 'location_name' in data:
                location_name = data['location_name']
                print(f"--- Game: Data lokasi diterima: {location_name} ---")
                try:
                    self.current_game_map = GameMap(location_name, self.config)
                    if hasattr(self.current_game_map, 'play_music'): self.current_game_map.play_music()
                    
                    self.boat.change_map(self.current_game_map) # Update tipe perahu & sprite berdasarkan map
                    if self.boat.rect: # Pastikan rect ada setelah change_map
                         self.boat.rect.midbottom = (self.config.SCREEN_WIDTH // 2, self.config.SCREEN_HEIGHT - 70)

                    if not self.player:
                        self.player = Player(self.boat, self) # Player butuh boat dan game
                    else:
                        # Jika player sudah ada, update boatnya jika perlu (meskipun Player init sudah handle)
                        if hasattr(self.player, 'boat'): self.player.boat = self.boat
                    
                    # Posisikan player berdasarkan boat
                    if self.player and self.player.rect and self.boat and self.boat.rect:
                        self.player.rect.midbottom = self.boat.rect.midtop
                    
                    self.fishing_system = FishingSystem(self) # FishingSystem butuh game
                    self.fishing_challenge = FishingSkillChallenge() # Sesuai IMPROVE/fishing_challenge.py
                    
                    print(f"--- Game: Setup untuk state fishing lokasi '{location_name}' selesai. ---")
                except Exception as e:
                    print(f"--- Game: ERROR saat setup state fishing: {e} ---")
                    import traceback; traceback.print_exc()
                    self.change_state('map_explore') # Kembali ke map explore jika gagal
                    return
            else:
                print("--- Game: ERROR - Tidak ada location_name untuk state fishing! Kembali ke map_explore. ---")
                self.change_state('map_explore')
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
            # Logika musik untuk main_menu (jika ada)
            # menu_music_path = os.path.join(self.config.SOUND_PATH, "main_menu_theme.ogg")
            # self.play_music_file(menu_music_path, loop=-1)
            pass

    def play_music_file(self, music_path, loop=-1):
        if os.path.exists(music_path):
            try:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.play(loop, fade_ms=1000)
                print(f"--- Game: Memainkan musik: {music_path} ---")
            except pygame.error as e:
                print(f"--- Game: Error memainkan musik {music_path}: {e} ---")
        else:
            print(f"--- Game: File musik tidak ditemukan: {music_path} ---")


    def run(self):
        print("--- Game: Memulai Game.run()... ---")
        if self.current_state_name == 'main_menu': # Panggil change_state untuk setup awal jika state adalah main_menu
            self.change_state('main_menu')

        print("--- Game: Memasuki game loop utama. ---")
        while self.running:
            # print(f"--- Game Loop: Iterasi, self.running = {self.running}, state = {self.current_state_name} ---") # Uncomment for detailed debug
            dt = self.clock.tick(self.config.FPS) / 1000.0
            if dt > 0.1 : dt = 0.1 # Batasi delta time maksimum untuk mencegah lonjakan
            self.current_fps = self.clock.get_fps()

            # 1. Handle Events
            for event in pygame.event.get():
                # print(f"--- Event Diterima: {event} ---") # Uncomment for detailed event debug
                if event.type == pygame.QUIT:
                    print("--- Game: Event pygame.QUIT diterima. Menghentikan game. ---")
                    self.running = False
                    # Tidak langsung keluar, biarkan loop selesai untuk cleanup jika perlu
                
                if self.running: # Hanya proses event state jika game masih berjalan
                    self.handle_state_specific_event(event)

            if not self.running: # Jika event QUIT membuat running False, keluar dari loop
                break

            # 2. Update Game Logic
            try:
                self.update_current_state(dt)
            except Exception as e:
                print(f"--- ERROR DI DALAM UPDATE STATE ({self.current_state_name}) ---")
                print(f"Detail Error: {e}")
                import traceback; traceback.print_exc()
                self.running = False # Hentikan game jika ada error di update

            if not self.running: break # Keluar jika update menyebabkan game berhenti

            # 3. Render
            try:
                self.render_current_state()
            except Exception as e:
                print(f"--- ERROR DI DALAM RENDER STATE ({self.current_state_name}) ---")
                print(f"Detail Error: {e}")
                import traceback; traceback.print_exc()
                self.running = False # Hentikan game jika ada error di render
        
        print("--- Game: Keluar dari game loop utama. ---")
        self.quit_game() # Panggil quit_game setelah loop selesai

    def handle_state_specific_event(self, event):
        """Menangani event berdasarkan state saat ini, setelah event QUIT utama diperiksa."""
        active_handler = None
        handled_by_specific_logic = False

        if self.current_state_name == 'fishing':
            # Fishing state mungkin punya logika event yang lebih kompleks
            if self.fishing_system and hasattr(self.fishing_system, 'challenge_active') and self.fishing_system.challenge_active:
                if self.fishing_challenge and hasattr(self.fishing_challenge, 'handle_event'): # FishingChallenge mungkin punya handle_event sendiri
                    if self.fishing_challenge.handle_event(event):
                        handled_by_specific_logic = True
            
            if not handled_by_specific_logic and self.fishing_system and hasattr(self.fishing_system, 'handle_event'):
                if self.fishing_system.handle_event(event):
                    handled_by_specific_logic = True
            
            if not handled_by_specific_logic and event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.change_state('map_explore')
                handled_by_specific_logic = True
        
        if handled_by_specific_logic:
            return

        # Handler umum untuk menu dan map explorer
        if self.current_state_name == 'main_menu': active_handler = self.main_menu
        elif self.current_state_name == 'settings': active_handler = self.settings_menu
        elif self.current_state_name == 'shop': active_handler = self.shop_menu
        elif self.current_state_name == 'market_screen': active_handler = self.market_screen
        elif self.current_state_name == 'inventory_screen': active_handler = self.inventory_screen
        elif self.current_state_name == 'map_explore': active_handler = self.map_explorer
        
        if active_handler and hasattr(active_handler, 'handle_event'):
            active_handler.handle_event(event) # Menu handle_event bisa mengubah game.running atau state

    def update_current_state(self, dt):
        if self.current_state_name == 'map_explore':
            if self.map_explorer and hasattr(self.map_explorer, 'update'):
                self.map_explorer.update(dt)
        elif self.current_state_name == 'fishing':
            if self.boat and hasattr(self.boat, 'update'):
                self.boat.update(dt, pygame.key.get_pressed()) # Boat update butuh keys
            if self.player and hasattr(self.player, 'update'):
                self.player.update(dt) # Player update mungkin tidak butuh keys jika hanya mengikuti boat
            if self.fishing_system and hasattr(self.fishing_system, 'update'):
                self.fishing_system.update(dt)
        # Tambahkan update untuk state lain jika perlu

    def render_current_state(self):
        self.screen.fill(self.config.COLORS.get('black', (0,0,0))) # Default background

        active_renderer = None
        if self.current_state_name == 'main_menu': active_renderer = self.main_menu
        elif self.current_state_name == 'settings': active_renderer = self.settings_menu
        elif self.current_state_name == 'shop': active_renderer = self.shop_menu
        elif self.current_state_name == 'market_screen': active_renderer = self.market_screen
        elif self.current_state_name == 'inventory_screen': active_renderer = self.inventory_screen
        elif self.current_state_name == 'map_explore':
            if self.map_explorer and hasattr(self.map_explorer, 'render'):
                self.map_explorer.render(self.screen)
        elif self.current_state_name == 'fishing':
            if self.current_game_map and hasattr(self.current_game_map, 'background_image'):
                self.screen.blit(self.current_game_map.background_image, (0,0))
            else: # Fallback jika background map tidak ada
                self.screen.fill(self.config.COLORS.get('water_deep', (5,30,56)))
            
            if self.boat and hasattr(self.boat, 'render'): self.boat.render(self.screen)
            if self.player and hasattr(self.player, 'render'): self.player.render(self.screen)
            if self.fishing_system and hasattr(self.fishing_system, 'render'): self.fishing_system.render(self.screen)
            
            if self.fishing_system and hasattr(self.fishing_system, 'challenge_active') and self.fishing_system.challenge_active:
                if self.fishing_challenge and hasattr(self.fishing_challenge, 'render'):
                    self.fishing_challenge.render(self.screen)
        
        # Render menu jika itu adalah state aktif dan bukan state gameplay utama
        if active_renderer and self.current_state_name not in ['fishing', 'map_explore'] and hasattr(active_renderer, 'render'):
            active_renderer.render(self.screen)

        # Render UI global di atas segalanya
        if self.ui and hasattr(self.ui, 'render'):
            self.ui.render(self.screen)

        # Render info debug
        if self.config.DEBUG:
            debug_text_y = self.config.SCREEN_HEIGHT - self.debug_font.get_height() - 5
            fps_text_surface = self.debug_font.render(f"FPS: {int(self.current_fps)}", True, self.config.COLORS.get('white', (255,255,255)))
            self.screen.blit(fps_text_surface, (10, debug_text_y ))
            
            state_text_surface = self.debug_font.render(f"State: {self.current_state_name}", True, self.config.COLORS.get('white', (255,255,255)))
            state_text_x = fps_text_surface.get_width() + 20
            self.screen.blit(state_text_surface, (state_text_x, debug_text_y))

            # Debug info tambahan jika diperlukan
            # if self.current_state_name == 'fishing' and self.fishing_system:
            #     fs_debug = f"Cast: {self.fishing_system.is_casting}, Reel: {self.fishing_system.is_reeling}, Wait: {self.fishing_system.is_waiting_for_bite}, Hooked: {self.fishing_system.current_hooked_fish is not None}, Chal: {self.fishing_system.challenge_active}"
            #     fs_surf = self.debug_font.render(fs_debug, True, self.config.COLORS.get('white'))
            #     self.screen.blit(fs_surf, (10, debug_text_y - fs_surf.get_height() - 5))


        pygame.display.flip() # Update seluruh layar

    def quit_game(self):
        print("--- Game: Menutup game (quit_game dipanggil)... ---")
        # pygame.quit() # main.py akan memanggil pygame.quit() dan sys.exit() di finally block
        # sys.exit() # Tidak perlu sys.exit() di sini, biarkan main.py yang menangani

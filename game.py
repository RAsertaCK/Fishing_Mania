# TES/game.py
import pygame
import sys
import os

from config import Config
from menu import MainMenu, SettingsMenu, ShopMenu, MarketScreen, InventoryScreen
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
            def __init__(self): self.name = "initial_setup"
        self.boat = Boat(InitialDummyMap(), self.config)

        self.main_menu = MainMenu(self)
        self.settings_menu = SettingsMenu(self)
        self.shop_menu = ShopMenu(self)
        self.market_screen = MarketScreen(self)
        self.inventory_screen = InventoryScreen(self)
        
        self.all_sprites = pygame.sprite.Group()
        self.blocks = pygame.sprite.Group()

        try:
            self.character_spritesheet = Spritesheet(self.config.PLAYER_SPRITESHEET_PATH)
            print(f"--- Game: Spritesheet karakter '{self.config.PLAYER_SPRITESHEET_PATH}' dimuat. ---")
        except Exception as e:
            print(f"--- Game: ERROR memuat spritesheet karakter: {e}. Player darat mungkin tidak tampil. ---")
            self.character_spritesheet = None

        self.land_player = None
        if self.character_spritesheet:
            self.land_player = LandPlayer(self, 10, 10)
            print(f"--- Game: LandPlayer (pemain darat) berhasil diinisialisasi. ---")
        else:
            print("--- Game: LandPlayer tidak dapat diinisialisasi karena spritesheet gagal dimuat. ---")

        self.land_explorer = LandExplorer(self)
        self.map_explorer = MapExplorer(self)

        self.current_game_map = None
        self.player = None

        self.fishing_system = None
        self.fishing_challenge = None

        self.ui = UI(self)
        print("--- Game: Game.__init__() selesai. ---")

    def change_state(self, new_state_name, data=None):
        print(f"--- Game: Mengubah state dari {self.current_state_name} ke {new_state_name} dengan data: {data} ---")
        
        self.all_sprites.empty()
        self.blocks.empty()

        if self.current_state_name not in ['main_menu', 'settings'] and \
           new_state_name not in ['fishing', 'map_explore', 'land_explore']:
             if pygame.mixer.music.get_busy():
                pygame.mixer.music.fadeout(500)

        old_state = self.current_state_name
        self.current_state_name = new_state_name

        if new_state_name == 'land_explore':
            print("--- Game: Memproses state land_explore ---")
            print("--- Game: LandExplorer sudah diinisialisasi, beralih ke state land_explore. ---")
            if self.land_explorer:
                self.land_explorer.setup_scene()

        elif new_state_name == 'map_explore':
            print("--- Game: Memproses state map_explore (laut) ---")
            print("--- Game: MapExplorer sudah diinisialisasi, beralih ke state map_explore. ---")

        elif new_state_name == 'fishing':
            print("--- Game: Memproses state fishing ---")
            if data and 'location_name' in data:
                location_name = data['location_name']
                print(f"--- Game: Data lokasi diterima: {location_name} ---")
                try:
                    self.current_game_map = GameMap(location_name, self.config)
                    if hasattr(self.current_game_map, 'play_music'): self.current_game_map.play_music()
                    
                    self.boat.change_map(self.current_game_map)
                    if self.boat.rect:
                         self.boat.rect.midbottom = (self.config.SCREEN_WIDTH // 2, self.config.SCREEN_HEIGHT - 70)

                    if not self.player:
                        self.player = PlayerBoat(self.boat, self)
                    else:
                        if hasattr(self.player, 'boat'): self.player.boat = self.boat
                    
                    if self.player and self.player.rect and self.boat and self.boat.rect:
                        self.player.rect.midbottom = self.boat.rect.midtop
                    
                    self.fishing_system = FishingSystem(self)
                    self.fishing_challenge = FishingSkillChallenge()
                    
                    print(f"--- Game: Setup untuk state fishing lokasi '{location_name}' selesai. ---")
                except Exception as e:
                    print(f"--- Game: ERROR saat setup state fishing: {e} ---")
                    import traceback
                    traceback.print_exc()
                    self.change_state('map_explore')
                    return
            else:
                print("--- Game: ERROR - Tidak ada location_name untuk state fishing! Kembali ke map_explore. ---")
                self.change_state('map_explore')
                return
        elif new_state_name == 'shop':
            pass
        elif new_state_name == 'market_screen':
            pass
        elif new_state_name == 'inventory_screen':
            pass
        elif new_state_name == 'main_menu':
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
        if self.current_state_name == 'main_menu':
            self.change_state('main_menu')

        print("--- Game: Memasuki game loop utama. ---")
        while self.running:
            dt = self.clock.tick(self.config.FPS) / 1000.0
            if dt > 0.1 : dt = 0.1
            self.current_fps = self.clock.get_fps()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("--- Game: Event pygame.QUIT diterima. Menghentikan game. ---")
                    self.running = False
                
                if self.running:
                    self.handle_state_specific_event(event)

            if not self.running:
                break

            try:
                self.update_current_state(dt)
            except Exception as e:
                print(f"--- ERROR DI DALAM UPDATE STATE ({self.current_state_name}) ---")
                print(f"Detail Error: {e}")
                import traceback
                traceback.print_exc()
                self.running = False

            if not self.running: break

            try:
                self.render_current_state()
            except Exception as e:
                print(f"--- ERROR DI DALAM RENDER STATE ({self.current_state_name}) ---")
                print(f"Detail Error: {e}")
                import traceback
                traceback.print_exc()
                self.running = False
        
        print("--- Game: Keluar dari game loop utama. ---")
        self.quit_game()

    def handle_state_specific_event(self, event):
        active_handler = None
        handled_by_specific_logic = False

        if self.current_state_name == 'fishing':
            if self.fishing_system and hasattr(self.fishing_system, 'challenge_active') and self.fishing_system.challenge_active:
                if self.fishing_challenge and hasattr(self.fishing_challenge, 'handle_event'):
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

        if self.current_state_name == 'main_menu': active_handler = self.main_menu
        elif self.current_state_name == 'settings': active_handler = self.settings_menu
        elif self.current_state_name == 'shop': active_handler = self.shop_menu
        elif self.current_state_name == 'market_screen': active_handler = self.market_screen
        elif self.current_state_name == 'inventory_screen': active_handler = self.inventory_screen
        elif self.current_state_name == 'land_explore': active_handler = self.land_explorer
        elif self.current_state_name == 'map_explore': active_handler = self.map_explorer
        
        if active_handler and hasattr(active_handler, 'handle_event'):
            active_handler.handle_event(event)

    def update_current_state(self, dt):
        if self.current_state_name == 'land_explore':
            if self.land_explorer and hasattr(self.land_explorer, 'update'):
                self.land_explorer.update(dt)
            if self.land_player:
                self.land_player.update()
        elif self.current_state_name == 'map_explore':
            if self.map_explorer and hasattr(self.map_explorer, 'update'):
                self.map_explorer.update(dt)
        elif self.current_state_name == 'fishing':
            if self.boat and hasattr(self.boat, 'update'):
                self.boat.update(dt, pygame.key.get_pressed())
            if self.player and hasattr(self.player, 'update'):
                self.player.update(dt)
            if self.fishing_system and hasattr(self.fishing_system, 'update'):
                self.fishing_system.update(dt)
        
    def render_current_state(self, ):
        self.screen.fill(self.config.COLORS.get('black', (0,0,0)))

        active_renderer = None
        if self.current_state_name == 'main_menu': active_renderer = self.main_menu
        elif self.current_state_name == 'settings': active_renderer = self.settings_menu
        elif self.current_state_name == 'shop': active_renderer = self.shop_menu
        elif self.current_state_name == 'market_screen': active_renderer = self.market_screen
        elif self.current_state_name == 'inventory_screen': active_renderer = self.inventory_screen
        elif self.current_state_name == 'land_explore':
            if self.land_explorer and hasattr(self.land_explorer, 'render'):
                self.land_explorer.render(self.screen)
            pass
        elif self.current_state_name == 'map_explore':
            if self.map_explorer and hasattr(self.map_explorer, 'render'):
                self.map_explorer.render(self.screen)
        elif self.current_state_name == 'fishing':
            if self.current_game_map and hasattr(self.current_game_map, 'background_image'):
                self.screen.blit(self.current_game_map.background_image, (0,0))
            else:
                self.screen.fill(self.config.COLORS.get('water_deep', (5,30,56)))
            
            if self.boat and hasattr(self.boat, 'render'): self.boat.render(self.screen)
            if self.player and hasattr(self.player, 'render'): self.player.render(self.screen)
            if self.fishing_system and hasattr(self.fishing_system, 'render'): self.fishing_system.render(self.screen)
            
            if self.fishing_system and hasattr(self.fishing_system, 'challenge_active') and self.fishing_system.challenge_active:
                if self.fishing_challenge and hasattr(self.fishing_challenge, 'render'):
                    self.fishing_challenge.render(self.screen)
        
        if active_renderer and self.current_state_name not in ['fishing', 'map_explore', 'land_explore'] and hasattr(active_renderer, 'render'):
            active_renderer.render(self.screen)

        if self.ui and hasattr(self.ui, 'render') and self.current_state_name in ['land_explore', 'map_explore', 'fishing']:
            self.ui.render(self.screen)

        if self.config.DEBUG:
            debug_text_y = self.config.SCREEN_HEIGHT - self.debug_font.get_height() - 5
            fps_text_surface = self.debug_font.render(f"FPS: {int(self.current_fps)}", True, self.config.COLORS.get('white', (255,255,255)))
            self.screen.blit(fps_text_surface, (10, debug_text_y ))
            
            state_text_surface = self.debug_font.render(f"State: {self.current_state_name}", True, self.config.COLORS.get('white', (255,255,255)))
            state_text_x = fps_text_surface.get_width() + 20
            self.screen.blit(state_text_surface, (state_text_x, debug_text_y))

        pygame.display.flip()

    def quit_game(self):
        print("--- Game: Menutup game (quit_game dipanggil)... ---")
# IMPROVE/fishing_system.py
import pygame
import os
import random
# from fish import Fish # Tidak perlu impor Fish di sini jika hanya menangani data ikan

class FishingSystem:
    def __init__(self, game_instance): # Menerima instance Game
        self.game = game_instance
        self.config = self.game.config
        
        self.is_casting = False
        self.is_reeling = False
        self.is_waiting_for_bite = False
        self.hook_depth = 0
        
        # Dapatkan max_hook_depth dari game_map saat ini
        if self.game.current_game_map and hasattr(self.game.current_game_map, 'data') and \
           'depth_range' in self.game.current_game_map.data:
            self.max_hook_depth = self.game.current_game_map.data['depth_range'][1]
        else:
            self.max_hook_depth = 200 # Fallback
        
        self.cast_speed = 150
        self.reel_speed = 180

        self.current_hooked_fish_data = None # Akan menyimpan data ikan yang terkait (dict)
        self.challenge_active = False
        
        self.hook_color = self.config.COLORS.get("white", (255,255,255))
        self.line_color = self.config.COLORS.get("text_inactive", (180,180,180))
        self.hook_width = 6
        self.hook_tip_height = 12

        self.bite_timer_start = 0
        self.current_wait_time_for_bite = 0
        # print("--- FishingSystem: Instance FishingSystem dibuat. ---")

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
        # Jika menggulung dan ada ikan terkait TAPI challenge belum aktif/selesai, mulai challenge
        if not from_challenge_resolve and self.current_hooked_fish_data and not self.challenge_active:
            self.start_fishing_challenge(self.current_hooked_fish_data)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if self.challenge_active and self.game.fishing_challenge:
                    # FishingSkillChallenge di IMPROVE tidak punya handle_event, tapi kita bisa tambahkan jika perlu
                    # Untuk sekarang, asumsikan SPACE di challenge ditangani di update challenge
                    # Atau, jika FishingSkillChallenge punya handle_event:
                    # if hasattr(self.game.fishing_challenge, 'handle_event') and self.game.fishing_challenge.handle_event(event):
                    #     return True
                    # Jika tidak, biarkan update challenge yang menangani SPACE
                    pass # Event SPACE saat challenge aktif akan dicek di update challenge
                elif not self.is_casting and not self.is_reeling and not self.current_hooked_fish_data:
                    self.start_cast()
                    return True
                elif self.is_casting or self.is_waiting_for_bite: # Jika sedang melempar atau menunggu, SPACE akan menggulung
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
                self.current_wait_time_for_bite = random.randint(2000, 5000) # Tunggu 2-5 detik
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
                        self.start_reel_in() # Tidak ada ikan, gulung kosong
                else:
                    self.start_reel_in()

        elif self.is_reeling:
            reel_speed_actual = self.reel_speed
            # Bisa tambahkan logika perlambatan jika ada ikan besar (setelah challenge selesai)
            # if self.current_hooked_fish_data and not self.challenge_active:
            #    reel_speed_actual *= 0.7 # Contoh: lebih lambat jika ada ikan

            self.hook_depth -= reel_speed_actual * dt
            if self.hook_depth <= 0:
                self.hook_depth = 0
                self.is_reeling = False
                if self.current_hooked_fish_data and not self.challenge_active: # Ikan berhasil ditarik setelah challenge (jika ada)
                    print(f"--- FishingSystem: Ikan {self.current_hooked_fish_data.get('name', 'Misterius')} berhasil ditarik ke perahu (setelah challenge)! ---")
                    # Logika penambahan ke inventaris sudah ada di resolve_fishing_challenge
                    # self.current_hooked_fish_data = None # Direset di resolve
                elif not self.current_hooked_fish_data:
                    print("--- FishingSystem: Gulungan kosong selesai. ---")
                self.current_hooked_fish_data = None # Pastikan reset jika sudah sampai atas

        # Update fishing challenge jika aktif
        if self.challenge_active and self.game.fishing_challenge:
            if hasattr(self.game.fishing_challenge, 'update'):
                 self.game.fishing_challenge.update() # Versi IMPROVE tidak pakai dt
            
            # Periksa hasil challenge
            challenge_result_status = getattr(self.game.fishing_challenge, 'result', None)
            if challenge_result_status is not None: # Jika challenge sudah menghasilkan sesuatu ('caught' atau 'failed')
                self.resolve_fishing_challenge(challenge_result_status == "caught") # Kirim True jika "caught"

    def start_fishing_challenge(self, fish_data_hooked):
        if self.game.fishing_challenge and hasattr(self.game.fishing_challenge, 'start'):
            print(f"--- FishingSystem: Memulai fishing challenge untuk {fish_data_hooked.get('name')} ---")
            self.game.fishing_challenge.start() # Versi IMPROVE tidak pakai argumen ikan
            self.challenge_active = True
            self.is_casting = False
            self.is_waiting_for_bite = False
            # self.is_reeling tetap True karena kita sedang dalam proses menggulung saat challenge
            if not self.is_reeling: self.is_reeling = True


    def resolve_fishing_challenge(self, success):
        print(f"--- FishingSystem: Menyelesaikan fishing challenge. Sukses: {success} ---")
        self.challenge_active = False
        self.game.fishing_challenge.result = None # Reset hasil challenge untuk pemanggilan berikutnya

        hooked_fish_name = self.current_hooked_fish_data.get('name', 'Ikan Misterius') if self.current_hooked_fish_data else "Ikan Tak Dikenal"

        if success and self.current_hooked_fish_data:
            print(f"    SELAMAT! Ikan {hooked_fish_name} berhasil ditangkap!")
            if self.game.inventory and hasattr(self.game.inventory, 'add_fish_from_data'): # Asumsi ada metode ini
                self.game.inventory.add_fish_from_data(self.current_hooked_fish_data)
            elif self.game.inventory and hasattr(self.game.inventory, 'add'): # Fallback ke 'add' jika ada
                 # 'add' di IMPROVE/inventory.py menerima objek Fish, bukan data. Ini perlu disesuaikan.
                 # Untuk sekarang, kita asumsikan ada cara untuk menambah dari data atau kita buat objek Fish.
                 # Jika inventory.add() butuh objek Fish, kita perlu buat instance Fish di sini.
                 # from fish import Fish # Impor jika perlu buat instance Fish
                 # fish_obj = Fish(self.current_hooked_fish_data, (0,0)) # Posisi dummy
                 # self.game.inventory.add(fish_obj)
                 print(f"    PERINGATAN: Inventory.add_fish_from_data tidak ada. Ikan {hooked_fish_name} mungkin tidak tersimpan.")
            else:
                print(f"    ERROR: Tidak bisa menambahkan ikan {hooked_fish_name} ke inventaris.")
            
            # Tambah koin jika berhasil
            if hasattr(self.game, 'wallet'):
                fish_value = self.current_hooked_fish_data.get('value', 0)
                self.game.wallet += fish_value
                print(f"    Koin bertambah {fish_value}. Total koin: {self.game.wallet}")

        else:
            print(f"    SAYANG SEKALI, ikan {hooked_fish_name} lepas!")
        
        self.current_hooked_fish_data = None # Ikan sudah ditangani (tertangkap atau lepas)

        # Lanjutkan menggulung jika belum sampai atas
        if not self.is_reeling and self.hook_depth > 0 : # Jika challenge selesai dan kail belum di atas
            self.start_reel_in(from_challenge_resolve=True)
        elif self.hook_depth <= 0: # Jika sudah di atas
            self.is_reeling = False


    def render(self, screen):
        if (self.is_casting or self.is_reeling or self.is_waiting_for_bite or self.challenge_active) and \
           self.game.boat and self.game.boat.rect and self.game.boat.type not in ["initial_setup", "dummy"]:
            
            # Pastikan player ada dan punya rect untuk posisi pancing relatif ke pemain/perahu
            # Untuk simple, kita pakai posisi perahu
            line_start_x = self.game.boat.rect.centerx
            line_start_y = self.game.boat.rect.top + 10 # Sedikit di atas perahu

            water_surface_y = self.game.boat.rect.bottom - 25 # Perkiraan permukaan air relatif ke perahu
            hook_end_y = water_surface_y + self.hook_depth
            hook_end_x = line_start_x

            # Gambar tali pancing
            pygame.draw.line(screen, self.line_color, (line_start_x, line_start_y), (hook_end_x, hook_end_y), 2)

            # Gambar kail
            hook_visual_rect = pygame.Rect(hook_end_x - self.hook_width // 2, hook_end_y - self.hook_tip_height // 2, self.hook_width, self.hook_tip_height)
            pygame.draw.ellipse(screen, self.hook_color, hook_visual_rect) # Kail sederhana berbentuk elips

            # Tampilkan nama ikan yang terkait (jika ada dan belum di challenge)
            if self.current_hooked_fish_data and not self.challenge_active:
                fish_name_text = self.current_hooked_fish_data.get('name', 'Fish?')
                rarity_text = self.current_hooked_fish_data.get('rarity', '')
                
                # Pilih warna berdasarkan kelangkaan
                rarity_color_key = rarity_text.lower() if rarity_text else 'common'
                text_color = self.config.COLORS.get(rarity_color_key, self.config.COLORS.get('white'))

                if hasattr(self.game, 'debug_font'): # Gunakan debug_font dari game
                    fish_label = self.game.debug_font.render(f"~{fish_name_text}~ ({rarity_text})", True, text_color)
                    screen.blit(fish_label, (hook_visual_rect.centerx + 10, hook_visual_rect.centery - fish_label.get_height()//2))

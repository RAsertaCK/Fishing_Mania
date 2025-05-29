# fish.py
import pygame
import random
import os
import math

class Fish(pygame.sprite.Sprite):
    def __init__(self, fish_data, pos, config_instance):
        super().__init__()

        self.name = fish_data["name"]
        self.rarity = fish_data["rarity"]
        self.value = fish_data["value"]
        self.pos = list(pos) 
        
        self.config_ref = config_instance
        self.image_suffix = fish_data.get("image_suffix", self.name.lower().replace(' ', '_'))

        self.image = None 
        if self.config_ref:
            filename = f"fish_{self.rarity}_{self.image_suffix}.png"
            image_path = os.path.join(self.config_ref.FISH_PATH, filename)
            
            # print(f"--- Fish: Mencoba memuat ikan: {image_path} ---") # Aktifkan jika perlu debug path
            try:
                # Muat gambar asli terlebih dahulu
                loaded_image_direct = pygame.image.load(image_path)
                # Konversi alpha untuk transparansi
                self.image = loaded_image_direct.convert_alpha() 
                
                # Lakukan penskalaan setelah convert_alpha
                scale_factor = 0.7  # PERUBAHAN: Dari 0.1 (atau nilai sebelumnya) menjadi 0.4 untuk ikan lebih besar
                                    # Anda bisa coba nilai lain seperti 0.3, 0.5, 0.6, dst.

                new_width = int(self.image.get_width() * scale_factor)
                new_height = int(self.image.get_height() * scale_factor)
                
                if new_width > 0 and new_height > 0:
                    self.image = pygame.transform.scale(self.image, (new_width, new_height))
                else:
                    # Jika penskalaan menghasilkan ukuran tidak valid, gunakan gambar asli setelah convert_alpha
                    # atau fallback ke placeholder jika self.image menjadi tidak valid
                    print(f"--- Fish WARN: Penskalaan menghasilkan ukuran tidak valid ({new_width}x{new_height}) untuk {image_path}. Ukuran asli mungkin digunakan atau placeholder.")
                    if not (self.image.get_width() > 0 and self.image.get_height() > 0) : # Double check image is valid
                        self.image = None # Tandai untuk menggunakan placeholder di bawah
                
                # Debugging flags (opsional, bisa dihapus komentarnya jika perlu)
                # if self.image:
                #     print(f"--- Fish: Gambar '{image_path}' dimuat. Ukuran setelah skala: {self.image.get_size()}, Flags: {self.image.get_flags()} ---")
                #     if not (self.image.get_flags() & pygame.SRCALPHA):
                #         print(f"--- Fish WARN: Gambar '{image_path}' TIDAK memiliki SRCALPHA! Transparansi mungkin bermasalah.")

            except Exception as e:
                print(f"--- Fish ERROR: Gagal memuat atau memproses '{image_path}': {e}.")
                self.image = None # Pastikan self.image adalah None jika ada error
        
        if self.image is None: # Fallback absolut jika semua gagal
            print(f"--- Fish PERINGATAN: self.image None untuk {self.name}, membuat placeholder darurat (kuning).")
            self.image = pygame.Surface((30,20)) # Ukuran placeholder
            self.image.fill((200,200,0)) # Warna kuning untuk placeholder
            # Jika ingin placeholder ini juga bisa transparan, gunakan:
            # self.image = pygame.Surface((30,20), pygame.SRCALPHA)
            # self.image.fill((200,200,0, 128)) # Kuning semi-transparan

        self.swim_speed = random.uniform(20, 80)
        self.swim_direction = random.choice([-1, 1])
        self.wobble_amount = random.uniform(0.5, 2.0)
        self.wobble_speed = random.uniform(0.5, 1.5)
        self.time = 0
        
        # Pastikan self.image valid sebelum get_rect
        if self.image:
            self.rect = self.image.get_rect(center=pos)
        else: # Jika self.image masih None (misalnya error parah saat load)
            self.image = pygame.Surface((10,10)); self.image.fill((255,0,0)) # Placeholder error akhir
            self.rect = self.image.get_rect(center=pos)


        self.caught = False
        self.is_secured_on_hook = False

    def update(self, dt):
        self.time += dt
        if not self.caught and not self.is_secured_on_hook:
            self.pos[0] += self.swim_direction * self.swim_speed * dt
            self.pos[1] += math.sin(self.time * self.wobble_speed) * self.wobble_amount
            if random.random() < 0.01:
                self.swim_direction *= -1
        
        self.rect.center = self.pos
        return None

    def get_data(self):
        return {
            "name": self.name,
            "rarity": self.rarity,
            "value": self.value,
            "image_suffix": self.image_suffix
        }

    def follow_hook(self, hook_world_pos_x, hook_world_pos_y):
        if self.is_secured_on_hook:
            self.pos[0] = hook_world_pos_x
            self.pos[1] = hook_world_pos_y
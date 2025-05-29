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

        self.image = None # Akan diisi oleh load_image atau placeholder darurat
        if self.config_ref:
            filename = f"fish_{self.rarity}_{self.image_suffix}.png"
            image_path = os.path.join(self.config_ref.FISH_PATH, filename) #
            # print(f"--- Fish: Mencoba memuat ikan: {image_path} ---") # Aktifkan jika perlu debug path
            
            self.image = self.config_ref.load_image(image_path, 0.1) #
            
            # Jika self.image adalah placeholder standar dari Config (misal, 50x50 magenta), 
            # Anda bisa log di sini atau bahkan mencoba membuat placeholder yang lebih informatif
            # jika Anda mau, tapi untuk sekarang, kita gunakan saja apa yang dikembalikan load_image.
            if self.image.get_width() == 25 and self.image.get_height() == 25: # Cek heuristik untuk placeholder default
                 # Cek apakah file aslinya memang ada, jika tidak ada, maka ini benar placeholder
                 if not os.path.exists(image_path):
                      print(f"--- Fish: '{image_path}' tidak ditemukan, menggunakan placeholder dari Config.")
                 # else: file ada tapi setelah load_image jadi 50x50, bisa jadi error pygame saat load.
            
        if self.image is None: # Fallback absolut jika config_ref tidak ada atau load_image mengembalikan None (seharusnya tidak dengan implementasi baru)
            print(f"PERINGATAN Fish: self.image masih None untuk {self.name}, membuat placeholder darurat.")
            self.image = pygame.Surface((30,20)); self.image.fill((200,200,0)) # Kuning


        self.swim_speed = random.uniform(20, 80)
        self.swim_direction = random.choice([-1, 1])
        self.wobble_amount = random.uniform(0.5, 2.0)
        self.wobble_speed = random.uniform(0.5, 1.5)
        self.time = 0
        
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
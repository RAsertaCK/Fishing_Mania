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

        self.image = None # Inisialisasi image
        if self.config_ref:
            image_suffix = fish_data.get("image_suffix", self.name.lower().replace(' ', '_'))
            filename = f"fish_{self.rarity}_{image_suffix}.png" # Pastikan ekstensi .png
            image_path = os.path.join(self.config_ref.FISH_PATH, filename)
            
            # Coba muat gambar, jika gagal, self.image akan menjadi placeholder dari load_image
            self.image = self.config_ref.load_image(image_path, 0.5)
            if self.image.get_width() == 50 and self.image.get_height() == 50: # Cek apakah itu placeholder standar
                print(f"PERINGATAN Fish: Gagal memuat gambar untuk '{filename}', menggunakan placeholder.")
        
        if self.image is None: # Jika self.image masih None (misal config_ref tidak ada)
            print(f"PERINGATAN Fish: config_instance tidak ada atau gambar tidak termuat untuk {self.name}, membuat placeholder manual.")
            self.image = pygame.Surface((30,20)) 
            self.image.fill((200,200,0)) # Kuning sebagai indikasi

        self.swim_speed = random.uniform(20, 80)
        self.swim_direction = random.choice([-1, 1])
        self.wobble_amount = random.uniform(0.5, 2.0)
        self.wobble_speed = random.uniform(0.5, 1.5)
        self.time = 0
        self.escape_chance = {"common": 0.1, "rare": 0.3, "legendary": 0.5}.get(self.rarity, 0.2)
        
        self.rect = self.image.get_rect(center=pos)
        self.caught = False

    def update(self, dt):
        self.time += dt
        if not self.caught:
            self.pos[0] += self.swim_direction * self.swim_speed * dt
            self.pos[1] += math.sin(self.time * self.wobble_speed) * self.wobble_amount
            if random.random() < 0.01:
                self.swim_direction *= -1
        
        self.rect.center = self.pos # Update rect berdasarkan self.pos
        return None
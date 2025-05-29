# boat.py
import pygame
import os

class Boat:
    UPGRADE_LEVELS = {
        "speed": [200, 250, 300, 400, 500],
        "capacity": [10, 15, 20, 30, 50],
        "sonar": [0, 1, 2, 3, 4]
    }

    def __init__(self, game_map, config_instance):
        self.game_map = game_map
        self.config = config_instance

        self.upgrades = {"speed": 0, "capacity": 0, "sonar": 0}
        self.current_speed_value = self.UPGRADE_LEVELS["speed"][0]
        
        self.type = "default"
        if self.game_map and hasattr(self.game_map, 'name') and self.game_map.name not in ["initial_setup", "dummy"]:
             self.type = self.game_map.name.lower()
        
        self.base_image = None
        self.rect = None

        self.load_sprite() # Panggil load_sprite di init untuk memastikan kapal dimuat di awal


    def load_sprite(self):
        # Path utama yang ingin dimuat: kapal laut.png
        target_image_path = os.path.join(self.config.ASSET_PATH, "Player", "kapal laut.png") # Path ke kapal laut.png

        try:
            self.base_image = self.config.load_image(target_image_path, scale=0.7)
            # Jika gambar yang dimuat adalah placeholder (karena target_image_path tidak ditemukan),
            # maka Pygame akan membuat surface 50x50.
            # Kita tidak perlu mencari boat_default.png lagi jika sudah ada fallback otomatis.
            if self.base_image and self.base_image.get_width() > 1: # Cek jika gambar asli berhasil dimuat
                print(f"      Boat: Berhasil memuat kapal dari '{target_image_path}'.")
            else:
                # Ini berarti load_image mengembalikan placeholder, jadi kita sudah "fallback"
                print(f"      Boat: WARN: Gagal memuat '{target_image_path}'. Menggunakan placeholder internal.")

            # Inisialisasi rect jika belum ada, atau jika gambar yang dimuat adalah placeholder
            if not self.rect or (self.base_image and self.base_image.get_width() <= 1 and self.base_image.get_height() <= 1):
                 self.rect = self.base_image.get_rect(
                     midbottom=(self.config.SCREEN_WIDTH // 2, self.config.SCREEN_HEIGHT - 50)
                 )
        except Exception as e:
            print(f"      ERROR saat load_sprite untuk kapal: {e}. Menggunakan placeholder umum.")
            # Fallback ke placeholder jika terjadi error (ini sudah dilakukan oleh Config.load_image)
            self.base_image = pygame.Surface((100,50), pygame.SRCALPHA)
            self.base_image.fill(self.config.COLORS.get('blue', (0,0,255,100)))
            if not self.rect:
                self.rect = self.base_image.get_rect(
                    midbottom=(self.config.SCREEN_WIDTH // 2, self.config.SCREEN_HEIGHT - 50)
                )

    def change_map(self, new_game_map):
        self.game_map = new_game_map
        self.load_sprite() # Muat ulang sprite jika peta berubah

    def get_upgrade_cost(self, upgrade_type):
        current_level = self.upgrades.get(upgrade_type, 0)
        if upgrade_type not in self.UPGRADE_LEVELS or current_level >= len(self.UPGRADE_LEVELS[upgrade_type]) - 1:
            return None
        return (current_level + 1) * 100

    def upgrade(self, upgrade_type):
        current_level = self.upgrades.get(upgrade_type, 0)
        if upgrade_type not in self.UPGRADE_LEVELS or current_level >= len(self.UPGRADE_LEVELS[upgrade_type]) - 1:
            return False

        self.upgrades[upgrade_type] += 1
        new_level = self.upgrades[upgrade_type]

        if upgrade_type == "speed":
            self.current_speed_value = self.UPGRADE_LEVELS["speed"][new_level]
        elif upgrade_type == "capacity":
            pass
        elif upgrade_type == "sonar":
            pass
        return True

    def update(self, dt, keys):
        if not self.rect: # Hanya perlu cek self.rect, karena self.type sudah diinisialisasi
            return

        move_amount = self.current_speed_value * dt
        if keys[pygame.K_LEFT]:
            self.rect.x -= move_amount
        if keys[pygame.K_RIGHT]:
            self.rect.x += move_amount
        
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(self.config.SCREEN_WIDTH, self.rect.right)

    def render(self, surface):
        if self.base_image and self.rect and self.base_image.get_width() > 1 :
            surface.blit(self.base_image, self.rect)
        
        if self.upgrades.get("sonar", 0) > 0 and self.rect :
            try:
                sonar_img_path = os.path.join(self.config.UI_PATH, "sonar_indicator.png")
                if os.path.exists(sonar_img_path):
                    sonar_img = self.config.load_image(sonar_img_path, scale=0.5)
                    surface.blit(sonar_img, (self.rect.right - sonar_img.get_width() - 5, self.rect.top + 5))
            except Exception as e:
                pass
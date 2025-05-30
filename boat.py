# boat.py
import pygame
import os

class Boat:
    UPGRADE_LEVELS = {
        "speed": [200, 250, 300, 400, 500],
        "capacity": [10, 15, 20, 30, 50],
        "line_length": [450, 500, 700, 850, 1000] 
    }

    def __init__(self, game_map, config_instance, world_bounds_rect):
        self.game_map = game_map 
        self.config = config_instance 
        self.world_bounds_rect = world_bounds_rect 

        # Atur default untuk upgrades, ini akan di-overwrite oleh GameData jika ada save file
        self.upgrades = {"speed": 0, "capacity": 0, "line_length": 0} 
        
        # Nilai-nilai ini akan diupdate oleh Game saat memuat data
        self.current_speed_value = self.UPGRADE_LEVELS["speed"][0] 
        self.current_line_length_value = self.UPGRADE_LEVELS["line_length"][0] 
        self.current_capacity_value = self.UPGRADE_LEVELS["capacity"][0] 
        
        self.type = "default" 
        if self.game_map and hasattr(self.game_map, 'name') and self.game_map.name not in ["initial_setup", "dummy"]: 
             self.type = self.game_map.name.lower() 
        
        self.base_image = None 
        self.rect = None 

        self.load_sprite()
        if self.base_image: 
            initial_x = self.world_bounds_rect.centerx if self.world_bounds_rect else self.config.SCREEN_WIDTH // 2
            initial_y_bottom = self.config.SCREEN_HEIGHT - 70 
            
            if self.rect is None: 
                self.rect = self.base_image.get_rect(midbottom=(initial_x, initial_y_bottom))
            else: 
                self.rect.centerx = initial_x
                self.rect.midbottom = (initial_x, initial_y_bottom)
        
        self.facing_direction = -1 

    def load_sprite(self):
        target_image_path = os.path.join(self.config.ASSET_PATH, "Player", "kapal laut.png") 

        try:
            self.base_image = self.config.load_image(target_image_path, scale=0.7) 
            if self.base_image and self.base_image.get_width() > 1: 
                print(f"      Boat: Berhasil memuat kapal dari '{target_image_path}'.") 
            else:
                print(f"      Boat: WARN: Gagal memuat '{target_image_path}'. Menggunakan placeholder internal.") 
            
            current_midbottom = None
            if self.rect:
                current_midbottom = self.rect.midbottom
            
            self.rect = self.base_image.get_rect() 
            
            if current_midbottom: 
                self.rect.midbottom = current_midbottom
            else: 
                initial_x = self.world_bounds_rect.centerx if self.world_bounds_rect else self.config.SCREEN_WIDTH // 2
                self.rect.midbottom = (initial_x, self.config.SCREEN_HEIGHT - 70) 


        except Exception as e:
            print(f"      ERROR saat load_sprite untuk kapal: {e}. Menggunakan placeholder umum.") 
            self.base_image = pygame.Surface((100,50), pygame.SRCALPHA) 
            self.base_image.fill(self.config.COLORS.get('blue', (0,0,255,100))) 
            
            current_midbottom = None
            if self.rect:
                current_midbottom = self.rect.midbottom
            self.rect = self.base_image.get_rect()
            if current_midbottom:
                self.rect.midbottom = current_midbottom
            else:
                initial_x = self.world_bounds_rect.centerx if self.world_bounds_rect else self.config.SCREEN_WIDTH // 2
                self.rect.midbottom = (initial_x, self.config.SCREEN_HEIGHT - 70) 


    def change_map(self, new_game_map, new_world_bounds_rect): 
        self.game_map = new_game_map 
        self.world_bounds_rect = new_world_bounds_rect
        self.load_sprite() 
        if self.rect: 
            # Posisi Y akan diatur oleh game.py setelah water_top_y diketahui
            self.rect.centerx = self.world_bounds_rect.centerx
            # self.rect.midbottom = (self.rect.centerx, self.config.SCREEN_HEIGHT - 70) # Biarkan Game.py atur Y

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
        elif upgrade_type == "line_length": 
            self.current_line_length_value = self.UPGRADE_LEVELS["line_length"][new_level]
        elif upgrade_type == "capacity": # <--- TAMBAHKAN INI: Update current_capacity_value
            self.current_capacity_value = self.UPGRADE_LEVELS["capacity"][new_level]
        return True 

    def update(self, dt, keys):
        if not self.rect: 
            return

        move_amount = self.current_speed_value * dt 
        
        if keys[pygame.K_LEFT]: 
            self.rect.x -= move_amount 
            self.facing_direction = -1 
        if keys[pygame.K_RIGHT]: 
            self.rect.x += move_amount 
            self.facing_direction = 1 

        if self.world_bounds_rect:
            self.rect.left = max(self.world_bounds_rect.left, self.rect.left)
            self.rect.right = min(self.world_bounds_rect.right, self.rect.right)
        else: 
            self.rect.left = max(0, self.rect.left) 
            self.rect.right = min(self.config.SCREEN_WIDTH, self.rect.right) 

    def render_with_camera(self, surface, camera): 
        if self.base_image and self.rect: 
            flipped_image = pygame.transform.flip(self.base_image, self.facing_direction == 1, False)
            surface.blit(flipped_image, camera.apply(self.rect))
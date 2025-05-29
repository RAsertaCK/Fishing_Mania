# camera_system.py
import pygame

class Camera:
    def __init__(self, world_width, world_height, screen_width, screen_height):
        # 'camera' adalah Rect yang merepresentasikan viewport kamera di dalam dunia game.
        # Awalnya, kamera berada di pojok kiri atas dunia.
        self.camera_rect = pygame.Rect(0, 0, screen_width, screen_height) # Ukuran kamera = ukuran layar
        self.world_width = world_width    # Lebar total dunia/peta
        self.world_height = world_height  # Tinggi total dunia/peta
        self.screen_width = screen_width  # Lebar layar game
        self.screen_height = screen_height # Tinggi layar game
        
        # Menyimpan offset x dan y untuk kemudahan
        self.offset_x = 0
        self.offset_y = 0
        print(f"--- Camera: Diinisialisasi dengan dunia {world_width}x{world_height}, layar {screen_width}x{screen_height} ---")


    def apply(self, target_entity_or_rect):
        """
        Menerapkan offset kamera ke sebuah Rect atau sprite (yang memiliki atribut .rect).
        Mengembalikan Rect baru yang sudah digeser untuk digambar di layar.
        """
        if isinstance(target_entity_or_rect, pygame.Rect):
            return target_entity_or_rect.move(self.offset_x, self.offset_y)
        elif hasattr(target_entity_or_rect, 'rect'): # Jika objek punya atribut rect
            return target_entity_or_rect.rect.move(self.offset_x, self.offset_y)
        else:
            # Jika bukan Rect atau objek dengan .rect, kembalikan apa adanya (atau handle error)
            print("--- Camera WARN: apply() menerima target yang bukan Rect atau punya .rect ---")
            return target_entity_or_rect


    def apply_to_point(self, point_x, point_y):
        """
        Menerapkan offset kamera ke sebuah titik (x,y) dalam koordinat dunia.
        Mengembalikan tuple (screen_x, screen_y).
        """
        return (point_x + self.offset_x, point_y + self.offset_y)

    def update(self, target_focus_rect):
        """
        Memperbarui posisi kamera agar target_focus_rect (biasanya rect pemain)
        berada di tengah layar, dengan batasan agar kamera tidak keluar dari dunia.
        Target_focus_rect adalah Rect dalam koordinat dunia.
        """
        # Hitung posisi ideal kamera agar target berada di tengah layar
        # Offset adalah seberapa banyak dunia perlu digeser agar target di tengah
        # Jika target_focus_rect.centerx adalah 500 dan layar/2 adalah 640, maka x = 140.
        # Artinya dunia digeser 140px ke kanan, sehingga objek di 500px akan terlihat di 640px.
        self.offset_x = -target_focus_rect.centerx + self.screen_width // 2
        self.offset_y = -target_focus_rect.centery + self.screen_height // 2

        # Batasi offset agar kamera tidak menampilkan area di luar dunia game
        # Batas kiri: offset_x tidak boleh lebih dari 0 (dunia tidak bisa digeser ke kanan melebihi batas kirinya)
        self.offset_x = min(0, self.offset_x)
        # Batas atas: offset_y tidak boleh lebih dari 0
        self.offset_y = min(0, self.offset_y)

        # Batas kanan: offset_x tidak boleh kurang dari -(lebar_dunia - lebar_layar)
        # Ini berarti sudut kanan kamera tidak melebihi sudut kanan dunia
        if self.world_width > self.screen_width: # Hanya batasi jika dunia lebih lebar dari layar
            self.offset_x = max(-(self.world_width - self.screen_width), self.offset_x)
        else: # Jika dunia lebih sempit, kamera selalu di 0
            self.offset_x = 0 
            
        # Batas bawah: offset_y tidak boleh kurang dari -(tinggi_dunia - tinggi_layar)
        if self.world_height > self.screen_height: # Hanya batasi jika dunia lebih tinggi dari layar
            self.offset_y = max(-(self.world_height - self.screen_height), self.offset_y)
        else: # Jika dunia lebih pendek, kamera selalu di 0
            self.offset_y = 0
            
        # Update camera_rect (representasi viewport kamera di dunia)
        # Posisi topleft kamera di dunia adalah (-offset_x, -offset_y)
        self.camera_rect.topleft = (-self.offset_x, -self.offset_y)
        # print(f"--- Camera Update: Target Center=({target_focus_rect.centerx},{target_focus_rect.centery}), Offset=({self.offset_x},{self.offset_y}), CamRect=({self.camera_rect.x},{self.camera_rect.y}) ---")
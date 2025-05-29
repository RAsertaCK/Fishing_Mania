# market.py
class Market: # Pastikan kelas ini terdefinisi dengan nama Market
    def __init__(self, game_instance): 
        self.game = game_instance 
        print("--- Market: Market (logic) instance DIBUAT untuk IMPROVE. ---")

    def sell_fish(self, fish_object_or_data):
        value = 0
        fish_name_to_remove = "Ikan Tak Dikenal" 

        if isinstance(fish_object_or_data, dict):
            value = fish_object_or_data.get('value', 0)
            fish_name_to_remove = fish_object_or_data.get('name', fish_name_to_remove)
        elif hasattr(fish_object_or_data, 'value'): 
            value = fish_object_or_data.value
            if hasattr(fish_object_or_data, 'name'):
                 fish_name_to_remove = fish_object_or_data.name
        
        if value > 0:
            self.game.wallet += value
            # print(f"    Ikan '{fish_name_to_remove}' terjual seharga {value}. Koin sekarang: {self.game.wallet}")
            
            # Logika untuk menghapus ikan dari inventaris (disederhanakan)
            if self.game.inventory and hasattr(self.game.inventory, 'fish_list'):
                # Cara sederhana: coba hapus berdasarkan objek jika bukan dict, atau cari berdasarkan nama jika dict
                # Ini mungkin perlu disempurnakan tergantung bagaimana Anda menyimpan ikan di inventaris
                try:
                    if fish_object_or_data in self.game.inventory.fish_list:
                         self.game.inventory.fish_list.remove(fish_object_or_data)
                except (TypeError, ValueError): # TypeError jika fish_object_or_data tidak hashable (seperti dict)
                    # Jika error atau bukan objek yang bisa langsung dihapus, coba cara lain jika perlu
                    pass # Untuk sekarang, biarkan saja jika tidak mudah dihapus
            return value
        return 0

    def sell_all_fish_from_inventory(self):
        if not self.game.inventory or not hasattr(self.game.inventory, 'fish_list') or not self.game.inventory.fish_list:
            return 0
        
        total_sold_value = 0
        # Penting: Iterasi pada salinan jika Anda memodifikasi list saat iterasi.
        # Namun, karena kita akan clear() pada akhirnya, kita bisa hitung dulu.
        for fish_data_or_obj in list(self.game.inventory.fish_list): # Iterasi pada salinan
            value = 0
            if isinstance(fish_data_or_obj, dict):
                value = fish_data_or_obj.get('value', 0)
            elif hasattr(fish_data_or_obj, 'value'):
                value = fish_data_or_obj.value
            total_sold_value += value
        
        if total_sold_value > 0:
            self.game.wallet += total_sold_value
            num_fish_sold = len(self.game.inventory.fish_list)
            self.game.inventory.fish_list.clear() 
            print(f"--- Market: Semua {num_fish_sold} ikan terjual. Total nilai: {total_sold_value}. Koin sekarang: {self.game.wallet} ---")
        else:
            print("--- Market: Tidak ada ikan bernilai di inventaris untuk dijual. ---")
            
        return total_sold_value
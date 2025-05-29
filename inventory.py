# inventory.py
class Inventory:
    def __init__(self, game_instance):
        self.fish_list = []
        self.game = game_instance

    def add(self, fish):
        self.fish_list.append(fish)

    # Metode ini mungkin tidak digunakan jika game menggunakan add_fish_from_data
    def add_fish_from_data(self, fish_data):
        # Asumsi fish_data adalah dictionary seperti yang ada di GameMap.LOCATIONS
        # Kita perlu membuat instance Fish dari data ini
        from fish import Fish # Impor di sini untuk menghindari circular dependency
        # Posisi dummy (0,0) karena ikan di inventaris tidak dirender di dunia
        new_fish = Fish(fish_data, (0,0), self.game.config) # <--- PERBAIKAN: Tambahkan self.game.config
        self.fish_list.append(new_fish)

    def get_summary(self):
        summary = {}
        for fish in self.fish_list:
            key = f"{fish.name} ({fish.rarity})"
            summary[key] = summary.get(key, 0) + 1
        return summary

    def sell_all(self):
        total = sum(f.value for f in self.fish_list)
        self.fish_list.clear()
        return total

    def render(self, screen, font):
        screen.blit(font.render("Inventory:", True, (255, 255, 255)), (10, 100))
        for i, (name, count) in enumerate(self.get_summary().items()):
            text = font.render(f"{name} x{count}", True, (200, 200, 200))
            screen.blit(text, (10, 130 + i * 25))
class Inventory:
    def __init__(self):
        self.fish_list = []

    def add(self, fish):
        self.fish_list.append(fish)

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
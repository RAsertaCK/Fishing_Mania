class Config:
    WHITE = (255, 255, 255)  # Define the color white as an RGB tuple

class Collection:
    def __init__(self):
        self.caught = []
        self.fish_value = {
            "common": 10,
            "rare": 30,
            "legendary": 100
        }

    def add_fish(self, fish):
        self.caught.append((fish.kind, fish.rarity))
        return self.fish_value.get(fish.rarity, 0)

    def get_count(self, kind=None, rarity=None):
        if kind and rarity:
            return sum(1 for f in self.caught if f[0] == kind and f[1] == rarity)
        elif kind:
            return sum(1 for f in self.caught if f[0] == kind)
        elif rarity:
            return sum(1 for f in self.caught if f[1] == rarity)
        return len(self.caught)

    def render(self, screen, font):
        for i, fish in enumerate(self.caught[:10]):  # Show last 10 caught
            text = font.render(f"{fish[0]} ({fish[1]})", True, Config.WHITE)
            screen.blit(text, (10, 100 + i * 30))
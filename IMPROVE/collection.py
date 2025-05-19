class Collection:
    def __init__(self):
        self.caught = []
        self.fish_value = {
            "common": 10,
            "rare": 30,
            "legendary": 100
        }

    def add_fish(self, fish):
        self.caught.append((fish.name, fish.rarity))
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
        screen.blit(font.render("Fish Collection:", True, (255, 255, 255)), (10, 100))
        for i, (name, rarity) in enumerate(self.caught[-10:]):  # last 10 caught
            text = font.render(f"{name} ({rarity})", True, (200, 200, 200))
            screen.blit(text, (10, 130 + i * 25))
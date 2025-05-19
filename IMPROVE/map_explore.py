import pygame

class MapExplorer:
    def __init__(self):
        self.bg_color = (50, 120, 200)
        self.player_pos = [100, 100]
        self.player_speed = 200
        self.player_size = 32

        self.font = pygame.font.SysFont(None, 28)
        self.spot_rects = [
            pygame.Rect(400, 150, 50, 50),
            pygame.Rect(700, 400, 50, 50),
            pygame.Rect(200, 500, 50, 50),
        ]
        self.spot_names = ["Coast", "Sea", "Ocean"]
        self.trigger_zone = None

    def update(self, dt, keys):
        if keys[pygame.K_LEFT]: self.player_pos[0] -= self.player_speed * dt
        if keys[pygame.K_RIGHT]: self.player_pos[0] += self.player_speed * dt
        if keys[pygame.K_UP]: self.player_pos[1] -= self.player_speed * dt
        if keys[pygame.K_DOWN]: self.player_pos[1] += self.player_speed * dt

        player_rect = pygame.Rect(self.player_pos[0], self.player_pos[1], self.player_size, self.player_size)
        self.trigger_zone = None
        for i, spot in enumerate(self.spot_rects):
            if player_rect.colliderect(spot):
                self.trigger_zone = self.spot_names[i]

    def render(self, screen):
        screen.fill(self.bg_color)
        for i, rect in enumerate(self.spot_rects):
            pygame.draw.rect(screen, (0, 255, 100), rect)
            label = self.font.render(self.spot_names[i], True, (255, 255, 255))
            screen.blit(label, (rect.x, rect.y - 25))

        pygame.draw.rect(screen, (255, 255, 0), (*self.player_pos, self.player_size, self.player_size))

        if self.trigger_zone:
            msg = f"Press ENTER to fish at {self.trigger_zone}"
            text = self.font.render(msg, True, (255, 255, 255))
            screen.blit(text, (self.player_pos[0] - 50, self.player_pos[1] - 40))

    def get_selected_location(self):
        return self.trigger_zone

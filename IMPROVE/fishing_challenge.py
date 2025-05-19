import pygame
import random

class FishingSkillChallenge:
    def __init__(self):
        self.result = None
        self.timer = 0
        self.duration = 3000  # ms
        self.challenge_active = False

    def start(self):
        self.challenge_active = True
        self.timer = pygame.time.get_ticks()
        self.result = None

    def update(self):
        if not self.challenge_active:
            return
        current = pygame.time.get_ticks()
        if current - self.timer >= self.duration:
            if pygame.key.get_pressed()[pygame.K_SPACE]:
                self.result = "caught"
            else:
                self.result = "failed"
            self.challenge_active = False

    def render(self, screen):
        if not self.challenge_active:
            return
        font = pygame.font.SysFont(None, 48)
        text = font.render("TEKAN SPACE!", True, (255, 0, 0))
        rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        screen.blit(text, rect)

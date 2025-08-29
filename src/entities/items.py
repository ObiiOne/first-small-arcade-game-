import pygame
from src.constants import *

class Medkit:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, MEDKIT_SIZE, MEDKIT_SIZE)
        self.spawn_time = pygame.time.get_ticks()

    def is_expired(self):
        elapsed = pygame.time.get_ticks() - self.spawn_time
        return elapsed > MEDKIT_LIFETIME

    def color(self):
        elapsed = pygame.time.get_ticks() - self.spawn_time
        if elapsed > MEDKIT_LIFETIME - 2000:
            return YELLOW if (pygame.time.get_ticks() // 250) % 2 == 0 else GREEN
        return YELLOW


class StaminaBooster:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, STAMINA_BOOSTER_SIZE, STAMINA_BOOSTER_SIZE)
        self.spawn_time = pygame.time.get_ticks()

    def is_expired(self):
        elapsed = pygame.time.get_ticks() - self.spawn_time
        return elapsed > STAMINA_BOOSTER_LIFETIME

    def color(self):
        elapsed = pygame.time.get_ticks() - self.spawn_time
        if elapsed > STAMINA_BOOSTER_LIFETIME - 2000:
            return WHITE if (pygame.time.get_ticks() // 250) % 2 == 0 else YELLOW
        return YELLOW

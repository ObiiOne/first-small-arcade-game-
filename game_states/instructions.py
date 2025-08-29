import pygame
import sys
from src.constants import *


def draw_instructions(screen):
    screen.fill(BLACK)
    font = pygame.font.SysFont('arial', 24)
    lines = [
        "Двигай стрелками",
        "Бейся пробелом",
        "Собирай аптечки чтобы лечиться",
        "Собирай бустеры чтобы драться",
        "Помни, выносливость конечна",
        "Бей врагов в ближнем бою",
        "Уворачивайся от пуль",
        "Выживай и копи очки",
        "***",
        "Нажмите ESC для возврата в меню"
    ]

    for i, line in enumerate(lines):
        text = font.render(line, True, WHITE)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 4 + i * 40))

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    waiting = False

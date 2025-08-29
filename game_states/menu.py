import pygame
from src.constants import *


def draw_main_menu(screen):
    screen.fill(BLACK)
    font = pygame.font.SysFont('arial', 36)
    title_text = font.render("NOMAD", True, WHITE)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 4))

    play_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 50)
    instructions_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50)

    pygame.draw.rect(screen, WHITE, play_button)
    pygame.draw.rect(screen, WHITE, instructions_button)
    play_text = pygame.font.SysFont(None, 36).render("Новая игра", True, BLACK)
    instructions_text = pygame.font.SysFont(None, 36).render("Как играть", True, BLACK)
    screen.blit(play_text,
                (play_button.centerx - play_text.get_width() // 2, play_button.centery - play_text.get_height() // 2))
    screen.blit(instructions_text, (instructions_button.centerx - instructions_text.get_width() // 2,
                                    instructions_button.centery - instructions_text.get_height() // 2))

    return play_button, instructions_button

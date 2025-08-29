import pygame
import sys
from src.constants import *


def show_game_over_screen(screen, score):
    screen.fill(BLACK)
    font = pygame.font.SysFont('arial', 36)
    game_over_text = font.render(f"Wasted. Score: {score}", True, WHITE)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 100))

    menu_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 50)
    pygame.draw.rect(screen, YELLOW, menu_button)
    menu_text = font.render("Main Menu", True, BLACK)
    screen.blit(menu_text,
                (menu_button.centerx - menu_text.get_width() // 2, menu_button.centery - menu_text.get_height() // 2))

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if menu_button.collidepoint(event.pos):
                    waiting = False

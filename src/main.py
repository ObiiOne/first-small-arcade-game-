import pygame
import sys
import random
from constants import *
from game_states.menu import draw_main_menu
from game_states.instructions import draw_instructions
from game_states.game_over import show_game_over_screen
from game_states.playing import playing_state
from src.entities.enemies import Enemy, RangedEnemy
from utils.spawners import create_random_enemy, create_random_ranged_enemy


def init_game():
    player = pygame.Rect(WIDTH // 2, HEIGHT // 2, PLAYER_SIZE, PLAYER_SIZE)
    player_lives = 3
    player_stamina = 100
    score = 0

    enemies = []
    ranged_enemies = []
    bullets = []

    # Создаем обычных врагов
    for _ in range(2):
        enemy = create_random_enemy(enemies)
        if enemy:
            enemies.append(enemy)

    # Создаем стреляющих врагов
    for _ in range(1):
        ranged_enemy = create_random_ranged_enemy(ranged_enemies)
        if ranged_enemy:
            ranged_enemies.append(ranged_enemy)

    medkits = []
    stamina_boosters = []
    last_medkit_spawn = pygame.time.get_ticks()
    last_stamina_booster_spawn = pygame.time.get_ticks()
    game_start_time = pygame.time.get_ticks()

    return {
        'player': player,
        'player_lives': player_lives,
        'player_stamina': player_stamina,
        'score': score,
        'enemies': enemies,
        'ranged_enemies': ranged_enemies,
        'medkits': medkits,
        'stamina_boosters': stamina_boosters,
        'bullets': bullets,
        'attack_timer': 0,
        'last_death_time': 0,
        'last_medkit_spawn': last_medkit_spawn,
        'last_stamina_booster_spawn': last_stamina_booster_spawn,
        'game_start_time': game_start_time,
        'space_pressed': False,
        'MEDKIT_SPAWN_INTERVAL': random.randint(3000, 7000),
        'STAMINA_BOOSTER_SPAWN_INTERVAL': random.randint(3000, 7000)
    }


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("NOMAD")

    clock = pygame.time.Clock()
    running = True
    game_state = MENU
    game_data = init_game()
    space_pressed = False

    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Обработка ESC для перехода в главное меню
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_state != MENU:
                        game_state = MENU
                        game_data = init_game()

            if game_state == MENU:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    play_button, instructions_button = draw_main_menu(screen)
                    if play_button.collidepoint(event.pos):
                        game_data = init_game()
                        game_state = PLAYING
                    elif instructions_button.collidepoint(event.pos):
                        game_state = INSTRUCTIONS

            elif game_state == PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        game_data['space_pressed'] = True
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        game_data['space_pressed'] = False

        if game_state == MENU:
            draw_main_menu(screen)
            pygame.display.flip()

        elif game_state == INSTRUCTIONS:
            draw_instructions(screen)
            game_state = MENU

        elif game_state == PLAYING:
            game_state = playing_state(screen, game_data, clock)
            pygame.display.flip()

        elif game_state == GAME_OVER:
            show_game_over_screen(screen, game_data['score'])
            game_state = MENU

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

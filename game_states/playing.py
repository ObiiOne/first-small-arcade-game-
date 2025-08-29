import pygame
import random
from src.constants import *
from src.entities.items import Medkit, StaminaBooster
from utils.collisions import attack_enemy, update_bullets
from utils.spawners import spawn_enemy_timer


def playing_state(screen, game_data, clock):
    player = game_data['player']
    player_lives = game_data['player_lives']
    player_stamina = game_data['player_stamina']
    score = game_data['score']
    enemies = game_data['enemies']
    ranged_enemies = game_data['ranged_enemies']
    medkits = game_data['medkits']
    stamina_boosters = game_data['stamina_boosters']
    bullets = game_data['bullets']
    attack_timer = game_data['attack_timer']
    last_death_time = game_data['last_death_time']
    last_medkit_spawn = game_data['last_medkit_spawn']
    last_stamina_booster_spawn = game_data['last_stamina_booster_spawn']
    game_start_time = game_data['game_start_time']
    space_pressed = game_data['space_pressed']

    now = pygame.time.get_ticks()

    # Движение игрока
    keys = pygame.key.get_pressed()
    dx = dy = 0
    if keys[pygame.K_LEFT]:
        dx = -PLAYER_SPEED
    if keys[pygame.K_RIGHT]:
        dx = PLAYER_SPEED
    if keys[pygame.K_UP]:
        dy = -PLAYER_SPEED
    if keys[pygame.K_DOWN]:
        dy = PLAYER_SPEED

    from utils.collisions import can_move
    if can_move(player, dx, 0, OBSTACLES):
        player.x += dx
    if can_move(player, 0, dy, OBSTACLES):
        player.y += dy

    player.x = max(0, min(player.x, WIDTH - PLAYER_SIZE))
    player.y = max(0, min(player.y, HEIGHT - PLAYER_SIZE))

    # Трата выносливости со временем (1/120 за кадр)
    player_stamina -= 1 / 120
    if player_stamina < 0:
        player_stamina = 0

    # Обновляем обычных врагов
    for enemy in enemies[:]:
        other_enemies = [e for e in enemies if e != enemy] + ranged_enemies
        enemy.update(player, OBSTACLES, other_enemies, game_start_time)
        if enemy.rect.colliderect(player):
            player_lives -= 1
            enemies.remove(enemy)
            last_death_time = pygame.time.get_ticks()
            if player_lives <= 0:
                return GAME_OVER

    # Обновляем стреляющих врагов
    for enemy in ranged_enemies[:]:
        other_enemies = enemies + [e for e in ranged_enemies if e != enemy]
        enemy.update(player, OBSTACLES, other_enemies, bullets, game_start_time)
        if enemy.rect.colliderect(player):
            player_lives -= 1
            ranged_enemies.remove(enemy)
            last_death_time = pygame.time.get_ticks()
            if player_lives <= 0:
                return GAME_OVER

    # Обновляем пули и проверяем столкновения
    player_hit = update_bullets(bullets, player, enemies, ranged_enemies, medkits, stamina_boosters, OBSTACLES)
    if player_hit:
        player_lives -= 1
        if player_lives <= 0:
            return GAME_OVER

    # Проверка удара
    if space_pressed and player_stamina >= 5:
        if attack_timer == 0 or pygame.time.get_ticks() - attack_timer >= 10:
            player_stamina -= 5
            attack_timer = pygame.time.get_ticks()
            hit, points = attack_enemy(player, enemies, ranged_enemies)
            if hit:
                score += points
            space_pressed = False

    # Генерация врагов через 3 секунды после смерти
    last_death_time = spawn_enemy_timer(last_death_time, enemies, ranged_enemies)

    # Спавн аптечки
    if now - last_medkit_spawn > game_data['MEDKIT_SPAWN_INTERVAL'] and len(medkits) == 0:
        while True:
            x = random.randint(0, WIDTH - MEDKIT_SIZE)
            y = random.randint(0, HEIGHT - MEDKIT_SIZE)
            new_rect = pygame.Rect(x, y, MEDKIT_SIZE, MEDKIT_SIZE)
            if not any(new_rect.colliderect(wall) for wall in OBSTACLES):
                medkits.append(Medkit(x, y))
                last_medkit_spawn = now
                game_data['MEDKIT_SPAWN_INTERVAL'] = random.randint(3000, 7000)
                break

    # Проверка аптечек
    for medkit in medkits[:]:
        if player.colliderect(medkit.rect):
            player_lives = min(3, player_lives + 1)
            medkits.remove(medkit)
        elif medkit.is_expired():
            medkits.remove(medkit)

    # Спавн бустеров
    if now - last_stamina_booster_spawn > game_data['STAMINA_BOOSTER_SPAWN_INTERVAL'] and len(stamina_boosters) == 0:
        while True:
            x = random.randint(0, WIDTH - STAMINA_BOOSTER_SIZE)
            y = random.randint(0, HEIGHT - STAMINA_BOOSTER_SIZE)
            new_rect = pygame.Rect(x, y, STAMINA_BOOSTER_SIZE, STAMINA_BOOSTER_SIZE)
            if not any(new_rect.colliderect(wall) for wall in OBSTACLES):
                stamina_boosters.append(StaminaBooster(x, y))
                last_stamina_booster_spawn = now
                game_data['STAMINA_BOOSTER_SPAWN_INTERVAL'] = random.randint(3000, 7000)
                break

    # Проверка бустеров
    for stamina_booster in stamina_boosters[:]:
        if player.colliderect(stamina_booster.rect):
            player_stamina = min(MAX_STAMINA, player_stamina + 33)
            stamina_boosters.remove(stamina_booster)
        elif stamina_booster.is_expired():
            stamina_boosters.remove(stamina_booster)

    # Определяем цвет игрока
    if player_lives == 3:
        player_color = WHITE
    elif player_lives == 2:
        player_color = LIGHT_GRAY
    elif player_lives == 1:
        player_color = DARK_GRAY
    else:
        player_color = BLACK

    # Рисуем всё
    screen.fill(GREEN)

    # Рисуем препятствия
    for wall in OBSTACLES:
        pygame.draw.rect(screen, RED, wall)

    # Рисуем обычных врагов
    for enemy in enemies:
        enemy_color = enemy.get_color()
        if enemy_color:
            pygame.draw.rect(screen, enemy_color, enemy.rect)

    # Рисуем стреляющих врагов (круги)
    for enemy in ranged_enemies:
        enemy_color = enemy.get_color()
        if enemy_color:
            pygame.draw.circle(screen, enemy_color, enemy.rect.center, RANGED_ENEMY_SIZE // 2)

    # Рисуем аптечки
    for medkit in medkits:
        pygame.draw.rect(screen, medkit.color(), medkit.rect)

    # Рисуем бустеры выносливости (желтые круги)
    for stamina_booster in stamina_boosters:
        pygame.draw.circle(screen, stamina_booster.color(), stamina_booster.rect.center, STAMINA_BOOSTER_SIZE // 2)

    # Рисуем пули
    for bullet in bullets:
        pygame.draw.circle(screen, RED, bullet['rect'].center, BULLET_SIZE // 2)

    # Рисуем игрока
    pygame.draw.rect(screen, player_color, player)

    # Рисуем радиус атаки
    if keys[pygame.K_SPACE]:
        attack_radius = 1.5 * PLAYER_SIZE
        if player_stamina >= 5:
            # Нормальный цвет при достаточной выносливости
            pygame.draw.circle(screen, WHITE, player.center, attack_radius, 3)
        else:
            # Красный цвет при недостаточной выносливости
            pygame.draw.circle(screen, RED, player.center, attack_radius, 3)

    # Рисуем счет
    font = pygame.font.SysFont('arial', 36)
    score_text = font.render(f"Score: {score}", True, YELLOW)
    screen.blit(score_text, (20, 20))

    # Рисуем жизни
    lives_text = font.render(f"Lives: {player_lives}", True, YELLOW)
    screen.blit(lives_text, (WIDTH - 150, 20))

    # Рисуем стамину (целое число вверху посередине)
    stamina_text = font.render(f"Stamina:{int(player_stamina)}", True, YELLOW)
    screen.blit(stamina_text, (WIDTH // 2 - stamina_text.get_width() // 2, 20))

    # Отображаем обратный отсчет до начала движения врагов
    if pygame.time.get_ticks() - game_start_time < 1000:
        countdown = (1000 - (pygame.time.get_ticks() - game_start_time)) // 1000 + 1
        countdown_text = font.render(f"Start in: {countdown}", True, BLACK)
        screen.blit(countdown_text, (WIDTH // 2 - countdown_text.get_width() // 2, HEIGHT // 2))

    # Обновляем game_data
    game_data.update({
        'player_lives': player_lives,
        'player_stamina': player_stamina,
        'score': score,
        'enemies': enemies,
        'ranged_enemies': ranged_enemies,
        'medkits': medkits,
        'stamina_boosters': stamina_boosters,
        'bullets': bullets,
        'attack_timer': attack_timer,
        'last_death_time': last_death_time,
        'last_medkit_spawn': last_medkit_spawn,
        'last_stamina_booster_spawn': last_stamina_booster_spawn,
        'space_pressed': space_pressed
    })

    return PLAYING
import random
from src.entities.enemies import Enemy, RangedEnemy
from utils.collisions import can_spawn
from src.constants import *


def create_random_enemy(existing_enemies):
    attempts = 0
    while attempts < 50:
        attempts += 1
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            x = random.randint(70, WIDTH - 70 - ENEMY_SIZE)
            y = 70
        elif side == 'bottom':
            x = random.randint(70, WIDTH - 70 - ENEMY_SIZE)
            y = HEIGHT - 70 - ENEMY_SIZE
        elif side == 'left':
            x = 70
            y = random.randint(70, HEIGHT - 70 - ENEMY_SIZE)
        else:
            x = WIDTH - 70 - ENEMY_SIZE
            y = random.randint(70, HEIGHT - 70 - ENEMY_SIZE)

        new_enemy = pygame.Rect(x, y, ENEMY_SIZE, ENEMY_SIZE)

        if (not any(new_enemy.colliderect(w) for w in OBSTACLES) and
                can_spawn(new_enemy, existing_enemies, 100)):
            return Enemy(new_enemy)

    return None


def create_random_ranged_enemy(existing_enemies):
    attempts = 0
    while attempts < 50:
        attempts += 1
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            x = random.randint(70, WIDTH - 70 - RANGED_ENEMY_SIZE)
            y = 70
        elif side == 'bottom':
            x = random.randint(70, WIDTH - 70 - RANGED_ENEMY_SIZE)
            y = HEIGHT - 70 - RANGED_ENEMY_SIZE
        elif side == 'left':
            x = 70
            y = random.randint(70, HEIGHT - 70 - RANGED_ENEMY_SIZE)
        else:
            x = WIDTH - 70 - RANGED_ENEMY_SIZE
            y = random.randint(70, HEIGHT - 70 - RANGED_ENEMY_SIZE)

        new_enemy = pygame.Rect(x, y, RANGED_ENEMY_SIZE, RANGED_ENEMY_SIZE)

        if (not any(new_enemy.colliderect(w) for w in OBSTACLES) and
                can_spawn(new_enemy, existing_enemies, 100)):
            return RangedEnemy(new_enemy)

    return None


def spawn_enemy_timer(last_death_time, enemies, ranged_enemies):
    if pygame.time.get_ticks() - last_death_time >= 3000:
        if random.random() < 0.7:
            enemy = create_random_enemy(enemies)
            if enemy:
                enemies.append(enemy)
        else:
            ranged_enemy = create_random_ranged_enemy(ranged_enemies)
            if ranged_enemy:
                ranged_enemies.append(ranged_enemy)
        return pygame.time.get_ticks()
    return last_death_time

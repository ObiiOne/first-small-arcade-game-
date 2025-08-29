# import pygame
# import sys
# import random
# import math
# import os
#
# pygame.init()
#
# # Настройки окна
# WIDTH, HEIGHT = 800, 600
# screen = pygame.display.set_mode((WIDTH, HEIGHT))
# pygame.display.set_caption("NOMAD")
#
# # Размеры
# PLAYER_SIZE = 50
# ENEMY_SIZE = 50
# MEDKIT_SIZE = 20
# RANGED_ENEMY_SIZE = 50  # Размер стреляющего врага
# BULLET_SIZE = 4  # Размер пули
#
# # Скорости
# PLAYER_SPEED = 3
# ENEMY_SPEED = 5
# BULLET_SPEED = 7  # Скорость пули
# PATROL_CHANGE_INTERVAL = 60  # кадров между сменой направления патруля
#
# # Цвета
# WHITE = (255, 255, 255)
# LIGHT_GRAY = (200, 200, 200)
# DARK_GRAY = (100, 100, 100)
# BLACK = (0, 0, 0)
# BLUE = (0, 0, 255)
# RED = (255, 0, 0)
# GREEN = (25, 130, 20)
# BRIGHT_GREEN = (0, 255, 0)  # Ярко-зеленый для пуль
# YELLOW = (255, 255, 0)
# PURPLE = (128, 0, 128)
#
# # Состояния игры
# MENU = 0
# PLAYING = 1
# GAME_OVER = 2
# INSTRUCTIONS = 3
#
# # Инициализация состояния игры
# game_state = MENU
#
# # Игрок
# player = pygame.Rect(WIDTH // 2, HEIGHT // 2, PLAYER_SIZE, PLAYER_SIZE)
# player_lives = 3
# score = 0  # счет
#
# # Препятствия (будут сгенерированы процедурно)
# #obstacles = []
# # Препятствия
#
# obstacles = [
#     pygame.Rect(70, 70, 150, 20),
#     pygame.Rect(70, 70, 20, 150),
#     pygame.Rect(70, 350, 20, 150),
#     pygame.Rect(70, 500, 150, 20),
#     pygame.Rect(220, 70, 20, 150),
#     pygame.Rect(300, 500, 300, 20),
#     pygame.Rect(300, 400, 300, 20),
#     pygame.Rect(400, 70, 100, 20),
#     pygame.Rect(400, 200, 20, 100),
#     pygame.Rect(700, 150, 20, 300),
# ]
#
# # Враги, аптечки и пули
# enemies = []
# ranged_enemies = []  # Новый список для стреляющих врагов
# medkits = []
# bullets = []  # Список для пуль
#
# # Таймеры
# attack_timer = 0
# last_death_time = 0
# last_medkit_spawn = pygame.time.get_ticks()
# last_bullet_spawn = pygame.time.get_ticks()
# BULLET_SPAWN_INTERVAL = 2000  # Интервал между выстрелами (мс)
# MEDKIT_SPAWN_INTERVAL = 10000
# MEDKIT_LIFETIME = 10000
#
#
# # # Функция для процедурной генерации препятствий
# # def generate_obstacles(num_obstacles, min_size=30, max_size=100, min_distance=70, player_padding=100):
# #     obstacles = []
# #     player_rect = pygame.Rect(WIDTH // 2 - player_padding // 2,
# #                               HEIGHT // 2 - player_padding // 2,
# #                               player_padding, player_padding)
# #
# #     for _ in range(num_obstacles):
# #         attempts = 0
# #         placed = False
# #
# #         while not placed and attempts < 100:  # Ограничим количество попыток
# #             attempts += 1
# #
# #             # Выбираем случайный тип препятствия
# #             obstacle_type = random.choice(["rectangle", "line_h", "line_v"])
# #
# #             if obstacle_type == "rectangle":
# #                 width = random.randint(min_size, max_size)
# #                 height = random.randint(min_size, max_size)
# #                 x = random.randint(min_distance, WIDTH - width - min_distance)
# #                 y = random.randint(min_distance, HEIGHT - height - min_distance)
# #                 new_obstacle = pygame.Rect(x, y, width, height)
# #
# #             elif obstacle_type == "line_h":  # Горизонтальная линия
# #                 width = random.randint(min_size * 2, max_size * 3)
# #                 height = random.randint(10, 20)
# #                 x = random.randint(min_distance, WIDTH - width - min_distance)
# #                 y = random.randint(min_distance, HEIGHT - height - min_distance)
# #                 new_obstacle = pygame.Rect(x, y, width, height)
# #
# #             else:  # Вертикальная линия
# #                 width = random.randint(10, 20)
# #                 height = random.randint(min_size * 2, max_size * 3)
# #                 x = random.randint(min_distance, WIDTH - width - min_distance)
# #                 y = random.randint(min_distance, HEIGHT - height - min_distance)
# #                 new_obstacle = pygame.Rect(x, y, width, height)
# #
# #             # Проверяем условия размещения
# #             valid_placement = True
# #
# #             # Не слишком близко к краям
# #             if (x < min_distance or y < min_distance or
# #                     x + width > WIDTH - min_distance or
# #                     y + height > HEIGHT - min_distance):
# #                 valid_placement = False
# #
# #             # Не слишком близко к игроку
# #             if new_obstacle.colliderect(player_rect):
# #                 valid_placement = False
# #
# #             # Не пересекается с другими препятствиями
# #             for obstacle in obstacles:
# #                 if new_obstacle.colliderect(obstacle):
# #                     valid_placement = False
# #                     break
# #
# #             # Проверяем, не блокирует ли препятствие проходы
# #             if valid_placement and not is_path_clear(obstacles + [new_obstacle]):
# #                 valid_placement = False
# #
# #             if valid_placement:
# #                 obstacles.append(new_obstacle)
# #                 placed = True
# #
# #     return obstacles
# #
# #
# # # Функция проверки проходимости уровня
# # def is_path_clear(obstacles, sample_points=20):
# #     """
# #     Проверяет, есть ли достаточное количество свободных путей на карте
# #     """
# #     free_paths = 0
# #
# #     for _ in range(sample_points):
# #         # Выбираем случайные точки на карте
# #         start_x = random.randint(70, WIDTH - 70)
# #         start_y = random.randint(70, HEIGHT - 70)
# #         end_x = random.randint(70, WIDTH - 70)
# #         end_y = random.randint(70, HEIGHT - 70)
# #
# #         # Создаем временный прямоугольник для проверки пути
# #         temp_rect = pygame.Rect(start_x, start_y, 10, 10)
# #
# #         # Проверяем, не заблокирован ли путь препятствиями
# #         path_clear = True
# #         steps = 50  # Количество проверок вдоль пути
# #         for i in range(steps + 1):
# #             check_x = start_x + (end_x - start_x) * i / steps
# #             check_y = start_y + (end_y - start_y) * i / steps
# #             temp_rect.center = (check_x, check_y)
# #
# #             for obstacle in obstacles:
# #                 if temp_rect.colliderect(obstacle):
# #                     path_clear = False
# #                     break
# #
# #             if not path_clear:
# #                 break
# #
# #         if path_clear:
# #             free_paths += 1
# #
# #     # Считаем уровень проходимым, если достаточно свободных путей
# #     return free_paths >= sample_points * 0.6  # 60% путей должны быть свободны
#
#
# # Проверка столкновений
# def can_move(rect, dx, dy, obstacles, other_enemies=[]):
#     new_rect = rect.move(dx, dy)
#     for wall in obstacles:
#         if new_rect.colliderect(wall):
#             return False
#     for e in other_enemies:
#         if new_rect.colliderect(e.rect):
#             return False
#     return True
#
#
# # Класс врага с жизнями
# class Enemy:
#     def __init__(self, rect):
#         self.rect = rect
#         self.health = 2  # 2 хп у врага
#         angle = random.uniform(0, 2 * math.pi)
#         self.dx = math.cos(angle)
#         self.dy = math.sin(angle)
#         self.mode = 'patrol'
#         self.frames = 0
#         self.last_hit_time = 0
#
#     def update(self, player, obstacles, enemies):
#         self.frames += 1
#         vector_to_player = (player.centerx - self.rect.centerx, player.centery - self.rect.centery)
#         dist = math.hypot(*vector_to_player)
#         can_see_player = False
#
#         # Проверка видимости игрока по прямой
#         steps = int(dist / 5)
#         if steps > 0:
#             step_x = vector_to_player[0] / steps
#             step_y = vector_to_player[1] / steps
#             temp_rect = self.rect.copy()
#             blocked = False
#             for _ in range(steps):
#                 temp_rect.x += step_x
#                 temp_rect.y += step_y
#                 for wall in obstacles:
#                     if temp_rect.colliderect(wall):
#                         blocked = True
#                         break
#                 if blocked:
#                     break
#             can_see_player = not blocked
#
#         self.mode = 'chase' if can_see_player else 'patrol'
#
#         move_x = move_y = 0
#
#         if self.mode == 'chase':
#             if dist != 0:
#                 dx = vector_to_player[0] / dist
#                 dy = vector_to_player[1] / dist
#                 move_x = dx * ENEMY_SPEED
#                 move_y = dy * ENEMY_SPEED
#         else:
#             move_x = self.dx * ENEMY_SPEED
#             move_y = self.dy * ENEMY_SPEED
#             if self.frames % PATROL_CHANGE_INTERVAL == 0:
#                 angle = random.uniform(0, 2 * math.pi)
#                 self.dx = math.cos(angle)
#                 self.dy = math.sin(angle)
#
#         if can_move(self.rect, move_x, move_y, obstacles, enemies):
#             self.rect.x += move_x
#             self.rect.y += move_y
#         else:
#             if self.mode == 'patrol':
#                 angle = random.uniform(0, 2 * math.pi)
#                 self.dx = math.cos(angle)
#                 self.dy = math.sin(angle)
#
#         # Ограничение границ окна
#         self.rect.x = max(0, min(self.rect.x, WIDTH - ENEMY_SIZE))
#         self.rect.y = max(0, min(self.rect.y, HEIGHT - ENEMY_SIZE))
#
#     def get_color(self):
#         # Цвет в зависимости от здоровья
#         if self.health == 2:
#             return BLUE
#         elif self.health == 1:
#             return PURPLE
#         elif self.health == 0:
#             # Враг мигает
#             elapsed = pygame.time.get_ticks() - self.last_hit_time
#             if elapsed < 1000:  # Враг мигает 1 секунду
#                 return (255, 255, 255) if (pygame.time.get_ticks() // 250) % 2 == 0 else BLUE
#             else:
#                 return None  # Враг исчезает
#
#
# # Класс стреляющего врага
# class RangedEnemy:
#     def __init__(self, rect):
#         self.rect = rect
#         self.health = 2  # 2 хп у врага
#         angle = random.uniform(0, 2 * math.pi)
#         self.dx = math.cos(angle)
#         self.dy = math.sin(angle)
#         self.mode = 'patrol'
#         self.frames = 0
#         self.last_hit_time = 0
#         self.last_shot_time = 0
#
#     def update(self, player, obstacles, enemies, bullets):
#         self.frames += 1
#         vector_to_player = (player.centerx - self.rect.centerx, player.centery - self.rect.centery)
#         dist = math.hypot(*vector_to_player)
#         can_see_player = False
#
#         # Проверка видимости игрока по прямой
#         steps = int(dist / 5)
#         if steps > 0:
#             step_x = vector_to_player[0] / steps
#             step_y = vector_to_player[1] / steps
#             temp_rect = self.rect.copy()
#             blocked = False
#             for _ in range(steps):
#                 temp_rect.x += step_x
#                 temp_rect.y += step_y
#                 for wall in obstacles:
#                     if temp_rect.colliderect(wall):
#                         blocked = True
#                         break
#                 if blocked:
#                     break
#             can_see_player = not blocked
#
#         self.mode = 'chase' if can_see_player else 'patrol'
#
#         move_x = move_y = 0
#
#         # Стреляющий враг не приближается к игроку, а держится на расстоянии
#         if self.mode == 'chase':
#             # Двигаемся в направлении, противоположном игроку
#             if dist != 0 and dist < 200:  # Если слишком близко к игроку
#                 dx = -vector_to_player[0] / dist
#                 dy = -vector_to_player[1] / dist
#                 move_x = dx * ENEMY_SPEED
#                 move_y = dy * ENEMY_SPEED
#             elif dist > 300:  # Если слишком далеко от игрока
#                 dx = vector_to_player[0] / dist
#                 dy = vector_to_player[1] / dist
#                 move_x = dx * ENEMY_SPEED
#                 move_y = dy * ENEMY_SPEED
#         else:
#             move_x = self.dx * ENEMY_SPEED
#             move_y = self.dy * ENEMY_SPEED
#             if self.frames % PATROL_CHANGE_INTERVAL == 0:
#                 angle = random.uniform(0, 2 * math.pi)
#                 self.dx = math.cos(angle)
#                 self.dy = math.sin(angle)
#
#         if can_move(self.rect, move_x, move_y, obstacles, enemies):
#             self.rect.x += move_x
#             self.rect.y += move_y
#         else:
#             if self.mode == 'patrol':
#                 angle = random.uniform(0, 2 * math.pi)
#                 self.dx = math.cos(angle)
#                 self.dy = math.sin(angle)
#
#         # Ограничение границ окна
#         self.rect.x = max(0, min(self.rect.x, WIDTH - RANGED_ENEMY_SIZE))
#         self.rect.y = max(0, min(self.rect.y, HEIGHT - RANGED_ENEMY_SIZE))
#
#         # Стрельба по игроку
#         if can_see_player and pygame.time.get_ticks() - self.last_shot_time > BULLET_SPAWN_INTERVAL:
#             self.shoot(player, bullets)
#             self.last_shot_time = pygame.time.get_ticks()
#
#     def shoot(self, player, bullets):
#         # Вычисляем направление к игроку
#         dx = player.centerx - self.rect.centerx
#         dy = player.centery - self.rect.centery
#         dist = max(0.1, math.hypot(dx, dy))  # Избегаем деления на ноль
#
#         # Нормализуем вектор
#         dx /= dist
#         dy /= dist
#
#         # Создаем пулю в позиции врага
#         bullet_rect = pygame.Rect(
#             self.rect.centerx - BULLET_SIZE // 2,
#             self.rect.centery - BULLET_SIZE // 2,
#             BULLET_SIZE, BULLET_SIZE
#         )
#
#         bullets.append({
#             'rect': bullet_rect,
#             'dx': dx * BULLET_SPEED,
#             'dy': dy * BULLET_SPEED
#         })
#
#     def get_color(self):
#         # Цвет в зависимости от здоровья
#         if self.health == 2:
#             return BLUE
#         elif self.health == 1:
#             return PURPLE
#         elif self.health == 0:
#             # Враг мигает
#             elapsed = pygame.time.get_ticks() - self.last_hit_time
#             if elapsed < 1000:  # Враг мигает 1 секунду
#                 return (255, 255, 255) if (pygame.time.get_ticks() // 250) % 2 == 0 else BLUE
#             else:
#                 return None  # Враг исчезает
#
#
# # Класс для пуль
# class Bullet:
#     def __init__(self, x, y, dx, dy):
#         self.rect = pygame.Rect(x, y, BULLET_SIZE, BULLET_SIZE)
#         self.dx = dx
#         self.dy = dy
#
#     def update(self):
#         self.rect.x += self.dx
#         self.rect.y += self.dy
#
#
# # Создание врага на случайной границе с проверкой коллизий
# def create_random_enemy(existing_enemies):
#     while True:
#         side = random.choice(['top', 'bottom', 'left', 'right'])
#         if side == 'top':
#             x = random.randint(70, WIDTH - 70 - ENEMY_SIZE)
#             y = 70
#         elif side == 'bottom':
#             x = random.randint(70, WIDTH - 70 - ENEMY_SIZE)
#             y = HEIGHT - 70 - ENEMY_SIZE
#         elif side == 'left':
#             x = 70
#             y = random.randint(70, HEIGHT - 70 - ENEMY_SIZE)
#         else:  # right
#             x = WIDTH - 70 - ENEMY_SIZE
#             y = random.randint(70, HEIGHT - 70 - ENEMY_SIZE)
#
#         new_enemy = pygame.Rect(x, y, ENEMY_SIZE, ENEMY_SIZE)
#         # проверяем столкновение с препятствиями и другими врагами
#         if not any(new_enemy.colliderect(w) for w in obstacles) and \
#                 not any(new_enemy.colliderect(e.rect) for e in existing_enemies):
#             return Enemy(new_enemy)
#
#
# # Создание стреляющего врага на случайной границе с проверкой коллизий
# def create_random_ranged_enemy(existing_enemies):
#     while True:
#         side = random.choice(['top', 'bottom', 'left', 'right'])
#         if side == 'top':
#             x = random.randint(70, WIDTH - 70 - RANGED_ENEMY_SIZE)
#             y = 70
#         elif side == 'bottom':
#             x = random.randint(70, WIDTH - 70 - RANGED_ENEMY_SIZE)
#             y = HEIGHT - 70 - RANGED_ENEMY_SIZE
#         elif side == 'left':
#             x = 70
#             y = random.randint(70, HEIGHT - 70 - RANGED_ENEMY_SIZE)
#         else:  # right
#             x = WIDTH - 70 - RANGED_ENEMY_SIZE
#             y = random.randint(70, HEIGHT - 70 - RANGED_ENEMY_SIZE)
#
#         new_enemy = pygame.Rect(x, y, RANGED_ENEMY_SIZE, RANGED_ENEMY_SIZE)
#         # проверяем столкновение с препятствиями и другими врагами
#         if not any(new_enemy.colliderect(w) for w in obstacles) and \
#                 not any(new_enemy.colliderect(e.rect) for e in existing_enemies):
#             return RangedEnemy(new_enemy)
#
#
# # Генерация начальных врагов
# def init_game():
#     global player, player_lives, score, enemies, ranged_enemies, medkits, bullets, last_medkit_spawn, obstacles, game_state
#     player = pygame.Rect(WIDTH // 2, HEIGHT // 2, PLAYER_SIZE, PLAYER_SIZE)
#     player_lives = 3
#     score = 0
#
#     # Генерируем случайные препятствия
#     # obstacles = generate_obstacles(random.randint(8, 15))  # От 8 до 15 препятствий
#
#     enemies = []
#     ranged_enemies = []
#     bullets = []
#
#     # Создаем обычных врагов
#     for _ in range(2):  # Меньше обычных врагов
#         enemies.append(create_random_enemy(enemies))
#
#     # Создаем стреляющих врагов
#     for _ in range(1):  # Один стреляющий враг
#         ranged_enemies.append(create_random_ranged_enemy(ranged_enemies))
#
#     medkits = []
#     last_medkit_spawn = pygame.time.get_ticks()
#     game_state = PLAYING
#
#
# class Medkit:
#     def __init__(self, x, y):
#         self.rect = pygame.Rect(x, y, MEDKIT_SIZE, MEDKIT_SIZE)
#         self.spawn_time = pygame.time.get_ticks()
#
#     def is_expired(self):
#         elapsed = pygame.time.get_ticks() - self.spawn_time
#         return elapsed > MEDKIT_LIFETIME
#
#     def color(self):
#         elapsed = pygame.time.get_ticks() - self.spawn_time
#         if elapsed > MEDKIT_LIFETIME - 3000:  # мигаем последние 3 сек
#             return YELLOW if (pygame.time.get_ticks() // 250) % 2 == 0 else GREEN
#         return YELLOW
#
#
# # Обработчик удара по врагу
# def attack_enemy(player, enemies, ranged_enemies):
#     attack_radius = 1.5 * PLAYER_SIZE
#     attack_circle = pygame.Rect(player.centerx - attack_radius, player.centery - attack_radius, 2 * attack_radius,
#                                 2 * attack_radius)
#
#     hit = False
#
#     # Проверяем попадание по обычным врагам
#     for enemy in enemies[:]:
#         if attack_circle.colliderect(enemy.rect):
#             enemy.health -= 1  # Уменьшаем здоровье врага
#             enemy.last_hit_time = pygame.time.get_ticks()
#             if enemy.health <= 0:
#                 enemies.remove(enemy)
#                 hit = True
#
#     # Проверяем попадание по стреляющим врагам
#     for enemy in ranged_enemies[:]:
#         if attack_circle.colliderect(enemy.rect):
#             enemy.health -= 1  # Уменьшаем здоровье врага
#             enemy.last_hit_time = pygame.time.get_ticks()
#             if enemy.health <= 0:
#                 ranged_enemies.remove(enemy)
#                 hit = True
#
#     return hit
#
#
# # Генерация нового врага через 3 секунды
# def spawn_enemy_timer(last_death_time, enemies, ranged_enemies):
#     if pygame.time.get_ticks() - last_death_time >= 3000:
#         # Случайно выбираем тип врага для спавна
#         if random.random() < 0.7:  # 70% chance for regular enemy
#             enemies.append(create_random_enemy(enemies))
#         else:  # 30% chance for ranged enemy
#             ranged_enemies.append(create_random_ranged_enemy(ranged_enemies))
#         return pygame.time.get_ticks()  # Обновляем время последнего убийства
#     return last_death_time
#
#
# # Обновление пуль
# def update_bullets(bullets, player, enemies, ranged_enemies, medkits, obstacles):
#     for bullet in bullets[:]:
#         # Двигаем пулю
#         bullet['rect'].x += bullet['dx']
#         bullet['rect'].y += bullet['dy']
#
#         # Проверяем столкновение с границами экрана
#         if (bullet['rect'].x < 0 or bullet['rect'].x > WIDTH or
#                 bullet['rect'].y < 0 or bullet['rect'].y > HEIGHT):
#             bullets.remove(bullet)
#             continue
#
#         # Проверяем столкновение с препятствиями
#         for wall in obstacles:
#             if bullet['rect'].colliderect(wall):
#                 if bullet in bullets:
#                     bullets.remove(bullet)
#                 break
#
#         # Проверяем столкновение с игроком
#         if bullet['rect'].colliderect(player):
#             if bullet in bullets:
#                 bullets.remove(bullet)
#                 return True  # Игрок получил удар
#
#         # Проверяем столкновение с обычными врагами
#         for enemy in enemies[:]:
#             if bullet['rect'].colliderect(enemy.rect):
#                 if bullet in bullets:
#                     bullets.remove(bullet)
#                 enemy.health -= 1
#                 enemy.last_hit_time = pygame.time.get_ticks()
#                 if enemy.health <= 0:
#                     enemies.remove(enemy)
#                 break
#
#         # Проверяем столкновение со стреляющими врагами
#         for enemy in ranged_enemies[:]:
#             if bullet['rect'].colliderect(enemy.rect):
#                 if bullet in bullets:
#                     bullets.remove(bullet)
#                 enemy.health -= 1
#                 enemy.last_hit_time = pygame.time.get_ticks()
#                 if enemy.health <= 0:
#                     ranged_enemies.remove(enemy)
#                 break
#
#         # Проверяем столкновение с аптечками
#         for medkit in medkits[:]:
#             if bullet['rect'].colliderect(medkit.rect):
#                 if bullet in bullets:
#                     bullets.remove(bullet)
#                 medkits.remove(medkit)
#                 break
#
#     return False  # Игрок не получил удар
#
#
# # Отображение главного меню
# def draw_main_menu():
#     screen.fill(BLACK)
#     font = pygame.font.SysFont('arial', 36)
#     title_text = font.render("NOMAD", True, YELLOW)
#     screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 4))
#
#     play_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 50)
#     instructions_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50)
#
#     pygame.draw.rect(screen, WHITE, play_button)
#     pygame.draw.rect(screen, WHITE, instructions_button)
#     play_text = pygame.font.SysFont(None, 36).render("Новая игра", True, BLACK)
#     instructions_text = pygame.font.SysFont(None, 36).render("Как играть", True, BLACK)
#     screen.blit(play_text,
#                 (play_button.centerx - play_text.get_width() // 2, play_button.centery - play_text.get_height() // 2))
#     screen.blit(instructions_text, (instructions_button.centerx - instructions_text.get_width() // 2,
#                                     instructions_button.centery - instructions_text.get_height() // 2))
#
#     return play_button, instructions_button
#
#
# # Экран с инструкциями
# def draw_instructions():
#     screen.fill(BLACK)
#     font = pygame.font.SysFont('arial', 24)
#     lines = [
#         "Управление: стрелки для движения",
#         "Пробел для атаки",
#         "Собирайте аптечки для восстановления здоровья",
#         "Уворачивайтесь от врагов и пуль",
#         "Синие круги - стреляющие враги",
#         "Нажмите ESC для возврата в меню"
#     ]
#
#     for i, line in enumerate(lines):
#         text = font.render(line, True, WHITE)
#         screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 4 + i * 40))
#
#     pygame.display.flip()
#
#     waiting = True
#     while waiting:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.quit()
#                 sys.exit()
#             if event.type == pygame.KEYDOWN:
#                 if event.key == pygame.K_ESCAPE:
#                     waiting = False
#
#
# # Функция для отображения экрана конца игры
# def show_game_over_screen():
#     screen.fill(BLACK)
#     font = pygame.font.SysFont('arial', 36)
#     game_over_text = font.render(f"Wasted. Score: {score}", True, WHITE)
#     screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 100))
#
#     menu_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 50)
#     pygame.draw.rect(screen, YELLOW, menu_button)
#     menu_text = font.render("Main Menu", True, BLACK)
#     screen.blit(menu_text,
#                 (menu_button.centerx - menu_text.get_width() // 2, menu_button.centery - menu_text.get_height() // 2))
#
#     pygame.display.flip()
#
#     waiting = True
#     while waiting:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.quit()
#                 sys.exit()
#             if event.type == pygame.MOUSEBUTTONDOWN:
#                 if menu_button.collidepoint(event.pos):
#                     waiting = False
#
#
# # Основной цикл
# running = True
# clock = pygame.time.Clock()
#
# while running:
#     clock.tick(60)
#     now = pygame.time.get_ticks()
#
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False
#
#         if game_state == MENU:
#             if event.type == pygame.MOUSEBUTTONDOWN:
#                 play_button, instructions_button = draw_main_menu()
#                 if play_button.collidepoint(event.pos):
#                     init_game()
#                 elif instructions_button.collidepoint(event.pos):
#                     game_state = INSTRUCTIONS
#
#     if game_state == MENU:
#         play_button, instructions_button = draw_main_menu()
#         pygame.display.flip()
#
#     elif game_state == INSTRUCTIONS:
#         draw_instructions()
#         game_state = MENU
#
#     elif game_state == PLAYING:
#         # Движение игрока
#         keys = pygame.key.get_pressed()
#         dx = dy = 0
#         if keys[pygame.K_LEFT]:
#             dx = -PLAYER_SPEED
#         if keys[pygame.K_RIGHT]:
#             dx = PLAYER_SPEED
#         if keys[pygame.K_UP]:
#             dy = -PLAYER_SPEED
#         if keys[pygame.K_DOWN]:
#             dy = PLAYER_SPEED
#
#         if can_move(player, dx, 0, obstacles):
#             player.x += dx
#         if can_move(player, 0, dy, obstacles):
#             player.y += dy
#
#         player.x = max(0, min(player.x, WIDTH - PLAYER_SIZE))
#         player.y = max(0, min(player.y, HEIGHT - PLAYER_SIZE))
#
#         # Обновляем обычных врагов
#         for enemy in enemies[:]:
#             other_enemies = [e for e in enemies if e != enemy] + ranged_enemies
#             enemy.update(player, obstacles, other_enemies)
#             if enemy.rect.colliderect(player):
#                 player_lives -= 1
#                 enemies.remove(enemy)
#                 last_death_time = pygame.time.get_ticks()
#                 if player_lives <= 0:
#                     game_state = GAME_OVER
#
#         # Обновляем стреляющих врагов
#         for enemy in ranged_enemies[:]:
#             other_enemies = enemies + [e for e in ranged_enemies if e != enemy]
#             enemy.update(player, obstacles, other_enemies, bullets)
#             if enemy.rect.colliderect(player):
#                 player_lives -= 1
#                 ranged_enemies.remove(enemy)
#                 last_death_time = pygame.time.get_ticks()
#                 if player_lives <= 0:
#                     game_state = GAME_OVER
#
#         # Обновляем пули и проверяем столкновения
#         player_hit = update_bullets(bullets, player, enemies, ranged_enemies, medkits, obstacles)
#         if player_hit:
#             player_lives -= 1
#             if player_lives <= 0:
#                 game_state = GAME_OVER
#
#         # Проверка удара
#         if keys[pygame.K_SPACE]:
#             if attack_timer == 0 or pygame.time.get_ticks() - attack_timer >= 10:  # Удар только если прошло больше 500 мс
#                 attack_timer = pygame.time.get_ticks()
#                 if attack_enemy(player, enemies, ranged_enemies):  # Если враг убит
#                     score += 1
#
#         # Генерация врагов через 3 секунды после смерти
#         last_death_time = spawn_enemy_timer(last_death_time, enemies, ranged_enemies)
#
#         # Спавн аптечки
#         if now - last_medkit_spawn > MEDKIT_SPAWN_INTERVAL and len(medkits) == 0:
#             while True:
#                 x = random.randint(0, WIDTH - MEDKIT_SIZE)
#                 y = random.randint(0, HEIGHT - MEDKIT_SIZE)
#                 new_rect = pygame.Rect(x, y, MEDKIT_SIZE, MEDKIT_SIZE)
#                 if not any(new_rect.colliderect(wall) for wall in obstacles):
#                     medkits.append(Medkit(x, y))
#                     last_medkit_spawn = now
#                     break
#
#         # Проверка аптечек
#         for medkit in medkits[:]:
#             if player.colliderect(medkit.rect):
#                 player_lives = min(3, player_lives + 1)  # Не больше 3 жизней
#                 medkits.remove(medkit)
#             elif medkit.is_expired():
#                 medkits.remove(medkit)
#
#         # Определяем цвет игрока
#         if player_lives == 3:
#             player_color = WHITE
#         elif player_lives == 2:
#             player_color = LIGHT_GRAY
#         elif player_lives == 1:
#             player_color = DARK_GRAY
#         else:
#             player_color = BLACK
#
#         # Рисуем всё
#         screen.fill(GREEN)
#
#         # Рисуем препятствия
#         for wall in obstacles:
#             pygame.draw.rect(screen, RED, wall)
#
#         # Рисуем обычных врагов
#         for enemy in enemies:
#             enemy_color = enemy.get_color()
#             if enemy_color:
#                 pygame.draw.rect(screen, enemy_color, enemy.rect)
#
#         # Рисуем стреляющих врагов (круги)
#         for enemy in ranged_enemies:
#             enemy_color = enemy.get_color()
#             if enemy_color:
#                 pygame.draw.circle(screen, enemy_color, enemy.rect.center, RANGED_ENEMY_SIZE // 2)
#
#         # Рисуем аптечки
#         for medkit in medkits:
#             pygame.draw.rect(screen, medkit.color(), medkit.rect)
#
#         # Рисуем пули
#         for bullet in bullets:
#             pygame.draw.circle(screen, BRIGHT_GREEN, bullet['rect'].center, BULLET_SIZE // 2)
#
#         # Рисуем игрока
#         pygame.draw.rect(screen, player_color, player)
#
#         # Рисуем радиус атаки
#         if keys[pygame.K_SPACE]:
#             attack_radius = 1.5 * PLAYER_SIZE
#             pygame.draw.circle(screen, WHITE, player.center, attack_radius, 3)
#
#         # Рисуем счет
#         font = pygame.font.SysFont('arial', 36)
#         score_text = font.render(f"Score: {score}", True, YELLOW)
#         screen.blit(score_text, (20, 20))
#
#         # Рисуем жизни
#         lives_text = font.render(f"Lives: {player_lives}", True, YELLOW)
#         screen.blit(lives_text, (WIDTH - 150, 20))
#
#         pygame.display.flip()
#
#     elif game_state == GAME_OVER:
#         show_game_over_screen()
#         game_state = MENU
#
# pygame.quit()
# sys.exit()

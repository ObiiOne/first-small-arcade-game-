import pygame
import sys
import random
import math

pygame.init()

# Настройки окна
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NOMAD")

# Размеры
PLAYER_SIZE = 50
ENEMY_SIZE = 50
MEDKIT_SIZE = 20
STAMINA_BOOSTER_SIZE = 20
RANGED_ENEMY_SIZE = 50
BULLET_SIZE = 8

# Скорости
PLAYER_SPEED = 3
ENEMY_SPEED = 5
BULLET_SPEED = 6
PATROL_CHANGE_INTERVAL = 60

# Цвета
WHITE = (255, 255, 255)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (25, 130, 20)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# Состояния игры
MENU = 0
PLAYING = 1
GAME_OVER = 2
INSTRUCTIONS = 3

# Инициализация состояния игры
game_state = MENU

# Игрок
player = pygame.Rect(WIDTH // 2, HEIGHT // 2, PLAYER_SIZE, PLAYER_SIZE)
player_lives = 3
player_stamina = 100
score = 0
MAX_STAMINA = 100

# Препятствия
obstacles = [
    pygame.Rect(70, 70, 150, 20),
    pygame.Rect(70, 70, 20, 150),
    pygame.Rect(70, 350, 20, 150),
    pygame.Rect(70, 500, 150, 20),
    pygame.Rect(220, 70, 20, 150),
    pygame.Rect(300, 500, 300, 20),
    pygame.Rect(300, 400, 300, 20),
    pygame.Rect(400, 70, 100, 20),
    pygame.Rect(400, 200, 20, 100),
    pygame.Rect(700, 150, 20, 300),
]

# Враги, аптечки и пули
enemies = []
ranged_enemies = []
medkits = []
stamina_boosters = []
bullets = []

# Таймеры
attack_timer = 0
last_death_time = 0
last_medkit_spawn = pygame.time.get_ticks()
last_stamina_booster_spawn = pygame.time.get_ticks()
BULLET_SPAWN_INTERVAL = 2000
MEDKIT_SPAWN_INTERVAL = random.randint(3000, 7000)
STAMINA_BOOSTER_SPAWN_INTERVAL = random.randint(3000, 7000)
MEDKIT_LIFETIME = 5000
STAMINA_BOOSTER_LIFETIME = 5000
game_start_time = 0  # Время начала игры


# Проверка столкновений
def can_move(rect, dx, dy, obstacles, other_enemies=[]):
    new_rect = rect.move(dx, dy)
    for wall in obstacles:
        if new_rect.colliderect(wall):
            return False
    for e in other_enemies:
        if new_rect.colliderect(e.rect):
            return False
    return True


# Проверка столкновения с другими врагами при генерации (радиус 100 пикселей)
def can_spawn(new_rect, existing_enemies, min_distance=100):
    for enemy in existing_enemies:
        # Создаем расширенный прямоугольник для проверки расстояния
        expanded_rect = enemy.rect.inflate(min_distance, min_distance)
        if new_rect.colliderect(expanded_rect):
            return False
    return True


# Класс врага с жизнями
class Enemy:
    def __init__(self, rect):
        self.rect = rect
        self.health = 2
        angle = random.uniform(0, 2 * math.pi)
        self.dx = math.cos(angle)
        self.dy = math.sin(angle)
        self.mode = 'patrol'
        self.frames = 0
        self.last_hit_time = 0

    def update(self, player, obstacles, enemies, game_start_time):
        # Проверяем, прошла ли задержка в 1000 мс после начала игры
        if pygame.time.get_ticks() - game_start_time < 1000:
            return  # Не двигаемся первые 1000 мс

        self.frames += 1
        vector_to_player = (player.centerx - self.rect.centerx, player.centery - self.rect.centery)
        dist = math.hypot(*vector_to_player)
        can_see_player = False

        # Проверка видимости игрока по прямой
        steps = int(dist / 5)
        if steps > 0:
            step_x = vector_to_player[0] / steps
            step_y = vector_to_player[1] / steps
            temp_rect = self.rect.copy()
            blocked = False
            for _ in range(steps):
                temp_rect.x += step_x
                temp_rect.y += step_y
                for wall in obstacles:
                    if temp_rect.colliderect(wall):
                        blocked = True
                        break
                if blocked:
                    break
            can_see_player = not blocked

        self.mode = 'chase' if can_see_player else 'patrol'

        move_x = move_y = 0

        if self.mode == 'chase':
            if dist != 0:
                dx = vector_to_player[0] / dist
                dy = vector_to_player[1] / dist
                move_x = dx * ENEMY_SPEED
                move_y = dy * ENEMY_SPEED
        else:
            move_x = self.dx * ENEMY_SPEED
            move_y = self.dy * ENEMY_SPEED
            if self.frames % PATROL_CHANGE_INTERVAL == 0:
                angle = random.uniform(0, 2 * math.pi)
                self.dx = math.cos(angle)
                self.dy = math.sin(angle)

        if can_move(self.rect, move_x, move_y, obstacles, enemies):
            self.rect.x += move_x
            self.rect.y += move_y
        else:
            if self.mode == 'patrol':
                angle = random.uniform(0, 2 * math.pi)
                self.dx = math.cos(angle)
                self.dy = math.sin(angle)

        # Ограничение границ окна
        self.rect.x = max(0, min(self.rect.x, WIDTH - ENEMY_SIZE))
        self.rect.y = max(0, min(self.rect.y, HEIGHT - ENEMY_SIZE))

    def get_color(self):
        if self.health == 2:
            return BLUE
        elif self.health == 1:
            return PURPLE
        elif self.health <= 0:
            elapsed = pygame.time.get_ticks() - self.last_hit_time
            if elapsed < 1000:
                return (255, 255, 255) if (pygame.time.get_ticks() // 250) % 2 == 0 else BLUE
            else:
                return None


# Класс стреляющего врага
class RangedEnemy:
    def __init__(self, rect):
        self.rect = rect
        self.health = 2
        angle = random.uniform(0, 2 * math.pi)
        self.dx = math.cos(angle)
        self.dy = math.sin(angle)
        self.mode = 'patrol'
        self.frames = 0
        self.last_hit_time = 0
        self.last_shot_time = 0
        self.cooldown_until = 0  # Время, до которого враг не может двигаться после выстрела

    def update(self, player, obstacles, enemies, bullets, game_start_time):
        # Проверяем, прошла ли задержка в 1000 мс после начала игры
        if pygame.time.get_ticks() - game_start_time < 1000:
            return  # Не двигаемся и не стреляем первые 1000 мс

        current_time = pygame.time.get_ticks()

        # Если враг в кд после выстрела, не двигаемся
        if current_time < self.cooldown_until:
            return

        self.frames += 1
        vector_to_player = (player.centerx - self.rect.centerx, player.centery - self.rect.centery)
        dist = math.hypot(*vector_to_player)
        can_see_player = False

        # Проверка видимости игрока по прямой
        steps = int(dist / 5)
        if steps > 0:
            step_x = vector_to_player[0] / steps
            step_y = vector_to_player[1] / steps
            temp_rect = self.rect.copy()
            blocked = False
            for _ in range(steps):
                temp_rect.x += step_x
                temp_rect.y += step_y
                for wall in obstacles:
                    if temp_rect.colliderect(wall):
                        blocked = True
                        break
                if blocked:
                    break
            can_see_player = not blocked

        self.mode = 'chase' if can_see_player else 'patrol'

        move_x = move_y = 0

        if self.mode == 'chase':
            if dist != 0 and dist < 200:
                dx = -vector_to_player[0] / dist
                dy = -vector_to_player[1] / dist
                move_x = dx * ENEMY_SPEED
                move_y = dy * ENEMY_SPEED
            elif dist > 300:
                dx = vector_to_player[0] / dist
                dy = vector_to_player[1] / dist
                move_x = dx * ENEMY_SPEED
                move_y = dy * ENEMY_SPEED
        else:
            move_x = self.dx * ENEMY_SPEED
            move_y = self.dy * ENEMY_SPEED
            if self.frames % PATROL_CHANGE_INTERVAL == 0:
                angle = random.uniform(0, 2 * math.pi)
                self.dx = math.cos(angle)
                self.dy = math.sin(angle)

        if can_move(self.rect, move_x, move_y, obstacles, enemies):
            self.rect.x += move_x
            self.rect.y += move_y

        # Ограничение границ окна
        self.rect.x = max(0, min(self.rect.x, WIDTH - RANGED_ENEMY_SIZE))
        self.rect.y = max(0, min(self.rect.y, HEIGHT - RANGED_ENEMY_SIZE))

        # Стрельба по игроку
        if can_see_player and current_time - self.last_shot_time > BULLET_SPAWN_INTERVAL:
            self.shoot(player, bullets)
            self.last_shot_time = current_time
            self.cooldown_until = current_time + 100  # 100ms кд после выстрела

    def shoot(self, player, bullets):
        dx = player.centerx - self.rect.centerx
        dy = player.centery - self.rect.centery
        dist = max(0.1, math.hypot(dx, dy))

        dx /= dist
        dy /= dist

        # Создаем пулю на расстоянии от стрелка, чтобы не касаться его
        bullet_offset = RANGED_ENEMY_SIZE // 2 + BULLET_SIZE + 5  # Отступ от центра стрелка
        bullet_x = self.rect.centerx + dx * bullet_offset - BULLET_SIZE // 2
        bullet_y = self.rect.centery + dy * bullet_offset - BULLET_SIZE // 2

        bullet_rect = pygame.Rect(bullet_x, bullet_y, BULLET_SIZE, BULLET_SIZE)

        bullets.append({
            'rect': bullet_rect,
            'dx': dx * BULLET_SPEED,
            'dy': dy * BULLET_SPEED,
            'owner': 'enemy'
        })

    def get_color(self):
        if self.health == 2:
            return BLUE
        elif self.health == 1:
            return PURPLE
        elif self.health <= 0:
            elapsed = pygame.time.get_ticks() - self.last_hit_time
            if elapsed < 1000:
                return (255, 255, 255) if (pygame.time.get_ticks() // 250) % 2 == 0 else BLUE
            else:
                return None


# Создание врага на случайной границе с проверкой коллизий
def create_random_enemy(existing_enemies):
    attempts = 0
    while attempts < 50:  # Ограничиваем попытки
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

        # Проверяем столкновения с препятствиями и другими врагами (радиус 100 пикселей)
        if (not any(new_enemy.colliderect(w) for w in obstacles) and
                can_spawn(new_enemy, existing_enemies, 100)):
            return Enemy(new_enemy)

    # Если не удалось найти позицию, возвращаем None
    return None


# Создание стреляющего врага на случайной границе с проверкой коллизий
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

        if (not any(new_enemy.colliderect(w) for w in obstacles) and
                can_spawn(new_enemy, existing_enemies, 100)):
            return RangedEnemy(new_enemy)

    return None


# Генерация начальных врагов
def init_game():
    global player, player_lives, player_stamina, score, enemies, ranged_enemies, medkits, stamina_boosters, bullets, last_medkit_spawn, game_state, game_start_time
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
    game_start_time = pygame.time.get_ticks()  # Запоминаем время начала игры
    game_state = PLAYING


class Medkit:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, MEDKIT_SIZE, MEDKIT_SIZE)
        self.spawn_time = pygame.time.get_ticks()

    def is_expired(self):
        elapsed = pygame.time.get_ticks() - self.spawn_time
        return elapsed > MEDKIT_LIFETIME

    def color(self):
        elapsed = pygame.time.get_ticks() - self.spawn_time
        if elapsed > MEDKIT_LIFETIME - 2000:  # мигаем последние 2 сек
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
        if elapsed > STAMINA_BOOSTER_LIFETIME - 2000:  # мигаем последние 2 сек
            return WHITE if (pygame.time.get_ticks() // 250) % 2 == 0 else YELLOW
        return YELLOW


# Обработчик удара по врагу
def attack_enemy(player, enemies, ranged_enemies):
    attack_radius = 1.5 * PLAYER_SIZE
    attack_circle = pygame.Rect(player.centerx - attack_radius, player.centery - attack_radius,
                                2 * attack_radius, 2 * attack_radius)

    hit = False
    points_earned = 0

    for enemy in enemies[:]:
        if attack_circle.colliderect(enemy.rect):
            enemy.health -= 1
            enemy.last_hit_time = pygame.time.get_ticks()
            if enemy.health <= 0:
                enemies.remove(enemy)
                hit = True
                points_earned += 1

    for enemy in ranged_enemies[:]:
        if attack_circle.colliderect(enemy.rect):
            enemy.health -= 1
            enemy.last_hit_time = pygame.time.get_ticks()
            if enemy.health <= 0:
                ranged_enemies.remove(enemy)
                hit = True
                points_earned += 3

    return hit, points_earned


# Генерация нового врага через 3 секунды
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


# Обновление пуль
def update_bullets(bullets, player, enemies, ranged_enemies, medkits, stamina_boosters, obstacles):
    player_hit = False

    for bullet in bullets[:]:
        # Двигаем пулю
        bullet['rect'].x += bullet['dx']
        bullet['rect'].y += bullet['dy']

        # Проверяем столкновение с границами экрана
        if (bullet['rect'].x < 0 or bullet['rect'].x > WIDTH or
                bullet['rect'].y < 0 or bullet['rect'].y > HEIGHT):
            if bullet in bullets:
                bullets.remove(bullet)
            continue

        # Проверяем столкновение с препятствиями
        for wall in obstacles:
            if bullet['rect'].colliderect(wall):
                if bullet in bullets:
                    bullets.remove(bullet)
                break

        # Проверяем столкновение с игроком
        if bullet['rect'].colliderect(player):
            if bullet in bullets:
                bullets.remove(bullet)
                player_hit = True

        # Проверяем столкновение с обычных врагов
        for enemy in enemies[:]:
            if bullet['rect'].colliderect(enemy.rect):
                if bullet in bullets:
                    bullets.remove(bullet)
                enemy.health -= 1
                enemy.last_hit_time = pygame.time.get_ticks()
                if enemy.health <= 0:
                    enemies.remove(enemy)
                break

        # Проверяем столкновение со стреляющими врагами
        for enemy in ranged_enemies[:]:
            if bullet['rect'].colliderect(enemy.rect):
                if bullet in bullets:
                    bullets.remove(bullet)
                enemy.health -= 1
                enemy.last_hit_time = pygame.time.get_ticks()
                if enemy.health <= 0:
                    ranged_enemies.remove(enemy)
                break

        # Проверяем столкновение с аптечками
        for medkit in medkits[:]:
            if bullet['rect'].colliderect(medkit.rect):
                if bullet in bullets:
                    bullets.remove(bullet)
                medkits.remove(medkit)
                break

       # Проверяем столкновение с бустером
        for stamina_booster in stamina_boosters[:]:
            if bullet['rect'].colliderect(stamina_booster.rect):
                if bullet in bullets:
                    bullets.remove(bullet)
                stamina_boosters.remove(stamina_booster)
                break

    return player_hit


# Отображение главного меню
def draw_main_menu():
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


# Экран с инструкциями
def draw_instructions():
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


# Функция для отображения экрана конца игры
def show_game_over_screen():
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


# Основной цикл
space_pressed = False
running = True
clock = pygame.time.Clock()

while running:
    clock.tick(60)
    now = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_state == MENU:
            if event.type == pygame.MOUSEBUTTONDOWN:
                play_button, instructions_button = draw_main_menu()
                if play_button.collidepoint(event.pos):
                    init_game()
                elif instructions_button.collidepoint(event.pos):
                    game_state = INSTRUCTIONS

        elif game_state == PLAYING:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    space_pressed = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    space_pressed = False

    if game_state == MENU:
        play_button, instructions_button = draw_main_menu()
        pygame.display.flip()

    elif game_state == INSTRUCTIONS:
        draw_instructions()
        game_state = MENU

    elif game_state == PLAYING:
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

        if can_move(player, dx, 0, obstacles):
            player.x += dx
        if can_move(player, 0, dy, obstacles):
            player.y += dy

        player.x = max(0, min(player.x, WIDTH - PLAYER_SIZE))
        player.y = max(0, min(player.y, HEIGHT - PLAYER_SIZE))

        # Трата выносливости со временем (1/120 за кадр)
        player_stamina -= 1/120
        if player_stamina < 0:
            player_stamina = 0

        # Обновляем обычных врагов (передаем время начала игры)
        for enemy in enemies[:]:
            other_enemies = [e for e in enemies if e != enemy] + ranged_enemies
            enemy.update(player, obstacles, other_enemies, game_start_time)
            if enemy.rect.colliderect(player):
                player_lives -= 1
                enemies.remove(enemy)
                last_death_time = pygame.time.get_ticks()
                if player_lives <= 0:
                    game_state = GAME_OVER

        # Обновляем стреляющих врагов (передаем время начала игры)
        for enemy in ranged_enemies[:]:
            other_enemies = enemies + [e for e in ranged_enemies if e != enemy]
            enemy.update(player, obstacles, other_enemies, bullets, game_start_time)
            if enemy.rect.colliderect(player):
                player_lives -= 1
                ranged_enemies.remove(enemy)
                last_death_time = pygame.time.get_ticks()
                if player_lives <= 0:
                    game_state = GAME_OVER

        # Обновляем пули и проверяем столкновения
        player_hit = update_bullets(bullets, player, enemies, ranged_enemies, medkits, stamina_boosters, obstacles)
        if player_hit:
            player_lives -= 1
            if player_lives <= 0:
                game_state = GAME_OVER

        # Проверка удара
        if space_pressed and player_stamina >= 5:
            if attack_timer == 0 or pygame.time.get_ticks() - attack_timer >= 10:
                player_stamina -= 5
                attack_timer = pygame.time.get_ticks()
                hit, points = attack_enemy(player, enemies, ranged_enemies)
                if hit:
                    score += points
                space_pressed = False  # Сбрасываем флаг после удара

        # Генерация врагов через 3 секунды после смерти
        last_death_time = spawn_enemy_timer(last_death_time, enemies, ranged_enemies)

        # Спавн аптечки
        if now - last_medkit_spawn > MEDKIT_SPAWN_INTERVAL and len(medkits) == 0:
            while True:
                x = random.randint(0, WIDTH - MEDKIT_SIZE)
                y = random.randint(0, HEIGHT - MEDKIT_SIZE)
                new_rect = pygame.Rect(x, y, MEDKIT_SIZE, MEDKIT_SIZE)
                if not any(new_rect.colliderect(wall) for wall in obstacles):
                    medkits.append(Medkit(x, y))
                    last_medkit_spawn = now
                    # Генерируем новый случайный интервал для следующей аптечки
                    MEDKIT_SPAWN_INTERVAL = random.randint(3000, 7000)
                    break

        # Проверка аптечек
        for medkit in medkits[:]:
            if player.colliderect(medkit.rect):
                player_lives = min(3, player_lives + 1)
                medkits.remove(medkit)
            elif medkit.is_expired():
                medkits.remove(medkit)

        # Спавн бустеров
        if now - last_stamina_booster_spawn > STAMINA_BOOSTER_SPAWN_INTERVAL and len(stamina_boosters) == 0:
            while True:
                x = random.randint(0, WIDTH - STAMINA_BOOSTER_SIZE)
                y = random.randint(0, HEIGHT - STAMINA_BOOSTER_SIZE)
                new_rect = pygame.Rect(x, y, STAMINA_BOOSTER_SIZE, STAMINA_BOOSTER_SIZE)
                if not any(new_rect.colliderect(wall) for wall in obstacles):
                    stamina_boosters.append(StaminaBooster(x, y))
                    last_stamina_booster_spawn = now
                    # Генерируем новый случайный интервал для следующего бустера
                    STAMINA_BOOSTER_SPAWN_INTERVAL = random.randint(3000, 7000)
                    break

        # Проверка бустеров
        for stamina_booster in stamina_boosters[:]:
            if player.colliderect(stamina_booster.rect):
                player_stamina = min(MAX_STAMINA, player_stamina + 33)  # Восстанавливаем 33 стамины
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
        for wall in obstacles:
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
            pygame.draw.circle(screen, WHITE, player.center, attack_radius, 3)

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
            countdown_text = font.render(f"Start in: {countdown}", True, WHITE)
            screen.blit(countdown_text, (WIDTH // 2 - countdown_text.get_width() // 2, HEIGHT // 2))

        pygame.display.flip()

    elif game_state == GAME_OVER:
        show_game_over_screen()
        game_state = MENU

pygame.quit()
sys.exit()

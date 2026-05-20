import pygame
import sys
import random
import math
import os

# Устанавливаем рабочую директорию в папку со скриптом
os.chdir(os.path.dirname(os.path.abspath(__file__)))

pygame.init()

# ==================== НАСТРОЙКИ ОКНА ====================
WIDTH, HEIGHT = 1024, 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NOMAD")

# ==================== КОНСТАНТЫ ИГРЫ (РЕГУЛИРУЙ ЗДЕСЬ) ====================
# --- Игрок ---
PLAYER_LIVES = 5
PLAYER_SIZE = 50
PLAYER_SPEED = 2.5
PLAYER_RADIUS = PLAYER_SIZE // 2
MELEE_STAMINA_COST = 5
CIRCLE_ATTACK_STAMINA_COST = 10
PLAYER_SHOOT_COOLDOWN = 250
NUM_CIRCLE_BULLETS = 16
MAX_STAMINA = 100
PLAYER_STAMINA_REGEN = 1/60
PLAYER_WALL_MARGIN = 2

# --- Враги ---
ENEMY_SIZE = 50
RANGED_ENEMY_SIZE = 50
ENEMY_SPEED = 1.2
ENEMY_HEALTH = 2
BULLET_SPEED = 4
BULLET_SIZE = 8
BULLET_SPAWN_INTERVAL = 1500
PATROL_CHANGE_INTERVAL = 60
ENEMY_REPULSION_RADIUS = ENEMY_SIZE * 1.2
ENEMY_REPULSION_FORCE = 0.8

# --- Волна ---
WAVE_TOTAL = 3
WAVE_SPAWN_DELAY_MIN = 1000
WAVE_SPAWN_DELAY_MAX = 3000

# --- Уровни ---
LEVEL_TRANSITION_DELAY = 2000

# --- Препятствия ---
WALL_THICKNESS = 20
DOOR_HEIGHT = 100
MAX_CLUSTERS = 18
MAX_SINGLE_BLOCKS = 30
MIN_GAP = 100
CENTER_CLEAR_W = 120
CENTER_CLEAR_H = 160
EXIT_CLEAR_W = 120
EXIT_CLEAR_H = 160

# --- Предметы ---
PICKUP_SIZE = 41
BOOSTER_ICON_SIZE = 50
MEDKIT_LIFETIME = 7500
STAMINA_BOOSTER_LIFETIME = 7500
TRANSFORM_BOOSTER_LIFETIME = 10500
MEDKIT_SPAWN_INTERVAL_MIN = 6000
MEDKIT_SPAWN_INTERVAL_MAX = 14000
STAMINA_BOOSTER_SPAWN_INTERVAL_MIN = 6000
STAMINA_BOOSTER_SPAWN_INTERVAL_MAX = 14000
TRANSFORM_BOOSTER_SPAWN_INTERVAL_MIN = 10000
TRANSFORM_BOOSTER_SPAWN_INTERVAL_MAX = 20000

# --- Монетки ---
COIN_RADIUS = 5
COIN_LIFETIME = 10000
COIN_BLINK_START = 2000
COINS_PER_ENEMY_MIN = 1
COINS_PER_ENEMY_MAX = 3
COIN_DROP_RADIUS = 50

# --- NPC таверны ---
NPC_RADIUS = 50

# --- ЦВЕТА (оставлены для UI и вспомогательных элементов) ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (25, 130, 20)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
LIGHT_GRAY = (192, 192, 192)
DARK_GRAY = (96, 96, 96)
BROWN = (139, 69, 19)
CREAM = (255, 253, 208)
PURPLE = (128, 0, 128)
PINK = (255, 105, 180)

# ==================== ЗАГРУЗКА СПРАЙТОВ ====================
def load_sprite(path, scale_to=None):
    img = pygame.image.load(path).convert_alpha()
    if scale_to:
        img = pygame.transform.scale(img, scale_to)
    return img

sprites = {
    'sword': load_sprite("res/sword.png", (ENEMY_SIZE, ENEMY_SIZE)),
    'archer': load_sprite("res/archer.png", (RANGED_ENEMY_SIZE, RANGED_ENEMY_SIZE)),
    'sw_hero': load_sprite("res/sw-hero.png", (PLAYER_SIZE, PLAYER_SIZE)),
    'mg_hero': load_sprite("res/mg-hero.png", (PLAYER_SIZE, PLAYER_SIZE)),
    'arrow': load_sprite("res/arrow.png", (BULLET_SIZE*2, BULLET_SIZE*2)),
    'tunder': load_sprite("res/tunder.png", (BULLET_SIZE*2, BULLET_SIZE*2)),
    'medic': load_sprite("res/medic.png", (BOOSTER_ICON_SIZE, BOOSTER_ICON_SIZE)),
    'meat': load_sprite("res/meat.png", (BOOSTER_ICON_SIZE, BOOSTER_ICON_SIZE)),
    'mug': load_sprite("res/mug.png", (BOOSTER_ICON_SIZE, BOOSTER_ICON_SIZE)),
    'coin': load_sprite("res/coin.png", (COIN_RADIUS*4, COIN_RADIUS*4)),
    'merc': load_sprite("res/merc.png", (NPC_RADIUS*2, NPC_RADIUS*2)),
    'barman': load_sprite("res/barman.png", (NPC_RADIUS*2, NPC_RADIUS*2)),
    'wall': load_sprite("res/wall.png"),
    'bush': load_sprite("res/bush.png"),
    'door': load_sprite("res/door.png", (WALL_THICKNESS, DOOR_HEIGHT)),
    'grass': load_sprite("res/grass.png"),
    'floor': load_sprite("res/floor.png")
}

# ==================== СОСТОЯНИЯ ИГРЫ ====================
MENU = 0
PLAYING = 1
GAME_OVER = 2
INSTRUCTIONS = 3
WIN = 4
game_state = MENU

ROOM_ENEMY = 0
ROOM_TAVERN = 1
ROOM_FINAL_TAVERN = 2
game_room_state = ROOM_ENEMY

# ==================== ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ====================
player = pygame.Rect(0, 0, PLAYER_SIZE, PLAYER_SIZE)
player_lives = PLAYER_LIVES
player_stamina = MAX_STAMINA
score = 0

enemy_rooms_completed = 0
rooms_until_tavern = random.randint(3, 5)

player_transformed = False
transform_start_time = 0
player_last_shot_time = 0

obstacles = []

door_y = HEIGHT // 2 - DOOR_HEIGHT // 2
left_door_rect = pygame.Rect(0, door_y, WALL_THICKNESS, DOOR_HEIGHT)
right_door_rect = pygame.Rect(WIDTH - WALL_THICKNESS, door_y, WALL_THICKNESS, DOOR_HEIGHT)
left_door_open = True
right_door_open = False
player_moved = False

wave_enemies = []
wave_spawned = 0
wave_spawn_timer = 0
wave_active = False
wave_all_dead = False

enemies = []
ranged_enemies = []
medkits = []
stamina_boosters = []
bullets = []
transform_boosters = []
coins = []
tavern_npcs = []
barman_used = False

attack_timer = 0
last_medkit_spawn = pygame.time.get_ticks()
last_stamina_booster_spawn = pygame.time.get_ticks()
last_transform_booster_spawn = pygame.time.get_ticks()
game_start_time = 0
level_start_delay = 0

# ==================== КЛАСС ПРЕПЯТСТВИЯ ====================
class Obstacle:
    def __init__(self, rect, sprite_key):
        self.rect = rect
        raw = sprites[sprite_key]
        if sprite_key in ('wall', 'bush'):
            self.image = pygame.transform.scale(raw, (rect.width, rect.height))
        else:
            self.image = raw
    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

# ==================== ГЕНЕРАЦИЯ УРОВНЯ ====================
def rects_distance(r1, r2):
    dx = max(r1.left - r2.right, r2.left - r1.right, 0)
    dy = max(r1.top - r2.bottom, r2.top - r1.bottom, 0)
    return math.hypot(dx, dy)

def generate_random_shape(n):
    cells = set()
    cells.add((0, 0))
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    for _ in range(n - 1):
        cells_list = list(cells)
        random.shuffle(cells_list)
        added = False
        for cell in cells_list:
            dirs = directions[:]
            random.shuffle(dirs)
            for d in dirs:
                nx, ny = cell[0] + d[0], cell[1] + d[1]
                if (nx, ny) not in cells:
                    cells.add((nx, ny))
                    added = True
                    break
            if added:
                break
        if not added:
            break
    return list(cells)

def generate_inner_obstacles():
    obs = []
    block_size = 50
    inner_margin = WALL_THICKNESS + MIN_GAP
    inner_rect = pygame.Rect(inner_margin, inner_margin,
                             WIDTH - 2 * inner_margin,
                             HEIGHT - 2 * inner_margin)
    start_clear = pygame.Rect(0, door_y - 30,
                              WALL_THICKNESS + CENTER_CLEAR_W,
                              DOOR_HEIGHT + 60)
    exit_clear = pygame.Rect(WIDTH - WALL_THICKNESS - EXIT_CLEAR_W, door_y - 30,
                             EXIT_CLEAR_W, DOOR_HEIGHT + 60)

    all_placed = []
    attempts_per_cluster = 300
    for _ in range(MAX_CLUSTERS):
        n_blocks = random.randint(1, 6)
        shape_cells = generate_random_shape(n_blocks)
        min_cx = min(c[0] for c in shape_cells)
        min_cy = min(c[1] for c in shape_cells)
        max_cx = max(c[0] for c in shape_cells)
        max_cy = max(c[1] for c in shape_cells)
        shape_w = (max_cx - min_cx + 1) * block_size
        shape_h = (max_cy - min_cy + 1) * block_size

        for _ in range(attempts_per_cluster):
            if inner_rect.width < shape_w or inner_rect.height < shape_h:
                break
            grid_x = random.randint(0, (inner_rect.width - shape_w) // block_size)
            grid_y = random.randint(0, (inner_rect.height - shape_h) // block_size)
            base_x = inner_rect.left + grid_x * block_size
            base_y = inner_rect.top + grid_y * block_size

            new_rects = []
            for cx, cy in shape_cells:
                rect = pygame.Rect(base_x + (cx - min_cx) * block_size,
                                   base_y + (cy - min_cy) * block_size,
                                   block_size, block_size)
                new_rects.append(rect)

            if any(r.colliderect(start_clear) or r.colliderect(exit_clear) for r in new_rects):
                continue
            collision = False
            for r1 in new_rects:
                for r2 in all_placed:
                    if rects_distance(r1, r2) < MIN_GAP:
                        collision = True
                        break
                if collision:
                    break
            if not collision:
                for r in new_rects:
                    obs.append(Obstacle(r, 'wall'))
                all_placed.extend(new_rects)
                break

    for _ in range(MAX_SINGLE_BLOCKS):
        for _ in range(200):
            x = inner_rect.left + random.randint(0, (inner_rect.width - block_size) // block_size) * block_size
            y = inner_rect.top + random.randint(0, (inner_rect.height - block_size) // block_size) * block_size
            rect = pygame.Rect(x, y, block_size, block_size)
            if rect.colliderect(start_clear) or rect.colliderect(exit_clear):
                continue
            collision = False
            for r2 in all_placed:
                if rects_distance(rect, r2) < MIN_GAP:
                    collision = True
                    break
            if not collision:
                obs.append(Obstacle(rect, 'bush'))
                all_placed.append(rect)
                break
    return obs

# ==================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ====================
def can_move(rect, dx, dy, obstacles, other_enemies=[], margin=0):
    new_rect = rect.move(dx, dy)
    test_rect = new_rect.inflate(-margin*2, -margin*2) if margin else new_rect
    for obs in obstacles:
        if test_rect.colliderect(obs.rect):
            return False
    for e in other_enemies:
        if new_rect.colliderect(e.rect):
            return False
    return True

def can_spawn(new_rect, existing_enemies, min_distance=100):
    for enemy in existing_enemies:
        expanded_rect = enemy.rect.inflate(min_distance, min_distance)
        if new_rect.colliderect(expanded_rect):
            return False
    return True

def is_coin_position_free(x, y):
    test_rect = pygame.Rect(x - COIN_RADIUS, y - COIN_RADIUS, COIN_RADIUS*2, COIN_RADIUS*2)
    for obs in obstacles:
        if test_rect.colliderect(obs.rect):
            return False
    return True

def spawn_coins(x, y):
    global coins
    count = random.randint(COINS_PER_ENEMY_MIN, COINS_PER_ENEMY_MAX)
    for _ in range(count):
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(0, COIN_DROP_RADIUS)
            cx = x + math.cos(angle) * dist
            cy = y + math.sin(angle) * dist
            cx = max(COIN_RADIUS, min(WIDTH - COIN_RADIUS, cx))
            cy = max(COIN_RADIUS, min(HEIGHT - COIN_RADIUS, cy))
            if is_coin_position_free(cx, cy):
                coins.append(Coin(cx, cy))
                break

# ==================== КЛАССЫ СУЩНОСТЕЙ ====================
class Enemy:
    def __init__(self, rect):
        self.rect = rect
        self.health = ENEMY_HEALTH
        self.last_hit_time = 0
        angle = random.uniform(0, 2 * math.pi)
        self.move_dir_x = math.cos(angle)
        self.move_dir_y = math.sin(angle)
        self.sees_player = False
        self.sprite = sprites['sword']

    def has_line_of_sight(self, player, obstacles):
        dx = player.centerx - self.rect.centerx
        dy = player.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        steps = int(dist / 5)
        if steps == 0:
            return True
        step_x = dx / steps
        step_y = dy / steps
        temp = self.rect.copy()
        for _ in range(steps):
            temp.x += step_x
            temp.y += step_y
            for obs in obstacles:
                if temp.colliderect(obs.rect):
                    return False
        return True

    def update(self, player, obstacles, all_enemies, game_start_time):
        now = pygame.time.get_ticks()
        if now - game_start_time < 1000:
            return

        self.sees_player = self.has_line_of_sight(player, obstacles)

        if self.sees_player:
            dx = player.centerx - self.rect.centerx
            dy = player.centery - self.rect.centery
            dist = max(0.1, math.hypot(dx, dy))
            move_x = (dx / dist) * ENEMY_SPEED
            move_y = (dy / dist) * ENEMY_SPEED

            if can_move(self.rect, move_x, move_y, obstacles, all_enemies):
                self.rect.x += move_x
                self.rect.y += move_y
            else:
                if can_move(self.rect, move_x, 0, obstacles, all_enemies):
                    self.rect.x += move_x
                if can_move(self.rect, 0, move_y, obstacles, all_enemies):
                    self.rect.y += move_y
        else:
            move_x = self.move_dir_x * ENEMY_SPEED
            move_y = self.move_dir_y * ENEMY_SPEED
            if can_move(self.rect, move_x, move_y, obstacles, all_enemies):
                self.rect.x += move_x
                self.rect.y += move_y
            else:
                angle = random.uniform(0, 2 * math.pi)
                self.move_dir_x = math.cos(angle)
                self.move_dir_y = math.sin(angle)

    def draw(self, screen):
        if self.health > 0:
            screen.blit(self.sprite, self.rect.topleft)
        else:
            elapsed = pygame.time.get_ticks() - self.last_hit_time
            if elapsed < 1000:
                if (pygame.time.get_ticks() // 250) % 2 == 0:
                    screen.blit(self.sprite, self.rect.topleft)

class RangedEnemy(Enemy):
    def __init__(self, rect):
        super().__init__(rect)
        self.last_shot_time = 0
        self.cooldown_until = 0
        self.sprite = sprites['archer']

    def update(self, player, obstacles, all_enemies, bullets, game_start_time):
        now = pygame.time.get_ticks()
        if now - game_start_time < 1000:
            return
        if now < self.cooldown_until:
            return

        self.sees_player = self.has_line_of_sight(player, obstacles)

        if self.sees_player:
            dx = player.centerx - self.rect.centerx
            dy = player.centery - self.rect.centery
            dist = math.hypot(dx, dy)
            if dist < 400 and now - self.last_shot_time > BULLET_SPAWN_INTERVAL:
                self.shoot(player, bullets)
                self.last_shot_time = now
                self.cooldown_until = now + 100
        else:
            move_x = self.move_dir_x * ENEMY_SPEED
            move_y = self.move_dir_y * ENEMY_SPEED
            if can_move(self.rect, move_x, move_y, obstacles, all_enemies):
                self.rect.x += move_x
                self.rect.y += move_y
            else:
                angle = random.uniform(0, 2 * math.pi)
                self.move_dir_x = math.cos(angle)
                self.move_dir_y = math.sin(angle)

    def shoot(self, player, bullets):
        dx = player.centerx - self.rect.centerx
        dy = player.centery - self.rect.centery
        dist = max(0.1, math.hypot(dx, dy))
        dx /= dist
        dy /= dist
        offset = RANGED_ENEMY_SIZE // 2 + BULLET_SIZE + 5
        bx = self.rect.centerx + dx * offset - BULLET_SIZE // 2
        by = self.rect.centery + dy * offset - BULLET_SIZE // 2
        bullet_rect = pygame.Rect(bx, by, BULLET_SIZE, BULLET_SIZE)
        bullets.append({
            'rect': bullet_rect,
            'dx': dx * BULLET_SPEED,
            'dy': dy * BULLET_SPEED,
            'owner': 'enemy',
            'sprite': sprites['arrow']
        })

class Medkit:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PICKUP_SIZE, PICKUP_SIZE)
        self.spawn_time = pygame.time.get_ticks()
        self.sprite = sprites['medic']
    def is_expired(self):
        return pygame.time.get_ticks() - self.spawn_time > MEDKIT_LIFETIME
    def draw(self, screen):
        if self.is_expired(): return
        now = pygame.time.get_ticks()
        if now - self.spawn_time > MEDKIT_LIFETIME - 2000:
            if (now // 250) % 2 == 0: return
        base_x = self.rect.centerx - BOOSTER_ICON_SIZE // 2
        base_y = self.rect.centery - BOOSTER_ICON_SIZE // 2
        screen.blit(self.sprite, (base_x, base_y))

class StaminaBooster:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PICKUP_SIZE, PICKUP_SIZE)
        self.spawn_time = pygame.time.get_ticks()
        self.sprite = sprites['meat']
    def is_expired(self):
        return pygame.time.get_ticks() - self.spawn_time > STAMINA_BOOSTER_LIFETIME
    def draw(self, screen):
        if self.is_expired(): return
        now = pygame.time.get_ticks()
        if now - self.spawn_time > STAMINA_BOOSTER_LIFETIME - 2000:
            if (now // 250) % 2 == 0: return
        base_x = self.rect.centerx - BOOSTER_ICON_SIZE // 2
        base_y = self.rect.centery - BOOSTER_ICON_SIZE // 2
        screen.blit(self.sprite, (base_x, base_y))

class TransformBooster:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PICKUP_SIZE, PICKUP_SIZE)
        self.spawn_time = pygame.time.get_ticks()
        self.sprite = sprites['mug']
    def is_expired(self):
        return pygame.time.get_ticks() - self.spawn_time > TRANSFORM_BOOSTER_LIFETIME
    def draw(self, screen):
        if self.is_expired(): return
        now = pygame.time.get_ticks()
        if now - self.spawn_time > TRANSFORM_BOOSTER_LIFETIME - 2000:
            if (now // 250) % 2 == 0: return
        base_x = self.rect.centerx - BOOSTER_ICON_SIZE // 2
        base_y = self.rect.centery - BOOSTER_ICON_SIZE // 2
        screen.blit(self.sprite, (base_x, base_y))

class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.spawn_time = pygame.time.get_ticks()
        self.sprite = sprites['coin']
    def is_expired(self):
        return pygame.time.get_ticks() - self.spawn_time > COIN_LIFETIME
    def draw(self, screen):
        if self.is_expired():
            return
        now = pygame.time.get_ticks()
        if now - self.spawn_time > COIN_LIFETIME - COIN_BLINK_START:
            if (now // 250) % 2 == 0:
                return
        rect = self.sprite.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(self.sprite, rect.topleft)

class TavernNPC:
    def __init__(self, npc_type, x, y):
        self.type = npc_type
        self.x = x
        self.y = y
        self.radius = NPC_RADIUS
        self.activated = False
        self.sprite = sprites['merc'] if npc_type == 'trader' else sprites['barman']

    def draw(self, screen):
        if self.activated:
            # При активации оба NPC розовеют
            tinted = self.sprite.copy()
            tinted.fill(PINK, special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(tinted, (self.x - self.radius, self.y - self.radius))
        else:
            # Всегда показываем спрайт
            screen.blit(self.sprite, (self.x - self.radius, self.y - self.radius))

# ==================== ИНИЦИАЛИЗАЦИЯ УРОВНЕЙ ====================
def init_level():
    global player, player_stamina
    global enemies, ranged_enemies, medkits, stamina_boosters, bullets, transform_boosters, coins
    global last_medkit_spawn, last_stamina_booster_spawn, last_transform_booster_spawn
    global game_state, game_start_time
    global player_transformed, transform_start_time, player_last_shot_time
    global obstacles
    global left_door_open, right_door_open, player_moved
    global wave_enemies, wave_spawned, wave_spawn_timer, wave_active, wave_all_dead
    global tavern_npcs, barman_used

    obs = []
    obs.append(Obstacle(pygame.Rect(0, 0, WIDTH, WALL_THICKNESS), 'wall'))
    obs.append(Obstacle(pygame.Rect(0, HEIGHT - WALL_THICKNESS, WIDTH, WALL_THICKNESS), 'wall'))
    obs.append(Obstacle(pygame.Rect(0, 0, WALL_THICKNESS, door_y), 'wall'))
    obs.append(Obstacle(pygame.Rect(0, door_y + DOOR_HEIGHT, WALL_THICKNESS, HEIGHT - (door_y + DOOR_HEIGHT)), 'wall'))
    obs.append(Obstacle(pygame.Rect(WIDTH - WALL_THICKNESS, 0, WALL_THICKNESS, door_y), 'wall'))
    obs.append(Obstacle(pygame.Rect(WIDTH - WALL_THICKNESS, door_y + DOOR_HEIGHT, WALL_THICKNESS, HEIGHT - (door_y + DOOR_HEIGHT)), 'wall'))

    inner = generate_inner_obstacles()
    obstacles = obs + inner

    spawn_clear = pygame.Rect(WIDTH - WALL_THICKNESS - ENEMY_SIZE - 10,
                              door_y + DOOR_HEIGHT//2 - ENEMY_SIZE//2,
                              ENEMY_SIZE + 20, ENEMY_SIZE + 20)
    obstacles = [o for o in obstacles if not o.rect.colliderect(spawn_clear)]

    player = pygame.Rect(70, door_y + DOOR_HEIGHT//2 - PLAYER_SIZE//2, PLAYER_SIZE, PLAYER_SIZE)

    enemies = []
    ranged_enemies = []
    bullets = []
    transform_boosters = []
    wave_enemies = []
    coins = []
    tavern_npcs = []
    wave_spawned = 0
    wave_spawn_timer = 0
    wave_active = False
    wave_all_dead = False

    left_door_open = True
    right_door_open = False
    player_moved = False

    medkits = []
    stamina_boosters = []
    last_medkit_spawn = pygame.time.get_ticks()
    last_stamina_booster_spawn = pygame.time.get_ticks()
    last_transform_booster_spawn = pygame.time.get_ticks()

    player_transformed = False
    transform_start_time = 0
    player_last_shot_time = 0

    barman_used = False
    game_start_time = pygame.time.get_ticks() + LEVEL_TRANSITION_DELAY


def init_tavern(final=False):
    global player, player_stamina
    global enemies, ranged_enemies, medkits, stamina_boosters, bullets, transform_boosters, coins
    global last_medkit_spawn, last_stamina_booster_spawn, last_transform_booster_spawn
    global game_state, game_start_time
    global player_transformed, transform_start_time, player_last_shot_time
    global obstacles
    global left_door_open, right_door_open, player_moved
    global wave_enemies, wave_spawned, wave_spawn_timer, wave_active, wave_all_dead
    global tavern_npcs, barman_used

    obs = []
    obs.append(Obstacle(pygame.Rect(0, 0, WIDTH, WALL_THICKNESS), 'wall'))
    obs.append(Obstacle(pygame.Rect(0, HEIGHT - WALL_THICKNESS, WIDTH, WALL_THICKNESS), 'wall'))
    obs.append(Obstacle(pygame.Rect(0, 0, WALL_THICKNESS, door_y), 'wall'))
    obs.append(Obstacle(pygame.Rect(0, door_y + DOOR_HEIGHT, WALL_THICKNESS, HEIGHT - (door_y + DOOR_HEIGHT)), 'wall'))
    if final:
        obs.append(Obstacle(pygame.Rect(WIDTH - WALL_THICKNESS, 0, WALL_THICKNESS, HEIGHT), 'wall'))
    else:
        obs.append(Obstacle(pygame.Rect(WIDTH - WALL_THICKNESS, 0, WALL_THICKNESS, door_y), 'wall'))
        obs.append(Obstacle(pygame.Rect(WIDTH - WALL_THICKNESS, door_y + DOOR_HEIGHT, WALL_THICKNESS, HEIGHT - (door_y + DOOR_HEIGHT)), 'wall'))
    obstacles = obs

    player = pygame.Rect(70, door_y + DOOR_HEIGHT//2 - PLAYER_SIZE//2, PLAYER_SIZE, PLAYER_SIZE)

    enemies = []
    ranged_enemies = []
    bullets = []
    transform_boosters = []
    wave_enemies = []
    coins = []
    wave_spawned = 0
    wave_spawn_timer = 0
    wave_active = False
    wave_all_dead = False

    left_door_open = True
    right_door_open = not final
    player_moved = False

    medkits = []
    stamina_boosters = []
    last_medkit_spawn = pygame.time.get_ticks()
    last_stamina_booster_spawn = pygame.time.get_ticks()
    last_transform_booster_spawn = pygame.time.get_ticks()

    player_transformed = False
    transform_start_time = 0
    player_last_shot_time = 0

    trader_x = WIDTH // 2 - 120
    trader_y = HEIGHT // 4
    barman_x = WIDTH // 2 + 120
    barman_y = HEIGHT // 4
    tavern_npcs = [
        TavernNPC('trader', trader_x, trader_y),
        TavernNPC('barman', barman_x, barman_y)
    ]
    barman_used = False

    game_start_time = pygame.time.get_ticks() + LEVEL_TRANSITION_DELAY


def start_new_game():
    global score, enemy_rooms_completed, rooms_until_tavern, game_room_state, player_lives, player_stamina
    score = 0
    enemy_rooms_completed = 0
    rooms_until_tavern = random.randint(3, 5)
    game_room_state = ROOM_ENEMY
    player_lives = PLAYER_LIVES
    init_level()
    player_stamina = MAX_STAMINA

# ==================== АТАКА И СТРЕЛЬБА ====================
def attack_enemy(player, enemies, ranged_enemies):
    attack_radius = 1.5 * PLAYER_SIZE
    attack_rect = pygame.Rect(player.centerx - attack_radius, player.centery - attack_radius,
                              attack_radius * 2, attack_radius * 2)
    hit = False
    points = 0
    for e in enemies[:]:
        if attack_rect.colliderect(e.rect):
            e.health -= 1
            e.last_hit_time = pygame.time.get_ticks()
            if e.health <= 0:
                spawn_coins(e.rect.centerx, e.rect.centery)
                enemies.remove(e)
                hit = True
                points += 1
    for e in ranged_enemies[:]:
        if attack_rect.colliderect(e.rect):
            e.health -= 1
            e.last_hit_time = pygame.time.get_ticks()
            if e.health <= 0:
                spawn_coins(e.rect.centerx, e.rect.centery)
                ranged_enemies.remove(e)
                hit = True
                points += 3
    return hit, points

def update_bullets(bullets, player, enemies, ranged_enemies, medkits, stamina_boosters, obstacles):
    global score
    player_hit = False
    for b in bullets[:]:
        b['rect'].x += b['dx']
        b['rect'].y += b['dy']
        if b['rect'].x < 0 or b['rect'].x > WIDTH or b['rect'].y < 0 or b['rect'].y > HEIGHT:
            bullets.remove(b)
            continue
        wall_hit = False
        for obs in obstacles:
            if b['rect'].colliderect(obs.rect):
                bullets.remove(b)
                wall_hit = True
                break
        if wall_hit:
            continue
        if b['rect'].colliderect(player) and b.get('owner') != 'player':
            bullets.remove(b)
            player_hit = True
            continue
        hit_enemy = False
        for e in enemies[:]:
            if b['rect'].colliderect(e.rect):
                bullets.remove(b)
                e.health -= 1
                e.last_hit_time = pygame.time.get_ticks()
                if e.health <= 0:
                    spawn_coins(e.rect.centerx, e.rect.centery)
                    enemies.remove(e)
                    score += 1
                hit_enemy = True
                break
        if hit_enemy:
            continue
        for e in ranged_enemies[:]:
            if b['rect'].colliderect(e.rect):
                bullets.remove(b)
                e.health -= 1
                e.last_hit_time = pygame.time.get_ticks()
                if e.health <= 0:
                    spawn_coins(e.rect.centerx, e.rect.centery)
                    ranged_enemies.remove(e)
                    score += 3
                hit_enemy = True
                break
        if hit_enemy:
            continue
        for mk in medkits[:]:
            if b['rect'].colliderect(mk.rect):
                bullets.remove(b)
                medkits.remove(mk)
                break
        else:
            for sb in stamina_boosters[:]:
                if b['rect'].colliderect(sb.rect):
                    bullets.remove(b)
                    stamina_boosters.remove(sb)
                    break
    return player_hit

# ==================== МЕНЮ ====================
play_btn = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 50)
instr_btn = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50)

def draw_main_menu():
    screen.fill(BLACK)
    font = pygame.font.SysFont('arial', 36)
    title_text = font.render("NOMAD", True, WHITE)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 4))
    pygame.draw.rect(screen, WHITE, play_btn)
    pygame.draw.rect(screen, WHITE, instr_btn)
    play_text = pygame.font.SysFont(None, 36).render("Новая игра", True, BLACK)
    instr_text = pygame.font.SysFont(None, 36).render("Как играть", True, BLACK)
    screen.blit(play_text, (play_btn.centerx - play_text.get_width() // 2, play_btn.centery - play_text.get_height() // 2))
    screen.blit(instr_text, (instr_btn.centerx - instr_text.get_width() // 2, instr_btn.centery - instr_text.get_height() // 2))

def draw_instructions():
    screen.fill(BLACK)
    font = pygame.font.SysFont('arial', 24)
    lines = [
        "Управление: W A S D",
        "Ближний бой: пробел",
        "Аптечка лечит",
        "Окорочок восстанавливает стамину",
        "Кружка пива: круговая атака (пробел)",
        "Собирай монеты, выживай!",
        "ESC – назад в меню"
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
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                waiting = False

def show_game_over_screen():
    screen.fill(BLACK)
    font = pygame.font.SysFont('arial', 36)
    game_over_text = font.render(f"Wasted. Score: {score}", True, WHITE)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 100))
    menu_btn = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 50)
    pygame.draw.rect(screen, YELLOW, menu_btn)
    menu_text = font.render("Main Menu", True, BLACK)
    screen.blit(menu_text, (menu_btn.centerx - menu_text.get_width() // 2, menu_btn.centery - menu_text.get_height() // 2))
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and menu_btn.collidepoint(event.pos):
                waiting = False

def show_win_screen():
    screen.fill(BLACK)
    font = pygame.font.SysFont('arial', 36)
    win_text = font.render(f"Победа, твой счет: {score}", True, WHITE)
    screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2 - 100))
    menu_btn = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 50)
    pygame.draw.rect(screen, YELLOW, menu_btn)
    menu_text = font.render("В меню", True, BLACK)
    screen.blit(menu_text, (menu_btn.centerx - menu_text.get_width() // 2, menu_btn.centery - menu_text.get_height() // 2))
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and menu_btn.collidepoint(event.pos):
                waiting = False

# ==================== ГЛАВНЫЙ ЦИКЛ ====================
space_pressed = False
running = True
clock = pygame.time.Clock()

while running:
    clock.tick(60)
    now = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif game_state == MENU and event.type == pygame.MOUSEBUTTONDOWN:
            if play_btn.collidepoint(event.pos):
                pygame.time.wait(50)
                start_new_game()
                game_state = PLAYING
            elif instr_btn.collidepoint(event.pos):
                game_state = INSTRUCTIONS
        elif game_state == PLAYING:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                space_pressed = True
            elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                space_pressed = False

    if game_state == MENU:
        draw_main_menu()
        pygame.display.flip()
    elif game_state == INSTRUCTIONS:
        draw_instructions()
        game_state = MENU
    elif game_state == PLAYING:
        if now < game_start_time:
            screen.fill(GREEN)
            font = pygame.font.SysFont('arial', 48)
            if game_room_state == ROOM_ENEMY:
                room_text = f"Вражеская комната {enemy_rooms_completed + 1}"
            elif game_room_state == ROOM_FINAL_TAVERN:
                room_text = "Таверна (финал)"
            else:
                room_text = "Таверна"
            level_text = font.render(room_text, True, WHITE)
            screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, HEIGHT // 2 - 50))
            pygame.display.flip()
            continue

        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_a]: dx = -PLAYER_SPEED
        if keys[pygame.K_d]: dx = PLAYER_SPEED
        if keys[pygame.K_w]: dy = -PLAYER_SPEED
        if keys[pygame.K_s]: dy = PLAYER_SPEED

        if not player_moved and (dx != 0 or dy != 0 or space_pressed):
            player_moved = True
            if left_door_open:
                obstacles.append(Obstacle(left_door_rect, 'wall'))
                left_door_open = False
                if game_room_state == ROOM_ENEMY:
                    wave_active = True
                    wave_spawn_timer = now + random.randint(WAVE_SPAWN_DELAY_MIN, WAVE_SPAWN_DELAY_MAX)

        if can_move(player, dx, 0, obstacles, margin=PLAYER_WALL_MARGIN):
            player.x += dx
        if can_move(player, 0, dy, obstacles, margin=PLAYER_WALL_MARGIN):
            player.y += dy

        if game_room_state == ROOM_ENEMY:
            if wave_active and not wave_all_dead and wave_spawned < WAVE_TOTAL and now >= wave_spawn_timer:
                obstacles = [o for o in obstacles if o.rect != right_door_rect]
                right_door_open = True
                spawn_x = WIDTH - WALL_THICKNESS - ENEMY_SIZE - 5
                spawn_y = door_y + DOOR_HEIGHT//2 - ENEMY_SIZE//2
                spawn_rect = pygame.Rect(spawn_x, spawn_y, ENEMY_SIZE, ENEMY_SIZE)
                if not any(spawn_rect.colliderect(o.rect) for o in obstacles):
                    if random.random() < 0.5:
                        e = Enemy(spawn_rect)
                        enemies.append(e)
                    else:
                        e = RangedEnemy(spawn_rect)
                        ranged_enemies.append(e)
                    wave_enemies.append(e)
                    wave_spawned += 1
                obstacles.append(Obstacle(right_door_rect, 'wall'))
                right_door_open = False
                wave_spawn_timer = now + random.randint(WAVE_SPAWN_DELAY_MIN, WAVE_SPAWN_DELAY_MAX)

            if wave_active and wave_spawned == WAVE_TOTAL and not wave_all_dead:
                wave_enemies = [e for e in wave_enemies if e.health > 0]
                if len(wave_enemies) == 0:
                    wave_all_dead = True
                    wave_active = False
                    obstacles = [o for o in obstacles if o.rect != right_door_rect]
                    right_door_open = True

            if right_door_open and player.colliderect(right_door_rect):
                enemy_rooms_completed += 1
                if enemy_rooms_completed == 10:
                    game_room_state = ROOM_FINAL_TAVERN
                    init_tavern(final=True)
                else:
                    rooms_until_tavern -= 1
                    if rooms_until_tavern <= 0:
                        game_room_state = ROOM_TAVERN
                        rooms_until_tavern = random.randint(3, 5)
                        init_tavern(final=False)
                    else:
                        saved_transformed = player_transformed
                        saved_transform_start = transform_start_time
                        init_level()
                        player_transformed = saved_transformed
                        transform_start_time = saved_transform_start

        elif game_room_state in (ROOM_TAVERN, ROOM_FINAL_TAVERN):
            if game_room_state == ROOM_TAVERN and right_door_open and player.colliderect(right_door_rect):
                game_room_state = ROOM_ENEMY
                init_level()

            attack_radius = 1.5 * PLAYER_SIZE
            attack_rect = pygame.Rect(player.centerx - attack_radius, player.centery - attack_radius,
                                      attack_radius * 2, attack_radius * 2)
            for npc in tavern_npcs:
                npc.activated = False

            if space_pressed:
                for npc in tavern_npcs:
                    npc_rect = pygame.Rect(npc.x - npc.radius, npc.y - npc.radius,
                                           npc.radius * 2, npc.radius * 2)
                    if attack_rect.colliderect(npc_rect):
                        npc.activated = True
                        if npc.type == 'trader':
                            pass
                        elif npc.type == 'barman':
                            if game_room_state == ROOM_FINAL_TAVERN:
                                player_lives = PLAYER_LIVES
                                player_stamina = MAX_STAMINA
                                game_state = WIN
                            else:
                                if not barman_used:
                                    barman_used = True
                                    player_lives = PLAYER_LIVES
                                    player_stamina = MAX_STAMINA

        if game_room_state == ROOM_ENEMY:
            player_stamina -= PLAYER_STAMINA_REGEN
            if player_stamina < 0:
                player_stamina = 0

            all_enemies = enemies + ranged_enemies
            for e in enemies[:]:
                others = [en for en in all_enemies if en != e]
                e.update(player, obstacles, others, game_start_time)
                if e.rect.colliderect(player):
                    player_lives -= 1
                    e.health = 0
                    spawn_coins(e.rect.centerx, e.rect.centery)
                    enemies.remove(e)
                    if player_lives <= 0:
                        game_state = GAME_OVER
            for e in ranged_enemies[:]:
                others = [en for en in all_enemies if en != e]
                e.update(player, obstacles, others, bullets, game_start_time)
                if e.rect.colliderect(player):
                    player_lives -= 1
                    e.health = 0
                    spawn_coins(e.rect.centerx, e.rect.centery)
                    ranged_enemies.remove(e)
                    if player_lives <= 0:
                        game_state = GAME_OVER

            if update_bullets(bullets, player, enemies, ranged_enemies, medkits, stamina_boosters, obstacles):
                player_lives -= 1
                if player_lives <= 0:
                    game_state = GAME_OVER

            if space_pressed and player_stamina >= MELEE_STAMINA_COST and not player_transformed:
                if attack_timer == 0 or now - attack_timer >= 10:
                    player_stamina -= MELEE_STAMINA_COST
                    attack_timer = now
                    hit, pts = attack_enemy(player, enemies, ranged_enemies)
                    if hit:
                        score += pts
                    space_pressed = False

            if player_transformed and keys[pygame.K_SPACE] and now - player_last_shot_time >= PLAYER_SHOOT_COOLDOWN and player_stamina >= CIRCLE_ATTACK_STAMINA_COST:
                player_stamina -= CIRCLE_ATTACK_STAMINA_COST
                for i in range(NUM_CIRCLE_BULLETS):
                    angle = 2 * math.pi * i / NUM_CIRCLE_BULLETS
                    offset = PLAYER_RADIUS + BULLET_SIZE + 5
                    bx = player.centerx + math.cos(angle) * offset - BULLET_SIZE // 2
                    by = player.centery + math.sin(angle) * offset - BULLET_SIZE // 2
                    bullets.append({
                        'rect': pygame.Rect(bx, by, BULLET_SIZE, BULLET_SIZE),
                        'dx': math.cos(angle) * BULLET_SPEED,
                        'dy': math.sin(angle) * BULLET_SPEED,
                        'owner': 'player',
                        'sprite': sprites['tunder']
                    })
                player_last_shot_time = now

            if wave_active and not wave_all_dead:
                if now - last_medkit_spawn > random.randint(MEDKIT_SPAWN_INTERVAL_MIN, MEDKIT_SPAWN_INTERVAL_MAX) and not medkits:
                    while True:
                        x = random.randint(0, WIDTH - PICKUP_SIZE)
                        y = random.randint(0, HEIGHT - PICKUP_SIZE)
                        rect = pygame.Rect(x, y, PICKUP_SIZE, PICKUP_SIZE)
                        if not any(rect.colliderect(o.rect) for o in obstacles):
                            medkits.append(Medkit(x, y))
                            last_medkit_spawn = now
                            break
                if now - last_stamina_booster_spawn > random.randint(STAMINA_BOOSTER_SPAWN_INTERVAL_MIN, STAMINA_BOOSTER_SPAWN_INTERVAL_MAX) and not stamina_boosters:
                    while True:
                        x = random.randint(0, WIDTH - PICKUP_SIZE)
                        y = random.randint(0, HEIGHT - PICKUP_SIZE)
                        rect = pygame.Rect(x, y, PICKUP_SIZE, PICKUP_SIZE)
                        if not any(rect.colliderect(o.rect) for o in obstacles):
                            stamina_boosters.append(StaminaBooster(x, y))
                            last_stamina_booster_spawn = now
                            break
                if now - last_transform_booster_spawn > random.randint(TRANSFORM_BOOSTER_SPAWN_INTERVAL_MIN, TRANSFORM_BOOSTER_SPAWN_INTERVAL_MAX) and not transform_boosters:
                    while True:
                        x = random.randint(0, WIDTH - PICKUP_SIZE)
                        y = random.randint(0, HEIGHT - PICKUP_SIZE)
                        rect = pygame.Rect(x, y, PICKUP_SIZE, PICKUP_SIZE)
                        if not any(rect.colliderect(o.rect) for o in obstacles):
                            transform_boosters.append(TransformBooster(x, y))
                            last_transform_booster_spawn = now
                            break

            for mk in medkits[:]:
                if player.colliderect(mk.rect):
                    player_lives = min(PLAYER_LIVES, player_lives + 1)
                    medkits.remove(mk)
                elif mk.is_expired():
                    medkits.remove(mk)
            for sb in stamina_boosters[:]:
                if player.colliderect(sb.rect):
                    player_stamina = MAX_STAMINA
                    stamina_boosters.remove(sb)
                elif sb.is_expired():
                    stamina_boosters.remove(sb)
            for tb in transform_boosters[:]:
                if player.colliderect(tb.rect):
                    if not player_transformed:
                        player_transformed = True
                        transform_start_time = now
                    else:
                        transform_start_time = now
                    transform_boosters.remove(tb)
                elif tb.is_expired():
                    transform_boosters.remove(tb)

            if player_transformed and now - transform_start_time >= 31000:
                player_transformed = False

            for c in coins[:]:
                if c.is_expired():
                    coins.remove(c)
                elif math.hypot(player.centerx - c.x, player.centery - c.y) < PLAYER_RADIUS + COIN_RADIUS:
                    score += 1
                    coins.remove(c)

        # ==================== ОТРИСОВКА ====================
        # Фон: трава для вражеских комнат, пол для таверны
        if game_room_state == ROOM_ENEMY:
            tile = sprites['grass']
        else:
            tile = sprites['floor']
        for y in range(0, HEIGHT, 64):
            for x in range(0, WIDTH, 64):
                screen.blit(tile, (x, y))

        for obs in obstacles:
            obs.draw(screen)

        if left_door_open:
            screen.blit(sprites['door'], left_door_rect.topleft)
        if right_door_open:
            screen.blit(sprites['door'], right_door_rect.topleft)

        if game_room_state == ROOM_ENEMY:
            for e in enemies:
                e.draw(screen)
            for e in ranged_enemies:
                e.draw(screen)
            for mk in medkits:
                mk.draw(screen)
            for sb in stamina_boosters:
                sb.draw(screen)
            for tb in transform_boosters:
                tb.draw(screen)
            for b in bullets:
                screen.blit(b['sprite'], b['rect'].topleft)

        for npc in tavern_npcs:
            npc.draw(screen)

        for c in coins:
            c.draw(screen)

        if game_room_state == ROOM_ENEMY and player_transformed:
            elapsed = now - transform_start_time
            if elapsed < 30000 or (int((elapsed - 30000) / (1000/6)) % 2 == 0):
                screen.blit(sprites['mg_hero'], player.topleft)
        else:
            screen.blit(sprites['sw_hero'], player.topleft)
            if game_room_state == ROOM_ENEMY and keys[pygame.K_SPACE] and not player_transformed:
                attack_radius = 1.5 * PLAYER_SIZE
                pygame.draw.circle(screen, WHITE, player.center, attack_radius, 3)

        font = pygame.font.SysFont('arial', 36)
        screen.blit(font.render(f"Score: {score}", True, YELLOW), (20, 20))
        screen.blit(font.render(f"Lives: {player_lives}", True, YELLOW), (WIDTH - 150, 20))
        screen.blit(font.render(f"Stamina:{int(player_stamina)}", True, YELLOW), (WIDTH // 2 - 100, 20))
        if game_room_state == ROOM_ENEMY:
            room_info = f"Room {enemy_rooms_completed + 1}/10"
            screen.blit(font.render(room_info, True, YELLOW), (WIDTH // 2 - 50, 60))

        pygame.display.flip()

    elif game_state == GAME_OVER:
        show_game_over_screen()
        game_state = MENU
    elif game_state == WIN:
        show_win_screen()
        game_state = MENU

pygame.quit()
sys.exit()

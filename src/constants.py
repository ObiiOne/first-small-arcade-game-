import pygame

# Настройки окна
WIDTH, HEIGHT = 800, 600

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

# Препятствия
OBSTACLES = [
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

# Тайминги
BULLET_SPAWN_INTERVAL = 2000
MEDKIT_LIFETIME = 5000
STAMINA_BOOSTER_LIFETIME = 5000
MAX_STAMINA = 100

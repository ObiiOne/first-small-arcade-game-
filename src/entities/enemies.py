import pygame
import math
import random
from src.constants import *


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
        if pygame.time.get_ticks() - game_start_time < 1000:
            return

        self.frames += 1
        vector_to_player = (player.centerx - self.rect.centerx, player.centery - self.rect.centery)
        dist = math.hypot(*vector_to_player)
        can_see_player = False

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

        from utils.collisions import can_move
        if can_move(self.rect, move_x, move_y, obstacles, enemies):
            self.rect.x += move_x
            self.rect.y += move_y
        else:
            if self.mode == 'patrol':
                angle = random.uniform(0, 2 * math.pi)
                self.dx = math.cos(angle)
                self.dy = math.sin(angle)

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
        self.cooldown_until = 0

    def update(self, player, obstacles, enemies, bullets, game_start_time):
        if pygame.time.get_ticks() - game_start_time < 1000:
            return

        current_time = pygame.time.get_ticks()

        if current_time < self.cooldown_until:
            return

        self.frames += 1
        vector_to_player = (player.centerx - self.rect.centerx, player.centery - self.rect.centery)
        dist = math.hypot(*vector_to_player)
        can_see_player = False

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

        from utils.collisions import can_move
        if can_move(self.rect, move_x, move_y, obstacles, enemies):
            self.rect.x += move_x
            self.rect.y += move_y

        self.rect.x = max(0, min(self.rect.x, WIDTH - RANGED_ENEMY_SIZE))
        self.rect.y = max(0, min(self.rect.y, HEIGHT - RANGED_ENEMY_SIZE))

        if can_see_player and current_time - self.last_shot_time > BULLET_SPAWN_INTERVAL:
            self.shoot(player, bullets)
            self.last_shot_time = current_time
            self.cooldown_until = current_time + 100

    def shoot(self, player, bullets):
        dx = player.centerx - self.rect.centerx
        dy = player.centery - self.rect.centery
        dist = max(0.1, math.hypot(dx, dy))

        dx /= dist
        dy /= dist

        bullet_offset = RANGED_ENEMY_SIZE // 2 + BULLET_SIZE + 5
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
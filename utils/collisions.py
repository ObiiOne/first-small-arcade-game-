import pygame
import math
from src.constants import *


def can_move(rect, dx, dy, obstacles, other_enemies=[]):
    new_rect = rect.move(dx, dy)
    for wall in obstacles:
        if new_rect.colliderect(wall):
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


def update_bullets(bullets, player, enemies, ranged_enemies, medkits, stamina_boosters, obstacles):
    player_hit = False

    for bullet in bullets[:]:
        bullet['rect'].x += bullet['dx']
        bullet['rect'].y += bullet['dy']

        if (bullet['rect'].x < 0 or bullet['rect'].x > WIDTH or
                bullet['rect'].y < 0 or bullet['rect'].y > HEIGHT):
            if bullet in bullets:
                bullets.remove(bullet)
            continue

        for wall in obstacles:
            if bullet['rect'].colliderect(wall):
                if bullet in bullets:
                    bullets.remove(bullet)
                break

        if bullet['rect'].colliderect(player):
            if bullet in bullets:
                bullets.remove(bullet)
                player_hit = True

        for enemy in enemies[:]:
            if bullet['rect'].colliderect(enemy.rect):
                if bullet in bullets:
                    bullets.remove(bullet)
                enemy.health -= 1
                enemy.last_hit_time = pygame.time.get_ticks()
                if enemy.health <= 0:
                    enemies.remove(enemy)
                break

        for enemy in ranged_enemies[:]:
            if bullet['rect'].colliderect(enemy.rect):
                if bullet in bullets:
                    bullets.remove(bullet)
                enemy.health -= 1
                enemy.last_hit_time = pygame.time.get_ticks()
                if enemy.health <= 0:
                    ranged_enemies.remove(enemy)
                break

        for medkit in medkits[:]:
            if bullet['rect'].colliderect(medkit.rect):
                if bullet in bullets:
                    bullets.remove(bullet)
                medkits.remove(medkit)
                break

        for stamina_booster in stamina_boosters[:]:
            if bullet['rect'].colliderect(stamina_booster.rect):
                if bullet in bullets:
                    bullets.remove(bullet)
                stamina_boosters.remove(stamina_booster)
                break

    return player_hit

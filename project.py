import pygame
from pygame import key
import random
import math
import sys
import os
import json
from enum import Enum

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

pygame.init()

screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Mini_Mario")
clock = pygame.time.Clock()
icon = pygame.image.load(get_resource_path("images/favicon.ico")).convert_alpha()
pygame.display.set_icon(icon)

try:
    main_menu_bg = pygame.image.load(get_resource_path("images/main_menu_bg.png")).convert()
    main_menu_bg = pygame.transform.scale(main_menu_bg, (1280, 720))
    level_select_bg = pygame.image.load(get_resource_path("images/level_select_bg.png")).convert()
    level_select_bg = pygame.transform.scale(level_select_bg, (1280, 720))
    win_bg = pygame.image.load(get_resource_path("images/win_bg.png")).convert()
    win_bg = pygame.transform.scale(win_bg, (1280, 720))
    lose_bg = pygame.image.load(get_resource_path("images/lose_bg.png")).convert()
    lose_bg = pygame.transform.scale(lose_bg, (1280, 720))
    pause_menu_bg = pygame.image.load(get_resource_path("images/pause_menu_bg.png")).convert()
    pause_menu_bg = pygame.transform.scale(pause_menu_bg, (1280, 720))
    settings_bg = pygame.image.load(get_resource_path("images/settings_bg.png")).convert()
    settings_bg = pygame.transform.scale(settings_bg, (1280, 720))
    achievements_bg = pygame.image.load(get_resource_path("images/achievements_bg.png")).convert()
    achievements_bg = pygame.transform.scale(achievements_bg, (1280, 720))
except pygame.error:
    main_menu_bg = None
    level_select_bg = None
    settings_bg = None
    win_bg = None
    pause_menu_bg = None
    lose_bg = None
    achievements_bg = None

backgrounds = {}
bg_themes = {
    "tutorial": "images/font.png", "forest": "images/font.png",
    "desert": "images/desert.jpg", "ice": "images/winter.jpg",
    "volcano": "images/volcano.png", "final": "images/final.jpg",
}
for theme, path in bg_themes.items():
    try:
        bg_surface = pygame.image.load(get_resource_path(path)).convert()
        backgrounds[theme] = pygame.transform.scale(bg_surface, (1280, 720))
    except pygame.error:
        colors = {
            "tutorial": (200, 220, 255), "forest": (100, 150, 100),
            "desert": (210, 180, 140), "ice": (173, 216, 230),
            "volcano": (180, 60, 30), "final": (50, 30, 80),
        }
        fallback = pygame.Surface((1280, 720))
        fallback.fill(colors.get(theme, (100, 150, 255)))
        backgrounds[theme] = fallback

win_font = pygame.image.load(get_resource_path("images/winter.jpg")).convert_alpha()
volc_font = pygame.image.load(get_resource_path("images/volcano.png")).convert_alpha()
des_font = pygame.image.load(get_resource_path("images/desert.jpg")).convert_alpha()
fin_font = pygame.image.load(get_resource_path("images/final.jpg")).convert_alpha()

walk_right = [
    pygame.image.load(get_resource_path("images/player_right/player_right1.png")).convert_alpha(),
    pygame.image.load(get_resource_path("images/player_right/player_right2.png")).convert_alpha(),
    pygame.image.load(get_resource_path("images/player_right/player_right3.png")).convert_alpha(),
    pygame.image.load(get_resource_path("images/player_right/player_right4.png")).convert_alpha(),
]
walk_left = [
    pygame.image.load(get_resource_path("images/player_left/player_left1.png")).convert_alpha(),
    pygame.image.load(get_resource_path("images/player_left/player_left2.png")).convert_alpha(),
    pygame.image.load(get_resource_path("images/player_left/player_left3.png")).convert_alpha(),
    pygame.image.load(get_resource_path("images/player_left/player_left4.png")).convert_alpha(),
]

ghost = pygame.image.load(get_resource_path("images/ghost.png")).convert_alpha()
enemy_sprites = {
    "ghost": ghost,
    "flying_ghost": pygame.image.load(get_resource_path("images/flying_ghost.png")).convert_alpha(),
    "patrol_ghost": pygame.image.load(get_resource_path("images/patrol_ghost.png")).convert_alpha(),
    "soldier": pygame.image.load(get_resource_path("images/solider.png")).convert_alpha(),
    "spiker": pygame.image.load(get_resource_path("images/spiker.png")).convert_alpha(),
    "tank": pygame.image.load(get_resource_path("images/tank.png")).convert_alpha(),
    "boss": pygame.image.load(get_resource_path("images/boss.png")).convert_alpha(),
}
player_bullet = pygame.image.load(get_resource_path("images/bullet.png")).convert_alpha()
coin_img = pygame.image.load(get_resource_path("images/coin.png")).convert_alpha()
coin_img = pygame.transform.scale(coin_img, (30, 30))

powerup_images = {}
powerup_paths = {
    "speed": "images/powerup_speed.png",
    "infinite_ammo": "images/powerup_ammo.png",
    "extra_life": "images/powerup_life.png",
    "double_points": "images/powerup_points.png"
}
for p_type, path in powerup_paths.items():
    try:
        img = pygame.image.load(get_resource_path(path)).convert_alpha()
        powerup_images[p_type] = pygame.transform.scale(img, (30, 30))
    except pygame.error:
        powerup_images[p_type] = None

class GameState(Enum):
    MAIN_MENU = 0
    PLAYING = 1
    GAME_OVER = 2
    LEVEL_TRANSITION = 3
    GAME_WIN = 4
    LEVEL_SELECT = 5
    TUTORIAL = 6
    DIFFICULTY_SELECT = 7
    SETTINGS = 8
    PAUSED = 9
    ACHIEVEMENTS = 10

class Difficulty(Enum):
    EASY = 0
    NORMAL = 1
    HARD = 2

DIFFICULTY_SETTINGS = {
    Difficulty.EASY: {"name": "ЛЕГКО", "name_en": "EASY", "color": (100, 220, 100), "score_mult": 0.7, "spawn_mult": 1.5, "max_enemies": 3, "health_mult": 0.8, "scroll_mult": 0.85, "description": "Меньше врагов, меньше очков для победы"},
    Difficulty.NORMAL: {"name": "НОРМАЛЬНО", "name_en": "NORMAL", "color": (255, 220, 100), "score_mult": 1.0, "spawn_mult": 1.0, "max_enemies": 5, "health_mult": 1.0, "scroll_mult": 1.0, "description": "Стандартные настройки игры"},
    Difficulty.HARD: {"name": "СЛОЖНО", "name_en": "HARD", "color": (255, 80, 80), "score_mult": 1.6, "spawn_mult": 0.55, "max_enemies": 8, "health_mult": 1.4, "scroll_mult": 1.15, "description": "Много врагов, высокие требования к очкам"}
}

ACHIEVEMENTS = {
    "FIRST_KILL": {"name": "Первая кровь", "desc": "Убейте своего первого врага"},
    "TUTORIAL_DONE": {"name": "Ученик", "desc": "Пройдите обучение"},
    "LEVEL_1": {"name": "Начало пути", "desc": "Пройдите 1-й уровень"},
    "LEVEL_2": {"name": "Пустынный бегун", "desc": "Пройдите 2-й уровень"},
    "LEVEL_3": {"name": "Ледяной поход", "desc": "Пройдите 3-й уровень"},
    "LEVEL_4": {"name": "Огненный тест", "desc": "Пройдите 4-й уровень"},
    "LEVEL_5": {"name": "Покоритель", "desc": "Пройдите 5-й уровень"},
    "COIN_50": {"name": "Богач", "desc": "Соберите 50 монет за один уровень"},
}

unlocked_achievements = []
achievement_queue = []
achievement_popup = None

run_stats = {
    "coins_collected": 0,
    "enemies_killed": 0,
    "damage_taken": 0,
    "double_jumps": 0
}

def unlock_achievement(ach_id):
    global unlocked_achievements, achievement_queue
    if ach_id in ACHIEVEMENTS and ach_id not in unlocked_achievements:
        unlocked_achievements.append(ach_id)
        achievement_queue.append(ach_id)
        save_game_progress(unlocked_levels, best_scores, unlocked_achievements)

def check_run_achievements():
    if run_stats['coins_collected'] >= 50:
        unlock_achievement("COIN_50")
    if run_stats['damage_taken'] == 0 and not is_tutorial:
        unlock_achievement("NO_HIT")
    if run_stats['enemies_killed'] >= 10:
        unlock_achievement("KILL_10")
    if run_stats['double_jumps'] >= 20:
        unlock_achievement("DOUBLE_JUMP_20")

def draw_achievement_popup():
    global achievement_popup, achievement_queue
    if achievement_popup:
        achievement_popup['timer'] -= 1
        if achievement_popup['timer'] <= 0:
            achievement_popup = None
        else:
            ach_id = achievement_popup['id']
            ach_data = ACHIEVEMENTS[ach_id]
            progress = min(1.0, (140 - achievement_popup['timer']) / 20.0)
            if achievement_popup['timer'] < 20:
                progress = achievement_popup['timer'] / 20.0
            popup_w, popup_h = 450, 90
            start_x, end_x = 1280, 1280 - popup_w - 20
            current_x = start_x + (end_x - start_x) * progress
            y = 20
            popup_surf = pygame.Surface((popup_w, popup_h), pygame.SRCALPHA)
            popup_surf.fill((0, 0, 0, 200))
            screen.blit(popup_surf, (current_x, y))
            pygame.draw.rect(screen, (255, 215, 0), (current_x, y, popup_w, popup_h), 3)
            title_text = small_font.render(f"ДОСТИЖЕНИЕ: {ach_data['name']}", True, (255, 215, 0))
            desc_text = small_font.render(ach_data['desc'], True, (255, 255, 255))
            screen.blit(title_text, (current_x + 15, y + 15))
            screen.blit(desc_text, (current_x + 15, y + 45))
    elif achievement_queue:
        ach_id = achievement_queue.pop(0)
        achievement_popup = {'id': ach_id, 'timer': 140}

def draw_achievements_menu():
    if settings_bg: screen.blit(achievements_bg, (0, 0))
    else: screen.fill((30, 30, 50))
    title_text = level_font.render("ДОСТИЖЕНИЯ", True, (255, 215, 0))
    screen.blit(title_text, (1280 // 2 - title_text.get_width() // 2, 20))
    cols, box_w, box_h = 2, 550, 100
    padding_x, padding_y = 40, 20
    start_x = (1280 - (cols * box_w + padding_x)) // 2
    start_y = 120
    mouse_pos = pygame.mouse.get_pos()
    for i, (ach_id, ach_data) in enumerate(ACHIEVEMENTS.items()):
        col, row = i % cols, i // cols
        x = start_x + col * (box_w + padding_x)
        y = start_y + row * (box_h + padding_y)
        rect = pygame.Rect(x, y, box_w, box_h)
        is_unlocked = ach_id in unlocked_achievements
        if is_unlocked:
            pygame.draw.rect(screen, (40, 60, 40), rect)
            pygame.draw.rect(screen, (100, 255, 100), rect, 3)
            name_color, desc_color = (255, 215, 0), (200, 255, 200)
            pygame.draw.circle(screen, (255, 215, 0), (x + 35, y + 40), 20)
            star_text = small_font.render("★", True, (0, 0, 0))
            screen.blit(star_text, (x + 35 - star_text.get_width()//2, y + 40 - star_text.get_height()//2))
        else:
            pygame.draw.rect(screen, (40, 40, 40), rect)
            pygame.draw.rect(screen, (100, 100, 100), rect, 3)
            name_color, desc_color = (150, 150, 150), (100, 100, 100)
            pygame.draw.circle(screen, (100, 100, 100), (x + 35, y + 40), 20)
            lock_text = small_font.render("?", True, (0, 0, 0))
            screen.blit(lock_text, (x + 35 - lock_text.get_width()//2, y + 40 - lock_text.get_height()//2))
        name_text = label.render(ach_data['name'], True, name_color)
        screen.blit(name_text, (x + 80, y + 15))
        desc_text = small_font.render(ach_data['desc'], True, desc_color)
        screen.blit(desc_text, (x + 80, y + 60))
    back_button = pygame.Rect(540, 620, 200, 50)
    if back_button.collidepoint(mouse_pos):
        pygame.draw.rect(screen, (200, 80, 80), back_button)
        pygame.draw.rect(screen, (255, 255, 255), back_button, 3)
    else:
        pygame.draw.rect(screen, (150, 50, 50), back_button)
        pygame.draw.rect(screen, (255, 255, 255), back_button, 2)
    back_text = menu_font.render("Назад", True, (255, 255, 255))
    screen.blit(back_text, (back_button.centerx - back_text.get_width() // 2, back_button.centery - back_text.get_height() // 2))
    return back_button

game_state = GameState.MAIN_MENU
current_difficulty = Difficulty.NORMAL
settings_return_to = GameState.MAIN_MENU

class Enemy:
    def __init__(self, x, y, enemy_type="ghost", health_mult=1.0):
        self.type = enemy_type
        self.image = enemy_sprites.get(enemy_type, ghost)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed_x = -3
        self.speed_y = 0
        self.attack_timer = 0
        self.direction = -1
        self.jump_timer = 0
        self.platform = None
        
        # Босс-специфичные параметры
        self.phase = 1
        self.dash_timer = 0
        self.is_dashing = False
        self.dash_cooldown = 0
        self.flash_timer = 0  # для мигания при смене фазы
        self.minion_spawn_timer = 0
        self.shake_timer = 0  # тряска экрана
        
        base_health = {"ghost": 1, "flying_ghost": 1, "patrol_ghost": 1, "soldier": 2, "spiker": 1, "tank": 5, "boss": 30}.get(enemy_type, 1)
        self.health = max(1, int(math.ceil(base_health * health_mult)))
        self.max_health = self.health
        
        if enemy_type == "flying_ghost": self.speed_x = -5; self.fly_offset = random.randint(0, 100)
        elif enemy_type == "patrol_ghost": self.speed_x = -2
        elif enemy_type == "soldier": self.speed_x = -4
        elif enemy_type == "spiker": self.speed_x = -6
        elif enemy_type == "tank": self.speed_x = -1
        elif enemy_type == "boss": self.speed_x = -2

    def _update_phase(self):
        """Определяет текущую фазу босса по HP"""
        if self.type != "boss": return
        hp_percent = self.health / self.max_health
        old_phase = self.phase
        if hp_percent <= 0.33: self.phase = 3
        elif hp_percent <= 0.66: self.phase = 2
        else: self.phase = 1
        
        # Эффект при смене фазы
        if self.phase != old_phase:
            self.flash_timer = 60  # мигаем 60 кадров
            effects.append(Effect(self.rect.centerx, self.rect.centery, "ghost_death"))
            # Сообщение игроку
            if self.phase == 2:
                add_tutorial_message("⚠️ БОСС РАЗЪЯРЁН! Атаки стали опаснее!", 180)
            elif self.phase == 3:
                add_tutorial_message("💀 ЯРОСТЬ БОССА! Берегись рывков и миньонов!", 180)

    def _boss_shoot(self):
        if self.phase == 1:
            # Одиночный выстрел
            enemy_bullets.append(EnemyBullet(self.rect.x, self.rect.y + 40, vx=-12, vy=0, size=(20, 8)))
        elif self.phase == 2:
            # Веер из 3 пуль
            for angle_offset in [-0.4, 0, 0.4]:
                vx = -10 * math.cos(angle_offset)
                vy = 10 * math.sin(angle_offset)
                enemy_bullets.append(EnemyBullet(
                    self.rect.x, self.rect.y + 40, 
                    vx=vx, vy=vy, 
                    size=(18, 8), 
                    color=(255, 150, 0)  # оранжевые пули
                ))
        elif self.phase == 3:
            # Самонаводящаяся пуля
            dx = player_x - self.rect.x
            dy = player_y - self.rect.y
            dist = max(1, math.sqrt(dx*dx + dy*dy))
            vx = (dx / dist) * 7
            vy = (dy / dist) * 7
            enemy_bullets.append(EnemyBullet(
                self.rect.x, self.rect.y + 40, 
                vx=vx, vy=vy, 
                size=(18, 18), 
                homing=True, 
                color=(255, 100, 255)  # фиолетовые шары
            ))

    def _boss_dash(self):
        """Рывок босса к игроку (только в фазе 3)"""
        if self.phase != 3 or self.dash_cooldown > 0: return
        if abs(player_x - self.rect.x) > 300:
            self.is_dashing = True
            self.dash_timer = 30
            self.dash_cooldown = 180  # кулдаун 3 секунды
            add_tutorial_message("⚡ РЫВОК БОССА!", 60)
            effects.append(Effect(self.rect.centerx, self.rect.centery, "powerup"))

    def _boss_spawn_minion(self):
        """Призыв миньона (только в фазе 3)"""
        if self.phase != 3 or len(current_level_obj.enemies) >= 5: return
        if self.minion_spawn_timer <= 0:
            if self.platform:
                spawn_x = random.choice([self.platform.left + 50, self.platform.right - 100])
                minion = Enemy(spawn_x, self.platform.y - 40, "ghost", 1.0)
                minion.platform = self.platform
                current_level_obj.enemies.append(minion)
                effects.append(Effect(spawn_x, self.platform.y - 40, "ghost_death"))
                add_tutorial_message("👻 Босс призвал миньона!", 90)
            self.minion_spawn_timer = 300  # каждые 5 секунд

    def update(self, scroll_speed, platforms):
        self.attack_timer += 1
        self.jump_timer += 1
        if self.flash_timer > 0: self.flash_timer -= 1
        if self.dash_cooldown > 0: self.dash_cooldown -= 1
        if self.minion_spawn_timer > 0: self.minion_spawn_timer -= 1
        if self.dash_timer > 0: self.dash_timer -= 1
        else: self.is_dashing = False
        
        player_dx = player_x - self.rect.x
        player_dy = player_y - self.rect.y
        
        # === ЛОГИКА БОССА ===
                # === ЛОГИКА БОССА ===
        if self.type == "boss":
            self._update_phase()
            
            # Скорость движения зависит от фазы
            phase_speed = {1: 2, 2: 3.5, 3: 5}[self.phase]

            # Желаемая позиция: игрок + смещение вправо
            desired_x = player_x + 300  # Босс всегда правее игрока

            # Ограничиваем, чтобы не уходил слишком далеко вправо (за пределы экрана)
            max_x = 1280 - self.rect.width - 50  # немного отступа от края
            desired_x = min(desired_x, max_x)

            # Ограничиваем, чтобы не был левее игрока
            min_x = player_x + 100  # минимум на 100 пикселей правее
            desired_x = max(desired_x, min_x)

            # Плавное движение к желаемой позиции
            diff = desired_x - self.rect.x
            if abs(diff) > 2:
                move_step = phase_speed if diff > 0 else -phase_speed
                self.rect.x += move_step

            # Если босс делает рывок (фаза 3), он может временно игнорировать это правило
            if self.is_dashing:
                direction = 1 if player_x > self.rect.x else -1
                self.rect.x += direction * 12
                # Но всё равно не даём уйти слишком далеко влево
                self.rect.x = max(self.rect.x, player_x + 50)

            # Прыжки (фаза 2+)
            if self.phase >= 2 and self.jump_timer > 120 and self.speed_y == 0:
                self.speed_y = -15
                self.jump_timer = 0
                effects.append(Effect(self.rect.centerx, self.rect.bottom, "jump"))

            # Стрельба
            shoot_interval = {1: 90, 2: 60, 3: 35}[self.phase]
            if self.attack_timer > shoot_interval:
                self._boss_shoot()
                self.attack_timer = 0

            # Рывки и миньоны (фаза 3)
            if self.phase == 3:
                self._boss_dash()
                self._boss_spawn_minion()
        
        # === ЛОГИКА ОБЫЧНЫХ ВРАГОВ (без изменений) ===
        elif self.type == "flying_ghost":
            if player_dx > 0: self.rect.x += 2
            else: self.rect.x -= 4
            if abs(player_dy) > 10: self.rect.y += 2 if player_dy > 0 else -2
            self.rect.y += math.sin(pygame.time.get_ticks() * 0.005 + self.fly_offset) * 2
        elif self.type == "patrol_ghost":
            self.rect.x += self.speed_x - scroll_speed
            self.rect.x += math.sin(pygame.time.get_ticks() * 0.003) * 2
        elif self.type == "soldier":
            self.rect.x += self.speed_x - scroll_speed
            if abs(player_dx) < 500 and self.attack_timer > 90:
                enemy_bullets.append(EnemyBullet(self.rect.x, self.rect.y + 20, vx=-10, vy=0, size=(15, 6)))
                self.attack_timer = 0
        elif self.type == "spiker":
            self.rect.x += self.speed_x - scroll_speed
            if self.jump_timer > 60: self.speed_y = -12; self.jump_timer = 0
            self.speed_y += 0.6
            self.rect.y += self.speed_y
            if self.rect.y >= 500: self.rect.y = 500; self.speed_y = 0
        elif self.type == "tank":
            if abs(player_dx) < 350: self.rect.x -= 8
            else: self.rect.x += self.speed_x - scroll_speed
        else:
            self.rect.x += self.speed_x - scroll_speed
        
        # Гравитация
        if self.type not in ["flying_ghost", "patrol_ghost"]:
            on_ground = False
            for platform in platforms:
                if (self.rect.bottom >= platform.top and self.rect.bottom <= platform.top + 15 and self.rect.right > platform.left and self.rect.left < platform.right):
                    on_ground = True
                    self.rect.y = platform.top - self.rect.height
                    break
            if not on_ground and self.rect.bottom < 600:
                self.speed_y += 0.5
                self.rect.y += self.speed_y
            else:
                if self.type != "spiker": self.speed_y = 0
        return self.rect.x + self.rect.width > 0

    def take_damage(self):
        self.health -= 1
        # Эффект попадания
        effects.append(Effect(self.rect.centerx, self.rect.centery, "shoot"))
        return self.health <= 0

    def draw(self, screen):
        # Мигание при смене фазы
        if self.flash_timer > 0 and (self.flash_timer // 4) % 2 == 0:
            # Рисуем белую вспышку
            flash_surf = self.image.copy()
            flash_surf.fill((255, 255, 255, 180), special_flags=pygame.BLEND_RGBA_ADD)
            screen.blit(flash_surf, self.rect)
        else:
            # Красноватый оттенок в фазе 3
            if self.type == "boss" and self.phase == 3:
                tinted = self.image.copy()
                tinted.fill((255, 50, 50, 80), special_flags=pygame.BLEND_RGBA_ADD)
                screen.blit(tinted, self.rect)
            else:
                screen.blit(self.image, self.rect)
        
        # Полоска здоровья (у босса — большая и снизу экрана)
        base_health = {"ghost": 1, "flying_ghost": 1, "patrol_ghost": 1, "soldier": 2, "spiker": 1, "tank": 5, "boss": 30}.get(self.type, 1)
        max_h = max(1, int(math.ceil(base_health * DIFFICULTY_SETTINGS[current_difficulty]["health_mult"])))
        
        if self.type == "boss":
            # ОГРОМНАЯ полоска HP босса внизу экрана
            bar_width, bar_height = 800, 25
            bar_x = (1280 - bar_width) // 2
            bar_y = 670
            # Фон
            pygame.draw.rect(screen, (40, 0, 0), (bar_x - 3, bar_y - 3, bar_width + 6, bar_height + 6))
            pygame.draw.rect(screen, (80, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            # Заполнение с цветом фазы
            hp_width = int(bar_width * (self.health / max_h))
            phase_colors = {1: (100, 255, 100), 2: (255, 200, 0), 3: (255, 50, 50)}
            pygame.draw.rect(screen, phase_colors[self.phase], (bar_x, bar_y, hp_width, bar_height))
            pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)
            # Имя босса
            boss_name = {1: "🔥 ТЁМНЫЙ ВЛАСТЫКА 🔥", 2: "⚡ РАЗЪЯРЁННЫЙ БОСС ⚡", 3: "💀 ЯРОСТЬ 💀"}[self.phase]
            name_text = small_font.render(boss_name, True, phase_colors[self.phase])
            screen.blit(name_text, (bar_x + bar_width // 2 - name_text.get_width() // 2, bar_y - 30))
        elif self.health < max_h:
            bar_width, bar_height = self.rect.width, 4
            bar_x, bar_y = self.rect.x, self.rect.y - 8
            pygame.draw.rect(screen, (80, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            hp_width = int(bar_width * (self.health / max_h))
            pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, hp_width, bar_height))
            
class PowerUp:
    def __init__(self, x, y, power_type):
        self.rect = pygame.Rect(x, y, 30, 30) # Увеличил размер до 30x30 под картинки
        self.type = power_type
        self.lifetime = 300
        self.animation_frame = 0
        self.image = powerup_images.get(power_type)
        
    def update(self, scroll_speed):
        self.rect.x -= scroll_speed
        self.lifetime -= 1
        self.animation_frame = (self.animation_frame + 1) % 20
        return self.lifetime > 0 and self.rect.x + self.rect.width > 0
        
    def draw(self, screen):
        if self.image:
            # Рисуем картинку бонуса
            screen.blit(self.image, self.rect)
        else:
            # Запасной вариант, если картинки нет в папке images
            colors = {"speed": (255, 255, 0), "infinite_ammo": (0, 255, 255), "extra_life": (255, 0, 0), "double_points": (255, 165, 0)}
            color = colors.get(self.type, (255, 255, 255))
            pygame.draw.rect(screen, color, self.rect)
            pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)

class Level:
    def __init__(self, level_num, is_tutorial=False):
        self.num = level_num
        self.is_tutorial = is_tutorial
        self.platforms = []
        self.enemies = []
        self.powerups = []
        self.coins = []
        base_scroll = 3 if is_tutorial else 4
        base_spawn_delay = 5000 if is_tutorial else 2500
        base_goal = 50 if is_tutorial else 150
        if is_tutorial: diff = DIFFICULTY_SETTINGS[Difficulty.EASY]
        else: diff = DIFFICULTY_SETTINGS[current_difficulty]
        self.scroll_speed = int(base_scroll * diff["scroll_mult"])
        self.ghost_spawn_delay = int(base_spawn_delay * diff["spawn_mult"])
        self.goal_score = int(base_goal * diff["score_mult"])
        self.background_color = (150, 200, 255) if is_tutorial else (100, 150, 255)
        self.gravity = 1.0
        self.theme = "tutorial" if is_tutorial else "normal"
        self.last_spawned_enemy = None
        self.generate_level()
    def generate_level(self):
        diff = DIFFICULTY_SETTINGS[Difficulty.EASY if self.is_tutorial else current_difficulty]
        health_mult = diff["health_mult"]
        if self.is_tutorial:
            self.scroll_speed = 2; self.goal_score = 30; self.background_color = (200, 220, 255); self.theme = "tutorial"
            self.platforms = [pygame.Rect(300, 550, 200, 20), pygame.Rect(600, 500, 180, 20), pygame.Rect(900, 450, 200, 20), pygame.Rect(1200, 400, 250, 20), pygame.Rect(1600, 500, 200, 20)]
            self.coins = [pygame.Rect(650, 460, 30, 30), pygame.Rect(950, 410, 30, 30), pygame.Rect(1300, 360, 30, 30), pygame.Rect(1650, 460, 30, 30)]
            self.powerups = [PowerUp(1250, 360, "speed")]
        elif self.num == 1:
            self.scroll_speed = int(4 * diff["scroll_mult"]); self.ghost_spawn_delay = int(3500 * diff["spawn_mult"]); self.goal_score = int(150 * diff["score_mult"]); self.background_color = (100, 150, 255); self.theme = "forest"
            self.platforms = [pygame.Rect(300, 550, 200, 20), pygame.Rect(600, 450, 200, 20), pygame.Rect(900, 350, 200, 20), pygame.Rect(1200, 500, 250, 20), pygame.Rect(1500, 400, 180, 20), pygame.Rect(1800, 300, 150, 20), pygame.Rect(2100, 480, 220, 20), pygame.Rect(2500, 350, 200, 20)]
            for i in range(15): self.coins.append(pygame.Rect(random.randint(500, 3000), random.choice([400, 450, 500, 530]), 30, 30))
        elif self.num == 2:
            self.scroll_speed = int(5 * diff["scroll_mult"]); self.ghost_spawn_delay = int(3000 * diff["spawn_mult"]); self.goal_score = int(250 * diff["score_mult"]); self.background_color = (255, 200, 100); self.theme = "desert"; self.gravity = 1.1
            self.platforms = [pygame.Rect(300, 550, 150, 20), pygame.Rect(500, 480, 180, 20), pygame.Rect(750, 400, 120, 20), pygame.Rect(900, 520, 200, 20), pygame.Rect(1150, 350, 160, 20), pygame.Rect(1400, 450, 140, 20), pygame.Rect(1700, 300, 180, 20), pygame.Rect(2000, 500, 200, 20), pygame.Rect(2300, 380, 150, 20), pygame.Rect(2600, 450, 170, 20)]
            for i in range(25): self.coins.append(pygame.Rect(random.randint(400, 3200), random.choice([380, 430, 470, 520]), 30, 30))
            enemy_cycle = ["patrol_ghost", "ghost", "flying_ghost"]
            for i, platform in enumerate(self.platforms[::3]): self.enemies.append(Enemy(platform.x + 50, platform.y - 40, enemy_cycle[i % len(enemy_cycle)], health_mult))
        elif self.num == 3:
            self.scroll_speed = int(6 * diff["scroll_mult"]); self.ghost_spawn_delay = int(2500 * diff["spawn_mult"]); self.goal_score = int(350 * diff["score_mult"]); self.background_color = (150, 200, 255); self.theme = "ice"; self.gravity = 1.2
            self.platforms = [pygame.Rect(300, 550, 100, 20), pygame.Rect(450, 500, 120, 20), pygame.Rect(620, 420, 100, 20), pygame.Rect(780, 340, 100, 20), pygame.Rect(950, 460, 120, 20), pygame.Rect(1120, 380, 100, 20), pygame.Rect(1300, 520, 120, 20), pygame.Rect(1480, 300, 100, 20), pygame.Rect(1650, 450, 120, 20), pygame.Rect(1850, 370, 100, 20), pygame.Rect(2050, 500, 120, 20), pygame.Rect(2250, 280, 100, 20), pygame.Rect(2450, 420, 120, 20), pygame.Rect(2650, 350, 100, 20)]
            for i in range(35): self.coins.append(pygame.Rect(random.randint(300, 3500), random.choice([360, 410, 460, 510, 540]), 30, 30))
            enemy_cycle = ["ghost", "flying_ghost", "patrol_ghost"]
            for i, platform in enumerate(self.platforms[::2]): self.enemies.append(Enemy(platform.x + 30, platform.y - 40, enemy_cycle[i % len(enemy_cycle)], health_mult))
            for i in range(3): self.powerups.append(PowerUp(random.randint(800, 2800), random.choice([350, 400, 450, 500]), random.choice(["speed", "infinite_ammo", "extra_life", "double_points"])))
        elif self.num == 4:
            self.scroll_speed = int(7 * diff["scroll_mult"]); self.ghost_spawn_delay = int(2000 * diff["spawn_mult"]); self.goal_score = int(450 * diff["score_mult"]); self.background_color = (255, 100, 50); self.theme = "volcano"; self.gravity = 1.3
            self.platforms = [pygame.Rect(300, 550, 80, 20), pygame.Rect(420, 510, 100, 20), pygame.Rect(550, 460, 90, 20), pygame.Rect(680, 400, 110, 20), pygame.Rect(830, 350, 100, 20), pygame.Rect(970, 480, 120, 20), pygame.Rect(1130, 420, 90, 20), pygame.Rect(1260, 360, 110, 20), pygame.Rect(1410, 530, 100, 20), pygame.Rect(1550, 470, 120, 20), pygame.Rect(1710, 390, 90, 20), pygame.Rect(1840, 320, 110, 20), pygame.Rect(1990, 500, 100, 20), pygame.Rect(2130, 440, 120, 20), pygame.Rect(2290, 370, 90, 20), pygame.Rect(2420, 310, 110, 20), pygame.Rect(2570, 480, 100, 20), pygame.Rect(2710, 420, 120, 20)]
            for i in range(45): self.coins.append(pygame.Rect(random.randint(300, 3800), random.choice([350, 400, 450, 500, 550]), 30, 30))
            enemy_cycle = ["patrol_ghost", "soldier", "spiker", "tank"]
            for i, platform in enumerate(self.platforms):
                if random.random() < 0.3: self.enemies.append(Enemy(platform.x + 40, platform.y - 40, enemy_cycle[i % len(enemy_cycle)], health_mult))
            for i in range(5): self.powerups.append(PowerUp(random.randint(500, 3200), random.choice([350, 400, 450, 500]), random.choice(["speed", "infinite_ammo", "double_points"])))
        elif self.num == 5:
            self.scroll_speed = int(5 * diff["scroll_mult"])
            self.ghost_spawn_delay = 999999  # Отключаем обычных врагов
            self.goal_score = int(1000 * diff["score_mult"])
            self.background_color = (50, 30, 80); self.theme = "final"; self.gravity = 1.2

            # Создаем удобные платформы для битвы
            arena_y = 450
            self.platforms = [
                pygame.Rect(150, 550, 200, 20),       # Стартовая точка игрока (слева)
                pygame.Rect(500, arena_y, 800, 30),    # Длинная арена по центру и справа
                pygame.Rect(100, 400, 150, 20),        # Верхняя платформа для уклонений
            ]

            # Монеты разбросаны по уровню
            for i in range(60):
                self.coins.append(pygame.Rect(random.randint(200, 1200), random.choice([350, 400, 500]), 30, 30))

            # Спавним босса СРАЗУ в правой части экрана (координата X = 900)
            boss_platform = self.platforms[1] # Главная арена
            boss = Enemy(900, boss_platform.y - 90, "boss", health_mult)
            boss.platform = boss_platform # Оставляем для гравитации
            self.enemies = [boss]

            # Бонусы на уровне
            for i in range(5):
                self.powerups.append(PowerUp(
                    random.randint(400, 1100),
                    random.choice([350, 400]),
                    random.choice(["speed", "infinite_ammo", "double_points", "extra_life"])
                ))

bullets = []
bullets_left = 5
bullets_infinite = False
infinite_ammo_timer = 0
score = 0
ghosts_killed = 0
player_anim_count = 0
bg_x = 0
player_speed = 15
player_x = 150
player_y = 500
player_speed_multiplier = 1.0
speed_boost_timer = 0
double_points = False
double_points_timer = 0

player_health = 3
max_player_health = 3

is_jumping = False
player_velocity_y = 0
gravity = 1.0
jump_strength = -18
is_on_ground = True
double_jump_available = False
has_double_jumped = False

invincible_frames = 0
invincible_duration = 120

current_level = 1
max_level = 5
level_complete = False
level_transition = False
level_transition_timer = 0
current_level_obj = None
is_tutorial = False

def load_game_progress():
    try:
        with open("save.json", "r") as f:
            data = json.load(f)
            return (data.get("unlocked_levels", 1), 
                    data.get("best_scores", {}),
                    data.get("unlocked_achievements", []))
    except:
        return 1, {}, []

def save_game_progress(unlocked_levels, best_scores, unlocked_achievements):
    data = {"unlocked_levels": unlocked_levels, "best_scores": best_scores, "unlocked_achievements": unlocked_achievements}
    with open("save.json", "w") as f:
        json.dump(data, f)

unlocked_levels, best_scores, unlocked_achievements = load_game_progress()

class Particle:
    def __init__(self, x, y, color, velocity_x=0, velocity_y=0, size=3, life=60):
        self.x, self.y, self.color = x, y, color
        self.velocity_x, self.velocity_y = velocity_x, velocity_y
        self.size, self.life, self.max_life = size, life, life
    def update(self):
        self.x += self.velocity_x; self.y += self.velocity_y; self.velocity_y += 0.1; self.life -= 1
        return self.life > 0
    def draw(self, surface):
        alpha = int(255 * (self.life / self.max_life))
        if alpha > 0:
            particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, (*self.color, alpha), (self.size, self.size), self.size)
            surface.blit(particle_surface, (int(self.x - self.size), int(self.y - self.size)))

class EnemyBullet:
    def __init__(self, x, y, vx=-12, vy=0, size=(20, 8), homing=False, color=(255, 50, 50)):
        self.rect = pygame.Rect(x, y, size[0], size[1])
        self.vx = vx
        self.vy = vy
        self.homing = homing
        self.color = color
        self.life = 300  # пуля живёт 5 секунд
    
    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        self.life -= 1
        # Возвращаем True, если пуля ещё "жива" и в пределах экрана
        return self.life > 0 and -50 < self.rect.x < 1350 and -50 < self.rect.y < 800
    
    def draw(self, screen):
        if self.homing:
            # Самонаводящаяся пуля — фиолетовый шар
            pygame.draw.circle(screen, self.color, self.rect.center, max(1, self.rect.width // 2))
            pygame.draw.circle(screen, (255, 255, 255), self.rect.center, max(1, self.rect.width // 4))
        else:
            # Обычная пуля — прямоугольник
            pygame.draw.rect(screen, self.color, self.rect)

class Effect:
    def __init__(self, x, y, effect_type):
        self.x, self.y, self.type = x, y, effect_type
        self.particles, self.duration = [], 0
        self.create_effect()
    def create_effect(self):
        if self.type == "jump":
            for _ in range(15):
                angle, speed = random.uniform(0, math.pi), random.uniform(1, 3)
                self.particles.append(Particle(self.x + random.randint(-10, 10), self.y + 50, (100, 150, 255), math.cos(angle) * speed * random.choice([-1, 1]), -abs(math.sin(angle) * speed), random.randint(2, 4), random.randint(20, 40)))
            self.duration = 40
        elif self.type == "land":
            for _ in range(20):
                angle, speed = random.uniform(0, math.pi), random.uniform(1, 4)
                self.particles.append(Particle(self.x + random.randint(-20, 20), self.y + 45, (150, 150, 200), math.cos(angle) * speed * random.choice([-1, 1]), -abs(math.sin(angle) * speed) * 0.5, random.randint(2, 5), random.randint(30, 50)))
            self.duration = 50
        elif self.type == "shoot":
            for _ in range(8):
                angle, speed = random.uniform(-0.3, 0.3), random.uniform(2, 5)
                self.particles.append(Particle(self.x + 70, self.y + 60, (255, 255, 100), math.cos(angle) * speed, math.sin(angle) * speed, random.randint(2, 3), random.randint(15, 25)))
            self.duration = 25
        elif self.type == "ghost_death":
            for _ in range(30):
                angle, speed = random.uniform(0, math.pi * 2), random.uniform(1, 6)
                self.particles.append(Particle(self.x + random.randint(-10, 10), self.y + random.randint(-10, 10), (200, 100, 255), math.cos(angle) * speed, math.sin(angle) * speed, random.randint(3, 6), random.randint(40, 60)))
            self.duration = 60
        elif self.type == "coin_collect":
            for _ in range(25):
                angle, speed = random.uniform(0, math.pi * 2), random.uniform(1, 4)
                self.particles.append(Particle(self.x + 15, self.y + 15, (255, 215, 0), math.cos(angle) * speed, math.sin(angle) * speed, random.randint(2, 4), random.randint(30, 45)))
            self.duration = 45
        elif self.type == "powerup":
            for _ in range(20):
                angle, speed = random.uniform(0, math.pi * 2), random.uniform(1, 5)
                self.particles.append(Particle(self.x + 15, self.y + 15, (0, 255, 255), math.cos(angle) * speed, math.sin(angle) * speed, random.randint(2, 5), random.randint(30, 50)))
            self.duration = 50
    def update(self):
        for particle in self.particles[:]:
            if not particle.update(): self.particles.remove(particle)
        self.duration -= 1
        return len(self.particles) > 0 and self.duration > 0
    def draw(self, surface):
        for particle in self.particles: particle.draw(surface)

class FloatingNumber:
    def __init__(self, x, y, number, color):
        self.x, self.y, self.number, self.color = x, y, number, color
        self.life, self.velocity_y = 60, -2
    def update(self):
        self.y += self.velocity_y; self.life -= 1
        return self.life > 0
    def draw(self, surface):
        alpha = min(255, self.life * 4)
        text = ammo_font.render(f"+{self.number}", True, self.color)
        text.set_alpha(alpha)
        surface.blit(text, (int(self.x), int(self.y)))

effects = []
floating_numbers = []
enemy_bullets = []
ghost_timer = pygame.USEREVENT + 1
coin_timer = pygame.USEREVENT + 2

label = pygame.font.SysFont("comicsans", 40, bold=True)
ammo_font = pygame.font.SysFont("comicsans", 30, bold=True)
level_font = pygame.font.SysFont("comicsans", 60, bold=True)
title_font = pygame.font.SysFont("comicsans", 80, bold=True)
menu_font = pygame.font.SysFont("comicsans", 50, bold=True)
small_font = pygame.font.SysFont("comicsans", 25, bold=True)
tutorial_font = pygame.font.SysFont("comicsans", 35, bold=True)

lose_label = label.render("GAME OVER!", False, (175, 91, 61))
level_buttons = []
was_on_ground = True
tutorial_messages = []
tutorial_message_timer = 0

def add_tutorial_message(message, duration=180):
    global tutorial_messages, tutorial_message_timer
    tutorial_messages.append({"text": message, "timer": duration})

def draw_tutorial_hints():
    panel_height = 120
    panel_surface = pygame.Surface((1280, panel_height), pygame.SRCALPHA)
    panel_surface.fill((0, 0, 0, 180))
    screen.blit(panel_surface, (0, 0))
    pygame.draw.line(screen, (255, 255, 0), (0, panel_height), (1280, panel_height), 2)
    visible_messages = tutorial_messages[-3:] if len(tutorial_messages) > 3 else tutorial_messages
    y_offset = 15
    for msg in visible_messages[:]:
        msg["timer"] -= 1
        if msg["timer"] <= 0:
            if msg in tutorial_messages: tutorial_messages.remove(msg)
        else:
            alpha = min(255, msg["timer"] * 4)
            text = tutorial_font.render(msg["text"], True, (255, 255, 0))
            text.set_alpha(alpha)
            text_rect = text.get_rect(center=(640, y_offset + 20))
            screen.blit(text, text_rect)
            y_offset += 35

def check_platform_collision(player_rect, check_vertical=True):
    collision_type, collision_platform = None, None
    for platform in current_level_obj.platforms:
        if player_rect.colliderect(platform):
            if check_vertical:
                if (player_velocity_y >= 0 and player_rect.bottom >= platform.top and player_rect.bottom <= platform.top + 25 and player_rect.right > platform.left + 5 and player_rect.left < platform.right - 5):
                    collision_type, collision_platform = "top", platform; break
                elif (player_velocity_y < 0 and player_rect.top <= platform.bottom and player_rect.top >= platform.bottom - 15 and player_rect.right > platform.left + 5 and player_rect.left < platform.right - 5):
                    collision_type, collision_platform = "bottom", platform; break
            else:
                if (player_rect.right > platform.left and player_rect.left < platform.right and player_rect.bottom > platform.top + 10 and player_rect.top < platform.bottom - 10):
                    if abs(player_rect.right - platform.left) < abs(player_rect.left - platform.right): collision_type = "right"
                    else: collision_type = "left"
                    collision_platform = platform; break
    return collision_type, collision_platform

def start_tutorial():
    global current_level_obj, game_state, is_tutorial, score, bullets_left, player_x, player_y, player_velocity_y, bullets, ghosts_killed, effects, floating_numbers, tutorial_messages, invincible_frames, player_health, max_player_health, run_stats
    player_x, player_y, player_velocity_y, score, bullets_left, ghosts_killed = 150, 500, 0, 0, 5, 0
    player_health = max_player_health
    run_stats = {"coins_collected": 0, "enemies_killed": 0, "damage_taken": 0, "double_jumps": 0}
    bullets.clear(); effects.clear(); floating_numbers.clear(); tutorial_messages.clear()
    invincible_frames = invincible_duration
    is_tutorial = True
    current_level_obj = Level(0, is_tutorial=True)
    game_state = GameState.TUTORIAL
    add_tutorial_message("ДОБРО ПОЖАЛОВАТЬ В ОБУЧЕНИЕ!", 120)
    add_tutorial_message("Используйте A и D для движения влево/вправо", 180)
    add_tutorial_message("Нажмите ПРОБЕЛ чтобы прыгнуть", 180)
    add_tutorial_message("Двойной прыжок в воздухе для большей высоты!", 180)
    add_tutorial_message("Нажмите B чтобы стрелять по призракам", 180)
    add_tutorial_message("Нажмите R чтобы перезарядить патроны", 180)
    add_tutorial_message("Собирайте монеты для очков!", 180)
    add_tutorial_message("Пройдите уровень чтобы начать игру!", 200)

def load_level(level_num):
    global current_level, current_level_obj, gravity, score, bullets_left, ghosts_killed, bullets, effects, floating_numbers, is_tutorial, invincible_frames, player_x, player_y, player_velocity_y, is_on_ground, player_health, max_player_health, run_stats
    current_level = level_num
    is_tutorial = False
    current_level_obj = Level(level_num)
    gravity = current_level_obj.gravity
    player_x, player_y, player_velocity_y, is_on_ground = 150, 500, 0, True
    score, bullets_left, ghosts_killed = 0, 5, 0
    player_health = max_player_health
    run_stats = {"coins_collected": 0, "enemies_killed": 0, "damage_taken": 0, "double_jumps": 0}
    bullets.clear(); effects.clear(); floating_numbers.clear()
    invincible_frames = invincible_duration
    pygame.time.set_timer(ghost_timer, current_level_obj.ghost_spawn_delay)
    game_state = GameState.PLAYING

def complete_tutorial():
    global game_state, unlocked_levels
    if unlocked_levels < 1: unlocked_levels = 1
    unlock_achievement("TUTORIAL_DONE")
    save_game_progress(unlocked_levels, best_scores, unlocked_achievements)
    game_state = GameState.MAIN_MENU

def next_level():
    global current_level, level_complete, level_transition, level_transition_timer, game_state, unlocked_levels, best_scores, is_tutorial, invincible_frames
    if is_tutorial:
        complete_tutorial()
        return False
    
    unlock_achievement(f"LEVEL_{current_level}")
    check_run_achievements()
    
    level_key = f"{current_level}_{current_difficulty.name}"
    if level_key not in best_scores or score > best_scores[level_key]: best_scores[level_key] = score
    if current_level < max_level and current_level + 1 > unlocked_levels:
        unlocked_levels = current_level + 1
        save_game_progress(unlocked_levels, best_scores, unlocked_achievements)
    if current_level < max_level:
        current_level += 1
        level_complete, level_transition = True, True
        level_transition_timer = pygame.time.get_ticks()
        load_level(current_level)
        return True
    else:
        game_state = GameState.GAME_WIN
        return False

def draw_level_transition():
    if is_tutorial:
        screen.fill((200, 230, 255))
        level_text = level_font.render("ОБУЧЕНИЕ ПРОЙДЕНО!", True, (0, 200, 0))
        next_text = label.render("Возврат в меню...", True, (50, 50, 50))
        screen.blit(level_text, (1280 // 2 - level_text.get_width() // 2, 300))
        screen.blit(next_text, (1280 // 2 - next_text.get_width() // 2, 400))
    else:
        current_bg = backgrounds.get(current_level_obj.theme, backgrounds["tutorial"])
        screen.blit(current_bg, (0, 0))
        level_text = level_font.render(f"LEVEL {current_level} - {current_level_obj.theme.upper()}!", True, (255, 215, 0))
        next_text = label.render("Get ready for next level...", True, (255, 255, 255))
        screen.blit(level_text, (1280 // 2 - level_text.get_width() // 2, 300))
        screen.blit(next_text, (1280 // 2 - next_text.get_width() // 2, 400))

def draw_hud():
    if is_tutorial: level_text = ammo_font.render("ОБУЧЕНИЕ", True, (255, 255, 0))
    else: level_text = ammo_font.render(f"Уровень: {current_level}/{max_level}", True, (255, 255, 255))
    progress_text = ammo_font.render(f"Прогресс: {score}/{current_level_obj.goal_score}", True, (255, 255, 255))
    if bullets_infinite: ammo_text = ammo_font.render(f"Патроны: БЕСКОНЕЧНО", True, (0, 255, 0))
    else: ammo_text = ammo_font.render(f"Патроны: {bullets_left}", True, (255, 255, 255))
    score_text = ammo_font.render(f"Очки: {score}", True, (255, 215, 0))
    diff_settings = DIFFICULTY_SETTINGS[current_difficulty]
    diff_text = small_font.render(f"Сложность: {diff_settings['name']}", True, diff_settings["color"])
    y_offset = 10
    screen.blit(level_text, (10, y_offset))
    screen.blit(progress_text, (10, y_offset + 40))
    screen.blit(ammo_text, (10, y_offset + 80))
    screen.blit(score_text, (10, y_offset + 120))
    screen.blit(diff_text, (10, y_offset + 160))
    health_text = ammo_font.render(f"HP: {player_health}/{max_player_health}", True, (255, 50, 50))
    screen.blit(health_text, (10, y_offset + 200))
    info_offset = 240
    if player_speed_multiplier > 1.0:
        speed_text = ammo_font.render("УСКОРЕНИЕ!", True, (255, 255, 0))
        screen.blit(speed_text, (10, y_offset + info_offset)); info_offset += 40
    if double_points:
        points_text = ammo_font.render("x2 ОЧКИ!", True, (255, 165, 0))
        screen.blit(points_text, (10, y_offset + info_offset)); info_offset += 40
    if invincible_frames > 0:
        invincible_text = ammo_font.render("НЕУЯЗВИМОСТЬ", True, (100, 200, 255))
        screen.blit(invincible_text, (10, y_offset + info_offset))
    esc_hint = small_font.render("ESC - Пауза", True, (200, 200, 200))
    screen.blit(esc_hint, (1280 - esc_hint.get_width() - 10, 10))

def draw_main_menu():
    if main_menu_bg: screen.blit(main_menu_bg, (0, 0))
    else: screen.fill((100, 150, 255))
    for effect in effects[:]:
        if not effect.update(): effects.remove(effect)
        else: effect.draw(screen)
    if random.random() < 0.3: effects.append(Effect(random.randint(0, 1280), random.randint(0, 720), random.choice(["coin_collect", "ghost_death"])))
    title_text = title_font.render("MINI MARIO", True, (255, 215, 0))
    screen.blit(title_text, (1280 // 2 - title_text.get_width() // 2, 20))
    subtitle_text = label.render("Advanced Platformer", True, (255, 255, 255))
    screen.blit(subtitle_text, (1280 // 2 - subtitle_text.get_width() // 2, 100))
    
    start_text = menu_font.render("Начать игру", True, (255, 255, 255))
    level_text = menu_font.render("Выбор уровня", True, (255, 255, 255))
    achievements_text = menu_font.render("Достижения", True, (255, 255, 255))
    settings_text = menu_font.render("Настройки", True, (255, 255, 255))
    quit_text = menu_font.render("Выход", True, (255, 255, 255))
    
    button_padding_x, button_padding_y, button_spacing = 50, 15, 40
    max_text_width = max(start_text.get_width(), level_text.get_width(), achievements_text.get_width(), settings_text.get_width(), quit_text.get_width())
    fixed_button_width = max_text_width + button_padding_x * 2
    fixed_button_height = 60
    start_y, center_x = 180, 1280 // 2

    start_button = pygame.Rect(center_x - fixed_button_width // 2, start_y, fixed_button_width, fixed_button_height)
    y = start_y + fixed_button_height + button_spacing
    level_select_button = pygame.Rect(center_x - fixed_button_width // 2, y, fixed_button_width, fixed_button_height)
    y += fixed_button_height + button_spacing
    achievements_button = pygame.Rect(center_x - fixed_button_width // 2, y, fixed_button_width, fixed_button_height)
    y += fixed_button_height + button_spacing
    settings_button = pygame.Rect(center_x - fixed_button_width // 2, y, fixed_button_width, fixed_button_height)
    y += fixed_button_height + button_spacing
    quit_button = pygame.Rect(center_x - fixed_button_width // 2, y, fixed_button_width, fixed_button_height)
    
    mouse_pos = pygame.mouse.get_pos()
    def draw_btn(rect, text_surf, hover_color, normal_color, border_color):
        if rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, hover_color, rect, border_radius=8)
            pygame.draw.rect(screen, (255, 255, 255), rect, 3, border_radius=8)
        else:
            pygame.draw.rect(screen, normal_color, rect, border_radius=8)
            pygame.draw.rect(screen, border_color, rect, 3, border_radius=8)
        screen.blit(text_surf, (rect.centerx - text_surf.get_width() // 2, rect.centery - text_surf.get_height() // 2))
    
    draw_btn(start_button, start_text, (70, 220, 70), (50, 200, 50), (0, 100, 0))
    tutorial_note = small_font.render("(с обучения)", True, (200, 255, 200))
    screen.blit(tutorial_note, (start_button.centerx - tutorial_note.get_width() // 2, start_button.bottom + 3))
    draw_btn(level_select_button, level_text, (220, 120, 70), (200, 100, 50), (100, 50, 0))
    draw_btn(achievements_button, achievements_text, (220, 200, 70), (200, 180, 50), (100, 90, 0))
    draw_btn(settings_button, settings_text, (100, 150, 220), (70, 120, 200), (30, 60, 130))
    draw_btn(quit_button, quit_text, (220, 70, 70), (200, 50, 50), (100, 0, 0))
    
    diff_settings = DIFFICULTY_SETTINGS[current_difficulty]
    current_diff_text = label.render(f"Сложность: {diff_settings['name']}", True, diff_settings["color"])
    screen.blit(current_diff_text, (1280 // 2 - current_diff_text.get_width() // 2, quit_button.bottom + 25))
    progress_text = small_font.render(f"Уровней открыто: {unlocked_levels}/{max_level}", True, (255, 255, 200))
    screen.blit(progress_text, (10, 690))
    return start_button, level_select_button, achievements_button, settings_button, quit_button

def draw_settings():
    if settings_bg: screen.blit(settings_bg, (0, 0))
    else: screen.fill((40, 40, 80))
    title_text = level_font.render("НАСТРОЙКИ", True, (255, 215, 0))
    screen.blit(title_text, (1280 // 2 - title_text.get_width() // 2, 20))
    controls_rect = pygame.Rect(60, 110, 560, 450)
    pygame.draw.rect(screen, (60, 60, 100), controls_rect)
    pygame.draw.rect(screen, (150, 150, 200), controls_rect, 3)
    controls_title = menu_font.render("УПРАВЛЕНИЕ", True, (255, 220, 100))
    screen.blit(controls_title, (controls_rect.centerx - controls_title.get_width() // 2, 125))
    controls_list = [("A / D", "Движение"), ("ПРОБЕЛ", "Прыжок"), ("B", "Стрельба"), ("R", "Перезарядка"), ("ESC", "Пауза")]
    y, line_padding = 180, 12
    for key_name, description in controls_list:
        key_text = label.render(key_name, True, (100, 220, 255))
        desc_text = ammo_font.render("— " + description, True, (230, 230, 230))
        row_height = max(key_text.get_height(), desc_text.get_height())
        screen.blit(key_text, (controls_rect.x + 30, y + (row_height - key_text.get_height()) // 2))
        screen.blit(desc_text, (controls_rect.x + 200, y + (row_height - desc_text.get_height()) // 2))
        y += row_height + line_padding
    diff_rect = pygame.Rect(660, 110, 560, 450)
    pygame.draw.rect(screen, (60, 60, 100), diff_rect)
    pygame.draw.rect(screen, (150, 150, 200), diff_rect, 3)
    diff_title = menu_font.render("СЛОЖНОСТЬ", True, (255, 220, 100))
    screen.blit(diff_title, (diff_rect.centerx - diff_title.get_width() // 2, 125))
    diff_buttons = {}
    btn_width, btn_height, btn_spacing = 150, 50, 20
    total_w = btn_width * 3 + btn_spacing * 2
    start_x = diff_rect.x + (diff_rect.width - total_w) // 2
    btn_y = 190
    mouse_pos = pygame.mouse.get_pos()
    difficulties = [Difficulty.EASY, Difficulty.NORMAL, Difficulty.HARD]
    for i, diff in enumerate(difficulties):
        settings = DIFFICULTY_SETTINGS[diff]
        x = start_x + i * (btn_width + btn_spacing)
        button_rect = pygame.Rect(x, btn_y, btn_width, btn_height)
        diff_buttons[diff] = button_rect
        is_hover, is_selected = button_rect.collidepoint(mouse_pos), (diff == current_difficulty)
        bg_color = (min(255, settings["color"][0] // 3 + (30 if is_hover else 0)), min(255, settings["color"][1] // 3 + (30 if is_hover else 0)), min(255, settings["color"][2] // 3 + (30 if is_hover else 0)))
        pygame.draw.rect(screen, bg_color, button_rect, border_radius=8)
        pygame.draw.rect(screen, settings["color"] if is_selected else (150, 150, 150), button_rect, 4 if is_selected else 2, border_radius=8)
        name_text = label.render(settings["name"], True, settings["color"])
        if name_text.get_width() > btn_width - 20:
            scale = (btn_width - 20) / name_text.get_width()
            name_text = pygame.transform.scale(name_text, (int(name_text.get_width() * scale), int(name_text.get_height() * scale)))
        screen.blit(name_text, (x + btn_width // 2 - name_text.get_width() // 2, btn_y + btn_height // 2 - name_text.get_height() // 2))
        if is_selected:
            check_text = small_font.render("✓ выбрано", True, settings["color"])
            screen.blit(check_text, (x + btn_width // 2 - check_text.get_width() // 2, btn_y + btn_height + 8))
    current_settings = DIFFICULTY_SETTINGS[current_difficulty]
    desc_y = 280
    desc_text_original = small_font.render(current_settings["description"], True, (220, 220, 220))
    max_width = diff_rect.width - 40
    if desc_text_original.get_width() > max_width:
        words = current_settings["description"].split()
        line1, line2 = " ".join(words[:len(words)//2]), " ".join(words[len(words)//2:])
        screen.blit(small_font.render(line1, True, (220, 220, 220)), (diff_rect.centerx - small_font.render(line1, True, (220, 220, 220)).get_width() // 2, desc_y))
        screen.blit(small_font.render(line2, True, (220, 220, 220)), (diff_rect.centerx - small_font.render(line2, True, (220, 220, 220)).get_width() // 2, desc_y + 22))
        desc_y += 50
    else:
        screen.blit(desc_text_original, (diff_rect.centerx - desc_text_original.get_width() // 2, desc_y))
        desc_y += 50
    details = [f"Очки: x{current_settings['score_mult']}", f"Враги: x{current_settings['spawn_mult']:.2f}", f"Макс: {current_settings['max_enemies']}", f"HP: x{current_settings['health_mult']}", f"Скорость: x{current_settings['scroll_mult']}"]
    y = desc_y
    for detail in details:
        detail_text = small_font.render(detail, True, (180, 180, 220))
        text_x = max(diff_rect.x + 10, diff_rect.centerx - detail_text.get_width() // 2)
        screen.blit(detail_text, (text_x, y))
        y += detail_text.get_height() + 6
    back_button = pygame.Rect(540, 580, 200, 55)
    if back_button.collidepoint(mouse_pos):
        pygame.draw.rect(screen, (200, 80, 80), back_button, border_radius=8)
        pygame.draw.rect(screen, (255, 255, 255), back_button, 3, border_radius=8)
    else:
        pygame.draw.rect(screen, (150, 50, 50), back_button, border_radius=8)
        pygame.draw.rect(screen, (255, 255, 255), back_button, 2, border_radius=8)
    screen.blit(menu_font.render("Назад", True, (255, 255, 255)), (back_button.centerx - menu_font.render("Назад", True, (255, 255, 255)).get_width() // 2, back_button.centery - menu_font.render("Назад", True, (255, 255, 255)).get_height() // 2))
    screen.blit(small_font.render("Сложность применяется к новым играм", True, (255, 255, 255)), (1280 // 2 - small_font.render("Сложность применяется к новым играм", True, (255, 255, 255)).get_width() // 2, 650))
    return diff_buttons, back_button

def draw_pause_menu():
    if pause_menu_bg: screen.blit(pause_menu_bg, (0, 0))
    else:
        for i in range(720): pygame.draw.line(screen, (20 + i//10, 15 + i//15, 40 + i//8), (0, i), (1280, i))
    overlay = pygame.Surface((1280, 720)); overlay.set_alpha(180); overlay.fill((0, 0, 0)); screen.blit(overlay, (0, 0))
    pause_text = title_font.render("ПАУЗА", True, (255, 215, 0))
    shadow_text = title_font.render("ПАУЗА", True, (100, 80, 0))
    screen.blit(shadow_text, (1280 // 2 - pause_text.get_width() // 2 + 4, 184))
    screen.blit(pause_text, (1280 // 2 - pause_text.get_width() // 2, 180))
    button_width, button_height, button_spacing, start_y, center_x = 420, 65, 25, 320, 1280 // 2
    continue_button = pygame.Rect(center_x - button_width // 2, start_y, button_width, button_height)
    settings_button = pygame.Rect(center_x - button_width // 2, start_y + button_height + button_spacing, button_width, button_height)
    menu_button = pygame.Rect(center_x - button_width // 2, start_y + 2 * (button_height + button_spacing), button_width, button_height)
    mouse_pos = pygame.mouse.get_pos()
    def draw_btn(rect, text_surf, hover_color, normal_color):
        if rect.collidepoint(mouse_pos): pygame.draw.rect(screen, hover_color, rect); pygame.draw.rect(screen, (255, 255, 255), rect, 3)
        else: pygame.draw.rect(screen, normal_color, rect); pygame.draw.rect(screen, (200, 200, 200), rect, 2)
        screen.blit(text_surf, (rect.centerx - text_surf.get_width() // 2, rect.centery - text_surf.get_height() // 2))
    draw_btn(continue_button, menu_font.render("Продолжить", True, (255, 255, 255)), (80, 200, 80), (50, 150, 50))
    draw_btn(settings_button, menu_font.render("Настройки", True, (255, 255, 255)), (100, 150, 220), (70, 120, 200))
    draw_btn(menu_button, menu_font.render("В главное меню", True, (255, 255, 255)), (200, 80, 80), (150, 50, 50))
    screen.blit(small_font.render("Нажмите ESC чтобы продолжить", True, (200, 200, 200)), (1280 // 2 - small_font.render("Нажмите ESC чтобы продолжить", True, (200, 200, 200)).get_width() // 2, 660))
    return continue_button, settings_button, menu_button

def draw_level_select():
    if level_select_bg: screen.blit(level_select_bg, (0, 0))
    else: screen.fill((50, 50, 100))
    screen.blit(level_font.render("ВЫБОР УРОВНЯ", True, (255, 215, 0)), (1280 // 2 - level_font.render("ВЫБОР УРОВНЯ", True, (255, 215, 0)).get_width() // 2, 30))
    diff_settings = DIFFICULTY_SETTINGS[current_difficulty]
    screen.blit(label.render(f"Сложность: {diff_settings['name']}", True, diff_settings["color"]), (1280 // 2 - label.render(f"Сложность: {diff_settings['name']}", True, diff_settings["color"]).get_width() // 2, 110))
    level_buttons.clear()
    button_width, button_height = 240, 170
    total_height = 2 * button_height + 50
    start_y = (720 - total_height) // 2 + 20
    level_positions = {1: {"x": 220, "y": start_y}, 2: {"x": 480, "y": start_y}, 3: {"x": 740, "y": start_y}, 4: {"x": 350, "y": start_y + button_height + 50}, 5: {"x": 610, "y": start_y + button_height + 50}}
    themes_names = {1: "Forest", 2: "Desert", 3: "Ice", 4: "Volcano", 5: "Final"}
    for i in range(1, max_level + 1):
        x, y = level_positions[i]["x"], level_positions[i]["y"]
        button_rect = pygame.Rect(x, y, button_width, button_height)
        level_buttons.append(button_rect)
        is_unlocked = i <= unlocked_levels
        if is_unlocked:
            for j in range(button_height): pygame.draw.line(screen, (100 + int(j * 0.3), 130 + int(j * 0.2), 180), (x, y + j), (x + button_width, y + j))
            border_color, text_color = (255, 215, 0), (255, 255, 255)
        else:
            pygame.draw.rect(screen, (60, 60, 70), button_rect)
            border_color, text_color = (80, 80, 80), (150, 150, 150)
        pygame.draw.rect(screen, border_color, button_rect, 3)
        screen.blit(label.render(f"УРОВЕНЬ {i}", True, text_color), (x + button_width // 2 - label.render(f"УРОВЕНЬ {i}", True, text_color).get_width() // 2, y + 40))
        screen.blit(label.render(themes_names[i], True, (220, 220, 220)), (x + button_width // 2 - label.render(themes_names[i], True, (220, 220, 220)).get_width() // 2, y + 80))
        level_key = f"{i}_{current_difficulty.name}"
        if level_key in best_scores and is_unlocked: screen.blit(small_font.render(f"Рекорд: {best_scores[level_key]}", True, (255, 215, 0)), (x + button_width // 2 - small_font.render(f"Рекорд: {best_scores[level_key]}", True, (255, 215, 0)).get_width() // 2, y + 125))
        if not is_unlocked: screen.blit(level_font.render("🔒", True, (200, 50, 50)), (x + button_width // 2 - level_font.render("🔒", True, (200, 50, 50)).get_width() // 2, y + 70))
    back_button = pygame.Rect(540, 620, 200, 50)
    mouse_pos = pygame.mouse.get_pos()
    if back_button.collidepoint(mouse_pos): pygame.draw.rect(screen, (200, 80, 80), back_button); pygame.draw.rect(screen, (255, 255, 255), back_button, 3)
    else: pygame.draw.rect(screen, (150, 50, 50), back_button); pygame.draw.rect(screen, (255, 255, 255), back_button, 2)
    screen.blit(menu_font.render("Назад", True, (255, 255, 255)), (back_button.centerx - menu_font.render("Назад", True, (255, 255, 255)).get_width() // 2, back_button.centery - menu_font.render("Назад", True, (255, 255, 255)).get_height() // 2))
    screen.blit(small_font.render(f"Открыто уровней: {unlocked_levels}/{max_level}", True, (255, 255, 200)), (10, 690))
    return back_button

current_level_obj = Level(1)
running = True

while running:
    if game_state == GameState.MAIN_MENU:
        start_btn, level_btn, ach_btn, settings_btn, quit_btn = draw_main_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if start_btn.collidepoint(mouse_pos): start_tutorial()
                elif level_btn.collidepoint(mouse_pos): game_state = GameState.LEVEL_SELECT
                elif ach_btn.collidepoint(mouse_pos): game_state = GameState.ACHIEVEMENTS
                elif settings_btn.collidepoint(mouse_pos): settings_return_to = GameState.MAIN_MENU; game_state = GameState.SETTINGS
                elif quit_btn.collidepoint(mouse_pos): running = False

    elif game_state == GameState.ACHIEVEMENTS:
        back_btn = draw_achievements_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.collidepoint(pygame.mouse.get_pos()): game_state = GameState.MAIN_MENU

    elif game_state == GameState.SETTINGS:
        diff_buttons, back_btn = draw_settings()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for diff, rect in diff_buttons.items():
                    if rect.collidepoint(mouse_pos): current_difficulty = diff
                if back_btn.collidepoint(mouse_pos): game_state = settings_return_to

    elif game_state == GameState.PAUSED:
        cont_btn, pause_settings_btn, menu_btn = draw_pause_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: game_state = GameState.PLAYING if not is_tutorial else GameState.TUTORIAL
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if cont_btn.collidepoint(mouse_pos): game_state = GameState.PLAYING if not is_tutorial else GameState.TUTORIAL
                elif pause_settings_btn.collidepoint(mouse_pos): settings_return_to = GameState.PAUSED; game_state = GameState.SETTINGS
                elif menu_btn.collidepoint(mouse_pos): game_state = GameState.MAIN_MENU

    elif game_state == GameState.LEVEL_SELECT:
        back_button = draw_level_select()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for i, button_rect in enumerate(level_buttons):
                    if button_rect.collidepoint(mouse_pos):
                        level_num = i + 1
                        if level_num <= unlocked_levels: load_level(level_num); game_state = GameState.PLAYING
                if back_button.collidepoint(mouse_pos): game_state = GameState.MAIN_MENU

    elif game_state == GameState.TUTORIAL or game_state == GameState.PLAYING:
        if speed_boost_timer > 0:
            speed_boost_timer -= 1
            if speed_boost_timer <= 0: player_speed_multiplier = 1.0
        if infinite_ammo_timer > 0:
            infinite_ammo_timer -= 1
            if infinite_ammo_timer <= 0: bullets_infinite = False
        if double_points_timer > 0:
            double_points_timer -= 1
            if double_points_timer <= 0: double_points = False
        
        current_bg = backgrounds.get(current_level_obj.theme, backgrounds["tutorial"])
        screen.blit(current_bg, (bg_x, 0)); screen.blit(current_bg, (bg_x + 1280, 0))
        for effect in effects[:]:
            if not effect.update(): effects.remove(effect)
            else: effect.draw(screen)
        for floating_number in floating_numbers[:]:
            if not floating_number.update(): floating_numbers.remove(floating_number)
            else: floating_number.draw(screen)
        
        if not level_complete and score >= current_level_obj.goal_score: next_level()
        if level_transition:
            draw_level_transition()
            if pygame.time.get_ticks() - level_transition_timer > 2000: level_transition, level_complete = False, False
            pygame.display.update(); continue
        
        bg_x -= current_level_obj.scroll_speed
        if bg_x <= -1280: bg_x = 0
        for platform in current_level_obj.platforms: platform.x -= current_level_obj.scroll_speed
        current_level_obj.platforms = [p for p in current_level_obj.platforms if p.x + p.width > 0]
        if not is_tutorial and current_level_obj.platforms and current_level_obj.platforms[-1].x < 400:
            if random.random() < 0.6:
                new_x, new_y, new_width = 1280, random.choice([500, 450, 400, 350]), random.randint(150, 250)
                new_platform = pygame.Rect(new_x, new_y, new_width, 20)
                overlap = False
                for platform in current_level_obj.platforms:
                    if new_platform.colliderect(platform) and abs(new_platform.y - platform.y) < 50: overlap = True; break
                if not overlap: current_level_obj.platforms.append(new_platform)
        
        for platform in current_level_obj.platforms:
            if current_level_obj.theme == "tutorial": pygame.draw.rect(screen, (100, 200, 100), platform); pygame.draw.rect(screen, (50, 150, 50), platform, 2)
            elif current_level_obj.theme == "ice": pygame.draw.rect(screen, (173, 216, 230), platform); pygame.draw.rect(screen, (135, 206, 235), platform, 2)
            elif current_level_obj.theme == "desert": pygame.draw.rect(screen, (210, 180, 140), platform); pygame.draw.rect(screen, (160, 130, 90), platform, 2)
            elif current_level_obj.theme == "volcano": pygame.draw.rect(screen, (180, 60, 30), platform); pygame.draw.rect(screen, (255, 100, 50), platform, 2)
            elif current_level_obj.theme == "final": pygame.draw.rect(screen, (100, 50, 150), platform); pygame.draw.rect(screen, (200, 100, 255), platform, 2)
            else: pygame.draw.rect(screen, (139, 69, 19), platform); pygame.draw.rect(screen, (101, 50, 12), platform, 2)
        
        player_rect = walk_left[0].get_rect(topleft=(player_x, player_y))
        coins_to_remove = []
        for i, coin in enumerate(current_level_obj.coins):
            screen.blit(coin_img, coin); coin.x -= current_level_obj.scroll_speed
            if coin.x + coin.width < 0: coins_to_remove.append(i); continue
            if player_rect.colliderect(coin):
                coins_to_remove.append(i)
                points = 20 if double_points else 10
                score += points
                run_stats["coins_collected"] += 1
                effects.append(Effect(coin.x + 15, coin.y + 15, "coin_collect"))
                floating_numbers.append(FloatingNumber(coin.x, coin.y, points, (255, 215, 0)))
        for i in sorted(coins_to_remove, reverse=True):
            if i < len(current_level_obj.coins): current_level_obj.coins.pop(i)
        
        powerups_to_remove = []
        for i, powerup in enumerate(current_level_obj.powerups):
            if not powerup.update(current_level_obj.scroll_speed): powerups_to_remove.append(i); continue
            powerup.draw(screen)
            if player_rect.colliderect(powerup.rect):
                powerups_to_remove.append(i)
                effects.append(Effect(powerup.rect.x, powerup.rect.y, "powerup"))
                if powerup.type == "speed":
                    player_speed_multiplier, speed_boost_timer = 1.5, 600
                    floating_numbers.append(FloatingNumber(powerup.rect.x, powerup.rect.y, "Скорость", (255, 255, 0)))
                    if is_tutorial: add_tutorial_message("УСКОРЕНИЕ! Вы двигаетесь быстрее!", 120)
                elif powerup.type == "infinite_ammo":
                    bullets_infinite, infinite_ammo_timer = True, 600
                    floating_numbers.append(FloatingNumber(powerup.rect.x, powerup.rect.y, "∞ Патроны", (0, 255, 255)))
                    if is_tutorial: add_tutorial_message("БЕСКОНЕЧНЫЕ ПАТРОНЫ! Перезарядка не нужна!", 120)
                elif powerup.type == "extra_life":
                    if player_health < max_player_health:
                        player_health += 1
                        floating_numbers.append(FloatingNumber(powerup.rect.x, powerup.rect.y, "1 HP", (255, 0, 0)))
                        if is_tutorial: add_tutorial_message("Восстановление HP! +1 здоровье!", 120)
                    else:
                        score += 100
                        floating_numbers.append(FloatingNumber(powerup.rect.x, powerup.rect.y, 100, (255, 0, 0)))
                        if is_tutorial: add_tutorial_message("HP полное! Получите +100 очков!", 120)
                elif powerup.type == "double_points":
                    double_points, double_points_timer = True, 600
                    floating_numbers.append(FloatingNumber(powerup.rect.x, powerup.rect.y, "x2 Очки", (255, 165, 0)))
                    if is_tutorial: add_tutorial_message("УДВОЕНИЕ ОЧКОВ! В два раза больше за убийства!", 120)
        for i in sorted(powerups_to_remove, reverse=True):
            if i < len(current_level_obj.powerups): current_level_obj.powerups.pop(i)
        
        enemies_to_remove = []
        for i, enemy in enumerate(current_level_obj.enemies):
            if not enemy.update(current_level_obj.scroll_speed, current_level_obj.platforms): enemies_to_remove.append(i); continue
            enemy.draw(screen)
            if player_rect.colliderect(enemy.rect) and invincible_frames <= 0:
                player_health -= 1
                run_stats["damage_taken"] += 1
                invincible_frames = invincible_duration
                if is_tutorial: add_tutorial_message("Ой! Вас ударил призрак! Осталось HP: " + str(player_health), 180)
                if player_health <= 0: game_state = GameState.GAME_OVER
        for i in sorted(enemies_to_remove, reverse=True):
            if i < len(current_level_obj.enemies): current_level_obj.enemies.pop(i)
        
        keys = pygame.key.get_pressed()
        current_speed = player_speed * player_speed_multiplier
        if keys[pygame.K_a] and player_x > 50: player_x -= current_speed
        elif keys[pygame.K_d] and player_x < 1200: player_x += current_speed
        
        if invincible_frames > 0:
            if (invincible_frames // 3) % 2 == 0:
                if keys[pygame.K_a]: screen.blit(walk_left[player_anim_count], (player_x, player_y))
                else: screen.blit(walk_right[player_anim_count], (player_x, player_y))
        else:
            if keys[pygame.K_a]: screen.blit(walk_left[player_anim_count], (player_x, player_y))
            else: screen.blit(walk_right[player_anim_count], (player_x, player_y))
        
        if (keys[pygame.K_a] or keys[pygame.K_d]) and is_on_ground: player_anim_count = (player_anim_count + 1) % 4
        
        player_rect.x = player_x
        side_collision, side_platform = check_platform_collision(player_rect, check_vertical=False)
        if side_collision == "right": player_x = side_platform.left - player_rect.width
        elif side_collision == "left": player_x = side_platform.right
        
        player_velocity_y += gravity; player_y += player_velocity_y; player_rect.y = player_y
        collision_type, collision_platform = check_platform_collision(player_rect, check_vertical=True)
        if collision_type == "top" and not was_on_ground: effects.append(Effect(player_x + 35, player_y + 50, "land"))
        if collision_type == "top":
            player_y, player_velocity_y, is_jumping, is_on_ground = collision_platform.top - player_rect.height, 0, False, True
            double_jump_available, has_double_jumped = False, False
        elif collision_type == "bottom":
            player_y, player_velocity_y = collision_platform.bottom, 0
            if double_jump_available: double_jump_available = False
        else:
            if player_y >= 500:
                player_y, player_velocity_y, is_jumping, is_on_ground = 500, 0, False, True
                double_jump_available, has_double_jumped = False, False
            else: is_on_ground = False
        was_on_ground = is_on_ground
        
        if keys[pygame.K_r] and not bullets_infinite:
            bullets_left = 5
            if is_tutorial: add_tutorial_message("Патроны перезаряжены! У вас 5 пуль!", 90)
        
        bullets_to_remove = []
        for i, el in enumerate(bullets):
            screen.blit(player_bullet, (el.x, el.y)); el.x += 20
            if el.x > 1282: bullets_to_remove.append(i); continue
            for index, enemy in enumerate(current_level_obj.enemies):
                if el.colliderect(enemy.rect):
                    bullets_to_remove.append(i)
                    if enemy.take_damage():
                        current_level_obj.enemies.pop(index)
                        ghosts_killed += 1
                        run_stats["enemies_killed"] += 1
                        if enemy.type == "boss" and current_level == 5:
                            score = current_level_obj.goal_score
                        if ghosts_killed == 1: unlock_achievement("FIRST_KILL")
                        if enemy.type == "tank": points = 150 if double_points else 75
                        elif enemy.type == "soldier": points = 100 if double_points else 50
                        elif enemy.type == "boss": points = 1000 if double_points else 750
                        else: points = 50 if double_points else 25
                        score += points
                        effects.append(Effect(enemy.rect.x + enemy.rect.width // 2, enemy.rect.y + enemy.rect.height // 2, "ghost_death"))
                        floating_numbers.append(FloatingNumber(enemy.rect.x, enemy.rect.y, points, (200, 100, 255)))
                        if is_tutorial and ghosts_killed == 1: add_tutorial_message("Отлично! Вы убили моба!", 120)
                    break
        for i in sorted(bullets_to_remove, reverse=True):
            if i < len(bullets): bullets.pop(i)
        
        if invincible_frames > 0: invincible_frames -= 1
        
        enemy_bullets_to_remove = []
        for i, bullet in enumerate(enemy_bullets):
            if not bullet.update():
                enemy_bullets_to_remove.append(i)
                continue
            bullet.draw(screen)
            if player_rect.colliderect(bullet.rect) and invincible_frames <= 0:
                player_health -= 1
                run_stats["damage_taken"] += 1
                invincible_frames = invincible_duration
                effects.append(Effect(player_rect.centerx, player_rect.centery, "ghost_death"))
                if player_health <= 0: game_state = GameState.GAME_OVER
                enemy_bullets_to_remove.append(i)
        for i in sorted(enemy_bullets_to_remove, reverse=True):
            if i < len(enemy_bullets): enemy_bullets.pop(i)

        draw_hud()
        if is_tutorial: draw_tutorial_hints()
    
    elif game_state == GameState.GAME_OVER:
        if lose_bg: screen.blit(lose_bg, (0, 0))
        else:
            for i in range(720): pygame.draw.line(screen, (255 - i//4, 30, 30), (0, i), (1280, i))
        overlay = pygame.Surface((1280, 720)); overlay.set_alpha(200); overlay.fill((0, 0, 0)); screen.blit(overlay, (0, 0))
        game_over_text = level_font.render("GAME OVER", True, (255, 50, 50))
        shadow_text = level_font.render("GAME OVER", True, (100, 0, 0))
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.003)) * 10
        game_over_y, game_over_x = 50 + pulse, 1280 // 2 - game_over_text.get_width() // 2
        screen.blit(shadow_text, (game_over_x + 5, game_over_y + 5)); screen.blit(game_over_text, (game_over_x, game_over_y))
        
        line_width = 450
        line_x = (1280 - line_width) // 2
        line_y = game_over_y + game_over_text.get_height() + 20
        pygame.draw.line(screen, (255, 100, 100), (line_x, line_y), (line_x + line_width, line_y), 3)
        
        stats_width, stats_height = 650, 220
        stats_x, stats_y = (1280 - stats_width) // 2, line_y + 25
        stats_rect = pygame.Rect(stats_x, stats_y, stats_width, stats_height)
        for i in range(3): pygame.draw.rect(screen, (50 + i*20, 50 + i*20, 80 + i*20), (stats_x - i, stats_y - i, stats_width + i*2, stats_height + i*2), 2)
        pygame.draw.rect(screen, (100, 100, 150), stats_rect); pygame.draw.rect(screen, (150, 150, 200), stats_rect, 3)
        final_score_text = label.render(f"Итоговые очки: {score}", True, (255, 215, 0))
        ghosts_killed_text = label.render(f"Призраков убито: {ghosts_killed}", True, (200, 100, 255))
        diff_settings = DIFFICULTY_SETTINGS[current_difficulty]
        diff_text = label.render(f"Сложность: {diff_settings['name']}", True, diff_settings["color"])
        level_text = label.render("Обучение не пройдено", True, (100, 100, 255)) if is_tutorial else label.render(f"Пройдено уровней: {current_level}", True, (100, 100, 255))
        total_text_height = 50 * 4
        start_text_y = stats_y + (stats_height - total_text_height) // 2
        screen.blit(final_score_text, (1280 // 2 - final_score_text.get_width() // 2, start_text_y))
        screen.blit(ghosts_killed_text, (1280 // 2 - ghosts_killed_text.get_width() // 2, start_text_y + 50))
        screen.blit(level_text, (1280 // 2 - level_text.get_width() // 2, start_text_y + 100))
        screen.blit(diff_text, (1280 // 2 - diff_text.get_width() // 2, start_text_y + 150))
        button_width, button_height, button_spacing = 300, 60, 40
        total_buttons_width = button_width * 2 + button_spacing
        start_button_x = (1280 - total_buttons_width) // 2
        button_y = stats_y + stats_height + 30
        if button_y + button_height > 700: button_y = 630
        menu_button = pygame.Rect(start_button_x, button_y, button_width, button_height)
        level_select_btn = pygame.Rect(start_button_x + button_width + button_spacing, button_y, button_width, button_height)
        mouse_pos = pygame.mouse.get_pos()
        if menu_button.collidepoint(mouse_pos): pygame.draw.rect(screen, (80, 180, 230), menu_button); pygame.draw.rect(screen, (255, 255, 255), menu_button, 4)
        else: pygame.draw.rect(screen, (50, 150, 200), menu_button); pygame.draw.rect(screen, (0, 100, 150), menu_button, 4)
        screen.blit(label.render("Главное меню", True, (255, 255, 255)), (menu_button.centerx - label.render("Главное меню", True, (255, 255, 255)).get_width() // 2, menu_button.centery - label.render("Главное меню", True, (255, 255, 255)).get_height() // 2))
        if level_select_btn.collidepoint(mouse_pos): pygame.draw.rect(screen, (230, 130, 80), level_select_btn); pygame.draw.rect(screen, (255, 255, 255), level_select_btn, 4)
        else: pygame.draw.rect(screen, (200, 100, 50), level_select_btn); pygame.draw.rect(screen, (100, 50, 0), level_select_btn, 4)
        screen.blit(label.render("Выбор уровня", True, (255, 255, 255)), (level_select_btn.centerx - label.render("Выбор уровня", True, (255, 255, 255)).get_width() // 2, level_select_btn.centery - label.render("Выбор уровня", True, (255, 255, 255)).get_height() // 2))
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if menu_button.collidepoint(mouse_pos): game_state = GameState.MAIN_MENU
                elif level_select_btn.collidepoint(mouse_pos): game_state = GameState.LEVEL_SELECT

    elif game_state == GameState.GAME_WIN:
        if win_bg: screen.blit(win_bg, (0, 0))
        else:
            for i in range(720): pygame.draw.line(screen, (255, 200 + i//3, 100), (0, i), (1280, i))
            for i in range(720): pygame.draw.line(screen, (255, 200 + int(i * 0.07), 100), (0, i), (1280, i))
        if random.random() < 0.5:
            for _ in range(3): effects.append(Effect(random.randint(0, 1280), random.randint(0, 360), "coin_collect"))
        for effect in effects[:]:
            if not effect.update(): effects.remove(effect)
            else: effect.draw(screen)
        win_text = level_font.render("ПОБЕДА!", True, (255, 50, 50))
        shadow_win = level_font.render("ПОБЕДА!", True, (150, 0, 0))
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.002)) * 15
        win_y, win_x = 50 + pulse, 1280 // 2 - win_text.get_width() // 2
        screen.blit(shadow_win, (win_x + 5, win_y + 5)); screen.blit(win_text, (win_x, win_y))
        for i in range(8):
            angle = pygame.time.get_ticks() * 0.002 + i * math.pi / 4
            x, y = 1280 // 2 + math.cos(angle) * 180, win_y + 50 + math.sin(angle) * 40
            screen.blit(level_font.render("⭐", True, (255, 255, 100)), (x - 20, y - 20))
            
        # ИСПРАВЛЕННАЯ СТРОКА
        line_width = 450
        line_x = (1280 - line_width) // 2
        line_y = win_y + win_text.get_height() + 20
        pygame.draw.line(screen, (255, 100, 50), (line_x, line_y), (line_x + line_width, line_y), 3)
        
        stats_width, stats_height = 650, 180
        stats_x, stats_y = (1280 - stats_width) // 2, line_y + 25
        stats_rect = pygame.Rect(stats_x, stats_y, stats_width, stats_height)
        for i in range(3): pygame.draw.rect(screen, (255 - i*30, 215 - i*30, 0), (stats_x - i, stats_y - i, stats_width + i*2, stats_height + i*2), 2)
        pygame.draw.rect(screen, (255, 215, 0, 100), stats_rect); pygame.draw.rect(screen, (255, 200, 0), stats_rect, 3)
        final_score = label.render(f"Итоговые очки: {score}", True, (255, 100, 0))
        congrats_text = label.render("Поздравляем! Вы прошли игру!", True, (0, 100, 0))
        diff_settings = DIFFICULTY_SETTINGS[current_difficulty]
        diff_text = label.render(f"Сложность: {diff_settings['name']}", True, diff_settings["color"])
        total_text_height = 60 * 3
        start_text_y = stats_y + (stats_height - total_text_height) // 2
        screen.blit(final_score, (1280 // 2 - final_score.get_width() // 2, start_text_y))
        screen.blit(congrats_text, (1280 // 2 - congrats_text.get_width() // 2, start_text_y + 60))
        screen.blit(diff_text, (1280 // 2 - diff_text.get_width() // 2, start_text_y + 120))
        button_width, button_height, button_spacing = 300, 60, 40
        total_buttons_width = button_width * 2 + button_spacing
        start_button_x = (1280 - total_buttons_width) // 2
        button_y = stats_y + stats_height + 30
        if button_y + button_height > 700: button_y = 630
        menu_button = pygame.Rect(start_button_x, button_y, button_width, button_height)
        level_select_btn = pygame.Rect(start_button_x + button_width + button_spacing, button_y, button_width, button_height)
        mouse_pos = pygame.mouse.get_pos()
        if menu_button.collidepoint(mouse_pos): pygame.draw.rect(screen, (80, 180, 230), menu_button); pygame.draw.rect(screen, (255, 255, 255), menu_button, 4)
        else: pygame.draw.rect(screen, (50, 150, 200), menu_button); pygame.draw.rect(screen, (0, 100, 150), menu_button, 4)
        screen.blit(label.render("Главное меню", True, (255, 255, 255)), (menu_button.centerx - label.render("Главное меню", True, (255, 255, 255)).get_width() // 2, menu_button.centery - label.render("Главное меню", True, (255, 255, 255)).get_height() // 2))
        if level_select_btn.collidepoint(mouse_pos): pygame.draw.rect(screen, (230, 130, 80), level_select_btn); pygame.draw.rect(screen, (255, 255, 255), level_select_btn, 4)
        else: pygame.draw.rect(screen, (200, 100, 50), level_select_btn); pygame.draw.rect(screen, (100, 50, 0), level_select_btn, 4)
        screen.blit(label.render("Выбор уровня", True, (255, 255, 255)), (level_select_btn.centerx - label.render("Выбор уровня", True, (255, 255, 255)).get_width() // 2, level_select_btn.centery - label.render("Выбор уровня", True, (255, 255, 255)).get_height() // 2))
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if menu_button.collidepoint(mouse_pos): game_state = GameState.MAIN_MENU
                elif level_select_btn.collidepoint(mouse_pos): game_state = GameState.LEVEL_SELECT

    draw_achievement_popup()
    pygame.display.update()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if (game_state == GameState.PLAYING or game_state == GameState.TUTORIAL):
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: game_state = GameState.PAUSED
        if (game_state == GameState.TUTORIAL or game_state == GameState.PLAYING):
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if not is_jumping and is_on_ground:
                    player_velocity_y, is_jumping, is_on_ground = jump_strength, True, False
                    double_jump_available, has_double_jumped = True, False
                    effects.append(Effect(player_x + 35, player_y + 50, "jump"))
                    if is_tutorial: add_tutorial_message("Хороший прыжок! Снова нажмите пробел в воздухе для двойного прыжка!", 120)
                elif double_jump_available and not has_double_jumped and is_jumping:
                    player_velocity_y, double_jump_available, has_double_jumped = jump_strength * 0.9, False, True
                    run_stats["double_jumps"] += 1
                    effects.append(Effect(player_x + 35, player_y + 50, "jump"))
                    if is_tutorial: add_tutorial_message("Двойной прыжок! Отлично!", 90)
            max_enemies = DIFFICULTY_SETTINGS[current_difficulty]["max_enemies"]
            health_mult = DIFFICULTY_SETTINGS[current_difficulty]["health_mult"]
            if event.type == ghost_timer and len(current_level_obj.enemies) < max_enemies and not is_tutorial:
                spawn_y = 500 - ghost.get_height()
                if current_level_obj.platforms:
                    available_platforms = [p for p in current_level_obj.platforms if 1000 <= p.x <= 1300]
                    if available_platforms: spawn_y = random.choice(available_platforms).y - ghost.get_height()
                enemy_types = ["ghost", "flying_ghost", "patrol_ghost", "soldier", "spiker", "tank"]
                if current_level_obj.last_spawned_enemy and len(enemy_types) > 1: available_types = [t for t in enemy_types if t != current_level_obj.last_spawned_enemy]
                else: available_types = enemy_types
                enemy_type = random.choice(available_types)
                current_level_obj.last_spawned_enemy = enemy_type
                current_level_obj.enemies.append(Enemy(1280, spawn_y, enemy_type, health_mult))
            if event.type == coin_timer and len(current_level_obj.coins) < 10:
                if current_level_obj.platforms:
                    available_platforms = [p for p in current_level_obj.platforms if 800 <= p.x <= 1200]
                    if available_platforms:
                        platform = random.choice(available_platforms)
                        current_level_obj.coins.append(pygame.Rect(platform.x + random.randint(10, platform.width - 40), platform.y - 40, 30, 30))
            if event.type == pygame.KEYUP and event.key == pygame.K_b:
                if bullets_infinite or bullets_left > 0:
                    bullets.append(player_bullet.get_rect(topleft=(player_x + 70, player_y + 60)))
                    if not bullets_infinite: bullets_left -= 1
                    effects.append(Effect(player_x + 70, player_y + 60, "shoot"))
                    if is_tutorial and bullets_left == 4: add_tutorial_message("Вы выстрелили! Нажмите R чтобы перезарядиться.", 120)
    
    clock.tick(35)

pygame.quit()
sys.exit()
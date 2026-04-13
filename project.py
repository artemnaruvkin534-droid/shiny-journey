import pygame
from pygame import key
import random
import math
import sys
import os
import json
from enum import Enum

def get_resource_path(relative_path):
    """Получить путь к ресурсу для PyInstaller"""
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

# Загрузка изображений
bg = pygame.image.load(get_resource_path("images/font.png")).convert_alpha()
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
bullet = pygame.image.load(get_resource_path("images/bullet.png")).convert_alpha()
coin_img = pygame.image.load(get_resource_path("images/coin.png")).convert_alpha()
coin_img = pygame.transform.scale(coin_img, (30, 30))

# Состояния игры
class GameState(Enum):
    MAIN_MENU = 0
    PLAYING = 1
    GAME_OVER = 2
    LEVEL_TRANSITION = 3
    GAME_WIN = 4
    LEVEL_SELECT = 5
    TUTORIAL = 6

game_state = GameState.MAIN_MENU

# Класс для врага
class Enemy:
    def __init__(self, x, y, enemy_type="ghost"):
        self.rect = ghost.get_rect(topleft=(x, y))
        self.type = enemy_type
        self.speed_x = random.choice([-2, -3]) if enemy_type == "ghost" else -4
        self.speed_y = 0
        self.patrol_range = random.randint(100, 200)
        self.start_x = x
        
    def update(self, scroll_speed, platforms):
        self.rect.x -= scroll_speed + abs(self.speed_x)
        
        if self.type == "patrol_ghost":
            self.rect.x += math.sin(pygame.time.get_ticks() * 0.003) * 2
            
        on_ground = False
        for platform in platforms:
            if (self.rect.bottom >= platform.top and 
                self.rect.bottom <= platform.top + 15 and
                self.rect.right > platform.left and 
                self.rect.left < platform.right):
                on_ground = True
                self.rect.y = platform.top - self.rect.height
                break
                
        if not on_ground and self.rect.bottom < 600:
            self.speed_y += 0.5
            self.rect.y += self.speed_y
        else:
            self.speed_y = 0
            
        return self.rect.x + self.rect.width > 0
    
    def draw(self, screen):
        screen.blit(ghost, self.rect)

# Класс для бонусов
class PowerUp:
    def __init__(self, x, y, power_type):
        self.rect = pygame.Rect(x, y, 25, 25)
        self.type = power_type
        self.lifetime = 300
        self.animation_frame = 0
        
    def update(self, scroll_speed):
        self.rect.x -= scroll_speed
        self.lifetime -= 1
        self.animation_frame = (self.animation_frame + 1) % 20
        return self.lifetime > 0 and self.rect.x + self.rect.width > 0
    
    def draw(self, screen):
        colors = {
            "speed": (255, 255, 0),
            "infinite_ammo": (0, 255, 255),
            "extra_life": (255, 0, 0),
            "double_points": (255, 165, 0)
        }
        color = colors.get(self.type, (255, 255, 255))
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)

# Класс уровня
class Level:
    def __init__(self, level_num, is_tutorial=False):
        self.num = level_num
        self.is_tutorial = is_tutorial
        self.platforms = []
        self.enemies = []
        self.powerups = []
        self.coins = []
        self.scroll_speed = 3 if is_tutorial else 4
        self.ghost_spawn_delay = 5000 if is_tutorial else 2500
        self.goal_score = 50 if is_tutorial else 150
        self.background_color = (150, 200, 255) if is_tutorial else (100, 150, 255)
        self.gravity = 1.0
        self.theme = "tutorial" if is_tutorial else "normal"
        self.generate_level()
        
    def generate_level(self):
        """Генерация уровня на основе номера"""
        if self.is_tutorial:
            self.scroll_speed = 2
            self.goal_score = 30
            self.background_color = (200, 220, 255)
            self.theme = "tutorial"
            self.platforms = [
                pygame.Rect(300, 550, 200, 20),
                pygame.Rect(600, 500, 180, 20),
                pygame.Rect(900, 450, 200, 20),
                pygame.Rect(1200, 400, 250, 20),
                pygame.Rect(1600, 500, 200, 20),
            ]
            self.coins = [
                pygame.Rect(650, 460, 30, 30),
                pygame.Rect(950, 410, 30, 30),
                pygame.Rect(1300, 360, 30, 30),
                pygame.Rect(1650, 460, 30, 30),
            ]
            self.powerups = [PowerUp(1250, 360, "speed")]
            
        elif self.num == 1:
            self.scroll_speed = 4
            self.ghost_spawn_delay = 2500
            self.goal_score = 150
            self.background_color = (100, 150, 255)
            self.theme = "forest"
            self.platforms = [
                pygame.Rect(300, 550, 200, 20),
                pygame.Rect(600, 450, 200, 20),
                pygame.Rect(900, 350, 200, 20),
                pygame.Rect(1200, 500, 250, 20),
                pygame.Rect(1500, 400, 180, 20),
                pygame.Rect(1800, 300, 150, 20),
                pygame.Rect(2100, 480, 220, 20),
                pygame.Rect(2500, 350, 200, 20),
            ]
            for i in range(15):
                x = random.randint(500, 3000)
                y = random.choice([400, 450, 500, 530])
                self.coins.append(pygame.Rect(x, y, 30, 30))
                
        elif self.num == 2:
            self.scroll_speed = 5
            self.ghost_spawn_delay = 2000
            self.goal_score = 250
            self.background_color = (255, 200, 100)
            self.theme = "desert"
            self.gravity = 1.1
            self.platforms = [
                pygame.Rect(300, 550, 150, 20),
                pygame.Rect(500, 480, 180, 20),
                pygame.Rect(750, 400, 120, 20),
                pygame.Rect(900, 520, 200, 20),
                pygame.Rect(1150, 350, 160, 20),
                pygame.Rect(1400, 450, 140, 20),
                pygame.Rect(1700, 300, 180, 20),
                pygame.Rect(2000, 500, 200, 20),
                pygame.Rect(2300, 380, 150, 20),
                pygame.Rect(2600, 450, 170, 20),
            ]
            for i in range(25):
                x = random.randint(400, 3200)
                y = random.choice([380, 430, 470, 520])
                self.coins.append(pygame.Rect(x, y, 30, 30))
            for platform in self.platforms[::3]:
                self.enemies.append(Enemy(platform.x + 50, platform.y - 40, "patrol_ghost"))
                
        elif self.num == 3:
            self.scroll_speed = 6
            self.ghost_spawn_delay = 1500
            self.goal_score = 350
            self.background_color = (150, 200, 255)
            self.theme = "ice"
            self.gravity = 1.2
            self.platforms = [
                pygame.Rect(300, 550, 100, 20),
                pygame.Rect(450, 500, 120, 20),
                pygame.Rect(620, 420, 100, 20),
                pygame.Rect(780, 340, 100, 20),
                pygame.Rect(950, 460, 120, 20),
                pygame.Rect(1120, 380, 100, 20),
                pygame.Rect(1300, 520, 120, 20),
                pygame.Rect(1480, 300, 100, 20),
                pygame.Rect(1650, 450, 120, 20),
                pygame.Rect(1850, 370, 100, 20),
                pygame.Rect(2050, 500, 120, 20),
                pygame.Rect(2250, 280, 100, 20),
                pygame.Rect(2450, 420, 120, 20),
                pygame.Rect(2650, 350, 100, 20),
            ]
            for i in range(35):
                x = random.randint(300, 3500)
                y = random.choice([360, 410, 460, 510, 540])
                self.coins.append(pygame.Rect(x, y, 30, 30))
            for platform in self.platforms[::2]:
                self.enemies.append(Enemy(platform.x + 30, platform.y - 40, "ghost"))
            for i in range(3):
                x = random.randint(800, 2800)
                y = random.choice([350, 400, 450, 500])
                power_type = random.choice(["speed", "infinite_ammo", "extra_life", "double_points"])
                self.powerups.append(PowerUp(x, y, power_type))
                
        elif self.num == 4:
            self.scroll_speed = 7
            self.ghost_spawn_delay = 1200
            self.goal_score = 450
            self.background_color = (255, 100, 50)
            self.theme = "volcano"
            self.gravity = 1.3
            self.platforms = [
                pygame.Rect(300, 550, 80, 20),
                pygame.Rect(420, 510, 100, 20),
                pygame.Rect(550, 460, 90, 20),
                pygame.Rect(680, 400, 110, 20),
                pygame.Rect(830, 350, 100, 20),
                pygame.Rect(970, 480, 120, 20),
                pygame.Rect(1130, 420, 90, 20),
                pygame.Rect(1260, 360, 110, 20),
                pygame.Rect(1410, 530, 100, 20),
                pygame.Rect(1550, 470, 120, 20),
                pygame.Rect(1710, 390, 90, 20),
                pygame.Rect(1840, 320, 110, 20),
                pygame.Rect(1990, 500, 100, 20),
                pygame.Rect(2130, 440, 120, 20),
                pygame.Rect(2290, 370, 90, 20),
                pygame.Rect(2420, 310, 110, 20),
                pygame.Rect(2570, 480, 100, 20),
                pygame.Rect(2710, 420, 120, 20),
            ]
            for i in range(45):
                x = random.randint(300, 3800)
                y = random.choice([350, 400, 450, 500, 550])
                self.coins.append(pygame.Rect(x, y, 30, 30))
            for platform in self.platforms:
                if random.random() < 0.4:
                    self.enemies.append(Enemy(platform.x + 40, platform.y - 40, "patrol_ghost"))
            for i in range(5):
                x = random.randint(500, 3200)
                y = random.choice([350, 400, 450, 500])
                power_type = random.choice(["speed", "infinite_ammo", "double_points"])
                self.powerups.append(PowerUp(x, y, power_type))
                
        elif self.num == 5:
            self.scroll_speed = 8
            self.ghost_spawn_delay = 1000
            self.goal_score = 600
            self.background_color = (50, 50, 100)
            self.theme = "final"
            self.gravity = 1.4
            self.platforms = [
                pygame.Rect(300, 550, 100, 20),
                pygame.Rect(450, 500, 100, 20),
                pygame.Rect(600, 450, 100, 20),
                pygame.Rect(750, 400, 100, 20),
                pygame.Rect(900, 350, 100, 20),
                pygame.Rect(1050, 300, 100, 20),
                pygame.Rect(1200, 500, 100, 20),
                pygame.Rect(1350, 450, 100, 20),
                pygame.Rect(1500, 400, 100, 20),
                pygame.Rect(1650, 350, 100, 20),
                pygame.Rect(1800, 300, 100, 20),
                pygame.Rect(1950, 250, 100, 20),
                pygame.Rect(2100, 500, 100, 20),
                pygame.Rect(2250, 450, 100, 20),
                pygame.Rect(2400, 400, 100, 20),
                pygame.Rect(2550, 350, 100, 20),
                pygame.Rect(2700, 300, 100, 20),
                pygame.Rect(2850, 250, 100, 20),
            ]
            for i in range(60):
                x = random.randint(300, 4000)
                y = random.choice([300, 350, 400, 450, 500, 550])
                self.coins.append(pygame.Rect(x, y, 30, 30))
            for platform in self.platforms:
                if random.random() < 0.6:
                    self.enemies.append(Enemy(platform.x + 30, platform.y - 40, "patrol_ghost"))
            for i in range(7):
                x = random.randint(500, 3500)
                y = random.choice([300, 350, 400, 450, 500])
                power_type = random.choice(["speed", "infinite_ammo", "double_points", "extra_life"])
                self.powerups.append(PowerUp(x, y, power_type))

# Игровые переменные
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

# Физика
is_jumping = False
player_velocity_y = 0
gravity = 1.0
jump_strength = -18
is_on_ground = True
double_jump_available = False
has_double_jumped = False

# Защита при появлении
invincible_frames = 0
invincible_duration = 120

current_level = 1
max_level = 5
level_complete = False
level_transition = False
level_transition_timer = 0
current_level_obj = None
is_tutorial = False

# Система сохранения прогресса
def load_game_progress():
    try:
        with open("save.json", "r") as f:
            data = json.load(f)
            return data.get("unlocked_levels", 1), data.get("best_scores", {})
    except:
        return 1, {}

def save_game_progress(unlocked_levels, best_scores):
    data = {
        "unlocked_levels": unlocked_levels,
        "best_scores": best_scores
    }
    with open("save.json", "w") as f:
        json.dump(data, f)

# Загрузка прогресса
unlocked_levels, best_scores = load_game_progress()

# Система частиц
class Particle:
    def __init__(self, x, y, color, velocity_x=0, velocity_y=0, size=3, life=60):
        self.x = x
        self.y = y
        self.color = color
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.size = size
        self.life = life
        self.max_life = life

    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.velocity_y += 0.1
        self.life -= 1
        return self.life > 0

    def draw(self, surface):
        alpha = int(255 * (self.life / self.max_life))
        if alpha > 0:
            particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, (*self.color, alpha), (self.size, self.size), self.size)
            surface.blit(particle_surface, (int(self.x - self.size), int(self.y - self.size)))

class Effect:
    def __init__(self, x, y, effect_type):
        self.x = x
        self.y = y
        self.type = effect_type
        self.particles = []
        self.duration = 0
        self.create_effect()

    def create_effect(self):
        if self.type == "jump":
            for _ in range(15):
                angle = random.uniform(0, math.pi)
                speed = random.uniform(1, 3)
                velocity_x = math.cos(angle) * speed * random.choice([-1, 1])
                velocity_y = -abs(math.sin(angle) * speed)
                self.particles.append(Particle(
                    self.x + random.randint(-10, 10), self.y + 50,
                    (100, 150, 255), velocity_x, velocity_y,
                    random.randint(2, 4), random.randint(20, 40)
                ))
            self.duration = 40
        elif self.type == "land":
            for _ in range(20):
                angle = random.uniform(0, math.pi)
                speed = random.uniform(1, 4)
                velocity_x = math.cos(angle) * speed * random.choice([-1, 1])
                velocity_y = -abs(math.sin(angle) * speed) * 0.5
                self.particles.append(Particle(
                    self.x + random.randint(-20, 20), self.y + 45,
                    (150, 150, 200), velocity_x, velocity_y,
                    random.randint(2, 5), random.randint(30, 50)
                ))
            self.duration = 50
        elif self.type == "shoot":
            for _ in range(8):
                angle = random.uniform(-0.3, 0.3)
                speed = random.uniform(2, 5)
                velocity_x = math.cos(angle) * speed
                velocity_y = math.sin(angle) * speed
                self.particles.append(Particle(
                    self.x + 70, self.y + 60,
                    (255, 255, 100), velocity_x, velocity_y,
                    random.randint(2, 3), random.randint(15, 25)
                ))
            self.duration = 25
        elif self.type == "ghost_death":
            for _ in range(30):
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(1, 6)
                velocity_x = math.cos(angle) * speed
                velocity_y = math.sin(angle) * speed
                self.particles.append(Particle(
                    self.x + random.randint(-10, 10), self.y + random.randint(-10, 10),
                    (200, 100, 255), velocity_x, velocity_y,
                    random.randint(3, 6), random.randint(40, 60)
                ))
            self.duration = 60
        elif self.type == "coin_collect":
            for _ in range(25):
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(1, 4)
                velocity_x = math.cos(angle) * speed
                velocity_y = math.sin(angle) * speed
                self.particles.append(Particle(
                    self.x + 15, self.y + 15,
                    (255, 215, 0), velocity_x, velocity_y,
                    random.randint(2, 4), random.randint(30, 45)
                ))
            self.duration = 45
        elif self.type == "powerup":
            for _ in range(20):
                angle = random.uniform(0, math.pi * 2)
                speed = random.uniform(1, 5)
                velocity_x = math.cos(angle) * speed
                velocity_y = math.sin(angle) * speed
                self.particles.append(Particle(
                    self.x + 12, self.y + 12,
                    (0, 255, 255), velocity_x, velocity_y,
                    random.randint(2, 5), random.randint(30, 50)
                ))
            self.duration = 50

    def update(self):
        for particle in self.particles[:]:
            if not particle.update():
                self.particles.remove(particle)
        self.duration -= 1
        return len(self.particles) > 0 and self.duration > 0

    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)

class FloatingNumber:
    def __init__(self, x, y, number, color):
        self.x = x
        self.y = y
        self.number = number
        self.color = color
        self.life = 60
        self.velocity_y = -2

    def update(self):
        self.y += self.velocity_y
        self.life -= 1
        return self.life > 0

    def draw(self, surface):
        alpha = min(255, self.life * 4)
        text = ammo_font.render(f"+{self.number}", True, self.color)
        text.set_alpha(alpha)
        surface.blit(text, (int(self.x), int(self.y)))

effects = []
floating_numbers = []

# Таймеры
ghost_timer = pygame.USEREVENT + 1
coin_timer = pygame.USEREVENT + 2

# Шрифты
label = pygame.font.SysFont("comicsans", 40, bold=True)
ammo_font = pygame.font.SysFont("comicsans", 30, bold=True)
level_font = pygame.font.SysFont("comicsans", 60, bold=True)
title_font = pygame.font.SysFont("comicsans", 80, bold=True)
menu_font = pygame.font.SysFont("comicsans", 50, bold=True)
small_font = pygame.font.SysFont("comicsans", 25, bold=True)
tutorial_font = pygame.font.SysFont("comicsans", 35, bold=True)

# Тексты
lose_label = label.render("GAME OVER!", False, (175, 91, 61))

# Кнопки выбора уровня
level_buttons = []
level_button_rects = []

was_on_ground = True

# Подсказки для обучения
tutorial_messages = []
tutorial_message_timer = 0

def add_tutorial_message(message, duration=180):
    global tutorial_messages, tutorial_message_timer
    tutorial_messages.append({"text": message, "timer": duration})

def draw_tutorial_hints():
    """Отрисовка подсказок в обучающем уровне"""
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
            if msg in tutorial_messages:
                tutorial_messages.remove(msg)
        else:
            alpha = min(255, msg["timer"] * 4)
            text = tutorial_font.render(msg["text"], True, (255, 255, 0))
            text.set_alpha(alpha)
            text_rect = text.get_rect(center=(640, y_offset + 20))
            screen.blit(text, text_rect)
            y_offset += 35

def check_platform_collision(player_rect, check_vertical=True):
    collision_type = None
    collision_platform = None
    
    for platform in current_level_obj.platforms:
        if player_rect.colliderect(platform):
            if check_vertical:
                if (player_velocity_y >= 0 and
                    player_rect.bottom >= platform.top and
                    player_rect.bottom <= platform.top + 25 and
                    player_rect.right > platform.left + 5 and
                    player_rect.left < platform.right - 5):
                    collision_type = "top"
                    collision_platform = platform
                    break
                elif (player_velocity_y < 0 and
                      player_rect.top <= platform.bottom and
                      player_rect.top >= platform.bottom - 15 and
                      player_rect.right > platform.left + 5 and
                      player_rect.left < platform.right - 5):
                    collision_type = "bottom"
                    collision_platform = platform
                    break
            else:
                if (player_rect.right > platform.left and
                    player_rect.left < platform.right and
                    player_rect.bottom > platform.top + 10 and
                    player_rect.top < platform.bottom - 10):
                    if abs(player_rect.right - platform.left) < abs(player_rect.left - platform.right):
                        collision_type = "right"
                    else:
                        collision_type = "left"
                    collision_platform = platform
                    break
    return collision_type, collision_platform

def start_tutorial():
    global current_level_obj, game_state, is_tutorial, score, bullets_left
    global player_x, player_y, player_velocity_y, bullets, ghosts_killed
    global effects, floating_numbers, tutorial_messages, invincible_frames
    
    player_x = 150
    player_y = 500
    player_velocity_y = 0
    score = 0
    bullets_left = 5
    ghosts_killed = 0
    bullets.clear()
    effects.clear()
    floating_numbers.clear()
    tutorial_messages.clear()
    
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

def reset_game():
    global player_x, player_y, player_velocity_y, bullets, score, bullets_left, bg_x
    global is_on_ground, double_jump_available, has_double_jumped, ghosts_killed
    global current_level, level_complete, game_state, effects, floating_numbers
    global was_on_ground, player_speed_multiplier, speed_boost_timer, bullets_infinite
    global infinite_ammo_timer, double_points, double_points_timer, current_level_obj, is_tutorial
    global invincible_frames
    
    player_x = 150
    player_y = 500
    player_velocity_y = 0
    bg_x = 0
    score = 0
    bullets_left = 5
    ghosts_killed = 0
    current_level = 1
    level_complete = False
    is_on_ground = True
    double_jump_available = False
    has_double_jumped = False
    was_on_ground = True
    player_speed_multiplier = 1.0
    speed_boost_timer = 0
    bullets_infinite = False
    infinite_ammo_timer = 0
    double_points = False
    double_points_timer = 0
    is_tutorial = False
    
    invincible_frames = invincible_duration
    
    bullets.clear()
    effects.clear()
    floating_numbers.clear()
    
    current_level_obj = Level(current_level)
    game_state = GameState.PLAYING
    
    gravity = current_level_obj.gravity
    pygame.time.set_timer(ghost_timer, current_level_obj.ghost_spawn_delay)
    pygame.time.set_timer(coin_timer, 1500)

def load_level(level_num):
    global current_level, current_level_obj, gravity, score, bullets_left, ghosts_killed
    global bullets, effects, floating_numbers, is_tutorial, invincible_frames
    global player_x, player_y, player_velocity_y, is_on_ground
    
    current_level = level_num
    is_tutorial = False
    current_level_obj = Level(level_num)
    gravity = current_level_obj.gravity
    
    player_x = 150
    player_y = 500
    player_velocity_y = 0
    is_on_ground = True
    
    score = 0
    bullets_left = 5
    ghosts_killed = 0
    bullets.clear()
    effects.clear()
    floating_numbers.clear()
    
    invincible_frames = invincible_duration
    
    pygame.time.set_timer(ghost_timer, current_level_obj.ghost_spawn_delay)
    game_state = GameState.PLAYING

def complete_tutorial():
    global game_state, unlocked_levels
    
    if unlocked_levels < 1:
        unlocked_levels = 1
        save_game_progress(unlocked_levels, best_scores)
    
    game_state = GameState.MAIN_MENU
    add_tutorial_message("Обучение пройдено! Удачи в игре!", 180)

def next_level():
    global current_level, level_complete, level_transition, level_transition_timer, game_state
    global unlocked_levels, best_scores, is_tutorial, invincible_frames
    
    if is_tutorial:
        complete_tutorial()
        return False
    
    level_key = str(current_level)
    if level_key not in best_scores or score > best_scores[level_key]:
        best_scores[level_key] = score
    
    if current_level < max_level and current_level + 1 > unlocked_levels:
        unlocked_levels = current_level + 1
        save_game_progress(unlocked_levels, best_scores)
    
    if current_level < max_level:
        current_level += 1
        level_complete = True
        level_transition = True
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
        screen.fill(current_level_obj.background_color)
        level_text = level_font.render(f"LEVEL {current_level} - {current_level_obj.theme.upper()}!", True, (255, 215, 0))
        next_text = label.render("Get ready for next level...", True, (255, 255, 255))
        screen.blit(level_text, (1280 // 2 - level_text.get_width() // 2, 300))
        screen.blit(next_text, (1280 // 2 - next_text.get_width() // 2, 400))

def draw_hud():
    if is_tutorial:
        level_text = ammo_font.render("ОБУЧЕНИЕ", True, (255, 255, 0))
    else:
        level_text = ammo_font.render(f"Уровень: {current_level}/{max_level}", True, (255, 255, 255))
    
    progress_text = ammo_font.render(f"Прогресс: {score}/{current_level_obj.goal_score}", True, (255, 255, 255))
    
    if bullets_infinite:
        ammo_text = ammo_font.render(f"Патроны: БЕСКОНЕЧНО", True, (0, 255, 0))
    else:
        ammo_text = ammo_font.render(f"Патроны: {bullets_left}", True, (255, 255, 255))
    
    score_text = ammo_font.render(f"Очки: {score}", True, (255, 215, 0))
    
    y_offset = 10
    screen.blit(level_text, (10, y_offset))
    screen.blit(progress_text, (10, y_offset + 40))
    screen.blit(ammo_text, (10, y_offset + 80))
    screen.blit(score_text, (10, y_offset + 120))
    
    if player_speed_multiplier > 1.0:
        speed_text = ammo_font.render("УСКОРЕНИЕ!", True, (255, 255, 0))
        screen.blit(speed_text, (10, y_offset + 160))
    if double_points:
        points_text = ammo_font.render("x2 ОЧКИ!", True, (255, 165, 0))
        screen.blit(points_text, (10, y_offset + 200))
    if invincible_frames > 0:
        invincible_text = ammo_font.render("НЕУЯЗВИМОСТЬ", True, (100, 200, 255))
        screen.blit(invincible_text, (10, y_offset + 240))

def draw_main_menu():
    screen.fill((100, 150, 255))
    
    for effect in effects[:]:
        if not effect.update():
            effects.remove(effect)
        else:
            effect.draw(screen)
    
    if random.random() < 0.3:
        effect_type = random.choice(["coin_collect", "ghost_death"])
        effects.append(Effect(random.randint(0, 1280), random.randint(0, 720), effect_type))
    
    title_text = title_font.render("MINI MARIO", True, (255, 215, 0))
    screen.blit(title_text, (1280 // 2 - title_text.get_width() // 2, 20))
    
    subtitle_text = label.render("Advanced Platformer", True, (255, 255, 255))
    screen.blit(subtitle_text, (1280 // 2 - subtitle_text.get_width() // 2, 100))
    
    start_text = menu_font.render("Start Game", True, (255, 255, 255))
    level_text = menu_font.render("Level Select", True, (255, 255, 255))
    quit_text = menu_font.render("Quit", True, (255, 255, 255))
    
    button_padding_x = 50
    button_padding_y = 15
    button_spacing = 40  # Расстояние между кнопками
    
    start_button_width = start_text.get_width() + button_padding_x
    start_button_height = start_text.get_height() + button_padding_y
    level_button_width = level_text.get_width() + button_padding_x
    level_button_height = level_text.get_height() + button_padding_y
    quit_button_width = quit_text.get_width() + button_padding_x
    quit_button_height = quit_text.get_height() + button_padding_y

    # Общая высота всех кнопок с отступами
    start_y = 160
    center_x = 1280 // 2

    start_button = pygame.Rect(center_x - start_button_width // 2, start_y, start_button_width, start_button_height)
    level_select_button = pygame.Rect(center_x - level_button_width // 2, start_y + start_button_height + button_spacing, level_button_width, level_button_height)
    quit_button = pygame.Rect(center_x - quit_button_width // 2, start_y + start_button_height + button_spacing + level_button_height + button_spacing, quit_button_width, quit_button_height)
    
    # Кнопка обучения (Start Game)
    pygame.draw.rect(screen, (50, 200, 50), start_button)
    pygame.draw.rect(screen, (0, 100, 0), start_button, 3)
    screen.blit(start_text, (start_button.centerx - start_text.get_width() // 2,
                             start_button.centery - start_text.get_height() // 2))
    
    # Маленькая подпись под кнопкой обучения
    tutorial_note = small_font.render("(Tutorial Level)", True, (200, 255, 200))
    screen.blit(tutorial_note, (start_button.centerx - tutorial_note.get_width() // 2, start_button.bottom + 5))
    
    # Кнопка выбора уровней
    pygame.draw.rect(screen, (200, 100, 50), level_select_button)
    pygame.draw.rect(screen, (100, 50, 0), level_select_button, 3)
    screen.blit(level_text, (level_select_button.centerx - level_text.get_width() // 2,
                             level_select_button.centery - level_text.get_height() // 2))
    
    # Кнопка выхода
    pygame.draw.rect(screen, (200, 50, 50), quit_button)
    pygame.draw.rect(screen, (100, 0, 0), quit_button, 3)
    screen.blit(quit_text, (quit_button.centerx - quit_text.get_width() // 2,
                            quit_button.centery - quit_text.get_height() // 2))
    
    # Информация о прогрессе
    progress_text = small_font.render(f"Уровней открыто: {unlocked_levels}/{max_level}", True, (255, 255, 200))
    screen.blit(progress_text, (10, 690))
    
    # Инструкции (сдвинуты вниз, чтобы не мешать кнопкам)
    instructions = [
        "УПРАВЛЕНИЕ:",
        "A/D - Движение влево/вправо",
        "ПРОБЕЛ - Прыжок (двойной прыжок в воздухе)",
        "B - Стрельба",
        "R - Перезарядка"
    ]
    
    start_y_instructions = 500
    for i, instruction in enumerate(instructions):
        inst_text = label.render(instruction, True, (255, 255, 255))
        screen.blit(inst_text, (1280 // 2 - inst_text.get_width() // 2, start_y_instructions + i * 40))
    
    return start_button, level_select_button, quit_button

def draw_level_select():
    screen.fill((50, 50, 100))
    
    title_text = level_font.render("ВЫБОР УРОВНЯ", True, (255, 215, 0))
    screen.blit(title_text, (1280 // 2 - title_text.get_width() // 2, 30))
    
    level_buttons.clear()
    
    # Размеры кнопок
    button_width = 240
    button_height = 170
    
    # Центрируем по вертикали
    total_height = 2 * button_height + 50
    start_y = (720 - total_height) // 2
    
    # Позиции для 5 уровней
    level_positions = {
        1: {"x": 220, "y": start_y},
        2: {"x": 480, "y": start_y},
        3: {"x": 740, "y": start_y},
        4: {"x": 350, "y": start_y + button_height + 50},
        5: {"x": 610, "y": start_y + button_height + 50}
    }
    
    themes_names = {
        1: "Forest", 2: "Desert", 3: "Ice", 4: "Volcano", 5: "Final"
    }
    
    for i in range(1, max_level + 1):
        x = level_positions[i]["x"]
        y = level_positions[i]["y"]
        
        button_rect = pygame.Rect(x, y, button_width, button_height)
        level_buttons.append(button_rect)
        
        is_unlocked = i <= unlocked_levels
        
        if is_unlocked:
            # Градиентная заливка для открытых уровней
            for j in range(button_height):
                color_value = 100 + int(j * 0.3)
                color = (color_value, 130 + int(j * 0.2), 180)
                pygame.draw.line(screen, color, (x, y + j), (x + button_width, y + j))
            border_color = (255, 215, 0)
            text_color = (255, 255, 255)
        else:
            # Темная заливка для закрытых уровней
            pygame.draw.rect(screen, (60, 60, 70), button_rect)
            border_color = (80, 80, 80)
            text_color = (150, 150, 150)
        
        pygame.draw.rect(screen, border_color, button_rect, 3)
        
        # Номер уровня
        level_num_text = label.render(f"УРОВЕНЬ {i}", True, text_color)
        num_x = x + button_width // 2 - level_num_text.get_width() // 2
        num_y = y + 40  # Оставляем на месте
        screen.blit(level_num_text, (num_x, num_y))
        
        # Название темы (ПОДНЯТО ВЫШЕ)
        theme_text = label.render(themes_names[i], True, (220, 220, 220))
        theme_x = x + button_width // 2 - theme_text.get_width() // 2
        theme_y = y + 80  # Было 95, поднято на 15 пикселей выше
        screen.blit(theme_text, (theme_x, theme_y))
        
        # Рекорд
        level_key = str(i)
        if level_key in best_scores and is_unlocked:
            best_text = small_font.render(f"Рекорд: {best_scores[level_key]}", True, (255, 215, 0))
            best_x = x + button_width // 2 - best_text.get_width() // 2
            best_y = y + 125  # Было 135, поднято на 10 пикселей выше
            screen.blit(best_text, (best_x, best_y))
        
        # Замок для заблокированных уровней
        if not is_unlocked:
            lock_text = level_font.render("🔒", True, (200, 50, 50))
            lock_x = x + button_width // 2 - lock_text.get_width() // 2
            lock_y = y + 70  # Было 75, поднято на 5 пикселей выше
            screen.blit(lock_text, (lock_x, lock_y))
    
    # Кнопка "Назад"
    back_button = pygame.Rect(540, 620, 200, 50)
    
    mouse_pos = pygame.mouse.get_pos()
    if back_button.collidepoint(mouse_pos):
        pygame.draw.rect(screen, (200, 80, 80), back_button)
        pygame.draw.rect(screen, (255, 255, 255), back_button, 3)
    else:
        pygame.draw.rect(screen, (150, 50, 50), back_button)
        pygame.draw.rect(screen, (255, 255, 255), back_button, 2)
    
    back_text = menu_font.render("Назад", True, (255, 255, 255))
    screen.blit(back_text, (back_button.centerx - back_text.get_width() // 2,
                            back_button.centery - back_text.get_height() // 2))
    
    # Информация о прогрессе
    progress_text = small_font.render(f"Открыто уровней: {unlocked_levels}/{max_level}", True, (255, 255, 200))
    screen.blit(progress_text, (10, 690))
    
    return back_button
# Загрузка первого уровня
current_level_obj = Level(1)

# Основной игровой цикл
running = True
while running:
    if game_state == GameState.MAIN_MENU:
        start_btn, level_btn, quit_btn = draw_main_menu()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if start_btn.collidepoint(mouse_pos):
                    start_tutorial()
                elif level_btn.collidepoint(mouse_pos):
                    game_state = GameState.LEVEL_SELECT
                elif quit_btn.collidepoint(mouse_pos):
                    running = False
    
    elif game_state == GameState.LEVEL_SELECT:
        back_button = draw_level_select()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                for i, button_rect in enumerate(level_buttons):
                    if button_rect.collidepoint(mouse_pos):
                        level_num = i + 1
                        if level_num <= unlocked_levels:
                            load_level(level_num)
                            game_state = GameState.PLAYING
                
                if back_button.collidepoint(mouse_pos):
                    game_state = GameState.MAIN_MENU
    
    elif game_state == GameState.TUTORIAL or game_state == GameState.PLAYING:
        # Обновление бонусов
        if speed_boost_timer > 0:
            speed_boost_timer -= 1
            if speed_boost_timer <= 0:
                player_speed_multiplier = 1.0
        
        if infinite_ammo_timer > 0:
            infinite_ammo_timer -= 1
            if infinite_ammo_timer <= 0:
                bullets_infinite = False
        
        if double_points_timer > 0:
            double_points_timer -= 1
            if double_points_timer <= 0:
                double_points = False
        
        # Отрисовка фона
        screen.fill(current_level_obj.background_color)
        screen.blit(bg, (bg_x, 0))
        screen.blit(bg, (bg_x + 1280, 0))
        
        # Эффекты
        for effect in effects[:]:
            if not effect.update():
                effects.remove(effect)
            else:
                effect.draw(screen)
        
        for floating_number in floating_numbers[:]:
            if not floating_number.update():
                floating_numbers.remove(floating_number)
            else:
                floating_number.draw(screen)
        
        # Проверка завершения уровня
        if not level_complete and score >= current_level_obj.goal_score:
            next_level()
        
        # Переход между уровнями
        if level_transition:
            draw_level_transition()
            if pygame.time.get_ticks() - level_transition_timer > 2000:
                level_transition = False
                level_complete = False
            pygame.display.update()
            continue
        
        # Скроллинг фона
        bg_x -= current_level_obj.scroll_speed
        if bg_x <= -1280:
            bg_x = 0
        
        # Обновление платформ
        for platform in current_level_obj.platforms:
            platform.x -= current_level_obj.scroll_speed
        
        current_level_obj.platforms = [p for p in current_level_obj.platforms if p.x + p.width > 0]
        
        # Генерация новых платформ
        if not is_tutorial and current_level_obj.platforms and current_level_obj.platforms[-1].x < 400:
            if random.random() < 0.6:
                new_x = 1280
                new_y = random.choice([500, 450, 400, 350])
                new_width = random.randint(150, 250)
                new_platform = pygame.Rect(new_x, new_y, new_width, 20)
                overlap = False
                for platform in current_level_obj.platforms:
                    if (new_platform.colliderect(platform) and
                            abs(new_platform.y - platform.y) < 50):
                        overlap = True
                        break
                if not overlap:
                    current_level_obj.platforms.append(new_platform)
        
        # Отрисовка платформ
        for platform in current_level_obj.platforms:
            if current_level_obj.theme == "tutorial":
                pygame.draw.rect(screen, (100, 200, 100), platform)
                pygame.draw.rect(screen, (50, 150, 50), platform, 2)
            elif current_level_obj.theme == "ice":
                pygame.draw.rect(screen, (173, 216, 230), platform)
                pygame.draw.rect(screen, (135, 206, 235), platform, 2)
            elif current_level_obj.theme == "desert":
                pygame.draw.rect(screen, (210, 180, 140), platform)
                pygame.draw.rect(screen, (160, 130, 90), platform, 2)
            elif current_level_obj.theme == "volcano":
                pygame.draw.rect(screen, (180, 60, 30), platform)
                pygame.draw.rect(screen, (255, 100, 50), platform, 2)
            elif current_level_obj.theme == "final":
                pygame.draw.rect(screen, (100, 50, 150), platform)
                pygame.draw.rect(screen, (200, 100, 255), platform, 2)
            else:
                pygame.draw.rect(screen, (139, 69, 19), platform)
                pygame.draw.rect(screen, (101, 50, 12), platform, 2)
        
        player_rect = walk_left[0].get_rect(topleft=(player_x, player_y))
        
        # Монеты
        coins_to_remove = []
        for i, coin in enumerate(current_level_obj.coins):
            screen.blit(coin_img, coin)
            coin.x -= current_level_obj.scroll_speed
            
            if coin.x + coin.width < 0:
                coins_to_remove.append(i)
                continue
            
            if player_rect.colliderect(coin):
                coins_to_remove.append(i)
                points = 20 if double_points else 10
                score += points
                effects.append(Effect(coin.x + 15, coin.y + 15, "coin_collect"))
                floating_numbers.append(FloatingNumber(coin.x, coin.y, points, (255, 215, 0)))
        
        for i in sorted(coins_to_remove, reverse=True):
            if i < len(current_level_obj.coins):
                current_level_obj.coins.pop(i)
        
        # Бонусы
        powerups_to_remove = []
        for i, powerup in enumerate(current_level_obj.powerups):
            if not powerup.update(current_level_obj.scroll_speed):
                powerups_to_remove.append(i)
                continue
            
            powerup.draw(screen)
            
            if player_rect.colliderect(powerup.rect):
                powerups_to_remove.append(i)
                effects.append(Effect(powerup.rect.x, powerup.rect.y, "powerup"))
                
                if powerup.type == "speed":
                    player_speed_multiplier = 1.5
                    speed_boost_timer = 600
                    floating_numbers.append(FloatingNumber(powerup.rect.x, powerup.rect.y, "Скорость", (255, 255, 0)))
                    if is_tutorial:
                        add_tutorial_message("УСКОРЕНИЕ! Вы двигаетесь быстрее!", 120)
                elif powerup.type == "infinite_ammo":
                    bullets_infinite = True
                    infinite_ammo_timer = 600
                    floating_numbers.append(FloatingNumber(powerup.rect.x, powerup.rect.y, "∞ Патроны", (0, 255, 255)))
                    if is_tutorial:
                        add_tutorial_message("БЕСКОНЕЧНЫЕ ПАТРОНЫ! Перезарядка не нужна!", 120)
                elif powerup.type == "extra_life":
                    score += 100
                    floating_numbers.append(FloatingNumber(powerup.rect.x, powerup.rect.y, "+100", (255, 0, 0)))
                elif powerup.type == "double_points":
                    double_points = True
                    double_points_timer = 600
                    floating_numbers.append(FloatingNumber(powerup.rect.x, powerup.rect.y, "x2 Очки", (255, 165, 0)))
                    if is_tutorial:
                        add_tutorial_message("УДВОЕНИЕ ОЧКОВ! В два раза больше за убийства!", 120)
        
        for i in sorted(powerups_to_remove, reverse=True):
            if i < len(current_level_obj.powerups):
                current_level_obj.powerups.pop(i)
        
        # Враги
        enemies_to_remove = []
        for i, enemy in enumerate(current_level_obj.enemies):
            if not enemy.update(current_level_obj.scroll_speed, current_level_obj.platforms):
                enemies_to_remove.append(i)
                continue
            
            enemy.draw(screen)
            
            # Проверка столкновения с учетом неуязвимости
            if player_rect.colliderect(enemy.rect) and invincible_frames <= 0:
                if is_tutorial:
                    add_tutorial_message("Ой! Вас ударил призрак! Попробуйте снова!", 180)
                game_state = GameState.GAME_OVER
        
        for i in sorted(enemies_to_remove, reverse=True):
            if i < len(current_level_obj.enemies):
                current_level_obj.enemies.pop(i)
        
        # Управление игроком
        keys = pygame.key.get_pressed()
        current_speed = player_speed * player_speed_multiplier
        
        if keys[pygame.K_a] and player_x > 50:
            player_x -= current_speed
        elif keys[pygame.K_d] and player_x < 1200:
            player_x += current_speed
        
        # Отрисовка игрока с эффектом мигания при неуязвимости
        if invincible_frames > 0:
            # Мигание каждые 5 кадров
            if (invincible_frames // 3) % 2 == 0:
                if keys[pygame.K_a]:
                    screen.blit(walk_left[player_anim_count], (player_x, player_y))
                else:
                    screen.blit(walk_right[player_anim_count], (player_x, player_y))
            # Иначе не рисуем (эффект мигания)
        else:
            if keys[pygame.K_a]:
                screen.blit(walk_left[player_anim_count], (player_x, player_y))
            else:
                screen.blit(walk_right[player_anim_count], (player_x, player_y))
        
        if (keys[pygame.K_a] or keys[pygame.K_d]) and is_on_ground:
            player_anim_count = (player_anim_count + 1) % 4
        
        # Коллизии
        player_rect.x = player_x
        side_collision, side_platform = check_platform_collision(player_rect, check_vertical=False)
        
        if side_collision == "right":
            player_x = side_platform.left - player_rect.width
        elif side_collision == "left":
            player_x = side_platform.right
        
        player_velocity_y += gravity
        player_y += player_velocity_y
        player_rect.y = player_y
        collision_type, collision_platform = check_platform_collision(player_rect, check_vertical=True)
        
        if collision_type == "top" and not was_on_ground:
            effects.append(Effect(player_x + 35, player_y + 50, "land"))
        
        if collision_type == "top":
            player_y = collision_platform.top - player_rect.height
            player_velocity_y = 0
            is_jumping = False
            is_on_ground = True
            double_jump_available = False
            has_double_jumped = False
        elif collision_type == "bottom":
            player_y = collision_platform.bottom
            player_velocity_y = 0
            if double_jump_available:
                double_jump_available = False
        else:
            if player_y >= 500:
                player_y = 500
                player_velocity_y = 0
                is_jumping = False
                is_on_ground = True
                double_jump_available = False
                has_double_jumped = False
            else:
                is_on_ground = False
        
        was_on_ground = is_on_ground
        
        # Перезарядка
        if keys[pygame.K_r] and not bullets_infinite:
            bullets_left = 5
            if is_tutorial:
                add_tutorial_message("Патроны перезаряжены! У вас 5 пуль!", 90)
        
        # Пули
        bullets_to_remove = []
        for i, el in enumerate(bullets):
            screen.blit(bullet, (el.x, el.y))
            el.x += 20
            
            if el.x > 1282:
                bullets_to_remove.append(i)
                continue
            
            for index, enemy in enumerate(current_level_obj.enemies):
                if el.colliderect(enemy.rect):
                    current_level_obj.enemies.pop(index)
                    bullets_to_remove.append(i)
                    ghosts_killed += 1
                    points = 50 if double_points else 25
                    score += points
                    effects.append(Effect(enemy.rect.x + enemy.rect.width // 2,
                                         enemy.rect.y + enemy.rect.height // 2, "ghost_death"))
                    floating_numbers.append(FloatingNumber(enemy.rect.x, enemy.rect.y, points, (200, 100, 255)))
                    if is_tutorial and ghosts_killed == 1:
                        add_tutorial_message("Отлично! Вы убили призрака! +25 очков!", 120)
                    break
        
        for i in sorted(bullets_to_remove, reverse=True):
            if i < len(bullets):
                bullets.pop(i)
        
        # Уменьшаем счетчик неуязвимости
        if invincible_frames > 0:
            invincible_frames -= 1
        
        draw_hud()
        
        # Отрисовка подсказок для обучения
        if is_tutorial:
            draw_tutorial_hints()
    
    elif game_state == GameState.GAME_OVER:
        # Затемняем фон
        overlay = pygame.Surface((1280, 720))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Анимированный текст GAME OVER (по центру)
        game_over_text = level_font.render("GAME OVER", True, (255, 50, 50))
        shadow_text = level_font.render("GAME OVER", True, (100, 0, 0))
        
        # Эффект пульсации
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.003)) * 10
        game_over_y = 50 + pulse
        
        # Центрируем текст GAME OVER
        game_over_x = 1280 // 2 - game_over_text.get_width() // 2
        screen.blit(shadow_text, (game_over_x + 5, game_over_y + 5))
        screen.blit(game_over_text, (game_over_x, game_over_y))
        
        # Разделительная линия (по центру)
        line_width = 450
        line_x = (1280 - line_width) // 2
        line_y = game_over_y + game_over_text.get_height() + 20
        pygame.draw.line(screen, (255, 100, 100), (line_x, line_y), (line_x + line_width, line_y), 3)
        
        # Рамка для статистики (по центру)
        stats_width = 650
        stats_height = 180
        stats_x = (1280 - stats_width) // 2
        stats_y = line_y + 25
        stats_rect = pygame.Rect(stats_x, stats_y, stats_width, stats_height)
        
        # Красивая рамка с градиентом
        for i in range(3):
            pygame.draw.rect(screen, (50 + i*20, 50 + i*20, 80 + i*20), 
                           (stats_x - i, stats_y - i, stats_width + i*2, stats_height + i*2), 2)
        pygame.draw.rect(screen, (100, 100, 150), stats_rect)
        pygame.draw.rect(screen, (150, 150, 200), stats_rect, 3)
        
        # Статистика (внутри рамки, по центру)
        final_score_text = label.render(f"Итоговые очки: {score}", True, (255, 215, 0))
        ghosts_killed_text = label.render(f"Призраков убито: {ghosts_killed}", True, (200, 100, 255))
        
        if is_tutorial:
            level_text = label.render("Обучение не пройдено", True, (100, 100, 255))
        else:
            level_text = label.render(f"Пройдено уровней: {current_level}", True, (100, 100, 255))
        
        # Вычисляем позиции для текста внутри рамки с равными отступами
        total_text_height = 50 * 3
        start_text_y = stats_y + (stats_height - total_text_height) // 2
        
        screen.blit(final_score_text, (1280 // 2 - final_score_text.get_width() // 2, start_text_y))
        screen.blit(ghosts_killed_text, (1280 // 2 - ghosts_killed_text.get_width() // 2, start_text_y + 50))
        screen.blit(level_text, (1280 // 2 - level_text.get_width() // 2, start_text_y + 100))
        
       
        button_width = 300  
        button_height = 60  
        button_spacing = 40  
        
        # Вычисляем позиции для двух кнопок рядом
        total_buttons_width = button_width * 2 + button_spacing
        start_button_x = (1280 - total_buttons_width) // 2
        button_y = stats_y + stats_height + 30
        
        # Проверяем, не выходят ли кнопки за нижний край
        if button_y + button_height > 700:
            button_y = 630
        
        menu_button = pygame.Rect(start_button_x, button_y, button_width, button_height)
        level_select_btn = pygame.Rect(start_button_x + button_width + button_spacing, button_y, button_width, button_height)
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Кнопка "Главное меню" с увеличенным шрифтом
        if menu_button.collidepoint(mouse_pos):
            pygame.draw.rect(screen, (80, 180, 230), menu_button)
            pygame.draw.rect(screen, (255, 255, 255), menu_button, 4)
        else:
            pygame.draw.rect(screen, (50, 150, 200), menu_button)
            pygame.draw.rect(screen, (0, 100, 150), menu_button, 4)
        
        menu_text = label.render("Главное меню", True, (255, 255, 255))
        screen.blit(menu_text, (menu_button.centerx - menu_text.get_width() // 2,
                                menu_button.centery - menu_text.get_height() // 2))
        
        # Кнопка "Выбор уровня" с увеличенным шрифтом
        if level_select_btn.collidepoint(mouse_pos):
            pygame.draw.rect(screen, (230, 130, 80), level_select_btn)
            pygame.draw.rect(screen, (255, 255, 255), level_select_btn, 4)
        else:
            pygame.draw.rect(screen, (200, 100, 50), level_select_btn)
            pygame.draw.rect(screen, (100, 50, 0), level_select_btn, 4)
        
        select_text = label.render("Выбор уровня", True, (255, 255, 255))
        screen.blit(select_text, (level_select_btn.centerx - select_text.get_width() // 2,
                                  level_select_btn.centery - select_text.get_height() // 2))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if menu_button.collidepoint(mouse_pos):
                    game_state = GameState.MAIN_MENU
                elif level_select_btn.collidepoint(mouse_pos):
                    game_state = GameState.LEVEL_SELECT
    
    elif game_state == GameState.GAME_WIN:
        # Золотистый фон с градиентом
        for i in range(720):
            color_value = 200 + int(i * 0.07)
            color = (255, color_value, 100)
            pygame.draw.line(screen, color, (0, i), (1280, i))
        
        # Партиклы конфетти
        if random.random() < 0.5:
            for _ in range(3):
                effect = Effect(random.randint(0, 1280), random.randint(0, 360), "coin_collect")
                effects.append(effect)
        
        # Эффекты
        for effect in effects[:]:
            if not effect.update():
                effects.remove(effect)
            else:
                effect.draw(screen)
        
        # Текст победы с анимацией (по центру)
        win_text = level_font.render("ПОБЕДА!", True, (255, 50, 50))
        shadow_win = level_font.render("ПОБЕДА!", True, (150, 0, 0))
        
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.002)) * 15
        win_y = 50 + pulse
        
        win_x = 1280 // 2 - win_text.get_width() // 2
        screen.blit(shadow_win, (win_x + 5, win_y + 5))
        screen.blit(win_text, (win_x, win_y))
        
        # Звездочки вокруг текста
        for i in range(8):
            angle = pygame.time.get_ticks() * 0.002 + i * math.pi / 4
            x = 1280 // 2 + math.cos(angle) * 180
            y = win_y + 50 + math.sin(angle) * 40
            star_text = level_font.render("⭐", True, (255, 255, 100))
            screen.blit(star_text, (x - 20, y - 20))
        
        # Разделительная линия (по центру)
        line_width = 450
        line_x = (1280 - line_width) // 2
        line_y = win_y + win_text.get_height() + 20
        pygame.draw.line(screen, (255, 100, 50), (line_x, line_y), (line_x + line_width, line_y), 3)
        
        # Рамка для статистики (по центру)
        stats_width = 650
        stats_height = 150
        stats_x = (1280 - stats_width) // 2
        stats_y = line_y + 25
        stats_rect = pygame.Rect(stats_x, stats_y, stats_width, stats_height)
        
        # Красивая рамка с градиентом
        for i in range(3):
            pygame.draw.rect(screen, (255 - i*30, 215 - i*30, 0), 
                           (stats_x - i, stats_y - i, stats_width + i*2, stats_height + i*2), 2)
        pygame.draw.rect(screen, (255, 215, 0, 100), stats_rect)
        pygame.draw.rect(screen, (255, 200, 0), stats_rect, 3)
        
        # Статистика (по центру)
        final_score = label.render(f"Итоговые очки: {score}", True, (255, 100, 0))
        congrats_text = label.render("Поздравляем! Вы прошли игру!", True, (0, 100, 0))
        
        # Центрируем текст внутри рамки
        total_text_height = 60 * 2
        start_text_y = stats_y + (stats_height - total_text_height) // 2
        
        screen.blit(final_score, (1280 // 2 - final_score.get_width() // 2, start_text_y))
        screen.blit(congrats_text, (1280 // 2 - congrats_text.get_width() // 2, start_text_y + 60))
        
        # УВЕЛИЧЕННЫЕ КНОПКИ (по центру, рядом друг с другом)
        button_width = 300  # Увеличено с 200 до 250
        button_height = 60  # Увеличено с 50 до 60
        button_spacing = 40  # Увеличено расстояние между кнопками
        
        total_buttons_width = button_width * 2 + button_spacing
        start_button_x = (1280 - total_buttons_width) // 2
        button_y = stats_y + stats_height + 30
        
        if button_y + button_height > 700:
            button_y = 630
        
        menu_button = pygame.Rect(start_button_x, button_y, button_width, button_height)
        level_select_btn = pygame.Rect(start_button_x + button_width + button_spacing, button_y, button_width, button_height)
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Кнопка "Главное меню"
        if menu_button.collidepoint(mouse_pos):
            pygame.draw.rect(screen, (80, 180, 230), menu_button)
            pygame.draw.rect(screen, (255, 255, 255), menu_button, 4)
        else:
            pygame.draw.rect(screen, (50, 150, 200), menu_button)
            pygame.draw.rect(screen, (0, 100, 150), menu_button, 4)
        
        menu_text = label.render("Главное меню", True, (255, 255, 255))
        screen.blit(menu_text, (menu_button.centerx - menu_text.get_width() // 2,
                                menu_button.centery - menu_text.get_height() // 2))
        
        # Кнопка "Выбор уровня"
        if level_select_btn.collidepoint(mouse_pos):
            pygame.draw.rect(screen, (230, 130, 80), level_select_btn)
            pygame.draw.rect(screen, (255, 255, 255), level_select_btn, 4)
        else:
            pygame.draw.rect(screen, (200, 100, 50), level_select_btn)
            pygame.draw.rect(screen, (100, 50, 0), level_select_btn, 4)
        
        select_text = label.render("Выбор уровня", True, (255, 255, 255))
        screen.blit(select_text, (level_select_btn.centerx - select_text.get_width() // 2,
                                  level_select_btn.centery - select_text.get_height() // 2))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if menu_button.collidepoint(mouse_pos):
                    game_state = GameState.MAIN_MENU
                elif level_select_btn.collidepoint(mouse_pos):
                    game_state = GameState.LEVEL_SELECT
    
    pygame.display.update()
    
    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if (game_state == GameState.TUTORIAL or game_state == GameState.PLAYING) and not level_transition:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if not is_jumping and is_on_ground:
                    player_velocity_y = jump_strength
                    is_jumping = True
                    is_on_ground = False
                    double_jump_available = True
                    has_double_jumped = False
                    effects.append(Effect(player_x + 35, player_y + 50, "jump"))
                    if is_tutorial:
                        add_tutorial_message("Хороший прыжок! Снова нажмите пробел в воздухе для двойного прыжка!", 120)
                elif double_jump_available and not has_double_jumped and is_jumping:
                    player_velocity_y = jump_strength * 0.9
                    double_jump_available = False
                    has_double_jumped = True
                    effects.append(Effect(player_x + 35, player_y + 50, "jump"))
                    if is_tutorial:
                        add_tutorial_message("Двойной прыжок! Отлично!", 90)
            
            if event.type == ghost_timer and len(current_level_obj.enemies) < 10 and not is_tutorial:
                spawn_y = 500 - ghost.get_height()
                if current_level_obj.platforms:
                    available_platforms = [p for p in current_level_obj.platforms if 1000 <= p.x <= 1300]
                    if available_platforms:
                        platform = random.choice(available_platforms)
                        spawn_y = platform.y - ghost.get_height()
                current_level_obj.enemies.append(Enemy(1280, spawn_y))
            
            if event.type == coin_timer and len(current_level_obj.coins) < 10:
                if current_level_obj.platforms:
                    available_platforms = [p for p in current_level_obj.platforms if 800 <= p.x <= 1200]
                    if available_platforms:
                        platform = random.choice(available_platforms)
                        coin_x = platform.x + random.randint(10, platform.width - 40)
                        coin_y = platform.y - 40
                        current_level_obj.coins.append(pygame.Rect(coin_x, coin_y, 30, 30))
            
            if event.type == pygame.KEYUP and event.key == pygame.K_b:
                if bullets_infinite or bullets_left > 0:
                    bullets.append(bullet.get_rect(topleft=(player_x + 70, player_y + 60)))
                    if not bullets_infinite:
                        bullets_left -= 1
                    effects.append(Effect(player_x + 70, player_y + 60, "shoot"))
                    if is_tutorial and bullets_left == 4:
                        add_tutorial_message("Вы выстрелили! Нажмите R чтобы перезарядиться.", 120)
    
    clock.tick(35)

pygame.quit()
sys.exit()
import pygame
from pygame import key
import random
import math
import sys
import os
import traceback



def get_resource_path(relative_path):
    """Получить путь к ресурсу для PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller временная папка
        base_path = sys._MEIPASS
    else:
        # Обычный путь при разработке
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

pygame.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Mini_Mario")
clock = pygame.time.Clock()
icon = pygame.image.load(get_resource_path("images/favicon.ico")).convert_alpha()
pygame.display.set_icon(icon)

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
MAIN_MENU = 0
PLAYING = 1
GAME_OVER = 2
LEVEL_TRANSITION = 3
GAME_WIN = 4

game_state = MAIN_MENU

bullets = []
bullets_left = 5

ghost_list_in_game = []
coins = []
score = 0
ghosts_killed = 0

player_anim_count = 0
bg_x = 0

player_speed = 15
player_x = 150
player_y = 500

is_jumping = False
player_velocity_y = 0
gravity = 1.0
jump_strength = -18
is_on_ground = True
double_jump_available = False
has_double_jumped = False

current_level = 1
max_level = 3
level_complete = False
level_transition = False
level_transition_timer = 0

level_data = {
    1: {"scroll_speed": 4, "ghost_spawn": 2500, "goal": 150},
    2: {"scroll_speed": 5, "ghost_spawn": 2000, "goal": 250},
    3: {"scroll_speed": 6, "ghost_spawn": 1500, "goal": 350}
}

scroll_speed = level_data[1]["scroll_speed"]

platforms = [
    pygame.Rect(300, 550, 200, 20),
    pygame.Rect(600, 450, 200, 20),
    pygame.Rect(900, 350, 200, 20),
    pygame.Rect(1200, 500, 250, 20),
]


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
        self.velocity_y += 0.1  # гравитация
        self.life -= 1
        return self.life > 0

    def draw(self, surface):
        alpha = int(255 * (self.life / self.max_life))
        if alpha > 0:
            particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, (*self.color, alpha), (self.size, self.size), self.size)
            surface.blit(particle_surface, (int(self.x - self.size), int(self.y - self.size)))


# Эффекты
class Effect:
    def __init__(self, x, y, effect_type):
        self.x = x
        self.y = y
        self.type = effect_type
        self.particles = []
        self.duration = 0

        if effect_type == "jump":
            self.create_jump_effect()
        elif effect_type == "land":
            self.create_land_effect()
        elif effect_type == "shoot":
            self.create_shoot_effect()
        elif effect_type == "ghost_death":
            self.create_ghost_death_effect()
        elif effect_type == "coin_collect":
            self.create_coin_collect_effect()

    def create_jump_effect(self):
        for _ in range(15):
            angle = random.uniform(0, math.pi)
            speed = random.uniform(1, 3)
            velocity_x = math.cos(angle) * speed * random.choice([-1, 1])
            velocity_y = -abs(math.sin(angle) * speed)
            self.particles.append(Particle(
                self.x + random.randint(-10, 10),
                self.y + 50,
                (100, 150, 255),  # Голубые частицы
                velocity_x,
                velocity_y,
                random.randint(2, 4),
                random.randint(20, 40)
            ))
        self.duration = 40

    def create_land_effect(self):
        for _ in range(20):
            angle = random.uniform(0, math.pi)
            speed = random.uniform(1, 4)
            velocity_x = math.cos(angle) * speed * random.choice([-1, 1])
            velocity_y = -abs(math.sin(angle) * speed) * 0.5
            self.particles.append(Particle(
                self.x + random.randint(-20, 20),
                self.y + 45,
                (150, 150, 200),  # Серо-голубые частицы
                velocity_x,
                velocity_y,
                random.randint(2, 5),
                random.randint(30, 50)
            ))
        self.duration = 50

    def create_shoot_effect(self):
        for _ in range(8):
            angle = random.uniform(-0.3, 0.3)
            speed = random.uniform(2, 5)
            velocity_x = math.cos(angle) * speed
            velocity_y = math.sin(angle) * speed
            self.particles.append(Particle(
                self.x + 70,
                self.y + 60,
                (255, 255, 100),  # Желтые частицы
                velocity_x,
                velocity_y,
                random.randint(2, 3),
                random.randint(15, 25)
            ))
        self.duration = 25

    def create_ghost_death_effect(self):
        for _ in range(30):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 6)
            velocity_x = math.cos(angle) * speed
            velocity_y = math.sin(angle) * speed
            self.particles.append(Particle(
                self.x + random.randint(-10, 10),
                self.y + random.randint(-10, 10),
                (200, 100, 255),  # Фиолетовые частицы
                velocity_x,
                velocity_y,
                random.randint(3, 6),
                random.randint(40, 60)
            ))
        self.duration = 60

    def create_coin_collect_effect(self):
        for _ in range(25):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 4)
            velocity_x = math.cos(angle) * speed
            velocity_y = math.sin(angle) * speed
            self.particles.append(Particle(
                self.x + 15,
                self.y + 15,
                (255, 215, 0),  # Золотые частицы
                velocity_x,
                velocity_y,
                random.randint(2, 4),
                random.randint(30, 45)
            ))
        self.duration = 45

    def update(self):
        for particle in self.particles[:]:
            if not particle.update():
                self.particles.remove(particle)
        self.duration -= 1
        return len(self.particles) > 0 and self.duration > 0

    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)


# Списки эффектов
effects = []
floating_numbers = []


# Плавающие числа для отображения очков
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


sounds = pygame.mixer.Sound(get_resource_path("sounds/sounds.mp3"))
sounds.play()


ghost_timer = pygame.USEREVENT + 1
pygame.time.set_timer(ghost_timer, level_data[1]["ghost_spawn"])

coin_timer = pygame.USEREVENT + 2
pygame.time.set_timer(coin_timer, 1500)

label = pygame.font.SysFont("comicsans", 40, bold=True)
ammo_font = pygame.font.SysFont("comicsans", 30, bold=True)
level_font = pygame.font.SysFont("comicsans", 60, bold=True)
title_font = pygame.font.SysFont("comicsans", 80, bold=True)
menu_font = pygame.font.SysFont("comicsans", 50, bold=True)

lose_label = label.render("GAME OVER!", False, (175, 91, 61))
restart_label = label.render("Restarting...", False, (255, 161, 93))
restart_label_rect = restart_label.get_rect(topleft=(525, 420))

# Кнопки меню
start_button = pygame.Rect(540, 300, 200, 60)
quit_button = pygame.Rect(540, 400, 200, 60)

# Переменная для отслеживания приземления
was_on_ground = True


def check_platform_collision(player_rect, check_vertical=True):
    collision_type = None
    collision_platform = None

    for platform in platforms:
        if player_rect.colliderect(platform):
            if check_vertical:
                # Проверка столкновения сверху (игрок падает на платформу)
                if (player_velocity_y >= 0 and
                        player_rect.bottom >= platform.top and
                        player_rect.bottom <= platform.top + 25 and
                        player_rect.right > platform.left + 5 and
                        player_rect.left < platform.right - 5):
                    collision_type = "top"
                    collision_platform = platform
                    break
                # Проверка столкновения снизу (игрок ударяется головой о платформу)
                elif (player_velocity_y < 0 and
                      player_rect.top <= platform.bottom and
                      player_rect.top >= platform.bottom - 15 and
                      player_rect.right > platform.left + 5 and
                      player_rect.left < platform.right - 5):
                    collision_type = "bottom"
                    collision_platform = platform
                    break
            else:
                # Проверка боковых столкновений
                if (player_rect.right > platform.left and
                        player_rect.left < platform.right and
                        player_rect.bottom > platform.top + 10 and
                        player_rect.top < platform.bottom - 10):
                    # Определяем с какой стороны столкновение
                    if abs(player_rect.right - platform.left) < abs(player_rect.left - platform.right):
                        collision_type = "right"
                    else:
                        collision_type = "left"
                    collision_platform = platform
                    break

    return collision_type, collision_platform


def reset_game():
    global player_x, player_y, player_velocity_y, ghost_list_in_game, bullets, coins, score, bullets_left, bg_x, platforms, is_on_ground, double_jump_available, has_double_jumped, ghosts_killed, current_level, level_complete, scroll_speed, game_state, effects, floating_numbers, was_on_ground

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
    game_state = PLAYING
    was_on_ground = True

    ghost_list_in_game.clear()
    bullets.clear()
    coins.clear()
    effects.clear()
    floating_numbers.clear()

    platforms = [
        pygame.Rect(300, 550, 200, 20),
        pygame.Rect(600, 450, 200, 20),
        pygame.Rect(900, 350, 200, 20),
        pygame.Rect(1200, 500, 250, 20),
    ]

    scroll_speed = level_data[1]["scroll_speed"]
    pygame.time.set_timer(ghost_timer, level_data[1]["ghost_spawn"])


def next_level():
    global current_level, level_complete, level_transition, level_transition_timer, scroll_speed, game_state

    if current_level < max_level:
        current_level += 1
        level_complete = True
        level_transition = True
        level_transition_timer = pygame.time.get_ticks()

        ghost_list_in_game.clear()
        bullets.clear()
        coins.clear()
        bullets_left = 5

        scroll_speed = level_data[current_level]["scroll_speed"]
        pygame.time.set_timer(ghost_timer, level_data[current_level]["ghost_spawn"])
        return True
    return False


def draw_level_transition():
    screen.fill((200, 230, 255))
    level_text = level_font.render(f"LEVEL {current_level} COMPLETE!", True, (0, 100, 200))
    next_text = label.render("Get ready for next level...", True, (50, 50, 50))
    screen.blit(level_text, (1280 // 2 - level_text.get_width() // 2, 300))
    screen.blit(next_text, (1280 // 2 - next_text.get_width() // 2, 400))


def draw_hud():
    level_text = ammo_font.render(f"Level: {current_level}/{max_level}", True, (255, 255, 255))
    progress_text = ammo_font.render(f"Progress: {score}/{level_data[current_level]['goal']}", True, (255, 255, 255))
    ammo_text = ammo_font.render(f"Ammo: {bullets_left}", True, (255, 255, 255))
    score_text = ammo_font.render(f"Score: {score}", True, (255, 215, 0))

    screen.blit(level_text, (10, 10))
    screen.blit(progress_text, (10, 50))
    screen.blit(ammo_text, (10, 90))
    screen.blit(score_text, (10, 130))


def draw_main_menu():
    screen.fill((100, 150, 255))

    # Анимированные частицы на фоне меню
    for effect in effects[:]:
        if not effect.update():
            effects.remove(effect)
        else:
            effect.draw(screen)

    # Добавляем новые частицы для фона меню
    if random.random() < 0.3:
        effect_type = random.choice(["coin_collect", "ghost_death"])
        effects.append(Effect(
            random.randint(0, 1280),
            random.randint(0, 720),
            effect_type
        ))

    # Заголовок
    title_text = title_font.render("MINI MARIO", True, (255, 215, 0))
    screen.blit(title_text, (1280 // 2 - title_text.get_width() // 2, 150))

    # Кнопка "Start Game"
    pygame.draw.rect(screen, (50, 200, 50), start_button)
    pygame.draw.rect(screen, (0, 100, 0), start_button, 3)
    start_text = menu_font.render("Start Game", True, (255, 255, 255))
    screen.blit(start_text, (start_button.centerx - start_text.get_width() // 2,
                             start_button.centery - start_text.get_height() // 2))

    # Кнопка "Quit"Ы
    pygame.draw.rect(screen, (200, 50, 50), quit_button)
    pygame.draw.rect(screen, (100, 0, 0), quit_button, 3)
    quit_text = menu_font.render("Quit", True, (255, 255, 255))
    screen.blit(quit_text, (quit_button.centerx - quit_text.get_width() // 2,
                            quit_button.centery - quit_text.get_height() // 2))

    # Инструкции
    instructions = [
        "CONTROLS:",
        "A/D - Move Left/Right",
        "SPACE - Jump (Double Tap for Double Jump)",
        "B - Shoot",
        "R - Reload Ammo"
    ]

    for i, instruction in enumerate(instructions):
        inst_text = label.render(instruction, True, (255, 255, 255))
        screen.blit(inst_text, (1280 // 2 - inst_text.get_width() // 2, 500 + i * 40))


running = True
while running:
    if game_state == MAIN_MENU:
        draw_main_menu()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if start_button.collidepoint(mouse_pos):
                    reset_game()
                elif quit_button.collidepoint(mouse_pos):
                    running = False
                    pygame.quit()

    elif game_state == PLAYING:
        screen.blit(bg, (bg_x, 0))
        screen.blit(bg, (bg_x + 1280, 0))

        # Отрисовка эффектов
        for effect in effects[:]:
            if not effect.update():
                effects.remove(effect)
            else:
                effect.draw(screen)

        # Отрисовка плавающих чисел
        for floating_number in floating_numbers[:]:
            if not floating_number.update():
                floating_numbers.remove(floating_number)
            else:
                floating_number.draw(screen)

        # ПРОВЕРКА ЗАВЕРШЕНИЯ УРОВНЯ
        if not level_complete and score >= level_data[current_level]["goal"]:
            if not next_level():
                # ПОБЕДА В ИГРЕ
                game_state = GAME_WIN

        # ПЕРЕХОД МЕЖДУ УРОВНЯМИ
        if level_transition:
            draw_level_transition()
            if pygame.time.get_ticks() - level_transition_timer > 2000:
                level_transition = False
                level_complete = False
            pygame.display.update()
            continue

        bg_x -= scroll_speed
        if bg_x <= -1280:
            bg_x = 0

        for platform in platforms:
            platform.x -= scroll_speed

        platforms = [p for p in platforms if p.x + p.width > 0]

        if platforms and platforms[-1].x < 400:
            if random.random() < 0.5:
                new_x = 1280
                new_y = random.choice([500, 450, 400])
                new_width = random.randint(180, 300)
                # Проверка на перекрытие с существующими платформами
                new_platform = pygame.Rect(new_x, new_y, new_width, 20)
                overlap = False
                for platform in platforms:
                    if (new_platform.colliderect(platform) and
                            abs(new_platform.y - platform.y) < 50):
                        overlap = True
                        break
                if not overlap:
                    platforms.append(new_platform)

        for platform in platforms:
            pygame.draw.rect(screen, (139, 69, 19), platform)
            pygame.draw.rect(screen, (101, 50, 12), platform, 2)

        player_rect = walk_left[0].get_rect(topleft=(player_x, player_y))

        coins_to_remove = []
        for i, coin in enumerate(coins):
            screen.blit(coin_img, coin)
            coin.x -= scroll_speed

            if coin.x + coin.width < 0:
                coins_to_remove.append(i)
                continue

            if player_rect.colliderect(coin):
                coins_to_remove.append(i)
                score += 10
                # Эффект сбора монеты
                effects.append(Effect(coin.x + 15, coin.y + 15, "coin_collect"))
                floating_numbers.append(FloatingNumber(coin.x, coin.y, 10, (255, 215, 0)))

        for i in sorted(coins_to_remove, reverse=True):
            if i < len(coins):
                coins.pop(i)

        ghost_to_remove = []
        for (i, el) in enumerate(ghost_list_in_game):
            screen.blit(ghost, el)
            el.x -= 15 + scroll_speed

            ghost_on_surface = False
            for platform in platforms:
                if (el.bottom >= platform.top and
                        el.bottom <= platform.top + 10 and
                        el.right > platform.left and
                        el.left < platform.right):
                    ghost_on_surface = True
                    el.y = platform.top - el.height
                    break

            if not ghost_on_surface:
                if el.bottom >= 500:
                    ghost_on_surface = True
                    el.y = 500 - el.height

            if not ghost_on_surface:
                el.y += 5
            else:
                if el.y < 100:
                    el.y = 100

            if el.x + el.width < 0:
                ghost_to_remove.append(i)
            elif player_rect.colliderect(el):
                game_state = GAME_OVER

        for i in sorted(ghost_to_remove, reverse=True):
            if i < len(ghost_list_in_game):
                ghost_list_in_game.pop(i)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            bullets_left = 5

        if keys[pygame.K_a]:
            screen.blit(walk_left[player_anim_count], (player_x, player_y))
        else:
            screen.blit(walk_right[player_anim_count], (player_x, player_y))

        if keys[pygame.K_a] and player_x > 50:
            player_x -= player_speed
        elif keys[pygame.K_d] and player_x < 1200:
            player_x += player_speed

        # ОБРАБОТКА БОКОВЫХ СТОЛКНОВЕНИЙ
        player_rect.x = player_x
        side_collision, side_platform = check_platform_collision(player_rect, check_vertical=False)

        if side_collision == "right":
            player_x = side_platform.left - player_rect.width
        elif side_collision == "left":
            player_x = side_platform.right

        # ОБРАБОТКА ВЕРТИКАЛЬНОГО ДВИЖЕНИЯ И СТОЛКНОВЕНИЙ
        player_velocity_y += gravity
        player_y += player_velocity_y

        player_rect.y = player_y
        collision_type, collision_platform = check_platform_collision(player_rect, check_vertical=True)

        # Проверка приземления для эффекта
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

        if (keys[pygame.K_a] or keys[pygame.K_d]) and is_on_ground:
            player_anim_count = (player_anim_count + 1) % 4

        bullets_to_remove = []
        for (i, el) in enumerate(bullets):
            screen.blit(bullet, (el.x, el.y))
            el.x += 20

            if el.x > 1282:
                bullets_to_remove.append(i)
                continue

            if ghost_list_in_game:
                for (index, ghost_el) in enumerate(ghost_list_in_game):
                    if el.colliderect(ghost_el):
                        ghost_list_in_game.pop(index)
                        bullets_to_remove.append(i)
                        ghosts_killed += 1
                        score += 25
                        # Эффект смерти призрака
                        effects.append(
                            Effect(ghost_el.x + ghost_el.width // 2, ghost_el.y + ghost_el.height // 2, "ghost_death"))
                        floating_numbers.append(FloatingNumber(ghost_el.x, ghost_el.y, 25, (200, 100, 255)))
                        break

        for i in sorted(bullets_to_remove, reverse=True):
            if i < len(bullets):
                bullets.pop(i)

        draw_hud()

    elif game_state == GAME_OVER:
        screen.fill((254, 242, 232))
        screen.blit(lose_label, (525, 320))
        final_score_text = label.render(f"Final Score: {score}", False, (255, 215, 0))
        ghosts_killed_text = label.render(f"Ghosts Killed: {ghosts_killed}", False, (200, 100, 255))
        level_text = label.render(f"Level Reached: {current_level}", False, (100, 100, 255))

        screen.blit(final_score_text, (510, 380))
        screen.blit(ghosts_killed_text, (510, 430))
        screen.blit(level_text, (510, 480))

        # Кнопка возврата в меню
        menu_button = pygame.Rect(550, 550, 200, 60)
        pygame.draw.rect(screen, (50, 150, 200), menu_button)
        pygame.draw.rect(screen, (0, 100, 150), menu_button, 3)
        menu_text = label.render("Main Menu", True, (255, 255, 255))
        screen.blit(menu_text, (menu_button.centerx - menu_text.get_width() // 2,
                                menu_button.centery - menu_text.get_height() // 2))

        mouse = pygame.mouse.get_pos()
        if menu_button.collidepoint(mouse) and pygame.mouse.get_pressed()[0]:
            game_state = MAIN_MENU

    elif game_state == GAME_WIN:
        screen.fill((255, 255, 200))
        win_text = level_font.render("YOU WIN!", True, (255, 215, 0))
        final_score = label.render(f"Final Score: {score}", True, (0, 100, 200))
        screen.blit(win_text, (1280 // 2 - win_text.get_width() // 2, 300))
        screen.blit(final_score, (1280 // 2 - final_score.get_width() // 2, 400))

        # Кнопка возврата в меню
        menu_button = pygame.Rect(550, 500, 200, 60)
        pygame.draw.rect(screen, (50, 150, 200), menu_button)
        pygame.draw.rect(screen, (0, 100, 150), menu_button, 3)
        menu_text = label.render("Main Menu", True, (255, 255, 255))
        screen.blit(menu_text, (menu_button.centerx - menu_text.get_width() // 2,
                                menu_button.centery - menu_text.get_height() // 2))

        mouse = pygame.mouse.get_pos()
        if menu_button.collidepoint(mouse) and pygame.mouse.get_pressed()[0]:
            game_state = MAIN_MENU

    pygame.display.update()

    # Обработка событий для всех состояний игры
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()

        if game_state == PLAYING and not level_transition:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if not is_jumping and is_on_ground:
                    player_velocity_y = jump_strength
                    is_jumping = True
                    is_on_ground = False
                    double_jump_available = True
                    has_double_jumped = False
                    # Эффект прыжка
                    effects.append(Effect(player_x + 35, player_y + 50, "jump"))
                elif double_jump_available and not has_double_jumped and is_jumping:
                    player_velocity_y = jump_strength * 0.9
                    double_jump_available = False
                    has_double_jumped = True
                    # Эффект двойного прыжка
                    effects.append(Effect(player_x + 35, player_y + 50, "jump"))

            if event.type == ghost_timer:
                spawn_y = 500 - ghost.get_height()
                available_platforms = [p for p in platforms if 1000 <= p.x <= 1300]
                if available_platforms:
                    platform = random.choice(available_platforms)
                    spawn_y = platform.y - ghost.get_height()
                ghost_list_in_game.append(ghost.get_rect(topleft=(1280, spawn_y)))

            if event.type == coin_timer and len(coins) < 5:
                available_platforms = [p for p in platforms if 800 <= p.x <= 1200]
                if available_platforms:
                    platform = random.choice(available_platforms)
                    coin_x = platform.x + random.randint(10, platform.width - 40)
                    coin_y = platform.y - 40
                    coins.append(pygame.Rect(coin_x, coin_y, 30, 30))

            if event.type == pygame.KEYUP and event.key == pygame.K_b and bullets_left > 0:
                bullets.append(bullet.get_rect(topleft=(player_x + 70, player_y + 60)))
                bullets_left -= 1
                # Эффект выстрела
                effects.append(Effect(player_x + 70, player_y + 60, "shoot"))

    clock.tick(35)

import pygame
from pygame import key
import random

image_path = "/data/data/game.myapp/files/app/"

pygame.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Mini_Mario")
clock = pygame.time.Clock()
icon = pygame.image.load(image_path + "images/icon.png").convert_alpha()
pygame.display.set_icon(icon)

bg = pygame.image.load(image_path + "images/font.png").convert_alpha()
walk_right = [
    pygame.image.load(image_path + "images/player_right/player_right1.png").convert_alpha(),
    pygame.image.load(image_path + "images/player_right/player_right2.png").convert_alpha(),
    pygame.image.load(image_path + "images/player_right/player_right3.png").convert_alpha(),
    pygame.image.load(image_path + "images/player_right/player_right4.png").convert_alpha(),
]
walk_left = [
    pygame.image.load(image_path + "images/player_left/player_left1.png").convert_alpha(),
    pygame.image.load(image_path + "images/player_left/player_left2.png").convert_alpha(),
    pygame.image.load(image_path + "images/player_left/player_left3.png").convert_alpha(),
    pygame.image.load(image_path + "images/player_left/player_left4.png").convert_alpha(),
]

ghost = pygame.image.load(image_path + "images/ghost.png").convert_alpha()
bullet = pygame.image.load(image_path + "images/bullet.png").convert_alpha()
coin_img = pygame.image.load(image_path + "images/coin.png")
coin_img = pygame.transform.scale(coin_img, (30, 30))

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

sounds = pygame.mixer.Sound("sounds/sounds.mp3")

ghost_timer = pygame.USEREVENT + 1
pygame.time.set_timer(ghost_timer, level_data[1]["ghost_spawn"])

coin_timer = pygame.USEREVENT + 2
pygame.time.set_timer(coin_timer, 1500)

label = pygame.font.SysFont("comicsans", 40, bold=True)
ammo_font = pygame.font.SysFont("comicsans", 30, bold=True)
level_font = pygame.font.SysFont("comicsans", 60, bold=True)

lose_label = label.render("GAME OVER!", False, (175, 91, 61))
restart_label = label.render("Restarting...", False, (255, 161, 93))
restart_label_rect = restart_label.get_rect(topleft=(525, 420))

gameplay = True


def check_platform_collision(player_rect, check_vertical=True):
    collision_type = None
    collision_platform = None

    for platform in platforms:
        if player_rect.colliderect(platform):
            if check_vertical:
                if (player_velocity_y >= 0 and
                        player_rect.bottom >= platform.top and
                        player_rect.bottom <= platform.top + 20 and
                        player_rect.right > platform.left + 10 and
                        player_rect.left < platform.right - 10):
                    collision_type = "top"
                    collision_platform = platform
                    break
                elif (player_velocity_y < 0 and
                      player_rect.top <= platform.bottom and
                      player_rect.top >= platform.bottom - 10 and
                      player_rect.right > platform.left + 10 and
                      player_rect.left < platform.right - 10):
                    collision_type = "bottom"
                    collision_platform = platform
                    break
            else:
                if (player_rect.right > platform.left and
                        player_rect.left < platform.right and
                        player_rect.bottom > platform.top + 5 and
                        player_rect.top < platform.bottom - 5):
                    collision_type = "side"
                    collision_platform = platform
                    break

    return collision_type, collision_platform


def reset_game():
    global player_x, player_y, player_velocity_y, ghost_list_in_game, bullets, coins, score, bullets_left, bg_x, platforms, is_on_ground, double_jump_available, has_double_jumped, ghosts_killed, current_level, level_complete

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

    ghost_list_in_game.clear()
    bullets.clear()
    coins.clear()

    platforms = [
        pygame.Rect(300, 550, 200, 20),
        pygame.Rect(600, 450, 200, 20),
        pygame.Rect(900, 350, 200, 20),
        pygame.Rect(1200, 500, 250, 20),
    ]

    scroll_speed = level_data[1]["scroll_speed"]
    pygame.time.set_timer(ghost_timer, level_data[1]["ghost_spawn"])


def next_level():
    global current_level, level_complete, level_transition, level_transition_timer, scroll_speed

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


running = True
while running:

    screen.blit(bg, (bg_x, 0))
    screen.blit(bg, (bg_x + 1280, 0))

    if gameplay:
        # ПРОВЕРКА ЗАВЕРШЕНИЯ УРОВНЯ
        if not level_complete and score >= level_data[current_level]["goal"]:
            if not next_level():
                # ПОБЕДА В ИГРЕ
                screen.fill((255, 255, 200))
                win_text = level_font.render("YOU WIN!", True, (255, 215, 0))
                final_score = label.render(f"Final Score: {score}", True, (0, 100, 200))
                screen.blit(win_text, (1280 // 2 - win_text.get_width() // 2, 300))
                screen.blit(final_score, (1280 // 2 - final_score.get_width() // 2, 400))
                pygame.display.update()
                pygame.time.wait(3000)
                reset_game()
                continue

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
                platforms.append(pygame.Rect(new_x, new_y, new_width, 20))

    for platform in platforms:
        pygame.draw.rect(screen, (139, 69, 19), platform)
        pygame.draw.rect(screen, (101, 50, 12), platform, 2)

    if gameplay and not level_transition:
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
                gameplay = False

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

        player_rect.x = player_x
        side_collision, side_platform = check_platform_collision(player_rect, check_vertical=False)

        if side_collision == "side":
            if keys[pygame.K_a]:
                player_x = side_platform.right
            elif keys[pygame.K_d]:
                player_x = side_platform.left - player_rect.width

        player_velocity_y += gravity
        player_y += player_velocity_y

        player_rect.y = player_y
        collision_type, collision_platform = check_platform_collision(player_rect, check_vertical=True)

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
                        break

        for i in sorted(bullets_to_remove, reverse=True):
            if i < len(bullets):
                bullets.pop(i)

        draw_hud()

    else:
        screen.fill((254, 242, 232))
        screen.blit(lose_label, (525, 320))
        final_score_text = label.render(f"Final Score: {score}", False, (255, 215, 0))
        ghosts_killed_text = label.render(f"Ghosts Killed: {ghosts_killed}", False, (200, 100, 255))
        level_text = label.render(f"Level Reached: {current_level}", False, (100, 100, 255))

        screen.blit(final_score_text, (500, 380))
        screen.blit(ghosts_killed_text, (500, 465))
        screen.blit(level_text, (500, 510))
        screen.blit(restart_label, restart_label_rect)

        mouse = pygame.mouse.get_pos()
        if restart_label_rect.collidepoint(mouse) and pygame.mouse.get_pressed()[0]:
            gameplay = True
            reset_game()

    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and gameplay and not level_transition:
            if not is_jumping and is_on_ground:
                player_velocity_y = jump_strength
                is_jumping = True
                is_on_ground = False
                double_jump_available = True
                has_double_jumped = False
            elif double_jump_available and not has_double_jumped and is_jumping:
                player_velocity_y = jump_strength * 0.9
                double_jump_available = False
                has_double_jumped = True

        if event.type == ghost_timer and gameplay and not level_transition:
            spawn_y = 500 - ghost.get_height()
            available_platforms = [p for p in platforms if 1000 <= p.x <= 1300]
            if available_platforms:
                platform = random.choice(available_platforms)
                spawn_y = platform.y - ghost.get_height()
            ghost_list_in_game.append(ghost.get_rect(topleft=(1280, spawn_y)))

        if event.type == coin_timer and gameplay and not level_transition and len(coins) < 5:
            available_platforms = [p for p in platforms if 800 <= p.x <= 1200]
            if available_platforms:
                platform = random.choice(available_platforms)
                coin_x = platform.x + random.randint(10, platform.width - 40)
                coin_y = platform.y - 40
                coins.append(pygame.Rect(coin_x, coin_y, 30, 30))

        if gameplay and event.type == pygame.KEYUP and event.key == pygame.K_b and bullets_left > 0 and not level_transition:
            bullets.append(bullet.get_rect(topleft=(player_x + 70, player_y + 60)))
            bullets_left -= 1

    clock.tick(40)
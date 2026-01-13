import pygame
import random
import sys
import time

pygame.init()

WIDTH, HEIGHT = 640, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CONTRA - Pygame")

clock = pygame.time.Clock()
font_big = pygame.font.SysFont("monospace", 48, bold=True)
font_med = pygame.font.SysFont("monospace", 24, bold=True)
font_small = pygame.font.SysFont("monospace", 16, bold=True)

# Estados: menu, playing, gameOver
game_state = "menu"
score = 0
lives = 3
level = 1

player = {
    "x": 50, "y": 300, "vx": 0, "vy": 0,
    "width": 32, "height": 32,
    "jumping": False,
    "direction": "right",
    "shooting": False
}

bullets = []
enemies = []
platforms = []
keys = {}

camera_x = 0
menu_selection = 0
anim_frame = 0
last_enemy_spawn = time.time()


def start_game():
    global game_state, score, lives, level, player
    global bullets, enemies, camera_x, platforms

    game_state = "playing"
    score = 0
    lives = 3
    level = 1

    player.update({"x": 50, "y": 300, "vx": 0, "vy": 0,
                   "jumping": False, "direction": "right",
                   "shooting": False})
    bullets = []
    enemies = []
    camera_x = 0

    platforms[:] = [
        {"x": 0, "y": 360, "width": 2000, "height": 40},
        {"x": 200, "y": 280, "width": 150, "height": 20},
        {"x": 400, "y": 220, "width": 150, "height": 20},
        {"x": 600, "y": 280, "width": 150, "height": 20},
        {"x": 800, "y": 200, "width": 150, "height": 20},
    ]


def shoot():
    p = player
    bullets.append({
        "x": p["x"] + (p["direction"] == "right") * p["width"],
        "y": p["y"] + p["height"] // 2,
        "vx": 8 if p["direction"] == "right" else -8,
        "width": 8,
        "height": 3,
        "enemy": False
    })
    player["shooting"] = True


def spawn_enemy():
    types = ["soldier", "runner"]
    t = random.choice(types)
    enemies.append({
        "x": camera_x + WIDTH + random.randint(0, 200),
        "y": 320,
        "vx": -2.5 if t == "runner" else -1,
        "width": 32,
        "height": 32,
        "type": t,
        "health": 1,
        "shootTimer": random.randint(30, 90)
    })


def draw_menu():
    screen.fill((0, 0, 0))
    text = font_big.render("CONTRA", True, (255, 0, 0))
    screen.blit(text, (WIDTH//2 - text.get_width()//2, 80))

    screen.blit(font_med.render("1987 KONAMI", True, (255, 255, 255)),
                (WIDTH//2 - 80, 130))

    options = ["1 PLAYER", "2 PLAYERS"]
    for i, opt in enumerate(options):
        col = (255, 0, 0) if menu_selection == i else (150, 150, 150)
        txt = font_med.render(opt, True, col)
        screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 200 + i * 40))

    cursor = font_med.render("▶", True, (255, 0, 0))
    screen.blit(cursor, (180, 200 + menu_selection * 40))


def draw_background():
    screen.fill((64, 128, 192))
    for i in range(10):
        offset = (camera_x * 0.3) % 200
        pygame.draw.polygon(screen, (32, 96, 64),
                            [(i * 200 - offset, 300),
                             (i * 200 + 80 - offset, 200),
                             (i * 200 + 160 - offset, 300)])


def draw_platforms():
    for plat in platforms:
        sx = plat["x"] - camera_x
        pygame.draw.rect(screen, (64, 128, 64),
                         (sx, plat["y"], plat["width"], plat["height"]))


def draw_player():
    p = player
    sx = p["x"] - camera_x
    pygame.draw.rect(screen, (0, 128, 255), (sx+8, p["y"]+8, 16, 16))
    pygame.draw.rect(screen, (255, 176, 128), (sx+10, p["y"], 12, 10))
    gunx = sx + 24 if p["direction"] == "right" else sx + 4
    pygame.draw.rect(screen, (64, 64, 64), (gunx, p["y"]+12, 8, 3))


def draw_enemies():
    for e in enemies:
        sx = e["x"] - camera_x
        col = (255, 64, 64) if e["type"] == "runner" else (128, 64, 64)
        pygame.draw.rect(screen, col, (sx+8, e["y"]+8, 16, 16))
        pygame.draw.rect(screen, (192, 128, 96), (sx+10, e["y"], 12, 10))


def draw_bullets():
    for b in bullets:
        sx = b["x"] - camera_x
        pygame.draw.rect(screen, (255, 255, 0), (sx, b["y"], b["width"], b["height"]))


def draw_hud():
    pygame.draw.rect(screen, (0, 0, 0), (0, 0, WIDTH, 30))
    screen.blit(font_small.render(f"1P {score:06d}", True, (255, 255, 255)), (10, 6))
    screen.blit(font_small.render(f"LIVES: {lives}", True, (255, 255, 255)), (250, 6))
    screen.blit(font_small.render(f"STAGE {level}", True, (255, 255, 255)), (450, 6))


def update():
    global camera_x, lives, game_state, score, last_enemy_spawn

    p = player

    # Movimiento
    if keys.get(pygame.K_LEFT):
        p["vx"] = -4
        p["direction"] = "left"
    elif keys.get(pygame.K_RIGHT):
        p["vx"] = 4
        p["direction"] = "right"
    else:
        p["vx"] = 0

    if keys.get(pygame.K_UP) and not p["jumping"]:
        p["vy"] = -12
        p["jumping"] = True

    # Física
    p["vy"] += 0.6
    p["x"] += p["vx"]
    p["y"] += p["vy"]

    # Plataformas
    for plat in platforms:
        if (p["x"]+p["width"] > plat["x"] and p["x"] < plat["x"]+plat["width"] and
            p["y"]+p["height"] > plat["y"] and p["y"]+p["height"] < plat["y"]+plat["height"]+10 and
            p["vy"] > 0):
            p["y"] = plat["y"] - p["height"]
            p["vy"] = 0
            p["jumping"] = False

    # Caída muerte
    if p["y"] > HEIGHT:
        lives -= 1
        if lives <= 0:
            game_over()
            return
        p.update({"x": 50, "y": 300, "vx": 0, "vy": 0})

    # Cámara
    camera_x = max(0, p["x"] - 200)

    # Balas
    for b in bullets[:]:
        b["x"] += b["vx"]
        if b["x"] < camera_x - 50 or b["x"] > camera_x + WIDTH + 50:
            bullets.remove(b)

    # Enemigos spawn
    if time.time() - last_enemy_spawn > 2:
        spawn_enemy()
        last_enemy_spawn = time.time()

    # Enemigos update
    for e in enemies[:]:
        e["x"] += e["vx"]

        # Balas enemigas
        e["shootTimer"] -= 1
        if e["shootTimer"] <= 0 and random.random() < 0.02:
            bullets.append({
                "x": e["x"],
                "y": e["y"] + e["height"]//2,
                "vx": -6,
                "width": 8,
                "height": 3,
                "enemy": True
            })
            e["shootTimer"] = random.randint(60, 150)

        # Balas jugador vs enemigo
        for b in bullets[:]:
            if not b["enemy"] and (b["x"]+b["width"] > e["x"] and b["x"] < e["x"]+e["width"] and
                                   b["y"]+b["height"] > e["y"] and b["y"] < e["y"]+e["height"]):
                e["health"] -= 1
                bullets.remove(b)
                if e["health"] <= 0:
                    score += 100
                    enemies.remove(e)
                break

        # Enemigo vs jugador
        if (p["x"]+p["width"] > e["x"] and p["x"] < e["x"]+e["width"] and
            p["y"]+p["height"] > e["y"] and p["y"] < e["y"]+e["height"]):
            lives -= 1
            if lives <= 0:
                game_over()
                return
            enemies.remove(e)

    # Balas enemigas vs jugador
    for b in bullets[:]:
        if b["enemy"] and (b["x"]+b["width"] > p["x"] and b["x"] < p["x"]+p["width"] and
                           b["y"]+b["height"] > p["y"] and b["y"] < p["y"]+p["height"]):
            lives -= 1
            bullets.remove(b)
            if lives <= 0:
                game_over()
                return


def game_over():
    global game_state
    game_state = "gameOver"


### MAIN LOOP ###
running = True
while running:
    clock.tick(60)
    anim_frame += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            keys[event.key] = True

            if game_state == "menu":
                if event.key in (pygame.K_UP, pygame.K_DOWN):
                    menu_selection = 1 - menu_selection
                if event.key == pygame.K_RETURN:
                    start_game()

            elif game_state == "playing":
                if event.key == pygame.K_SPACE and not player["shooting"]:
                    shoot()

            elif game_state == "gameOver" and event.key == pygame.K_RETURN:
                game_state = "menu"
                menu_selection = 0

        elif event.type == pygame.KEYUP:
            keys[event.key] = False
            if event.key == pygame.K_SPACE:
                player["shooting"] = False

    # UPDATE + DRAW
    if game_state == "menu":
        draw_menu()
    elif game_state == "playing":
        update()
        draw_background()
        draw_platforms()
        draw_player()
        draw_enemies()
        draw_bullets()
        draw_hud()
    else:
        screen.fill((0, 0, 0))
        screen.blit(font_big.render("GAME OVER", True, (255, 0, 0)),
                    (WIDTH//2 - 150, 160))
        screen.blit(font_med.render(f"SCORE: {score}", True, (255, 255, 255)),
                    (WIDTH//2 - 80, 220))

    pygame.display.flip()

pygame.quit()
sys.exit()

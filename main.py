import pygame
import random
import webbrowser

# Initialize Pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Car Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (150, 150, 150, 150)
DARK_GRAY = (30, 30, 30)
LEVEL_COLORS = [(50, 50, 50), (70, 70, 70), (90, 90, 90), (110, 110, 110), (130, 130, 130)]

# Car size
car_width, car_height = 30, 60

# Load images
car_img = pygame.image.load("car.png")
car_img = pygame.transform.scale(car_img, (car_width, car_height))

enemy_car_imgs = [
    pygame.transform.scale(pygame.image.load("car3.png"), (car_width, car_height)),
    pygame.transform.scale(pygame.image.load("car4.png"), (car_width, car_height))
]

# Original and alternate side background images
forest_img = pygame.transform.scale(pygame.image.load("carforest.jpg"), (WIDTH // 2 - 150, HEIGHT))
forest_img_alt = pygame.transform.scale(pygame.image.load("carforest2.jpg"), (WIDTH // 2 - 150, HEIGHT))

menu_bg = pygame.transform.scale(pygame.image.load("main_background.jpg"), (WIDTH, HEIGHT))
about_bg = pygame.transform.scale(pygame.image.load("about_background.jpg"), (WIDTH, HEIGHT))
score_bg = pygame.transform.scale(pygame.image.load("score_background.jpg"), (WIDTH, HEIGHT))

# Load sounds
engine_sound = pygame.mixer.Sound("engine.mp3")
crash_sound = pygame.mixer.Sound("crash.mp3")

# Clock
clock = pygame.time.Clock()
FPS = 60

# Fonts
font = pygame.font.SysFont(None, 32)
small_font = pygame.font.SysFont(None, 24)

# Button helper
def draw_button(text, x, y, width, height, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    button_rect = pygame.Rect(x, y, width, height)
    transparent_gray = pygame.Surface((width, height), pygame.SRCALPHA)
    transparent_gray.fill((150, 150, 150, 100))
    screen.blit(transparent_gray, (x, y))
    draw_text(text, 20, WHITE, x + width // 2, y + height // 2)
    if button_rect.collidepoint(mouse) and click[0] == 1 and action:
        pygame.time.delay(200)
        action()
    return button_rect

# Bullet class
class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 10
        self.width = 5
        self.height = 10

    def move(self):
        self.y -= self.speed

    def draw(self):
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

# Car class
class Car:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - car_height - 10
        self.speed = 5
        self.min_x = WIDTH // 2 - 150
        self.max_x = WIDTH // 2 + 150 - car_width

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > self.min_x:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < self.max_x:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < HEIGHT - car_height:
            self.y += self.speed

    def draw(self):
        screen.blit(car_img, (self.x, self.y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, car_width, car_height)

# Enemy class
class Enemy:
    def __init__(self):
        self.width = car_width
        self.height = car_height
        self.x = random.randint(WIDTH//2 - 150, WIDTH//2 + 150 - self.width)
        self.y = -self.height
        self.speed = 5
        self.image = random.choice(enemy_car_imgs)

    def move(self):
        self.y += self.speed

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

# Draw text
def draw_text(text, size, color, x, y, center=True):
    font_obj = pygame.font.SysFont(None, size)
    text_surface = font_obj.render(text, True, color)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    screen.blit(text_surface, text_rect)
    return text_rect

# Draw background with dynamic image switching
def draw_game_background(score):
    forest = forest_img if score < 10 else forest_img_alt
    screen.blit(forest, (0, 0))
    screen.blit(forest, (WIDTH // 2 + 150, 0))
    level = min(score // 20, 4)
    road_color = LEVEL_COLORS[level]
    pygame.draw.rect(screen, road_color, (WIDTH//2 - 150, 0, 300, HEIGHT))
    for i in range(0, HEIGHT, 40):
        pygame.draw.line(screen, WHITE, (WIDTH//2, i), (WIDTH//2, i+20), 5)

# Game loop
def game_loop():
    game_active = False
    game_over = False
    about_screen = False
    paused = False
    last_space_time = 0
    car = Car()
    enemies = []
    bullets = []
    score = 0
    high_score = 0

    def start_game():
        nonlocal game_active, about_screen, game_over, paused, car, enemies, bullets, score
        game_active = True
        about_screen = False
        game_over = False
        paused = False
        car = Car()
        enemies = []
        bullets = []
        score = 0
        engine_sound.play(-1)

    def restart_game():
        nonlocal game_active, game_over, paused, car, enemies, bullets, score
        game_active = True
        game_over = False
        paused = False
        car = Car()
        enemies = []
        bullets = []
        score = 0
        engine_sound.play(-1)

    def main_menu():
        nonlocal game_active, game_over, about_screen, paused
        game_active = False
        game_over = False
        about_screen = False
        paused = False
        engine_sound.stop()

    def show_about():
        nonlocal about_screen
        about_screen = True

    def back_to_menu():
        nonlocal about_screen
        about_screen = False
        engine_sound.stop()

    link_rect = pygame.Rect(0, 0, 0, 0)

    while True:
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                engine_sound.stop()
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if about_screen and link_rect.collidepoint(mouse_pos):
                    webbrowser.open("https://your-link-page.com")
            if event.type == pygame.KEYDOWN:
                if game_active and not paused:
                    if event.key == pygame.K_f:
                        bullet_x = car.x + car_width // 2 - 2
                        bullet_y = car.y
                        bullets.append(Bullet(bullet_x, bullet_y))
                if not game_active and not about_screen:
                    if event.key == pygame.K_RETURN:
                        start_game()
                    elif event.key == pygame.K_a:
                        show_about()
                if game_over:
                    if event.key == pygame.K_r:
                        restart_game()
                    elif event.key == pygame.K_ESCAPE:
                        engine_sound.stop()
                        pygame.quit()
                    elif event.key == pygame.K_RETURN:
                        main_menu()
                if about_screen and event.key == pygame.K_BACKSPACE:
                    back_to_menu()
                if event.key == pygame.K_SPACE:
                    current_time = pygame.time.get_ticks()
                    if current_time - last_space_time < 400:
                        paused = not paused
                    last_space_time = current_time

        if game_active and not paused:
            draw_game_background(score)
            car.move(keys)
            car.draw()

            if len(enemies) < 3 and random.randint(1, 20) == 1:
                enemies.append(Enemy())

            for enemy in enemies[:]:
                enemy.move()
                enemy.draw()
                if enemy.get_rect().colliderect(car.get_rect()):
                    engine_sound.stop()
                    crash_sound.play()
                    game_active = False
                    game_over = True
                    if score > high_score:
                        high_score = score
                elif enemy.y > HEIGHT:
                    enemies.remove(enemy)
                    score += 1

            for bullet in bullets[:]:
                bullet.move()
                bullet.draw()
                if bullet.y < 0:
                    bullets.remove(bullet)
                else:
                    for enemy in enemies[:]:
                        if bullet.get_rect().colliderect(enemy.get_rect()):
                            bullets.remove(bullet)
                            enemies.remove(enemy)
                            score += 5
                            break

            draw_text(f"Score: {score}", 24, BLACK, 10, 10, center=False)
            draw_text(f"High Score: {high_score}", 24, BLACK, 10, 40, center=False)
            draw_button("Back to Menu", WIDTH - 160, 10, 150, 30, lambda: main_menu())

        elif paused:
            draw_text("Game Paused", 36, RED, WIDTH // 2, HEIGHT // 2)

        elif game_over:
            screen.blit(score_bg, (0, 0))
            draw_text("GAME OVER", 48, RED, WIDTH // 2, HEIGHT // 2 - 100)
            draw_text(f"Final Score: {score}", 32, WHITE, WIDTH // 2, HEIGHT // 2 - 40)
            draw_text(f"High Score: {high_score}", 32, WHITE, WIDTH // 2, HEIGHT // 2 + 10)
            draw_button("Restart", WIDTH//2 - 210, HEIGHT//2 + 80, 140, 40, lambda: restart_game())
            draw_button("Main Menu", WIDTH//2 - 70, HEIGHT//2 + 80, 140, 40, lambda: main_menu())
            draw_button("Exit", WIDTH//2 + 70, HEIGHT//2 + 80, 140, 40, lambda: pygame.quit())

        elif about_screen:
            screen.blit(about_bg, (0, 0))
            draw_text("ABOUT THIS GAME", 40, WHITE, WIDTH // 2, 100)
            draw_text("Created using Python and Pygame", 24, WHITE, WIDTH // 2, 200)
            draw_text("Control your car with arrow keys", 24, WHITE, WIDTH // 2, 250)
            draw_text("Press 'F' to shoot bullets", 24, WHITE, WIDTH // 2, 300)
            draw_text("Avoid enemy cars to gain points", 24, WHITE, WIDTH // 2, 350)
            link_rect = draw_text("Click here to learn more", 20, RED, WIDTH // 2, 400)
            draw_button("Back", WIDTH//2 - 75, 460, 150, 40, lambda: back_to_menu())

        else:
            screen.blit(menu_bg, (0, 0))
            draw_text("PYTHON CAR GAME", 48, WHITE, WIDTH // 2, HEIGHT // 2 - 100)
            draw_button("Start Game", WIDTH//2 - 150, HEIGHT//2, 140, 40, lambda: start_game())
            draw_button("About", WIDTH//2 + 10, HEIGHT//2, 140, 40, lambda: show_about())

        pygame.display.update()
        clock.tick(FPS)

# Run the game
game_loop()

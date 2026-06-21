import pygame
import random
import sys

pygame.init()

WIDTH = 600
HEIGHT = 600
CELL = 30
COLS = WIDTH // CELL
ROWS = HEIGHT // CELL

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Змійка")
clock = pygame.time.Clock()

GREEN_BG = (60, 130, 60)
WHITE = (240, 240, 240)
DARK_GREEN = (30, 110, 60)
LIGHT_GREEN = (90, 200, 110)
SNAKE_COLOR = (10, 90, 35)
RED = (200, 50, 50)
GRAY = (70, 70, 80)
BLUE = (70, 130, 230)
YELLOW = (240, 200, 60)
PEAR_COLOR = (190, 210, 60)
SPARK_COLOR = (255, 230, 120)
EXPLOSION_COLOR = (255, 140, 30)

font_big = pygame.font.SysFont("arial", 60, bold=True)
font_med = pygame.font.SysFont("arial", 34, bold=True)
font_small = pygame.font.SysFont("arial", 22)

MENU = "menu"
SETTINGS = "settings"
PLAYING = "playing"
GAME_OVER = "game_over"

LEVELS = ["Рівень 1", "Рівень 2", "Рівень 3"]
LEVEL_SPEED = [6, 10, 14]
level = 0

PEAR_LIFETIME_MS = 12000  # груша зникає і з'являється нова кожні 12 секунд


class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text

    def draw(self):
        hover = self.rect.collidepoint(pygame.mouse.get_pos())
        color = BLUE if hover else GRAY
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        label = font_med.render(self.text, True, WHITE)
        screen.blit(label, label.get_rect(center=self.rect.center))

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)


def draw_text(text, font, color, y):
    label = font.render(text, True, color)
    screen.blit(label, label.get_rect(center=(WIDTH // 2, y)))


def draw_background():
    screen.fill(GREEN_BG)
    for row in range(ROWS):
        for col in range(COLS):
            if (row + col) % 2 == 0:
                pygame.draw.rect(screen, DARK_GREEN, (col * CELL, row * CELL, CELL, CELL))


def random_empty_cell(occupied):
    while True:
        pos = (random.randint(0, COLS - 1), random.randint(0, ROWS - 1))
        if pos not in occupied:
            return pos


def spawn_food(snake, other_food_positions):
    occupied = set(snake) | set(other_food_positions)
    pos = random_empty_cell(occupied)
    # бомба замаскована під грушу - 1 шанс з 4, що "груша" виявиться бомбою
    food_type = "bomb" if random.random() < 0.25 else "pear"
    return {"pos": pos, "type": food_type}


def draw_apple(pos):
    x, y = pos
    pygame.draw.rect(screen, RED, (x * CELL + 3, y * CELL + 3, CELL - 6, CELL - 6), border_radius=8)


def draw_pear(pos, is_bomb):
    x, y = pos
    cx = x * CELL + CELL // 2
    cy = y * CELL + CELL // 2

    # груша - дві кульки різного розміру одна над одною
    pygame.draw.circle(screen, PEAR_COLOR, (cx, cy + 4), CELL // 3)
    pygame.draw.circle(screen, PEAR_COLOR, (cx, cy - 4), CELL // 4)
    pygame.draw.line(screen, DARK_GREEN, (cx, cy - CELL // 3), (cx + 2, cy - CELL // 2), 2)

    if is_bomb:
        # ледь помітна іскра - маленька і прозора, легко не помітити
        spark_x = cx + CELL // 6
        spark_y = cy - CELL // 6
        spark = pygame.Surface((6, 6), pygame.SRCALPHA)
        pygame.draw.circle(spark, (*SPARK_COLOR, 90), (3, 3), 2)
        screen.blit(spark, (spark_x, spark_y))


def menu():
    btn_play = Button(WIDTH // 2 - 100, 250, 200, 60, "Грати")
    btn_settings = Button(WIDTH // 2 - 100, 330, 200, 60, "Налаштування")
    btn_quit = Button(WIDTH // 2 - 100, 410, 200, 60, "Вихід")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if btn_play.is_clicked(event):
                return PLAYING
            if btn_settings.is_clicked(event):
                return SETTINGS
            if btn_quit.is_clicked(event):
                pygame.quit()
                sys.exit()

        screen.fill((20, 20, 30))
        draw_text("ЗМІЙКА", font_big, LIGHT_GREEN, 140)
        btn_play.draw()
        btn_settings.draw()
        btn_quit.draw()
        draw_text(LEVELS[level], font_small, YELLOW, 500)

        pygame.display.flip()
        clock.tick(60)


def settings():
    global level
    btn_back = Button(WIDTH // 2 - 100, 450, 200, 60, "Назад")
    btn_left = Button(WIDTH // 2 - 160, 250, 60, 60, "<")
    btn_right = Button(WIDTH // 2 + 100, 250, 60, 60, ">")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if btn_back.is_clicked(event):
                return MENU
            if btn_left.is_clicked(event):
                level = (level - 1) % len(LEVELS)
            if btn_right.is_clicked(event):
                level = (level + 1) % len(LEVELS)

        screen.fill((20, 20, 30))
        draw_text("НАЛАШТУВАННЯ", font_big, BLUE, 130)

        draw_text("Рівень складності", font_small, WHITE, 200)
        btn_left.draw()
        btn_right.draw()
        draw_text(LEVELS[level], font_med, YELLOW, 280)

        btn_back.draw()

        pygame.display.flip()
        clock.tick(60)


def explosion_animation(pos):
    x, y = pos
    cx = x * CELL + CELL // 2
    cy = y * CELL + CELL // 2

    for radius in range(5, 90, 8):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.draw.circle(screen, EXPLOSION_COLOR, (cx, cy), radius)
        pygame.draw.circle(screen, YELLOW, (cx, cy), max(0, radius - 15))
        pygame.display.flip()
        clock.tick(30)


def pause_menu():
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((10, 10, 15))

    btn_resume = Button(WIDTH // 2 - 100, 230, 200, 60, "Продовжити")
    btn_settings = Button(WIDTH // 2 - 100, 310, 200, 60, "Налаштування")
    btn_menu = Button(WIDTH // 2 - 100, 390, 200, 60, "Головне меню")

    paused_frame = screen.copy()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return PLAYING
            if btn_resume.is_clicked(event):
                return PLAYING
            if btn_settings.is_clicked(event):
                return SETTINGS
            if btn_menu.is_clicked(event):
                return MENU

        screen.blit(paused_frame, (0, 0))
        screen.blit(overlay, (0, 0))
        draw_text("ПАУЗА", font_big, WHITE, 150)
        btn_resume.draw()
        btn_settings.draw()
        btn_menu.draw()

        pygame.display.flip()
        clock.tick(60)


def game():
    snake = [(COLS // 2, ROWS // 2)]
    direction = (1, 0)

    apple_pos = random_empty_cell(set(snake))
    pear_food = spawn_food(snake, [apple_pos])
    pear_spawn_time = pygame.time.get_ticks()

    score = 0
    speed = LEVEL_SPEED[level]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w) and direction != (0, 1):
                    direction = (0, -1)
                elif event.key in (pygame.K_DOWN, pygame.K_s) and direction != (0, -1):
                    direction = (0, 1)
                elif event.key in (pygame.K_LEFT, pygame.K_a) and direction != (1, 0):
                    direction = (-1, 0)
                elif event.key in (pygame.K_RIGHT, pygame.K_d) and direction != (-1, 0):
                    direction = (1, 0)
                elif event.key == pygame.K_ESCAPE:
                    action = pause_menu()
                    while action == SETTINGS:
                        settings()
                        action = pause_menu()
                    if action == MENU:
                        return MENU, score

        # якщо груша "прострочилась" - вона зникає і з'являється нова
        now = pygame.time.get_ticks()
        if now - pear_spawn_time >= PEAR_LIFETIME_MS:
            pear_food = spawn_food(snake, [apple_pos])
            pear_spawn_time = now

        head_x, head_y = snake[0]
        new_head = (head_x + direction[0], head_y + direction[1])
        snake.insert(0, new_head)

        ate_something = False

        if new_head == apple_pos:
            score += 1
            apple_pos = random_empty_cell(set(snake) | {pear_food["pos"]})
            ate_something = True

        elif new_head == pear_food["pos"]:
            if pear_food["type"] == "bomb":
                explosion_animation(pear_food["pos"])
                return GAME_OVER, score
            score += 2
            pear_food = spawn_food(snake, [apple_pos])
            pear_spawn_time = pygame.time.get_ticks()
            ate_something = True

        if not ate_something:
            snake.pop()

        if (new_head[0] < 0 or new_head[0] >= COLS or
                new_head[1] < 0 or new_head[1] >= ROWS or
                new_head in snake[1:]):
            return GAME_OVER, score

        draw_background()
        draw_apple(apple_pos)
        draw_pear(pear_food["pos"], is_bomb=(pear_food["type"] == "bomb"))

        for x, y in snake:
            rect = (x * CELL + 2, y * CELL + 2, CELL - 4, CELL - 4)
            pygame.draw.rect(screen, SNAKE_COLOR, rect, border_radius=6)
            pygame.draw.rect(screen, WHITE, rect, 1, border_radius=6)

        score_label = font_small.render(f"Очки: {score}", True, WHITE)
        screen.blit(score_label, (10, 10))

        pygame.display.flip()
        clock.tick(speed)


def game_over(score):
    btn_again = Button(WIDTH // 2 - 100, 320, 200, 60, "Грати знову")
    btn_menu = Button(WIDTH // 2 - 100, 400, 200, 60, "Меню")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if btn_again.is_clicked(event):
                return PLAYING
            if btn_menu.is_clicked(event):
                return MENU

        screen.fill((20, 20, 30))
        draw_text("ГРА ОКІНЧЕНА", font_big, RED, 180)
        draw_text(f"Очки: {score}", font_med, YELLOW, 250)
        btn_again.draw()
        btn_menu.draw()

        pygame.display.flip()
        clock.tick(60)


def main():
    state = MENU
    score = 0
    while True:
        if state == MENU:
            state = menu()
        elif state == SETTINGS:
            state = settings()
        elif state == PLAYING:
            state, score = game()
        elif state == GAME_OVER:
            state = game_over(score)


main()
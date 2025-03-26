import random
import sys

import pygame
from pygame.locals import *

pygame.init()
pygame.mixer.init()

# ------------ CONFIGURATIONS -----------------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
# Load the button image (do this somewhere after pygame.init())
button_img = pygame.image.load("images/button.png")
# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
DARK_GRAY = (100, 100, 100)
ORANGE = (255, 165, 0)

# Fonts
FONT_LARGE = pygame.font.SysFont("Arial", 50)
FONT_MED = pygame.font.SysFont("Arial", 36)
FONT_SMALL = pygame.font.SysFont("Arial", 24)

background_img = pygame.image.load("images/menu_background.png")
background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Load sounds (optional)
try:
    CLICK_SOUND = pygame.mixer.Sound("sounds/click.wav")
    CLICK_SOUND.set_volume(0.5)
    background_img.convert_alpha()

except:
    CLICK_SOUND = None

try:
    MENU_MUSIC = "sounds/menu_music.wav"
    GAME_MUSIC = "sounds/game_music.wav"
    GAME_OVER_MUSIC = "sounds/game_over_music.wav"
except:
    MENU_MUSIC = None
    GAME_MUSIC = None
    GAME_OVER_MUSIC = None

# Game States
STATE_MAIN_MENU = 0
STATE_PROBLEM_TYPE = 1
STATE_GAME = 2
STATE_GAME_OVER = 3

# Problem Types
PROB_ADDITION = 0
PROB_SUBTRACTION = 1
PROB_MULTIPLICATION = 2
PROB_DIVISION = 3


def draw_text(surface, text, font, color, x, y, center=False):
    render = font.render(text, True, color)
    rect = render.get_rect(topleft=(x, y))
    if center:
        rect.center = (x, y)
    surface.blit(render, rect)
    return rect


def play_sound(sound):
    if sound:
        sound.play()


def play_music(music_file):
    if music_file:
        pygame.mixer.music.load(music_file)
        pygame.mixer.music.play(-1)


def stop_music():
    pygame.mixer.music.stop()


def draw_3d_button(surface, text, font, x, y, w, h, pressed=False):
    base_top_color = (200, 220, 255)
    base_bottom_color = (150, 170, 220)
    border_color = (40, 40, 80)
    highlight_color = (255, 255, 255)

    if pressed:
        base_top_color = (170, 190, 235)
        base_bottom_color = (120, 140, 190)

    offset = 2 if pressed else 0
    shadow_offset = 4

    # Shadow
    pygame.draw.rect(surface, (50, 50, 50), (x + offset + shadow_offset, y + offset + shadow_offset, w, h),
                     border_radius=10)

    def interpolate_color(c1, c2, t):
        return (
            int(c1[0] + (c2[0] - c1[0]) * t),
            int(c1[1] + (c2[1] - c1[1]) * t),
            int(c1[2] + (c2[2] - c1[2]) * t)
        )

    top_half_height = h // 2
    for i in range(top_half_height):
        t = i / float(top_half_height - 1)
        row_color = interpolate_color(base_top_color, base_bottom_color, t * 0.5)
        pygame.draw.line(surface, row_color, (x + offset, y + offset + i), (x + offset + w, y + offset + i))

    for i in range(top_half_height, h):
        t = (i - top_half_height) / float(h - top_half_height - 1)
        row_color = interpolate_color(base_bottom_color, (100, 100, 150), t * 0.5)
        pygame.draw.line(surface, row_color, (x + offset, y + offset + i), (x + offset + w, y + offset + i))

    pygame.draw.line(surface, highlight_color, (x + offset, y + offset), (x + offset + w, y + offset), 2)
    pygame.draw.rect(surface, border_color, (x + offset, y + offset, w, h), 2, border_radius=10)

    draw_text(surface, text, font, BLACK, x + offset + w // 2, y + offset + h // 2, center=True)


def generate_problem(problem_type, level):
    max_num = 20 + (level * 10)
    a = random.randint(1, max_num)
    b = random.randint(1, max_num)

    if problem_type == PROB_ADDITION:
        question = f"{a} + {b} ="
        correct_answer = a + b
    elif problem_type == PROB_SUBTRACTION:
        if b > a:
            a, b = b, a
        question = f"{a} - {b} ="
        correct_answer = a - b
    elif problem_type == PROB_MULTIPLICATION:
        question = f"{a} × {b} ="
        correct_answer = a * b
    else:  # PROB_DIVISION
        b = random.randint(1, max_num // 2 if max_num // 2 > 0 else 1)
        a = b * random.randint(1, max_num // b if b != 0 else 1)
        question = f"{a} ÷ {b} ="
        correct_answer = a // b

    correct_str = str(correct_answer)
    options = [correct_str]
    while len(options) < 4:
        wrong = correct_answer + random.randint(-max_num, max_num)
        if wrong < 0:
            wrong = abs(wrong)
        if str(wrong) not in options:
            options.append(str(wrong))
    random.shuffle(options)

    return question, correct_str, options


# ---------------- New Button Class -------------------
# Load the button image (do this somewhere after pygame.init())
button_img = pygame.image.load("images/button.png")
answer_button_img = pygame.image.load("images/answer_button.png")


class Button:
    def __init__(self, x, y, w, h, text, callback):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.text = text
        self.callback = callback
        self.pressed = False

    def is_hovered(self):
        mx, my = pygame.mouse.get_pos()
        return (self.x <= mx <= self.x + self.w) and (self.y <= my <= self.y + self.h)

    def draw(self, surface):
        # Scale the button image to desired size (if needed)
        scaled_button = pygame.transform.smoothscale(button_img.convert_alpha(), (self.w, self.h))

        # If pressed, optionally draw it slightly darker or offset
        if self.pressed:
            # Create a slightly dark overlay
            overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 50))  # 50 is alpha value, increase for darker
            # Blit button
            surface.blit(scaled_button, (self.x, self.y))
            # Blit overlay
            surface.blit(overlay, (self.x, self.y))
        else:
            # Just draw the normal button
            surface.blit(scaled_button, (self.x, self.y))

        # Draw the text centered
        text_surf = FONT_MED.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=(self.x + self.w // 2, self.y + self.h // 2))
        # If pressed, maybe move the text down a pixel or two
        if self.pressed:
            text_rect.y += 2
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered():
                play_sound(CLICK_SOUND)
                self.pressed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.pressed and self.is_hovered():
                self.callback()
            self.pressed = False


class MathGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Главное меню")
        self.clock = pygame.time.Clock()

        self.state = STATE_MAIN_MENU
        self.problem_type = PROB_ADDITION

        # Game variables
        self.level = 1
        self.score = 0
        self.health = 3
        self.correct_count = 0
        self.time_limit = 15
        self.remaining_time = self.time_limit

        self.current_question = ""
        self.current_answer = None
        self.current_options = []

        self.start_time = 0

        # Feedback after answer
        self.last_chosen_box = None
        self.last_answer_correct = None
        self.answer_feedback_time = 0

        play_music(MENU_MUSIC)

        # Setup buttons for main menu
        self.start_button = Button(300, 200, 200, 60, "Старт", self.start_game)
        self.options_button = Button(300, 300, 200, 60, "Опции", self.show_options)
        self.quit_button = Button(300, 400, 200, 60, "Выход", self.quit_game)

    def start_game(self):
        self.reset_game()
        self.state = STATE_GAME
        stop_music()
        play_music(GAME_MUSIC)

    def show_options(self):
        self.state = STATE_PROBLEM_TYPE
        stop_music()
        play_music(MENU_MUSIC)

    def quit_game(self):
        pygame.quit()
        sys.exit()

    def reset_game(self):
        self.level = 1
        self.score = 0
        self.health = 3
        self.correct_count = 0
        self.time_limit = 15
        self.generate_new_problem()

    def generate_new_problem(self):
        self.current_question, self.current_answer, self.current_options = generate_problem(self.problem_type,
                                                                                            self.level)
        self.remaining_time = self.time_limit
        self.start_time = pygame.time.get_ticks()
        self.last_chosen_box = None
        self.last_answer_correct = None
        self.answer_feedback_time = 0

    def update_timer(self):
        elapsed = (pygame.time.get_ticks() - self.start_time) / 1000.0
        self.remaining_time = int(self.time_limit - elapsed)
        if self.remaining_time < 0:
            self.handle_wrong_answer()

    def handle_correct_answer(self):
        self.score += 10
        self.correct_count += 1
        if self.correct_count % 2 == 0:
            self.level += 1
            self.time_limit = max(5, self.time_limit - 1)
        self.delay_new_problem()

    def handle_wrong_answer(self):
        self.health -= 1
        if self.health <= 0:
            self.state = STATE_GAME_OVER
            stop_music()
            play_music(GAME_OVER_MUSIC)
        else:
            self.delay_new_problem()

    def delay_new_problem(self):
        self.answer_feedback_time = pygame.time.get_ticks()

    def check_feedback_timeout(self):
        if self.answer_feedback_time > 0:
            if pygame.time.get_ticks() - self.answer_feedback_time > 500:
                self.generate_new_problem()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)

    def handle_events(self):
        events = pygame.event.get()
        mx, my = pygame.mouse.get_pos()

        for event in events:
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if self.state == STATE_MAIN_MENU:
                # Handle button events
                self.start_button.handle_event(event)
                self.options_button.handle_event(event)
                self.quit_button.handle_event(event)

            elif self.state == STATE_PROBLEM_TYPE:
                # Problem type selection
                if event.type == MOUSEBUTTONDOWN:
                    ops_positions = [(100, 300), (250, 300), (400, 300), (550, 300)]
                    for i, pos in enumerate(ops_positions):
                        x, y = pos
                        if x <= mx <= x + 100 and y <= my <= y + 100:
                            play_sound(CLICK_SOUND)
                            self.problem_type = i
                            self.state = STATE_MAIN_MENU
                            stop_music()
                            play_music(MENU_MUSIC)

            elif self.state == STATE_GAME:
                if self.answer_feedback_time == 0:
                    if event.type == MOUSEBUTTONDOWN:
                        box_positions = [(200, 300), (320, 300), (440, 300), (560, 300)]
                        for i, pos in enumerate(box_positions):
                            x, y = pos
                            if x <= mx <= x + 80 and y <= my <= y + 80:
                                play_sound(CLICK_SOUND)
                                chosen_answer = self.current_options[i]
                                self.last_chosen_box = i
                                self.last_answer_correct = (chosen_answer == self.current_answer)
                                if self.last_answer_correct:
                                    self.handle_correct_answer()
                                else:
                                    self.handle_wrong_answer()

            elif self.state == STATE_GAME_OVER:
                if event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        self.state = STATE_MAIN_MENU
                        stop_music()
                        play_music(MENU_MUSIC)

        # Handle hovering in Problem Type Selection
        if self.state == STATE_PROBLEM_TYPE:
            self.hovered_op = None
            ops_positions = [(100, 300), (250, 300), (400, 300), (550, 300)]
            for i, pos in enumerate(ops_positions):
                x, y = pos
                if x <= mx <= x + 100 and y <= my <= y + 100:
                    self.hovered_op = i
                    break

    def update(self):
        if self.state == STATE_GAME:
            if self.answer_feedback_time == 0:
                self.update_timer()
            else:
                self.check_feedback_timeout()

    def render(self):
        self.screen.blit(background_img, (0, 0))

        if self.state == STATE_MAIN_MENU:
            draw_text(self.screen, "Math Master", FONT_LARGE, BLACK, SCREEN_WIDTH // 2, 100, center=True)
            self.start_button.draw(self.screen)
            self.options_button.draw(self.screen)
            self.quit_button.draw(self.screen)

        elif self.state == STATE_PROBLEM_TYPE:
            draw_text(self.screen, "Выберите арифметический знак", FONT_LARGE, BLACK, SCREEN_WIDTH // 2, 100,
                      center=True)
            ops_positions = [(100, 250), (250, 250), (400, 250), (550, 250)]

            ops_symbols = ["+", "-", "×", "÷"]
            for i, pos in enumerate(ops_positions):
                x, y = pos
                color = GREEN if self.hovered_op == i else ORANGE
                pygame.draw.rect(self.screen, color, (x, y, 100, 100))
                draw_text(self.screen, ops_symbols[i], FONT_LARGE, BLACK, x + 50, y + 50, center=True)

        elif self.state == STATE_GAME:
            draw_text(self.screen, f"Уровень: {self.level}", FONT_SMALL, BLACK, 50, 50)
            draw_text(self.screen, f"Балл: {self.score}", FONT_SMALL, BLACK, 50, 80)
            draw_text(self.screen, f"Здоровье: {self.health}", FONT_SMALL, RED, 50, 110)
            draw_text(self.screen, self.current_question, FONT_LARGE, BLACK, SCREEN_WIDTH // 2, 200, center=True)

            time_bar_x = 600
            time_bar_y = 50
            time_bar_width = 150
            time_bar_height = 20
            fraction = max(0, self.remaining_time / self.time_limit)
            pygame.draw.rect(self.screen, BLACK, (time_bar_x, time_bar_y, time_bar_width, time_bar_height), 2)
            pygame.draw.rect(self.screen, GREEN, (time_bar_x, time_bar_y, time_bar_width * fraction, time_bar_height))
            draw_text(self.screen, str(self.remaining_time), FONT_SMALL, BLACK, time_bar_x + time_bar_width + 30,
                      time_bar_y, center=True)

            box_positions = [(200, 300), (320, 300), (440, 300), (560, 300)]
            for i, pos in enumerate(box_positions):
                x, y = pos
                box_color = ORANGE
                if self.last_chosen_box is not None and i == self.last_chosen_box:
                    box_color = GREEN if self.last_answer_correct else RED
                pygame.draw.rect(self.screen, box_color, (x, y, 80, 80))
                draw_text(self.screen, str(self.current_options[i]), FONT_MED, BLACK, x + 40, y + 40, center=True)

        elif self.state == STATE_GAME_OVER:
            draw_text(self.screen, "Игра окончена", FONT_LARGE, RED, SCREEN_WIDTH // 2, 200, center=True)
            draw_text(self.screen, f"Ваш балл: {self.score}", FONT_MED, BLACK, SCREEN_WIDTH // 2, 300, center=True)
            draw_text(self.screen, "Нажмите ПРОБЕЛ для выхода", FONT_SMALL, BLACK, SCREEN_WIDTH // 2, 400, center=True)

        pygame.display.flip()


if __name__ == "__main__":
    game = MathGame()
    game.run()

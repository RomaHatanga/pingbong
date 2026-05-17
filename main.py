# ============================================================================
# 🎮 ПИН-ПОНГ — ПОЛНАЯ ВЕРСИЯ С ГРАФИКОЙ И ЗВУКОМ
# ============================================================================
# [1]  ИМПОРТЫ
import pygame
import sys
import os

# [2]  ИНИЦИАЛИЗАЦИЯ
pygame.init()
pygame.mixer.init()  # [2a] 🔊 Инициализация микшера для звука

# [3]  НАСТРОЙКИ ОКНА
WIDTH, HEIGHT = 800, 600

# [4]  ЦВЕТА (запасной вариант, если нет изображений)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BACKGROUND_COLOR = (50, 50, 100)  # [4a] 🖼️ Цвет фона по умолчанию

# [5]  РАЗМЕРЫ ОБЪЕКТОВ — 🔧 ширина ракетки 30 пикселей
PADDLE_WIDTH = 30       # 🔄 Увеличена ширина: 20 → 30 пикселей (×1.5)
PADDLE_HEIGHT = 100
BALL_SIZE = 30

# [6]  СОЗДАНИЕ ОКНА
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Пин-понг на Algo VSCode")

# [7]  ШРИФТ
font = pygame.font.SysFont(None, 36)
pause_font = pygame.font.SysFont(None, 48)  # [7a] Шрифт для меню паузы

# ============================================================================
# [8]  🔹 ФУНКЦИЯ ЗАГРУЗКИ ИЗОБРАЖЕНИЙ 🔹
# ============================================================================
def load_image(name, size=None):
    """[8a] Загружает PNG-изображение и масштабирует при необходимости"""
    try:
        img = pygame.image.load(name).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except pygame.error as e:
        print(f"⚠️ Не удалось загрузить {name}: {e}")
        return pygame.Surface((size if size else (1, 1)), pygame.SRCALPHA)

# ============================================================================
# [9]  🔹 ФУНКЦИЯ ЗАГРУЗКИ ЗВУКОВ 🔹
# ============================================================================
def load_sound(name, volume=0.5):
    """[9a] Загружает звуковой файл (.ogg/.wav/.mp3) и настраивает громкость"""
    try:
        sound = pygame.mixer.Sound(name)
        sound.set_volume(volume)
        return sound
    except pygame.error as e:
        print(f"⚠️ Не удалось загрузить звук {name}: {e}")
        return None

# ============================================================================
# [10] 🔹 ЗАГРУЗКА ГРАФИЧЕСКИХ АССЕТОВ 🔹
# ============================================================================
fon_img = load_image("fon.png", (WIDTH, HEIGHT))
raketka_img = load_image("raketka.png", (PADDLE_WIDTH, PADDLE_HEIGHT))
raketka_img_flipped = pygame.transform.flip(raketka_img, True, False) if raketka_img.get_width() > 1 else raketka_img
ball_img = load_image("ball.png", (BALL_SIZE, BALL_SIZE))
use_images = fon_img.get_width() > 1 and raketka_img.get_width() > 1 and ball_img.get_width() > 1

# ============================================================================
# [11] 🔹 ЗАГРУЗКА АУДИО 🔹
# ============================================================================
try:
    pygame.mixer.music.load("haggstrom.mp3")
    pygame.mixer.music.set_volume(0.4)
    pygame.mixer.music.play(-1)
    print("✅ Фоновая музыка: haggstrom.mp3")
except pygame.error as e:
    print(f"⚠️ Ошибка загрузки музыки: {e}")

hit_sound = load_sound("hit.ogg", volume=0.6)
if hit_sound:
    print("✅ Звук удара: hit.ogg")

death_sound = load_sound("death.ogg", volume=0.7)
if death_sound:
    print("✅ Звук гола: death.ogg")

# ============================================================================
# [12] ИГРОВЫЕ ПЕРЕМЕННЫЕ
# ============================================================================
p1_y = p2_y = HEIGHT // 2 - PADDLE_HEIGHT // 2
ball_x, ball_y = WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2
ball_dx, ball_dy = 5, 5

score_p1 = 0
score_p2 = 0
WIN_SCORE = 10
winner = None

clock = pygame.time.Clock()
sound_enabled = True
game_paused = False

# ============================================================================
# [13] 🔹 ОСНОВНОЙ ИГРОВОЙ ЦИКЛ 🔹
# ============================================================================
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.mixer.music.stop()
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game_paused = not game_paused
                print(f"⏸️ Пауза: {'ВКЛ' if game_paused else 'ВЫКЛ'}")
            
            if event.key == pygame.K_m:
                sound_enabled = not sound_enabled
                print(f"🔊 Звук: {'ВКЛ' if sound_enabled else 'ВЫКЛ'}")
            elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                new_vol = min(1.0, pygame.mixer.music.get_volume() + 0.1)
                pygame.mixer.music.set_volume(new_vol)
            elif event.key == pygame.K_MINUS:
                new_vol = max(0.0, pygame.mixer.music.get_volume() - 0.1)
                pygame.mixer.music.set_volume(new_vol)

    if game_paused:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        pause_text = pause_font.render("⏸️ ПАУЗА", True, WHITE)
        resume_text = font.render("Нажмите ESC для продолжения", True, (200, 200, 255))
        controls_text = font.render("W/S — левый | ↑/↓ — правый | M — звук | +/- — громкость", True, (180, 180, 220))
        
        screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 - 40))
        screen.blit(resume_text, (WIDTH//2 - resume_text.get_width()//2, HEIGHT//2 + 10))
        screen.blit(controls_text, (WIDTH//2 - controls_text.get_width()//2, HEIGHT//2 + 50))
        
        pygame.display.flip()
        clock.tick(30)
        continue

    # ▶️ [14] УПРАВЛЕНИЕ РАКЕТКАМИ
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] and p1_y > 0: p1_y -= 5
    if keys[pygame.K_s] and p1_y < HEIGHT - PADDLE_HEIGHT: p1_y += 5
    if keys[pygame.K_UP] and p2_y > 0: p2_y -= 5
    if keys[pygame.K_DOWN] and p2_y < HEIGHT - PADDLE_HEIGHT: p2_y += 5

    # [15] ФИЗИКА МЯЧА
    ball_x += ball_dx
    ball_y += ball_dy

    # [15a] Отскок от верхней/нижней границы 🔇 ЗВУК УБРАН
    if ball_y <= 0 or ball_y >= HEIGHT - BALL_SIZE:
        ball_dy *= -1
        # hit.ogg здесь больше не воспроизводится

    # [16] 🎵 ОТСКАК ОТ РАКЕТОК + ЗВУК hit.ogg ✅ ТОЛЬКО ЗДЕСЬ
    if (ball_x <= PADDLE_WIDTH and p1_y < ball_y + BALL_SIZE and ball_y < p1_y + PADDLE_HEIGHT):
        ball_dx *= -1
        if sound_enabled and hit_sound:
            hit_sound.play()
    
    if (ball_x >= WIDTH - PADDLE_WIDTH - BALL_SIZE and p2_y < ball_y + BALL_SIZE and ball_y < p2_y + PADDLE_HEIGHT):
        ball_dx *= -1
        if sound_enabled and hit_sound:
            hit_sound.play()

    # [17] 💀 ГОЛ / СБРОС МЯЧА + ЗВУК death.ogg
    if ball_x < 0:
        score_p2 += 1
        if sound_enabled and death_sound:
            death_sound.play()
        ball_x, ball_y = WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2
        ball_dx = 5
    elif ball_x > WIDTH - BALL_SIZE:
        score_p1 += 1
        if sound_enabled and death_sound:
            death_sound.play()
        ball_x, ball_y = WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2
        ball_dx = -5

    # [18] ПРОВЕРКА ПОБЕДЫ
    if score_p1 >= WIN_SCORE:
        winner = "Первый игрок wins!"
    elif score_p2 >= WIN_SCORE:
        winner = "Второй игрок wins!"

    # ========================================================================
    # [19] 🔹 ОТРИСОВКА КАДРА 🔹
    # ========================================================================
    if use_images and fon_img.get_width() == WIDTH:
        screen.blit(fon_img, (0, 0))
    else:
        screen.fill(BACKGROUND_COLOR)

    if winner:
        win_text = font.render(winner, True, WHITE)
        screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2))
        if hit_sound:
            hit_sound.play()
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()
                pygame.quit()
                sys.exit()
        continue

    if use_images:
        screen.blit(raketka_img, (0, p1_y))
        screen.blit(raketka_img_flipped, (WIDTH - PADDLE_WIDTH, p2_y))
    else:
        pygame.draw.rect(screen, WHITE, (0, p1_y, PADDLE_WIDTH, PADDLE_HEIGHT))
        pygame.draw.rect(screen, WHITE, (WIDTH - PADDLE_WIDTH, p2_y, PADDLE_WIDTH, PADDLE_HEIGHT))
    
    if use_images:
        screen.blit(ball_img, (ball_x, ball_y))
    else:
        pygame.draw.ellipse(screen, WHITE, (ball_x, ball_y, BALL_SIZE, BALL_SIZE))
    
    score_text = font.render(f"П1: {score_p1}  П2: {score_p2}", True, WHITE)
    screen.blit(score_text, (20, 20))
    
    hint_text = font.render(f"Звук: {'ON' if sound_enabled else 'OFF'} [M] | Пауза: [ESC]", True, (200, 200, 255))
    screen.blit(hint_text, (WIDTH - 320, 20))

    pygame.display.flip()
    clock.tick(60)
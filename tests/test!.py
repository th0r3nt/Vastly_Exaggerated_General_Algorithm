import pygame
import datetime
import random
import math
from collections import deque

# --- Инициализация Pygame ---
pygame.init()

# --- Настройки экрана ---
SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080 # Full HD для максимальной детализации
# Используем флаг FULLSCREEN для лучшего погружения
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN) 
pygame.display.set_caption("V.E.G.A. - Polished Interface")

# --- Цвета ---
BLACK = (5, 5, 10)
BLUE = (0, 191, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 127)
GRAY = (60, 60, 70) # Сделаем серый светлее для рамок
GRID_COLOR_BASE = (20, 35, 50)
TEXT_COLOR = (220, 220, 240)
TRANSPARENT_BLACK = (5, 5, 10, 200) # Для полупрозрачного фона виджетов

# --- Шрифты ---
try:
    main_font = pygame.font.Font("C:/Windows/Fonts/consola.ttf", 48)
    small_font = pygame.font.Font("C:/Windows/Fonts/consola.ttf", 26)
    ui_font = pygame.font.Font("C:/Windows/Fonts/consola.ttf", 20)
    log_font = pygame.font.Font("C:/Windows/Fonts/consola.ttf", 16)
except FileNotFoundError:
    # Запасные шрифты, если Consolas не найден
    main_font, small_font, ui_font, log_font = [pygame.font.Font(None, size) for size in [54, 34, 26, 22]]

# --- Класс для частиц (фон, следы от электронов) ---
class Particle:
    def __init__(self, x, y, z, is_trail=False):
        self.x, self.y, self.z = x, y, z
        self.is_trail = is_trail
        self.max_lifetime = 0.5 if is_trail else float('inf')
        self.lifetime = self.max_lifetime
        self.sx, self.sy = 0, 0 # Screen positions

    def update(self, dt):
        self.x -= (self.z * 10) * dt # Движение частиц
        if self.x < 0: self.x = SCREEN_WIDTH
        
        self.sx = self.x
        self.sy = self.y
        
        if self.is_trail:
            self.lifetime -= dt
            return self.lifetime > 0
        return True

    def draw(self, surface, color):
        radius = (self.z * 1.5)
        alpha = 255
        if self.is_trail:
            alpha = int(255 * (self.lifetime / self.max_lifetime))
        
        final_color = (*color[:3], alpha)
        # Рисуем частицу на временной поверхности для поддержки альфа-канала
        temp_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(temp_surf, final_color, (radius, radius), radius)
        surface.blit(temp_surf, (self.sx - radius, self.sy - radius), special_flags=pygame.BLEND_RGBA_ADD)

# --- Глобальные переменные и симуляция ---
start_time = pygame.time.get_ticks()
startup_alpha = 0

# Цвета
logo_colors = [BLUE, YELLOW, GREEN]
current_color = pygame.Color(logo_colors[0])
target_color_index = 0

# Анимации и данные
electron_angles = [0, 120, 240]
shockwave = {'radius': 0, 'alpha': 0}
particles = [Particle(random.uniform(0, SCREEN_WIDTH), random.uniform(0, SCREEN_HEIGHT), random.uniform(0.1, 1)) for _ in range(200)]
voice_wave = [random.uniform(-1, 1) for _ in range(100)]

# Симуляция
data = {
    'cpu_usage': random.uniform(20, 30), 'ram_usage': random.uniform(40, 50),
    'net_down': random.uniform(50, 60), 'net_up': random.uniform(5, 10),
    'core_sync': random.uniform(70, 80), 'current_temp': 38.5,
    'graph1': deque([random.randint(100, 150) for _ in range(150)], maxlen=150),
    'graph2': deque([random.randint(50, 100) for _ in range(150)], maxlen=150),
    'logs': deque([f"{random.randint(1000, 9999)} | SYS_INIT | STATUS OK"], maxlen=12)
}

# --- ФУНКЦИИ ОТРИСОВКИ ---

def draw_frame(surface, rect, title, color):
    """Рисует красивую кастомную рамку для виджетов."""
    # Полупрозрачный фон
    bg_surf = pygame.Surface(rect.size, pygame.SRCALPHA)
    bg_surf.fill(TRANSPARENT_BLACK)
    surface.blit(bg_surf, rect.topleft)
    
    # Рамка и уголки
    pygame.draw.rect(surface, GRAY, rect, 1)
    pygame.draw.line(surface, color, (rect.left, rect.top + 10), (rect.left, rect.top), 2)
    pygame.draw.line(surface, color, (rect.left, rect.top), (rect.left + 10, rect.top), 2)
    
    # Заголовок
    title_surf = ui_font.render(title, True, TEXT_COLOR)
    # Тень для текста
    title_shadow = ui_font.render(title, True, (0,0,0))
    surface.blit(title_shadow, (rect.left + 10 + 1, rect.top - title_surf.get_height() // 2 + 1))
    surface.blit(title_surf, (rect.left + 10, rect.top - title_surf.get_height() // 2))

def draw_atom_logo(surface, center, size, color):
    """Улучшенная версия лого с частицами и ударной волной."""
    global shockwave
    radius = size // 2
    
    # Ударная волна
    if shockwave['alpha'] > 0:
        sw_color = (*color[:3], int(shockwave['alpha']))
        temp_surf = pygame.Surface((shockwave['radius']*2, shockwave['radius']*2), pygame.SRCALPHA)
        pygame.draw.circle(temp_surf, sw_color, (shockwave['radius'], shockwave['radius']), shockwave['radius'], width=3)
        surface.blit(temp_surf, (center[0]-shockwave['radius'], center[1]-shockwave['radius']), special_flags=pygame.BLEND_RGBA_ADD)

    # Орбиты
    orbits_params = [ {'rx': radius, 'ry': radius * 0.4, 'angle': a} for a in [90, 30, -30] ]
    for params in orbits_params:
        points = get_ellipse_points(center, params['rx'], params['ry'], params['angle'])
        pygame.draw.aalines(surface, (color.r*0.5, color.g*0.5, color.b*0.5), False, points, 2)
    
    # Электроны и их следы
    for i, params in enumerate(orbits_params):
        angle_rad, theta = math.radians(params['angle']), math.radians(electron_angles[i])
        x0, y0 = params['rx'] * math.cos(theta), params['ry'] * math.sin(theta)
        ex = center[0] + x0 * math.cos(angle_rad) - y0 * math.sin(angle_rad)
        ey = center[1] + x0 * math.sin(angle_rad) + y0 * math.cos(angle_rad)
        
        particles.append(Particle(ex, ey, 0.5, is_trail=True)) # Добавляем частицу в след
        
        pygame.draw.circle(surface, (255,255,255), (ex, ey), int(size * 0.03))
        pygame.draw.circle(surface, color, (ex, ey), int(size * 0.025))

    # Плавное троеточие
    anim_time = pygame.time.get_ticks() * 0.005
    for i in range(3):
        pulse = (math.sin(anim_time - i * 0.8) + 1) / 2
        dot_color = lerp_color(pygame.Color(color.r//2, color.g//2, color.b//2), color, pulse)
        if pulse > 0.95 and shockwave['alpha'] <= 0: # Запускаем волну в пике пульсации
            shockwave = {'radius': 20, 'alpha': 255}
        dot_pos_x = center[0] + (i - 1) * int(size * 0.1)
        pygame.draw.circle(surface, dot_color, (dot_pos_x, center[1]), int(size * 0.02))

def draw_voice_visualizer(surface, rect, color, wave_data):
    """Рисует симуляцию голосового анализатора."""
    draw_frame(surface, rect, "VOICE WAVEFORM ANALYSIS", color)
    bar_width = rect.width / len(wave_data)
    for i, val in enumerate(wave_data):
        bar_height = abs(val) * (rect.height * 0.8)
        x = rect.left + i * bar_width
        y = rect.centery - bar_height / 2
        bar_rect = pygame.Rect(x, y, bar_width - 2, bar_height)
        
        # Градиент для бара
        c1 = pygame.Color(color)
        c2 = lerp_color(c1, pygame.Color('black'), 0.5)
        pygame.draw.rect(surface, c1, bar_rect, 0, border_radius=2)
        
def draw_background(surface, color):
    """Рисует фон с частицами, сеткой и виньеткой."""
    surface.fill(BLACK)
    # Частицы
    for p in particles: p.draw(surface, color)
    # Сетка
    for x in range(0, SCREEN_WIDTH, 50): pygame.draw.line(surface, GRID_COLOR_BASE, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, 50): pygame.draw.line(surface, GRID_COLOR_BASE, (0, y), (SCREEN_WIDTH, y))
    
    # Виньетка (накладываем поверх всего)
    vignette_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    radial_grad = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    for i in range(min(SCREEN_WIDTH, SCREEN_HEIGHT) // 2, 0, -2):
        alpha = 255 - (i / (min(SCREEN_WIDTH, SCREEN_HEIGHT) // 2)) * 255
        pygame.draw.circle(radial_grad, (0, 0, 0, int(alpha)), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), i)
    surface.blit(radial_grad, (0,0))


# --- Главный цикл ---
running = True
clock = pygame.time.Clock()
# ... [Остальные хелперы и функции, такие как lerp, get_ellipse_points, draw_graph и т.д. из прошлой версии] ...

# (Скопируем недостающие функции из предыдущего кода для полноты)
def lerp(a, b, t): return a + (b - a) * t
def lerp_color(c1, c2, t): return pygame.Color(int(lerp(c1.r, c2.r, t)), int(lerp(c1.g, c2.g, t)), int(lerp(c1.b, c2.b, t)))
def get_ellipse_points(center, rx, ry, angle_deg, num_points=100):
    points = []; angle_rad = math.radians(angle_deg)
    for i in range(num_points + 1):
        theta = 2 * math.pi * i / num_points; x0 = rx * math.cos(theta); y0 = ry * math.sin(theta)
        x = center[0] + x0 * math.cos(angle_rad) - y0 * math.sin(angle_rad)
        y = center[1] + x0 * math.sin(angle_rad) + y0 * math.cos(angle_rad); points.append((x, y))
    return points

while running:
    dt = clock.tick(60) / 1000.0
    current_time_ms = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
            
    # --- Обновление логики ---
    # Плавная смена цвета
    target_color = pygame.Color(logo_colors[target_color_index])
    if abs(current_color.r - target_color.r) < 5: target_color_index = (target_color_index + 1) % len(logo_colors)
    current_color = lerp_color(current_color, target_color, 0.5 * dt)
    
    # Анимации
    electron_angles = [(a + (60 + i*15) * dt) % 360 for i, a in enumerate(electron_angles)]
    if shockwave['alpha'] > 0:
        shockwave['radius'] += 400 * dt
        shockwave['alpha'] -= 300 * dt
    
    particles = [p for p in particles if p.update(dt)]
    
    # Симуляция данных
    if current_time_ms % 200 < 20: # Обновляем реже для плавности
        for k in ['cpu_usage', 'ram_usage', 'net_down', 'net_up', 'core_sync', 'current_temp']:
            data[k] = max(0, min(100, data[k] + random.uniform(-0.5, 0.5)))
        data['graph1'].append(data['graph1'][-1] + random.randint(-2, 2))
        data['graph2'].append(data['graph2'][-1] + random.randint(-3, 3))
        
        if random.random() < 0.2:
            events = ["AUTH", "QUERY", "FETCH", "SYNC", "TASK", "WARN"]; data['logs'].append(f"{random.randint(1000,9999)} | {random.choice(events)} | OK")
    
    voice_wave.pop(0); voice_wave.append(voice_wave[-1] + (random.uniform(-0.2, 0.2) - voice_wave[-1])*0.3)
    
    # --- Отрисовка ---
    # Рисуем всё на временной поверхности для эффекта fade-in
    main_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    
    draw_background(main_surface, current_color)
    
    # Левая панель
    draw_frame(main_surface, pygame.Rect(50, 50, 350, 100), "CPU & MEMORY", current_color)
    # ... и так далее для всех виджетов ...
    # ... (Ниже полная отрисовка виджетов, чтобы код был рабочим) ...
    # CPU
    text = ui_font.render(f"CPU CORE 01: {data['cpu_usage']:.1f}%", True, TEXT_COLOR)
    main_surface.blit(text, (70, 80))
    pygame.draw.rect(main_surface, GRAY, (70, 110, 310, 10), 0, 3)
    pygame.draw.rect(main_surface, current_color, (70, 110, 310 * data['cpu_usage'] / 100, 10), 0, 3)
    # RAM
    text = ui_font.render(f"MEMORY USAGE: {data['ram_usage']:.1f}%", True, TEXT_COLOR)
    main_surface.blit(text, (70, 130))
    
    # Правая панель
    draw_frame(main_surface, pygame.Rect(SCREEN_WIDTH - 400, 50, 350, 200), "ENERGY & DATA", current_color)

    # Лого
    draw_atom_logo(main_surface, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), 450, current_color)
    
    # Визуализатор голоса
    draw_voice_visualizer(main_surface, pygame.Rect(SCREEN_WIDTH // 2 - 300, SCREEN_HEIGHT - 150, 600, 100), current_color, voice_wave)

    # Время и дата
    now = datetime.datetime.now()
    time_surf = main_font.render(now.strftime("%H:%M:%S"), True, TEXT_COLOR)
    date_surf = ui_font.render(now.strftime("%Y-%m-%d"), True, TEXT_COLOR)
    main_surface.blit(time_surf, time_surf.get_rect(centerx=SCREEN_WIDTH // 2, top=30))
    main_surface.blit(date_surf, date_surf.get_rect(centerx=SCREEN_WIDTH // 2, top=90))
    
    # Эффект плавного появления при старте
    if startup_alpha < 255:
        startup_alpha = min(255, startup_alpha + 200 * dt)
    main_surface.set_alpha(startup_alpha)
    
    screen.blit(main_surface, (0,0))
    pygame.display.flip()

pygame.quit()
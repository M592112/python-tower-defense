import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
GRID_SIZE = 40
TOWER_COST = 50
UPGRADE_COST = 30

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
LIGHT_BLUE = (173, 216, 230)
YELLOW = (255, 255, 0)
GOLD = (255, 215, 0)
DARK_BLUE = (0, 0, 139)
PURPLE = (128, 0, 128)

# Path coordinates (grid positions)
PATH = [
    (0, 7), (1, 7), (2, 7), (3, 7), (4, 7), (5, 7),
    (5, 6), (5, 5), (5, 4), (5, 3),
    (6, 3), (7, 3), (8, 3), (9, 3), (10, 3),
    (10, 4), (10, 5), (10, 6), (10, 7), (10, 8),
    (11, 8), (12, 8), (13, 8), (14, 8), (15, 8),
    (15, 9), (15, 10), (15, 11), (16, 11), (17, 11),
    (18, 11), (19, 11)
]

# Initialize display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Tower Defense")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

# ---------------------------------------
# ENEMY CLASS
# ---------------------------------------
class Enemy:
    def __init__(self, speed_multiplier=1, health_multiplier=1):
        self.path_index = 0
        self.x = PATH[0][0] * GRID_SIZE + GRID_SIZE // 2
        self.y = PATH[0][1] * GRID_SIZE + GRID_SIZE // 2
        self.speed = 1 * speed_multiplier
        self.radius = 12
        self.health = 100 * health_multiplier
        self.max_health = 100 * health_multiplier
        self.reward = int(10 * health_multiplier)

    def move(self):
        if self.path_index < len(PATH) - 1:
            target_x = PATH[self.path_index + 1][0] * GRID_SIZE + GRID_SIZE // 2
            target_y = PATH[self.path_index + 1][1] * GRID_SIZE + GRID_SIZE // 2

            dx = target_x - self.x
            dy = target_y - self.y
            distance = math.sqrt(dx**2 + dy**2)

            if distance < self.speed:
                self.path_index += 1
            else:
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed

    def take_damage(self, damage):
        self.health -= damage

    def is_alive(self):
        return self.health > 0

    def draw(self):
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.radius)
        # Health bar
        bar_width = 30
        bar_height = 4
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - bar_width//2, self.y - 20, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (self.x - bar_width//2, self.y - 20, bar_width * health_ratio, bar_height))

    def reached_end(self):
        return self.path_index >= len(PATH) - 1

# ---------------------------------------
# PROJECTILE CLASS
# ---------------------------------------
class Projectile:
    def __init__(self, x, y, target, damage):
        self.x = x
        self.y = y
        self.target = target
        self.speed = 5
        self.damage = damage
        self.radius = 5

    def move(self):
        if self.target and self.target.is_alive():
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            distance = math.sqrt(dx**2 + dy**2)

            if distance < self.speed:
                return True  # hit target
            else:
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed
                return False

        return True  # target dead

    def draw(self):
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.radius)

# ---------------------------------------
# TOWER CLASS
# ---------------------------------------
class Tower:
    def __init__(self, grid_x, grid_y):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.x = grid_x * GRID_SIZE + GRID_SIZE // 2
        self.y = grid_y * GRID_SIZE + GRID_SIZE // 2
        self.level = 1
        self.range = 100
        self.damage = 20
        self.fire_rate = 60
        self.fire_timer = 0

    def upgrade(self):
        if self.level < 3:
            self.level += 1
            self.range += 20
            self.damage += 15
            self.fire_rate = max(30, self.fire_rate - 10)
            return True
        return False

    def can_upgrade(self):
        return self.level < 3

    def find_target(self, enemies):
        for enemy in enemies:
            distance = math.sqrt((enemy.x - self.x)**2 + (enemy.y - self.y)**2)
            if distance <= self.range:
                return enemy
        return None

    def shoot(self, target):
        if self.fire_timer <= 0:
            self.fire_timer = self.fire_rate
            return Projectile(self.x, self.y, target, self.damage)
        return None

    def update(self):
        if self.fire_timer > 0:
            self.fire_timer -= 1

    def is_clicked(self, mouse_x, mouse_y):
        rect = pygame.Rect(self.grid_x * GRID_SIZE, self.grid_y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        return rect.collidepoint(mouse_x, mouse_y)

    def draw(self, selected=False):
        # Range circle
        pygame.draw.circle(
            screen, LIGHT_BLUE, (int(self.x), int(self.y)), self.range,
            2 if selected else 1
        )

        # Tower color by level
        color = BLUE if self.level == 1 else (DARK_BLUE if self.level == 2 else PURPLE)
        pygame.draw.rect(
            screen, color,
            (self.grid_x * GRID_SIZE + 5, self.grid_y * GRID_SIZE + 5, GRID_SIZE - 10, GRID_SIZE - 10)
        )

        # Level indicator
        text = small_font.render(str(self.level), True, WHITE)
        screen.blit(text, (self.x - 7, self.y - 10))

# ---------------------------------------
# WAVE MANAGER
# ---------------------------------------
class WaveManager:
    def __init__(self):
        self.wave = 1
        self.enemies_per_wave = 5
        self.enemies_to_spawn = self.enemies_per_wave
        self.spawn_timer = 0
        self.spawn_delay = 90

    def spawn_enemy(self):
        if self.enemies_to_spawn > 0 and self.spawn_timer <= 0:
            self.spawn_timer = self.spawn_delay
            self.enemies_to_spawn -= 1
            speed_mult = 1 + (self.wave - 1) * 0.1
            health_mult = 1 + (self.wave - 1) * 0.2
            return Enemy(speed_mult, health_mult)
        return None

    def update(self):
        if self.spawn_timer > 0:
            self.spawn_timer -= 1

    def next_wave(self):
        self.wave += 1
        self.enemies_per_wave += 2
        self.enemies_to_spawn = self.enemies_per_wave

# ---------------------------------------
# GAME STATE
# ---------------------------------------
class GameState:
    def __init__(self):
        self.money = 200
        self.lives = 20
        self.score = 0

    def add_money(self, amount):
        self.money += amount

    def spend_money(self, amount):
        if self.money >= amount:
            self.money -= amount
            return True
        return False

    def lose_life(self):
        self.lives -= 1

    def add_score(self, points):
        self.score += points

# ---------------------------------------
# HELPERS
# ---------------------------------------
def is_valid_tower_position(grid_x, grid_y, towers):
    if (grid_x, grid_y) in PATH:
        return False
    for tower in towers:
        if tower.grid_x == grid_x and tower.grid_y == grid_y:
            return False
    return True

def draw_grid():
    for x in range(0, WINDOW_WIDTH, GRID_SIZE):
        pygame.draw.line(screen, GRAY, (x, 0), (x, WINDOW_HEIGHT), 1)
    for y in range(0, WINDOW_HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, GRAY, (0, y), (WINDOW_WIDTH, y), 1)

def draw_path():
    for pos in PATH:
        rect = pygame.Rect(pos[0] * GRID_SIZE, pos[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(screen, BROWN, rect)

def draw_ui(game_state, wave_manager, selected_tower):
    screen.blit(font.render(f"Wave: {wave_manager.wave}", True, WHITE), (10, 10))
    screen.blit(font.render(f"Money: ${game_state.money}", True, GOLD), (10, 45))
    screen.blit(font.render(f"Lives: {game_state.lives}", True, RED), (10, 80))
    screen.blit(small_font.render(f"Score: {game_state.score}", True, WHITE), (10, 115))

    # Tower cost
    screen.blit(small_font.render(f"Tower: ${TOWER_COST}", True, WHITE),
                (WINDOW_WIDTH - 150, 10))

    if selected_tower:
        screen.blit(small_font.render(f"Upgrade: ${UPGRADE_COST}", True, WHITE),
                    (WINDOW_WIDTH - 170, 35))

        if selected_tower.level >= 3:
            screen.blit(small_font.render("MAX LEVEL", True, WHITE),
                        (WINDOW_WIDTH - 140, 60))
        else:
            screen.blit(small_font.render("Press U to upgrade", True, WHITE),
                        (WINDOW_WIDTH - 180, 60))

# ---------------------------------------
# MAIN GAME LOOP
# ---------------------------------------
def main():
    running = True
    enemies = []
    towers = []
    projectiles = []
    wave_manager = WaveManager()
    game_state = GameState()
    selected_tower = None

    while running:
        # -----------------------
        # EVENTS
        # -----------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                grid_x = mouse_x // GRID_SIZE
                grid_y = mouse_y // GRID_SIZE

                clicked_tower = None
                for tower in towers:
                    if tower.is_clicked(mouse_x, mouse_y):
                        clicked_tower = tower
                        break

                if clicked_tower:
                    selected_tower = clicked_tower
                elif is_valid_tower_position(grid_x, grid_y, towers):
                    if game_state.spend_money(TOWER_COST):
                        towers.append(Tower(grid_x, grid_y))
                        selected_tower = None

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_u and selected_tower:
                    if selected_tower.can_upgrade() and game_state.spend_money(UPGRADE_COST):
                        selected_tower.upgrade()

        # -----------------------
        # WAVE & ENEMY LOGIC
        # -----------------------
        wave_manager.update()
        new_enemy = wave_manager.spawn_enemy()
        if new_enemy:
            enemies.append(new_enemy)

        if wave_manager.enemies_to_spawn == 0 and len(enemies) == 0:
            wave_manager.next_wave()

        for enemy in enemies[:]:
            enemy.move()
            if enemy.reached_end():
                game_state.lose_life()
                enemies.remove(enemy)

        # -----------------------
        # TOWER LOGIC
        # -----------------------
        for tower in towers:
            tower.update()
            target = tower.find_target(enemies)
            if target:
                projectile = tower.shoot(target)
                if projectile:
                    projectiles.append(projectile)

        # -----------------------
        # PROJECTILE LOGIC
        # -----------------------
        for projectile in projectiles[:]:
            if projectile.move():
                if projectile.target and projectile.target.is_alive():
                    projectile.target.take_damage(projectile.damage)
                projectiles.remove(projectile)

        # -----------------------
        # REMOVE DEAD ENEMIES
        # -----------------------
        for enemy in enemies[:]:
            if not enemy.is_alive():
                game_state.add_money(enemy.reward)
                game_state.add_score(enemy.reward * 10)
                enemies.remove(enemy)

        # -----------------------
        # GAME OVER CHECK
        # -----------------------
        if game_state.lives <= 0:
            running = False

        # -----------------------
        # DRAWING
        # -----------------------
        screen.fill(GREEN)
        draw_path()

        for tower in towers:
            tower.draw(selected=tower == selected_tower)

        for projectile in projectiles:
            projectile.draw()

        for enemy in enemies:
            enemy.draw()

        draw_grid()
        draw_ui(game_state, wave_manager, selected_tower)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

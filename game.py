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
DARK_GREEN = (0, 100, 0)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
LIGHT_BLUE = (173, 216, 230)
YELLOW = (255, 255, 0)
GOLD = (255, 215, 0)
DARK_BLUE = (0, 0, 139)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)

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
pygame.display.set_caption("Tower Defense - Defend Your Base!")
clock = pygame.time.Clock()

# Fonts
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)
large_font = pygame.font.Font(None, 72)
tiny_font = pygame.font.Font(None, 20)

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
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius, 2)

        # Health bar
        bar_width = 30
        bar_height = 5
        ratio = max(0, self.health / self.max_health)
        pygame.draw.rect(screen, BLACK, (self.x - bar_width//2 - 1, self.y - 22, bar_width + 2, bar_height + 2))
        pygame.draw.rect(screen, RED, (self.x - bar_width//2, self.y - 21, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (self.x - bar_width//2, self.y - 21, bar_width * ratio, bar_height))

    def reached_end(self):
        return self.path_index >= len(PATH) - 1


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
                return True
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed
            return False
        return True

    def draw(self):
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.radius)
        if self.radius > 2:  # Prevent negative radius error
            pygame.draw.circle(screen, ORANGE, (int(self.x), int(self.y)), self.radius - 2)


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
            if math.dist((enemy.x, enemy.y), (self.x, self.y)) <= self.range:
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
        if selected:
            pygame.draw.circle(screen, LIGHT_BLUE, (int(self.x), int(self.y)), self.range, 3)
        else:
            pygame.draw.circle(screen, LIGHT_BLUE, (int(self.x), int(self.y)), self.range, 1)

        color = BLUE if self.level == 1 else DARK_BLUE if self.level == 2 else PURPLE
        size = GRID_SIZE - 10
        pygame.draw.rect(screen, color, (self.grid_x * GRID_SIZE + 5, self.grid_y * GRID_SIZE + 5, size, size))
        pygame.draw.rect(screen, BLACK, (self.grid_x * GRID_SIZE + 5, self.grid_y * GRID_SIZE + 5, size, size), 2)

        level_text = small_font.render(str(self.level), True, WHITE)
        shadow = small_font.render(str(self.level), True, BLACK)
        screen.blit(shadow, (self.x - 6, self.y - 9))
        screen.blit(level_text, (self.x - 7, self.y - 10))


class WaveManager:
    def __init__(self):
        self.wave = 1
        self.enemies_per_wave = 5
        self.enemies_to_spawn = self.enemies_per_wave
        self.spawn_timer = 0
        self.spawn_delay = 90
        self.wave_complete = False

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
        self.wave_complete = False


class GameState:
    def __init__(self):
        self.money = 200
        self.lives = 20
        self.score = 0
        self.game_over = False
        self.high_score = 0

    def add_money(self, amount):
        self.money += amount

    def spend_money(self, amount):
        if self.money >= amount:
            self.money -= amount
            return True
        return False

    def lose_life(self):
        self.lives -= 1
        if self.lives <= 0:
            self.game_over = True
            if self.score > self.high_score:
                self.high_score = self.score

    def add_score(self, points):
        self.score += points

    def reset(self):
        self.money = 200
        self.lives = 20
        self.score = 0
        self.game_over = False


def is_valid_tower_position(grid_x, grid_y, towers):
    if (grid_x, grid_y) in PATH:
        return False
    if grid_x < 0 or grid_y < 0 or grid_x >= WINDOW_WIDTH // GRID_SIZE or grid_y >= WINDOW_HEIGHT // GRID_SIZE:
        return False
    for t in towers:
        if t.grid_x == grid_x and t.grid_y == grid_y:
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
        pygame.draw.rect(screen, BLACK, rect, 1)


def draw_ui(game_state, wave_manager, selected_tower, paused):
    wave_text = font.render(f"Wave: {wave_manager.wave}", True, WHITE)
    screen.blit(wave_text, (10, 8))
    money_text = font.render(f"Money: ${game_state.money}", True, GOLD)
    screen.blit(money_text, (10, 40))
    lives_text = font.render(f"Lives: {game_state.lives}", True, RED)
    screen.blit(lives_text, (10, 72))
    score_text = small_font.render(f"Score: {game_state.score}", True, WHITE)
    screen.blit(score_text, (10, 104))
    high_text = small_font.render(f"High: {game_state.high_score}", True, YELLOW)
    screen.blit(high_text, (10, 128))

    # Controls (top right)
    cost_text = small_font.render(f"Place Tower: ${TOWER_COST} (Left click)", True, WHITE)
    screen.blit(cost_text, (WINDOW_WIDTH - 320, 8))
    sell_text = small_font.render("Sell Tower: Right click (refund 50%)", True, WHITE)
    screen.blit(sell_text, (WINDOW_WIDTH - 320, 32))
    upgrade_text = small_font.render(f"Upgrade: ${UPGRADE_COST} (Select + U)", True, WHITE)
    screen.blit(upgrade_text, (WINDOW_WIDTH - 320, 56))
    pause_text = small_font.render("P = Pause", True, WHITE)
    screen.blit(pause_text, (WINDOW_WIDTH - 320, 80))

    if paused:
        paused_text = large_font.render("PAUSED", True, YELLOW)
        rect = paused_text.get_rect(center=(WINDOW_WIDTH // 2, 40))
        screen.blit(paused_text, rect)

    # Selected tower panel
    if selected_tower:
        panel_x = WINDOW_WIDTH - 200
        panel_y = WINDOW_HEIGHT - 120
        panel = pygame.Rect(panel_x, panel_y, 190, 110)
        pygame.draw.rect(screen, DARK_GREEN, panel)
        pygame.draw.rect(screen, BLACK, panel, 2)

        title = small_font.render("Selected Tower", True, WHITE)
        screen.blit(title, (panel_x + 10, panel_y + 8))
        lvl = small_font.render(f"Level: {selected_tower.level}", True, WHITE)
        screen.blit(lvl, (panel_x + 10, panel_y + 34))
        dmg = small_font.render(f"Damage: {selected_tower.damage}", True, WHITE)
        screen.blit(dmg, (panel_x + 10, panel_y + 58))
        rng = small_font.render(f"Range: {selected_tower.range}", True, WHITE)
        screen.blit(rng, (panel_x + 10, panel_y + 82))

        if not selected_tower.can_upgrade():
            max_text = small_font.render("MAX LEVEL", True, GOLD)
            screen.blit(max_text, (panel_x + 100, panel_y + 34))


def draw_game_over(game_state):
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    overlay.set_alpha(210)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))

    go_text = large_font.render("GAME OVER", True, RED)
    rect = go_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 80))
    screen.blit(go_text, rect)

    score_text = font.render(f"Final Score: {game_state.score}", True, WHITE)
    rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
    screen.blit(score_text, rect)

    high_text = small_font.render(f"High Score: {game_state.high_score}", True, YELLOW)
    rect = high_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 40))
    screen.blit(high_text, rect)

    instr = small_font.render("Press R to Restart or Q to Quit", True, WHITE)
    rect = instr.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 80))
    screen.blit(instr, rect)


def reset_game():
    enemies = []
    towers = []
    projectiles = []
    wave_manager = WaveManager()
    game_state = GameState()
    selected_tower = None
    paused = False
    return enemies, towers, projectiles, wave_manager, game_state, selected_tower, paused


def main():
    running = True
    enemies, towers, projectiles, wave_manager, game_state, selected_tower, paused = reset_game()

    pregame_timer = 120  # Let player build before first wave

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if game_state.game_over:
                    if event.key == pygame.K_r:
                        enemies, towers, projectiles, wave_manager, game_state, selected_tower, paused = reset_game()
                    elif event.key == pygame.K_q:
                        running = False
                else:
                    if event.key == pygame.K_p:
                        paused = not paused

                    if event.key == pygame.K_u and selected_tower and not paused:
                        if selected_tower.can_upgrade() and game_state.spend_money(UPGRADE_COST):
                            selected_tower.upgrade()

                    if event.key == pygame.K_s and selected_tower and not paused:
                        refund = int(TOWER_COST * 0.5 * selected_tower.level)
                        game_state.add_money(refund)
                        towers.remove(selected_tower)
                        selected_tower = None

            elif event.type == pygame.MOUSEBUTTONDOWN and not game_state.game_over and not paused:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                grid_x = mouse_x // GRID_SIZE
                grid_y = mouse_y // GRID_SIZE

                if event.button == 3:  # Right click → sell
                    for t in towers:
                        if t.is_clicked(mouse_x, mouse_y):
                            refund = int(TOWER_COST * 0.5 * t.level)
                            game_state.add_money(refund)
                            if t == selected_tower:
                                selected_tower = None
                            towers.remove(t)
                            break

                elif event.button == 1:  # Left click → select or place
                    clicked = None
                    for t in towers:
                        if t.is_clicked(mouse_x, mouse_y):
                            clicked = t
                            break
                    if clicked:
                        selected_tower = clicked
                    else:
                        if is_valid_tower_position(grid_x, grid_y, towers):
                            if game_state.spend_money(TOWER_COST):
                                towers.append(Tower(grid_x, grid_y))
                                selected_tower = None

        if not game_state.game_over and not paused:
            if pregame_timer > 0:
                pregame_timer -= 1
            else:
                wave_manager.update()
                enemy = wave_manager.spawn_enemy()
                if enemy:
                    enemies.append(enemy)

                if wave_manager.enemies_to_spawn == 0 and len(enemies) == 0:
                    wave_manager.next_wave()

                # Enemy updates
                for enemy in enemies[:]:
                    enemy.move()
                    if enemy.reached_end():
                        game_state.lose_life()
                        enemies.remove(enemy)

                # Tower updates
                for tower in towers:
                    tower.update()
                    target = tower.find_target(enemies)
                    if target:
                        proj = tower.shoot(target)
                        if proj:
                            projectiles.append(proj)

                # Projectile updates
                for proj in projectiles[:]:
                    hit = proj.move()
                    if hit:
                        if proj.target and proj.target.is_alive():
                            proj.target.take_damage(proj.damage)
                        if proj in projectiles:
                            projectiles.remove(proj)

                # Remove dead enemies
                for enemy in enemies[:]:
                    if not enemy.is_alive():
                        game_state.add_money(enemy.reward)
                        game_state.add_score(enemy.reward * 10)
                        enemies.remove(enemy)

                if game_state.game_over:
                    if game_state.score > game_state.high_score:
                        game_state.high_score = game_state.score

        # Rendering
        screen.fill(DARK_GREEN)
        draw_path()
        for tower in towers:
            tower.draw(selected=(tower == selected_tower))
        for proj in projectiles:
            proj.draw()
        for enemy in enemies:
            enemy.draw()
        draw_grid()
        draw_ui(game_state, wave_manager, selected_tower, paused)

        if game_state.game_over:
            draw_game_over(game_state)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

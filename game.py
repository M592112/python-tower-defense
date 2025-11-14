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

class Enemy:
    def __init__(self):
        self.path_index = 0
        self.x = PATH[0][0] * GRID_SIZE + GRID_SIZE // 2
        self.y = PATH[0][1] * GRID_SIZE + GRID_SIZE // 2
        self.speed = 1
        self.radius = 12
        self.health = 100
        self.max_health = 100
        
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

class Projectile:
    def __init__(self, x, y, target):
        self.x = x
        self.y = y
        self.target = target
        self.speed = 5
        self.damage = 20
        self.radius = 5
        
    def move(self):
        if self.target and self.target.is_alive():
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance < self.speed:
                return True  # Hit target
            else:
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed
                return False
        return True  # Target dead, remove projectile
    
    def draw(self):
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.radius)

class Tower:
    def __init__(self, grid_x, grid_y):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.x = grid_x * GRID_SIZE + GRID_SIZE // 2
        self.y = grid_y * GRID_SIZE + GRID_SIZE // 2
        self.range = 100
        self.damage = 20
        self.fire_rate = 60  # frames between shots
        self.fire_timer = 0
        
    def find_target(self, enemies):
        for enemy in enemies:
            distance = math.sqrt((enemy.x - self.x)**2 + (enemy.y - self.y)**2)
            if distance <= self.range:
                return enemy
        return None
    
    def shoot(self, target):
        if self.fire_timer <= 0:
            self.fire_timer = self.fire_rate
            return Projectile(self.x, self.y, target)
        return None
    
    def update(self):
        if self.fire_timer > 0:
            self.fire_timer -= 1
        
    def draw(self):
        # Draw range circle
        pygame.draw.circle(screen, LIGHT_BLUE, (int(self.x), int(self.y)), self.range, 1)
        # Draw tower
        pygame.draw.rect(screen, BLUE, (self.grid_x * GRID_SIZE + 5, self.grid_y * GRID_SIZE + 5, 
                                       GRID_SIZE - 10, GRID_SIZE - 10))

def is_valid_tower_position(grid_x, grid_y, towers):
    # Check if position is on path
    if (grid_x, grid_y) in PATH:
        return False
    # Check if position is already occupied
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

def main():
    running = True
    enemies = [Enemy()]
    towers = []
    projectiles = []
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                grid_x = mouse_x // GRID_SIZE
                grid_y = mouse_y // GRID_SIZE
                
                if is_valid_tower_position(grid_x, grid_y, towers):
                    towers.append(Tower(grid_x, grid_y))
        
        # Update enemies
        for enemy in enemies:
            enemy.move()
        
        # Update towers
        for tower in towers:
            tower.update()
            target = tower.find_target(enemies)
            if target:
                projectile = tower.shoot(target)
                if projectile:
                    projectiles.append(projectile)
        
        # Update projectiles
        for projectile in projectiles[:]:
            if projectile.move():
                if projectile.target and projectile.target.is_alive():
                    projectile.target.take_damage(projectile.damage)
                projectiles.remove(projectile)
        
        # Remove dead enemies
        enemies = [enemy for enemy in enemies if enemy.is_alive() and not enemy.reached_end()]
        
        # Fill screen
        screen.fill(GREEN)
        
        # Draw elements
        draw_path()
        for tower in towers:
            tower.draw()
        for projectile in projectiles:
            projectile.draw()
        for enemy in enemies:
            enemy.draw()
        draw_grid()
        
        # Update display
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
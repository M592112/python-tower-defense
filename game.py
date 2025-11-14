import pygame
import sys

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
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Fill screen
        screen.fill(GREEN)
        
        # Draw elements
        draw_path()
        draw_grid()
        
        # Update display
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
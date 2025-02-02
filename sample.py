import pygame
import numpy as np
import heapq
import random

# Grid Settings
GRID_SIZE = (20, 20)
CELL_SIZE = 30  # Pixel size per grid cell
EXIT_POSITIONS = [(19, 9), (19, 10)]  
NUM_PEOPLE = 15
PANIC_PROBABILITY = 0.2  
SPEED_VARIATION = [1, 2]  
SCREEN_SIZE = (GRID_SIZE[1] * CELL_SIZE, GRID_SIZE[0] * CELL_SIZE)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (150, 150, 150)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("Emergency Evacuation Simulation")

# Create Grid
grid = np.zeros(GRID_SIZE)
grid[:, 0] = grid[:, -1] = 1  
grid[0, :] = grid[-1, :] = 1  
for ex in EXIT_POSITIONS:
    grid[ex] = 2  

# Add obstacles
obstacles = [(random.randint(5, 15), random.randint(5, 15)) for _ in range(10)]
for ob in obstacles:
    grid[ob] = 1  

# Add people
people = []
while len(people) < NUM_PEOPLE:
    x, y = random.randint(1, GRID_SIZE[0] - 2), random.randint(1, GRID_SIZE[1] - 2)
    if grid[x, y] == 0:
        speed = random.choice(SPEED_VARIATION)
        grid[x, y] = 3
        people.append({"pos": (x, y), "speed": speed})

# A* Algorithm for Pathfinding
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star_search(start):
    open_list = []
    heapq.heappush(open_list, (0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}
    
    while open_list:
        _, current = heapq.heappop(open_list)
        if grid[current] == 2:
            break
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < GRID_SIZE[0] and 0 <= neighbor[1] < GRID_SIZE[1]:
                if grid[neighbor] in [0, 2]:
                    new_cost = cost_so_far[current] + 1
                    if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                        cost_so_far[neighbor] = new_cost
                        priority = new_cost + heuristic(neighbor, EXIT_POSITIONS[0])
                        heapq.heappush(open_list, (priority, neighbor))
                        came_from[neighbor] = current

    path = []
    current = EXIT_POSITIONS[0]
    while current in came_from and came_from[current] is not None:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path

# Move People
def move_people():
    global people
    new_positions = []
    
    for person in people:
        x, y = person["pos"]
        speed = person["speed"]
        
        if grid[x, y] == 2:
            continue

        if random.random() < PANIC_PROBABILITY:
            dx, dy = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < GRID_SIZE[0] and 0 <= new_y < GRID_SIZE[1] and grid[new_x, new_y] in [0, 2]:
                grid[x, y] = 0
                grid[new_x, new_y] = 3
                new_positions.append({"pos": (new_x, new_y), "speed": speed})
                continue

        path = a_star_search((x, y))
        if path and len(path) > speed:
            new_x, new_y = path[speed - 1]
            grid[x, y] = 0
            grid[new_x, new_y] = 3
            new_positions.append({"pos": (new_x, new_y), "speed": speed})
        else:
            new_positions.append({"pos": (x, y), "speed": speed})

    people = new_positions

# Draw the Grid
def draw_grid():
    screen.fill(WHITE)
    for x in range(GRID_SIZE[0]):
        for y in range(GRID_SIZE[1]):
            rect = pygame.Rect(y * CELL_SIZE, x * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if grid[x, y] == 1:  # Walls/Obstacles
                pygame.draw.rect(screen, BLACK, rect)
            elif grid[x, y] == 2:  # Exit
                pygame.draw.rect(screen, GREEN, rect)
            elif grid[x, y] == 3:  # People
                pygame.draw.rect(screen, RED, rect)
            else:
                pygame.draw.rect(screen, GRAY, rect, 1)  
    pygame.display.flip()

# Run the Simulation
running = True
paused = False
clock = pygame.time.Clock()
evacuation_time = 0

while running:
    clock.tick(5)  

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused  

    if not paused and any(grid[p["pos"]] == 3 for p in people):
        move_people()
        draw_grid()
        evacuation_time += 1

print(f"Total Evacuation Time: {evacuation_time} steps")
pygame.quit()

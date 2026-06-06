import pygame
import numpy as np

world_width = 600
world_height = 400
n = 10
background_colour = (20,20,40)

pygame.init()

screen = pygame.display.set_mode((world_width,world_height))

running = True

# Initialize arrays with random values

positions = np.column_stack([
    np.random.uniform(0, world_width, n),
    np.random.uniform(0, world_height, n)
])
print(positions)

velocities = np.zeros((n, 2))
print(velocities)

# Running loop
while running:
    # Check for events
    for event in pygame.event.get():
        # Check for quit
        if event.type == pygame.QUIT:
            running = False

    screen.fill(background_colour)

    # Draw particles

    for p in positions:
        pygame.draw.circle(screen, (255, 0, 0), (int(p[0]), int(p[1])), 5)

    pygame.display.update()

pygame.quit()
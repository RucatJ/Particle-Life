import pygame
import numpy as np

world_width = 400
world_height = 400

screen_width = 600
screen_height = 600

camera = [world_height/2, world_height/2]

n = 10
background_colour = (20,20,40)
r = 5

pygame.init()

screen = pygame.display.set_mode((screen_width,screen_height))

running = True

# Initialize arrays with random values

positions = np.column_stack([
    np.random.uniform(0, world_width, n),
    np.random.uniform(0, world_height, n)
])
# print(positions)

# velocities = np.zeros((n, 2))

velocities = np.column_stack([
    np.random.uniform(-1, 1, n),
    np.random.uniform(-1, 1, n)
])

clock = pygame.time.Clock()

# Running loop
while running:
    # Check for events
    for event in pygame.event.get():
        # Check for quit
        if event.type == pygame.QUIT:
            running = False

    # Fill screen colour
    screen.fill(background_colour)

    # Clamp particle positions
    positions[:, 0] = np.clip(positions[:, 0], r, world_width - r)
    positions[:, 1] = np.clip(positions[:, 1], r, world_height - r)

    # Draw particles
    for p in positions:
        position = (
            int(p[0] + camera[0]/2),
            int(p[1] + camera[1]/2)
        )

        pygame.draw.circle(screen, (255, 0, 0), position, r)

    # Update particle positions
    positions += velocities

    # Update screen
    pygame.display.update()
    clock.tick(60)

pygame.quit()
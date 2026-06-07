import pygame
import numpy as np
from math import floor

world_width = 800
world_height = 800

screen_width = 1000
screen_height = 1000

# Interaction limits
max_dist = 200
min_dist = 10

camera = [(screen_width - world_width) / 2, (screen_height - world_height) / 2]

n = 250
background_colour = (20,20,40)
world_colour = (40, 40, 80,)
r = 3
force_scale = 0.1

type_count = 6
colours = np.random.uniform(0,255, (type_count, 3))

pygame.init()

screen = pygame.display.set_mode((screen_width,screen_height))

running = True

# Initialize the coolest sounding array name ever

force_matrix = np.random.uniform(-1, 1, (type_count, type_count))

print(force_matrix)

# Initialize all particles

particles = np.column_stack([
    # Positions
    np.random.uniform(0, world_width, n),
    np.random.uniform(0, world_height, n),
    # Velocities
    np.random.uniform(-1, 1, n),
    np.random.uniform(-1, 1, n),
    # Types
    np.random.randint(0, type_count, n),
    # Grid cell
    np.zeros(n),
    np.zeros(n)
])

# print(particles)

clock = pygame.time.Clock()

print("\nRunning\n")

# Running loop
while running:
    # Check for events
    for event in pygame.event.get():
        # Check for quit
        if event.type == pygame.QUIT:
            running = False

    # Draw background
    screen.fill(background_colour)
    pygame.draw.rect(screen, world_colour, [
        camera[0],
        camera[1],
        world_width,
        world_height
    ])

    # Toroidal world
    particles[:, 0] = particles[:, 0] % world_width
    particles[:, 1] = particles[:, 1] % world_height

    # Draw particles

    for p in particles:
        # print(p, camera)
        # position = (
        #     int(p[0] % world_width + camera[0]),
        #     int(p[1] % world_height + camera[1])
        # )

        position = (
            int(p[0] + camera[0]),
            int(p[1] + camera[1])
        )

        pygame.draw.circle(screen, colours[int(p[4])-1], position, r)

    # Create grid and add all particles to grid

    grid = [[[] for i in range(floor(world_width / max_dist))] for i in range(floor(world_height / max_dist))]

    for i, p in enumerate(particles):
        cell_x = floor(p[0] / max_dist)
        cell_y = floor(p[1] / max_dist)
        if not grid[cell_y][cell_x] == 0:
            grid[cell_y][cell_x].append(i)
        else:
            grid[cell_y][cell_x] = [i]

        p[5] = cell_x
        p[6] = cell_y

    # Particle interactions (where it all goes wrong)
    for p in particles:
        near = []

        for dy in (-1, 0, 1):
            if grid[dy]:
                for dx in (-1, 0 ,1):
                    if grid[dy][dx]:
                        cell = (int(p[6] + dx), int(p[5] + dy))
                        near.append(cell)

        print(near)

        for _p in particles:
            force = [0, 0]

            diff_vect = [p[0] - _p[0], p[1] - _p[1]]
            diff = np.linalg.norm(diff_vect)

            if not diff:
                continue
            norm = [diff_vect[0] / diff, diff_vect[1] / diff]

            # print(diff)
            if not max_dist <= diff and not min_dist >= diff:
                force = force_matrix[int(p[4])][int(_p[4])] * ((max_dist/2 - abs(max_dist/2 - (diff - min_dist)))/(max_dist/2))
                force = [force * norm[0], force * norm[1]]
                # print(force)

                # print(force)
            elif diff <= min_dist:
                force = -pow((diff - min_dist)/2, 2)
                force = [force * norm[0], force * norm[1]]

            _p[2] += force[0] * force_scale
            _p[3] += force[1] * force_scale

    # Update particle positions
    particles[:, 0] += particles[:, 2]
    particles[:, 1] += particles[:, 3]

    # Slightly dampen velocities over time
    particles[:, 2] *= 0.9
    particles[:, 3] *= 0.9

    # Update screen
    pygame.display.update()
    clock.tick(60)

print(grid)

pygame.quit()
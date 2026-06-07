import pygame
import numpy as np
from math import floor, sqrt, ceil
from numba import jit

world_width = 800
world_height = 800

screen_width = 1000
screen_height = 1000

# Interaction limits
max_dist = 150
min_dist = 10

camera = [(screen_width - world_width) / 2, (screen_height - world_height) / 2]

n = 300
background_colour = (20,20,40)
world_colour = (40, 40, 80,)
r = 4
force_scale = 0.15

type_count = 12
colours = np.random.uniform(0,255, (type_count, 3))

pygame.init()

screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption("Epic Simulation :)")

running = True

# Initialize the coolest sounding array name ever

force_matrix = np.random.uniform(-1, 1, (type_count, type_count))

# print(force_matrix)

# Initialize all particles

positions = np.column_stack([
    np.random.uniform(0, world_width, n),
    np.random.uniform(0, world_height, n)
])

velocities = np.column_stack([
    np.random.uniform(-1, 1, n),
    np.random.uniform(-1, 1, n)
])

types = np.random.randint(0, type_count, n)

cell = np.zeros((n, 2))

# print(cell)

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
    positions[:, 0] = positions[:, 0] % world_width
    positions[:, 1] = positions[:, 1] % world_height

    # Clamp particle positions
    # positions[:, 0] = np.clip(positions[:, 0], 0, world_width)
    # positions[:, 1] = np.clip(positions[:, 1], 0, world_height)

    # Draw particles

    for i, p in enumerate(positions):
        # print(p, camera)
        # position = (
        #     int(p[0] % world_width + camera[0]),
        #     int(p[1] % world_height + camera[1])
        # )

        position = (
            int(p[0] + camera[0]),
            int(p[1] + camera[1])
        )

        pygame.draw.circle(screen, colours[int(types[i])], position, r)

    # Create grid and add all particles to grid

    grid = [[[] for i in range(ceil(world_width / max_dist))] for i in range(ceil(world_height / max_dist))]

    # print(grid)

    for i, p in enumerate(positions):
        cell_x = floor(p[0] / max_dist)
        cell_y = floor(p[1] / max_dist)

        # print(p[0], cell_x, p[1], cell_y)

        grid[cell_y][cell_x].append(i)

        cell[i][0] = cell_x
        cell[i][1] = cell_y

    gr = ceil(world_height / max_dist)
    gc = ceil(world_width / max_dist)

    max_dist_sq = max_dist**2
    min_dist_sq = min_dist**2

    # Particle interactions (where it all goes wrong)

    for i, p in enumerate(positions):
        for dcy in (-1, 0, 1):
                for dcx in (-1, 0 ,1):
                    ix = int((cell[i][0] + dcy) % gr)
                    iy = int((cell[i][1] + dcx) % gc)

                    if ix < gr and iy < gc:
                        # print(len(grid[iy][ix]))
                        for _i in grid[iy][ix]:

                            if i == _i:
                                continue

                            _p = positions[_i]

                            fx = 0
                            fy = 0

                            dx = positions[_i][0] - p[0]
                            dy = positions[_i][1] - p[1]

                            if dx > world_width / 2:
                                dx -= world_width
                            elif dx < -world_width / 2:
                                dx += world_width

                            if dy > world_height / 2:
                                dy -= world_height
                            elif dy < -world_height / 2:
                                dy += world_height

                            square_diff = dx**2 + dy**2

                            # print(diff)
                            if min_dist_sq <= square_diff <= max_dist_sq:
                                diff = sqrt(square_diff)
                                norm_x = dx / diff
                                norm_y = dy / diff

                                force = force_matrix[int(types[_i])][int(types[i])] * ((max_dist/2 - abs(max_dist/2 - (diff - min_dist)))/(max_dist/2))

                                fx = force * norm_x
                                fy = force * norm_y
                                # print(force)

                            elif square_diff <= min_dist_sq:
                                diff = sqrt(square_diff)
                                norm_x = dx / diff
                                norm_y = dy / diff

                                force = (diff - min_dist) * 2.5

                                fx = force * norm_x
                                fy = force * norm_y

                            velocities[i][0] += fx * force_scale
                            velocities[i][1] += fy * force_scale

    # Update particle positions
    positions[:, 0] += velocities[:, 0]
    positions[:, 1] += velocities[:, 1]

    # Slightly dampen velocities over time
    velocities[:, 0] *= 0.9
    velocities[:, 1] *= 0.9

    # Update screen
    pygame.display.update()
    clock.tick(30)

print(grid)

pygame.quit()
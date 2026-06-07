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

n = 1000
background_colour = (20,20,40)
world_colour = (40, 40, 80,)
r = 4
force_scale = 0.05

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

    max_dist_sq = max_dist**2
    min_dist_sq = min_dist**2

    # Particle interactions (where it all goes wrong)

    for i, p in enumerate(positions):
        deltas = positions - positions[i]
        dx = deltas[:, 0]
        dy = deltas[:, 1]

        dx = np.where(dx > world_width / 2, dx - world_width, dx)
        dx = np.where(dx < -world_width / 2, dx + world_width, dx)
        dy = np.where(dy > world_height / 2, dy - world_height, dy)
        dy = np.where(dy < -world_height / 2, dy + world_height, dy)

        sq_dists = dx**2 + dy**2
        dists = np.sqrt(np.maximum(sq_dists, 1e-10))

        lr_mask = (sq_dists >= min_dist_sq) & (sq_dists <= max_dist_sq)
        sr_mask = (sq_dists < min_dist_sq) & (sq_dists > 0)

        forces = np.zeros(n)
        d = dists[lr_mask]
        forces[lr_mask] = force_matrix[types[i], types][lr_mask] * ((max_dist/2 - np.abs(max_dist/2 - (d - min_dist))) / (max_dist/2))
        forces[sr_mask] = (dists[sr_mask] - min_dist) * 2.5

        norm_x = dx / dists
        norm_y = dy / dists

        velocities[i][0] += np.sum(forces * norm_x) * force_scale
        velocities[i][1] += np.sum(forces * norm_y) * force_scale

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
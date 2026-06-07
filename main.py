import pygame
import numpy as np
from math import floor, ceil

world_width = 800
world_height = 800

screen_width = 1000
screen_height = 1000

# Interaction limits
max_dist = 150
min_dist = 10

camera = [(screen_width - world_width) / 2, (screen_height - world_height) / 2]

n = 500
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

print(cell)

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

        pygame.draw.circle(screen, colours[int(types[i])-1], position, r)

    # Create grid and add all particles to grid

    grid = {}

    # print(grid)

    for i, p in enumerate(positions):
        cell_x = floor(p[0] / max_dist)
        cell_y = floor(p[1] / max_dist)

        # print(p[0], cell_x, p[1], cell_y)

        grid.setdefault((cell_y, cell_x), []).append(i)

        cell[i][0] = cell_y
        cell[i][1] = cell_x

    # Particle interactions (where it all goes wrong)
    for i, p in enumerate(positions):
        for dy in (-1, 0, 1):
                for dx in (-1, 0 ,1):
                    if (int(cell[i][0] + dy), int(cell[i][1] + dx)) in grid.keys():
                        for _i in grid[(int(cell[i][0] + dy), int(cell[i][1] + dx))]:
                            _p = particles[_i]

                            force = [0, 0]

                            diff_vect = [p[0] - positions[_i][0], p[1] - positions[_i][1]]
                            square_diff = diff_vect[0]**2 + diff_vect[1]**2

                            if not square_diff:
                                continue

                            # print(diff)
                            if not max_dist**2 <= square_diff and not min_dist**2 >= square_diff:
                                diff = np.linalg.norm(diff_vect)
                                norm = [diff_vect[0] / diff, diff_vect[1] / diff]

                                force = force_matrix[int(types[i])][int(types[_i])] * ((max_dist/2 - abs(max_dist/2 - (diff - min_dist)))/(max_dist/2))

                                force = [force * norm[0], force * norm[1]]
                                # print(force)

                                # print(force)
                            elif square_diff <= min_dist**2:
                                diff = np.linalg.norm(diff_vect)
                                norm = [diff_vect[0] / diff, diff_vect[1] / diff]

                                force = -((diff - min_dist)/2)**2
                                force = [force * norm[0], force * norm[1]]

                            velocities[_i][0] += force[0] * force_scale
                            velocities[_i][1] += force[1] * force_scale

    # Update particle positions
    positions[:, 0] += velocities[:, 0]
    positions[:, 1] += velocities[:, 1]

    # Slightly dampen velocities over time
    velocities[:, 0] *= 0.95
    velocities[:, 1] *= 0.95

    # Update screen
    pygame.display.update()
    clock.tick(30)

print(grid)

pygame.quit()
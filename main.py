import pygame
import numpy as np
from numpy.random import normal

world_width = 400
world_height = 400

screen_width = 600
screen_height = 600

# Interaction limits
max_dist = 200
min_dist = 20

camera = [world_height/2, world_height/2]

n = 150
background_colour = (20,20,40)
world_colour = (40, 40, 80,)
r = 5

type_count = 4
colours = np.random.uniform(0,255, (type_count, 3))

pygame.init()

screen = pygame.display.set_mode((screen_width,screen_height))

running = True

# Initialize arrays with random values

positions = np.column_stack([
    np.random.uniform(0, world_width, n),
    np.random.uniform(0, world_height, n)
])
# print(positions)

# Initialize types matrix

types = np.random.randint(0, type_count, n)
print(types)

# velocities = np.zeros((n, 2))

velocities = np.column_stack([
    np.random.uniform(-1, 1, n),
    np.random.uniform(-1, 1, n)
])

# Initialize the coolest sounding array name ever

force_matrix = np.random.uniform(-1, 1, (type_count, type_count))

print(force_matrix)

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
        camera[0]/2,
        camera[1]/2,
        world_width,
        world_height
    ])

    # Clamp particle positions
    positions[:, 0] = np.clip(positions[:, 0], r, world_width - r)
    positions[:, 1] = np.clip(positions[:, 1], r, world_height - r)

    # Draw particles
    for i, p in enumerate(positions):
        position = (
            int(p[0] + camera[0]/2),
            int(p[1] + camera[1]/2)
        )

        pygame.draw.circle(screen, colours[types[i]-1], position, r)

    # Particle interactions (where it all goes wrong)
    for i, p in enumerate(positions):
        for _i, _p in enumerate(positions):
            diff_vect = np.array([p[0], p[1]]) - [_p[0], _p[1]]
            diff = np.linalg.norm(diff_vect)
            # print(diff)
            if diff == 0:
                continue
            if not max_dist <= diff and not min_dist >= diff:
                A = force_matrix[types[i]][types[_i]]
                # print(A)
                X = max_dist
                N = min_dist
                R = diff

                force = A * ((X/2 - abs(X/2 - (R - N)))/(X/2)) * (diff_vect / diff)
                # print(force)

                # print(force)
                _p[0] += force[0]
                _p[1] += force[1]

    # Update particle positions
    positions += velocities

    # Slightly dampen velocities over time
    velocities *= 0.995

    # Update screen
    pygame.display.update()
    clock.tick(60)

pygame.quit()
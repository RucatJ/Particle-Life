import pygame
import numpy as np

world_width = 500
world_height = 500

screen_width = 700
screen_height = 700

# Interaction limits
max_dist = 250
min_dist = 5

camera = [world_width/2, world_height/2]

n = 200
background_colour = (20,20,40)
world_colour = (40, 40, 80,)
r = 3

type_count = 8
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
    np.random.randint(0, type_count, n)
])

print(particles)

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
    particles[:, 0] = np.clip(particles[:, 0], r, world_width - r)
    particles[:, 1] = np.clip(particles[:, 1], r, world_height - r)

    # Draw particles
    for p in particles:
        # print(p, camera)
        position = (
            int(p[0] + camera[0]/2),
            int(p[1] + camera[1]/2)
        )

        pygame.draw.circle(screen, colours[int(p[4])-1], position, r)
        pygame.draw.circle(screen, (255, 255, 255), camera, 10)

    # Particle interactions (where it all goes wrong)
    for p in particles:
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

            _p[0] += force[0]
            _p[1] += force[1]

    # Update particle positions
    particles[:, 0] += particles[:, 2]
    particles[:, 1] += particles[:, 3]

    # Slightly dampen velocities over time
    particles[:, 2] *= 0.995
    particles[:, 3] *= 0.995

    # Update screen
    pygame.display.update()
    clock.tick(60)

pygame.quit()
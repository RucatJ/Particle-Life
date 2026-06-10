import pygame
import numpy as np
import pyopencl as cl

platform = cl.get_platforms()[0]
device = platform.get_devices()[0]
ctx = cl.Context([device])
queue = cl.CommandQueue(ctx)

seed = input("Select seed: ")
if not seed:
    seed = np.random.randint(0, 999999999)
else:
    try:
        seed = int(seed)
    except ValueError:
        print("That's not an integer")
        quit()

print(f"Seed: {seed}")
np.random.seed(seed)

# list things
for p in cl.get_platforms():
    print(p.name)
    for d in p.get_devices():
        print("    " + d.name)

print(device.name)

world_width = 1200
world_height = 1000

screen_width = 1300
screen_height = 1100

# Interaction limits
max_dist = 120
min_dist = 4
density_limit = 0.2

camera = [(screen_width - world_width) / 2, (screen_height - world_height) / 2]

n = 6000
background_colour = (20,20,40)
world_colour = (40, 40, 80,)
r = 1
force_scale = 0.01

type_count = 12
colours = np.random.uniform(0,255, (type_count, 3))

pygame.init()

screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption("Epic Simulation :)")
font = pygame.font.SysFont("timesnewroman", 18)

running = True

# Initialize the coolest sounding array name ever

force_matrix = np.random.uniform(-1, 1, (type_count, type_count))
print(force_matrix)

# print(force_matrix)

# Initialize all particles

positions = np.column_stack([
    np.random.uniform(0, world_width, n),
    np.random.uniform(0, world_height, n)
])

# velocities = np.column_stack([
#     np.random.uniform(-1, 1, n),
#     np.random.uniform(-1, 1, n)
# ])

velocities = np.zeros((n, 2))

types = np.random.randint(0, type_count, n)

cell = np.zeros((n, 2))

# print(cell)

clock = pygame.time.Clock()

#
# SETUP PYOPENCL STUFF
#

pos32 = positions.astype(np.float32)
vel32 = velocities.astype(np.float32)
types32 = types.astype(np.int32)
fm32 = force_matrix.astype(np.float32).flatten()

# Create buffer for variables

# The mf variable just has all the flags (classes) such as cl.mem_flags.READ_ONLY now becomes mf.READ_ONLY
mf = cl.mem_flags

pos_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=pos32)
types_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=types32)
fm_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=fm32)
vel_buf = cl.Buffer(ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=vel32)

kernel_code = open("kernel.c", "r").read()

program = cl.Program(ctx, kernel_code).build()
kernel = cl.Kernel(program, "update")

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

        pygame.draw.circle(screen, colours[int(types[i])], position, r)

    max_dist_sq = max_dist**2
    min_dist_sq = min_dist**2

    # Particle interactions (where it all goes wrong)

    kernel(
        queue,
        (n,),
        None,
        pos_buf,
        vel_buf,
        types_buf,
        fm_buf,
        np.int32(n),
        np.float32(world_width),
        np.float32(world_height),
        np.float32(max_dist_sq),
        np.float32(min_dist_sq),
        np.float32(max_dist),
        np.float32(min_dist),
        np.int32(type_count),
        np.float32(force_scale),
        np.float32(density_limit)
    )

    cl.enqueue_copy(queue, vel32, vel_buf)
    queue.finish()
    velocities = vel32

    # for i, p in enumerate(positions):
    #     deltas = positions - positions[i]
    #     dx = deltas[:, 0]
    #     dy = deltas[:, 1]
    #
    #     dx = np.where(dx > world_width / 2, dx - world_width, dx)
    #     dx = np.where(dx < -world_width / 2, dx + world_width, dx)
    #     dy = np.where(dy > world_height / 2, dy - world_height, dy)
    #     dy = np.where(dy < -world_height / 2, dy + world_height, dy)
    #
    #     sq_dists = dx**2 + dy**2
    #     dists = np.sqrt(np.maximum(sq_dists, 1e-10))
    #
    #     lr_mask = (sq_dists >= min_dist_sq) & (sq_dists <= max_dist_sq)
    #     sr_mask = (sq_dists < min_dist_sq) & (sq_dists > 0)
    #
    #     forces = np.zeros(n)
    #     d = dists[lr_mask]
    #     forces[lr_mask] = force_matrix[types[i], types][lr_mask] * ((max_dist/2 - np.abs(max_dist/2 - (d - min_dist))) / (max_dist/2))
    #     forces[sr_mask] = (dists[sr_mask] - min_dist) * 5
    #
    #     norm_x = dx / dists
    #     norm_y = dy / dists
    #
    #     fx, fy =  np.sum(forces * norm_x), np.sum(forces * norm_y)
    #
    #     velocities[i][0] +=  fx * force_scale
    #     velocities[i][1] +=  fy * force_scale

    # Slightly dampen velocities over time
    velocities[:, 0] *= 0.8
    velocities[:, 1] *= 0.8

    vel32 = velocities.astype(np.float32)
    cl.enqueue_copy(queue, vel_buf, vel32)

    # Update particle positions
    positions[:, 0] += velocities[:, 0]
    positions[:, 1] += velocities[:, 1]

    pos32 = positions.astype(np.float32)
    cl.enqueue_copy(queue, pos_buf, pos32)

    fps = round(clock.get_fps())
    stats_text = font.render(f"FPS: {str(fps)} Seed: {seed}", True, (255,255,255))

    screen.blit(stats_text, (5, 5))

    # Update screen
    pygame.display.update()
    clock.tick(30)

pygame.quit()
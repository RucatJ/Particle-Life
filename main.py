import pygame

pygame.init()

screen = pygame.display.set_mode((600,400))

running = True

# Running loop
while running:
    # Check for events
    for event in pygame.event.get():
        # Check for quit
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
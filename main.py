
import  pygame
from grille import grid, cell_size, offset_x, offset_y, draw_grid
from ClasseBus import Bus, draw_bus , draw_image,get_rect, collides , in_bounds
from lecture import lire_carte

pygame.init()

WIDTH = 768
HEIGHT = 644

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BusJam")

background = pygame.image.load("Assets/image.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

UP = "U"
LEFT = "L"
RIGHT = "R"
DOWN = "D"

bus_images = {
    0: pygame.image.load("Assets/bus2.png").convert_alpha(),
    1: pygame.image.load("Assets/bus4.png").convert_alpha(),
    2: pygame.image.load("Assets/bus6.png").convert_alpha(),
    3: pygame.image.load("Assets/bus8.png").convert_alpha(),
    4: pygame.image.load("Assets/bus10.png").convert_alpha(),
    5: pygame.image.load("Assets/imageTransp.png").convert_alpha()
}

for key in bus_images:
    bus_images[key] = pygame.transform.scale(bus_images[key], (cell_size, cell_size))

buses, personnages, taille_parking = lire_carte("cartes/carte0", bus_images)

grid = [[0]*taille_parking for _ in range(taille_parking)]
print(buses)
print(personnages)
print(taille_parking)

running = True
show_grid = True

while running:

    screen.blit(background, (0, 0))

    if show_grid:
        draw_grid(screen, grid, cell_size, offset_x, offset_y)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_g:
                show_grid = not show_grid

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            for b in buses:
                rect = get_rect(b, cell_size, offset_x, offset_y)

                if rect.collidepoint(mouse_pos):
                    b.dragging = True
                    b.offset_x = mouse_pos[0] - rect.x
                    b.offset_y = mouse_pos[1] - rect.y

        if event.type == pygame.MOUSEBUTTONUP:
            for b in buses:
                b.dragging = False

    mouse_pos = pygame.mouse.get_pos()

    for b in buses:
        if b.dragging:

            old_x, old_y = b.x, b.y

            if b.direction in ["L", "R"]:
                b.x = (mouse_pos[0] - b.offset_x - offset_x) // cell_size
            else:
                b.y = (mouse_pos[1] - b.offset_y - offset_y) // cell_size

            if collides(b, buses) or not in_bounds(b, grid):
                b.x, b.y = old_x, old_y

    for b in buses:
        if b is not None:
            draw_image(screen, b, cell_size, offset_x, offset_y)

    pygame.display.flip()

pygame.quit()

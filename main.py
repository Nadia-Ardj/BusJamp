
import  pygame
from grille import grid, cell_size, offset_x, offset_y, draw_grid
from ClasseBus import Bus, draw_bus , draw_image,get_rect, collides , in_bounds
from lecture import lire_carte


pygame.init()
buses, personnages, taille_parking = lire_carte("cartes/carte0.txt" , bus_images)
WIDTH = 768
HEIGHT = 644
grid = [[0]*taille_parking for _ in range(taille_parking)]
print(chauffeur)


pygame.display.set_caption("BusJam")
screen = pygame.display.set_mode((WIDTH,HEIGHT))

background = pygame.image.load("Assets/image.png")
background = pygame.transform.scale(background,(WIDTH,HEIGHT))

UP = "U"
LEFT="L"
RIGHT= "R"
DOWN ="D"

bus_images = {
        1: pygame.image.load("Assets/bus2.png").convert_alpha(),
        2: pygame.image.load("Assets/bus4.png").convert_alpha(),
        3: pygame.image.load("Assets/bus6.png").convert_alpha(),
        4: pygame.image.load("Assets/bus8.png").convert_alpha(),
        5: pygame.image.load("Assets/bus10.png").convert_alpha()
}
#convert_alpha() --> pour mettre le fond transparent
for key in bus_images:
    bus_images[key] = pygame.transform.scale(
        bus_images[key],
        (cell_size, cell_size))

"""buses = [
        Bus(2, "U", 7, True,bus_images[2], 2, 2),
        Bus(3, "R", 0, True,bus_images[3], 1, 1),
        Bus(2, "L", 1, False,bus_images[2],3, 0)
    ]"""


running = True
show_grid = True
show_bus = True

while running:

    screen.blit(background, (0,0))
    if show_grid:
        draw_grid(screen,grid,cell_size,offset_x ,offset_y)


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running =False

        if event.type == pygame.KEYDOWN:
          if event.key == pygame.K_g:
            show_grid = not show_grid


    for b in buses:
        if show_bus:
            draw_image(screen, b, cell_size, offset_x, offset_y)

    if event.type == pygame.MOUSEBUTTONDOWN:
        mouse_pos = pygame.mouse.get_pos()

        for b in buses:
            rect = get_rect(b, cell_size, offset_x, offset_y)

            if rect.collidepoint(mouse_pos):
                b.dragging = True

                # offset pour éviter saut
                b.offset_x = mouse_pos[0] - rect.x
                b.offset_y = mouse_pos[1] - rect.y

    if event.type == pygame.MOUSEBUTTONUP:
        for b in chauffeur:
            b.dragging = False

    mouse_pos = pygame.mouse.get_pos()

    for b in buses:
        if b.dragging:

            old_x, old_y = b.x, b.y

            if b.direction in ["L", "R"]:
                new_x = (mouse_pos[0] - b.offset_x - offset_x) // cell_size    # - offset_x -->enlève le décalage de la grille
                b.x = new_x                                                    # - b.offset_x -->enlève le décalage du clic
            else:
                new_y = (mouse_pos[1] - b.offset_y - offset_y) // cell_size
                b.y = new_y

            # collision
            if collides(b, buses):
                b.x, b.y = old_x, old_y

            # depacement de la grille
            if not in_bounds(b, grid) or collides(b, buses):
                b.x, b.y = old_x, old_y

    pygame.display.flip()



pygame.quit()
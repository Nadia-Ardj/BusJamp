
import  pygame
from grille import grid, cell_size, offset_x, offset_y, draw_grid
from ClasseBus import Bus, draw_bus

pygame.init()
WIDTH = 768
HEIGHT = 644

bus_images = {
    1: pygame.image.load("Assets/bus2.png"),
    2: pygame.image.load("Assets/bus4.png"),
    3: pygame.image.load("Assets/bus6.png"),
    4: pygame.image.load("Assets/bus8.png"),
    5: pygame.image.load("Assets/bus10.png"),
}
UP = "U"
LEFT="L"
RIGHT= "R"
DOWN ="D"


buses = [
        Bus(2, "U", 7, True, 2, 2),
        Bus(3, "R", 0, True, 1, 1),
        Bus(2, "L", 1, False, 3, 0)
    ]
pygame.display.set_caption("BusJam")
screen = pygame.display.set_mode((WIDTH,HEIGHT))

background = pygame.image.load("Assets/image.png")
background = pygame.transform.scale(background,(WIDTH,HEIGHT))

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
            draw_bus(screen, b, cell_size, offset_x, offset_y)


    pygame.display.flip()



pygame.quit()
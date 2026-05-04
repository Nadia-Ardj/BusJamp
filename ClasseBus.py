
import pygame
from grille import grid, cell_size, offset_x, offset_y, draw_grid

COLORS = {
    0:    (220, 50, 50), #red
    1:   (50, 100, 220), #blue
    2:  (50, 180, 100), #green
    3: (240, 200, 50), #yellow
    4: (255, 140, 0),  #orange
    5: (160, 90, 200), #purple
    6:   (255, 120, 180), #pink
    7:   (50, 200, 200),  #cyan
    8: (149, 165, 166), #gris clair
    9:(155, 89, 182)    #violet
}

#colorer le fond noir par une couleur
def replace_black_with_color(image, new_color):

    image = image.convert_alpha()
    width, height = image.get_size()

    for x in range(width):
        for y in range(height):

            if image.get_at((x, y))[:3] == (0, 0, 0):
                image.set_at((x, y), new_color)

    return image


class Bus:
        def __init__(self, taille: int, direction: str, couleur: int, image , x: int, y: int , visite: bool, charge: int, capacite: int):
            self.taille = taille
            self.direction = direction  # U, D, L, R
            self.couleur =  COLORS[couleur]
            self.x = x
            self.y = y
            # image coloré une seul fois :
            self.image = replace_black_with_color(image, self.couleur)
            self.dragging = False
            self.offset_x = 0
            self.offset_y = 0
            self.visite = visite
            self.charge = charge
            self.capacite = capacite


        def __repr__(self):
            return f"Bus(taille={self.taille}, direction='{self.direction}', couleur={self.couleur}, chauffeur={self.chauffeur}, x={self.x}, y={self.y},visite={self.visite}, charge={self.charge})"



def draw_bus(screen,  bus, cell_size, offset_x, offset_y):

            for i in range(bus.taille):

                if bus.direction in ["L", "R"]:
                    x = bus.x + i
                    y = bus.y
                else:
                    x = bus.x
                    y = bus.y + i

                rect = pygame.Rect(
                    offset_x + x * cell_size,
                    offset_y + y * cell_size,
                    cell_size,
                    cell_size
                )
                pygame.draw.rect(screen, bus.couleur, rect)

def draw_image(screen, bus, cell_size, offset_x, offset_y):

    image = bus.image

    # rotation selon direction
    if bus.direction == "U":
        image = pygame.transform.rotate(image, 90)
    elif bus.direction == "D":
        image = pygame.transform.rotate(image, -90)
    elif bus.direction == "L":
        image = pygame.transform.rotate(image, 180)

    # resize après rotation
    if bus.direction in ["L", "R"]:
        size = (bus.taille * cell_size, cell_size)
    else:
        size = (cell_size, bus.taille * cell_size)

    image = pygame.transform.scale(image, size)

    screen.blit(image, (offset_x + bus.x * cell_size,
                        offset_y + bus.y * cell_size))

def deplacement_bus(screen, bus, cell_size, offset_x,offset_y):
    for i in  range(bus.taille):
        if bus.direction == "U":
           pygame.MOUSEWHEEL()

    old_x, old_y = b.x, b.y

    if b.direction in ["L", "R"]:
        b.x = new_x
    else:
        b.y = new_y

    if not in_bounds(b, grid) or collides(b, buses):
        b.x, b.y = old_x, old_y


def get_rect(bus, cell_size, offset_x, offset_y):

    if bus.direction in ["L", "R"]:
        width = bus.taille * cell_size
        height = cell_size
    else:
        width = cell_size
        height = bus.taille * cell_size

    return pygame.Rect(
        offset_x + bus.x * cell_size,
        offset_y + bus.y * cell_size,
        width,
        height
    )
#fonction qui récupére les cases d'un bus :
def get_cells(bus):
    cells = []

    for i in range(bus.taille):
        if bus.direction in ["L", "R"]:
            x = bus.x + i
            y = bus.y
        else:
            x = bus.x
            y = bus.y + i

        cells.append((x, y))

    return cells

#la collision avec les autres bus:
def collides(bus, buses):
    my_cells = get_cells(bus)

    for other in buses:
        if other == bus:
            continue

        other_cells = get_cells(other)

        for cell in my_cells:
            if cell in other_cells:
                return True

    return False


#bloquer les bords de la grille :
def in_bounds(bus, grid):
    for (x, y) in get_cells(bus):
        if x < 0 or y < 0:
            return False
        if y >= len(grid) or x >= len(grid[0]):
            return False
    return True






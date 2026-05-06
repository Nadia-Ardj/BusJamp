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
    9:(155, 89, 182),    #violet
    10:(0, 0, 0)      #invisible pour les buses XXX
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
    def __init__(self, taille: int, direction: str, couleur: int, image, x: int, y: int, visite: bool, charge: int,
                 capacite: int):
        self.taille = taille
        self.direction = direction  # U, D, L, R
        self.couleur_id = couleur
        self.couleur = COLORS[couleur]
        self.x = x
        self.y = y
        # image coloré une seul fois :
        self.image = replace_black_with_color(image, self.couleur)

        self.offset_x = 0
        self.offset_y = 0

        self.visite = visite
        self.charge = charge
        self.capacite = capacite
        self.dragging = False

        self.target_x = self.x
        self.target_y = self.y

        self.speed = 3
        self.moving = False

    def __repr__(self):
        return f"Bus(taille={self.taille}, direction='{self.direction}', couleur={self.couleur},  x={self.x}, y={self.y},visite={self.visite}, charge={self.charge})"

#---desiner les bus ----#

#calculer précisément la zone rectangulaire du bus
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

#dessiner le bus avec son image
def draw_image(screen, bus, cell_size, offset_x, offset_y):
    # 1. Obtenir le rectangle de destination exact grâce à get_rect
    rect_destination = get_rect(bus, cell_size, offset_x, offset_y)

    image = bus.image

    # rotation selon direction
    if bus.direction == "U":
        image = pygame.transform.rotate(image, 90)
    elif bus.direction == "D":
        image = pygame.transform.rotate(image, -90)
    elif bus.direction == "L":
        image = pygame.transform.rotate(image, 180)
    elif bus.direction == "R":
        image = pygame.transform.rotate(image, 0)  #elle est à droite par défaut


    # 2. On redimensionne l'image du bus pour qu'elle fasse exactement la taille du rectangle
    image = pygame.transform.scale(image, (rect_destination.width, rect_destination.height))

    # 3. On dessine cette image aux bonnes coordonnées
    screen.blit(image, rect_destination)



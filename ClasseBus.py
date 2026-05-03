
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


class Bus:
        def __init__(self, taille: int, direction: str, color_id: int, chauffeur: bool, x: int, y: int):
            self.taille = taille
            self.direction = direction  # U, D, L, R
            self.couleur =  COLORS[color_id]
            self.chauffeur = chauffeur
            self.x = x
            self.y = y

        def __repr__(self):
            return f"Bus(taille={self.taille}, direction='{self.direction}', couleur={self.couleur}, chauffeur={self.chauffeur}, x={self.x}, y={self.y})"



def draw_bus(screen,  bus, cell_size, offset_x, offset_y):

            for i in range(bus.taille):

                if bus.direction == 'L' or  bus.direction == 'R':
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








"""bus = Bus(
    x=2,
    y=3,
    capacity=3,
    emplacement="H",
    direction="L",
    color_id=0
)"""
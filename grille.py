import pygame
rows,cols = 4,6
cell_size = 30


def create_grid(rows, cols):
    return [[0 for _ in range(cols)] for _ in range(rows)]

grid = create_grid(rows, cols)
offset_x = 150
offset_y = 300
def draw_grid(screen, grid, cell_size,offset_x,offset_y):
    for y in range(len(grid)):
        for x in range(len(grid[0])):
            rect = pygame.Rect(offset_x + x * cell_size,
                               offset_y + y * cell_size,
                               cell_size,
                               cell_size)
            pygame.draw.rect(screen, (200, 200, 200), rect, 1)  # contour


def draw_parking(screen, parking, taille_parking, parking_x, parking_y, cell_size):
    """
    Dessine la zone de parking en haut et les bus qui y sont garés
    """
    for i in range(taille_parking):
        # 10 pixels d'espace entre chaque place de parking
        place_x = parking_x + i * (cell_size + 10)
        place_y = parking_y

        # 1. Dessiner le contour de la place vide
        rect_place = pygame.Rect(place_x, place_y, cell_size, cell_size)
        pygame.draw.rect(screen, (100, 100, 100), rect_place, 2)

        # 2. Dessiner le bus s'il y en a un
        bus_garé = parking[i]
        if bus_garé is not None:
            image_bus = bus_garé.image

            # Rotation vers le haut "U" (90 degrés)
            image_bus = pygame.transform.rotate(image_bus, 90)
            image_bus = pygame.transform.scale(image_bus, (cell_size, cell_size))

            screen.blit(image_bus, (place_x, place_y))

            # --- Affichage de la jauge (Dessinée 5 pixels SOUS le bus) ---
            font = pygame.font.SysFont("Arial", 12, bold=True)
            texte_charge = font.render(f"{bus_garé.charge}/{bus_garé.capacite}", True, (255, 255, 255))
            # place_y + cell_size + 5 place le texte juste sous le bus
            screen.blit(texte_charge, (place_x + (cell_size // 4), place_y + cell_size + 5))


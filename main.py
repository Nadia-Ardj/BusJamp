import  pygame
from grille import grid, cell_size, offset_x, offset_y, draw_grid, draw_parking
from ClasseBus import Bus , draw_image,get_rect
from lecture import lire_carte, est_jouable, deplacer_bus, monter, liberer_bus
from PassagerVisuel import PassagerVisuel, draw_file_attente

pygame.init()

WIDTH = 668
HEIGHT = 744

#Calculer dynamiquement la taille de la grille chargée
rows = len(grid)        # Nombre de lignes réelles
cols = len(grid[0])     # Nombre de colonnes réelles
offset_x = (WIDTH  - cols * cell_size) // 2
offset_y = (HEIGHT - rows * cell_size) // 2

# --- 1. Positionnement du Parking (Tout en haut) ---
parking_x = offset_x  # Aligné horizontalement avec la grille
parking_y = 210        # 210 pixels du haut de l'écran
parking_cell_size = cell_size

# --- 2. Ajustement de la Grille (En dessous du parking) ---
# On décale la grille vers le bas pour laisser de la place au parking et à ses jauges
# (Hauteur du parking + 60 pixels d'espace de sécurité ( l'ecart entre les deux parkings)

offset_y = parking_y + parking_cell_size + 60

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

buses, personnages, taille_parking, grid = lire_carte("cartes/carte0", bus_images, cell_size)
parking = [None] * taille_parking


print(buses)
print(personnages)
print(taille_parking)

#----
# ---pposition de la file d'attente des personnages ( à droite du parking) ---
file_personnages_x = parking_x + (taille_parking * (cell_size + 10)) + 40
file_personnages_y = parking_y + (cell_size // 2)

#liste pour suivre les passagers en train de marcher : [(PassagerVisuel, Bus_Cible), ...]
passagers_en_marche = []


running = True
show_grid = True

while running:

    screen.blit(background, (0, 0))

    # -------------

    #1. Dessiner la grille de jeu principale
    if show_grid:
        draw_grid(screen, grid, cell_size, offset_x, offset_y)

    #2. Dessiner la zone de parking et ses bus garés
    draw_parking(screen, parking, taille_parking, parking_x, parking_y, cell_size)

    #3. Dessiner la file d'attente des personnages qui attendent
    draw_file_attente(screen, personnages, file_personnages_x, file_personnages_y, cell_size)

    # 4. Gérer la logique de départ de la file (crée un passager visuel)
    # On n'appelle 'monter' que si aucun passager n'est déjà en train de marcher (un par un)
    if len(passagers_en_marche) == 0:
        monter(parking, taille_parking, personnages, parking_x, parking_y, cell_size,
               passagers_en_marche, file_personnages_x, file_personnages_y)

    # mettre à jour et dessiner les passagers qui MARCENT vers les bus
    for pv, bus_cible in list(passagers_en_marche):
        pv.update()
        pv.draw(screen)

        # Si le passager touche le bus, il monte physiquement dedans
        if pv.arrive:
            bus_cible.charge += 1
            print(f" Un passager est monté ! Charge : {bus_cible.charge}/{bus_cible.capacite}")
            passagers_en_marche.remove((pv, bus_cible))  # On supprime l'animation

    # 5. Libérer les bus pleins
    liberer_bus(parking, taille_parking)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_g:
                show_grid = not show_grid

# -------------
#Gestion du clic:

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            for b in buses:
                rect = get_rect(b, cell_size, offset_x, offset_y)

                if rect.collidepoint(mouse_pos):
                    if est_jouable(grid, b):
                        # On récupère le statut exact du déplacement
                        statut = deplacer_bus(buses, b, parking, taille_parking, grid)

                        if statut == "gare":
                            print(f" SUCCÈS : Le bus {b.couleur} a rejoint le parking !")
                            print(f"Nombre de bus restants : {len(buses)}")
                        elif statut == "detruit":
                            print(f" NETTOYAGE : L'obstacle/bus décoratif {b.couleur} a été retiré du plateau !")
                            print(f"Nombre de bus restants : {len(buses)}")
                        elif statut == "plein":
                            print(f" IMPOSSIBLE : Le bus {b.couleur} peut sortir, mais le parking est plein.")
                    else:
                        print(f" BLOQUÉ : Le bus {b.couleur} ne peut pas sortir, la voie {b.direction} est obstruée.")

                    break   # un seul bus tritéé par clic



        #-----dessiner le bus ----#
    for b in buses:
        if b is not None:
            draw_image(screen, b, cell_size, offset_x, offset_y)

    pygame.display.flip()

pygame.quit()
import  pygame
from grille import grid, cell_size, offset_x, offset_y, draw_grid, draw_parking
from ClasseBus import Bus , draw_image,get_rect
from lecture import lire_carte, est_jouable, deplacer_bus, monter, liberer_bus, vider_emplacement_bus
from PassagerVisuel import PassagerVisuel, draw_file_attente

pygame.init()
pygame.mixer.init()    #activer les songs


# --- Chargement de la musique de fond ---
try:
    pygame.mixer.music.load("Song/musique_fond.ogg")
    pygame.mixer.music.set_volume(0.2) # Volume
    pygame.mixer.music.play(-1) # pour que la musique tourne en boucle infinie
except pygame.error as e:
    print(f"Impossible de charger la musique : {e}")

# --- Chargement des songs de bruitage  ---
try:
    son_collision = pygame.mixer.Sound("Song/collision_bus.ogg")
    son_deplacement = pygame.mixer.Sound("Song/bus_parti_vers_parking.ogg")
    son_chargement = pygame.mixer.Sound("Song/passager_monté.ogg")
    son_plein = pygame.mixer.Sound("Song/bus_parti.ogg")
    son_victoire = pygame.mixer.Sound("Song/victoire.ogg")
    son_echec = pygame.mixer.Sound("Song/echec.ogg")

    #ajusteer le volume
    son_collision.set_volume(0.5)
    son_deplacement.set_volume(0.6)
    son_chargement.set_volume(0.5)
    son_plein.set_volume(0.6)
    son_victoire.set_volume(0.7)
    son_echec.set_volume(0.7)

except pygame.error as e:
    print(f"Erreur lors du chargement des song : {e}")

    son_collision = None
    son_deplacement = None
    son_chargement = None
    son_plein = None
    son_victoire = None
    son_echec = None

"""# ------
print("--- VÉRIFICATION DES SONS ---")
print("Collision chargé :", son_collision is not None)
print("Déplacement chargé :", son_deplacement is not None)
print("chargement :", son_chargement is not None)
print("Victoire chargé :", son_victoire is not None)
print("Échec chargé :", son_echec is not None)
print("est plein :", son_plein is not None)
print("-----------------------------")"""

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

#for key in bus_images:
#    bus_images[key] = pygame.transform.scale(bus_images[key], (cell_size, cell_size))  --> la redimension sera faiteavec la fctn draw_image et lire_carte

buses, personnages, taille_parking, grid = lire_carte("cartes/carte2", bus_images, cell_size)
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
game_over = False
victoire = False
son_fin_joue = False   #pour eviter que le song tourne en boucle
frames_bloquees = 0

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
    #on n'appelle 'monter' que si aucun passager n'est déjà en train de marcher (un par un)
    if len(passagers_en_marche) == 0:
        monter(parking, taille_parking, personnages, parking_x, parking_y, cell_size,
               passagers_en_marche, file_personnages_x, file_personnages_y)

    #mettre à jour et dessiner les passagers qui MARCENT vers les bus
    for pv, bus_cible in list(passagers_en_marche):
        pv.update()
        pv.draw(screen)

        #si le passager touchee le bus, il monte dedans
        if pv.arrive:
            bus_cible.charge += 1

            # --- JOUER LE SON DE CHARGEMENTT ---
            if son_chargement:
                son_chargement.play()
            print(f" Un passager est monté ! Charge : {bus_cible.charge}/{bus_cible.capacite}")
            passagers_en_marche.remove((pv, bus_cible))  #on supprime l'animation

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
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_g:
                show_grid = not show_grid


        if event.type == pygame.MOUSEBUTTONDOWN:
            if victoire or game_over:
                continue  # pour desactiver les clics si la partie est finie
            mouse_pos = pygame.mouse.get_pos()

            for b in list(buses):
                rect = get_rect(b, cell_size, offset_x, offset_y)

                if rect.collidepoint(mouse_pos):
                    if est_jouable(grid, b):
                        if b.capacite == 10 :
                            print(f" NETTOYAGE : L'obstacle/bus décoratif {b.couleur} a été retiré du plateau !")
                            # on libere les cases occupées par ce bus sur la grille
                            vider_emplacement_bus(grid, b)
                            buses.remove(b)

                            #on ajoute le song du deplacement
                            if son_deplacement:
                              son_deplacement.play()



                        else:
                            print(f"c'est un bus normal{b.couleur}")
                            if son_deplacement:
                              son_deplacement.play()



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
                        # --- JOUER LE SONGG DE COLLISION  ---
                        if son_collision:
                            son_collision.play()
                        print(f" BLOQUÉ : Le bus {b.couleur} ne peut pas sortir, la voie {b.direction} est obstruée.")
                        print(f" BLOQUÉ : Le bus {b.couleur} ne peut pas sortir, la voie {b.direction} est obstruée.")

                    break   # un seul bus tritéé par clic

    # ---déction de la victoire ---
    if len(buses) == 0 and len(personnages) == 0 and len(passagers_en_marche) == 0 and all(p is None for p in parking):

            victoire = True
            if not son_fin_joue:
                pygame.mixer.music.stop()  # on coupe la musique de fond
                if son_victoire:
                    son_victoire.play()  # on joue le son de vecxtoire
                son_fin_joue = True

# --- d"tecion de l'echec  ---
    #on vérifie si le parking est plein
   # parking_plein = all(p is not None for p in parking)

    #on regarde la couleur du tout premier personnage dans la file d'attente
   # prochain_passager_couleur = personnages[0] if len(personnages) > 0 else None

    #on vérifie si ce prochain passager a son bus de la même couleur dans le parking
   # un_bus_peut_charger = False
   # if prochain_passager_couleur is not None:
     #   for p in parking:
      #      if p is not None and p.couleur == prochain_passager_couleur:
                #on vérifie aussi que ce bus n'est pas déjà plein et sur le point de partir
    #            if p.charge < p.capacite:
  #                  un_bus_peut_charger = True
  #                  break

        #le GameOver ne se déclenche que si :
        # -le parking est plein
        # -le prochain passager ne peut monter nulle part
        # -aucun passager n'est en train de marcher vers un bus
        # -il reste encore des bus sur la grille
  #      if parking_plein and not un_bus_peut_charger and len(passagers_en_marche) == 0 and len(buses) != 0:
     #       game_over = True
   #         if not son_fin_joue:
  #              pygame.mixer.music.stop()  #on coupe la musique
#                if son_echec:
 #                   son_echec.play()  #son de défaite"""
#             son_fin_joue = True"""

#----------
#---------ici on utilisé l'IA pour nous aider , parce qu'on a fait cette fonction au dessus mais elle déclenche vite la défaite ---------
#----------

# --- détection de l'échec ---
    parking_plein = all(p is not None for p in parking)
    prochain_passager_couleur = personnages[0] if len(personnages) > 0 else None

    un_bus_peut_charger = False
    if prochain_passager_couleur is not None:
        for p in parking:
            if p is not None and p.couleur == prochain_passager_couleur:
                if p.charge < p.capacite:
                    un_bus_peut_charger = True
                    break

    #si on détecte une situation de blocage théorique
    if parking_plein and not un_bus_peut_charger and len(passagers_en_marche) == 0 and len(buses) != 0:
        #on incrémente le compteur à chaque frame où on est bloqué
        frames_bloquees += 1
    else:
        # Dès que la situation change on remet à zéro
        frames_bloquees = 0

    #on ne déclare le GameOver quesi la situation de blocage persiste pendant plus de 60 frames (environ 1 seconde)
    if frames_bloquees > 60:
        game_over = True
        if not son_fin_joue:
            pygame.mixer.music.stop()  #on coupe la musique
            if son_echec:
                son_echec.play()  #son de défaite
            son_fin_joue = True

#-----------------


    #-----dessiner le bus ----#
    for b in buses:
        if b is not None:
            draw_image(screen, b, cell_size, offset_x, offset_y)

    # --- AFFICHAGE DES éCRANS DE FIN ---
    if victoire:
            # création d'une police d'écriture
            font_fin = pygame.font.SysFont("Arial", 50, bold=True)
            texte = font_fin.render("VICTOIRE !", True, (46, 204, 113))  # Vert
            #centrer le texte à l'écran
            text_rect = texte.get_rect(center=(WIDTH // 2, HEIGHT // 2))

            # faire un fond sombre derrière le texte pour mieux le voir
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))  # un nooir transparent
            screen.blit(overlay, (0, 0))
            screen.blit(texte, text_rect)



    elif game_over:

        font_fin = pygame.font.SysFont("Arial", 50, bold=True)
        texte = font_fin.render("GAME OVER", True, (231, 76, 60))
        text_rect = texte.get_rect(center=(WIDTH // 2, HEIGHT // 2))

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        screen.blit(texte, text_rect)



    pygame.display.flip()

pygame.quit()
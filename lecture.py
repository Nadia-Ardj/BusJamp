import pygame
from ClasseBus import Bus, replace_black_with_color

COLORS = {
    0:  (220, 50,  50),   # red
    1:  (50,  100, 220),  # blue
    2:  (50,  180, 100),  # green
    3:  (240, 200, 50),   # yellow
    4:  (255, 140, 0),    # orange
    5:  (160, 90,  200),  # purple
    6:  (255, 120, 180),  # pink
    7:  (50,  200, 200),  # cyan
    8:  (149, 165, 166),  # gris clair
    9:  (155, 89,  182),  # violet
    10: (0,   0,   0),    # invisible pour les cases XXX
}


def lire_carte(carte, bus_images, cell_size):
    """
    Lit un fichier de carte BusJam et retourne les buses, personnages,
    taille du parking et la grille logique.

    Format du fichier :
      - ligne 0    : taille_parking (entier)
      - lignes 1..N-1 : grille, chaque case = 3 chars  (capacité, direction, couleur_id)
                        ou "XXX " pour une case vide
      - ligne N    : file d'attente des personnages (un chiffre par personnage)
    """

    with open(carte, "r", encoding="utf-8") as flux:
        lignes = [ligne.strip() for ligne in flux if ligne.strip()]

    taille_parking = int(lignes[0])
    personnages = [int(p) for p in lignes[-1]]  # convertit en int pour comparer avec couleur_id
    lignes = lignes[1:-1]  # retire première et dernière ligne

    # --- Étape 1 : construire la grille brute de Bus ---
    grid = []

    for i, ligne_str in enumerate(lignes):
        ligne_row = []

        for c in range(0, len(ligne_str), 4):   #  step=4 explicite
            cell = ligne_str[c:c + 3]            # compare les 3 chars

            if cell != "XXX":
                capacite_brute  = int(ligne_str[c])
                direction = ligne_str[c + 1]
                couleur   = int(ligne_str[c + 2])
                # --- Si c'est 0, la vraie capacité logique est 10 ---
                if capacite_brute == 0 and direction !="X" :    #on transforme que si c'est un décor
                    capacite = 10
                else:
                    capacite = capacite_brute

                # --- SÉLECTION DE L'IMAGE CORRESPONDANTE ---
                # capacité 2  -> (2 // 2) - 1 = 0 (bus2.png, taille 1)
                # capacité 4  -> (4 // 2) - 1 = 1 (bus4.png, taille 2)
                # capacité 6  -> (6 // 2) - 1 = 2 (bus6.png, taille 3)
                # capacité 8  -> (8 // 2) - 1 = 3 (bus8.png, taille 4)
                # capacité 10 -> (10 // 2) - 1 = 4 (bus10.png, taille 5)
                cle_image = (capacite // 2) - 1

                # Récupération de l'image de base
                raw_image = bus_images.get(cle_image, bus_images.get(5))

                # ---
                couleur_rgb = COLORS.get(couleur, (149, 165, 166))

                image = replace_black_with_color(
                    pygame.transform.scale(raw_image, (cell_size, cell_size)),
                    couleur_rgb
                )

                bus = Bus(
                    x=c // 4,   #  x = colonne = c//4
                    y=i,        #  y = ligne   = i
                    capacite=capacite,
                    taille=capacite//2,   
                    direction=direction,
                    couleur=couleur,
                    visite=False,
                    charge=0,
                    image=image,
                )
            else:
                # image vide pour les cases XXX
                dummy_image = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
                dummy_image.fill((0, 0, 0, 0))

                bus = Bus(
                    x=c // 4,
                    y=i,
                    capacite=0,
                    taille=0,
                    direction="X",
                    couleur=10,
                    visite=True,   # marqué visité  : on ne le traitera pas
                    charge=0,
                    image=dummy_image,
                )

            ligne_row.append(bus)
        grid.append(ligne_row)

    # --- Étape 2 : reconstruire la liste des buses logiques ---
    # Un bus multi-cases n'est représenté qu'une seule fois dans `buses`,
    # par sa case de DÉBUT (U→case du haut, D→case du haut, L→case gauche, R→case gauche).

    buses = []

    for i, ligne_row in enumerate(grid):
        for j, bus in enumerate(ligne_row):

            if bus.visite:
                continue

            # Bus de taille 1 (capacite == 0 déjà filtré ; capacite == 2 → 1 seule case)
            if bus.capacite == 2:
                bus.visite = True
                bus.taille = 1
                buses.append(bus)
                continue

            # --- Direction U (référence = case du haut) ---
            if bus.direction == "U":
                k = i
                while (k < len(grid)
                       and grid[k][j].couleur == bus.couleur
                       and grid[k][j].direction == "U" and ((k-i)<bus.taille or bus.capacite==0)):
                    grid[k][j].visite = True
                    k += 1
                bus.taille = k - i          # taille sur bus (case de début)
                buses.append(bus)           # on ajoute bus, pas grid[k-1]

            # --- Direction D  ---
            elif bus.direction == "D":
                k = i
                while (k < len(grid)
                       and grid[k][j].couleur == bus.couleur
                       and grid[k][j].direction == "D" and ((k - i) < bus.taille or bus.capacite == 0)):
                    grid[k][j].visite = True
                    k += 1
                bus.taille = k - i          # corrigé
                buses.append(bus)           # corrigé

            # --- Direction L  ---
            elif bus.direction == "L":
                k = j
                while (k < len(ligne_row)
                       and grid[i][k].couleur == bus.couleur
                       and grid[i][k].direction == "L" and ((k - j) < bus.taille or bus.capacite == 0)):
                    grid[i][k].visite = True
                    k += 1
                bus.taille = k - j          # corrigé
                buses.append(bus)           # corrigé

            # --- Direction R  ---
            elif bus.direction == "R":
                k = j
                while (k < len(ligne_row)
                       and grid[i][k].couleur == bus.couleur
                       and grid[i][k].direction == "R" and ((k - j) < bus.taille or bus.capacite == 0)):
                    grid[i][k].visite = True
                    k += 1
                bus.taille = k - j          #  corrigé
                buses.append(bus)           #  corrigé

    return buses, personnages, taille_parking, grid   #  on retourne aussi grid


# ---------------------------------------------------------------------------
# Fonctions logiques  du jeu
# ---------------------------------------------------------------------------

def est_jouable(grid, bus):
    """Retourne True si le bus peut sortir de la grille sans obstacle."""
    if bus.direction == "U":
        for i in range(bus.y - 1, -1, -1):
            if grid[i][bus.x].direction != "X":
                return False

    elif bus.direction == "D":
        for i in range(bus.y + bus.taille, len(grid)):
            if grid[i][bus.x].direction != "X":
                return False

    elif bus.direction == "L":
        for j in range(bus.x - 1, -1, -1):
            if grid[bus.y][j].direction != "X":
                return False

    elif bus.direction == "R":
        for j in range(bus.x + bus.taille, len(grid[bus.y])):
            if grid[bus.y][j].direction != "X":
                return False

    return True


def parking_libre(parking, taille_parking):
    """Retourne True s'il reste au moins une place vide (None) dans le parking."""
    for i in range(taille_parking):
        if parking[i] is None:
            return True
    return False

#retourner la place dans le parking
def empl_parking(parking, taille_parking):
    """Retourne le premier index  libre dans le parking, ou None."""
    for i in range(taille_parking):
        if parking[i] is None:
            return i
    return None


"""
    Remplace toutes les cases  occupées par le bus 
    par des objets Bus 'vides' (direction 'X', couleur 10).
    """
def vider_emplacement_bus(grid, bus):

    # 1. On détermine la liste des cases (x, y) occupées par ce bus
    cases_a_vider = []

    for i in range(bus.taille):
        if bus.direction in ["L", "R"]:
            cases_a_vider.append((bus.x + i, bus.y))
        elif bus.direction in ["U", "D"]:
            cases_a_vider.append((bus.x, bus.y + i))

    # 2. On remplace chacune de ces cases par un bus "vide"
    for cx, cy in cases_a_vider:
        # On s'assure de ne pas sortir des limites de la grille par sécurité
        if 0 <= cy < len(grid) and 0 <= cx < len(grid[0]):

            # On crée une surface transparente pour la case vide
            dummy_image = pygame.Surface((30, 30), pygame.SRCALPHA)
            dummy_image.fill((0, 0, 0, 0))

            # On écrase l'ancien bus par un bloc de vide "X"
            grid[cy][cx] = Bus(
                x=cx,
                y=cy,
                capacite=0,
                taille=0,
                direction="X",
                couleur=10,
                visite=True,
                charge=0,
                image=dummy_image
            )

"""Déplacer le bus vers le parking et nettoie sa place sur la grille."""

def deplacer_bus(buses, bus, parking, taille_parking, grid):
    """Déplace le bus vers le parking si c'est un vrai bus à charger."""
    # Si le bus est un bus "vide/décoratif" (capacité 0 ou "XXX")
    if bus.capacite == 0 or bus.direction == "X":
        vider_emplacement_bus(grid, bus)
        if bus in buses:
            buses.remove(bus)
        return "detruit"

    # Si c'est un bus qui doit recevoir des passagers
    if parking_libre(parking, taille_parking):
        j = empl_parking(parking, taille_parking)

        # On vide sa place dans la grille de jeu
        vider_emplacement_bus(grid, bus)

        # On l'envoie au parking
        bus.direction = "U"
        parking[j] = bus
        buses.remove(bus)
        return "gare"  # Succès (le bus a été bien placé dans le parking )
    else:
        print(" ÉCHEC : Le parking est complètement plein !")
        return "plein"



def est_plein(bus):
    return bus.capacite == bus.charge

#---tuple RGB en ID numérique :
def obtenir_id_depuis_rgb(rgb_tuple):
    from lecture import COLORS
    for couleur_id, val_rgb in COLORS.items():
        if val_rgb == rgb_tuple:
            return couleur_id
    return None # Non trouvé

#-------
"""
    Vérifie si le premier personnage de la file peut monter dans un bus du parking.
    Si oui, on crée un PassagerVisuel qui va marcher vers le bus.
    """
def monter(parking, taille_parking, personnages, parking_x, parking_y, cell_size, liste_visuels, file_x, file_y):

    if not personnages:
        return

    for i in range(taille_parking):
        p = parking[i]
        if p is not None:
            #print(f" Comparaison : Perso ID={personnages[0]} (type: {type(personnages[0])}) "
                 # f"avec Bus Couleur={p.couleur} (type: {type(p.couleur)})")
            if not est_plein(p):
                # verifier si e premier personnage de la file correspond à la couleur du bus
                # On convertit la couleur RGB du bus en ID numérique avant de comparer
             id_couleur_bus = obtenir_id_depuis_rgb(p.couleur)
             if id_couleur_bus == personnages[0]:
                couleur_id = personnages[0]
                print(f" Couleur {p.couleur} correspondante.")

                # récupérer la couleur RGB correspondante
                from lecture import COLORS
                couleur_rgb = COLORS.get(couleur_id, (255, 255, 255))

                # calcul de la position cible (le centre de la case de parking correspondante)
                place_x = parking_x + i * (cell_size + 10) + (cell_size // 2)
                place_y = parking_y + (cell_size // 2)

                # création du passager animé
                from PassagerVisuel import PassagerVisuel
                nouveau_passager = PassagerVisuel(
                    x_depart=file_x,
                    y_depart=file_y,
                    x_cible=place_x,
                    y_cible=place_y,
                    couleur_id=couleur_id,
                    couleur_rgb=couleur_rgb,
                    vitesse=4
                )

                # ajouter ce passager à la liste des animations en cours
                liste_visuels.append((nouveau_passager, p))  # On lie le passager visuel au bus cible 'p'

                # On retire le personnage de la file d'attente logique immédiatement
                del personnages[0]
                print(f" Passager de couleur {p.couleur} monte. Remplissage du bus : {p.charge}/{p.capacite}")
                return   #on traite un passeger à la fois
            else:
                print(" Pas de correspondance de couleur.")


#------
def liberer_bus(parking, taille_parking):
    """Si un bus est plein, il s'en va du parking et laisse sa place vide """
    for i in range(taille_parking):
        if parking[i] is not None and est_plein(parking[i]):
            print(f" Le bus {parking[i].couleur} est plein et quitte le parking !")
            parking[i] = None # La place redevient libre





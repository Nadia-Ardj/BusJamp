import os
import glob
import pygame
from grille import grid, cell_size, offset_x, offset_y, draw_grid, draw_parking
from ClasseBus import Bus, draw_image, get_rect
from lecture import lire_carte, est_jouable, deplacer_bus, monter, liberer_bus, vider_emplacement_bus
from PassagerVisuel import PassagerVisuel, draw_file_attente
from solveur import SolveurManager

pygame.init()
pygame.mixer.init()

WIDTH  = 668
HEIGHT = 744


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
    5: pygame.image.load("Assets/imageTransp.png").convert_alpha(),
}

# --- Chargement de la musique de fond ---
try:
    pygame.mixer.music.load("Song/musique_fond.ogg")
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1)
except pygame.error as e:
    print(f"Impossible de charger la musique : {e}")

# --- Chargement des songs de bruitage  ---
try:
    son_collision   = pygame.mixer.Sound("Song/collision_bus.ogg")
    son_deplacement = pygame.mixer.Sound("Song/bus_parti_vers_parking.ogg")
    son_chargement  = pygame.mixer.Sound("Song/passager_monté.ogg")
    son_plein       = pygame.mixer.Sound("Song/bus_parti.ogg")
    son_victoire    = pygame.mixer.Sound("Song/victoire.ogg")
    son_echec       = pygame.mixer.Sound("Song/echec.ogg")

    #ajusteer le volume
    son_collision.set_volume(0.5)
    son_deplacement.set_volume(0.6)
    son_chargement.set_volume(0.5)
    son_plein.set_volume(0.6)
    son_victoire.set_volume(0.7)
    son_echec.set_volume(0.7)

except pygame.error as e:
    print(f"Erreur sons : {e}")
    son_collision = son_deplacement = son_chargement = None
    son_plein = son_victoire = son_echec = None

"""# ------
print("--- VÉRIFICATION DES SONS ---")
print("Collision chargé :", son_collision is not None)
print("Déplacement chargé :", son_deplacement is not None)
print("chargement :", son_chargement is not None)
print("Victoire chargé :", son_victoire is not None)
print("Échec chargé :", son_echec is not None)
print("est plein :", son_plein is not None)
print("-----------------------------")"""


# ── Liste des cartes triées ────────────────────────────────────
def lister_cartes(dossier="cartes"):
    fichiers = glob.glob(os.path.join(dossier, "carte*"))
    def numero(p):
        chiffres = ''.join(filter(str.isdigit, os.path.basename(p)))
        return int(chiffres) if chiffres else 0
    return sorted(fichiers, key=numero)

cartes = lister_cartes()
index_niveau = 0

# ── Fonction qui (re)charge un niveau ─────────────────────────
def charger_niveau(chemin):
    global buses, personnages, taille_parking, grid
    global offset_x, offset_y, parking_x, parking_y, parking_cell_size
    global file_personnages_x, file_personnages_y
    global parking, passagers_en_marche, solveur
    global show_grid, game_over, victoire, son_fin_joue, frames_bloquees

    # --- Ajustement de la Grille (En dessous du parking) ---
    # On décale la grille vers le bas pour laisser de la place au parking et à ses jauges
    # (Hauteur du parking + 60 pixels d'espace de sécurité ( l'ecart entre les deux parkings)

    parking_y         = 210     # 210 pixels du haut de l'écran
    parking_cell_size = cell_size

    buses, personnages, taille_parking, grid = lire_carte(chemin, bus_images, cell_size)
    # Calculer dynamiquement la taille de la grille chargée
    rows = len(grid)    # Nombre de lignes réelles
    cols = len(grid[0])        # Nombre de colonnes réelles
    offset_x  = (WIDTH  - cols * cell_size) // 2
    offset_y  = parking_y + parking_cell_size + 60
    parking_x = offset_x   # Aligné horizontalement avec la grille

    parking             = [None] * taille_parking
    passagers_en_marche = []

    file_personnages_x = parking_x + (taille_parking * (cell_size + 10)) + 40
    file_personnages_y = parking_y + (cell_size // 2)

    solveur = SolveurManager(buses, personnages, parking, taille_parking, grid,
                             son_deplacement, son_collision)

    show_grid       = True
    game_over       = False
    victoire        = False
    son_fin_joue    = False
    frames_bloquees = 0

    try:
        pygame.mixer.music.load("Song/musique_fond.ogg")
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play(-1)
    except pygame.error:
        pass

    print(f"\n=== Niveau {index_niveau + 1}/{len(cartes)} : {chemin} ===")


# ── Premier chargement ─────────────────────────────────────────
charger_niveau(cartes[index_niveau])

frames_fin = 0
DELAI_FIN  = 120   # ~2 secondes à 60 fps

running = True

while running:

    screen.blit(background, (0, 0))

    #1. Dessiner la grille de jeu principale
    if show_grid:
        draw_grid(screen, grid, cell_size, offset_x, offset_y)
    # 2. Dessiner la zone de parking et ses bus garés
    draw_parking(screen, parking, taille_parking, parking_x, parking_y, cell_size)

    # 3. Dessiner la file d'attente des personnages qui attendent
    draw_file_attente(screen, personnages, file_personnages_x, file_personnages_y, cell_size)

    # 4. Gérer la logique de départ de la file (crée un passager visuel)
    # on n'appelle 'monter' que si aucun passager n'est déjà en train de marcher (un par un)
    if len(passagers_en_marche) == 0:
        monter(parking, taille_parking, personnages, parking_x, parking_y, cell_size,
               passagers_en_marche, file_personnages_x, file_personnages_y)

    # mettre à jour et dessiner les passagers qui MARCENT vers les bus
    for pv, bus_cible in list(passagers_en_marche):
        pv.update()
        pv.draw(screen)

        # si le passager touchee le bus, il monte dedans
        if pv.arrive:
            bus_cible.charge += 1

            # --- JOUER LE SON DE CHARGEMENTT ---
            if son_chargement:
                son_chargement.play()
            print(f" Un passager est monté ! Charge : {bus_cible.charge}/{bus_cible.capacite}")
            passagers_en_marche.remove((pv, bus_cible))
            # on supprime l'animation

    # 5. Libérer les bus pleins
    liberer_bus(parking, taille_parking)

    solveur.tick(passagers_en_marche, grid, buses, est_jouable)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_g:
                show_grid = not show_grid

            #Indicateur de prochain bus à jouer
            if event.key == pygame.K_h:
                solveur.get_hint()
            if event.key == pygame.K_a:
                solveur.toggle_auto()


        # -------------
        # Gestion du clic:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if victoire or game_over:
                continue # pour desactiver les clics si la partie est finie
            mouse_pos = pygame.mouse.get_pos()

            for b in list(buses):
                rect = get_rect(b, cell_size, offset_x, offset_y)
                if rect.collidepoint(mouse_pos):
                    if est_jouable(grid, b):
                        if b.capacite == 10 and b.couleur == 0:
                            print(f" NETTOYAGE : obstacle {b.couleur} retiré.")
                            # on libere les cases occupées par ce bus sur la grille
                            vider_emplacement_bus(grid, b)
                            buses.remove(b)
                            # on ajoute le song du deplacement
                            if son_deplacement:
                                son_deplacement.play()
                        else:
                            if son_deplacement:
                                son_deplacement.play()
                            solveur.on_clic_bus(b)
                            # On récupère le statut exact du déplacement
                            statut = deplacer_bus(buses, b, parking, taille_parking, grid)
                            if statut == "gare":
                                print(f" Bus {b.couleur} → parking. Restants : {len(buses)}")
                            elif statut == "detruit":
                                print(f" Bus {b.couleur} détruit. Restants : {len(buses)}")
                            elif statut == "plein":
                                print(f" Parking plein, bus {b.couleur} bloqué.")
                    else:
                        # --- JOUER LE SONGG DE COLLISION  ---
                        if son_collision:
                            son_collision.play()
                        print(f" BLOQUÉ : bus {b.couleur}, voie {b.direction} obstruée.")
                    break   # un seul bus tritéé par clic

    # ── Détection victoire ─────────────────────────────────────
    if (len(buses) == 0 and len(personnages) == 0
            and len(passagers_en_marche) == 0
            and all(p is None for p in parking)):
        victoire = True
        if not son_fin_joue:
            pygame.mixer.music.stop() # on coupe la musique de fond
            if son_victoire:
                son_victoire.play()  # on joue le son de vectoire
            son_fin_joue = True
    # --- d"tecion de l'echec  ---
    # on vérifie si le parking est plein
    # parking_plein = all(p is not None for p in parking)

    # on regarde la couleur du tout premier personnage dans la file d'attente
    # prochain_passager_couleur = personnages[0] if len(personnages) > 0 else None

    # on vérifie si ce prochain passager a son bus de la même couleur dans le parking
    # un_bus_peut_charger = False
    # if prochain_passager_couleur is not None:
    #   for p in parking:
    #      if p is not None and p.couleur == prochain_passager_couleur:
    # on vérifie aussi que ce bus n'est pas déjà plein et sur le point de partir
    #            if p.charge < p.capacite:
    #                  un_bus_peut_charger = True
    #                  break

    # le GameOver ne se déclenche que si :
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

    # ----------
    # ---------ici on utilisé l'IA pour nous aider , parce qu'on a fait cette fonction au dessus mais elle déclenche vite la défaite ---------
    # ----------



    # ── Détection de l'échec ────────────────────────────────────
    parking_plein             = all(p is not None for p in parking)
    prochain_passager_couleur = personnages[0] if personnages else None

    un_bus_peut_charger = False
    if prochain_passager_couleur is not None:
        for p in parking:
            if p is not None and p.couleur == prochain_passager_couleur:
                if p.charge < p.capacite:
                    un_bus_peut_charger = True
                    break

    # si on détecte une situation de blocage
    if parking_plein and not un_bus_peut_charger and len(passagers_en_marche) == 0 and len(buses) != 0:
        # on incrémente le compteur à chaque frame où on est bloqué
        frames_bloquees += 1
    else:
        # Dès que la situation change on remet à zéro
        frames_bloquees = 0

    # on ne déclare le GameOver quesi la situation de blocage persiste pendant plus de 60 frames (environ 1 seconde)
    if frames_bloquees > 60:
        game_over = True
        if not son_fin_joue:
            pygame.mixer.music.stop()
            # on coupe la musique
            if son_echec:
                son_echec.play()   #son de défaite
            son_fin_joue = True

    # ── Dessiner les bus ─────────────────────────────────────────
    bus_hint = solveur.bus_du_prochain_coup(buses)
    for b in buses:
        if b is not None:
            draw_image(screen, b, cell_size, offset_x, offset_y)
            if b is bus_hint:
                rect      = get_rect(b, cell_size, offset_x, offset_y)
                epaisseur = 3 if (pygame.time.get_ticks() // 300) % 2 == 0 else 1
                pygame.draw.rect(screen, (255, 255, 255), rect, epaisseur)

    # ── UI (interface de l'utilisateur  ─────────────────────────────────────────────────────
    font_ui = pygame.font.SysFont("Arial", 14)
    screen.blit(font_ui.render(f"Niveau {index_niveau + 1} / {len(cartes)}", True, (255, 220, 50)), (WIDTH - 110, 10))
    if solveur.solution_coups and solveur.hint_idx < len(solveur.solution_coups):
        nb = len(solveur.solution_coups) - solveur.hint_idx
        screen.blit(font_ui.render(f"Coups restants : {nb}", True, (255, 220, 50)), (10, 28))
    if solveur.auto_solve:
        screen.blit(font_ui.render("AUTO-SOLVE  ON", True, (50, 255, 120)), (10, 46))

    # ── Overlay fin de niveau + barre de décompte automatique ──
    if victoire or game_over:
        font_fin = pygame.font.SysFont("Arial", 50, bold=True)
        font_sub = pygame.font.SysFont("Arial", 20)
        overlay  = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        if victoire:
            texte = font_fin.render("VICTOIRE !", True, (46, 204, 113))
        else:
            texte = font_fin.render("GAME OVER",  True, (231, 76, 60))
        screen.blit(texte, texte.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

        # Barre de progression du délai
        frames_fin += 1
        barre_w = int((WIDTH - 80) * min(frames_fin / DELAI_FIN, 1.0))
        pygame.draw.rect(screen, (80, 80, 80),  (40, HEIGHT // 2 + 50, WIDTH - 80, 8))
        couleur_barre = (46, 204, 113) if victoire else (231, 76, 60)
        pygame.draw.rect(screen, couleur_barre, (40, HEIGHT // 2 + 50, barre_w, 8))

        if victoire:
            msg = "Niveau suivant…" if index_niveau + 1 < len(cartes) else "Retour au début…"
        else:
            msg = "On réessaie…"
        sous = font_sub.render(msg, True, (200, 200, 200))
        screen.blit(sous, sous.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80)))

        # Délai écoulé → charger le niveau suivant ou recommencer
        if frames_fin >= DELAI_FIN:
            frames_fin = 0
            if victoire:
                index_niveau = (index_niveau + 1) % len(cartes)
            # game_over : index_niveau inchangé → même carte
            charger_niveau(cartes[index_niveau])

    pygame.display.flip()

pygame.quit()
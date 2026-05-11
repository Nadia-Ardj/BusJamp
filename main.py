import re
import pygame
from grille import grid, cell_size, offset_x, offset_y, draw_grid, draw_parking
from ClasseBus import Bus, draw_image, get_rect
from lecture import lire_carte, est_jouable, deplacer_bus, monter, liberer_bus, vider_emplacement_bus
from PassagerVisuel import PassagerVisuel, draw_file_attente
from solveur import solveur_bfs

pygame.init()
pygame.mixer.init()

# --- Chargement de la musique de fond ---
try:
    pygame.mixer.music.load("Song/musique_fond.ogg")
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1)
except pygame.error as e:
    print(f"Impossible de charger la musique : {e}")

# --- Chargement des sons de bruitage ---
try:
    son_collision   = pygame.mixer.Sound("Song/collision_bus.ogg")
    son_deplacement = pygame.mixer.Sound("Song/bus_parti_vers_parking.ogg")
    son_chargement  = pygame.mixer.Sound("Song/passager_monté.ogg")
    son_plein       = pygame.mixer.Sound("Song/bus_parti.ogg")
    son_victoire    = pygame.mixer.Sound("Song/victoire.ogg")
    son_echec       = pygame.mixer.Sound("Song/echec.ogg")
    son_collision.set_volume(0.5)
    son_deplacement.set_volume(0.6)
    son_chargement.set_volume(0.5)
    son_plein.set_volume(0.6)
    son_victoire.set_volume(0.7)
    son_echec.set_volume(0.7)
except pygame.error as e:
    print(f"Erreur lors du chargement des sons : {e}")
    son_collision = son_deplacement = son_chargement = None
    son_plein = son_victoire = son_echec = None

WIDTH  = 668
HEIGHT = 744

rows   = len(grid)
cols   = len(grid[0])
offset_x = (WIDTH  - cols * cell_size) // 2
offset_y = (HEIGHT - rows * cell_size) // 2

parking_x         = offset_x
parking_y         = 210
parking_cell_size = cell_size
offset_y          = parking_y + parking_cell_size + 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BusJam")

background = pygame.image.load("Assets/image.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

bus_images = {
    0: pygame.image.load("Assets/bus2.png").convert_alpha(),
    1: pygame.image.load("Assets/bus4.png").convert_alpha(),
    2: pygame.image.load("Assets/bus6.png").convert_alpha(),
    3: pygame.image.load("Assets/bus8.png").convert_alpha(),
    4: pygame.image.load("Assets/bus10.png").convert_alpha(),
    5: pygame.image.load("Assets/imageTransp.png").convert_alpha(),
}

buses, personnages, taille_parking, grid = lire_carte("cartes/carte7", bus_images, cell_size)
parking = [None] * taille_parking

print(buses)
print(personnages)
print(taille_parking)

file_personnages_x = parking_x + (taille_parking * (cell_size + 10)) + 40
file_personnages_y = parking_y + (cell_size // 2)

passagers_en_marche = []

# ── Variables solveur ──────────────────────────────────────────
solution_coups = []   # liste de chaînes décrivant chaque coup
hint_idx       = 0    # prochain coup à jouer
auto_solve     = False
auto_timer     = 0


def construire_etat():
    """Convertit l'état pygame courant en dict lisible par le solveur."""
    return {
        'grille': [
            [{'dir': c.direction, 'couleur': c.couleur_id, 'cap': c.capacite}
             for c in row]
            for row in grid
        ],
        'buses': [
            {'x': b.x, 'y': b.y, 'dir': b.direction, 'couleur': b.couleur_id,
             'cap': b.capacite, 'taille': b.taille, 'charge': b.charge}
            for b in buses
        ],
        'parking': [
            None if p is None else
            {'x': 0, 'y': 0, 'dir': p.direction, 'couleur': p.couleur_id,
             'cap': p.capacite, 'taille': p.taille, 'charge': p.charge}
            for p in parking
        ],
        'personnages': list(personnages),
    }


def get_hint():
    """Lance le solveur depuis l'état courant et stocke la solution."""
    global solution_coups, hint_idx
    print("Calcul de la solution en cours...")
    import time
    t0 = time.perf_counter()
    solution_coups = solveur_bfs(construire_etat()) or []
    duree = time.perf_counter() - t0
    hint_idx = 0
    if solution_coups:
        print(f"Solution trouvée en {len(solution_coups)} coups !  (temps : {duree:.3f}s)")
    else:
        print(f"Aucune solution trouvée.  (temps : {duree:.3f}s)")


def bus_du_prochain_coup():
    """Retourne l'objet Bus pygame correspondant au prochain coup de la solution."""
    if not solution_coups or hint_idx >= len(solution_coups):
        return None
    coup = solution_coups[hint_idx]
    m = re.search(r'pos=\((\d+),(\d+)\)', coup)
    if not m:
        return None
    tx, ty = int(m.group(1)), int(m.group(2))
    for b in buses:
        if b.x == tx and b.y == ty:
            return b
    return None


def jouer_coup(b):
    """Exécute un coup (déplace le bus b) — partagé entre auto-solve et clic manuel."""
    if b.capacite == 10 and b.couleur == 0:
        vider_emplacement_bus(grid, b)
        buses.remove(b)
        if son_deplacement:
            son_deplacement.play()
    else:
        statut = deplacer_bus(buses, b, parking, taille_parking, grid)
        if statut in ("gare", "detruit") and son_deplacement:
            son_deplacement.play()
        elif statut == "plein" and son_collision:
            son_collision.play()

# ──────────────────────────────────────────────────────────────

running      = True
show_grid    = True
game_over    = False
victoire     = False
son_fin_joue = False
frames_bloquees = 0

while running:

    screen.blit(background, (0, 0))

    # 1. Grille
    if show_grid:
        draw_grid(screen, grid, cell_size, offset_x, offset_y)

    # 2. Parking
    draw_parking(screen, parking, taille_parking, parking_x, parking_y, cell_size)

    # 3. File d'attente
    draw_file_attente(screen, personnages, file_personnages_x, file_personnages_y, cell_size)

    # 4. Montée des passagers
    if len(passagers_en_marche) == 0:
        monter(parking, taille_parking, personnages, parking_x, parking_y, cell_size,
               passagers_en_marche, file_personnages_x, file_personnages_y)

    for pv, bus_cible in list(passagers_en_marche):
        pv.update()
        pv.draw(screen)
        if pv.arrive:
            bus_cible.charge += 1
            if son_chargement:
                son_chargement.play()
            print(f" Un passager est monté ! Charge : {bus_cible.charge}/{bus_cible.capacite}")
            passagers_en_marche.remove((pv, bus_cible))

    # 5. Libérer les bus pleins
    liberer_bus(parking, taille_parking)

    # ── Auto-solve : joue un coup toutes les 90 frames ────────
    if auto_solve and solution_coups and hint_idx < len(solution_coups):
        auto_timer += 1
        if auto_timer >= 300 and len(passagers_en_marche) == 0:
            auto_timer = 0
            b = bus_du_prochain_coup()
            if b and est_jouable(grid, b):
                hint_idx += 1
                jouer_coup(b)
            else:
                auto_solve = False   # désynchronisation, on arrête
    # ──────────────────────────────────────────────────────────

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_g:
                show_grid = not show_grid

            # ── Touche H : hint (surligne le prochain coup) ───
            if event.key == pygame.K_h:
                get_hint()

            # ── Touche A : auto-solve ─────────────────────────
            if event.key == pygame.K_a:
                get_hint()
                auto_solve = not auto_solve
                auto_timer = 0
                print(f"Auto-solve : {'ON' if auto_solve else 'OFF'}")

        if event.type == pygame.MOUSEBUTTONDOWN:
            if victoire or game_over:
                continue
            mouse_pos = pygame.mouse.get_pos()

            for b in list(buses):
                rect = get_rect(b, cell_size, offset_x, offset_y)
                if rect.collidepoint(mouse_pos):
                    if est_jouable(grid, b):
                        # Si le joueur clique manuellement, on avance hint_idx
                        # si c'est bien le bon bus, sinon on réinitialise la solution
                        b_hint = bus_du_prochain_coup()
                        if b is b_hint:
                            hint_idx += 1
                        else:
                            solution_coups = []   # le joueur dévie : on efface le hint

                        jouer_coup(b)
                    else:
                        if son_collision:
                            son_collision.play()
                        print(f" BLOQUÉ : Le bus {b.couleur} ne peut pas sortir.")
                    break

    # --- Détection de la victoire ---
    if (len(buses) == 0 and len(personnages) == 0
            and len(passagers_en_marche) == 0
            and all(p is None for p in parking)):
        victoire = True
        if not son_fin_joue:
            pygame.mixer.music.stop()
            if son_victoire:
                son_victoire.play()
            son_fin_joue = True

    # --- Détection de l'échec ---
    parking_plein          = all(p is not None for p in parking)
    prochain_passager_couleur = personnages[0] if personnages else None
    un_bus_peut_charger    = False
    if prochain_passager_couleur is not None:
        for p in parking:
            if p is not None and p.couleur == prochain_passager_couleur and p.charge < p.capacite:
                un_bus_peut_charger = True
                break

    if parking_plein and not un_bus_peut_charger and len(passagers_en_marche) == 0 and buses:
        frames_bloquees += 1
    else:
        frames_bloquees = 0

    if frames_bloquees > 60:
        game_over = True
        if not son_fin_joue:
            pygame.mixer.music.stop()
            if son_echec:
                son_echec.play()
            son_fin_joue = True

    # --- Dessin des bus (avec surligné hint) ---
    bus_hint = bus_du_prochain_coup()
    for b in buses:
        if b is not None:
            draw_image(screen, b, cell_size, offset_x, offset_y)
            if b is bus_hint:
                rect      = get_rect(b, cell_size, offset_x, offset_y)
                epaisseur = 3 if (pygame.time.get_ticks() // 300) % 2 == 0 else 1
                pygame.draw.rect(screen, (255, 255, 255), rect, epaisseur)

    # --- UI solveur ---
    font_ui = pygame.font.SysFont("Arial", 14)
    screen.blit(font_ui.render("H = Hint  |  A = Auto-solve  |  G = Grille", True, (200, 200, 200)), (10, 10))
    if solution_coups and hint_idx < len(solution_coups):
        nb = len(solution_coups) - hint_idx
        screen.blit(font_ui.render(f"Coups restants : {nb}", True, (255, 220, 50)), (10, 28))
    if auto_solve:
        screen.blit(font_ui.render("AUTO-SOLVE  ON", True, (50, 255, 120)), (10, 46))

    # --- Écrans de fin ---
    if victoire:
        font_fin = pygame.font.SysFont("Arial", 50, bold=True)
        texte    = font_fin.render("VICTOIRE !", True, (46, 204, 113))
        overlay  = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        screen.blit(texte, texte.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

    elif game_over:
        font_fin = pygame.font.SysFont("Arial", 50, bold=True)
        texte    = font_fin.render("GAME OVER", True, (231, 76, 60))
        overlay  = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        screen.blit(texte, texte.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

    pygame.display.flip()

pygame.quit()
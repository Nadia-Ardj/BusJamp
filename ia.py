"""
ia.py  –  Solveur IA pour BusJam.

S'intègre dans main (1).py SANS LE MODIFIER :
    from ia import BusJamSolver

Utilisation dans main (1).py :
    solver = BusJamSolver(buses, personnages, parking, grid, taille_parking)
    solution = solver.resoudre()   # liste de Bus pygame à cliquer dans l'ordre
"""

from collections import deque
import copy


# ──────────────────────────────────────────────────────────────
# 1.  Représentation de l'état (immuable, hashable)
# ──────────────────────────────────────────────────────────────

def get_state(grid, parking, personnages):
    """
    Transforme l'état courant en un tuple immuable pour le set 'visited'.

    CORRECTION : on encode (direction, couleur_id) par case pour avoir
    une clé fiable — les références d'objets Bus changent à chaque copie.
    """
    grid_state = tuple(
        tuple(
            (cell.direction, cell.couleur_id) for cell in row
        )
        for row in grid
    )
    parking_state = tuple(
        (p.couleur_id, p.charge) if p is not None else (-1, 0)
        for p in parking
    )
    return (grid_state, parking_state, tuple(personnages))


# ──────────────────────────────────────────────────────────────
# 2.  Simulation (copies indépendantes des objets pygame)
# ──────────────────────────────────────────────────────────────

def _copier_grille(grid):
    """Copie la grille en dupliquant chaque objet Bus (copie superficielle suffisante)."""
    return [[copy.copy(cell) for cell in row] for row in grid]


def _copier_parking(parking):
    """Copie le parking (None reste None, Bus est copié)."""
    return [copy.copy(p) if p is not None else None for p in parking]


def _vider_cases_bus(grid, bus):
    """
    Efface toutes les cases occupées par 'bus' dans la grille simulée.
    CORRECTION : on modifie vraiment la grille (le 'pass' d'origine ne faisait rien).
    """
    for k in range(bus.taille):
        if bus.direction in ("L", "R"):
            cx, cy = bus.x + k, bus.y
        else:
            cx, cy = bus.x, bus.y + k

        if 0 <= cy < len(grid) and 0 <= cx < len(grid[0]):
            # On marque la case comme vide (direction X = case libre)
            vide = copy.copy(grid[cy][cx])
            vide.direction = "X"
            vide.couleur_id = 10
            vide.capacite = 0
            vide.taille = 0
            vide.visite = True
            grid[cy][cx] = vide


def _propager_chargement(parking, personnages):
    """
    Simule les montées de passagers et libère les bus pleins.
    Boucle jusqu'à ce que plus rien ne change.
    """
    parking = list(parking)
    personnages = list(personnages)

    changed = True
    while changed:
        changed = False

        # Libérer les bus pleins
        for i in range(len(parking)):
            p = parking[i]
            if p is not None and p.charge >= p.capacite:
                parking[i] = None
                changed = True

        # Faire monter le prochain passager si couleur correspondante trouvée
        if personnages:
            prochain = personnages[0]
            for i in range(len(parking)):
                p = parking[i]
                if p is not None and p.couleur_id == prochain and p.charge < p.capacite:
                    bus_copie = copy.copy(p)
                    bus_copie.charge += 1
                    parking[i] = bus_copie
                    personnages.pop(0)
                    changed = True
                    break

    return parking, personnages


def simuler_deplacement(grid, bus, parking, taille_parking, personnages):
    """
    Simule le déplacement d'un bus vers le parking.

    CORRECTION majeure : la version d'origine ne modifiait rien (juste des 'pass').
    Maintenant on retourne de vraies copies modifiées de la grille et du parking.

    Retourne (new_grid, new_parking, new_personnages) ou (None, None, None) si impossible.
    """
    from lecture import est_jouable

    # Vérifier que le bus peut sortir
    if not est_jouable(grid, bus):
        return None, None, None

    new_grid = _copier_grille(grid)
    new_parking = _copier_parking(parking)
    new_persos = list(personnages)

    # --- Bus décoratif (cap == 10 ou cap == 0) : juste vider ses cases ---
    if bus.capacite == 10 or bus.capacite == 0:
        _vider_cases_bus(new_grid, bus)
        new_parking, new_persos = _propager_chargement(new_parking, new_persos)
        return new_grid, new_parking, new_persos

    # --- Bus normal : chercher une place libre au parking ---
    idx_libre = next((i for i in range(taille_parking) if new_parking[i] is None), -1)
    if idx_libre == -1:
        return None, None, None  # Parking plein

    # Vider les cases du bus sur la grille
    _vider_cases_bus(new_grid, bus)

    # Garer le bus (copie avec charge remise à 0)
    bus_gare = copy.copy(bus)
    bus_gare.charge = 0
    bus_gare.direction = "U"
    new_parking[idx_libre] = bus_gare

    # Propager les montées de passagers
    new_parking, new_persos = _propager_chargement(new_parking, new_persos)

    return new_grid, new_parking, new_persos


# ──────────────────────────────────────────────────────────────
# 3.  Détection victoire / défaite
# ──────────────────────────────────────────────────────────────

def _est_victoire(buses_restants, personnages, parking):
    return (
            len(buses_restants) == 0
            and len(personnages) == 0
            and all(p is None for p in parking)
    )


def _est_defaite(parking, personnages, taille_parking):
    """Parking plein ET le prochain passager ne peut monter nulle part."""
    if not personnages:
        return False
    if any(p is None for p in parking):
        return False
    prochain = personnages[0]
    for p in parking:
        if p is not None and p.couleur_id == prochain and p.charge < p.capacite:
            return False
    return True


# ──────────────────────────────────────────────────────────────
# 4.  Classe principale BusJamSolver
# ──────────────────────────────────────────────────────────────

class BusJamSolver:
    def __init__(self, buses_init, personnages_init, parking_init, grid_init, taille_parking):
        """
        Paramètres : objets pygame directement (Bus, listes, grille).
        """
        self.buses = buses_init
        self.personnages = personnages_init
        self.parking = parking_init
        self.grid = grid_init
        self.taille_parking = taille_parking

    # ----------------------------------------------------------
    # 4a.  Heuristique simple  (rapide, pas toujours optimale)
    # ----------------------------------------------------------

    def trouver_prochain_coup(self, current_buses, current_grid, current_parking, current_persos):
        """
        Cherche le meilleur bus à jouer selon une heuristique :
          1. Bus de la couleur du prochain passager et jouable
          2. N'importe quel bus jouable (déblocage)

        CORRECTION : on vérifie aussi que le parking a une place libre
        avant de proposer un bus.
        """
        from lecture import est_jouable, parking_libre

        taille = self.taille_parking

        # Priorité 1 : bus de la bonne couleur
        if current_persos:
            target_color = current_persos[0]
            for b in current_buses:
                if (b.couleur_id == target_color
                        and est_jouable(current_grid, b)
                        and (parking_libre(current_parking, taille) or b.capacite == 10)):
                    return b

        # Priorité 2 : n'importe quel bus jouable
        for b in current_buses:
            if (est_jouable(current_grid, b)
                    and (parking_libre(current_parking, taille) or b.capacite == 10)):
                return b

        return None

    # ----------------------------------------------------------
    # 4b.  BFS complet  (toujours optimal, peut être plus lent)
    # ----------------------------------------------------------

    def resoudre(self, max_etats=200_000):
        """
        Résout la carte par BFS et retourne la liste ordonnée des Bus
        pygame à cliquer.

        Retourne [] si aucune solution n'est trouvée.
        """
        from lecture import est_jouable

        etat_initial = (
            _copier_grille(self.grid),
            list(self.buses),
            _copier_parking(self.parking),
            list(self.personnages),
        )

        # file BFS : (grid, buses, parking, personnages, chemin)
        # chemin = liste de tuples (x, y) des bus à cliquer
        queue = deque()
        visites = set()

        cle0 = get_state(etat_initial[0], etat_initial[2], etat_initial[3])
        queue.append((*etat_initial, []))
        visites.add(cle0)

        explored = 0
        while queue:
            explored += 1
            if explored % 10_000 == 0:
                print(f"  … {explored} états explorés, {len(queue)} en attente")

            if len(visites) > max_etats:
                print(f"[BFS] Limite de {max_etats} états atteinte.")
                return []

            g, buses_courants, p, persos, chemin = queue.popleft()

            # Victoire ?
            if _est_victoire(buses_courants, persos, p):
                print(f"[BFS] Solution trouvée en {len(chemin)} coup(s) !")
                return chemin  # liste de (x, y)

            # Défaite ?
            if _est_defaite(p, persos, self.taille_parking):
                continue

            # Développer les coups possibles
            for bus in buses_courants:
                if not est_jouable(g, bus):
                    continue

                new_g, new_p, new_persos = simuler_deplacement(
                    g, bus, p, self.taille_parking, persos
                )
                if new_g is None:
                    continue

                new_buses = [b for b in buses_courants if b is not bus]

                cle = get_state(new_g, new_p, new_persos)
                if cle in visites:
                    continue
                visites.add(cle)

                queue.append((new_g, new_buses, new_p, new_persos, chemin + [(bus.x, bus.y)]))

        print("[BFS] Aucune solution trouvée.")
        return []

    # ----------------------------------------------------------
    # 4c.  Helper : retrouver le Bus pygame depuis (x, y)
    # ----------------------------------------------------------

    @staticmethod
    def trouver_bus_par_position(buses, x, y):
        """Retourne l'objet Bus dont la position (x, y) correspond."""
        for b in buses:
            if b.x == x and b.y == y:
                return b
        return None

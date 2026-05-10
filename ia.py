import collections
import copy


def get_state(grid, parking, personnages):
    # Transforme l'état actuel en un tuple immuable pour le set 'visited'
    grid_state = tuple(tuple(bus.couleur_id if bus else -1 for bus in row) for row in grid)
    parking_state = tuple(p.couleur_id if p else -1 for p in parking)
    return (grid_state, parking_state, tuple(personnages))


def simuler_deplacement(grid, bus, parking, taille_parking):
    # Simulation simplifiée de la logique de lecture.py
    new_grid = [row[:] for row in grid]
    new_parking = list(parking)

    # Trouver une place
    idx_libre = -1
    for i in range(taille_parking):
        if new_parking[i] is None:
            idx_libre = i
            break

    if idx_libre == -1: return None, None  # Parking plein

    # Vider les cases dans la grille simulée
    # (Logique simplifiée : on cherche tous les bus identiques connectés)
    target_id = bus.couleur_id
    for y in range(len(new_grid)):
        for x in range(len(new_grid[0])):
            if new_grid[y][x] == bus:
                # Dans une vraie simu, on remplacerait par un objet "vide"
                pass

                # Pour l'IA, on va juste renvoyer les données modifiées
    # Note : Une implémentation complète nécessiterait une copie profonde des objets Bus
    return new_grid, new_parking


class BusJamSolver:
    def __init__(self, buses_init, personnages_init, parking_init, grid_init):
        self.buses = buses_init
        self.personnages = personnages_init
        self.parking = parking_init
        self.grid = grid_init

    def trouver_prochain_coup(self, current_buses, current_grid, current_parking, current_persos):
        """
        Cherche le bus qui, une fois cliqué, débloque la situation.
        Priorité : Bus qui correspond au premier perso de la file.
        """
        from lecture import est_jouable, parking_libre

        # Stratégie Gourmande (Heuristique simple) :
        # 1. On cherche un bus déplaçable dont la couleur est celle du premier perso
        if current_persos:
            target_color = current_persos[0]
            for b in current_buses:
                if b.couleur_id == target_color and est_jouable(current_grid, b):
                    if parking_libre(current_parking, len(current_parking)):
                        return b

        # 2. Sinon, on cherche n'importe quel bus déplaçable qui ne bloque pas le parking
        for b in current_buses:
            if est_jouable(current_grid, b) and parking_libre(current_parking, len(current_parking)):
                return b

        return None
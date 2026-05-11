from collections import deque
import time

# ──────────────────────────────────────────────────────────────
# 1.  Lecture de la carte  (sans pygame)
# ──────────────────────────────────────────────────────────────

NOMS_COULEURS = {
    0:'Rouge', 1:'Bleu', 2:'Vert', 3:'Jaune', 4:'Orange',
    5:'Violet', 6:'Rose', 7:'Cyan', 8:'Gris', 9:'Violet foncé', 10:'(vide)'
}
def _nom(cid):
    return NOMS_COULEURS.get(cid, str(cid))


def lire_carte_logique(chemin):
    with open(chemin, encoding="utf-8") as f:
        lignes = [l.strip() for l in f if l.strip()]

    taille_parking = int(lignes[0])
    personnages    = [int(c) for c in lignes[-1]]
    lignes_grille  = lignes[1:-1]

    rows = len(lignes_grille)
    cols = len(lignes_grille[0].split())

    grille = []
    for i, ligne in enumerate(lignes_grille):
        tokens = ligne.split()
        row = []
        for j, cell in enumerate(tokens):
            if cell == "XXX":
                row.append({'dir':'X','couleur':10,'cap':0})
            else:
                cap_brute = int(cell[0])
                direction = cell[1]
                couleur   = int(cell[2])
                cap = 10 if (cap_brute == 0 and direction != 'X') else cap_brute
                row.append({'dir':direction,'couleur':couleur,'cap':cap})
        grille.append(row)

    visite = [[False]*cols for _ in range(rows)]
    buses  = []

    for i in range(rows):
        for j in range(cols):
            if visite[i][j]:
                continue
            c = grille[i][j]
            if c['dir'] == 'X':
                visite[i][j] = True
                continue

            if c['dir'] in ('L','R'):
                k = j
                while k < cols and grille[i][k]['couleur'] == c['couleur'] and grille[i][k]['dir'] == c['dir']:
                    visite[i][k] = True
                    k += 1
                taille = k - j
            else:
                k = i
                while k < rows and grille[k][j]['couleur'] == c['couleur'] and grille[k][j]['dir'] == c['dir']:
                    visite[k][j] = True
                    k += 1
                taille = k - i

            buses.append({
                'x': j, 'y': i,
                'dir': c['dir'],
                'couleur': c['couleur'],
                'cap': c['cap'],
                'taille': taille,
                'charge': 0,
            })

    return taille_parking, grille, buses, personnages


# ──────────────────────────────────────────────────────────────
# 2.  Logique du jeu
# ──────────────────────────────────────────────────────────────

def cases_bus(bus):
    cases = []
    for k in range(bus['taille']):
        if bus['dir'] in ('L','R'):
            cases.append((bus['x']+k, bus['y']))
        else:
            cases.append((bus['x'], bus['y']+k))
    return cases


def est_jouable(grille, bus):
    rows = len(grille)
    cols = len(grille[0])
    d = bus['dir']
    if d == 'U':
        for i in range(bus['y']-1, -1, -1):
            if grille[i][bus['x']]['dir'] != 'X':
                return False
    elif d == 'D':
        for i in range(bus['y']+bus['taille'], rows):
            if grille[i][bus['x']]['dir'] != 'X':
                return False
    elif d == 'L':
        for j in range(bus['x']-1, -1, -1):
            if grille[bus['y']][j]['dir'] != 'X':
                return False
    elif d == 'R':
        for j in range(bus['x']+bus['taille'], cols):
            if grille[bus['y']][j]['dir'] != 'X':
                return False
    return True


def vider_cases(grille, bus):
    g = [row[:] for row in grille]
    for (x,y) in cases_bus(bus):
        g[y][x] = {'dir':'X','couleur':10,'cap':0}
    return g


def propager_chargement(parking, personnages):
    """
    Simule les montées de passagers :
    - Le 1er passager de la file monte dans le 1er bus du parking
      dont la couleur correspond et qui n'est pas plein.
    - Les bus pleins libèrent leur place.
    Boucle jusqu'à plus aucun changement possible.
    """
    parking     = list(parking)
    personnages = list(personnages)

    changed = True
    while changed:
        changed = False

        # Libérer les bus pleins
        for i in range(len(parking)):
            if parking[i] is not None and parking[i]['charge'] >= parking[i]['cap']:
                parking[i] = None
                changed = True

        # Faire monter le prochain passager si possible
        if personnages:
            prochain = personnages[0]
            for i in range(len(parking)):
                p = parking[i]
                if p is not None and p['couleur'] == prochain and p['charge'] < p['cap']:
                    parking[i] = dict(p, charge=p['charge']+1)
                    personnages.pop(0)
                    changed = True
                    break

    return parking, personnages


def appliquer_coup(etat, idx_bus):
    buses       = etat['buses']
    grille      = etat['grille']
    parking     = etat['parking']
    personnages = etat['personnages']

    bus = buses[idx_bus]

    if not est_jouable(grille, bus):
        return None

    new_grille = vider_cases(grille, bus)
    new_buses  = [b for k,b in enumerate(buses) if k != idx_bus]

    if bus['cap'] == 0 or bus['dir'] == 'X':
        new_parking, new_personnages = propager_chargement(list(parking), list(personnages))
        return {
            'grille': new_grille,
            'buses': new_buses,
            'parking': new_parking,
            'personnages': new_personnages,
        }

    place = next((i for i,p in enumerate(parking) if p is None), None)
    if place is None:
        return None

    new_parking = list(parking)
    new_parking[place] = dict(bus, charge=0)

    new_parking, new_personnages = propager_chargement(new_parking, list(personnages))

    return {
        'grille': new_grille,
        'buses': new_buses,
        'parking': new_parking,
        'personnages': new_personnages,
    }


def est_victoire(etat):
    return (len(etat['buses']) == 0
            and len(etat['personnages']) == 0
            and all(p is None for p in etat['parking']))


def est_defaite(etat):
    parking     = etat['parking']
    personnages = etat['personnages']
    if not personnages:
        return False
    if any(p is None for p in parking):
        return False
    prochain = personnages[0]
    for p in parking:
        if p is not None and p['couleur'] == prochain and p['charge'] < p['cap']:
            return False
    return True


def etat_vers_cle(etat):
    grille_key = tuple(
        tuple((c['dir'], c['couleur']) for c in row)
        for row in etat['grille']
    )
    buses_key = tuple(
        (b['x'], b['y'], b['dir'], b['couleur'], b['cap'], b['charge'])
        for b in sorted(etat['buses'], key=lambda b: (b['y'], b['x']))
    )
    parking_key = tuple(
        None if p is None else (p['couleur'], p['charge'], p['cap'])
        for p in etat['parking']
    )
    return (grille_key, buses_key, parking_key, tuple(etat['personnages']))


# ──────────────────────────────────────────────────────────────
# 3.  Solveur BFS
# ──────────────────────────────────────────────────────────────

def solveur_bfs(etat_initial, max_etats=500_000):
    queue   = deque()
    visites = {}

    cle0 = etat_vers_cle(etat_initial)
    queue.append((etat_initial, []))
    visites[cle0] = True

    explored = 0
    t_debut  = time.perf_counter()

    while queue:
        explored += 1
        if explored % 10000 == 0:
            elapsed = time.perf_counter() - t_debut
            print(f"  … {explored} états explorés, {len(queue)} en attente  ({elapsed:.2f}s)")

        if len(visites) > max_etats:
            elapsed = time.perf_counter() - t_debut
            print(f"[BFS] Limite de {max_etats} états atteinte après {elapsed:.2f}s.")
            return None

        etat, chemin = queue.popleft()

        if est_victoire(etat):
            elapsed = time.perf_counter() - t_debut
            print(f"[BFS] Solution trouvée en {elapsed:.3f}s  ({explored} états explorés).")
            return chemin

        if est_defaite(etat):
            continue

        for idx, bus in enumerate(etat['buses']):
            if not est_jouable(etat['grille'], bus):
                continue

            nouvel_etat = appliquer_coup(etat, idx)
            if nouvel_etat is None:
                continue

            cle = etat_vers_cle(nouvel_etat)
            if cle in visites:
                continue
            visites[cle] = True

            desc = (f"Cliquer bus {_nom(bus['couleur']):12s} "
                    f"dir={bus['dir']} pos=({bus['x']},{bus['y']}) "
                    f"taille={bus['taille']} cap={bus['cap']}")
            queue.append((nouvel_etat, chemin + [desc]))

    elapsed = time.perf_counter() - t_debut
    print(f"[BFS] Aucune solution trouvée après {elapsed:.3f}s  ({explored} états explorés).")
    return None


# ──────────────────────────────────────────────────────────────
# 4.  Point d'entrée
# ──────────────────────────────────────────────────────────────

def main(chemin_carte="carte0"):
    print(f"\n{'='*60}")
    print(f"  BusJam Solveur IA  –  {chemin_carte}")
    print(f"{'='*60}\n")

    taille_parking, grille, buses, personnages = lire_carte_logique(chemin_carte)

    print(f"Parking    : {taille_parking} places")
    print(f"Grille     : {len(grille)} lignes × {len(grille[0])} colonnes")
    print(f"Bus sur grille ({len(buses)}) :")
    for b in buses:
        jouable_str = "✓ jouable" if est_jouable(grille, b) else "✗ bloqué"
        print(f"  {_nom(b['couleur']):12s} dir={b['dir']} pos=({b['x']},{b['y']}) "
              f"taille={b['taille']} cap={b['cap']}  {jouable_str}")
    print(f"\nFile d'attente ({len(personnages)} passagers) :")
    print(" ", [_nom(p) for p in personnages])
    print()

    etat_initial = {
        'grille'      : grille,
        'buses'       : buses,
        'parking'     : [None] * taille_parking,
        'personnages' : personnages,
    }

    print("Recherche BFS en cours…\n")
    t0       = time.perf_counter()
    solution = solveur_bfs(etat_initial)
    duree    = time.perf_counter() - t0

    if solution is None:
        print(f"\n❌  Aucune solution trouvée.  (temps : {duree:.3f}s)")
    else:
        print(f"\n✅  Solution en {len(solution)} coup(s)  —  trouvée en {duree:.3f}s :\n")
        for i, coup in enumerate(solution, 1):
            print(f"  Coup {i:2d} : {coup}")
        print()


if __name__ == "__main__":
    import sys
    carte = sys.argv[1] if len(sys.argv) > 1 else "carte0"
    main(carte)
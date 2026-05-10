import copy
from collections import deque


def obtenir_cases_bus(bus):
    cases = []
    # Utilise la taille 10 si c'est un obstacle de couleur autre que 0, sinon sa taille normale
    taille = 10 if (bus['cap'] == 0 and bus['couleur'] != 0) else bus['taille']
    for i in range(taille):
        if bus['dir'] in ['L', 'R']:
            cases.append((bus['x'] + i, bus['y']))
        else:
            cases.append((bus['x'], bus['y'] + i))
    return cases


def est_jouable_logique(grille, bus):
    rows, cols = len(grille), len(grille[0])
    x, y, d = bus['x'], bus['y'], bus['dir']
    # Calcul de la taille selon votre règle
    taille = 10 if (bus['cap'] == 0 and bus['couleur'] != 0) else bus['taille']

    try:
        if d == 'U':
            for i in range(y - 1, -1, -1):
                if grille[i][x]['dir'] != 'X': return False
        elif d == 'D':
            for i in range(y + taille, rows):
                if grille[i][x]['dir'] != 'X': return False
        elif d == 'L':
            for j in range(x - 1, -1, -1):
                if grille[y][j]['dir'] != 'X': return False
        elif d == 'R':
            for j in range(x + taille, cols):
                if grille[y][j]['dir'] != 'X': return False
        return True
    except:
        return False


def simulation_embarquement(parking, personnages):
    parking = [dict(p) if p else None for p in parking]
    persos = list(personnages)
    encore = True
    while encore:
        encore = False
        # Départ des bus pleins
        for i in range(len(parking)):
            if parking[i] and parking[i]['charge'] >= parking[i]['cap']:
                parking[i] = None
                encore = True
        # Embarquement
        if persos:
            for i in range(len(parking)):
                if parking[i] and parking[i]['couleur'] == persos[0] and parking[i]['charge'] < parking[i]['cap']:
                    parking[i]['charge'] += 1
                    persos.pop(0)
                    encore = True
                    break
    return parking, persos


def appliquer_coup(etat, idx_bus):
    bus = etat['buses'][idx_bus]

    # REGLE OBSTACLE : Si cap est 0, le bus est un obstacle, il ne bouge JAMAIS
    if bus['cap'] == 0:
        return None

    if not est_jouable_logique(etat['grille'], bus):
        return None

    # Vider les cases du bus sur la grille
    n_grille = copy.deepcopy(etat['grille'])
    for cx, cy in obtenir_cases_bus(bus):
        if 0 <= cy < len(n_grille) and 0 <= cx < len(n_grille[0]):
            n_grille[cy][cx] = {'dir': 'X', 'couleur': 10}

    n_bus = [b for i, b in enumerate(etat['buses']) if i != idx_bus]
    n_parking = copy.deepcopy(etat['parking'])

    libre = next((i for i, p in enumerate(n_parking) if p is None), None)
    if libre is None: return None

    n_parking[libre] = {'couleur': bus['couleur'], 'cap': bus['cap'], 'charge': 0}
    p_final, persos_final = simulation_embarquement(n_parking, etat['personnages'])

    return {'grille': n_grille, 'buses': n_bus, 'parking': p_final, 'personnages': persos_final}


def solveur_bfs(grid_py, buses_py, parking_py, persos_py):
    # Conversion initiale
    b_logique = []
    for b in buses_py:
        if b:
            b_logique.append({
                'x': b.x, 'y': b.y, 'dir': b.direction,
                'taille': b.taille, 'couleur': b.couleur,
                'cap': b.capacite, 'charge': b.charge
            })

    p_logique = [None if p is None else {'couleur': p.couleur, 'cap': p.capacite, 'charge': p.charge} for p in
                 parking_py]

    rows, cols = len(grid_py), len(grid_py[0])
    g_logique = [[{'dir': 'X'} for _ in range(cols)] for _ in range(rows)]
    for b in b_logique:
        for cx, cy in obtenir_cases_bus(b):
            if 0 <= cy < rows and 0 <= cx < cols:
                g_logique[cy][cx] = {'dir': b['dir']}

    etat_init = {'grille': g_logique, 'buses': b_logique, 'parking': p_logique, 'personnages': list(persos_py)}

    queue = deque([(etat_init, [])])
    # On utilise un set de strings pour optimiser la mémoire
    vus = {str(b_logique) + str(p_logique) + str(list(persos_py))}

    count = 0
    while queue and count < 150000:
        etat, chemin = queue.popleft()
        count += 1

        if not etat['personnages'] and all(p is None for p in etat['parking']):
            return chemin

        for i in range(len(etat['buses'])):
            nouveau = appliquer_coup(etat, i)
            if nouveau:
                cle = str(nouveau['buses']) + str(nouveau['parking']) + str(nouveau['personnages'])
                if cle not in vus:
                    vus.add(cle)
                    b = etat['buses'][i]
                    queue.append((nouveau, chemin + [(b['x'], b['y'])]))
    return None
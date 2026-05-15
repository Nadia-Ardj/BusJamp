"""
benchmark.py  —  Résout toutes les cartes BusJam sans interface graphique.
Usage :  python benchmark.py [dossier_cartes]
"""

import sys
import os
import glob
import time

# Ajout du répertoire courant au path pour importer solveur.py
sys.path.insert(0, os.path.dirname(__file__))
from solveur import lire_carte_logique, solveur_bfs, est_jouable, NOMS_COULEURS


# ── Helpers ───────────────────────────────────────────────────

def lister_cartes(dossier):
    fichiers = glob.glob(os.path.join(dossier, "carte*"))
    def numero(p):
        chiffres = ''.join(filter(str.isdigit, os.path.basename(p)))
        return int(chiffres) if chiffres else 0
    return sorted(fichiers, key=numero)


def resoudre(chemin):
    """
    Charge une carte et lance le BFS.
    Retourne (solution, duree_secondes) où solution est None si pas de solution.
    """
    taille_parking, grille, buses, personnages = lire_carte_logique(chemin)
    etat_initial = {
        'grille'      : grille,
        'buses'       : buses,
        'parking'     : [None] * taille_parking,
        'personnages' : personnages,
    }
    t0       = time.perf_counter()
    solution = solveur_bfs(etat_initial)
    duree    = time.perf_counter() - t0
    return solution, duree


# ── Programme principal ────────────────────────────────────────

def main():
    dossier = sys.argv[1] if len(sys.argv) > 1 else "cartes"
    cartes  = lister_cartes(dossier)

    if not cartes:
        print(f"Aucune carte trouvée dans '{dossier}'.")
        sys.exit(1)

    print(f"\n{'═'*62}")
    print(f"  BusJam — Benchmark  ({len(cartes)} cartes)")
    print(f"{'═'*62}\n")

    resultats   = []
    t_total_start = time.perf_counter()

    for i, chemin in enumerate(cartes, 1):
        nom = os.path.basename(chemin)
        print(f"[{i:>2}/{len(cartes)}]  {nom:<12}", end="  ", flush=True)

        solution, duree = resoudre(chemin)

        if solution is None:
            statut = "❌  sans solution"
        else:
            statut = f"✅  {len(solution):>2} coup(s)"

        print(f"{statut:<18}  {duree:.3f} s")
        resultats.append((nom, solution, duree))

    t_total = time.perf_counter() - t_total_start

    # ── Récapitulatif ──────────────────────────────────────────
    resolues   = [r for r in resultats if r[1] is not None]
    echouees   = [r for r in resultats if r[1] is None]
    durees     = [r[2] for r in resultats]

    print(f"\n{'─'*62}")
    print(f"  Cartes résolues   : {len(resolues)} / {len(cartes)}")
    print(f"  Sans solution     : {len(echouees)}")
    if resolues:
        nb_coups = [len(r[1]) for r in resolues]
        print(f"  Coups (min/moy/max) : {min(nb_coups)} / {sum(nb_coups)/len(nb_coups):.1f} / {max(nb_coups)}")
    print(f"{'─'*62}")
    print(f"  Temps total       : {t_total:.3f} s")
    print(f"  Temps moyen/carte : {sum(durees)/len(durees):.3f} s")
    print(f"  Plus rapide       : {min(durees):.3f} s  ({resultats[durees.index(min(durees))][0]})")
    print(f"  Plus lente        : {max(durees):.3f} s  ({resultats[durees.index(max(durees))][0]})")
    print(f"{'═'*62}\n")


if __name__ == "__main__":
    main()
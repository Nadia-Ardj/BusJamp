import os
import glob

def lister_cartes(dossier="cartes"):
    """
    Retourne la liste triée des fichiers de cartes trouvés dans le dossier.
    Exemple : ['cartes/carte0', 'cartes/carte1', ..., 'cartes/carte19']
    """
    fichiers = glob.glob(os.path.join(dossier, "carte*"))

    # Tri numérique : extrait le numéro à la fin du nom de fichier
    def numero(chemin):
        nom = os.path.basename(chemin)          # "carte19"
        chiffres = ''.join(filter(str.isdigit, nom))
        return int(chiffres) if chiffres else 0

    return sorted(fichiers, key=numero)


class GestionnaireNiveaux:
    """
    Garde en mémoire la liste des cartes et l'index du niveau courant.
    Fournit des méthodes pour charger le niveau suivant ou recommencer.
    """

    def __init__(self, dossier="cartes"):
        self.cartes = lister_cartes(dossier)
        if not self.cartes:
            raise FileNotFoundError(f"Aucune carte trouvée dans le dossier '{dossier}'.")
        self.index_courant = 0

    # ------------------------------------------------------------------
    @property
    def carte_courante(self):
        """Chemin de la carte en cours."""
        return self.cartes[self.index_courant]

    @property
    def numero_courant(self):
        """Numéro affiché (commence à 1 pour le joueur)."""
        return self.index_courant + 1

    @property
    def total(self):
        return len(self.cartes)

    @property
    def est_derniere(self):
        return self.index_courant >= len(self.cartes) - 1

    # ------------------------------------------------------------------
    def suivant(self):
        """Passe au niveau suivant. Retourne True si ok, False si c'était le dernier."""
        if self.est_derniere:
            return False
        self.index_courant += 1
        return True

    def recommencer(self):
        """Remet le niveau courant à zéro (utile après un game-over)."""
        pass  # l'index ne change pas ; main.py recharge simplement la même carte
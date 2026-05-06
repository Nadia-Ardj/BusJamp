import pygame
import math

class PassagerVisuel:
    def __init__(self, x_depart, y_depart, x_cible, y_cible, couleur_id, couleur_rgb, vitesse=5):
        self.x = x_depart
        self.y = y_depart
        self.x_cible = x_cible
        self.y_cible = y_cible
        self.couleur_id = couleur_id
        self.couleur_rgb = couleur_rgb
        self.vitesse = vitesse
        self.arrive = False

    def update(self):
        # Calculer la distance vers la cible(bus)
        dx = self.x_cible - self.x
        dy = self.y_cible - self.y
        distance = math.hypot(dx, dy)

        if distance <= self.vitesse:
            # Arrive au bus (destination )
            self.x = self.x_cible
            self.y = self.y_cible
            self.arrive = True
        else:
            # Se déplacer en direction de la cible
            self.x += (dx / distance) * self.vitesse
            self.y += (dy / distance) * self.vitesse

    def draw(self, screen):
        # On dessine un cercle de couleur pour représenter le passager

        pygame.draw.circle(screen, self.couleur_rgb, (int(self.x), int(self.y)), 10)
        # fairee un contour noir
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x), int(self.y)), 10, 1)


#----dessiner les personnages immobiles dans la file d'attente
def draw_file_attente(screen, personnages, file_x, file_y, cell_size):

    from lecture import COLORS
    #on dessine les 10 premiers personnages pour ne pas encombrer l'écran
    pour_dessin = personnages[:10]
    for idx, couleur_id in enumerate(pour_dessin):
        #on les aligne horizontalement vers la droite
        pos_x = file_x + idx * 25
        pos_y = file_y
        color = COLORS.get(couleur_id, (255, 255, 255))

        pygame.draw.circle(screen, color, (pos_x, pos_y), 10)
        pygame.draw.circle(screen, (0, 0, 0), (pos_x, pos_y), 10, 1)
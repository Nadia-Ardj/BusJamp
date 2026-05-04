COLORS = {
    0:    (220, 50, 50), #red
    1:   (50, 100, 220), #blue
    2:  (50, 180, 100), #green
    3: (240, 200, 50), #yellow
    4: (255, 140, 0),  #orange
    5: (160, 90, 200), #purple
    6:   (255, 120, 180), #pink
    7:   (50, 200, 200),  #cyan
    8: (149, 165, 166), #gris clair
    9:(155, 89, 182)    #violet
}

class Bus:
    def __init__(self, taille: int, direction: str, couleur: int, x: int, y: int, visite: bool, charge: int, capacite: int):
        self.taille = taille
        self.direction = direction  # U, D, L, R
        self.couleur = couleur
        self.x = x
        self.y = y
        self.visite = visite
        self.charge=charge
        self.capacite=capacite

    def __repr__(self):
        return f"Bus(taille={self.taille}, direction='{self.direction}', couleur={self.couleur}, x={self.x}, y={self.y}, visite={self.visite},capacite={self.capacite}, charge={self.charge})"



def lire_carte(carte):

    with open(carte, "r", encoding="utf_8") as flux:   ##Lire le fichier ligne par ligne sans \n ou les espaces non nécessaires (début/fin)
        lignes = [ligne.strip() for ligne in flux]

    taille_parking=int(lignes[0])

    personnages=[p for p in lignes[len(lignes)-1]]

    lignes=lignes[1:-1] #On enlève le premier et le dernier élément

    grille=[]

    for i, b in enumerate(lignes):     #Boucle pour construire la grille
        ligne=[]
        for c in range(0,len(b),4):     #Boucle pour construire les lignes de la grille
            if(b[c] != "X"):
                bus=Bus(x = i ,y=c//4 , capacite=int(b[c]), taille=int(b[c])//2, direction=b[c + 1], couleur=int(b[c + 2]),visite=False,charge=0)
            else:
                bus=Bus(x = i ,y=c//4 , capacite=0,taille=0,  direction="X", couleur="X",visite=False,charge=0)
            ligne.append(bus)
        grille.append(ligne)

    chauffeur=[]

    for i, ligne in enumerate(grille):
        for j, bus in enumerate(ligne):
            if not bus.visite:

                if bus.capacite==2:
                    bus.visite=True
                    chauffeur.append(bus)

                else:

                    if bus.direction=="U":

                        chauffeur.append(bus)

                        if bus.capacite!=0:
                            for k in range(i,i+bus.taille):
                                grille[k][j].visite=True
                        else:
                            k=i
                            while bus.couleur == grille[k][j].couleur and grille[k][j].direction == "U" and k<len(grille):
                                grille[k][j].visite = True
                                k+=1
                            bus.taille=k-i


                    elif bus.direction == "L":

                        chauffeur.append(bus)

                        if bus.capacite != 0:
                            for k in range(j, j + bus.taille ):
                                grille[i][k].visite = True

                        else:
                            k = j
                            while k < len(ligne) and grille[i][k].couleur == bus.couleur and grille[i][k].direction == "L":
                                grille[i][k].visite = True
                                k += 1
                            bus.taille = k - j

                    elif bus.direction=="D":

                        if bus.capacite != 0:
                            for k in range(i, i+bus.taille  ):
                                grille[k][j].visite = True
                        else:
                            k = i
                            while bus.couleur == grille[k][j].couleur and grille[k][j].direction == "D" and k < len(grille):
                                grille[k][j].visite = True
                                k += 1

                            grille[k-1][j].taille=k-i
                        chauffeur.append(grille[k-1][j])

                    elif bus.direction == "R":

                        if bus.capacite != 0:
                            for k in range(j, j+bus.taille):
                                grille[i][k].visite = True
                        else:
                            k = j
                            while bus.couleur == grille[i][k].couleur and grille[i][k].direction == "R" and k < len(ligne):
                                grille[i][k].visite = True
                                k += 1

                            grille[k - 1][j].taille =k - j
                        chauffeur.append(grille[i][k-1])

    return chauffeur, personnages, taille_parking

def est_jouable(grille, bus):

        if bus.direction=="U":
            if bus.x == 0:
                return True
            else:
                for i in range(bus.x-1,-1,-1):
                    if grille[i][bus.y].direction != "X":
                        return False

        if bus.direction=="L":
            if bus.y == 0:
                return True
            else:
                for i in range(bus.y-1,-1,-1):
                    if grille[bus.x][i].direction != "X":
                        return False

        if bus.direction=="D":
            if bus.x == len(grille)-1:
                return True
            else:
                for i in range(bus.x+1,len(grille)):
                    if grille[i][bus.y].direction != "X":
                        return False

        if bus.direction=="R":
            if bus.y == len(grille[bus.x])-1:
                return True
            else:
                for i in range(bus.y+1,len(grille[bus.x])):
                    if grille[bus.x][i].direction != "X":
                        return False
        return True




print(lire_carte("C:\\Users\\Lamine\\Desktop\\carte0.txt"))

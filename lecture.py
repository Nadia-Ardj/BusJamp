from ClasseBus import Bus,replace_black_with_color
from main import bus_images

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



def lire_carte(carte, bus_images):

    with open(carte, "r", encoding="utf_8") as flux:   ##Lire le fichier ligne par ligne sans \n ou les espaces non nécessaires (début/fin)
        lignes = [ligne.strip() for ligne in flux]

    taille_parking=int(lignes[0])

    personnages=[p for p in lignes[len(lignes)-1]]

    lignes=lignes[1:-1] #On enlève le premier et le dernier élément

    grid=[]

    for i, b in enumerate(lignes):
        ligne = []
        for c in range(0, len(b), 4):
          if b[c] != "X":
            capacite = int(b[c])
            direction = b[c + 1]
            couleur = int(b[c + 2])
            image = bus_images[couleur]
            bus = Bus(x=i,
                      y=c // 4,
                      capacite=capacite,
                      taille=capacite // 2,
                      direction=direction,
                      couleur=couleur,
                      visite=False,
                      charge=0,
                      image=replace_black_with_color(image, COLORS[couleur]))
          else:
              bus = Bus(x=i, y=c // 4, capacite=0, taille=0, direction="X", couleur="X", visite=False, charge=0,image=replace_black_with_color(image, COLORS[couleur]) )
              ligne.append(bus)
          grid.append(ligne)
    buses = []


    for i, ligne in enumerate(grid):
        for j, bus in enumerate(ligne):
            if not bus.visite:

                if bus.capacite==2:
                    bus.visite=True
                    buses.append(bus)

                else:

                    if bus.direction=="U":

                        buses.append(bus)

                        if bus.capacite!=0:
                            for k in range(i,i+bus.taille):
                                grid[k][j].visite=True
                        else:
                            k=i
                            while bus.couleur == grid[k][j].couleur and grid[k][j].direction == "U" and k<len(grid):
                                grid[k][j].visite = True
                                k+=1
                            bus.taille=k-i


                    elif bus.direction == "L":

                        buses.append(bus)

                        if bus.capacite != 0:
                            for k in range(j, j + bus.taille ):
                                grid[i][k].visite = True

                        else:
                            k = j
                            while k < len(ligne) and grid[i][k].couleur == bus.couleur and grid[i][k].direction == "L":
                                grid[i][k].visite = True
                                k += 1
                            bus.taille = k - j

                    elif bus.direction=="D":

                        if bus.capacite != 0:
                            for k in range(i, i+bus.taille  ):
                                grid[k][j].visite = True
                        else:
                            k = i
                            while bus.couleur == grid[k][j].couleur and grid[k][j].direction == "D" and k < len(grid):
                                grid[k][j].visite = True
                                k += 1

                            grid[k-1][j].taille=k-i
                        buses.append(grid[k-1][j])

                    elif bus.direction == "R":

                        if bus.capacite != 0:
                            for k in range(j, j+bus.taille):
                                grid[i][k].visite = True
                        else:
                            k = j
                            while bus.couleur == grid[i][k].couleur and grid[i][k].direction == "R" and k < len(ligne):
                                grid[i][k].visite = True
                                k += 1

                            grid[k - 1][j].taille =k - j
                        buses.append(grid[i][k-1])

    return buses, personnages, taille_parking

def est_jouable(grid, bus):

        if bus.direction=="U":
            if bus.x == 0:
                return True
            else:
                for i in range(bus.x-1,-1,-1):
                    if grid[i][bus.y].direction != "X":
                        return False

        if bus.direction=="L":
            if bus.y == 0:
                return True
            else:
                for i in range(bus.y-1,-1,-1):
                    if grid[bus.x][i].direction != "X":
                        return False

        if bus.direction=="D":
            if bus.x == len(grid)-1:
                return True
            else:
                for i in range(bus.x+1,len(grid)):
                    if grid[i][bus.y].direction != "X":
                        return False

        if bus.direction=="R":
            if bus.y == len(grid[bus.x])-1:
                return True
            else:
                for i in range(bus.y+1,len(grid[bus.x])):
                    if grid[bus.x][i].direction != "X":
                        return False
        return True


def parking_libre(parking, taille_parking):
    for i in range(0,taille_parking,2):
        if parking[0][i]==[]:
            return True
    return False

def empl_parking(parking, taille_parking):
    if parking_libre(parking, taille_parking):
        for i in range(0,taille_parking,2):
            if parking[0][i]==[]:
                return i



def deplacer_bus(buses, bus, parking, taille_parking):

    if bus.capacite!=0:
        if parking_libre(parking, taille_parking):
            j = empl_parking(parking, taille_parking)
            bus.direction = "U"
            parking[0][j]=bus
            buses.remove(bus)
    else:
        buses.remove(bus)


def est_plein(bus):
    return bus.capacite==bus.charge


def monter(parking, taille_parking, personnages):

    for i in range(0,taille_parking,2):
        if parking[0][i].couleur == personnages[0] and not est_plein(parking[0][i]):
            del personnages[0]
            parking[0][i].charge+=1
            return

def liberer_bus(parking, taille_parking):
    for i in range(0,taille_parking,2):
        if est_plein(parking[0][i]):
            del parking[0][i]


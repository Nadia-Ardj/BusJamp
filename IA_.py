from lecture import est_jouable


def peut_liberer_couleur(grid_temp, buses, couleur_cible):
    """
    Vérifie si un bus de la couleur_cible peut maintenant sortir
    dans la grille modifiée.
    """


    for b in buses:
        # On ne regarde que les bus de la couleur dont on a besoin
        if b.couleur_id == couleur_cible:
            # On vérifie si ce bus est devenu jouable grâce au mouvement précédent
            if est_jouable(grid_temp, b):
                return True
    return False


def choisir_meilleur_coup(buses, parking, personnages, grid, taille_parking):
    # 1. Lister les bus qui peuvent sortir (est_jouable)

    bus_jouables = [b for b in buses if est_jouable(grid, b)]

    if not bus_jouables or not personnages:
        return None

    # 2. Compter les premiers passagers de la même couleur (le groupe de tête)
    premiere_couleur = personnages[0]
    nb_passagers_groupe = 0
    for p_couleur in personnages:
        if p_couleur == premiere_couleur:
            nb_passagers_groupe += 1
        else:
            break

    # 3. Filtrer les bus jouables qui correspondent à cette couleur
    bus_bonne_couleur = [b for b in bus_jouables if b.couleur_id == premiere_couleur]

    if bus_bonne_couleur:
        # RÈGLE : Sortir celui qui a exactement la taille nécessaire OU le plus petit
        # On trie : d'abord ceux qui font exactement la taille du groupe, sinon par taille croissante
        bus_bonne_couleur.sort(key=lambda b: (b.taille != nb_passagers_groupe, b.taille))
        return bus_bonne_couleur[0].id

    # 4. RÈGLE DE LIBÉRATION : Si on doit sortir un bus pour en débloquer un autre
    # On cherche un bus jouable qui, une fois parti, libère un bus de la couleur du passager
    places_libres = parking.count(None)
    if places_libres > 0:
        for b in bus_jouables:
            # On simule temporairement la grille sans ce bus
            grid_temp = [row[:] for row in grid]
            # (Ici il faudrait vider les cases occupées par le bus b dans grid_temp)

            # Si après avoir enlevé 'b', un bus de la bonne couleur devient 'est_jouable'
            # alors on sacrifie une place au parking pour ce bus 'b'
            if peut_liberer_couleur(grid_temp, buses, premiere_couleur):
                return b.id

    # 5. Par défaut, si rien d'urgent, on prend le plus petit bus jouable pour économiser le parking
    bus_jouables.sort(key=lambda b: b.taille)
    return bus_jouables[0].id
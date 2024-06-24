from plateau import Plateau
import math
import copy
import random

class Etat_du_Jeu:
    def __init__(self, plateau, joueurs, joueur_jouant_index):
        self.plateau = copy.deepcopy(plateau)
        self.joueurs = copy.deepcopy(joueurs)
        self.joueur_jouant_index = joueur_jouant_index

    def verification_victoire(self):
        for joueur in self.joueurs:
            if len(joueur.territoires) == len(self.plateau.territoires):
                return True
        return False

    def obtenir_joueur_jouant(self):
        return self.joueurs[self.joueur_jouant_index]

    def tour_suivant(self):
        self.joueur_jouant_index = (self.joueur_jouant_index + 1) % len(self.joueurs)

    def copy(self):
        return Etat_du_Jeu(self.plateau, self.joueurs, self.joueur_jouant_index)


class Joueur:
    def __init__(self, nom, couleur):
        self.nom = nom
        self.couleur = couleur
        self.territoires = []

    def territoires_id(self):
        return [self.territoires[k].ID for k in range(len(self.territoires))]

    def ajouter_territoire(self, territoire):
        self.territoires.append(territoire)
        territoire.proprietaire = self

    def retirer_territoire(self, territoire):
        self.territoires = [t for t in self.territoires if t != territoire]

    def renfort(self, territoire, armees):
        if territoire in self.territoires:
            territoire.placer_armees(armees, self)
        else:
            raise ValueError("Le joueur ne controle pas ce territoire")


class Agent_de_Jeu(Joueur):
    def __init__(self, nom, couleur, jeu):
        super().__init__(nom, couleur)
        self.jeu = jeu

    def attaques_possibles(self):
        actions = []
        for territoire in self.territoires:
            if territoire.armees > 1:
                for id_voisin in territoire.ID_voisins:
                    voisin = self.jeu.plateau.trouver_territoire_par_id(id_voisin)
                    if voisin.proprietaire != self:
                        actions.append((territoire.ID, voisin.ID))
        return actions

    def armees_du_bonus_continent(self):
        bonus = 0
        for continent in self.jeu.plateau.continents:
            if all(territoire.proprietaire == self for territoire in continent.territoires):
                bonus += continent.armees_bonus
        return bonus

    def calculer_armees_tour_suivant(self):
        bonus_armee_defaut = max(3, len(self.territoires) // 3)
        continent_bonus = self.armees_du_bonus_continent()
        return bonus_armee_defaut + continent_bonus


class AgentMinMax(Agent_de_Jeu):
    def minimax(self, etat, profondeur, joueur_max):
        if profondeur == 0 or etat.verification_victoire():
            return self.evaluer(etat, self if joueur_max else etat.joueurs[(etat.joueur_jouant_index + 1) % len(etat.joueurs)])
        
        if joueur_max:
            max_eval = -math.inf
            meilleure_action = None
            for action in self.coups_possibles(etat):
                nouvel_etat = self.etat_resultant(etat, action)
                eval = self.minimax(nouvel_etat, profondeur - 1, False)
                if eval > max_eval:
                    max_eval = eval
                    meilleure_action = action
            return meilleure_action if profondeur == 3 else max_eval
        else:
            min_eval = math.inf
            meilleure_action = None
            for action in self.coups_possibles(etat):
                nouvel_etat = self.etat_resultant(etat, action)
                eval = self.minimax(nouvel_etat, profondeur - 1, True)
                if eval < min_eval:
                    min_eval = eval
                    meilleure_action = action
            return meilleure_action if profondeur == 3 else min_eval


        territoire_attaquant = nouvel_etat.plateau.trouver_territoire_par_id(territoire_attaquant_id)
        territoire_cible = nouvel_etat.plateau.trouver_territoire_par_id(territoire_cible_id)

        armees_attaquantes = territoire_attaquant.armees - 1
        nouvel_etat.attaque_deterministe(territoire_attaquant_id, territoire_cible_id, armees_attaquantes)

        return nouvel_etat

    def coups_possibles(self, etat):
        actions = []
        joueur_jouant = etat.obtenir_joueur_jouant()
        for territoire in joueur_jouant.territoires:
            if territoire.armees > 1:
                for id_voisin in territoire.ID_voisins:
                    neighbor = etat.plateau.trouver_territoire_par_id(id_voisin)
                    if neighbor.proprietaire != joueur_jouant:
                        actions.append((territoire.ID, neighbor.ID))
        return actions

    def evaluer(self, etat, joueur):
        # Evaluation logic goes here
        pass

    def attaque_minmax(self):
        meilleur_coup = self.minimax(self.jeu.obtenir_etat(), profondeur=3, joueur_max=True)

        territoire_attaquant, territoire_cible = meilleur_coup
        territoire_attaquant_obj = self.jeu.plateau.trouver_territoire_par_id(territoire_attaquant)

        armees_attaquantes = territoire_attaquant_obj.armees - 1

        self.jeu.attaque_deterministe(territoire_attaquant, territoire_cible, armees_attaquantes)


class Agent_aleatoire(Agent_de_Jeu):
    def attaque_alea(self):
        attaques_possibles = self.attaques_possibles()
        
        if not attaques_possibles:
            return

        attaque = random.choice(attaques_possibles)
        territoire_attaquant = self.jeu.plateau.trouver_territoire_par_id(attaque[0])
        territoire_cible = self.jeu.plateau.trouver_territoire_par_id(attaque[1])

        armees_attaquantes = territoire_attaquant.armees - 1
        self.jeu.attaque_stochastique(territoire_attaquant.ID, territoire_cible.ID, armees_attaquantes)


class Jeu:
    def __init__(self, joueurs):
        self.plateau = Plateau()
        self.joueurs = joueurs
        self.joueur_jouant_index = 0

        self.plateau.initialiser_plateau()
        self.distribuer_territoires()
        self.placement_initial_armees()

    def obtenir_etat(self):
        return Etat_du_Jeu(self.plateau, self.joueurs, self.joueur_jouant_index)

    def distribuer_territoires(self):
        territoires = self.plateau.territoires[:]
        random.shuffle(territoires)
        nb_joueurs = len(self.joueurs)
        for i, territoire in enumerate(territoires):
            joueur = self.joueurs[i % nb_joueurs]
            joueur.ajouter_territoire(territoire)

    def placement_initial_armees(self):
        for joueur in self.joueurs:
            armees_a_placer = 40
            joueur.total_armees = 40

            for territoire in joueur.territoires:
                if territoire.armees == 0:
                    territoire.armees += 1
                    armees_a_placer -= 1

            for _ in range(armees_a_placer):
                territoire = random.choice(joueur.territoires)
                territoire.armees += 1

    def boucle_de_jeu(self):
        while not self.verification_victoire():
            self.jouer_tour()
            self.tour_suivant()

    def jouer_tour(self):
        joueur_jouant = self.joueurs[self.joueur_jouant_index]
        print(f"C'est le tour de {joueur_jouant.nom}")
        self.phase_de_renfort(joueur_jouant)
        self.phase_attaque(joueur_jouant)
        self.phase_de_fortification(joueur_jouant)

        plotter = Plot(self)
        plotter.representation_territoires_controles()

    def phase_de_renfort(self, joueur):
        armees_a_placer = joueur.calculer_armees_tour_suivant()
        for _ in range(armees_a_placer):
            territoire = random.choice(joueur.territoires)
            territoire.armees += 1
        print(f"{joueur.nom} a renforcé ses territoires")

    def phase_attaque(self, joueur):
        if isinstance(joueur, AgentMinMax):
            joueur.attaque_minmax()
        elif isinstance(joueur, Agent_aleatoire):
            joueur.attaque_alea()
        else:
            self.human_phase_attaque(joueur)

    def phase_de_fortification(self, joueur):
        pass

    def tour_suivant(self):
        self.joueur_jouant_index = (self.joueur_jouant_index + 1) % len(self.joueurs)

    def verification_victoire(self):
        for joueur in self.joueurs:
            if len(joueur.territoires) == len(self.plateau.territoires):
                print(f"{joueur.nom} a gagné la partie!")
                return True
        return False

    def attaque_deterministe(self, territoire_attaquant_id, territoire_cible_id, armees_attaquantes):
        territoire_attaquant = self.plateau.trouver_territoire_par_id(territoire_attaquant_id)
        territoire_cible = self.plateau.trouver_territoire_par_id(territoire_cible_id)

        if territoire_cible_id not in territoire_attaquant.ID_voisins:
            raise ValueError("Le territoire cible n'est pas adjacent au territoire attaquant")

        if territoire_attaquant.proprietaire != self.joueurs[self.joueur_jouant_index]:
            raise ValueError("Le joueur ne détient pas le territoire d'attaque")
        if armees_attaquantes >= territoire_attaquant.armees:
            raise ValueError("Pas assez de troupes pour attaquer")

        armees_defenseur = territoire_cible.armees

        attack_vs_defense_probs = {
            (1, 1): (0.42, 0.58),
            (1, 2): (0.11, 0.89),
            (2, 1): (0.75, 0.25),
            (2, 2): (0.36, 0.64),
            (3, 1): (0.91, 0.09),
            (3, 2): (0.66, 0.34),
        }

        nb_des_attaquant = min(3, armees_attaquantes)
        nb_des_defendant = min(2, armees_defenseur)

        pertes_attaquant = 0
        pertes_defenseur = 0

        while armees_attaquantes > 1 and armees_defenseur > 0:
            prob = attack_vs_defense_probs[(nb_des_attaquant, nb_des_defendant)]
            if prob[0] > prob[1]:
                pertes_defenseur += 1
                armees_defenseur -= 1
            else:
                pertes_attaquant += 1
                armees_attaquantes -= 1

            nb_des_attaquant = min(3, armees_attaquantes)
            nb_des_defendant = min(2, armees_defenseur)

        territoire_attaquant.armees -= pertes_attaquant
        territoire_cible.armees -= pertes_defenseur

        if territoire_cible.armees <= 0:
            territoire_cible.proprietaire.retirer_territoire(territoire_cible)
            territoire_attaquant.proprietaire.ajouter_territoire(territoire_cible)
            territoire_cible.armees = armees_attaquantes - pertes_attaquant
            territoire_attaquant.armees -= (armees_attaquantes - pertes_attaquant)

        plotter = Plot(self)
        plotter.representation_territoires_controles()

    def attaque_stochastique(self, territoire_attaquant_id, territoire_cible_id, armees_attaquantes):
        territoire_attaquant = self.plateau.trouver_territoire_par_id(territoire_attaquant_id)
        territoire_cible = self.plateau.trouver_territoire_par_id(territoire_cible_id)

        if territoire_cible_id not in territoire_attaquant.ID_voisins:
            raise ValueError("Le territoire cible n'est pas adjacent au territoire attaquant")

        if territoire_attaquant.proprietaire != self.joueurs[self.joueur_jouant_index]:
            raise ValueError("Le joueur ne détient pas le territoire d'attaque")
        if armees_attaquantes >= territoire_attaquant.armees:
            raise ValueError("Pas assez de troupes pour attaquer")

        armees_defenseur = territoire_cible.armees

        nb_des_attaquant = min(3, armees_attaquantes)
        nb_des_defendant = min(2, armees_defenseur)

        while armees_attaquantes > 1 and armees_defenseur > 0:
            attack_rolls = sorted([random.randint(1, 6) for _ in range(nb_des_attaquant)], reverse=True)
            defense_rolls = sorted([random.randint(1, 6) for _ in range(nb_des_defendant)], reverse=True)

            for attack_roll, defense_roll in zip(attack_rolls, defense_rolls):
                if attack_roll > defense_roll:
                    armees_defenseur -= 1
                else:
                    armees_attaquantes -= 1

            nb_des_attaquant = min(3, armees_attaquantes)
            nb_des_defendant = min(2, armees_defenseur)

        territoire_attaquant.armees -= (territoire_attaquant.armees - armees_attaquantes)
        territoire_cible.armees = armees_defenseur

        if territoire_cible.armees <= 0:
            territoire_cible.proprietaire.retirer_territoire(territoire_cible)
            territoire_attaquant.proprietaire.ajouter_territoire(territoire_cible)
            territoire_cible.armees = armees_attaquantes - 1
            territoire_attaquant.armees -= (armees_attaquantes - 1)

        plotter = Plot(self)
        plotter.representation_territoires_controles()

    def evaluer(self):
        pass

class Plot:
    def __init__(self, partie: "Jeu"):
        self.partie = partie
        
        # Charger les positions des territoires depuis un fichier JSON
        with open("../Graphes/positions.json", "r") as f:
            import json
            self.positions = json.load(f)

    def representation_generale(self):
        import graph_tool.all as gt

        dict_adj = {u["id"]: u["ID_voisins"] for u in donnees_territoires}
        carte = gt.Graph(dict_adj, directed=False)
        gt.remove_parallel_edges(carte)

        couleur_territoire_continents = carte.new_vertex_property("string")
        pos = carte.new_vertex_property("vector<double>")
        vindex = carte.new_vertex_property("int")

        for v in carte.vertices():
            pos[v] = self.positions[str(int(v))]
            vindex[v] = int(v)
        carte.vp["pos"] = pos

        for c in self.partie.plateau.continents:
            couleur = c.couleur_def
            for t in c.territoires:
                couleur_territoire_continents[t.ID] = couleur

        gt.graph_draw(carte, pos=pos, vertex_fill_color=couleur_territoire_continents, vertex_text=vindex, fit_view=True, adjust_aspect=True, output="graphe.pdf")

    def representation_territoires_controles(self):
        import graph_tool.all as gt

        dict_adj = {self.partie.plateau.territoires[k].ID : self.partie.plateau.territoires[k].ID_voisins for k in range(len(self.partie.plateau.territoires))}

        carte = gt.Graph(dict_adj, directed=False)
        vertices_to_remove = [v for v in carte.obtenir_vertices() if int(v) not in dict_adj]
        for v in vertices_to_remove:
            carte.remove_vertex(v)

        gt.remove_parallel_edges(carte)

        couleur_territoire_joueur = carte.new_vertex_property("string")
        armee_territoire = carte.new_vertex_property("int")

        pos = carte.new_vertex_property("vector<double>")
        for v in carte.vertices():
            pos[v] = self.positions[str(int(v))]
        carte.vp["pos"] = pos

        for territoire in self.partie.plateau.territoires:
            proprietaire = territoire.proprietaire
            if proprietaire and proprietaire.couleur:
                couleur_territoire_joueur[territoire.ID] = proprietaire.couleur
            else:
                couleur_territoire_joueur[territoire.ID] = "#FFFFFF"  # Couleur par défaut pour les territoires sans propriétaire
            armee_territoire[territoire.ID] = territoire.armees

        gt.graph_draw(carte, pos=pos, vertex_fill_color=couleur_territoire_joueur, vertex_text=armee_territoire, fit_view=True, adjust_aspect=True, output="control_graphe.pdf")
        return carte

    def representation_adjacence_territoires(self):
        import graph_tool.all as gt

        dict_adj = {territoire.ID: territoire.ID_voisins for territoire in self.partie.plateau.territoires}

        carte = gt.Graph(directed=False)
        carte_sommets = {}
        for territoire in self.partie.plateau.territoires:
            sommet = carte.add_vertex()
            carte_sommets[territoire.ID] = sommet
        
        for territoire in self.partie.plateau.territoires:
            for voisin_id in territoire.ID_voisins:
                if voisin_id in carte_sommets:
                    carte.add_edge(carte_sommets[territoire.ID], carte_sommets[voisin_id])
        
        gt.remove_parallel_edges(carte)

        couleur_territoire = carte.new_vertex_property("vector<double>")
        pos = carte.new_vertex_property("vector<double>")

        for territoire in self.partie.plateau.territoires:
            pos[carte_sommets[territoire.ID]] = self.positions[str(territoire.ID)]
        carte.vp["pos"] = pos

        max_voisins_nb = 0
        max_autres_voisins_continent_nb = 0
        comptes_voisins = []
        comptes_autres_voisins_continent = []

        for territoire in self.partie.plateau.territoires:
            voisins_nb = len(territoire.ID_voisins)
            autres_voisins_continent_nb = len([
                voisin_id for voisin_id in territoire.ID_voisins
                if self.partie.plateau.trouver_territoire_par_id(voisin_id).continent != territoire.continent
            ])
            comptes_voisins.append(voisins_nb)
            comptes_autres_voisins_continent.append(autres_voisins_continent_nb)

            if voisins_nb > max_voisins_nb:
                max_voisins_nb = voisins_nb
            if autres_voisins_continent_nb > max_autres_voisins_continent_nb:
                max_autres_voisins_continent_nb = autres_voisins_continent_nb

        for idx, territoire in enumerate(self.partie.plateau.territoires):
            voisins_nb = comptes_voisins[idx]
            autres_voisins_continent_nb = comptes_autres_voisins_continent[idx]

            composante_rouge = (voisins_nb - 1) / max_voisins_nb
            composante_verte = 0  # autres_voisins_continent_nb / max_autres_voisins_continent_nb
            composante_bleue = 1 - composante_rouge
            composante_alpha = 1  # Opacité maximale

            couleur_territoire[carte_sommets[territoire.ID]] = [composante_rouge, composante_verte, composante_bleue, composante_alpha]

        gt.graph_draw(
            carte,
            pos=pos,
            vertex_fill_color=couleur_territoire,
            fit_view=True,
            adjust_aspect=True,
            output="neighbor_graph.pdf"
        )
        return carte

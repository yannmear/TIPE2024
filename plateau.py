from donnees import donnees_territoires
class Continent:
    def __init__(self, nom, armees_bonus, couleur_def="#ffffff"):
        self.nom = nom
        self.armees_bonus = armees_bonus
        self.territoires = []
        self.couleur_def = couleur_def
    
    def ajouter_territoire(self, territoire):
        self.territoires.append(territoire)

class Plateau :
    def __init__(self):
        self.territoires = []
        self.continents = []
    
    def noms_territoires(self):
        return list(map(lambda territoire:territoire.nom,self.territoires))

    def id_territoires(self):
        return list(map(lambda territoire:territoire.ID,self.territoires))

    def initialiser_plateau(self):
        # Initialisation des territoires et des continents
        A = Continent("Asie",7, "#88da8b")
        AN = Continent("Amérique du Nord",5,"#d8dc21")
        AS = Continent("Amérique du Sud",2,"#cb5046")
        EU = Continent("Europe",5,"#46c0db")
        OC = Continent("Océanie",2, "#a215a5" )
        AF = Continent("Afrique",3, "#9b7600" )

        self.continents.extend([A,AN,EU,AF,AS,OC])
        correspondance = {
            "A" : 0,
            "AN" : 1,
            "AS": 4,
            "EU": 2,
            "OC": 5,
            "AF": 3,}

        # Initialiser les territoires
        for donnee in donnees_territoires:
            territoire = Territoire(donnee["id"], donnee["nom"], donnee["continent"])
            self.territoires.append(territoire)
            self.continents[correspondance[donnee["continent"]]].ajouter_territoire(territoire)
        
        # Définir les voisins pour chaque territoire
        for donnee in donnees_territoires:
            territoire = self.trouver_territoire_par_id(donnee["id"])
            for id_voisin in donnee["ID_voisins"]:
                territoire.ajouter_voisin(id_voisin)

    def obtenir_nom_du_territoire(self, id):
        for territoire in self.territoires:
            if territoire.ID == id:
                return territoire.nom
        return None

    def obtenir_id_du_territoire(self, nom):
        for territoire in self.territoires:
            if territoire.nom == nom:
                return territoire.ID
        return None

    def trouver_territoire_par_id(self, id):
        for territoire in self.territoires:
            if territoire.ID == id:
                return territoire
        return None

class Territoire:
    def __init__(self, ID, nom, continent):
        self.ID = ID
        self.nom = nom
        self.continent = continent
        self.proprietaire = None
        self.armees = 0
        self.ID_voisins = []

    def ajouter_voisin(self,t_id):
        self.ID_voisins.append(t_id)
    

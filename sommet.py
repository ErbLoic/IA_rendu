"""Un sommet représente un état du jeu dans l'arbre de MCTS."""


class Sommet:
    def __init__(self, jeu, parent=None, coup=None):
        self._jeu = jeu
        self._parent = parent
        self._coup = coup              # Coup joué depuis le parent pour arriver ici.
        self._enfants = []
        self._visites = 0
        self._score = 0.0              # Somme des résultats des simulations.

    def get_jeu(self):
        return self._jeu

    def get_parent(self):
        return self._parent

    def get_coup(self):
        return self._coup

    def get_enfants(self):
        # Une copie empêche une autre classe de modifier la liste directement.
        return self._enfants[:]

    def get_visites(self):
        return self._visites

    def get_score(self):
        return self._score

    def ajouter_enfant(self, enfant):
        self._enfants.append(enfant)

    def maj_statistiques(self, resultat):
        self._visites = self._visites + 1
        self._score = self._score + resultat

    def est_complet(self):
        """Vrai si un enfant existe pour chaque coup possible."""
        return len(self._enfants) == len(self._jeu.coups_legaux())

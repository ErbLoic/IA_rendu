"""Joueur MinMax pour Manic Minelayers.

L'idée : j'essaie chaque coup possible. Après mon coup, je suppose que mon
adversaire jouera le meilleur coup possible pour lui, et ainsi de suite.
"""
from math import inf

from manicMinelayers import ManicMinelayers


class MinMax:
    def __init__(self, jeu=None, profondeur=4, heuristique=1):
        # Chaque joueur possède une instance de jeu, comme demandé dans le sujet.
        self._jeu = jeu if jeu is not None else ManicMinelayers()
        self._profondeur = profondeur
        self._heuristique = heuristique

    def get_jeu(self):
        return self._jeu

    def est_humain(self):
        return False

    def get_profondeur(self):
        return self._profondeur

    def set_profondeur(self, profondeur):
        self._profondeur = profondeur

    def choisir_coup(self, jeu=None, joueur=None):
        """Retourne le meilleur coup sans modifier le vrai jeu."""
        if jeu is None:
            jeu = self._jeu
        if joueur is None:
            joueur = jeu.get_joueur()

        coups = jeu.coups_legaux(joueur)
        if len(coups) == 0:
            return None

        meilleur_coup = coups[0]
        meilleur_score = -inf

        # On teste chacun de mes coups.
        for coup in coups:
            copie_jeu = jeu.copie()
            copie_jeu.jouer_coup(coup, joueur)

            score = self._chercher(
                copie_jeu,
                self._profondeur - 1,
                joueur,
                -inf,
                inf,
            )

            if score > meilleur_score:
                meilleur_score = score
                meilleur_coup = coup

        return meilleur_coup

    def _chercher(self, jeu, profondeur_restante, mon_numero, alpha, beta):
        """Partie récursive de MinMax avec élagage alpha-bêta."""
        # Une victoire vaut beaucoup plus qu'une évaluation habituelle.
        if jeu.est_terminee():
            gagnant = jeu.get_gagnant()
            if gagnant == mon_numero:
                return 100000 + profondeur_restante
            if gagnant == 0:
                return 0
            return -100000 - profondeur_restante

        # On ne regarde pas plus loin : on évalue simplement ce plateau.
        if profondeur_restante == 0:
            return self.evaluer(jeu, mon_numero)

        joueur_du_tour = jeu.get_joueur()
        coups = jeu.coups_legaux()

        if joueur_du_tour == mon_numero:
            # C'est mon tour : je garde le score le plus grand.
            meilleur_score = -inf
            for coup in coups:
                copie_jeu = jeu.copie()
                copie_jeu.jouer_coup(coup)
                score = self._chercher(copie_jeu, profondeur_restante - 1,
                                       mon_numero, alpha, beta)
                meilleur_score = max(meilleur_score, score)
                alpha = max(alpha, meilleur_score)
                if alpha >= beta:
                    break  # Les autres coups ne changeront plus la décision.
            return meilleur_score

        # C'est le tour de l'adversaire : il veut le score le plus petit pour moi.
        meilleur_score = inf
        for coup in coups:
            copie_jeu = jeu.copie()
            copie_jeu.jouer_coup(coup)
            score = self._chercher(copie_jeu, profondeur_restante - 1,
                                   mon_numero, alpha, beta)
            meilleur_score = min(meilleur_score, score)
            beta = min(beta, meilleur_score)
            if alpha >= beta:
                break
        return meilleur_score

    def evaluer(self, jeu, mon_numero):
        """Donne une note au plateau, quand on ne cherche pas plus loin.

        Heuristique 1 : comparer le nombre de coups disponibles.
        Heuristique 2 : mobilité + progression vers le côté adverse.
        """
        adversaire = 3 - mon_numero
        mes_coups = len(jeu.coups_legaux(mon_numero))
        coups_adversaire = len(jeu.coups_legaux(adversaire))

        if self._heuristique == 1:
            return 10 * (mes_coups - coups_adversaire)

        positions = jeu.get_positions()
        if positions[mon_numero] is None or positions[adversaire] is None:
            return 0  # pions pas encore posés : rien à évaluer
        ma_colonne = positions[mon_numero][1]
        colonne_adversaire = positions[adversaire][1]

        # Le joueur 1 avance vers la droite ; le joueur 2 vers la gauche.
        if mon_numero == 1:
            mon_avancement = ma_colonne
        else:
            mon_avancement = jeu.get_n() - 1 - ma_colonne
        if adversaire == 1:
            avancement_adversaire = colonne_adversaire
        else:
            avancement_adversaire = jeu.get_n() - 1 - colonne_adversaire

        return 6 * (mes_coups - coups_adversaire) + 2 * (mon_avancement - avancement_adversaire)


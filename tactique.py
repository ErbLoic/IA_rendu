"""Tactique gloutonne : évalue seulement l'état atteint par chaque coup."""
from manicMinelayers import ManicMinelayers


class TactiqueGloutonne:
    def __init__(self, jeu=None):
        self._jeu = jeu if jeu is not None else ManicMinelayers()

    def get_jeu(self):
        return self._jeu

    def est_humain(self):
        return False

    def choisir_coup(self, jeu=None, joueur=None):
        if jeu is None:
            jeu = self._jeu
        if joueur is None:
            joueur = jeu.get_joueur()

        meilleur_coup = None
        meilleur_score = -float("inf")

        for coup in jeu.coups_legaux(joueur):
            copie_jeu = jeu.copie()
            copie_jeu.jouer_coup(coup, joueur)

            # Si je gagne tout de suite, il est inutile de comparer les autres coups.
            if copie_jeu.get_gagnant() == joueur:
                return coup

            # Cette tactique est gloutonne : elle regarde uniquement le coup présent.
            mes_coups = len(copie_jeu.coups_legaux(joueur))
            coups_adversaire = len(copie_jeu.coups_legaux(3 - joueur))
            score = mes_coups - coups_adversaire

            if score > meilleur_score:
                meilleur_score = score
                meilleur_coup = coup

        return meilleur_coup

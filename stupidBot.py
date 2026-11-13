"""Joueur choisissant uniformément un coup licite."""
from random import choice
from manicMinelayers import ManicMinelayers


class StupidBot:
    def __init__(self, jeu=None):
        self._jeu = jeu if jeu is not None else ManicMinelayers()

    def get_jeu(self):
        return self._jeu

    def est_humain(self):
        return False

    def choisir_coup(self, jeu=None, joueur=None):
        if jeu is None:
            jeu = self._jeu
        coups = jeu.coups_legaux(joueur)
        if len(coups) == 0:
            return None
        return choice(coups)

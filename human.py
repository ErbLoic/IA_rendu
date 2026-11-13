"""Marqueur de joueur humain : les coups sont saisis dans la GUI."""
from manicMinelayers import ManicMinelayers


class Human:
    def __init__(self, jeu=None):
        self._jeu = jeu if jeu is not None else ManicMinelayers()

    def get_jeu(self):
        return self._jeu

    def est_humain(self):
        # La GUI attend un clic de souris au lieu d'appeler choisir_coup.
        return True

    def choisir_coup(self, jeu=None, joueur=None):
        raise RuntimeError("Un joueur humain choisit son coup à la souris dans la GUI.")

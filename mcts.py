"""Recherche Monte-Carlo (MCTS) expliquée en quatre étapes.

1. sélection : descendre dans l'arbre ;
2. expansion : ajouter un nouveau coup ;
3. simulation : finir une partie au hasard ;
4. rétropropagation : remonter le résultat dans l'arbre.
"""
from math import log, sqrt
from random import choice
from time import time

from manicMinelayers import ManicMinelayers
from sommet import Sommet


class MCTS:
    def __init__(self, jeu=None, iterations=500, temperature=1.41, temps_max=None):
        self._jeu = jeu if jeu is not None else ManicMinelayers()
        self._iterations = iterations
        self._temperature = temperature
        self._temps_max = temps_max      # en secondes, None = pas de limite

    def get_jeu(self):
        return self._jeu

    def est_humain(self):
        return False

    def get_iterations(self):
        return self._iterations

    def set_iterations(self, iterations):
        self._iterations = iterations

    def choisir_coup(self, jeu=None, joueur=None):
        if jeu is None:
            jeu = self._jeu
        if joueur is None:
            joueur = jeu.get_joueur()

        if len(jeu.coups_legaux(joueur)) == 0:
            return None

        # La racine est une copie : MCTS ne touche jamais à la vraie partie.
        racine = Sommet(jeu.copie())

        debut = time()
        for _ in range(self._iterations):
            if self._temps_max is not None and time() - debut > self._temps_max:
                break
            sommet = self._selection(racine, joueur)

            if not sommet.get_jeu().est_terminee():
                sommet = self._expansion(sommet)

            resultat = self._simulation(sommet.get_jeu(), joueur)
            self._retropropagation(sommet, resultat)

        enfants = racine.get_enfants()
        # Le coup le plus visité est celui qui a reçu le plus de simulations.
        meilleur_enfant = max(enfants, key=lambda enfant: enfant.get_visites())
        return meilleur_enfant.get_coup()

    def _selection(self, sommet, joueur_reference):
        """Descend dans l'arbre tant que toutes les possibilités sont connues."""
        while not sommet.get_jeu().est_terminee() and sommet.est_complet():
            enfants = sommet.get_enfants()
            if len(enfants) == 0:
                return sommet

            meilleur_enfant = enfants[0]
            meilleure_valeur = -float("inf")

            for enfant in enfants:
                valeur = self._valeur_uct(sommet, enfant, joueur_reference)
                if valeur > meilleure_valeur:
                    meilleure_valeur = valeur
                    meilleur_enfant = enfant

            sommet = meilleur_enfant

        return sommet

    def _valeur_uct(self, parent, enfant, joueur_reference):
        """Score UCT : succès moyen + bonus pour explorer les coups rares."""
        if enfant.get_visites() == 0:
            return float("inf")

        taux_victoire = enfant.get_score() / enfant.get_visites()

        # Au tour de l'adversaire, il faut choisir ce qui est mauvais pour nous.
        if parent.get_jeu().get_joueur() != joueur_reference:
            taux_victoire = 1 - taux_victoire

        bonus_exploration = self._temperature * sqrt(
            log(max(1, parent.get_visites())) / enfant.get_visites()
        )
        return taux_victoire + bonus_exploration

    def _expansion(self, sommet):
        """Crée un enfant en jouant un coup encore absent de l'arbre."""
        jeu = sommet.get_jeu()
        coups_deja_ajoutes = []
        for enfant in sommet.get_enfants():
            coups_deja_ajoutes.append(enfant.get_coup())

        coups_nouveaux = []
        for coup in jeu.coups_legaux():
            if coup not in coups_deja_ajoutes:
                coups_nouveaux.append(coup)

        coup = choice(coups_nouveaux)
        copie_jeu = jeu.copie()
        copie_jeu.jouer_coup(coup)

        enfant = Sommet(copie_jeu, sommet, coup)
        sommet.ajouter_enfant(enfant)
        return enfant

    def _simulation(self, jeu, joueur_reference):
        """Joue une partie entièrement au hasard depuis ce sommet."""
        copie_jeu = jeu.copie()

        while not copie_jeu.est_terminee():
            coup_au_hasard = choice(copie_jeu.coups_legaux())
            copie_jeu.jouer_coup(coup_au_hasard)

        gagnant = copie_jeu.get_gagnant()
        if gagnant == joueur_reference:
            return 1.0
        if gagnant == 0:
            return 0.5
        return 0.0

    def _retropropagation(self, sommet, resultat):
        """Ajoute le résultat à ce sommet puis à tous ses parents."""
        while sommet is not None:
            sommet.maj_statistiques(resultat)
            sommet = sommet.get_parent()

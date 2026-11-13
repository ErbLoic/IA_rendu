"""Concours entre IA, sans interface graphique.

Chaque duel est joué dans les deux sens (A commence, puis B commence)
pour étudier l'influence du joueur qui commence.
Lancer : python stats.py   (résultats affichés + fichier resultats.csv)
"""
from time import time

from manicMinelayers import ManicMinelayers
from stupidBot import StupidBot
from tactique import TactiqueGloutonne
from minMax import MinMax
from mcts import MCTS


def jouer_partie(joueur1, joueur2, m=5, n=10):
    """Joue une partie entière et retourne 1, 2 ou 0 (match nul)."""
    jeu = ManicMinelayers(m, n)
    joueurs = {1: joueur1, 2: joueur2}
    while not jeu.est_terminee():
        numero = jeu.get_joueur()
        coup = joueurs[numero].choisir_coup(jeu, numero)
        jeu.jouer_coup(coup, numero)
    return jeu.get_gagnant()


def tournoi(fabrique_joueur1, fabrique_joueur2, parties=100, m=5, n=10):
    """Joue plusieurs parties et compte les victoires de chaque joueur."""
    resultats = {"joueur_1": 0, "joueur_2": 0, "nuls": 0}
    for _ in range(parties):
        gagnant = jouer_partie(fabrique_joueur1(), fabrique_joueur2(), m, n)
        if gagnant == 1:
            resultats["joueur_1"] += 1
        elif gagnant == 2:
            resultats["joueur_2"] += 1
        else:
            resultats["nuls"] += 1
    return resultats


# Une "fabrique" crée un nouveau joueur pour chaque partie.
JOUEURS = {
    "StupidBot": lambda: StupidBot(),
    "Glouton": lambda: TactiqueGloutonne(),
    "MinMax_h1": lambda: MinMax(profondeur=3, heuristique=1),
    "MinMax_h2": lambda: MinMax(profondeur=3, heuristique=2),
    "MCTS": lambda: MCTS(iterations=200),
}

DUELS = [
    ("MinMax_h1", "StupidBot"),
    ("StupidBot", "Glouton"),
    ("MCTS", "MinMax_h2"),
    ("MinMax_h1", "MinMax_h2"),
    ("Glouton", "MinMax_h1"),
    ("MCTS", "StupidBot"),
    ("MCTS", "Glouton"),
]


if __name__ == "__main__":
    PARTIES = 100   # par sens, donc 200 parties par duel
    lignes = ["premier;second;victoires_premier;victoires_second;nuls;duree_s"]
    for a, b in DUELS:
        for premier, second in [(a, b), (b, a)]:
            debut = time()
            r = tournoi(JOUEURS[premier], JOUEURS[second], PARTIES)
            duree = round(time() - debut, 1)
            print(premier, "(commence) vs", second, ":", r, "-", duree, "s", flush=True)
            lignes.append(f"{premier};{second};{r['joueur_1']};{r['joueur_2']};{r['nuls']};{duree}")
    with open("resultats.csv", "w", encoding="utf-8") as fichier:
        fichier.write("\n".join(lignes) + "\n")

"""Lance une partie visible : on choisit les deux joueurs dans la console."""
from manicMinelayers import ManicMinelayers
from human import Human
from stupidBot import StupidBot
from tactique import TactiqueGloutonne
from minMax import MinMax
from mcts import MCTS


def creer_joueur(choix):
    if choix == "1":
        return Human()
    if choix == "2":
        return StupidBot()
    if choix == "3":
        return TactiqueGloutonne()
    if choix == "4":
        return MinMax(profondeur=4, heuristique=1)
    if choix == "5":
        return MinMax(profondeur=4, heuristique=2)
    return MCTS(iterations=500)


def demander_joueur(numero):
    print("Joueur", numero, ": 1-Humain 2-StupidBot 3-Glouton 4-MinMax h1 5-MinMax h2 6-MCTS")
    return creer_joueur(input("Votre choix : ").strip())


if __name__ == "__main__":
    joueur1 = demander_joueur(1)
    joueur2 = demander_joueur(2)
    jeu = ManicMinelayers(gui=True)
    jeu.lancer(joueur1, joueur2)

"""Moteur et interface graphique (Tkinter) du jeu Manic Minelayers.

Le plateau est une liste de listes. Chaque case contient :
    0 = case vide, 1 = pion du joueur 1, 2 = pion du joueur 2, 3 = marque.
Le moteur fonctionne sans fenêtre : les IA et les statistiques l'utilisent
directement. La fenêtre n'est créée que si on le demande (gui=True).
"""
from copy import deepcopy
from tkinter import Button, Label, Tk, messagebox


VIDE = 0
JOUEUR_1 = 1
JOUEUR_2 = 2
MARQUE = 3

COULEURS = {VIDE: "white", JOUEUR_1: "#65b9e8", JOUEUR_2: "#f5a34b", MARQUE: "#747474"}
TEXTES = {VIDE: "", JOUEUR_1: "1", JOUEUR_2: "2", MARQUE: "X"}
COULEUR_COUP_POSSIBLE = "#a9e7a0"

# Les 8 déplacements du cavalier aux échecs : (ligne, colonne).
DEPLACEMENTS_CAVALIER = [(2, 1), (2, -1), (-2, 1), (-2, -1),
                         (1, 2), (1, -2), (-1, 2), (-1, -2)]


class ManicMinelayers:
    """État d'une partie + interface graphique optionnelle."""

    def __init__(self, m=5, n=10, gui=False):
        if m < 1 or n < 2:
            raise ValueError("Le plateau doit avoir au moins 1 ligne et 2 colonnes.")
        self._m = m
        self._n = n
        self._plateau = [[VIDE] * n for _ in range(m)]
        self._positions = {JOUEUR_1: None, JOUEUR_2: None}
        self._joueur = JOUEUR_1          # joueur dont c'est le tour
        self._phase = "placement"        # "placement" puis "jeu"
        self._gagnant = None             # None = partie en cours, 0 = match nul
        # Partie graphique
        self._fenetre = None
        self._boutons = []
        self._statut = None
        self._joueurs = None             # (joueur1, joueur2) pour la GUI
        if gui:
            self.creer_interface()

    # ---------- Getters (on renvoie des copies pour protéger l'état) ----------
    def get_m(self):
        return self._m

    def get_n(self):
        return self._n

    def get_joueur(self):
        return self._joueur

    def get_phase(self):
        return self._phase

    def get_gagnant(self):
        return self._gagnant

    def get_plateau(self):
        return deepcopy(self._plateau)

    def get_positions(self):
        return self._positions.copy()

    def copie(self):
        """Copie de l'état du jeu (sans fenêtre), utilisée par les IA."""
        nouveau = ManicMinelayers(self._m, self._n)
        nouveau._plateau = deepcopy(self._plateau)
        nouveau._positions = self._positions.copy()
        nouveau._joueur = self._joueur
        nouveau._phase = self._phase
        nouveau._gagnant = self._gagnant
        return nouveau

    # ---------- Règles du jeu ----------
    def coups_legaux(self, joueur=None):
        """Liste des cases (ligne, colonne) où *joueur* peut aller."""
        if joueur is None:
            joueur = self._joueur
        if self._gagnant is not None:
            return []

        # Placement : première colonne pour J1, dernière colonne pour J2.
        if self._phase == "placement":
            if joueur != self._joueur:
                return []
            colonne = 0 if joueur == JOUEUR_1 else self._n - 1
            return [(ligne, colonne) for ligne in range(self._m)
                    if self._plateau[ligne][colonne] == VIDE]

        # Jeu : déplacements en L vers une case vide et dans le plateau.
        ligne, colonne = self._positions[joueur]
        coups = []
        for dl, dc in DEPLACEMENTS_CAVALIER:
            l, c = ligne + dl, colonne + dc
            if 0 <= l < self._m and 0 <= c < self._n and self._plateau[l][c] == VIDE:
                coups.append((l, c))
        return coups

    def jouer_coup(self, coup, joueur=None):
        """Joue *coup* pour le joueur courant. Lève ValueError si interdit."""
        if joueur is None:
            joueur = self._joueur
        if joueur != self._joueur:
            raise ValueError("Ce n'est pas le tour de ce joueur.")
        if coup not in self.coups_legaux(joueur):
            raise ValueError("Coup illicite : " + str(coup))

        ligne, colonne = coup
        if self._phase == "placement":
            self._plateau[ligne][colonne] = joueur
            self._positions[joueur] = coup
            if joueur == JOUEUR_1:
                self._joueur = JOUEUR_2
            else:
                self._joueur = JOUEUR_1
                self._phase = "jeu"
            return

        # Le pion quitte sa case et y laisse une marque.
        ancienne_ligne, ancienne_colonne = self._positions[joueur]
        self._plateau[ancienne_ligne][ancienne_colonne] = MARQUE
        self._plateau[ligne][colonne] = joueur
        self._positions[joueur] = coup

        adversaire = 3 - joueur
        if len(self.coups_legaux(adversaire)) == 0:
            # Adversaire bloqué : victoire si je peux encore bouger, sinon nul.
            if len(self.coups_legaux(joueur)) > 0:
                self._gagnant = joueur
            else:
                self._gagnant = 0
        else:
            self._joueur = adversaire

    def est_terminee(self):
        return self._gagnant is not None

    def afficher_console(self):
        symboles = {VIDE: ".", JOUEUR_1: "1", JOUEUR_2: "2", MARQUE: "X"}
        for ligne in self._plateau:
            print(" ".join(symboles[case] for case in ligne))

    # ---------- Interface graphique (Tkinter) ----------
    def creer_interface(self):
        if self._fenetre is not None:
            return
        self._fenetre = Tk()
        self._fenetre.title("Manic Minelayers")
        self._fenetre.minsize(700, 400)
        self._fenetre.bind("<Escape>", lambda event: self._fenetre.destroy())

        self._statut = Label(self._fenetre, font=("Arial", 16))
        self._statut.grid(row=0, column=0, columnspan=self._n, pady=10)

        self._boutons = []
        for ligne in range(self._m):
            self._fenetre.rowconfigure(ligne + 1, weight=1)
            ligne_boutons = []
            for colonne in range(self._n):
                self._fenetre.columnconfigure(colonne, weight=1)
                bouton = Button(self._fenetre, font=("Arial", 20, "bold"),
                                command=lambda l=ligne, c=colonne: self.clic_case(l, c))
                bouton.grid(row=ligne + 1, column=colonne, sticky="nsew", padx=2, pady=2)
                ligne_boutons.append(bouton)
            self._boutons.append(ligne_boutons)
        self.rafraichir()

    def rafraichir(self):
        """Redessine le plateau et le texte d'état."""
        if self._fenetre is None:
            return
        possibles = self.coups_legaux()
        for ligne in range(self._m):
            for colonne in range(self._n):
                valeur = self._plateau[ligne][colonne]
                couleur = COULEURS[valeur]
                if (ligne, colonne) in possibles:
                    couleur = COULEUR_COUP_POSSIBLE
                self._boutons[ligne][colonne].config(text=TEXTES[valeur], bg=couleur)

        if self._gagnant == 0:
            texte = "Match nul"
        elif self._gagnant is not None:
            texte = "Le joueur " + str(self._gagnant) + " gagne !"
        elif self._phase == "placement":
            texte = "Joueur " + str(self._joueur) + " : choisissez votre case de départ"
        else:
            texte = "Au tour du joueur " + str(self._joueur)
        self._statut.config(text=texte)

    def _tour_humain(self):
        """Vrai si le joueur courant joue à la souris."""
        if self._joueurs is None:
            return True                  # aucun joueur fourni : deux humains
        return self._joueurs[self._joueur - 1].est_humain()

    def clic_case(self, ligne, colonne):
        if self.est_terminee() or not self._tour_humain():
            return
        if (ligne, colonne) not in self.coups_legaux():
            return
        self.jouer_coup((ligne, colonne))
        self._apres_coup()

    def _apres_coup(self):
        self.rafraichir()
        if self.est_terminee():
            messagebox.showinfo("Fin de partie", self._statut.cget("text"))
        elif not self._tour_humain():
            # Petite pause pour que l'on puisse suivre les coups de l'IA.
            self._fenetre.after(400, self._jouer_ia)

    def _jouer_ia(self):
        ia = self._joueurs[self._joueur - 1]
        self.jouer_coup(ia.choisir_coup(self, self._joueur))
        self._apres_coup()

    def lancer(self, joueur1=None, joueur2=None):
        """Ouvre la fenêtre. Sans joueurs fournis, deux humains s'affrontent."""
        self.creer_interface()
        if joueur1 is not None and joueur2 is not None:
            self._joueurs = (joueur1, joueur2)
        self.rafraichir()
        if not self._tour_humain():
            self._fenetre.after(400, self._jouer_ia)
        self._fenetre.mainloop()


if __name__ == "__main__":
    ManicMinelayers(gui=True).lancer()

# Documentation technique - Manic Minelayers

Ce document explique comment le projet est construit : les données qu'on manipule,
le contenu de chaque classe et la façon dont les IA choisissent leurs coups.

## Organisation des fichiers

On a mis une classe par fichier, comme pour le Puissance 4 vu en TP.

```
Rendu/
  manicMinelayers.py   le jeu (règles + fenêtre Tkinter)
  human.py             joueur humain
  stupidBot.py         joueur au hasard
  tactique.py          tactique gloutonne (partie 2.7)
  minMax.py            MinMax avec alpha-bêta
  sommet.py            noeud de l'arbre utilisé par MCTS
  mcts.py              Monte-Carlo Tree Search
  stats.py             parties sans fenêtre et concours
  app.py               point d'entrée pour jouer une partie
```

Pour jouer on lance `python app.py`, pour les statistiques `python stats.py`.

Tous les attributs commencent par `_` : ils sont privés et on ne les lit
qu'avec des getters. Quand un getter renvoie une liste ou un dictionnaire, il
renvoie une copie. Comme ça, une IA ne peut pas modifier le plateau en douce,
elle est obligée de passer par `jouer_coup`, qui vérifie que le coup est permis.

Chaque joueur a la même méthode `choisir_coup(jeu, joueur)` qui renvoie une case
`(ligne, colonne)`. Le jeu et le fichier de stats n'ont donc pas besoin de savoir
quel type de joueur ils ont en face, ils appellent juste cette méthode.

## Structures de données

**Le plateau** est une liste de `m` listes de `n` entiers. Une case vaut :

| Valeur | Signification |
|---|---|
| 0 | case vide |
| 1 | pion du joueur 1 |
| 2 | pion du joueur 2 |
| 3 | marque laissée par un pion (case bloquée) |


**Les positions** des pions sont dans un dictionnaire
`{1: (ligne, colonne), 2: (ligne, colonne)}`. Avant le placement, la valeur est
`None`. On pourrait retrouver les pions en parcourant le plateau, mais garder
leur position évite de le faire à chaque coup.

**Les déplacements du cavalier** sont une liste de 8 décalages, par exemple
`(2, 1)` veut dire deux lignes plus bas et une colonne à droite. Pour trouver les
coups possibles, on ajoute chaque décalage à la position du pion et on garde les
cases qui sont dans le plateau et vides.

**Un coup** est simplement un tuple `(ligne, colonne)` : la case d'arrivée.

## Classe ManicMinelayers

C'est le coeur du projet. Elle connaît les règles, garde l'état de la partie et
peut afficher une fenêtre. La fenêtre est optionnelle : les IA et les stats
utilisent la classe sans jamais ouvrir de fenêtre, ce qui va beaucoup plus vite.

### Attributs

| Attribut | Rôle |
|---|---|
| `_m`, `_n` | nombre de lignes et de colonnes |
| `_plateau` | la grille décrite plus haut |
| `_positions` | position de chaque pion |
| `_joueur` | numéro du joueur dont c'est le tour (1 ou 2) |
| `_phase` | `"placement"` au début, puis `"jeu"` |
| `_gagnant` | `None` tant que la partie continue, 0 pour un nul, sinon 1 ou 2 |
| `_fenetre` | la fenêtre Tkinter (`None` si pas d'affichage) |
| `_boutons` | grille de boutons, un par case |
| `_statut` | le texte en haut de la fenêtre |
| `_joueurs` | les deux objets joueurs quand on lance une partie avec IA |

### Méthodes

| Méthode | Ce qu'elle fait |
|---|---|
| `get_m`, `get_n`, `get_joueur`, `get_phase`, `get_gagnant` | getters simples |
| `get_plateau`, `get_positions` | renvoient une copie |
| `copie()` | crée un nouveau jeu identique, sans fenêtre. Les IA s'en servent pour tester un coup |
| `coups_legaux(joueur)` | liste des cases où le joueur peut aller |
| `jouer_coup(coup, joueur)` | joue le coup, ou lève `ValueError` s'il est interdit |
| `est_terminee()` | vrai si on a un gagnant ou un nul |
| `afficher_console()` | affiche le plateau en texte, utile pour déboguer |
| `creer_interface()` | construit la fenêtre et la grille de boutons |
| `rafraichir()` | met à jour les couleurs et le texte |
| `clic_case(ligne, colonne)` | appelée quand on clique sur une case |
| `lancer(joueur1, joueur2)` | ouvre la fenêtre et démarre la partie |

### Déroulement d'un coup

Pendant le placement, `coups_legaux` renvoie les cases vides de la première
colonne pour le joueur 1 et de la dernière pour le joueur 2. Une fois les deux
pions posés, on passe en phase `"jeu"`.

Ensuite, `jouer_coup` met une marque (3) sur l'ancienne case, pose le pion sur la
nouvelle et regarde si l'adversaire peut encore bouger. S'il ne peut pas :

- si le joueur qui vient de jouer peut encore bouger, il gagne ;
- sinon les deux sont bloqués et c'est un match nul.

Si l'adversaire peut bouger, c'est simplement à lui de jouer.

### La fenêtre

On a choisi Tkinter. Chaque case est un bouton. Bleu pour le joueur 1, orange
pour le joueur 2, gris avec un X pour une marque, et vert pour les cases où le
joueur actuel a le droit d'aller. Quand c'est à une IA de jouer, on utilise
`fenetre.after(400, ...)` pour attendre un peu, sinon les coups s'enchaînent trop
vite pour être suivis à l'écran. Un clic est ignoré si ce n'est pas le tour d'un
humain.

## Classe Human

| Membre | Rôle |
|---|---|
| `_jeu` | instance de ManicMinelayers |
| `get_jeu()` | getter |
| `est_humain()` | renvoie `True` |
| `choisir_coup()` | lève une erreur |

L'humain ne choisit pas son coup par un appel de méthode : la fenêtre attend
qu'il clique. `est_humain()` sert justement à dire au jeu d'attendre un clic au
lieu d'appeler `choisir_coup`. Les autres joueurs renvoient `False`.

## Classe StupidBot

Mêmes attributs (`_jeu`). `choisir_coup` récupère les coups légaux et en tire un
avec `random.choice`. Il sert surtout de point de comparaison pour les autres IA.

## Classe TactiqueGloutonne (partie 2.7)

### Fonctionnement de `choisir_coup`

Pour chaque coup possible :

1. on copie le jeu et on joue le coup sur la copie ;
2. si ce coup fait gagner directement, on le renvoie sans chercher plus loin ;
3. sinon on calcule `score = mes coups possibles - coups possibles de l'adversaire` ;
4. on garde le coup qui a le meilleur score.

C'est glouton parce qu'on prend le meilleur choix tout de suite, à un seul coup
d'avance. On ne regarde jamais ce que l'adversaire va répondre, c'est la grosse
différence avec MinMax. L'avantage, c'est que c'est très rapide (100 parties en
une fraction de seconde). Le défaut, c'est qu'elle tombe dans des pièges qu'elle
ne voit pas venir.

## Classe MinMax

### Attributs

| Attribut | Rôle |
|---|---|
| `_jeu` | instance de ManicMinelayers |
| `_profondeur` | nombre de coups qu'on regarde à l'avance (3 ou 4 en pratique) |
| `_heuristique` | 1 ou 2, la fonction d'évaluation utilisée |

### Méthodes

| Méthode | Rôle |
|---|---|
| `get_jeu`, `get_profondeur`, `set_profondeur` | accès aux attributs |
| `choisir_coup(jeu, joueur)` | essaie chaque coup et garde le meilleur |
| `_chercher(jeu, profondeur, mon_numero, alpha, beta)` | la partie récursive |
| `evaluer(jeu, mon_numero)` | note un plateau avec l'heuristique choisie |

### Algorithme

On construit l'arbre des coups possibles. Quand c'est à nous de jouer, on prend
le coup qui donne le score le plus haut. Quand c'est à l'adversaire, on suppose
qu'il joue au mieux pour lui, donc on prend le score le plus bas. On descend
comme ça jusqu'à la profondeur fixée ou jusqu'à la fin de la partie.

Valeur d'une feuille :

- partie gagnée : `100000 + profondeur restante` ;
- partie perdue : `-100000 - profondeur restante` ;
- nul : 0 ;
- profondeur atteinte : on appelle `evaluer`.

On ajoute la profondeur restante pour que l'IA préfère gagner vite et, quand
elle perd de toute façon, perdre le plus tard possible.

### Élagage alpha-bêta

`alpha` est le meilleur score que je suis déjà sûr d'obtenir, `beta` le meilleur
que l'adversaire est sûr d'obtenir. Dès que `alpha >= beta`, la branche en cours
ne sera jamais choisie par l'un des deux, donc on arrête de l'explorer (`break`).
Le résultat est exactement le même qu'un MinMax classique, mais on visite
beaucoup moins de positions.

### Heuristique 1 : la mobilité

```
score = 10 × (mes coups possibles - coups possibles de l'adversaire)
```

Dans ce jeu, on perd quand on ne peut plus bouger. Le nombre de cases où l'on
peut aller est donc la mesure la plus directe de qui est en bonne position.

### Heuristique 2 : mobilité et avancée

```
score = 6 × (mes coups - coups adverses) + 2 × (mon avancée - avancée adverse)
```

L'avancée, c'est le nombre de colonnes parcourues vers le camp adverse (la
colonne du pion pour le joueur 1, `n - 1 - colonne` pour le joueur 2). L'idée de
départ était qu'aller vers l'adversaire permet de lui couper le chemin et de
l'enfermer près de son bord. On a baissé le poids de la mobilité pour que cette
deuxième partie ait vraiment un effet, sinon les deux heuristiques auraient
donné les mêmes coups.

Si un des pions n'est pas encore posé, on renvoie 0, il n'y a rien à mesurer.

### Ce qu'on a observé

L'heuristique 1 bat l'heuristique 2 à chaque partie. Avancer vers l'autre ne sert
à rien en soi, et ça pousse parfois l'IA à quitter une zone libre pour une zone
déjà pleine de marques. La mobilité seule est donc le meilleur critère qu'on ait
trouvé.

## Classe Sommet

Un sommet est un noeud de l'arbre de MCTS. La classe est récursive : chaque
sommet a des enfants qui sont eux-mêmes des sommets.

| Attribut | Rôle |
|---|---|
| `_jeu` | état du jeu à ce noeud (une copie) |
| `_parent` | sommet parent, `None` pour la racine |
| `_coup` | coup joué depuis le parent pour arriver ici |
| `_enfants` | liste des sommets enfants |
| `_visites` | nombre de simulations passées par ce noeud |
| `_score` | somme des résultats de ces simulations |

| Méthode | Rôle |
|---|---|
| getters | `get_jeu`, `get_parent`, `get_coup`, `get_enfants` (copie), `get_visites`, `get_score` |
| `ajouter_enfant(enfant)` | ajoute un enfant |
| `maj_statistiques(resultat)` | ajoute une visite et le résultat |
| `est_complet()` | vrai si tous les coups possibles ont déjà un enfant |

## Classe MCTS

### Attributs

| Attribut | Rôle |
|---|---|
| `_jeu` | instance de ManicMinelayers |
| `_iterations` | nombre maximum de simulations par coup (500 par défaut) |
| `_temperature` | constante d'exploration de la formule UCT (1,41 par défaut) |
| `_temps_max` | temps maximum en secondes, `None` pour ne pas limiter |

### Algorithme

On part d'une racine qui contient une copie du jeu, puis on répète quatre étapes
autant de fois que le permettent les itérations ou le temps :

1. **Sélection** (`_selection`). Tant que le sommet a déjà tous ses enfants, on
   descend vers celui qui a la meilleure valeur UCT.
2. **Expansion** (`_expansion`). On ajoute un enfant pour un coup qui n'a pas
   encore été essayé.
3. **Simulation** (`_simulation`). Depuis ce nouvel enfant, on finit la partie
   en jouant au hasard des deux côtés. On compte 1 si on gagne, 0,5 pour un nul,
   0 si on perd.
4. **Rétropropagation** (`_retropropagation`). On remonte jusqu'à la racine en
   ajoutant le résultat et une visite à chaque sommet traversé.

À la fin, on joue le coup de l'enfant de la racine qui a été visité le plus
souvent. On prend le plus visité et pas le meilleur taux, parce qu'un coup testé
deux fois avec deux victoires n'est pas plus fiable qu'un coup testé 150 fois
avec 70 % de réussite.

### Formule UCT

```
valeur = taux de victoire + température × racine( ln(visites du parent) / visites de l'enfant )
```

La première partie pousse vers les coups qui ont bien marché, la deuxième donne
un bonus aux coups peu testés. Plus la température est grande, plus l'IA explore.
Un enfant jamais visité a une valeur infinie, il est donc toujours essayé en
premier. Quand c'est au tour de l'adversaire dans l'arbre, on utilise
`1 - taux de victoire`, puisqu'il cherche ce qui est mauvais pour nous.

## Fichiers stats.py et app.py

`stats.py` contient deux fonctions. `jouer_partie(joueur1, joueur2)` joue une
partie complète sans fenêtre et renvoie le gagnant. `tournoi(...)` répète ça et
compte les victoires et les nuls. Chaque duel est joué 100 fois dans un sens puis
100 fois dans l'autre pour voir si commencer change quelque chose. Les résultats
sont affichés et écrits dans `resultats.csv`.

`app.py` demande dans la console qui joue (humain, StupidBot, glouton, MinMax h1,
MinMax h2 ou MCTS) puis ouvre la fenêtre.

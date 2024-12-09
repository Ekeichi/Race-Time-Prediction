  Ce repo est l'ébauche d'un projet en cours pour analyser plus simplement des données recueilli lors d'un entrainement. En effet, de manière générale, les outils à disposition actuellement ne permette pas au tout venant de bien traduire ce que sa montre lui donne. 
L'objectif ici est de rassembler une boîte à outils servant à aider l'utilisateur lambda dans sa pratique sportive.

  Dans un premier temps, le programme nommé time-prediction.py permet de donner une prédiction de temps de course, en fonction de la distance, du dénivelé et de la fréquence cardiaque moyenne. On utilise pour cela un dataset constitué d'un grand nombre de sortie de course à pied que l'on récupère grâce à l'API Strava (ce que le fichier extract_data.py permet de faire). On entraine ensuite un modèle simple de regression linéaire qui nous renvoie des coéfficient à appliquer pour calculer le temps de course. Ce premier projet m'a permi de comprendre comment fonctionne l'API Strava et d'entrevoir ce que je peux faire avec ces données.

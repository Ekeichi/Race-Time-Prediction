  Ce repository est l'ébauche d'un projet en cours pour analyser plus simplement des données recueilli lors d'un entrainement. En effet, de manière générale, les outils à disposition actuellement ne permette pas au tout venant de bien traduire ce que sa montre lui donne. 
L'objectif ici est de rassembler une boîte à outils servant à aider l'utilisateur lambda dans sa pratique sportive.

  Dans un premier temps, le programme nommé time-prediction.py permet de donner une prédiction de temps de course, en fonction de la distance, du dénivelé et de la fréquence cardiaque moyenne. On utilise pour cela un dataset constitué d'un grand nombre de sortie de course à pied que l'on récupère grâce à l'API Strava (ce que le fichier extract_data.py permet de faire). On entraine ensuite un modèle simple de regression linéaire qui nous renvoie des coéfficient à appliquer pour calculer le temps de course. Ce premier projet m'a permi de comprendre comment fonctionne l'API Strava et d'entrevoir ce que je peux faire avec ces données.

  Ensuite, j'ai pour objectif de concevoir une fonction permettant de donner l'état de fatigue de l'athlète après une sortie. On traduira cet état par un nombre, appelé score d'effort ou suffer_score. Ce score pourra ensuite être utilisé pour l'élaboration d'outils, notamment un indicateur simple et pertinent de fatigue ou de récupération. A l'avenir, on peut imaginer que ces valeurs seront utiles pour l'élaboration et l'ajustement en temps réel de plan d'entrainement. 

  L'objectif globale de cette démarche et de permettre à chaque athlète, novice ou expert, de s'appuyer sur des données interpretable facilement. Le ressenti ne sera pas le seul indicateur d'un état de fatigue ou de fraicheur. 


![Figure_1](https://github.com/user-attachments/assets/7b4c506e-9f14-49c2-beec-d5d6f2d0a82e)
![Figure_2](https://github.com/user-attachments/assets/20940dbe-f6b3-4f3a-b46b-03561ca4bf9c)

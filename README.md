# PeakFlow - Analyse de données d'entraînement sportif

PeakFlow est une application web qui vous permet d'analyser facilement vos données d'entraînement sportif en vous connectant à votre compte Strava. L'application récupère vos activités et fournit des analyses avancées pour vous aider à mieux comprendre votre entraînement, votre forme et votre fatigue.

## Fonctionnalités

- Connexion à l'API Strava pour récupérer vos activités
- Analyse détaillée de chaque activité avec:
  - Distribution des zones de fréquence cardiaque
  - Analyse de puissance (pour le cyclisme)
  - Prédiction de temps de course (pour la course à pied)
  - Calcul de score d'effort
  - Analyse de segments
- Visualisation des données avec graphiques
- Téléchargement des données au format CSV

## Installation

1. Clonez ce dépôt:
```bash
git clone https://github.com/yourusername/peakflow.git
cd peakflow
```

2. Créez un environnement virtuel et installez les dépendances:
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Créez un fichier `.env` à la racine du projet avec les informations suivantes:
```
FLASK_SECRET_KEY=votre_clé_secrète_flask
STRAVA_CLIENT_ID=votre_client_id_strava
STRAVA_CLIENT_SECRET=votre_client_secret_strava
STRAVA_REDIRECT_URL=http://localhost:5000/redirect
```

4. Lancez l'application:
```bash
python app.py
```

5. Accédez à l'application dans votre navigateur à l'adresse [http://localhost:5000](http://localhost:5000)

## Structure du projet

Le projet a été réorganisé en modules pour une meilleure maintenabilité:

- `app.py`: Point d'entrée principal de l'application Flask
- `peakflow/`: Package principal
  - `api/`: Module pour l'intégration avec l'API Strava
  - `models/`: Module pour les modèles d'analyse et de prédiction
  - `utils/`: Utilitaires divers
- `templates/`: Templates HTML pour l'interface utilisateur
- `data/`: Répertoire pour les données stockées

## Objectifs du projet

L'objectif de PeakFlow est de rendre les données d'entraînement plus accessibles et compréhensibles pour les athlètes de tous niveaux. Le projet vise à:

1. Fournir une interprétation claire des données recueillies lors des entraînements
2. Permettre à chaque athlète de suivre sa progression avec des indicateurs pertinents
3. Faciliter la prise de décision pour l'élaboration et l'ajustement des plans d'entraînement
4. Servir d'outil d'aide à l'optimisation des performances

À l'avenir, nous prévoyons d'ajouter:
- Un générateur de plans d'entraînement personnalisés
- Une analyse prédictive de la forme et de la fatigue
- Des recommandations d'entraînement basées sur vos données

## Captures d'écran

![Figure_1](https://github.com/user-attachments/assets/7b4c506e-9f14-49c2-beec-d5d6f2d0a82e)
![Figure_2](https://github.com/user-attachments/assets/20940dbe-f6b3-4f3a-b46b-03561ca4bf9c)
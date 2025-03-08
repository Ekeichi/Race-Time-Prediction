# PeakFlow - Analyse de données d'entraînement sportif

## À propos
PeakFlow est une application locale d'analyse de données d'entraînement sportif qui permet d'importer des fichiers CSV contenant des activités et de visualiser des analyses de performance avancées.

## Fonctionnalités
- Importation de données via fichiers CSV
- Analyse de zones cardiaques
- Modèle de fitness/fatigue
- Ratio charge aiguë/chronique (ACWR)
- Tableau de bord interactif
- Filtrage par période (7j, 1m, 3m, 6m, 1a)

## Utilisation
1. Lancer l'application: `python app.py`
2. Ouvrir un navigateur à l'adresse http://localhost:5001
3. Importer un fichier CSV d'activités
4. Explorer les graphiques d'analyse

## Structure du CSV
Le fichier CSV doit contenir les colonnes suivantes:
- activity_id: identifiant unique
- start_date_local: date et heure de l'activité
- type: type d'activité (Course, Vélo, etc.)
- distance: distance en km
- moving_time: durée de l'activité
- average_speed: vitesse moyenne en km/h
- suffer_score: score d'effort
- zone_0 à zone_5: temps passé dans chaque zone cardiaque (secondes)

## Notes personnelles
- Aucune connexion à l'API Strava requise
- Interface simplifiée sur une seule page
- Les données sont stockées localement dans le dossier 'data'
- Port par défaut: 5001
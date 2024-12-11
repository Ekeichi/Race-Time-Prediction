import requests
from flask import Flask, render_template, redirect, url_for
import json
import csv

app = Flask(__name__)

# Remplace par tes informations
CLIENT_ID = '141778'
CLIENT_SECRET = '"a334c280c5e9cd771d1a4659b58ce9e2cfe183f4'
REFRESH_TOKEN = 'cb0ffee179bd51fa97a6ac0787fcfa467b7f806e'
ACCESS_TOKEN = 'bbac68b38dda8e86d758e081b608b43633c21d2c'  # Token initial ou déjà rafraîchi

# Fonction pour rafraîchir le token d'accès
def refresh_token(refresh_token, client_id, client_secret):
    url = 'https://www.strava.com/api/v3/oauth/token'
    params = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    response = requests.post(url, data=params)
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        print(f"Erreur de rafraîchissement du token: {response.status_code}")
        return None

# Fonction pour récupérer les activités Strava
def get_activities(access_token):
    url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erreur lors de la récupération des activités: {response.status_code}")
        return []

# Fonction pour récupérer le stream des données de fréquence cardiaque
def get_activity_stream(activity_id, access_token, stream_type="heartrate"):
    url = f"https://www.strava.com/api/v3/activities/{activity_id}/streams"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "keys": stream_type,
        "key_by_type": True
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        streams = response.json()
        if stream_type in streams:
            return streams[stream_type]["data"]
        else:
            print(f"Le stream '{stream_type}' n'est pas disponible pour cette activité.")
            return None
    else:
        print(f"Erreur : {response.status_code} - {response.text}")
        return None

# Fonction pour définir les zones en fonction de la fréquence cardiaque
def define_zones(hr, hr_max):
    if hr < 0.5 * hr_max:
        return 0
    elif hr < 0.65 * hr_max:
        return 1
    elif hr < 0.81 * hr_max:
        return 2
    elif hr < 0.89 * hr_max:
        return 3
    elif hr < 0.97 * hr_max:
        return 4
    else:
        return 5

# Fonction pour calculer les zones et le score d'effort
def HR_zone(access_token, activity_id):
    heartrate_data = get_activity_stream(activity_id, access_token, stream_type="heartrate")
    zones = {0: [], 1: [], 2: [], 3: [], 4: [], 5: []}
    for hr in heartrate_data:
        if hr is None:  # Gestion des valeurs manquantes
            continue
        zone_point = define_zones(hr, hr_max=185)
        zones[zone_point].append(hr)
    return zones

# Fonction pour récupérer et rafraîchir les données, puis les afficher
@app.route('/refresh_data')
def refresh_data():
    global ACCESS_TOKEN

    # Rafraîchir le token d'accès
    ACCESS_TOKEN = refresh_token(REFRESH_TOKEN, CLIENT_ID, CLIENT_SECRET)
    if ACCESS_TOKEN is None:
        return "Erreur lors du rafraîchissement du token d'accès."

    # Récupérer les activités avec le token rafraîchi
    activities = get_activities(ACCESS_TOKEN)
    
    # Extraire les données nécessaires pour chaque activité
    activities_data = []
    for activity in activities:
        activity_id = activity['id']
        suffer_score = activity.get("suffer_score", "N/A")  # Valeur par défaut
        zones = HR_zone(ACCESS_TOKEN, activity_id)
        
        # Calcul du temps passé dans chaque zone
        time_in_zones = {zone: len(zones[zone]) for zone in zones}

        # Ajout des données à la liste
        activities_data.append({
            "activity_id": activity_id,
            "name": activity['name'],
            "suffer_score": suffer_score,
            "time_in_zones": json.dumps(time_in_zones)  # Sérialisation du dictionnaire
        })
    
    # Retourner à la page d'accueil avec les données mises à jour
    return render_template('index.html', activities=activities_data)

# Page d'accueil avec le bouton de rafraîchissement
@app.route('/')
def index():
    return render_template('index.html', activities=[])

# Fonction pour exporter les activités dans un fichier CSV
def export_to_csv(activities_data, filename="activities.csv"):
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["activity_id", "name", "suffer_score", "time_in_zones"])
        writer.writeheader()
        writer.writerows(activities_data)

# Lancer l'application
if __name__ == '__main__':
    app.run(debug=True)
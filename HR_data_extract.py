import requests
import csv
import pandas as pd

# Fonction pour obtenir les streams d'une activité
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
            print(f"Le stream '{stream_type}' n'est pas disponible pour l'activité {activity_id}.")
            return []
    else:
        print(f"Erreur : {response.status_code} - {response.text}")
        return []

# Définition des zones de fréquence cardiaque
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

# Calcul des temps passés dans chaque zone
def HR_zone(access_token, activity_id, hr_max=185):
    heartrate_data = get_activity_stream(activity_id, access_token)
    zones = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}  # Temps en secondes dans chaque zone
    for hr in heartrate_data:
        if hr is None:
            continue
        zone = define_zones(hr, hr_max)
        zones[zone] += 1  # Supposons une mesure par seconde
    return zones

# Fonction pour récupérer toutes les activités avec Suffer Score et HR zones
def get_all_activities_with_zones_and_suffer_score(access_token, per_page=30, output_csv="activities_with_details.csv"):
    url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    activities_data = []
    page = 1

    while True:
        params = {
            "page": page,
            "per_page": per_page
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            if not data:
                break
            for activity in data:
                activity_id = activity.get("id")
                suffer_score = activity.get("suffer_score", "N/A")
                
                # Récupérer les zones de fréquence cardiaque
                zones = HR_zone(access_token, activity_id)
                
                # Ajouter les données au tableau
                activity_details = {
                    "activity_id": activity_id,
                    "suffer_score": suffer_score,
                    **{f"zone_{z}": zones[z] for z in range(6)}  # Ajouter les temps dans chaque zone
                }
                activities_data.append(activity_details)
            page += 1
        else:
            print(f"Erreur lors de la récupération des activités : {response.status_code}")
            break

    # Exporter les données dans un fichier CSV
    fieldnames = ["activity_id", "suffer_score"] + [f"zone_{z}" for z in range(6)]
    with open(output_csv, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(activities_data)

    print(f"Les activités avec les zones et Suffer Score ont été exportées dans le fichier {output_csv}")

# Appel de la fonction principale
ACCESS_TOKEN = "81f79a4e01543f94a4b4f3d18637b76c81a45235"
get_all_activities_with_zones_and_suffer_score(ACCESS_TOKEN)

import requests
import json

# Fonction pour convertir la vitesse moyenne (m/s) en allure moyenne (min/km)
def speed_to_pace(speed_m_s):
    if speed_m_s > 0:
        pace_min_km = (1 / speed_m_s) * 1000 / 60
        return round(pace_min_km, 2)
    else:
        return None

# Configuration de l'accès API Strava
access_token = "5e45d9eeae8ff776a9868c88b45dbb28123b08df"  # Remplacez par votre token
url = "https://www.strava.com/api/v3/athlete/activities"
headers = {"Authorization": f"Bearer {access_token}"}

# Requête pour récupérer les activités (par défaut triées par date, la plus récente en premier)
response = requests.get(url, headers=headers, params={"per_page": 1, "page": 2})

if response.status_code == 200:
    activities = response.json()

    if activities:
        last_activity = activities[0]  # Prendre la première activité (la plus récente)
        
        # Extraire les données nécessaires
        name = last_activity.get("name")
        distance = last_activity.get("distance") / 1000  # Convertir en kilomètres
        elapsed_time = last_activity.get("elapsed_time") / 60  # Convertir en minutes
        average_speed = last_activity.get("average_speed")  # En m/s
        pace = speed_to_pace(average_speed)  # Allure en min/km
        elevation_gain = last_activity.get("total_elevation_gain")  # Dénivelé positif en mètres

        print("Dernière activité :")
        print(f"Nom : {name}")
        print(f"Distance : {distance:.2f} km")
        print(f"Temps écoulé : {elapsed_time:.2f} minutes")
        print(f"Allure moyenne : {pace} min/km")
        print(f"Dénivelé : {elevation_gain} m")
    else:
        print("Aucune activité trouvée.")
else:
    print(f"Erreur lors de la récupération des activités : {response.status_code}")
    print(response.text)
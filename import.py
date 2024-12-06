import requests
import json
import csv

# Votre token d'accès
access_token = "03b391e99bdcf19d9a424ea07f2761528db0997a"

# URL pour récupérer la liste des activités
url_activities = "https://www.strava.com/api/v3/athlete/activities"
headers = {"Authorization": f"Bearer {access_token}"}

# Nombre d'activités par page (maximum 200)
per_page = 1
# Définir le numéro de la première page
page = 1

# Chemin du fichier CSV pour exporter les données
output_file = "average_stats_per_run_activity_test.csv"

# Définir les en-têtes pour le CSV
keys = ["activity_name", "average_heart_rate", "total_time_seconds", "total_distance_km", "total_elevation_gain"]

# Ouvrir le fichier CSV pour écrire les données
with open(output_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=keys)
    writer.writeheader()

    while True:
        # Paramètres pour récupérer les activités
        params = {
            "per_page": per_page,
            "page": page
        }

        # Faire une requête GET pour récupérer les activités
        response = requests.get(url_activities, headers=headers, params=params)

        if response.status_code == 200:
            # Charger les données JSON
            activities = response.json()

            # Vérifier si des activités sont présentes
            if not activities:
                print(f"Aucune activité trouvée pour la page {page}. Fin de la récupération.")
                break

            # Parcourir chaque activité
            for activity in activities:
                if isinstance(activity, dict):  # S'assurer que 'activity' est un dictionnaire
                    activity_type = activity.get("type")

                    # Filtrer uniquement les activités de type "Run"
                    if activity_type == "Run":
                        activity_name = activity.get("name")
                        total_distance_meters = activity.get("distance")
                        total_time_seconds = activity.get("elapsed_time")
                        total_elevation_gain = activity.get("total_elevation_gain")

                        # Récupérer les détails de l'activité pour obtenir la FC moyenne
                        activity_id = activity.get("id")
                        url_activity_details = f"https://www.strava.com/api/v3/activities/{activity_id}"
                        response_activity_details = requests.get(url_activity_details, headers=headers)

                        if response_activity_details.status_code == 200:
                            # Charger les données détaillées de l'activité
                            activity_details = response_activity_details.json()
                            average_heart_rate = activity_details.get("average_heartrate", "N/A")  # FC moyenne

                            # Calculer la distance en kilomètres
                            total_distance_km = total_distance_meters / 1000

                            # Écrire les données dans le fichier CSV
                            writer.writerow({
                                "activity_name": activity_name,
                                "average_heart_rate": average_heart_rate,
                                "total_time_seconds": total_time_seconds,
                                "total_distance_km": total_distance_km
                            })

            # Passer à la page suivante
            print(f"Page {page} traitée.")
            # page += 1
            break
        else:
            print(f"Erreur lors de la récupération des activités : {response.status_code}")
            print(response.text)
            break

print(f"Données exportées dans le fichier {output_file}")
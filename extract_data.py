import requests
import csv
import json

class StravaDataExtractor:
   def __init__(self, access_token):
       self.access_token = access_token
       self.base_url = 'https://www.strava.com/api/v3'
       self.headers = {"Authorization": f"Bearer {access_token}"}
       
   def get_all_run_activities(self, per_page=200, output_file="strava_run_activities_comprehensive.csv"):
       """
       Récupère toutes les activités de course avec des métriques détaillées
       """
       # Définition exhaustive des clés pour le CSV
       keys = [
           # Informations générales
           "activity_name", "date", "type", 
           
           # Métriques de performance
           "total_distance_km", 
           "total_time_seconds", 
           "moving_time_seconds",
           "average_speed_km_h", 
           "max_speed_km_h", 
           "total_elevation_gain", 
           
           # Métriques physiologiques
           "average_heart_rate", 
           "max_heart_rate", 
           "suffer_score",
           
           # Métriques de puissance (si disponibles)
           "average_watts",
           "max_watts",
           
           # Métriques spécifiques course à pied
           "average_cadence",
       ]
       
       # Ouvrir le fichier CSV
       with open(output_file, mode="w", newline="", encoding="utf-8") as file:
           writer = csv.DictWriter(file, fieldnames=keys)
           writer.writeheader()
           
           # Initialiser la pagination
           page = 1
           
           while True:
               # Paramètres pour récupérer les activités
               params = {
                   "per_page": per_page,
                   "page": page
               }
               
               # Requête pour récupérer les activités
               response = requests.get(
                   f'{self.base_url}/athlete/activities', 
                   headers=self.headers, 
                   params=params
               )
               
               if response.status_code != 200:
                   print(f"Erreur lors de la récupération des activités : {response.status_code}")
                   print(response.text)
                   break
               
               # Charger les données JSON
               activities = response.json()
               
               # Vérifier si des activités sont présentes
               if not activities:
                   print(f"Aucune activité trouvée pour la page {page}. Fin de la récupération.")
                   break
               
               # Parcourir chaque activité
               for activity in activities:
                   # Filtrer uniquement les activités de type "Run"
                   if activity.get("type") == "Run":
                       try:
                           # Récupérer les détails complets de l'activité
                           activity_details = self.get_activity_details(activity.get("id"))
                           
                           if activity_details:
                               # Extraction des métriques détaillées
                               run_data = self.extract_comprehensive_metrics(activity, activity_details)
                               
                               # Écrire les données dans le fichier CSV
                               writer.writerow(run_data)
                       
                       except Exception as e:
                           print(f"Erreur lors du traitement d'une activité : {e}")
               
               print(f"Page {page} traitée.")
               page += 1
       
       print(f"Données exportées dans le fichier {output_file}")
   
   def get_activity_details(self, activity_id):
       """
       Récupère les détails détaillés d'une activité spécifique
       """
       try:
           response = requests.get(
               f'{self.base_url}/activities/{activity_id}', 
               headers=self.headers
           )
           
           if response.status_code == 200:
               return response.json()
           else:
               print(f"Erreur lors de la récupération des détails de l'activité {activity_id}")
               return None
       
       except Exception as e:
           print(f"Erreur lors de la récupération des détails de l'activité : {e}")
           return None
   
   def extract_comprehensive_metrics(self, activity, activity_details):
       """
       Extrait toutes les métriques disponibles pour une activité
       """
       return {
           # Informations générales
           "activity_name": activity.get("name", "N/A"),
           "date": activity.get("start_date_local", "N/A"),
           "type": activity.get("type", "N/A"),
           
           # Métriques de performance
           "total_distance_km": round(activity.get("distance", 0) / 1000, 2),
           "total_time_seconds": activity.get("elapsed_time", 0),
           "moving_time_seconds": activity.get("moving_time", 0),
           "average_speed_km_h": round(activity.get("average_speed", 0) * 3.6, 2),
           "max_speed_km_h": round(activity.get("max_speed", 0) * 3.6, 2),
           "total_elevation_gain": activity.get("total_elevation_gain", 0),
           
           # Métriques physiologiques
           "average_heart_rate": activity_details.get("average_heartrate", "N/A"),
           "max_heart_rate": activity_details.get("max_heartrate", "N/A"),
           "suffer_score": activity_details.get("suffer_score", "N/A"),
           
           # Métriques de puissance
           "average_watts": activity_details.get("average_watts", "N/A"),
           "max_watts": activity_details.get("max_watts", "N/A"),
           
           # Métriques spécifiques course à pied
           "average_cadence": activity.get("average_cadence", "N/A"),
       }


ACCESS_TOKEN = "749107f96bb1d165f7739a0687b67f60717ccc34"
   
# Création de l'extracteur
extractor = StravaDataExtractor(ACCESS_TOKEN)
   
# Exportation de toutes les activités de course en CSV
extractor.get_all_run_activities(output_file="strava_run_activities_comprehensive.csv")
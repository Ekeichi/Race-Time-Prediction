"""Module de gestion des données d'activité."""

import os
import csv
import json
from datetime import datetime
from peakflow.api.strava import StravaAPI
from peakflow.models.activity_analyzer import ActivityAnalyzer
from peakflow.models.power_analyzer import PowerAnalyzer

class DataManager:
    """Classe pour gérer les données des activités."""
    
    def __init__(self, csv_file="data/activities_with_details.csv"):
        """Initialise le gestionnaire de données."""
        self.csv_file = csv_file
        self.strava_api = StravaAPI()
        
    def fetch_and_save_activities(self):
        """Récupère toutes les activités avec leurs détails et les sauvegarde."""
        access_token = self.strava_api.get_access_token()
        if not access_token:
            return []
            
        # Récupération des activités de base
        activities = self.strava_api.get_all_activities()
        if not activities:
            return []
        
        # Enrichissement des données
        activities_data = []
        for activity in activities:
            # Extraire les informations de base
            activity_id = activity.get("id")
            activity_details = ActivityAnalyzer.extract_activity_details(activity)
            
            # Récupérer et ajouter les zones de fréquence cardiaque
            zones = self.strava_api.get_hr_zones(activity_id)
            activity_details.update({f"zone_{z}": zones[z] for z in range(6)})
            
            # Récupérer et traiter les streams
            streams = self.strava_api.get_activity_streams(activity_id)
            if streams:
                # Traiter les données de base (distance, temps, vitesse, altitude, fréquence cardiaque)
                streams_data = ActivityAnalyzer.process_streams_data(streams)
                activity_details.update(streams_data)
                
                # Calculer les segments
                distance_data = streams.get("distance", {}).get("data", [])
                time_data = streams.get("time", {}).get("data", [])
                velocity_data = streams.get("velocity_smooth", {}).get("data", [])
                segments = ActivityAnalyzer.calculate_segment_stats(distance_data, time_data, velocity_data)
                activity_details["segments"] = json.dumps(segments)
                
                # Traiter les données de puissance si disponibles
                watts_data = streams.get("watts", {}).get("data", [])
                if watts_data and activity.get("device_watts", False):
                    # FTP par défaut ou à personnaliser
                    ftp = 250  # À remplacer par une valeur stockée dans les préférences utilisateur
                    power_analysis = PowerAnalyzer.analyze_power_data(watts_data, ftp)
                    if power_analysis:
                        activity_details["power_analysis"] = json.dumps(power_analysis)
                        
                    power_data = PowerAnalyzer.process_power_data(streams)
                    if power_data:
                        activity_details["power_data"] = power_data
            
            activities_data.append(activity_details)
        
        # Assurer que le répertoire existe
        os.makedirs(os.path.dirname(self.csv_file), exist_ok=True)
        
        # Sauvegarder dans un fichier CSV
        self._save_to_csv(activities_data)
        
        return activities_data
    
    def _save_to_csv(self, activities_data):
        """Sauvegarde les données dans un fichier CSV."""
        if not activities_data:
            return
            
        # Déterminer les en-têtes à partir des clés de la première activité
        fieldnames = list(activities_data[0].keys())
        
        with open(self.csv_file, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(activities_data)
    
    def load_from_csv(self):
        """Charge les données depuis le fichier CSV."""
        try:
            with open(self.csv_file, mode="r", newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                activities = list(reader)
                
                # Convertir les chaînes JSON en objets Python
                for activity in activities:
                    json_fields = ["segments", "power_analysis", "power_data", 
                                  "pace_data", "elevation_data", "heartrate_data"]
                    for field in json_fields:
                        if field in activity and activity[field]:
                            try:
                                activity[field] = json.loads(activity[field])
                            except json.JSONDecodeError:
                                activity[field] = None
                
                return activities
        except FileNotFoundError:
            return []
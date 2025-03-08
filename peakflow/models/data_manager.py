"""Module de gestion des données d'activité."""

import os
import csv
import json
import sys
from datetime import datetime
from peakflow.models.activity_analyzer import ActivityAnalyzer
from peakflow.models.power_analyzer import PowerAnalyzer

# Augmenter la limite de taille des champs CSV
csv.field_size_limit(sys.maxsize)

class DataManager:
    """Classe pour gérer les données des activités."""
    
    def __init__(self, csv_file="data/activities_with_details.csv"):
        """Initialise le gestionnaire de données."""
        self.csv_file = csv_file
    
    def save_to_csv(self, activities_data):
        """Sauvegarde les données dans un fichier CSV."""
        if not activities_data:
            return
            
        # Déterminer les en-têtes à partir des clés de la première activité
        fieldnames = list(activities_data[0].keys())
        
        # Assurer que le répertoire existe
        os.makedirs(os.path.dirname(self.csv_file), exist_ok=True)
        
        with open(self.csv_file, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(activities_data)
        
        return True
    
    def load_from_csv(self, csv_file=None):
        """Charge les données depuis le fichier CSV.
        
        Args:
            csv_file: Optionnel, chemin vers un fichier CSV spécifique à charger.
                      Si non fourni, utilise le fichier CSV par défaut.
        """
        file_to_load = csv_file if csv_file else self.csv_file
        
        try:
            with open(file_to_load, mode="r", newline="", encoding="utf-8") as csvfile:
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
                
                # Si un fichier différent a été chargé, mettre à jour le fichier par défaut
                if csv_file and csv_file != self.csv_file:
                    self.save_to_csv(activities)
                
                return activities
        except FileNotFoundError:
            return []
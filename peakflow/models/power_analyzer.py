"""Module d'analyse de la puissance pour les activités cyclistes."""

import json
import numpy as np

class PowerAnalyzer:
    """Classe pour analyser les données de puissance des activités cyclistes."""
    
    @staticmethod
    def calculate_power_zones(ftp):
        """Calcule les zones de puissance basées sur le FTP."""
        return {
            'Z1': (0, round(0.55 * ftp)),
            'Z2': (round(0.55 * ftp), round(0.75 * ftp)),
            'Z3': (round(0.75 * ftp), round(0.90 * ftp)),
            'Z4': (round(0.90 * ftp), round(1.05 * ftp)),
            'Z5': (round(1.05 * ftp), round(1.20 * ftp)),
            'Z6': (round(1.20 * ftp), round(1.50 * ftp)),
            'Z7': (round(1.50 * ftp), float('inf'))
        }
    
    @staticmethod
    def analyze_power_data(watts_data, ftp):
        """Analyse les données de puissance pour une activité."""
        if not watts_data:
            return None
            
        # Filtrer les valeurs None et 0
        valid_watts = [w for w in watts_data if w is not None and w > 0]
        
        if not valid_watts:
            return None
            
        power_zones = PowerAnalyzer.calculate_power_zones(ftp)
        time_in_zones = {zone: 0 for zone in power_zones.keys()}
        
        # Calculer le temps passé dans chaque zone
        for watts in valid_watts:
            for zone, (min_watts, max_watts) in power_zones.items():
                if min_watts <= watts < max_watts:
                    time_in_zones[zone] += 1
                    break
                    
        return {
            'average_power': round(sum(valid_watts) / len(valid_watts), 2),
            'normalized_power': PowerAnalyzer.calculate_normalized_power(valid_watts),
            'max_power': max(valid_watts),
            'time_in_zones': time_in_zones,
            'intensity_factor': PowerAnalyzer.calculate_intensity_factor(valid_watts, ftp),
            'training_stress_score': PowerAnalyzer.calculate_tss(valid_watts, ftp),
            'power_curve': PowerAnalyzer.calculate_power_curve(valid_watts)
        }
    
    @staticmethod
    def calculate_normalized_power(watts_data):
        """Calcule la puissance normalisée."""
        if len(watts_data) < 30:
            return None
            
        # Moyenne mobile sur 30 secondes
        rolling_avg = []
        for i in range(len(watts_data) - 29):
            window = watts_data[i:i+30]
            rolling_avg.append(sum(window) / 30)
            
        # Élever à la 4ème puissance
        raised = [w ** 4 for w in rolling_avg]
        
        # Moyenne des valeurs
        avg = sum(raised) / len(raised)
        
        # Racine 4ème
        return round(avg ** 0.25, 2)
    
    @staticmethod
    def calculate_intensity_factor(watts_data, ftp):
        """Calcule le facteur d'intensité basé sur la puissance normalisée."""
        np = PowerAnalyzer.calculate_normalized_power(watts_data)
        if np is None:
            return None
        return round(np / ftp, 3)
    
    @staticmethod
    def calculate_tss(watts_data, ftp):
        """Calcule le Training Stress Score."""
        if not watts_data:
            return None
            
        duration_hours = len(watts_data) / 3600  # Convertir secondes en heures
        intensity_factor = PowerAnalyzer.calculate_intensity_factor(watts_data, ftp)
        
        if intensity_factor is None:
            return None
            
        return round(100 * duration_hours * intensity_factor ** 2, 1)
    
    @staticmethod
    def calculate_power_curve(watts_data):
        """Calcule la courbe de puissance (meilleures puissances sur différentes durées)."""
        if not watts_data:
            return None
            
        # Durées standards en secondes
        durations = [1, 5, 10, 30, 60, 300, 600, 1200, 3600]
        power_curve = {}
        
        for duration in durations:
            if len(watts_data) >= duration:
                max_power = 0
                for i in range(len(watts_data) - duration + 1):
                    avg_power = sum(watts_data[i:i+duration]) / duration
                    max_power = max(max_power, avg_power)
                power_curve[str(duration)] = round(max_power, 2)
                
        return power_curve
    
    @staticmethod
    def process_power_data(streams):
        """Traite les données de puissance à partir des streams d'une activité."""
        if not streams:
            return None
            
        watts_data = streams.get("watts", {}).get("data", [])
        if not watts_data:
            return None
            
        time_data = streams.get("time", {}).get("data", [])
        cadence_data = streams.get("cadence", {}).get("data", [])
        
        return json.dumps({
            "time": time_data,
            "watts": watts_data,
            "cadence": cadence_data
        }) if time_data and watts_data else None
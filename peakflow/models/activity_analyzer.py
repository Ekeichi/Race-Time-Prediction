"""Module d'analyse des activités sportives."""

import json
import datetime
import numpy as np

class ActivityAnalyzer:
    """Classe pour analyser les activités sportives."""
    
    @staticmethod
    def calculate_segment_stats(distance_data, time_data, velocity_data):
        """Calcule les statistiques pour chaque segment de l'activité."""
        segments = []
        if not distance_data or not time_data or not velocity_data:
            return segments
            
        for i in range(len(distance_data) - 1):
            segment = {
                'start_distance': round(distance_data[i] / 1000, 2),  # km
                'end_distance': round(distance_data[i + 1] / 1000, 2),  # km
                'duration': time_data[i + 1] - time_data[i],  # seconds
                'avg_speed': round(velocity_data[i] * 3.6, 2) if velocity_data[i] is not None else 0,  # km/h
                'instant_speed': round(velocity_data[i + 1] * 3.6, 2) if velocity_data[i + 1] is not None else 0  # km/h
            }
            segments.append(segment)
        return segments

    @staticmethod
    def extract_activity_details(activity):
        """Extrait les détails importants d'une activité Strava."""
        return {
            "activity_id": activity.get("id"),
            "name": activity.get("name", "N/A"),
            "type": activity.get("type", "N/A"),
            "start_date_local": activity.get("start_date_local", "N/A"),
            "distance": activity.get("distance", 0) / 1000,  # Conversion en km
            "moving_time": str(datetime.timedelta(seconds=activity.get("moving_time", 0))),
            "elapsed_time": str(datetime.timedelta(seconds=activity.get("elapsed_time", 0))),
            "total_elevation_gain": activity.get("total_elevation_gain", 0),
            "calories": activity.get("calories", 0),
            "average_speed": round((activity.get("average_speed", 0) * 3.6), 2),  # m/s to km/h
            "max_speed": round((activity.get("max_speed", 0) * 3.6), 2),  # m/s to km/h
            "average_heartrate": activity.get("average_heartrate", 0),
            "max_heartrate": activity.get("max_heartrate", 0),
            "suffer_score": activity.get("suffer_score", "N/A"),
            "weighted_average_watts": activity.get("weighted_average_watts", 0),
            "max_watts": activity.get("max_watts", 0),
            "kilojoules": activity.get("kilojoules", 0),
            "device_watts": activity.get("device_watts", False)
        }
    
    @staticmethod
    def process_streams_data(streams):
        """Traite les données de streams pour une activité."""
        if not streams:
            return {}
        
        # Données de base
        distance_data = streams.get("distance", {}).get("data", [])
        time_data = streams.get("time", {}).get("data", [])
        velocity_data = streams.get("velocity_smooth", {}).get("data", [])
        
        # Convertir distances
        distance_km = [d/1000 for d in distance_data] if distance_data else []
        
        # Convertir vitesses
        velocity_kmh = [round(v * 3.6, 2) if v is not None else None for v in velocity_data] if velocity_data else []
        
        return {
            "pace_data": json.dumps({
                "time": time_data,
                "distance": distance_km,
                "velocity": velocity_kmh
            }) if time_data and distance_km and velocity_kmh else None,
            
            "elevation_data": json.dumps({
                "distance": distance_km,
                "altitude": streams.get("altitude", {}).get("data", [])
            }) if distance_km and streams.get("altitude", {}).get("data", []) else None,
            
            "heartrate_data": json.dumps({
                "time": time_data,
                "heartrate": streams.get("heartrate", {}).get("data", [])
            }) if time_data and streams.get("heartrate", {}).get("data", []) else None
        }
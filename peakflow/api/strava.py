"""Module d'intégration avec l'API Strava."""

import os
import json
import requests
from datetime import datetime
import csv

class StravaAPI:
    """Classe pour interagir avec l'API Strava."""
    
    def __init__(self, token_file="strava_tokens.json"):
        """Initialise l'API Strava avec le fichier de tokens."""
        self.client_id = os.environ.get("STRAVA_CLIENT_ID")
        self.client_secret = os.environ.get("STRAVA_CLIENT_SECRET")
        self.redirect_url = os.environ.get("STRAVA_REDIRECT_URL")
        self.token_file = token_file
        self.tokens = self.load_tokens_from_file()
    
    def save_tokens_to_file(self, tokens):
        """Sauvegarde les tokens d'accès dans un fichier."""
        with open(self.token_file, "w") as f:
            json.dump(tokens, f)
        self.tokens = tokens
    
    def load_tokens_from_file(self):
        """Charge les tokens d'accès à partir d'un fichier."""
        try:
            with open(self.token_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return None
    
    def refresh_access_token(self):
        """Rafraîchit le token d'accès si nécessaire."""
        if not self.tokens:
            return None
            
        refresh_token = self.tokens.get("refresh_token")
        if not refresh_token:
            return None
            
        url = "https://www.strava.com/api/v3/oauth/token"
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        
        response = requests.post(url, params=params)
        if response.status_code == 200:
            tokens = response.json()
            self.save_tokens_to_file(tokens)
            return tokens
        else:
            print(f"Erreur lors du rafraîchissement du token : {response.text}")
            return None
    
    def get_authorization_url(self):
        """Génère l'URL d'autorisation pour l'API Strava."""
        return (f"https://www.strava.com/oauth/authorize"
                f"?client_id={self.client_id}"
                f"&response_type=code"
                f"&redirect_uri={self.redirect_url}"
                f"&approval_prompt=force"
                f"&scope=read_all,activity:read_all")
    
    def exchange_code_for_token(self, code):
        """Échange un code d'autorisation contre un token d'accès."""
        url = "https://www.strava.com/api/v3/oauth/token"
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code"
        }
        
        response = requests.post(url, params=params)
        if response.status_code == 200:
            tokens = response.json()
            self.save_tokens_to_file(tokens)
            return tokens
        else:
            print(f"Erreur lors de l'échange du code : {response.text}")
            return None
    
    def get_access_token(self):
        """Récupère un token d'accès valide, le rafraîchit si nécessaire."""
        if not self.tokens:
            return None
            
        if self.tokens.get("expires_at", 0) < datetime.now().timestamp():
            self.tokens = self.refresh_access_token()
        
        return self.tokens.get("access_token") if self.tokens else None
    
    def get_activity_streams(self, activity_id):
        """Récupère les données détaillées (streams) d'une activité."""
        access_token = self.get_access_token()
        if not access_token:
            return None
            
        url = f"https://www.strava.com/api/v3/activities/{activity_id}/streams"
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {
            "keys": "time,distance,velocity_smooth,heartrate,altitude,watts,cadence",
            "key_by_type": True
        }
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erreur lors de la récupération des streams pour l'activité {activity_id}: {response.status_code}")
            return None
    
    def get_hr_zones(self, activity_id):
        """Récupère les zones de fréquence cardiaque pour une activité donnée."""
        access_token = self.get_access_token()
        if not access_token:
            return {i: 0 for i in range(6)}
            
        url = f"https://www.strava.com/api/v3/activities/{activity_id}/zones"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            zones = response.json()
            hr_zones = {i: 0 for i in range(6)}
            for zone in zones:
                if zone["type"] == "heartrate":
                    for i, hr_data in enumerate(zone.get("distribution_buckets", [])):
                        hr_zones[i] = hr_data.get("time", 0)
            return hr_zones
        else:
            print(f"Erreur lors de la récupération des zones HR pour l'activité {activity_id}")
            return {i: 0 for i in range(6)}
    
    def get_all_activities(self, per_page=30, max_pages=None):
        """Récupère toutes les activités de base sans détails."""
        access_token = self.get_access_token()
        if not access_token:
            return []
            
        url = "https://www.strava.com/api/v3/athlete/activities"
        headers = {"Authorization": f"Bearer {access_token}"}
        activities = []
        page = 1
        
        while True:
            params = {"page": page, "per_page": per_page}
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if not data:
                    break
                    
                activities.extend(data)
                page += 1
                
                if max_pages and page > max_pages:
                    break
            else:
                print(f"Erreur lors de la récupération des activités (page {page}): {response.status_code}")
                break
        
        return activities
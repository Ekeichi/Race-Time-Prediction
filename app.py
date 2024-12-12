from flask import Flask, redirect, request, session, url_for, render_template, jsonify, send_file
import requests
import datetime
import os
import csv
import json

app = Flask(__name__)
app.secret_key = "votre_secret_key"

# Configuration Strava
CLIENT_ID = '141778'
CLIENT_SECRET = 'x'
REDIRECT_URL = "http://localhost:5000/redirect"  # URL de redirection
TOKEN_FILE = "strava_tokens.json"
CSV_FILE = "activities_with_details.csv"


def save_tokens_to_file(tokens):
    """Enregistre les tokens dans un fichier JSON."""
    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f)


def load_tokens_from_file():
    """Charge les tokens depuis un fichier JSON."""
    try:
        with open(TOKEN_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def refresh_access_token(refresh_token):
    """Rafraîchit le token d'accès Strava."""
    url = "https://www.strava.com/api/v3/oauth/token"
    params = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    response = requests.post(url, params=params)
    if response.status_code == 200:
        tokens = response.json()
        save_tokens_to_file(tokens)
        return tokens
    else:
        print(f"Erreur lors du rafraîchissement du token : {response.text}")
        return None


def HR_zone(access_token, activity_id):
    """Récupère les zones de fréquence cardiaque pour une activité donnée."""
    url = f"https://www.strava.com/api/v3/activities/{activity_id}/zones"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        zones = response.json()
        hr_zones = {i: 0 for i in range(6)}  # Initialiser un dictionnaire avec 6 zones
        for zone in zones:
            if zone["type"] == "heartrate":
                for i, hr_data in enumerate(zone.get("distribution_buckets", [])):
                    hr_zones[i] = hr_data.get("time", 0)
        return hr_zones
    else:
        print(f"Erreur lors de la récupération des zones HR pour l'activité {activity_id}")
        return {i: 0 for i in range(6)}


def get_all_activities_with_zones_and_suffer_score(access_token):
    """Récupère les activités avec zones et Suffer Score, puis les sauvegarde en CSV."""
    url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {"Authorization": f"Bearer {access_token}"}
    activities_data = []
    page = 1

    while True:
        params = {"page": page, "per_page": 30}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            if not data:
                break
            for activity in data:
                activity_id = activity.get("id")
                start_date = activity.get("start_date_local", "N/A")
                suffer_score = activity.get("suffer_score", "N/A")

                # Récupérer les zones de fréquence cardiaque
                zones = HR_zone(access_token, activity_id)

                # Ajouter les données au tableau
                activity_details = {
                    "activity_id": activity_id,
                    "start_date_local": start_date,
                    "suffer_score": suffer_score,
                    **{f"zone_{z}": zones[z] for z in range(6)}  # Ajouter les temps dans chaque zone
                }
                activities_data.append(activity_details)
            page += 1
        else:
            print(f"Erreur lors de la récupération des activités : {response.status_code}")
            break

    # Exporter les données dans un fichier CSV
    fieldnames = ["activity_id", "start_date_local", "suffer_score"] + [f"zone_{z}" for z in range(6)]
    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(activities_data)

    return activities_data


@app.route("/")
def index():
    """Page d'accueil avec instructions."""
    tokens = load_tokens_from_file()
    if not tokens:
        return redirect(url_for("authorize"))
    
    # Vérifier si le token est expiré
    if tokens["expires_at"] < datetime.datetime.now().timestamp():
        print("Token expiré, rafraîchissement en cours...")
        tokens = refresh_access_token(tokens["refresh_token"])
    
    return render_template("index.html", authorized=True)


@app.route("/authorize")
def authorize():
    """Redirige l'utilisateur pour autoriser l'application."""
    url = f"https://www.strava.com/oauth/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URL}&approval_prompt=force&scope=read_all,activity:read_all"
    return redirect(url)


@app.route("/redirect")
def redirect_uri():
    """Gère le callback après autorisation."""
    code = request.args.get("code")
    url = "https://www.strava.com/api/v3/oauth/token"
    params = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code"
    }
    response = requests.post(url, params=params)
    if response.status_code == 200:
        tokens = response.json()
        save_tokens_to_file(tokens)
        return redirect(url_for("index"))
    else:
        return f"Erreur : {response.text}"


@app.route("/activities")
def activities():
    """Affiche toutes les activités avec zones et Suffer Score."""
    tokens = load_tokens_from_file()
    if not tokens:
        return redirect(url_for("authorize"))
    
    # Rafraîchir le token si nécessaire
    if tokens["expires_at"] < datetime.datetime.now().timestamp():
        tokens = refresh_access_token(tokens["refresh_token"])

    # Récupérer les activités
    activities_data = get_all_activities_with_zones_and_suffer_score(tokens["access_token"])
    return render_template("activities.html", activities=activities_data)


@app.route("/download")
def download():
    """Télécharge le fichier CSV avec les activités."""
    if os.path.exists(CSV_FILE):
        return send_file(CSV_FILE, as_attachment=True)
    else:
        return "Aucun fichier disponible pour le téléchargement."


# Fichiers HTML dans le dossier templates (index.html, activities.html)
# 1. `index.html` inclut un lien vers `/authorize` ou `/activities`.
# 2. `activities.html` affiche les activités avec un lien pour télécharger le CSV.

if __name__ == "__main__":
    app.run(debug=True)
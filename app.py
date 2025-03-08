from flask import Flask, redirect, request, session, url_for, render_template, jsonify, send_file
import os
import json
import datetime
import polyline
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Importer les modules PeakFlow
from peakflow.api.strava import StravaAPI
from peakflow.models.data_manager import DataManager

# Initialiser l'application Flask
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "default_secret_key")

# Initialiser les gestionnaires
strava_api = StravaAPI()
data_manager = DataManager(csv_file="data/activities_with_details.csv")

@app.route("/")
def index():
    """Page d'accueil."""
    # Vérifier si l'utilisateur est authentifié
    if not strava_api.get_access_token():
        return redirect(url_for("authorize"))
    
    return render_template("index.html", authorized=True)

@app.route("/authorize")
def authorize():
    """Rediriger vers l'autorisation Strava."""
    return redirect(strava_api.get_authorization_url())

@app.route("/redirect")
def redirect_uri():
    """Gérer la redirection de Strava après autorisation."""
    code = request.args.get("code")
    if not code:
        return "Code d'autorisation manquant", 400
    
    tokens = strava_api.exchange_code_for_token(code)
    if not tokens:
        return "Erreur d'authentification", 400
    
    return redirect(url_for("index"))

@app.route("/activities")
def activities():
    """Afficher toutes les activités de l'utilisateur."""
    # Vérifier si l'utilisateur est authentifié
    if not strava_api.get_access_token():
        return redirect(url_for("authorize"))
    
    # Récupérer les activités
    activities_data = data_manager.fetch_and_save_activities()
    
    return render_template("activities.html", activities=activities_data)

@app.route("/activities/refresh")
def refresh_activities():
    """Rafraîchir les données des activités."""
    # Vérifier si l'utilisateur est authentifié
    if not strava_api.get_access_token():
        return redirect(url_for("authorize"))
    
    # Forcer le rafraîchissement des données
    activities_data = data_manager.fetch_and_save_activities()
    
    return redirect(url_for("activities"))

@app.route("/activities/load")
def load_activities():
    """Charger les activités depuis le fichier CSV sans API."""
    activities_data = data_manager.load_from_csv()
    
    return render_template("activities.html", activities=activities_data)

@app.route("/download")
def download():
    """Télécharger le fichier CSV des activités."""
    if os.path.exists(data_manager.csv_file):
        return send_file(data_manager.csv_file, as_attachment=True)
    else:
        return "Aucun fichier disponible pour le téléchargement.", 404

if __name__ == "__main__":
    # Assurer que le répertoire de données existe
    os.makedirs(os.path.dirname(data_manager.csv_file), exist_ok=True)
    
    # Lancer l'application
    app.run(debug=True)

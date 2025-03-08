from flask import Flask, redirect, request, session, url_for, render_template, jsonify, send_file, flash
import os
import json
import datetime
import polyline
import pandas as pd
import numpy as np
import matplotlib
# Utiliser le backend Agg (non-interactif) pour éviter les problèmes de thread
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

# Charger les variables d'environnement
load_dotenv()

# Importer les modules PeakFlow
from peakflow.models.data_manager import DataManager

# Initialiser l'application Flask
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "default_secret_key")

# Configuration pour le téléchargement de fichiers
UPLOAD_FOLDER = 'data/uploads'
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Créer le dossier d'upload s'il n'existe pas
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialiser le gestionnaire de données
data_manager = DataManager(csv_file="data/activities_with_details.csv")

def allowed_file(filename):
    """Vérifie si l'extension du fichier est autorisée."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET", "POST"])
def index():
    """Page d'accueil avec téléchargement de CSV et analyse combinés."""
    activities_data = data_manager.load_from_csv()
    upload_success = None
    
    if request.method == "POST":
        # Vérifier si un fichier a été fourni
        if 'file' not in request.files:
            upload_success = False
            return render_template("unified.html", 
                                  activities=activities_data, 
                                  upload_success=upload_success,
                                  error_message="Aucun fichier n'a été fourni")
            
        file = request.files['file']
        
        # Vérifier si un nom de fichier a été fourni
        if file.filename == '':
            upload_success = False
            return render_template("unified.html", 
                                  activities=activities_data, 
                                  upload_success=upload_success,
                                  error_message="Aucun fichier n'a été sélectionné")
            
        # Vérifier si le fichier est autorisé
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Charger les données depuis le fichier téléchargé
            activities_data = data_manager.load_from_csv(csv_file=filepath)
            upload_success = True
            
            return redirect(url_for("dashboard"))
        else:
            upload_success = False
            return render_template("unified.html", 
                                  activities=activities_data, 
                                  upload_success=upload_success,
                                  error_message="Type de fichier non autorisé. Seuls les fichiers CSV sont acceptés.")
    
    # Si aucune donnée chargée et première visite sur la page
    if not activities_data:
        return render_template("unified.html", activities=activities_data, show_upload=True)
    
    # Méthode GET - Rediriger vers le tableau de bord si des données existent
    return redirect(url_for("dashboard"))

@app.route("/download")
def download():
    """Télécharger le fichier CSV des activités."""
    if os.path.exists(data_manager.csv_file):
        return send_file(data_manager.csv_file, as_attachment=True)
    else:
        return "Aucun fichier disponible pour le téléchargement.", 404

def process_activities_data(activities_data):
    """Traite les données d'activités pour l'analyse."""
    # Convertir les données d'activités en DataFrame
    df = pd.DataFrame(activities_data)
    df['start_date_local'] = pd.to_datetime(df['start_date_local'])
    df['date'] = df['start_date_local'].dt.date
    
    # Calculer le score d'effort relatif pour chaque activité
    zone_weights = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5}
    
    def calculate_relative_effort(row):
        return sum((int(row.get(f'zone_{zone}', 0))/60) * np.exp(weight) for zone, weight in zone_weights.items())
    
    df['relative_effort'] = df.apply(calculate_relative_effort, axis=1)
    
    # Agréger par jour
    daily_effort = df.groupby('date')['relative_effort'].sum().reset_index()
    
    # Générer toutes les dates
    date_range = pd.date_range(start=daily_effort['date'].min(), end=daily_effort['date'].max())
    df_full = pd.DataFrame({'date': date_range.date})
    
    # Fusionner avec les efforts quotidiens
    df_full = df_full.merge(daily_effort, on='date', how='left')
    df_full['relative_effort'] = df_full['relative_effort'].fillna(0)
    
    return df_full

def filter_data_by_period(df_full, period):
    """Filtre les données en fonction de la période sélectionnée."""
    today = pd.Timestamp.now().date()
    
    if period == '7d':
        # Derniers 7 jours
        start_date = today - pd.Timedelta(days=7)
    elif period == '1m':
        # Dernier mois
        start_date = today - pd.Timedelta(days=30)
    elif period == '3m':
        # Derniers 3 mois
        start_date = today - pd.Timedelta(days=90)
    elif period == '6m':
        # Derniers 6 mois
        start_date = today - pd.Timedelta(days=180)
    elif period == '1y':
        # Dernière année
        start_date = today - pd.Timedelta(days=365)
    else:
        # Toutes les données
        return df_full
    
    return df_full[df_full['date'] >= start_date]

def generate_acwr_chart(activities_data, period='all'):
    """Génère le graphique d'évolution du ratio ACWR."""
    df_full = process_activities_data(activities_data)
    
    # Calcul de la charge aiguë (7 jours)
    charge_aigue = []
    for i in range(len(df_full)):
        last_7_days = df_full.iloc[max(0, i-6):i+1]
        ca = (last_7_days["relative_effort"].sum()/7)
        charge_aigue.append(ca)
    df_full["Charge_aigue"] = charge_aigue
    
    # Calcul de la charge chronique (28 jours)
    charge_chronique = []
    for i in range(len(df_full)):
        last_28_days = df_full.iloc[max(0, i-27):i+1]
        cc = (last_28_days["relative_effort"].sum()/28)
        charge_chronique.append(cc)
    df_full["Charge_chronique"] = charge_chronique
    
    # Calcul du ratio ACWR
    df_full['Ratio_AC'] = df_full['Charge_aigue'] / df_full['Charge_chronique'].replace(0, np.nan)
    df_full['Ratio_AC'] = df_full['Ratio_AC'].fillna(0)
    
    # Filtrer par période
    filtered_df = filter_data_by_period(df_full, period)
    
    # Création du graphique
    plt.figure(figsize=(10, 5))
    plt.plot(filtered_df['date'], filtered_df['Ratio_AC'], label='ACWR', color='green')
    plt.axhline(y=1.5, color='r', linestyle='--', label='Limite haute (1.5)')
    plt.axhline(y=0.8, color='b', linestyle='--', label='Limite basse (0.8)')
    
    # Titre avec indication de la période
    period_labels = {'7d': '7 derniers jours', '1m': 'dernier mois', '3m': '3 derniers mois',
                     '6m': '6 derniers mois', '1y': 'dernière année', 'all': 'toute la période'}
    plt.title(f'Évolution du Ratio Charge Aiguë / Charge Chronique (ACWR) - {period_labels[period]}')
    
    plt.xlabel('Date')
    plt.ylabel('Ratio')
    plt.legend()
    plt.grid()
    plt.tight_layout()
    
    # Convertir le graphique en image base64
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    return base64.b64encode(img.getvalue()).decode('utf-8')

def generate_fitness_fatigue_chart(activities_data, period='all'):
    """Génère le graphique d'évolution de la fatigue, forme et performance."""
    df_full = process_activities_data(activities_data)
    
    # Fonctions pour calculer la fatigue et la fitness
    def fatigue(fatigue_pre, effort):
        tau = 15
        fatigue_post = (effort + np.exp(-1/tau)*fatigue_pre)
        return fatigue_post

    def fitness(fitness_pre, effort):
        tau = 45
        fitness_post = effort + (np.exp(-1/tau)) * fitness_pre
        return fitness_post
    
    # Calcul des courbes
    courbe_fatigue = [0]
    courbe_fitness = [0]
    courbe_performance = [0]
    courbe_forme = [0]
    
    for i in range(len(df_full) - 1):
        effort = df_full.iloc[i + 1]["relative_effort"]
        instant_fatigue = fatigue(courbe_fatigue[-1], effort)
        instant_fitness = fitness(courbe_fitness[-1], effort)
        instant_performance = (instant_fitness - instant_fatigue)/2
        instant_forme = instant_fitness - 2*instant_fatigue
        
        courbe_fatigue.append(instant_fatigue)
        courbe_fitness.append(instant_fitness)
        courbe_performance.append(instant_performance)
        courbe_forme.append(instant_forme)
    
    # Ajouter les courbes au DataFrame
    df_full['fatigue'] = courbe_fatigue
    df_full['forme'] = courbe_forme
    df_full['performance'] = courbe_performance
    
    # Filtrer par période
    filtered_df = filter_data_by_period(df_full, period)
    
    # Création du graphique
    plt.figure(figsize=(10, 5))
    plt.plot(filtered_df['date'], filtered_df['fatigue'], label="Fatigue", color="red", linewidth=2)
    plt.plot(filtered_df['date'], filtered_df['forme'], label="Forme", color="green", linewidth=2)
    plt.plot(filtered_df['date'], filtered_df['performance'], label="Performance", color="blue", linewidth=2)
    
    # Titre avec indication de la période
    period_labels = {'7d': '7 derniers jours', '1m': 'dernier mois', '3m': '3 derniers mois',
                     '6m': '6 derniers mois', '1y': 'dernière année', 'all': 'toute la période'}
    plt.title(f'Évolution de la Fatigue, de la Forme et de la Performance - {period_labels[period]}')
    
    plt.xlabel("Date")
    plt.ylabel("Valeurs")
    plt.legend()
    plt.grid()
    plt.tight_layout()
    
    # Convertir le graphique en image base64
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    return base64.b64encode(img.getvalue()).decode('utf-8')

def generate_fatigue_performance_ratio_chart(activities_data, period='all'):
    """Génère le graphique du rapport entre fatigue et performance."""
    df_full = process_activities_data(activities_data)
    
    # Fonctions pour calculer la fatigue et la fitness
    def fatigue(fatigue_pre, effort):
        tau = 15
        fatigue_post = (effort + np.exp(-1/tau)*fatigue_pre)
        return fatigue_post

    def fitness(fitness_pre, effort):
        tau = 45
        fitness_post = effort + (np.exp(-1/tau)) * fitness_pre
        return fitness_post
    
    # Calcul des courbes
    courbe_fatigue = [0]
    courbe_fitness = [0]
    courbe_performance = [0]
    courbe_rapport = [0]
    
    for i in range(len(df_full) - 1):
        effort = df_full.iloc[i + 1]["relative_effort"]
        instant_fatigue = fatigue(courbe_fatigue[-1], effort)
        instant_fitness = fitness(courbe_fitness[-1], effort)
        instant_performance = (instant_fitness - instant_fatigue)/2
        
        # Gérer les cas de division par zéro ou de performance négative
        if instant_performance > 0.001:  # Seuil minimal pour éviter la division par des valeurs proches de zéro
            rapport = (instant_fatigue/instant_performance)*100
            # Limiter les valeurs extrêmes
            rapport = min(rapport, 200)
        else:
            # Valeur par défaut pour les cas problématiques
            rapport = 150
        
        courbe_fatigue.append(instant_fatigue)
        courbe_fitness.append(instant_fitness)
        courbe_performance.append(instant_performance)
        courbe_rapport.append(rapport)
    
    # Ajouter le rapport au DataFrame
    df_full['rapport'] = courbe_rapport
    
    # Filtrer par période
    filtered_df = filter_data_by_period(df_full, period)
    
    # Création du graphique
    plt.figure(figsize=(10, 5))
    plt.plot(filtered_df['date'], filtered_df['rapport'], color='black')
    plt.axhspan(150, 200, color='red', alpha=0.2, label="Excessive")
    plt.axhspan(100, 150, color='orange', alpha=0.2, label="Optimized")
    plt.axhspan(80, 100, color='yellow', alpha=0.2, label="Maintaining")
    plt.axhspan(50, 80, color='green', alpha=0.2, label="Performance")
    plt.axhspan(0, 50, color='blue', alpha=0.2, label="Decreasing")
    
    # Titre avec indication de la période
    period_labels = {'7d': '7 derniers jours', '1m': 'dernier mois', '3m': '3 derniers mois',
                     '6m': '6 derniers mois', '1y': 'dernière année', 'all': 'toute la période'}
    plt.title(f'Rapport entre la fatigue et la performance - {period_labels[period]}')
    
    plt.xlabel("Date")
    plt.ylabel("Rapport fatigue/performance (%)")
    plt.legend()
    plt.tight_layout()
    
    # Convertir le graphique en image base64
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    return base64.b64encode(img.getvalue()).decode('utf-8')

@app.route("/dashboard")
@app.route("/dashboard/<period>")
def dashboard(period='all'):
    """Afficher le tableau de bord d'analyse de performance avec période sélectionnable."""
    activities_data = data_manager.load_from_csv()
    
    if not activities_data:
        return redirect(url_for("index"))
    
    # Valider la période
    valid_periods = ['7d', '1m', '3m', '6m', '1y', 'all']
    if period not in valid_periods:
        period = 'all'
    
    # Préparation des données pour les graphiques
    dates = [act.get("start_date_local", "").split("T")[0] for act in activities_data]
    suffer_scores = [float(act.get("suffer_score", 0)) if act.get("suffer_score", "N/A") != "N/A" else 0 for act in activities_data]
    
    # Données pour les zones cardiaques
    hr_zones_data = {
        "labels": ["Zone 0", "Zone 1", "Zone 2", "Zone 3", "Zone 4", "Zone 5"],
        "datasets": []
    }
    
    for i, activity in enumerate(activities_data[:10]):  # Limiter à 10 activités récentes
        zone_values = [
            int(activity.get(f"zone_{z}", 0)) for z in range(6)
        ]
        date = activity.get("start_date_local", "").split("T")[0]
        hr_zones_data["datasets"].append({
            "label": date,
            "data": zone_values
        })
    
    # Calcul des distances parcourues par type d'activité
    activity_types = {}
    for activity in activities_data:
        activity_type = activity.get("type", "Unknown")
        distance = float(activity.get("distance", 0))
        if activity_type in activity_types:
            activity_types[activity_type] += distance
        else:
            activity_types[activity_type] = distance
    
    # Préparation des données pour la progression de vitesse
    speed_data = []
    for activity in sorted(activities_data, key=lambda x: x.get("start_date_local", "")):
        date = activity.get("start_date_local", "").split("T")[0]
        speed = float(activity.get("average_speed", 0))
        if speed > 0:
            speed_data.append({"date": date, "speed": speed})
    
    # Génération des graphiques avancés avec la période sélectionnée
    acwr_chart = generate_acwr_chart(activities_data, period)
    fitness_fatigue_chart = generate_fitness_fatigue_chart(activities_data, period)
    fatigue_performance_ratio_chart = generate_fatigue_performance_ratio_chart(activities_data, period)
    
    # Labels pour l'affichage
    period_labels = {
        '7d': '7 derniers jours', 
        '1m': 'Dernier mois',
        '3m': '3 derniers mois',
        '6m': '6 derniers mois', 
        '1y': 'Dernière année', 
        'all': 'Toute la période'
    }
    
    return render_template(
        "dashboard.html",
        activities=activities_data,
        dates=dates,
        suffer_scores=suffer_scores,
        hr_zones_data=hr_zones_data,
        activity_types=activity_types,
        speed_data=speed_data,
        acwr_chart=acwr_chart,
        fitness_fatigue_chart=fitness_fatigue_chart,
        fatigue_performance_ratio_chart=fatigue_performance_ratio_chart,
        current_period=period,
        period_labels=period_labels
    )

if __name__ == "__main__":
    # Assurer que le répertoire de données existe
    os.makedirs(os.path.dirname(data_manager.csv_file), exist_ok=True)
    
    # Lancer l'application - permettre l'accès depuis n'importe quelle adresse et sur un port différent
    app.run(debug=True, host='0.0.0.0', port=5001)

import math
import datetime
import random

def convertir_en_horaire(temps):
    if temps < 0:
        return "Temps invalide"
    
    heures = int(temps)
    minutes = int((temps - heures) * 60)
    secondes = round(((temps - heures) * 60 - minutes) * 60)
    
    # Ajuster si les secondes dépassent 60 (cas d'arrondi)
    if secondes == 60:
        secondes = 0
        minutes += 1
    if minutes == 60:
        minutes = 0
        heures += 1
    
    return f"{heures:02d}:{minutes:02d}:{secondes:02d}"

# Fonction pour convertir vitesse en allure
def vitesse_to_allure(vitesse_kmh):
    if vitesse_kmh <= 0:
        return "Vitesse invalide"
    minutes = 60 // vitesse_kmh
    secondes = round((60 / vitesse_kmh - minutes) * 60)
    return f"{int(minutes)}:{int(secondes):02d} min/km"

def calcul_allure(VO2max, experience):
    k = 3.5
    VMA = VO2max / k
    vitesses = []
    intensities = {
        "débutant": [0.60, 0.70, 0.80],
        "intermédiaire": [0.65, 0.70, 0.85, 0.92, 0.97],
        "avancé": [0.75, 0.85, 0.95]
    }
    pourcentage = intensities.get(experience)

    for p in pourcentage:
        v = VMA*p
        vitesses.append(v)

    allures = [vitesse_to_allure(v) for v in vitesses]
    print("Voici vos allures d'entrainement :")
    print(allures)

calcul_allure(60, "intermédiaire")

def calculate_progression_factor(weeks_to_race, total_weeks):
    """
    Calcule le facteur de progression avec un pic de charge suivi d'un tapering.
    """
    if weeks_to_race > 4:  # Période de montée en charge
        progression_factor = (total_weeks - weeks_to_race + 1) / (total_weeks * 0.8)
    else:  # Tapering sur les 4 dernières semaines
        progression_factor = 0.5 + (weeks_to_race / 8)
    
    return progression_factor

def generate_training_week(level, availability, weeks_to_race, current_volume, total_weeks):
    """
    Génère un programme d'entraînement hebdomadaire avec des séances prédéfinies.

    Args:
    - level (str): Niveau de l'athlète ('débutant', 'intermédiaire', 'avancé').
    - availability (int): Nombre de jours disponibles pour s'entraîner dans la semaine.
    - weeks_to_race (int): Nombre de semaines restantes avant la course.
    - current_volume (int): Volume hebdomadaire actuel en minutes.
    - total_weeks (int): Durée totale du plan d'entraînement en semaines.

    Returns:
    - dict: Programme d'entraînement pour une semaine.
    """
    
    # Progression dynamique
    progression_factor = calculate_progression_factor(weeks_to_race, total_weeks)
    target_volume = current_volume + (1 + progression_factor * 0.5)
    
    # Types de séances
    session_types = {
        "endurance": {"min_duration": 30, "max_duration": 60 + int(progression_factor * 30)},
        "fractionné": {"min_duration": 20, "max_duration": 40 + int(progression_factor * 10)},
        "long_run": {"min_duration": 60, "max_duration": 120 + int(progression_factor * 30)},
    }
    
    # Volume par niveau
    level_multiplier = {"débutant": 0.8, "intermédiaire": 1.0, "avancé": 1.2}
    total_minutes = int(target_volume * level_multiplier.get(level, 1.0))
    
    # Calcul de la durée pour chaque type de séance
    long_run_duration = random.randint(
        session_types["long_run"]["min_duration"], session_types["long_run"]["max_duration"]
    )
    fractionné_duration = random.randint(
        session_types["fractionné"]["min_duration"], session_types["fractionné"]["max_duration"]
    )
    endurance_duration = random.randint(
        session_types["endurance"]["min_duration"], session_types["endurance"]["max_duration"]
    )
    week_plan = [f"Endurance ({endurance_duration} min)"] * 7
    # Attribution des séances aux jours fixes
    if availability >= 2:
        week_plan[3] = f"Fractionné ({fractionné_duration} min)"  # Mercredi
        week_plan[6] = f"Long_run ({long_run_duration} min)"  # Vendredi
        
    rest_days = 7 - availability  # Jours restants pour le repos
    # Définir les jours de repos en fonction du nombre de jours disponibles
    rest_indices = {
        1: [4],          # Un jour de repos -> vendredi
        2: [0, 4],       # Deux jours -> lundi et vendredi 
        3: [0, 2, 4]     # Trois jours -> lundi, mercredi et vendredi
    }

    # Appliquer les jours de repos
    if rest_days in rest_indices:
        for index in rest_indices[rest_days]:
            week_plan[index] = "Repos"

    
    return {
        "target_volume": total_minutes,
        "week_plan": week_plan,
    }

def generate_training_plan(level, availability, total_weeks, current_volume):
    """
    Génère un programme d'entraînement complet jusqu'à la course.

    Args:
    - level (str): Niveau de l'athlète ('débutant', 'intermédiaire', 'avancé').
    - availability (int): Nombre de jours disponibles pour s'entraîner dans la semaine.
    - total_weeks (int): Durée totale du plan d'entraînement en semaines.
    - current_volume (int): Volume hebdomadaire initial en minutes.

    Returns:
    - list: Programme complet d'entraînement, semaine par semaine.
    """
    training_plan = []  # Liste pour stocker toutes les semaines
    for week in range(total_weeks):
        weeks_to_race = total_weeks - week  # Semaines restantes avant la course
        
        # Générer la semaine actuelle
        weekly_plan = generate_training_week(
            level=level,
            availability=availability,
            weeks_to_race=weeks_to_race,
            current_volume=current_volume,
            total_weeks=total_weeks
        )
        
        # Ajouter la semaine au programme
        training_plan.append(weekly_plan)
        
        # Mettre à jour le volume pour la semaine suivante
        current_volume = weekly_plan["target_volume"]

    return training_plan


full_plan = generate_training_plan(
    level="intermédiaire",
    availability=5,           # Nombre de jours disponibles par semaine
    total_weeks=16,           # Durée totale du plan en semaines
    current_volume=300        # Volume initial en minutes
)

# Afficher le programme complet
for week_num, week in enumerate(full_plan, 1):
    print(f"\nSemaine {week_num} : Volume cible = {week['target_volume']} min")
    for day, session in enumerate(week['week_plan'], 1):
        print(f"  - Jour {day} : {session}")
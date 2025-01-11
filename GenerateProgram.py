
user_data = {
    "objectif": "10 km",
    "niveau": "intermédiaire",
    "semaine_totale": 12,
    "jours_entrainement": 5,
    "allures": {
        "endurance": 6.5,  # min/km
        "seuil": 5.5,      # min/km
        "vitesse": 4.8     # min/km
    },
    "volume_initial": 50,  # en km/semaine
}

def generate_week(user_data, semaine):

    days_on = user_data["jours_entrainement"]
    semaine_plan = []
    volume = user_data["volume_initial"] * (1 + 0.1 * (semaine - 1))
    if semaine % 4 == 0:
        volume = volume - volume*0.3

    # Répartition des séances
    endurance_volume = volume * 0.25
    seuil_volume = volume * 0.25
    long_run = volume * 0.5

    # Exemple de plan hebdomadaire
    semaine_plan.append({"jour": "Lundi", "type": "Endurance", "distance": endurance_volume / 3})
    semaine_plan.append({"jour": "Mardi", "type": "Endurance", "distance": endurance_volume / 3})
    semaine_plan.append({"jour": "Jeudi", "type": "Seuil", "distance": seuil_volume, "allure": user_data["allures"]["seuil"]})
    semaine_plan.append({"jour": "Samedi", "type": "Longue sortie", "distance": long_run, "allure": user_data["allures"]["endurance"]})
    semaine_plan.append({"jour": "Dimanche", "type": "Récupération active", "distance": endurance_volume / 3})

    return semaine_plan
    
def generate_program(user_data):
    programme = {}
    for semaine in range(1, user_data["semaine_totale"] + 1):
        programme[f"Semaine {semaine}"] = generate_week(user_data, semaine)
    return programme

# Exemple de génération
programme = generate_program(user_data)
for semaine, details in programme.items():
    print(f"\n{semaine}:")
    for jour in details:
        print(jour)



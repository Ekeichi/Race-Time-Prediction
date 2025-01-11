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


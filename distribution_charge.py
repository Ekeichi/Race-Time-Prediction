from calculAllure import calcul_allure

user_data = {
    "FCmax" : 194,
    "VO2max" : 60,
    "experience" : "Intermédiaire"
}

import matplotlib.pyplot as plt

# Paramètres pour le profil de charge
semaines_totales = 12
volume_initial = 30  # Volume de départ en km
intensite_moyenne = 6  # Intensité sur une échelle RPE (1-10)
progression = 0.12  # Augmentation de 10 % par semaine
recuperation = 0.2  # Réduction de 50 % pour les semaines de récupération
tapering_start = 10  # Affûtage à partir de la semaine 10

# Calcul de la charge hebdomadaire
charges = []
volume_actuel = volume_initial

for semaine in range(1, semaines_totales + 1):
    if semaine >= tapering_start:
        # Affûtage : réduction graduelle du volume (20 % par semaine)
        volume_actuel *= 0.8
    elif semaine / 4 == 1:
        # Semaine de récupération : réduction de 50 % du volume
       volume_actuel *= 0.85  # Réduction de 30 % au lieu de 50 %
    elif semaine / 8 == 1:
        # Semaine de récupération : réduction de 50 % du volume
       volume_actuel *= 0.9  # Réduction de 30 % au lieu de 50 %
    else:
        # Progression normale
        volume_actuel *= (1 + progression)

    # Calcul de la charge (volume * intensité moyenne)
    charge = volume_actuel * intensite_moyenne
    charges.append(charge)

# Visualisation graphique
plt.figure(figsize=(12, 6))
plt.plot(range(1, semaines_totales + 1), charges, marker='o', label="Charge d'entraînement")
plt.axvline(x=4, color='orange', linestyle='--', label="Récupération (Semaine 4)")
plt.axvline(x=8, color='orange', linestyle='--', label="Récupération (Semaine 8)")
plt.axvline(x=10, color='green', linestyle='--', label="Début de l'affûtage")
plt.axvline(x=12, color='red', linestyle='--', label="Course (Semaine 12)")

# Détails du graphique
plt.title("Évolution de la charge d'entraînement sur 12 semaines avec une course prévue", fontsize=14)
plt.xlabel("Semaines", fontsize=12)
plt.ylabel("Charge d'entraînement (unités)", fontsize=12)
plt.xticks(range(1, semaines_totales + 1))
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()
plt.show()
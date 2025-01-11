import matplotlib.pyplot as plt

# Paramètres pour le profil de charge
semaines_totales = 12
volume_initial = 20  # Volume de départ en km
intensite_moyenne = 6  # Intensité sur une échelle RPE (1-10)
progression = 0.12  # Augmentation de 12 % par semaine
tapering_start = 10  # Affûtage à partir de la semaine 10

# Calcul de la charge hebdomadaire
charges = []
volume_actuel = volume_initial

for semaine in range(1, semaines_totales + 1):
    if semaine >= tapering_start:
        # Affûtage : réduction graduelle du volume (15 % par semaine)
        volume_actuel *= 0.85
    elif semaine / 4 == 1:
        # Semaine de récupération 1 : réduction de 25 % du volume
       volume_actuel *= 0.85  
    elif semaine / 8 == 1:
        # Semaine de récupération 2 : réduction de 10 % du volume
       volume_actuel *= 0.9
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
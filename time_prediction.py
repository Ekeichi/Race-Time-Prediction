import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import matplotlib.pyplot as plt

AB_file = ("average_stats_per_run_activity_test.csv")

data_AB = pd.read_csv(AB_file)
data_AB = data_AB.drop(columns=["activity_name"])
data_AB = data_AB.fillna(150)

# Diviser les données en train/test
X = data_AB[["total_distance_km", "total_elevation_gain", "average_heart_rate"]]
y = data_AB["total_time_seconds"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Entraîner le modèle
model = LinearRegression()
model.fit(X_train, y_train)

# Coefficients ajustés
beta_0 = model.intercept_
beta_1, beta_2, beta_3 = model.coef_

print(f"Beta_0 (interception) : {beta_0}")
print(f"Beta_1 (distance) : {beta_1}")
print(f"Beta_2 (dénivelé) : {beta_2}")
print(f"Beta_3 (rythme cardiaque) : {beta_3}")

# Relation entre le temps et distance/d+/FC
for col in X.columns:
    plt.scatter(X[col], y)
    plt.title(f"{col} vs Temps total")
    plt.xlabel(col)
    plt.ylabel("Total Time (s)")
    plt.show()

def temps_estime(distance_km, denivele_m, rythme_cardiaque_bpm, beta_0, beta_1, beta_2, beta_3):
    """
    Calcule le temps estimé d'une course en secondes à partir des caractéristiques d'entrée et des coefficients.
    
    Parameters:
        distance_km (float): Distance de la course en kilomètres.
        denivele_m (float): Dénivelé total en mètres.
        rythme_cardiaque_bpm (float): Rythme cardiaque moyen en bpm.
        beta_0 (float): Coefficient d'interception.
        beta_1 (float): Coefficient pour la distance.
        beta_2 (float): Coefficient pour le dénivelé.
        beta_3 (float): Coefficient pour le rythme cardiaque.

    Returns:
        float: Temps estimé en secondes.
    """
    return beta_0 + beta_1 * distance_km + beta_2 * denivele_m + beta_3 * rythme_cardiaque_bpm

# Nouvelle entrée
nouvelle_distance = 17  # km
nouveau_denivele = 725  # m
nouveau_rythme_cardiaque = 152 # bpm

# Calcul du temps estimé
temps = temps_estime(nouvelle_distance, nouveau_denivele, nouveau_rythme_cardiaque, beta_0, beta_1, beta_2, beta_3)
print(f"Temps estimé : {temps / 3600:.2f} heure(s)")  # Conversion en heure


import seaborn as sns

corr = data_AB.corr()
sns.heatmap(corr, annot=True, cmap='coolwarm')
plt.title("Matrice de corrélation")
plt.show()

sns.histplot(data_AB["total_time_seconds"], bins=30, kde=True)
plt.title("Distribution des temps de course")
plt.xlabel("Temps (secondes)")
plt.show()
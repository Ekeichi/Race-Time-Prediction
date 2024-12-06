import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

AB_file = ("average_stats_per_run_activity_test.csv")

data_AB = pd.read_csv(AB_file)
data_AB = data_AB.drop(columns=["activity_name"])

# Diviser les données en train/test
X = data_AB[["total_distance_km", "total_elevation_gain", "average_heart_rate"]]
y = data_AB["total_time_seconds"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Entraîner le modèle
model = LinearRegression()
model.fit(X_train, y_train)

# Évaluer le modèle
y_pred = model.predict(X_test)
# Coefficients ajustés
beta_0 = model.intercept_
beta_1, beta_2, beta_3 = model.coef_

print(f"Beta_0 (interception) : {beta_0}")
print(f"Beta_1 (distance) : {beta_1}")
print(f"Beta_2 (dénivelé) : {beta_2}")
print(f"Beta_3 (rythme cardiaque) : {beta_3}")

# # Entrées utilisateur
# distance_input = float(input("Entrez la distance (en km) : "))
# denivele_input = float(input("Entrez le dénivelé positif cumulé (en m) : "))
# historique_input = float(input("Entrez votre temps moyen au km (en minutes) : "))

# # Prédiction
# temps_prevu = model.predict([[distance_input, denivele_input, historique_input]])
# print(f"Temps estimé pour la course : {temps_prevu[0]:.2f} minutes")
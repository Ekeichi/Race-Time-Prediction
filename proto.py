import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

AB_file = ("average_stats_per_run_activity.csv")

data_AB = pd.read_csv(AB_file)
data_AB = data_AB.drop(columns=["activity_name"])

# Diviser les données en train/test
X = data_AB[["total_distance_km", "total_denivele_gain", "average_heart_rate"]]
y = data_AB["total_time_seconds"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Entraîner le modèle
model = LinearRegression()
model.fit(X_train, y_train)

# Évaluer le modèle
y_pred = model.predict(X_test)
print("Erreur absolue moyenne :", mean_absolute_error(y_test, y_pred))

# Afficher les coefficients
print("Coefficients du modèle :", model.coef_)

# Entrées utilisateur
distance_input = float(input("Entrez la distance (en km) : "))
denivele_input = float(input("Entrez le dénivelé positif cumulé (en m) : "))
historique_input = float(input("Entrez votre temps moyen au km (en minutes) : "))

# Prédiction
temps_prevu = model.predict([[distance_input, denivele_input, historique_input]])
print(f"Temps estimé pour la course : {temps_prevu[0]:.2f} minutes")
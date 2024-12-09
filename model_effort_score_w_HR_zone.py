import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import numpy as np
import xgboost as xgb
from sklearn.metrics import mean_squared_error

data = pd.read_csv('activities_with_details.csv')
data = data.drop(columns=['activity_id'])
data = data.dropna()
df = pd.DataFrame(data)

# X = df.drop('suffer_score', axis=1)
# y = df['suffer_score']

# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
zone_weights = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 6}
# Calculer le score d'effort initial basé sur les pondérations
def calculate_initial_effort(row, zone_weights):
    return sum(row[f'zone_{zone}'] * weight for zone, weight in zone_weights.items())

df['initial_effort'] = df.apply(calculate_initial_effort, axis=1, zone_weights=zone_weights)

# Erreur initiale entre le score réel et initial
df['initial_error'] = df['suffer_score'] - df['initial_effort']

# Modèle supervisé pour ajuster les poids
X = df[[f'zone_{zone}' for zone in range(6)]]
y = df['initial_error']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = LinearRegression()
model.fit(X_train, y_train)

# Ajustements appris par le modèle
adjustments = model.coef_
print("Ajustements appris pour chaque zone :", adjustments)

# Pondérations finales
adjusted_weights = {zone: zone_weights[zone] + adjustments[zone] for zone in range(6)}
print("Pondérations finales :", adjusted_weights)
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import numpy as np
import xgboost as xgb
from sklearn.metrics import mean_squared_error
import seaborn as sns
import matplotlib.pyplot as plt
import datetime as dt

data = pd.read_csv('activities_with_details.csv')
date = data['start_date_local']
data = data.drop(columns=['activity_id', 'start_date_local', 'suffer_score'])
data = data.dropna()
df = pd.DataFrame(data)

# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
zone_weights = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5}
# Calculer le score d'effort initial basé sur les pondérations
def calculate_initial_effort(row, zone_weights):
    return sum((row[f'zone_{zone}']/60) * np.exp(weight) for zone, weight in zone_weights.items())

df['initial_effort'] = df.apply(calculate_initial_effort, axis=1, zone_weights=zone_weights)

df = df.drop(columns=['zone_0', 'zone_1','zone_2','zone_3','zone_4','zone_5'])

df['date'] = date
df['date'] = pd.to_datetime(df['date'])

# Group by date and sum the initial_effort
daily_effort = df.groupby(df['date'].dt.date)['initial_effort'].sum().reset_index()

# Générer toutes les dates
date_range = pd.date_range(start=df['date'].min().date(), end=df['date'].max().date())

# Créer un DataFrame avec toutes les dates
df_full = pd.DataFrame({'date': date_range})

# Convertir les dates en format date
df_full['date'] = df_full['date'].dt.date

# Fusionner avec les efforts quotidiens
df_full = df_full.merge(daily_effort, on='date', how='left')

# Remplir les efforts manquants par 0
df_full['initial_effort'] = df_full['initial_effort'].fillna(0)

# # Trier dans l'ordre décroissant
# df_full = df_full.sort_values('date', ascending=False).reset_index(drop=True)


# Calcul de la charge aigue
charge_aigue = []

for i in range(len(df_full)):
    last_7_days = df_full.iloc[max(0, i-6):i+1]
    
    ca = (last_7_days["initial_effort"].sum()/7)
    
    charge_aigue.append(ca)

df_full["Charge_aigue"] = charge_aigue

# Calcul de la charge chronique
charge_chronique = []

for i in range(len(df_full)):
    last_28_days = df_full.iloc[max(0, i-27):i+1]
    
    cc = (last_28_days["initial_effort"].sum()/28)
    
    charge_chronique.append(cc)

df_full["Charge_chronique"] = charge_chronique

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Créer un tableau de visualisation
plt.figure(figsize=(15, 6))
plt.plot(df_full['date'], df_full['Charge_aigue'], label='Charge Aiguë (7 jours)', color='blue')
plt.plot(df_full['date'], df_full['Charge_chronique'], label='Charge Chronique (28 jours)', color='red')
plt.title('Évolution des Charges Aiguë et Chronique')
plt.xlabel('Date')
plt.ylabel('Charge d\'effort')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Tableau récapitulatif statistique
stats = df_full[['Charge_aigue', 'Charge_chronique']].describe()
print("\nRésumé statistique des charges :")
print(stats)

# Calcul du ratio Charge Aiguë / Charge Chronique
df_full['Ratio_AC'] = df_full['Charge_aigue'] / df_full['Charge_chronique']

print("\nRésumé du ratio Charge Aiguë / Charge Chronique :")
print(df_full['Ratio_AC'].describe())

# Visualisation du ratio
plt.figure(figsize=(15, 6))
plt.plot(df_full['date'], df_full['Ratio_AC'], label='Ratio Charge Aiguë / Chronique', color='green')
plt.title('Évolution du Ratio Charge Aiguë / Charge Chronique')
plt.xlabel('Date')
plt.ylabel('Ratio')
plt.axhline(y=1, color='r', linestyle='--')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
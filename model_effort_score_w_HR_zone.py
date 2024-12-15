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
zone_weights = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5}
# Calculer le score d'effort initial basé sur les pondérations
def calculate_relative_effort(row, zone_weights):
    return sum((row[f'zone_{zone}']/60) * np.exp(weight) for zone, weight in zone_weights.items())

df['relative_effort'] = df.apply(calculate_relative_effort, axis=1, zone_weights=zone_weights)

df = df.drop(columns=['zone_0', 'zone_1','zone_2','zone_3','zone_4','zone_5'])

df['date'] = date
df['date'] = pd.to_datetime(df['date'])

# Group by date and sum the initial_effort
daily_effort = df.groupby(df['date'].dt.date)['relative_effort'].sum().reset_index()

# Générer toutes les dates
date_range = pd.date_range(start=df['date'].min().date(), end=df['date'].max().date())

# Créer un DataFrame avec toutes les dates
df_full = pd.DataFrame({'date': date_range})

# Convertir les dates en format date
df_full['date'] = df_full['date'].dt.date

# Fusionner avec les efforts quotidiens
df_full = df_full.merge(daily_effort, on='date', how='left')

# Remplir les efforts manquants par 0
df_full['relative_effort'] = df_full['relative_effort'].fillna(0)

# # Trier dans l'ordre décroissant
# df_full = df_full.sort_values('date', ascending=False).reset_index(drop=True)


# Calcul de la charge aigue
charge_aigue = []

for i in range(len(df_full)):
    last_7_days = df_full.iloc[max(0, i-6):i+1]
    
    ca = (last_7_days["relative_effort"].sum()/7)
    
    charge_aigue.append(ca)

df_full["Charge_aigue"] = charge_aigue

# Calcul de la charge chronique
charge_chronique = []

for i in range(len(df_full)):
    last_28_days = df_full.iloc[max(0, i-27):i+1]
    
    cc = (last_28_days["relative_effort"].sum()/28)
    
    charge_chronique.append(cc)

df_full["Charge_chronique"] = charge_chronique


# # Créer un tableau de visualisation
# plt.figure(figsize=(15, 6))
# plt.plot(df_full['date'], df_full['Charge_aigue'], label='Charge Aiguë (7 jours)', color='blue')
# plt.plot(df_full['date'], df_full['Charge_chronique'], label='Charge Chronique (28 jours)', color='red')
# plt.title('Évolution des Charges Aiguë et Chronique')
# plt.xlabel('Date')
# plt.ylabel('Charge d\'effort')
# plt.legend()
# plt.xticks(rotation=45)
# plt.tight_layout()
# plt.show()

# Calcul du ratio Charge Aiguë / Charge Chronique (ACWR)
df_full['Ratio_AC'] = df_full['Charge_aigue'] / df_full['Charge_chronique']

# Visualisation du ratio
# plt.figure(figsize=(15, 6))
# plt.plot(df_full['date'], df_full['Ratio_AC'], label='ACWR', color='green')
# plt.title('Évolution du Ratio Charge Aiguë / Charge Chronique = ACWR')
# plt.xlabel('Date')
# plt.ylabel('Ratio')
# plt.axhline(y=1.5, color='r', linestyle='--', label='Limite ACWR (1.5)')
# plt.axhline(y=0.8, color='b', linestyle='--', label='Limite ACWR (0.8)')
# plt.legend()
# plt.xticks(rotation=45)
# plt.tight_layout()
# plt.show()


def etrimp(HR_ex, HR_repos, HR_MAX, temps, sexe):
    alpha = 0
    beta = 0
    if sexe == 'H':
        alpha = 0.64
        beta = 1.92
    elif sexe == 'F':
        alpha = 0.64
        beta = 1.92
    else:
        alpha = 0.64
        beta = 1.92
        print("Mauvais sexe, Homme par défaut.")
    
    delta = (HR_ex-HR_repos)/(HR_MAX-HR_repos)
    return temps*delta*alpha*np.exp(beta*delta)

def performance(performance_pre, effort):
    K = 2.0
    tau = 50
    tau_prime = 5
    tau_tier = 15
    perfo_post = performance_pre + (np.exp(-1/tau) - np.exp(-1/tau_prime) - K*np.exp(-1/tau_tier)) * effort
    return perfo_post

def fatigue(fatigue_pre, effort):
    tau = 15
    fatigue_post = (effort + np.exp(-1/tau)*fatigue_pre) 
    return fatigue_post

def fitness(fitness_pre, effort):
    tau = 50
    tau_prime = 50
    fitness_post = effort + (np.exp(-1/tau)) * fitness_pre
    return fitness_post

courbe_fatigue = [0]
courbe_fitness = [0]
courbe_performance = [0]
window_size = 200

for i in range(len(df_full) - 1):
    effort = df_full.iloc[i + 1]["relative_effort"]
    instant_fatigue = fatigue(courbe_fatigue[-1], effort)
    instant_fitness = fitness(courbe_fitness[-1], effort)
    instant_fitness = np.convolve()
    instant_performance = performance(courbe_performance[-1], effort)
    courbe_fatigue.append(instant_fatigue)
    courbe_fitness.append(instant_fitness)
    courbe_performance.append(instant_performance)
    if len(courbe_fatigue) > window_size:
        courbe_fatigue.pop(0)
        courbe_fitness.pop(0)
        courbe_performance.pop(0)


# temps = np.arange(len(courbe_fatigue))  # Index pour la fenêtre glissante

# plt.figure(figsize=(12, 6))

# #Tracer la courbe de fatigue
# plt.plot(temps, courbe_fatigue, label="Fatigue", color="red", linewidth=2)

# #Tracer la courbe de fitness
# plt.plot(temps, courbe_fitness, label="Fitness", color="green", linewidth=2)

# # Ajouter des options graphiques
# plt.xlabel("Temps (fenêtre glissante)")
# plt.ylabel("Valeurs")
# plt.title("Évolution de la Fatigue et de la Fitness")
# plt.legend()
# plt.grid()
# plt.show()
# courbe = [0]
# temps = []
# effort = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0 , 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 , 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# for i in range(len(effort)):
#     instant_fitness = fitness(courbe[-1], effort[i])
#     courbe.append(instant_fitness)
#     temps.append(i)


# plt.plot(courbe)
# plt.show()
# Initialisation des courbes
# courbe_fatigue = [0]
# courbe_fitness = [0]
# temps = []
# effort = [1] + [0] * 99  # Impulsion initiale

# # Calcul des réponses
# for i in range(len(effort)):
#     fatigue_val = fatigue(courbe_fatigue[-1], effort[i])
#     fitness_val = fitness(courbe_fitness[-1], effort[i])
#     courbe_fatigue.append(fatigue_val)
#     courbe_fitness.append(fitness_val)
#     temps.append(i)

# # Tracé des courbes
# plt.plot(temps, courbe_fatigue[1:], label="Fatigue", color="red")
# plt.plot(temps, courbe_fitness[1:], label="Fitness", color="blue")
# plt.xlabel("Temps")
# plt.ylabel("Valeur")
# plt.title("Comparaison des réponses impulsionnelles : Fatigue vs Fitness")
# plt.legend()
# plt.grid()
# plt.show()
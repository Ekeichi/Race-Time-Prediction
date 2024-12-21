import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import numpy as np
import xgboost as xgb
from sklearn.metrics import mean_squared_error
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime as dt



data = pd.read_csv('activities_with_details.csv')
date = data['start_date_local']
data = data.drop(columns=['activity_id', 'start_date_local', 'suffer_score'])
data = data.dropna()
df = pd.DataFrame(data)


zone_weights = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5}

#######################################
####### Traitement des données ########
#######################################

# Calculer le score d'effort initial basé sur les pondérations
def calculate_relative_effort(row, zone_weights):
    return sum((row[f'zone_{zone}']/60) * np.exp(weight) for zone, weight in zone_weights.items())

df['relative_effort'] = df.apply(calculate_relative_effort, axis=1, zone_weights=zone_weights)

df = df.drop(columns=['zone_0', 'zone_1','zone_2','zone_3','zone_4','zone_5'])

df['date'] = date
df['date'] = pd.to_datetime(df['date'])

# Group by date and sum the initial_effort
daily_effort = df.groupby(df['date'].dt.date)['relative_effort'].sum().reset_index()

date_du_jour = dt.now().date()

# Générer toutes les dates
date_range = pd.date_range(start=df['date'].min().date(), end=date_du_jour)

# Créer un DataFrame avec toutes les dates
df_full = pd.DataFrame({'date': date_range})

# Convertir les dates en format date
df_full['date'] = df_full['date'].dt.date

# Fusionner avec les efforts quotidiens
df_full = df_full.merge(daily_effort, on='date', how='left')

# Remplir les efforts manquants par 0
df_full['relative_effort'] = df_full['relative_effort'].fillna(0)

######################################################
####### Calcul des charges aigue et chronique ########
######################################################

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

# Calcul du ratio Charge Aiguë / Charge Chronique (ACWR)
df_full['Ratio_AC'] = df_full['Charge_aigue'] / df_full['Charge_chronique']


#######################################
####### Calcul des courbes ############
#######################################

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

def fatigue(fatigue_pre, effort):
    tau = 15
    fatigue_post = (effort + np.exp(-1/tau)*fatigue_pre) 
    return fatigue_post

def fitness(fitness_pre, effort):
    tau = 45
    tau_prime = 5
    fitness_post = effort + (np.exp(-1/tau)) * fitness_pre
    return fitness_post

window_size = 100
courbe_fatigue = [0]
courbe_fitness = [0]
courbe_performance = [0]
courbe_forme = [0]
courbe_rapport = [0]


for i in range(len(df_full) - 1):
    effort = df_full.iloc[i + 1]["relative_effort"]
    instant_fatigue = fatigue(courbe_fatigue[-1], effort)
    instant_fitness = fitness(courbe_fitness[-1], effort)
    instant_performance = (instant_fitness - instant_fatigue)/2
    instant_forme = instant_fitness - 2*instant_fatigue
    if instant_performance >= 0:
        rapport = (instant_fatigue/instant_performance)*100
    else:
        rapport = 150

    courbe_fatigue.append(instant_fatigue)
    courbe_fitness.append(instant_fitness)
    courbe_performance.append(instant_performance)
    courbe_forme.append(instant_forme)
    courbe_rapport.append(rapport)
    if len(courbe_fatigue) > window_size:
        courbe_fatigue.pop(0)
        courbe_fitness.pop(0)
        courbe_performance.pop(0)
        courbe_forme.pop(0)
        courbe_rapport.pop(0)


temps = np.arange(len(courbe_fatigue))  # Index pour la fenêtre glissante



def graphique():
    # Créer les sous-graphiques
    fig, axs = plt.subplots(2, 1, figsize=(10, 5))  # 2 lignes, 1 colonne

    # ---- Premier graphique : ACWR ----
    axs[0].plot(df_full['date'], df_full['Ratio_AC'], label='ACWR', color='green')
    axs[0].axhline(y=1.5, color='r', linestyle='--', label='Limite ACWR (1.5)')
    axs[0].axhline(y=0.8, color='b', linestyle='--', label='Limite ACWR (0.8)')
    axs[0].set_title('Évolution du Ratio Charge Aiguë / Charge Chronique = ACWR')
    axs[0].set_xlabel('Date')
    axs[0].set_ylabel('Ratio')
    axs[0].legend()
    axs[0].grid()
    axs[0].tick_params(axis='x', rotation=45)

    # ---- Deuxième graphique : Fatigue, Fitness, Performance ----
    axs[1].plot(temps, courbe_fatigue, label="Fatigue", color="red", linewidth=2)
    axs[1].plot(temps, courbe_forme, label="Forme", color="green", linewidth=2)
    axs[1].plot(temps, courbe_performance, label="Performance", color="blue", linewidth=2)
    axs[1].set_title("Évolution de la Fatigue, de la Forme et de la Performance")
    axs[1].set_xlabel("Temps (fenêtre glissante)")
    axs[1].set_ylabel("Valeurs")
    axs[1].legend()
    axs[1].grid()

    # Ajuster l'espacement entre les sous-graphiques
    plt.tight_layout()

    # Afficher les deux graphiques
    plt.show()


graphique()

derniere_valeur = courbe_rapport[-1]  # Récupération de la dernière valeur

if derniere_valeur < 50:
    print("Decreasing")
if derniere_valeur < 80:
    print("Resuming/Performance")
if derniere_valeur < 100:
    print("Maintaining")
if derniere_valeur < 150:
    print("Optimized")
if derniere_valeur >= 150:
    print("Excessive")


# Création de la courbe
plt.plot(temps, courbe_rapport)
plt.axhspan(150, 200, color='red', alpha=0.2, label="Excessive")
plt.axhspan(100, 150, color='orange', alpha=0.2, label="Optimized")
plt.axhspan(80, 100, color='yellow', alpha=0.2, label="Maintaining")
plt.axhspan(50, 80, color='green', alpha=0.2, label="Performance")
plt.axhspan(0, 50, color='blue', alpha=0.2, label="Decreasing")

# Ajout de titres et légendes
plt.title("Rapport entre la fatigue et la performance sur 100 jours")
plt.xlabel("Jours")
plt.ylabel("Rapport fatigue performance (en %)")
plt.legend()

# Affichage
plt.show()


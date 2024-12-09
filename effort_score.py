import pandas as pd
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from sklearn.model_selection import cross_val_score

# Importation des données
data_link = "Data/strava_run_activities_comprehensive.csv"
data = pd.read_csv(data_link)

# Nettoyage des données
data_step = data.dropna(axis=1, how='all')
data_step = data.drop(columns=["activity_name", "type", "average_stride_length", "total_steps"])
data_step = data_step.dropna(subset=["suffer_score", "average_heart_rate", "max_heart_rate"])

mean_values = {
    'max_watts': data_step['max_watts'].mean(),
    'average_watts': data_step['average_watts'].mean(),
    'average_cadence': data_step['average_cadence'].mean()
}
data_step.fillna(value=mean_values, inplace=True)

# Création de la colonne indiquant le temps de récupération entre deux séances
def time_bt_date(date_str1, date_str2, date_format):
    date1 = datetime.strptime(date_str1, date_format)
    date2 = datetime.strptime(date_str2, date_format)   
    time_diff = date2-date1
    return time_diff.total_seconds() / 3600

recup_time = [0]

for i in range(1, data_step.shape[0]):
    date_str1 = data_step.iloc[i-1, 0]
    date_str2 = data_step.iloc[i, 0]

    time = time_bt_date(date_str2, date_str1, "%Y-%m-%dT%H:%M:%SZ")
    recup_time.append(time)

data_step['recup_time'] = recup_time
data_step['recup_time'] = data_step['recup_time'].shift(-1)
data_step['recup_time'] = data_step['recup_time'].fillna(0)
data_step = data_step.drop(columns=['date'])

# Ajout de nouvelles colonnes pour capturer des relations complexes entre les données
timekm= data_step['total_distance_km'] * data_step['moving_time_seconds']
data_step['distance*time'] = timekm
data_cleaned = data_step.copy()

# Affichage de la matrice de corrélation entre toutes les données
corr = data_cleaned.corr()
sns.heatmap(corr, annot=True, cmap='coolwarm')
plt.title("Matrice de corrélation")
plt.show()

target_corr = corr['suffer_score']
threshold = 0.2
high_corr_features = target_corr[abs(target_corr) > threshold].index
X_high_corr = data_cleaned[high_corr_features]
X_high_corr = X_high_corr.drop(columns=['suffer_score'])
print(f"Variables sélectionnées : {list(high_corr_features)}")


# Création du dataset d'entrainement et de test
X = data_cleaned.drop(['suffer_score'], axis=1)
y = data_cleaned["suffer_score"]
X_train, X_test, y_train, y_test = train_test_split(X_high_corr, y, test_size=0.2, random_state=42)


# Entrainement du modèle sur le dataset d'entrainement
model = LinearRegression()
model.fit(X_train, y_train)

# Evaluation du modèle
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Erreur quadratique moyenne (MSE): {mse}")
print(f"Coefficient de détermination (R²): {r2}")

# Evaluation du modèle sur les données d'entrainement
y_pred_train = model.predict(X_train)
mse_t = mean_squared_error(y_train, y_pred_train)
r2_t = r2_score(y_train, y_pred_train)

print(f"Erreur quadratique moyenne sur le train (MSE): {mse_t}")
print(f"Coefficient de détermination sur le train (R²): {r2_t}")

residuals = y_test - y_pred
plt.scatter(y_pred, residuals)
plt.axhline(0, color='r', linestyle='--')
plt.xlabel("Valeurs prédites")
plt.ylabel("Résidus")
plt.title("Résidus vs Prédictions")
plt.show()

cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='r2')
print(f"Scores de validation croisée : {cv_scores}")
print(f"Moyenne des scores (R²) : {cv_scores.mean()}")

sns.histplot(residuals, kde=True)
plt.title("Distribution des résidus")
plt.show()

# Enregistrer le modèle
joblib.dump(model, "save/suffer_score_model.pkl")
print("Modèle sauvegardé avec succès.")
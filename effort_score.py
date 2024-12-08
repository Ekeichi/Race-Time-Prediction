import pandas as pd
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns


# Importation des données
data_link = "strava_run_activities_comprehensive.csv"
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

data_cleaned = data_step.copy()

# Création du dataset d'entrainement et de test
X = data_cleaned.drop(['suffer_score'], axis=1)
y = data_cleaned["suffer_score"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Affichage de la matrice de corrélation entre toutes les données
corr = data_cleaned.corr()
sns.heatmap(corr, annot=True, cmap='coolwarm')
plt.title("Matrice de corrélation")
plt.show()

# Entrainement du modèle sur le dataset d'entrainement
model = LinearRegression()
model.fit(X_train, y_train)

# Evaluation du modèle
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Erreur quadratique moyenne (MSE): {mse}")
print(f"Coefficient de détermination (R²): {r2}")


plt.scatter(y_test, y_pred)
plt.xlabel("Valeurs réelles (suffer_score)")
plt.ylabel("Valeurs prédites (suffer_score)")
plt.title("Prédictions vs Réalité")
plt.show()

residuals = y_test - y_pred
sns.histplot(residuals, kde=True)
plt.title("Distribution des résidus")
plt.show()
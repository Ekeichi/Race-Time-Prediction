import pandas as pd
from datetime import datetime

# Importation des données
data_link = "strava_run_activities_comprehensive.csv"
data = pd.read_csv(data_link)

# Nettoyage des données
data_step = data.dropna(axis=1, how='all')
data_step = data.drop(columns=["activity_name", "type"])
data_step = data_step.dropna(subset=["suffer_score", "average_heart_rate", "max_heart_rate"])

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

data_cleaned = data_step.copy()


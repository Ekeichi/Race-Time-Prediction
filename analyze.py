import pandas as pd

# Charger le fichier de la course
data_course = pd.read_csv("course_data.csv")

# Afficher les premières lignes pour vérifier
print(data_course.head())
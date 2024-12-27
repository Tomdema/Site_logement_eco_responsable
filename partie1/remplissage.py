import sqlite3
import random
from datetime import datetime, timedelta

# Chemin vers la base de données SQLite
database_path = "/Users/tom-demagnokpowou-tazzou/Desktop/TP_IoT /TP_IoT_partie_4_7/database.db"
# ouverture/initialisation de la base de donnee 
conn = sqlite3.connect(database_path)
conn.row_factory = sqlite3.Row
c = conn.cursor()

# Fonction pour générer une date aléatoire dans les trois derniers jours ouvrés du mois
def random_workday_last_days():
    today = datetime.now()
    year = today.year
    month = today.month

    # Passer au mois précédent si on est au début du mois
    if today.day <= 3:
        month -= 1
        if month == 0:
            month = 12
            year -= 1

    # Trouver le dernier jour du mois
    if month == 12:
        next_month = datetime(year + 1, 1, 1)
    else:
        next_month = datetime(year, month + 1, 1)

    last_day_of_month = next_month - timedelta(days=1)
    last_workdays = []

    # Obtenir les trois derniers jours ouvrés
    for i in range(3):
        day = last_day_of_month - timedelta(days=i)
        if day.weekday() < 5:  # 0-4 sont les jours de semaine (lundi-vendredi)
            last_workdays.append(day)

    return random.choice(last_workdays)

# Remplissage de la table 'mesure'
def insert_mesures():
    # ID des capteurs disponibles (à adapter en fonction de votre table capteur_actionneur)
    capteur_ids = [1, 2]  # Assurez-vous que ces IDs existent dans la table capteur_actionneur
    for _ in range(10):  # Insertion de 10 mesures aléatoires
        capteur_id = random.choice(capteur_ids)
        valeur = round(random.uniform(10.0, 40.0), 2)  # Valeurs aléatoires entre 10.0 et 40.0
        date_insertion = random_workday_last_days()
        c.execute(
            "INSERT INTO mesure (capteur_id, valeur, date_insertion) VALUES (?, ?, ?)",
            (capteur_id, valeur, date_insertion)
        )
    print("Mesures ajoutées avec succès.")

# Remplissage de la table 'facture'
def insert_factures():
    # ID des logements disponibles (à adapter en fonction de votre table logement)
    logement_ids = [1]  # Assurez-vous que ces IDs existent dans la table logement
    types_factures = ['Electricité', 'Consommation_eau']
    for _ in range(5):  # Insertion de 5 factures aléatoires
        logement_id = random.choice(logement_ids)
        type_facture = random.choice(types_factures)
        montant = round(random.uniform(20.0, 200.0), 2)  # Montant aléatoire entre 20.0 et 200.0
        valeur_consommation = round(random.uniform(50.0, 300.0), 2)  # Consommation aléatoire
        date_facture = random_workday_last_days()
        c.execute(
            "INSERT INTO facture (logement_id, type, montant, valeur_consommation, date_facture) VALUES (?, ?, ?, ?, ?)",
            (logement_id, type_facture, montant, valeur_consommation, date_facture)
        )
    print("Factures ajoutées avec succès.")

# Exécution des fonctions pour remplir la base de données
try:
    insert_mesures()
    insert_factures()
    
    # Sauvegarde des changements
    conn.commit()
except sqlite3.Error as e:
    print(f"Erreur lors de l'insertion des données: {e}")
    conn.rollback()
finally:
    # Fermeture de la connexion à la base de données
    conn.close()

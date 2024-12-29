from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import requests
import os
from datetime import datetime
from flask_caching import Cache

app = Flask(__name__)
app.secret_key = "secret_key"

# ✅ Configuration
API_KEY = os.getenv("OPENWEATHER_API_KEY", "350aea51d0cfada04d8f7b339ce23a74")
CITY = "Bures-sur-Yvette"
DATABASE_PATH = "/Users/tom-demagnokpowou-tazzou/Desktop/TP_IoT /TP_IoT_partie_4_7/partie3/database.db"


# ✅ Connexion à la base de données
def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

app.config['CACHE_TYPE'] = 'simple'  # Cache en mémoire
cache = Cache(app)

@cache.cached(timeout=300)
def get_weather():
    try:
        response = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erreur API météo : {e}")
        return None




# ✅ Page d'accueil
@app.route('/')
def index():
    weather_data = get_weather()
    conn = get_db_connection()
    logement = conn.execute("SELECT * FROM logement LIMIT 1").fetchone()

    current_month = datetime.now().strftime("%Y-%m")
    conso_elec = conn.execute("""
        SELECT SUM(valeur_consommation) AS total
        FROM facture
        WHERE type='Electricité' AND strftime('%Y-%m', date_facture) = ?
    """, (current_month,)).fetchone()['total'] or 0

    conso_eau = conn.execute("""
        SELECT SUM(valeur_consommation) AS total
        FROM facture
        WHERE type='Consommation_eau' AND strftime('%Y-%m', date_facture) = ?
    """, (current_month,)).fetchone()['total'] or 0

    nb_capteurs_actifs = conn.execute("""
        SELECT COUNT(*) AS nb FROM capteur_actionneur
        WHERE port_communication IS NOT NULL
    """).fetchone()['nb']

    total_factures = conn.execute("""
        SELECT SUM(montant) AS total FROM facture
    """).fetchone()['total'] or 0

    conn.close()

    return render_template('index.html',
                           logement=logement,
                           weather_data=weather_data,
                           conso_mois_en_cours=conso_elec,
                           eau_mois_en_cours=conso_eau,
                           nb_capteurs_actifs=nb_capteurs_actifs,
                           total_factures=total_factures,
                           image_name="eco_house.jpg")


# ✅ Route consommation
@app.route('/consommation')
def consommation():
    date_debut = request.args.get('date_debut')
    date_fin = request.args.get('date_fin')

    query = """
        SELECT type, strftime('%Y-%m-%d', date_facture) AS date_facture,
               SUM(montant) AS montant, SUM(valeur_consommation) AS valeur_consommation
        FROM facture
        WHERE logement_id = 1
    """
    params = []
    if date_debut:
        query += " AND date_facture >= ?"
        params.append(date_debut)
    if date_fin:
        query += " AND date_facture <= ?"
        params.append(date_fin)

    query += """
        GROUP BY type, date_facture
        ORDER BY date_facture
    """

    conn = get_db_connection()
    factures = conn.execute(query, params).fetchall()
    conn.close()

    # ✅ Structuration des données pour le graphique
    labels = set()
    chart_data = {}

    for facture in factures:
        date = facture['date_facture']
        labels.add(date)
        type_conso = facture['type']

        if type_conso not in chart_data:
            chart_data[type_conso] = {
                'dates': [],
                'montant': [],
                'valeur_consommation': []
            }

        chart_data[type_conso]['dates'].append(date)
        chart_data[type_conso]['montant'].append(facture['montant'])
        chart_data[type_conso]['valeur_consommation'].append(facture['valeur_consommation'])

    labels = sorted(labels)

    return render_template('consommation.html',
                           chart_data=chart_data,
                           labels=labels,
                           date_debut=date_debut,
                           date_fin=date_fin)




# ✅ Route pour les capteurs
@app.route('/capteurs')
def capteurs():
    conn = get_db_connection()
    capteurs = conn.execute("""
        SELECT ca.id, tc.nom AS type, p.nom AS piece, 
               ca.reference_commerciale, ca.port_communication,
               (SELECT m.valeur FROM mesure m WHERE m.capteur_id = ca.id ORDER BY m.date_insertion DESC LIMIT 1) AS valeur,
               (SELECT m.date_insertion FROM mesure m WHERE m.capteur_id = ca.id ORDER BY m.date_insertion DESC LIMIT 1) AS date_insertion,
               tc.unite_mesure
        FROM capteur_actionneur ca
        JOIN type_capteur_actionneur tc ON ca.type_id = tc.id
        JOIN piece p ON ca.piece_id = p.id
    """).fetchall()
    conn.close()
    return render_template('capteur.html', capteurs=capteurs)


# ✅ Route API température (DHT22 - ID: 3)
@app.route('/api/capteurs/dht22/temperature', methods=['POST'])
def recevoir_temperature_dht22():
    data = request.get_json()
    temperature = data.get('temperature')

    if temperature is not None:
        conn = get_db_connection()
        conn.execute("""
            INSERT INTO mesure (capteur_id, valeur, date_insertion)
            VALUES (2, ?, CURRENT_TIMESTAMP)
        """, (temperature,))
        conn.commit()
        conn.close()
        return jsonify({"message": "Température insérée avec succès"}), 200

    return jsonify({"error": "Données invalides"}), 400


# ✅ Route API humidité (DHT22 - ID: 3)
@app.route('/api/capteurs/dht22/humidite', methods=['POST'])
def recevoir_humidite_dht22():
    data = request.get_json()
    humidite = data.get('humidite')

    if humidite is not None:
        conn = get_db_connection()
        conn.execute("""
            INSERT INTO mesure (capteur_id, valeur, date_insertion)
            VALUES (4, ?, CURRENT_TIMESTAMP)
        """, (humidite,))
        conn.commit()
        conn.close()
        return jsonify({"message": "Humidité insérée avec succès"}), 200

    return jsonify({"error": "Données invalides"}), 400


# ✅ Route Visualisation
@app.route('/capteurs/visualisation/<int:capteur_id>')
def visualiser_mesures(capteur_id):
    conn = get_db_connection()
    
    # Récupération des informations du capteur
    capteur = conn.execute("""
        SELECT ca.id, tc.nom AS type_nom, p.nom AS piece_nom, ca.reference_commerciale
        FROM capteur_actionneur ca
        JOIN type_capteur_actionneur tc ON ca.type_id = tc.id
        JOIN piece p ON ca.piece_id = p.id
        WHERE ca.id = ?
    """, (capteur_id,)).fetchone()

    # Vérification si le capteur existe
    if not capteur:
        conn.close()
        flash("Capteur introuvable.", "danger")
        return redirect(url_for('capteurs'))

    # Récupération des mesures
    mesures = conn.execute("""
        SELECT valeur, date_insertion FROM mesure
        WHERE capteur_id = ?
        ORDER BY date_insertion DESC
        LIMIT 50
    """, (capteur_id,)).fetchall()
    conn.close()

    # Récupération des données météo
    weather_data = get_weather()
    temp_externe = weather_data['main']['temp'] if weather_data else None
    temp_externe_values = [temp_externe for _ in mesures] if temp_externe is not None else []

    # Passage des données au template
    return render_template('visualisation.html',
                           capteur=capteur,
                           mesures=mesures,
                           temp_externe=temp_externe,
                           temp_externe_values=temp_externe_values)

# ✅ Route Configuration
@app.route('/configuration', methods=['GET', 'POST'])
def configuration():
    conn = get_db_connection()
    pieces = conn.execute("SELECT * FROM piece").fetchall()
    types = conn.execute("SELECT * FROM type_capteur_actionneur").fetchall()

    if request.method == 'POST':
        action = request.form['action']
        if action == 'add':
            type_id = request.form['type_id']
            piece_id = request.form['piece_id']
            reference_commerciale = request.form['reference_commerciale']
            port_communication = request.form['port_communication']

            conn.execute("""
                INSERT INTO capteur_actionneur (type_id, piece_id, reference_commerciale, port_communication) 
                VALUES (?, ?, ?, ?)""", (type_id, piece_id, reference_commerciale, port_communication))
            conn.commit()
            flash("Capteur ajouté avec succès !")
        elif action == 'activate':
            capteur_id = request.form['capteur_id']
            port_communication = f"COM{capteur_id}"
            conn.execute("""
                UPDATE capteur_actionneur SET port_communication = ? 
                WHERE id = ?""", (port_communication, capteur_id))
            flash("Capteur activé avec succès !")
            conn.commit()
        elif action in ['delete', 'deactivate']:
            capteur_id = request.form['capteur_id']
            if action == 'delete':
                conn.execute("DELETE FROM capteur_actionneur WHERE id = ?", (capteur_id,))
                flash("Capteur supprimé avec succès !")
            else:
                conn.execute("""
                    UPDATE capteur_actionneur SET port_communication = NULL 
                    WHERE id = ?""", (capteur_id,))
                flash("Capteur désactivé avec succès !")
            conn.commit()

        return redirect(url_for('configuration'))

    capteurs = conn.execute("""
        SELECT ca.id, tc.nom AS type_nom, p.nom AS piece_nom, 
               ca.reference_commerciale, ca.port_communication
        FROM capteur_actionneur ca
        JOIN type_capteur_actionneur tc ON ca.type_id = tc.id
        JOIN piece p ON ca.piece_id = p.id
    """).fetchall()
    conn.close()
    return render_template('configuration.html', pieces=pieces, types=types, capteurs=capteurs)

@app.route('/facturation', methods=['GET', 'POST'])
def facturation():
    conn = get_db_connection()
    logements = conn.execute("SELECT * FROM logement").fetchall()
    types_facture = ["Electricité", "Consommation_eau"]

    if request.method == 'POST':
        logement_id = request.form['logement_id']
        type_facture = request.form['type']
        montant = request.form['montant']
        valeur_consommation = request.form['valeur_consommation']
        date_facture = request.form['date_facture']

        # Validation du format de la date
        import re
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_facture):
            flash("Format de date invalide. Utilisez 'YYYY-MM-DD'.", "danger")
            return redirect(url_for('facturation'))

        conn.execute("""
            INSERT INTO facture (logement_id, type, montant, valeur_consommation, date_facture)
            VALUES (?, ?, ?, ?, ?)
        """, (logement_id, type_facture, montant, valeur_consommation, date_facture))
        conn.commit()
        flash("Facture ajoutée avec succès !", "success")
        return redirect(url_for('facturation'))

    # Récupération des factures
    date_debut = request.args.get('date_debut')
    date_fin = request.args.get('date_fin')

    query = """
        SELECT id, logement_id, type, date_facture, montant, valeur_consommation
        FROM facture
        WHERE 1=1
    """
    params = []
    if date_debut:
        query += " AND date_facture >= ?"
        params.append(date_debut)
    if date_fin:
        query += " AND date_facture <= ?"
        params.append(date_fin)
    query += " ORDER BY date_facture DESC"

    factures = conn.execute(query, params).fetchall()
    conn.close()

    return render_template('facturation.html',
                           logements=logements,
                           types_facture=types_facture,
                           factures=factures,
                           date_debut=date_debut,
                           date_fin=date_fin)

@app.route('/facturation/supprimer/<int:facture_id>', methods=['POST'])
def supprimer_facture(facture_id):
    conn = get_db_connection()
    try:
        conn.execute("DELETE FROM facture WHERE id = ?", (facture_id,))
        conn.commit()
        flash("Facture supprimée avec succès !", "success")
    except sqlite3.Error as e:
        flash(f"Erreur lors de la suppression : {e}", "danger")
    finally:
        conn.close()
    return redirect(url_for('facturation'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)


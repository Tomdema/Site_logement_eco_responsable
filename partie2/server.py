from http.server import BaseHTTPRequestHandler, HTTPServer
import sqlite3
import json
from urllib.parse import parse_qs

# Chemin vers la base de données SQLite
database_path = "/Users/tom-demagnokpowou-tazzou/Desktop/TP_IoT /TP_IoT_partie_4_7/database.db"

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/get_mesures":
            # Récupération des mesures dans la base de données
            conn = sqlite3.connect(database_path)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT * FROM mesure")
            mesures = [dict(row) for row in c.fetchall()]
            conn.close()

            # Envoi des mesures sous forme de JSON
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(mesures).encode())

        elif self.path == "/get_factures":
            # Récupération des factures dans la base de données
            conn = sqlite3.connect(database_path)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT * FROM facture")
            factures = [dict(row) for row in c.fetchall()]
            conn.close()

            # Envoi des factures sous forme de JSON
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(factures).encode())

    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length)
        params = parse_qs(post_data.decode())

        if self.path == "/add_mesure":
            # Ajout d'une mesure dans la base de données
            capteur_id = int(params.get("capteur_id", [0])[0])
            valeur = float(params.get("valeur", [0])[0])

            conn = sqlite3.connect(database_path)
            c = conn.cursor()
            c.execute("INSERT INTO mesure (capteur_id, valeur) VALUES (?, ?)", (capteur_id, valeur))
            conn.commit()
            conn.close()

            # Confirmation de l'ajout
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Mesure ajoutee avec succes.")

        elif self.path == "/add_facture":
            # Ajout d'une facture dans la base de données
            logement_id = int(params.get("logement_id", [0])[0])
            type_facture = params.get("type", [""])[0]
            montant = float(params.get("montant", [0])[0])
            valeur_consommation = float(params.get("valeur_consommation", [0])[0])

            conn = sqlite3.connect(database_path)
            c = conn.cursor()
            c.execute(
                "INSERT INTO facture (logement_id, type, montant, valeur_consommation) VALUES (?, ?, ?, ?)",
                (logement_id, type_facture, montant, valeur_consommation),
            )
            conn.commit()
            conn.close()

            # Confirmation de l'ajout
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Facture ajoutee avec succes.")

# récupérer les mesures avec l'instruction curl -X GET http://localhost:8888/get_mesures 
# récupérer les mesures avec l'instruction curl -X GET http://localhost:8888/get_factures
# poster des mesures avec l'instruction curl -X POST -d "capteur_id=1&valeur=25.5" http://localhost:8888/add_mesure
# poster des mesures avec l'instruction curl -X POST -d "logement_id=1&type=Electricite&montant=100.0&valeur_consommation=200.0" http://localhost:8888/add_facture


if __name__ == "__main__":
    server = HTTPServer
    httpd = server(("localhost", 8888), MyHandler)
    print("Serveur HTTP en cours d'exécution sur http://localhost:8888...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

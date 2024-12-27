import http.server
import json
import sqlite3
import os

# Configuration de la base de données
database_path = "/Users/tom-demagnokpowou-tazzou/Desktop/TP_IoT /TP_IoT_partie_4_7/database.db"

class MyHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/upload_data':
            try:
                # Lire les données POST
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))

                temperature = data.get('temperature')
                humidity = data.get('humidity')

                # Vérification des données reçues
                if temperature is None or humidity is None:
                    raise ValueError("Invalid payload: 'temperature' and 'humidity' are required.")

                # Vérification de l'existence de la base
                if not os.path.exists(database_path):
                    raise FileNotFoundError(f"Database file not found: {database_path}")

                # Connexion et insertion dans la base de données
                conn = sqlite3.connect(database_path)
                c = conn.cursor()

                c.execute(
                    "INSERT INTO mesure (capteur_id, valeur, date_insertion) VALUES (3, ?, datetime('now'))",
                    (temperature,)
                )
                c.execute(
                    "INSERT INTO mesure (capteur_id, valeur, date_insertion) VALUES (3, ?, datetime('now'))",
                    (humidity,)
                )

                conn.commit()
                conn.close()

                # Réponse de succès
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"status": "success"}')

            except sqlite3.Error as e:
                # Erreur liée à SQLite
                self.send_response(500)
                self.end_headers()
                error_message = f"Database error: {e}"
                print(error_message)
                self.wfile.write(f'{{"status": "error", "message": "{error_message}"}}'.encode('utf-8'))

            except Exception as e:
                # Autre erreur
                self.send_response(500)
                self.end_headers()
                error_message = f"Unexpected error: {e}"
                print(error_message)
                self.wfile.write(f'{{"status": "error", "message": "{error_message}"}}'.encode('utf-8'))

def run(server_class=http.server.HTTPServer, handler_class=MyHandler):
    server_address = ('', 8888)
    httpd = server_class(server_address, handler_class)
    print('Starting server on port 8888...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()

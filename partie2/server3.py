import http.server
import socketserver
import requests
from datetime import datetime

# Configuration de l'API OpenWeather
LAT = "48.8566"  # Latitude de Paris
LON = "2.3522"   # Longitude de Paris
API_KEY = "350aea51d0cfada04d8f7b339ce23a74"

class MyHandler(http.server.BaseHTTPRequestHandler):

    # Méthode pour gérer les requêtes GET et afficher la page des prévisions météo
    def do_GET(self):
        if self.path == "/weather":
            self.handle_weather()
        else:
            self.send_error(404, "Page non trouvée")

    # Méthode pour récupérer les données météo et générer une page HTML
    def handle_weather(self):
        try:
            # Appel de l'API météo
            url = f"https://api.openweathermap.org/data/3.0/onecall?lat={LAT}&lon={LON}&exclude=current,minutely,hourly,alerts&units=metric&appid={API_KEY}"
            response = requests.get(url)
            response.raise_for_status()
            weather_data = response.json()
            
            # Extraction des prévisions pour 5 jours
            daily_forecasts = weather_data.get("daily", [])[:5]
            
            # Construction de la page HTML avec style
            html_content = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Prévisions Météo à 5 jours</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        margin: 20px;
                        background-color: #f9f9f9;
                        color: #333;
                    }
                    h1 {
                        color: #007BFF;
                        text-align: center;
                    }
                    table {
                        width: 100%;
                        border-collapse: collapse;
                        margin-top: 20px;
                    }
                    th, td {
                        border: 1px solid #ddd;
                        padding: 8px;
                        text-align: center;
                    }
                    th {
                        background-color: #007BFF;
                        color: white;
                    }
                    tr:nth-child(even) {
                        background-color: #f2f2f2;
                    }
                    tr:hover {
                        background-color: #ddd;
                    }
                </style>
            </head>
            <body>
                <h1>Prévisions Météo à 5 jours</h1>
                <table>
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Température Jour</th>
                            <th>Température Nuit</th>
                            <th>Condition</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            
            # Ajout des lignes de prévisions météo
            for forecast in daily_forecasts:
                date = datetime.fromtimestamp(forecast["dt"]).strftime("%Y-%m-%d")
                temp_day = forecast["temp"]["day"]
                temp_night = forecast["temp"]["night"]
                weather_condition = forecast["weather"][0]["description"]
                html_content += f"""
                    <tr>
                        <td>{date}</td>
                        <td>{temp_day}°C</td>
                        <td>{temp_night}°C</td>
                        <td>{weather_condition.capitalize()}</td>
                    </tr>
                """
            
            # Fermeture de la table et du HTML
            html_content += """
                    </tbody>
                </table>
            </body>
            </html>
            """
            
            # Envoi de la réponse
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html_content.encode("utf-8"))
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(f"Erreur lors de la récupération des prévisions météo: {str(e)}".encode("utf-8"))
#http://localhost:8888/weather
if __name__ == "__main__":
    # Configuration du serveur HTTP
    PORT = 8888
    Handler = MyHandler
    server = socketserver.TCPServer(("localhost", PORT), Handler)
    
    print(f"Serveur en cours d'exécution sur http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()

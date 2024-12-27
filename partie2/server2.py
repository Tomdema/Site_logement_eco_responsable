from http.server import BaseHTTPRequestHandler, HTTPServer
import sqlite3
import json

# Chemin vers la base de données SQLite
database_path = "/Users/tom-demagnokpowou-tazzou/Desktop/TP_IoT /TP_IoT_partie_4_7/database.db"

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/factures_pie_chart":
            # Récupération des factures dans la base de données
            conn = sqlite3.connect(database_path)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT type, SUM(montant) as total_montant FROM facture GROUP BY type")
            factures = c.fetchall()
            conn.close()

            # Construction des données pour Google Charts
            chart_data = [["Type", "Montant"]]
            for facture in factures:
                chart_data.append([facture["type"], float(facture["total_montant"])])

            # Génération de la page HTML avec Google Charts
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Camembert des Factures</title>
                <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
                <script type="text/javascript">
                    google.charts.load('current', {{'packages':['corechart']}});
                    google.charts.setOnLoadCallback(drawChart);

                    function drawChart() {{
                        var data = google.visualization.arrayToDataTable({json.dumps(chart_data)});
                        var options = {{
                            title: 'Repartition des Montants des Factures',
                            is3D: true,
                        }};
                        var chart = new google.visualization.PieChart(document.getElementById('piechart'));
                        chart.draw(data, options);
                    }}
                </script>
            </head>
            <body>
                <h1>Repartition des Montants des Factures</h1>
                <div id="piechart" style="width: 900px; height: 500px;"></div>
            </body>
            </html>
            """

            # Envoi de la réponse HTTP
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode())
#http://localhost:8888/factures_pie_chart

if __name__ == "__main__":
    server_class = HTTPServer
    httpd = server_class(("localhost", 8888), MyHandler)
    print("Serveur HTTP en cours d'exécution sur http://localhost:8888...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

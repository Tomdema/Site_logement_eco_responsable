#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include "DHT.h"

// Remplacez par l'adresse IP de votre serveur Python
#define SERVER_IP "192.168.75.5:8888"  // Exemple d'adresse IP du serveur Python

#ifndef STASSID
#define STASSID "Gad"
#define STAPSK "Gadou242@"
#endif

#define DHTPIN 5    // Pin numérique connecté au capteur DHT
#define DHTTYPE DHT22   // Type de capteur DHT
#define LED_PIN 2  // Pin numérique connectée à la LED (par exemple GPIO2)

DHT dht(DHTPIN, DHTTYPE);  // Initialiser le capteur DHT

void setup() {
  Serial.begin(115200);
  Serial.println();
  Serial.println("DHTxx test!");

  // Connexion au WiFi
  WiFi.begin(STASSID, STAPSK);
  
  unsigned int statusCode = WiFi.status();
  while (statusCode != WL_CONNECTED) {
    
    Serial.println(statusCode);
    delay(500);
    Serial.print(".");
    statusCode = WiFi.status();
  }
  Serial.println("");
  Serial.print("Connected! IP address: ");
  Serial.println(WiFi.localIP());

  dht.begin();  // Démarrer le capteur DHT

  pinMode(LED_PIN, OUTPUT);  // Configurer la broche de la LED comme sortie
}

void loop() {
  // Attendre quelques secondes entre les mesures
  delay(2000);

  // Lire l'humidité et la température
  float h = dht.readHumidity();
  float t = dht.readTemperature();

  // Vérifier si les lectures ont échoué
  if (isnan(h) || isnan(t)) {
    Serial.println(F("Failed to read from DHT sensor!"));
    return;
  }

  // Afficher les données dans le moniteur série
  Serial.print(F("Humidity: "));
  Serial.print(h);
  Serial.print(F("%  Temperature: "));
  Serial.print(t);
  Serial.println(F("°C"));

  // Logique pour allumer ou éteindre la LED en fonction de la température
  if (t > 27) {  // Si la température dépasse 25°C
    Serial.println("LED ON");  // Débogage
    digitalWrite(LED_PIN, LOW);  // Allumer la LED
  } else {
    Serial.println("LED OFF");  // Débogage
    digitalWrite(LED_PIN, HIGH);  // Éteindre la LED
  }

  // Envoyer les données au serveur Python
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClient client;
    HTTPClient http;

    Serial.print("[HTTP] begin...\n");
    http.begin(client, "http://" SERVER_IP "/upload_data");  // URL du serveur
    http.addHeader("Content-Type", "application/json");

    // Créer le payload JSON
    String jsonPayload = String("{\"temperature\":") + t + ",\"humidity\":" + h + "}";

    Serial.print("[HTTP] POST...\n");
    int httpCode = http.POST(jsonPayload);  // Envoyer la requête POST avec les données

    // Vérifier la réponse
    if (httpCode > 0) {
      Serial.printf("[HTTP] POST... code: %d\n", httpCode);
      if (httpCode == HTTP_CODE_OK) {
        String payload = http.getString();
        Serial.println("Received payload:\n<<");
        Serial.println(payload);
        Serial.println(">>");
      }
    } else {
      Serial.printf("[HTTP] POST... failed, error: %s\n", http.errorToString(httpCode).c_str());
    }

    http.end();  // Terminer la requête
  } else {
    Serial.println("WiFi not connected!");
  }
}

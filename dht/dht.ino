#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include "DHT.h"

// ⚙️ Configuration du réseau Wi-Fi
#define SERVER_IP "192.168.1.119:5001" // IP locale du serveur Flask
#define STASSID "Meteor-56CD710D"
#define STAPSK "H6NXv6t9fPc6vKDf"

// ⚙️ Configuration du capteur DHT
#define DHTPIN 5        // Broche du capteur DHT22
#define DHTTYPE DHT22   // Type du capteur

// ⚙️ Configuration LED
#define LED_PIN 2

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  // 🛜 Connexion Wi-Fi
  WiFi.begin(STASSID, STAPSK);
  Serial.print("Connexion au Wi-Fi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n✅ Wi-Fi connecté !");
  Serial.print("Adresse IP : ");
  Serial.println(WiFi.localIP());

  dht.begin();
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
}

void loop() {
  delay(5000); // Lecture toutes les 5 secondes

  // 📊 Lecture des données du capteur DHT
  float h = dht.readHumidity();
  float t = dht.readTemperature();

  if (isnan(h) || isnan(t)) {
    Serial.println("❌ Erreur de lecture du capteur DHT !");
    return;
  }

  Serial.printf("🌡️ Température : %.2f°C | 💧 Humidité : %.2f%%\n", t, h);

  // 🟢 Gestion de la LED
  digitalWrite(LED_PIN, (t > 27) ? LOW : HIGH);

  // 🛜 Envoi des données au serveur Flask
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClient client;
    HTTPClient http;

    // 🔗 Envoi de la Température
    http.begin(client, "http://" SERVER_IP "/api/capteurs/dht22/temperature");
    http.addHeader("Content-Type", "application/json");
    String tempPayload = String("{\"temperature\":") + t + "}";
    int httpResponseCodeTemp = http.POST(tempPayload);
    Serial.println(httpResponseCodeTemp > 0 ? "✅ Température envoyée" : "❌ Erreur d'envoi Température");
    http.end();

    // 🔗 Envoi de l'Humidité
    http.begin(client, "http://" SERVER_IP "/api/capteurs/dht22/humidite");
    http.addHeader("Content-Type", "application/json");
    String humidPayload = String("{\"humidite\":") + h + "}";
    int httpResponseCodeHumid = http.POST(humidPayload);
    Serial.println(httpResponseCodeHumid > 0 ? "✅ Humidité envoyée" : "❌ Erreur d'envoi Humidité");
    http.end();
  } else {
    Serial.println("❌ Wi-Fi déconnecté !");
    WiFi.begin(STASSID, STAPSK);
  }
}

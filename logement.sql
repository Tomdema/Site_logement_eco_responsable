-- database: /Users/tom-demagnokpowou-tazzou/Desktop/TP_IoT /TP_IoT_partie_4_7/partie3/database.db
--sqlite3 logement.db
--.read logement.sql
--Question 2
-- Suppression des tables si elles existent déjà (pour éviter les conflits)
DROP TABLE IF EXISTS mesure; 
DROP TABLE IF EXISTS capteur_actionneur;
DROP TABLE IF EXISTS type_capteur_actionneur;
DROP TABLE IF EXISTS piece;
DROP TABLE IF EXISTS facture;
DROP TABLE IF EXISTS logement;

--Question 3
-- Création de la table 'logement'
CREATE TABLE logement (id INTEGER PRIMARY KEY AUTOINCREMENT, adresse TEXT NOT NULL,telephone TEXT, adresse_ip TEXT, date_insertion TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

-- Création de la table 'piece'
CREATE TABLE piece (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT NOT NULL,logement_id INTEGER,coordonnees TEXT,FOREIGN KEY (logement_id) REFERENCES logement(id));

-- Création de la table 'type_capteur_actionneur'
CREATE TABLE type_capteur_actionneur (id INTEGER PRIMARY KEY AUTOINCREMENT,nom TEXT NOT NULL,unite_mesure TEXT, plage_precision TEXT  
);

-- Création de la table 'capteur_actionneur'
CREATE TABLE capteur_actionneur (id INTEGER PRIMARY KEY AUTOINCREMENT,type_id INTEGER,piece_id INTEGER,reference_commerciale TEXT,port_communication TEXT,date_insertion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY (type_id) REFERENCES type_capteur_actionneur(id),FOREIGN KEY (piece_id) REFERENCES piece(id));

-- Création de la table 'mesure'
CREATE TABLE mesure (id INTEGER PRIMARY KEY AUTOINCREMENT,capteur_id INTEGER,valeur REAL,
    date_insertion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY (capteur_id) REFERENCES capteur_actionneur(id));

-- Création de la table 'facture'
CREATE TABLE facture (id INTEGER PRIMARY KEY AUTOINCREMENT,logement_id INTEGER, type TEXT,date_facture TIMESTAMP DEFAULT CURRENT_TIMESTAMP,montant REAL, valeur_consommation REAL, FOREIGN KEY (logement_id) REFERENCES logement(id));

-- Question 4
-- logement
INSERT INTO logement (adresse, telephone, adresse_ip) VALUES
('134 Route de chartres Bures-sur-yvette 91440', '+33744580672', '192.168.1.198');
--Pieces 
INSERT INTO piece (nom, logement_id, coordonnees) VALUES
('Salon' , 1, '0,0,0'),
('chambre1', 1, '1,0,0'),
('chambre2', 1, '1,1,0'),
('Cuisine', 1, '0,0,1');

-- Question 5
INSERT INTO type_capteur_actionneur (nom, unite_mesure, plage_precision) VALUES 
('Température', '°C', '-20 à 140'),
('Humidité', 'g/m^3', '0-500'),
('Electricité', 'Kwh', '0-10000'),
('Consommation_eau', 'litres', '0-10000');

-- Question 6
INSERT INTO capteur_actionneur (type_id, piece_id, reference_commerciale, port_communication) VALUES
(1, 1, 'DHT11', 'COM1'),
(1, 1, 'DHT22', 'COM1'),
(3, 2, 'Somfy','COM5'),  -- Capteur de température
(2, 2, 'DHT22', 'COM2');  -- Capteur de consommation électrique

-- Exemple d'insertion de mesures
INSERT INTO mesure (capteur_id, valeur) VALUES
(1, 27.5),  -- Température mesurée
(1, 10.0), -- Consommation électrique en kWh
(2, 32.5),  -- Température mesurée
(2, 100.0); -- Consommation électrique en kWh
-- Exemple d'insertion de factures
INSERT INTO facture (logement_id, type, montant, valeur_consommation) VALUES
(1, 'Electricité', 75.0, 150.0),
(1, 'Consommation_eau', 30.0, 120.0);


# Site_logement_eco_responsable
Création d'un site pour la gestion des capteurs rendant une maison éco responsable efficiente

Ce projet est une application Flask pour la gestion et la visualisation des données d'une maison éco-responsable. Elle permet de suivre les mesures des capteurs de température et d'humidité, gérer les factures d'électricité et d'eau, et afficher des informations météorologiques en temps réel.

Pour lancer mon serveur Flask sur votre machine (backend.py), commencez par créer un environnement virtuel avec python -m venv venv et activez-le (source venv/bin/activate sur macOS/Linux ou venv\Scripts\activate sur Windows). Ensuite, mettez à jour pip avec pip install --upgrade pip et installez les dépendances nécessaires avec pip install flask flask-caching requests python-dotenv
_ Assurez vous que le DATABASE_PATH soit bien renseigné (lcalisation du fichier database.db ou générez le database.db avec le fichier sql) 
_ Le serveur est configuré pour démarrer sur le port 5001. Si nécessaire, modifiez dans cette ligne (essayez les ports 5000 et 5002 si votre port 5001 est occupé) : app.run(host='0.0.0.0', port=5001)
_ Si vous possedez un capteur dht 22 et un esp8266 , modifiez les parametres de connexion ainsi que la broche où est branché le dht sur votre esp dans le fichier dht.ino. Téléverser le code sur votre carte, les données envoyées rempliront automatiquement la rubtique mesure de la base de données et vous pourrez visualiser les données après avoir lancé le server Flask allez sur : http://localhost:5001


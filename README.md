# ELNEO_GOOGLE_DOCUMENTAI
ELNEO_LANDEVELD delivery document scanned nécessitant de OCR via IA de google

📄 Document AI PDF Extraction API
🎯 Objectif

Cette application permet d’extraire automatiquement des données (numéro de commande, lignes d’articles, quantités, etc.) à partir de PDF scannés en utilisant Google Document AI.

Le résultat est généré sous forme de fichier CSV téléchargeable.

🏗️ Architecture

Utilisateur → Interface Web → API FastAPI → Document AI → CSV

⚙️ Technologies utilisées
Python 3.11
FastAPI
Google Document AI
Pandas
Docker
Cloud Run
☁️ Configuration Google Cloud
🔹 Projet (en test jusqu'au 3 juillet 2026) 
project-8ac1d017-6b96-435e-978
🔹 APIs activées
Document AI API
Cloud Run API
Cloud Build API
Artifact Registry
🔹 Service Account
document-ai-service@project-8ac1d017-6b96-435e-978.iam.gserviceaccount.com
Rôle requis :
Document AI User
🔹 DOCUMENT AI : processeur: Custom Extractor= fourniture de 5 fichiers train, spécification des zones recherchées, établissement de la logique par IA 
Schema des zones recherchées: 
par page : POnumber
line_item (multiples) comprenant Pos, ordered,Shipped,code,description,article 

🤖 Configuration Document AI
Location : eu
Processor ID : 20041c8991c17684

🚀 Lancer en local
1. Installer les dépendances
pip install -r requirements.txt
2. Lancer l’application
uvicorn main:app --reload
3. Accéder à l’interface (via un autre terminal)
http://localhost:8000

🖥️ Utilisation
Ouvrir l’URL de l’application :"https://test-service-326356944878.europe-west1.run.app" sur les serveurs cloud run EU 
Charger un PDF scanné
Cliquer sur "Uploader et traiter"
Télécharger le fichier CSV généré

🐳 Docker
Build
docker build -t document-ai-app .
Run
docker run -p 8080:8080 document-ai-app
☁️ Déploiement Cloud Run
1. Build de l’image
gcloud builds submit \
  --tag europe-west1-docker.pkg.dev/project-8ac1d017-6b96-435e-978/cloud-run-source-deploy/test-service
2. Déploiement
gcloud run deploy test-service \
  --image europe-west1-docker.pkg.dev/project-8ac1d017-6b96-435e-978/cloud-run-source-deploy/test-service \
  --region europe-west1 \
  --allow-unauthenticated
   
🔌 API
GET /
Affiche une interface web simple pour uploader un fichier PDF.

POST /process
Request
Form-data :
file : fichier PDF
Response
Fichier CSV téléchargeable
📂 Structure du projet
.
├── main.py
├── requirements.txt
├── Dockerfile
└── README.md

⚠️ Points importants
Le client Document AI est initialisé dans la fonction (évite les crashs Cloud Run)
Le service écoute sur le port 8080
Gunicorn est utilisé pour la production

🐞 Problèmes rencontrés
Problème	Solution
Container ne démarre pas	Ne pas initialiser Document AI globalement
Gunicorn introuvable	Ajouter dans requirements.txt
Erreur port 8080	Vérifier CMD Docker
404 endpoint	Vérifier les routes FastAPI

🚀 Améliorations possibles
Interface utilisateur avancée (React / Streamlit)
Affichage des données avant export
Stockage dans Cloud Storage
Traitement batch de fichiers
mise en place de securité pour controler l'utilisation 

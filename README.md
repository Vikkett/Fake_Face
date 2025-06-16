# Fake_Face
Professional Face Swap est une application de bureau en Python permettant de réaliser des échanges de visages (face swap) de haute qualité entre deux images, ou en direct via webcam.

🧠 Fonctionnalités
📂 Charger une image source et une image cible

🧍 Générer un visage IA automatiquement depuis le web

🎥 Utiliser la webcam pour capturer une image source ou cible

🤖 Détection des visages et repérage de 68 points faciaux avec Dlib

🔄 Remplacement du visage avec ajustement des couleurs et mélange

🎛️ Contrôle de l’intensité du mélange et de la correction colorimétrique

💾 Enregistrement du résultat final

🖥️ Mode Live avec webcam (swap en temps réel)

🔧 Prérequis
Python 3.6+

Modules Python :

opencv-python

numpy

dlib

Pillow

tkinter (souvent inclus avec Python)

uuid

urllib

Modèle requis :
Télécharger shape_predictor_68_face_landmarks.dat depuis :
https://github.com/davisking/dlib-models
Placez le fichier dans le même dossier que le script.

▶️ Utilisation
Lancer l’application
bash
Copier
Modifier
python nom_du_fichier.py
Étapes typiques
Cliquez sur "Load Source" pour charger l’image du visage à transférer.

Cliquez sur "Load Target" pour charger l’image cible.

Cliquez sur "Swap Faces" pour effectuer l’échange.

Ajustez les curseurs de mélange et de correction des couleurs selon votre préférence.

Cliquez sur "Save Result" pour enregistrer l’image obtenue.

Essayez le mode Live avec une webcam pour tester en temps réel.

💡 Options supplémentaires
Generate AI Face : récupère un visage généré aléatoirement par IA.

Webcam Source / Target : capture une image directement depuis votre webcam.

Live Swap Video : active le remplacement de visage en temps réel avec la webcam.

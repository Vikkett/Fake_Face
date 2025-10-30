# FakeFace V 0.8

Application Python de **face swap** (échange de visages) avec interface graphique **Tkinter**, détection faciale via **dlib**, traitement d’images **OpenCV**, génération de visage IA (**thispersondoesnotexist.com**), sauvegarde, envoi **par e-mail** et mode **Live** (webcam en temps réel) pour un projet de portes ouvertes au CPNV.

> ⚠️ **Avertissement légal & éthique**  
> Utilisez ce programme uniquement avec le **consentement explicite** des personnes concernées.  
> Respectez les lois en vigueur (droit à l’image, RGPD/LPD) et les CGU des services tiers.

---

## 📸 Aperçu

Le projet permet :
- De charger deux images (source et cible)
- De détecter les visages via **dlib**
- De déformer et ajuster les couleurs de la source vers la cible
- D’effectuer un **blending** doux entre les deux visages
- De sauvegarder ou d’envoyer le résultat par e-mail
- D’utiliser un **mode Live** via webcam

---

## ✨ Fonctionnalités principales

- Interface **Tkinter** moderne et intuitive  
- Détection et repérage facial via `shape_predictor_68_face_landmarks.dat`  
- Chargement depuis fichier ou **webcam**
- Génération de **visage IA** automatique
- Réglages dynamiques : **opacité (Blend)** et **correction colorimétrique**
- **Masque doux** (convex hull élargi de 15 % + flou gaussien)
- **Envoi SMTP sécurisé** via Gmail (configurable)
- **Mode Live** fluide et léger pour le swap en direct

---

## 🧱 Architecture du projet

```bash
project/
├── main.py
├── shape_predictor_68_face_landmarks.dat
├── ai_faces/
├── icons/
│   ├── folder.png
│   ├── camera.png
│   ├── ai.png
│   ├── swap.png
│   ├── save.png
│   └── mail.png
├── .env                  # (optionnel) configuration SMTP
└── README.md
```

---

## ⚙️ Installation

### 1️⃣ Cloner le dépôt
```bash
git clone https://github.com/<votre-utilisateur>/<votre-projet>.git
cd <votre-projet>
```

### 2️⃣ Créer un environnement virtuel
```bash
python -m venv .venv
# Windows :
.venv\Scripts\activate
# macOS / Linux :
source .venv/bin/activate
```

### 3️⃣ Installer les dépendances
```bash
installer vs code pour utiliser C#
pip install opencv-python numpy Pillow dlib python-dotenv
```


---

## 🚀 Démarrage

```bash
python main.py
```

### Étapes d’utilisation :
1. **Load Source** et **Load Target**  
2. (Optionnel) **Generate AI Face**  
3. Cliquer sur **Swap Faces**  
4. Ajuster les sliders :  
   - `Blend Amount (Source Opacity)`  
   - `Color Adjustment`  
5. **Save Result** ou **Email Result**

---

## 🖥️ Interface graphique

| Bouton | Fonction |
|--------|-----------|
| **Load Source / Load Target** | Charger les images |
| **Webcam Source / Target** | Capturer depuis la caméra |
| **Generate AI Face** | Télécharger un visage IA |
| **Swap Faces** | Exécuter le swap |
| **Live Swap** | Mode webcam en direct |
| **Save Result** | Enregistrer le résultat |
| **Email Result** | Envoyer par e-mail |

---

## 🔐 Configuration E-mail sécurisée (.env)

Créer un fichier `.env` à la racine du projet :

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=465
SENDER_EMAIL=exemple@gmail.com
SENDER_PASSWORD=mot_de_passe_application
```

Dans le code :
```python
from dotenv import load_dotenv
import os

load_dotenv()
sender_email = os.getenv("SENDER_EMAIL")
sender_password = os.getenv("SENDER_PASSWORD")
smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
smtp_port = int(os.getenv("SMTP_PORT", "465"))
```

> 💡 Pour Gmail : activez la **vérification en deux étapes** et utilisez un **mot de passe d’application**.

---

## 🎥 Mode Live

- La **source** doit être chargée avant d’activer le mode.  
- Le masque utilisé est simplifié pour de meilleures performances.  
- Appuyer sur **Échap** pour quitter le mode Live.

---

## 💾 Sauvegarde & Export

- Enregistrement au format `.jpg` ou `.png`
- Nom automatique : `swap_<source>_<target>.jpg`
- Envoi par e-mail via **SMTP sécurisé (SSL)**

---

## ⚡ Performance & compatibilité

- Recommandé : images entre **720p** et **1080p**
- Éviter les fichiers > 20 MP
- Le mode **Live** dépend des performances CPU/GPU
- Compatible : **Windows**, **macOS**, **Linux**

---

## 🧩 Dépannage (FAQ)

**Q : “Dlib model not loaded”**  
➡️ Vérifiez que `shape_predictor_68_face_landmarks.dat` est bien à la racine.

**Q : “Cannot open webcam”**  
➡️ Fermez d’autres applications (Zoom, OBS...) et réessayez.  

**Q : “Face not detected”**  
➡️ Utilisez une image nette, visage bien visible et frontal.

**Q : “Email failed to send”**  
➡️ Vérifiez les identifiants SMTP et le port 465 (SSL activé).

---

## 🧠 Conseils techniques

- Le masque est créé à partir du **convex hull** des 68 landmarks, élargi de 15 %.  
- Flou Gaussien appliqué pour un bord doux : `GaussianBlur(25x25)`  
- Correction colorimétrique en **LAB** avec stats pondérées par masque.  
- Blending pondéré : `result = src * alpha + target * (1 - alpha)`

---

## 🛡️ Sécurité & conformité

- Obtenir un **consentement explicite** avant tout traitement.  
- Ne pas diffuser de deepfakes à des fins trompeuses.  
- Respecter les **réglementations RGPD/LPD**.  
- Ne jamais stocker de **mots de passe** dans le code.  

---

## 🧭 Feuille de route (Roadmap)

- [ ] Poisson blending pour fusion plus réaliste  
- [ ] Multi-visages & sélection manuelle  
- [ ] Accélération GPU (CUDA/cuDNN)  
- [ ] Interface plus réactive (threading)  
- [ ] Export automatique PDF + métadonnées  

---

## 📄 Licence

Projet éducatif CPNV
---

## 🙏 Crédits

- **Dlib** — Davis E. King  
- **OpenCV** — OpenCV.org  
- **Pillow** — Python Imaging Library  
- **thispersondoesnotexist.com** — pour la génération de visages IA  

# Importation de la bibliothèque OpenCV pour le traitement d’images et la vidéo
import cv2

# Importation de NumPy pour la manipulation de tableaux et matrices
import numpy as np

# Importation de Dlib pour la détection et le repérage des points clés du visage
import dlib

# Importation des composants Tkinter pour créer l’interface graphique
from tkinter import *

# Importation de la boîte de dialogue de fichiers et messages Tkinter
from tkinter import filedialog, messagebox

# Importation de PIL pour gérer l’affichage des images dans Tkinter
from PIL import Image, ImageTk

# Importation du module OS pour la gestion des fichiers et dossiers
import os

# Importation de urllib.request pour télécharger des images depuis le web
import urllib.request

# Importation de uuid pour générer des identifiants uniques (nommer fichiers)
import uuid


# Définition de la classe principale de l’application
class FaceSwapApp:
    # Initialisation de l’application avec la fenêtre Tkinter
    def __init__(self, root):
        # Sauvegarde de la fenêtre principale
        self.root = root
        # Création de l’interface utilisateur
        self.setup_ui()
        # Chargement des modèles de détection de visages
        self.load_models()

        # Initialisation des images source, cible et résultat
        self.source_image = None
        self.target_image = None
        self.result_image = None

        # Chemins des fichiers source et cible
        self.source_path = ""
        self.target_path = ""

        # Dimensions par défaut d’affichage
        self.display_width = 400
        self.display_height = 300


    # Méthode pour configurer l’interface graphique (UI)
    def setup_ui(self):
        # Titre de la fenêtre principale
        self.root.title("Professional Face Swap v2.3")

        # Dimensions initiales de la fenêtre
        self.root.geometry("1000x700")

        # Taille minimale de la fenêtre
        self.root.minsize(900, 600)

        # Création d’un cadre principal qui contient toute l’interface
        main_frame = Frame(self.root)
        # Placement du cadre (remplit tout l’espace disponible avec marges)
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Création d’un cadre pour afficher les images
        self.image_frame = Frame(main_frame)
        # Placement du cadre image
        self.image_frame.pack(fill=BOTH, expand=True)

        # Cadre pour l’image source
        self.source_frame = LabelFrame(self.image_frame, text="Source Image")
        # Placement de ce cadre dans une grille
        self.source_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # Label (zone d’affichage) pour l’image source
        self.source_label = Label(self.source_frame)
        # Placement du label
        self.source_label.pack()

        # Cadre pour l’image cible
        self.target_frame = LabelFrame(self.image_frame, text="Target Image")
        # Placement dans la grille
        self.target_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        # Label (zone d’affichage) pour l’image cible
        self.target_label = Label(self.target_frame)
        # Placement du label
        self.target_label.pack()

        # Cadre pour l’image résultat
        self.result_frame = LabelFrame(self.image_frame, text="Result Image")

        # Label pour afficher l’image résultat
        self.result_label = Label(self.result_frame)
        # Placement du label
        self.result_label.pack()

        # Cadre contenant les boutons de contrôle
        control_frame = Frame(main_frame)
        # Placement sous les images
        control_frame.pack(fill=X, pady=10)

        # Bouton pour charger l’image source
        Button(control_frame, text="Load Source", command=self.load_source).grid(row=0, column=0, padx=5)

        # Bouton pour charger l’image cible
        Button(control_frame, text="Load Target", command=self.load_target).grid(row=0, column=1, padx=5)

        # Bouton pour exécuter l’échange de visages
        Button(control_frame, text="Swap Faces", command=self.swap_faces).grid(row=0, column=2, padx=5)

        # Bouton pour sauvegarder le résultat (désactivé par défaut)
        self.save_button = Button(control_frame, text="Save Result", command=self.save_result, state=DISABLED)
        self.save_button.grid(row=0, column=3, padx=5)

        # Bouton pour générer un visage aléatoire depuis l’IA
        Button(control_frame, text="Generate AI Face", command=self.generate_ai_face).grid(row=0, column=4, padx=5)

        # Bouton pour capturer une image source via la webcam
        Button(control_frame, text="Webcam Source", command=lambda: self.capture_from_webcam(is_source=True)).grid(
            row=0, column=5, padx=5)

        # Bouton pour capturer une image cible via la webcam
        Button(control_frame, text="Webcam Target", command=lambda: self.capture_from_webcam(is_source=False)).grid(
            row=0, column=6, padx=5)

        # Bouton pour ouvrir un mode d’échange de visages en direct (vidéo)
        Button(control_frame, text="Live Swap Video", command=self.open_live_video).grid(row=0, column=7, padx=5)

        # Cadre des réglages (blend, color)
        settings_frame = Frame(control_frame)
        # Placement sous la ligne de boutons
        settings_frame.grid(row=1, column=0, columnspan=8, pady=5)

        # Label pour le paramètre "Blend Amount"
        Label(settings_frame, text="Blend Amount:").grid(row=0, column=0)

        # Curseur pour régler la fusion entre source et cible
        self.blend_scale = Scale(settings_frame, from_=0, to=100, orient=HORIZONTAL, length=150)
        # Valeur par défaut = 65
        self.blend_scale.set(65)
        # Placement du curseur
        self.blend_scale.grid(row=0, column=1)
        # Mise à jour du swap quand l’utilisateur relâche la souris
        self.blend_scale.bind("<ButtonRelease-1>", self.update_blend)

        # Label pour le paramètre "Color Adjustment"
        Label(settings_frame, text="Color Adjustment:").grid(row=0, column=2)

        # Curseur pour régler l’ajustement de couleur
        self.color_scale = Scale(settings_frame, from_=0, to=100, orient=HORIZONTAL, length=150)
        # Valeur par défaut = 50
        self.color_scale.set(50)
        # Placement du curseur
        self.color_scale.grid(row=0, column=3)
        # Mise à jour du swap quand la souris est relâchée
        self.color_scale.bind("<ButtonRelease-1>", self.update_color)

        # Variable pour afficher l’état en bas de la fenêtre
        self.status_var = StringVar()
        # Message initial
        self.status_var.set("Ready to load images")

        # Barre de statut en bas
        status_bar = Label(self.root, textvariable=self.status_var, bd=1, relief=SUNKEN, anchor=W)
        status_bar.pack(side=BOTTOM, fill=X)

        # Configuration des colonnes pour que l’affichage s’adapte
        for i in range(3):
            self.image_frame.columnconfigure(i, weight=1)
        self.image_frame.rowconfigure(0, weight=1)

    # Méthode qui charge les modèles de détection et de prédiction de visages
    def load_models(self):
        try:
            # Crée un détecteur de visage frontal basé sur dlib
            self.detector = dlib.get_frontal_face_detector()

            # Nom du fichier contenant le modèle des 68 points du visage
            model_path = "shape_predictor_68_face_landmarks.dat"

            # Vérifie si le fichier du modèle existe
            if not os.path.exists(model_path):
                # Lève une erreur si le fichier n’est pas trouvé
                raise FileNotFoundError("Dlib model file not found.")

            # Charge le prédicteur de formes (points clés du visage)
            self.predictor = dlib.shape_predictor(model_path)

        # Capture toute exception qui se produit
        except Exception as e:
            # Affiche une boîte d’erreur si le modèle ne se charge pas
            messagebox.showerror("Model Load Error", str(e))
            # Ferme la fenêtre principale si le modèle échoue
            self.root.destroy()

    # Méthode pour charger une image (source ou cible)
    def load_image(self, is_source=True):
        # Ouvre une boîte de dialogue pour choisir une image
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png")])

        # Si aucun fichier n’est sélectionné, on quitte la fonction
        if not path:
            return

        try:
            # Lit l’image choisie avec OpenCV
            image = cv2.imread(path)

            # Vérifie si l’image est valide
            if image is None:
                raise ValueError("Invalid image file")

            # Si l’image est une source (visage à copier)
            if is_source:
                # Stocke l’image source
                self.source_image = image
                # Sauvegarde son chemin
                self.source_path = path
                # Affiche l’image dans le label de l’interface
                self.show_image(image, self.source_label)
                # Change le texte du statut
                self.status_var.set(f"Source image loaded: {os.path.basename(path)}")

            # Sinon, l’image est une cible (visage à remplacer)
            else:
                self.target_image = image
                self.target_path = path
                self.show_image(image, self.target_label)
                self.status_var.set(f"Target image loaded: {os.path.basename(path)}")

            # Si les deux images sont chargées, on est prêt pour le swap
            if self.source_image is not None and self.target_image is not None:
                self.status_var.set("Ready to perform face swap")

        # En cas d’erreur, affiche une boîte d’erreur
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")

    # Raccourci pour charger une image source
    def load_source(self):
        self.load_image(is_source=True)

    # Raccourci pour charger une image cible
    def load_target(self):
        self.load_image(is_source=False)

    # Méthode pour capturer une photo depuis la webcam
    def capture_from_webcam(self, is_source=True):
        # Ouvre la webcam (index 0 = webcam par défaut)
        cap = cv2.VideoCapture(0)

        # Vérifie si la webcam s’ouvre correctement
        if not cap.isOpened():
            messagebox.showerror("Error", "Cannot open webcam.")
            return

        # Met à jour le statut pour indiquer les commandes clavier
        self.status_var.set("SPACE: Capture image | ESC: Exit")

        # Crée une fenêtre OpenCV
        cv2.namedWindow("Webcam", cv2.WINDOW_NORMAL)

        # Variable qui contiendra l’image capturée
        captured = None

        # Boucle infinie pour lire les frames de la webcam
        while True:
            # Lit une frame
            ret, frame = cap.read()

            # Si la lecture échoue, on sort
            if not ret:
                break

            # Affiche la frame dans la fenêtre
            cv2.imshow("Webcam", frame)

            # Attend une touche (1 ms)
            key = cv2.waitKey(1)

            # Si l’utilisateur appuie sur ESPACE → capture l’image
            if key == 32:
                captured = frame.copy()
                break
            # Si l’utilisateur appuie sur ESC → sort sans capturer
            elif key == 27:
                break

        # Libère la webcam
        cap.release()
        # Ferme la fenêtre OpenCV
        cv2.destroyAllWindows()

        # Si une image a été capturée
        if captured is not None:
            if is_source:
                self.source_image = captured
                self.source_path = "webcam_source.jpg"
                self.show_image(captured, self.source_label)
                self.status_var.set("Source image captured from webcam.")
            else:
                self.target_image = captured
                self.target_path = "webcam_target.jpg"
                self.show_image(captured, self.target_label)
                self.status_var.set("Target image captured from webcam.")

            # Si les deux images existent → prêt pour le swap
            if self.source_image is not None and self.target_image is not None:
                self.status_var.set("Ready to perform face swap.")

    # Méthode pour télécharger et utiliser un visage généré par IA
    def generate_ai_face(self):
        try:
            # Indique que le téléchargement commence
            self.status_var.set("Downloading AI face...")

            # Change le curseur en sablier
            self.root.config(cursor="watch")
            self.root.update()

            # URL du site qui génère un visage aléatoire
            url = "https://thispersondoesnotexist.com/"

            # Dossier où enregistrer les images téléchargées
            folder = os.path.join(os.getcwd(), "ai_faces")
            os.makedirs(folder, exist_ok=True)

            # Génère un nom unique pour l’image avec uuid
            filename = f"ai_face_{uuid.uuid4().hex[:8]}.jpg"
            filepath = os.path.join(folder, filename)

            # Télécharge l’image et l’enregistre
            urllib.request.urlretrieve(url, filepath)

            # Lit l’image téléchargée
            image = cv2.imread(filepath)

            # Vérifie que l’image est valide
            if image is None:
                raise ValueError("AI face could not be downloaded.")

            # Définit l’image source avec ce visage
            self.source_image = image
            self.source_path = filepath
            self.show_image(image, self.source_label)
            self.status_var.set("AI face loaded.")

            # Si une image cible existe déjà → prêt pour le swap
            if self.target_image is not None:
                self.status_var.set("Ready to perform face swap with AI face.")

        # En cas d’erreur pendant le téléchargement
        except Exception as e:
            messagebox.showerror("AI Face Error", str(e))
            self.status_var.set("AI face generation failed.")

        # Quoi qu’il arrive, réinitialise le curseur
        finally:
            self.root.config(cursor="")

    # Méthode qui récupère les points clés (landmarks) du visage
    def get_landmarks(self, image):
        # Convertit l’image en niveaux de gris
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Détecte les visages dans l’image
        faces = self.detector(gray)

        # Si aucun visage n’est trouvé → retourne None
        if len(faces) == 0:
            return None

        # Prend le premier visage détecté et calcule les 68 points
        shape = self.predictor(gray, faces[0])

        # Transforme les points en tableau NumPy (x, y)
        return np.array([(p.x, p.y) for p in shape.parts()], dtype=np.int32)

    # Méthode qui crée un masque basé sur les points du visage
    def create_mask(self, landmarks, shape):
        # Crée l’enveloppe convexe (contour du visage)
        hull = cv2.convexHull(landmarks)

        # Crée une image vide (masque noir)
        mask = np.zeros(shape[:2], dtype=np.float32)

        # Remplit la zone du visage en blanc (valeur = 1.0)
        cv2.fillConvexPoly(mask, hull, 1.0)

        # Floute le masque pour un mélange plus doux
        mask = cv2.GaussianBlur(mask, (15, 15), 0)

        # Ajoute une dimension supplémentaire (canal unique → masque)
        return mask[..., np.newaxis]

        # Méthode pour ajuster les couleurs de l'image source afin qu'elles correspondent à la cible
        def adjust_colors(self, source, target, mask):
            # Convertit les deux images en float32 pour éviter les pertes de précision
            source = source.astype(np.float32)
            target = target.astype(np.float32)

            # Calcule la moyenne des pixels dans la zone du visage source (définie par le masque)
            mean_src = np.sum(source * mask) / np.sum(mask)
            # Calcule la moyenne des pixels dans la zone du visage cible
            mean_tgt = np.sum(target * mask) / np.sum(mask)

            # Ajuste les couleurs de l’image source pour qu’elles soient proches de la cible
            source = source * (mean_tgt / mean_src)

            # Ramène les valeurs dans l’intervalle valide [0, 255] et convertit en uint8
            return np.clip(source, 0, 255).astype(np.uint8)

        # Méthode principale qui fait le face swap
        def swap_faces(self, src_img, tgt_img):
            # Récupère les points clés du visage source
            src_landmarks = self.get_landmarks(src_img)
            # Récupère les points clés du visage cible
            tgt_landmarks = self.get_landmarks(tgt_img)

            # Si un des deux visages n'est pas détecté, on annule
            if src_landmarks is None or tgt_landmarks is None:
                return None

            # Calcule la transformation affine entre les points source et cible
            M, _ = cv2.findHomography(src_landmarks, tgt_landmarks, cv2.RANSAC, 5.0)

            # Transforme l'image source pour l’aligner sur la cible
            warped_src = cv2.warpPerspective(src_img, M, (tgt_img.shape[1], tgt_img.shape[0]))

            # Transforme le masque du visage source
            mask_src = self.create_mask(src_landmarks, src_img.shape)
            warped_mask = cv2.warpPerspective(mask_src, M, (tgt_img.shape[1], tgt_img.shape[0]))

            # Ajuste les couleurs pour mieux se fondre dans la cible
            warped_src = self.adjust_colors(warped_src, tgt_img, warped_mask)

            # Mélange les deux images avec le masque
            swapped = tgt_img * (1 - warped_mask) + warped_src * warped_mask

            # Retourne l’image finale (convertie en uint8)
            return swapped.astype(np.uint8)

        # Met à jour l'image affichée avec le face swap
        def update_face_swap(self):
            # Si une des images (source ou cible) n’est pas dispo, on arrête
            if self.source_image is None or self.target_image is None:
                messagebox.showwarning("Warning", "Please load both source and target images.")
                return

            # Applique l’algorithme de face swap
            result = self.swap_faces(self.source_image, self.target_image)

            # Si le swap échoue (pas de visage trouvé)
            if result is None:
                messagebox.showerror("Error", "Face swap failed. Could not detect faces.")
                return

            # Affiche l’image résultante dans le label prévu
            self.show_image(result, self.result_label)
            # Sauvegarde aussi dans une variable pour l’export
            self.result_image = result
            # Met à jour le statut
            self.status_var.set("Face swap completed.")

        # Affiche une image donnée dans un label tkinter
        def show_image(self, image, label):
            # Convertit l’image OpenCV (BGR) en RGB (tkinter utilise PIL)
            img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Transforme en Image PIL
            img_pil = Image.fromarray(img_rgb)

            # Redimensionne l’image pour qu’elle tienne dans 250x250
            img_pil = img_pil.resize((250, 250), Image.Resampling.LANCZOS)

            # Convertit en ImageTk (format utilisable par tkinter)
            img_tk = ImageTk.PhotoImage(img_pil)

            # Met l’image dans le label
            label.config(image=img_tk)
            # Garde une référence pour éviter que l’image disparaisse
            label.image = img_tk

        # Sauvegarde l’image résultat sur le disque
        def save_result(self):
            # Si aucune image résultat n’existe, on arrête
            if not hasattr(self, "result_image") or self.result_image is None:
                messagebox.showwarning("Warning", "No result to save.")
                return

            # Ouvre une boîte de dialogue pour choisir l’emplacement
            path = filedialog.asksaveasfilename(defaultextension=".jpg",
                                                filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")])

            # Si l’utilisateur annule, on arrête
            if not path:
                return

            # Sauvegarde l’image résultat
            cv2.imwrite(path, self.result_image)
            # Met à jour le statut
            self.status_var.set(f"Result saved: {os.path.basename(path)}")

        # Active le mode face swap en direct via la webcam
        def live_face_swap(self):
            # Ouvre la webcam
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                messagebox.showerror("Error", "Cannot open webcam.")
                return

            # Boucle pour lire les images de la webcam
            while True:
                # Capture une frame
                ret, frame = cap.read()
                if not ret:
                    break

                # Si une image source est définie
                if self.source_image is not None:
                    # Applique le swap sur la frame en direct
                    swapped = self.swap_faces(self.source_image, frame)

                    # Si le swap marche, affiche le résultat
                    if swapped is not None:
                        cv2.imshow("Live Face Swap", swapped)
                    # Sinon, affiche l’image originale
                    else:
                        cv2.imshow("Live Face Swap", frame)
                # Si pas d’image source, on affiche la webcam normale
                else:
                    cv2.imshow("Live Face Swap", frame)

                # Quitte si l’utilisateur appuie sur ESC
                if cv2.waitKey(1) == 27:
                    break

            # Libère la webcam et ferme la fenêtre
            cap.release()
            cv2.destroyAllWindows()

    # Si ce fichier est exécuté directement (et pas importé)
    if __name__ == "__main__":
        # Crée une fenêtre Tkinter
        root = tk.Tk()
        # Crée l’application FaceSwapApp avec cette fenêtre
        app = FaceSwapApp(root)
        # Lance la boucle principale de Tkinter
        root.mainloop()

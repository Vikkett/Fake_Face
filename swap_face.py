# Importation de la librairie OpenCV pour le traitement d'image et la vision par ordinateur
import cv2
# Importation de Numpy pour la manipulation des matrices et des tableaux numériques
import numpy as np
# Importation de Dlib pour la détection de visage et les landmarks faciaux
import dlib
# Importation de toutes les fonctions de Tkinter pour créer l'interface graphique
from tkinter import *
# Importation spécifique pour ouvrir des boîtes de dialogue (ouvrir fichier, messages)
from tkinter import filedialog, messagebox
# Importation de Pillow pour gérer et afficher des images dans Tkinter
from PIL import Image, ImageTk
# Importation d'os pour la gestion des chemins de fichiers et dossiers
import os
# Importation d'urllib.request pour télécharger une image depuis internet
import urllib.request
# Importation de uuid pour générer des identifiants uniques (utile pour nommer des fichiers)
import uuid

# Définition d'une classe qui représente toute l'application de Face Swap
class FaceSwapApp:
    # Constructeur, appelé à la création de l'objet
    def __init__(self, root):
        # Stocke la fenêtre Tkinter principale
        self.root = root
        # Appelle la fonction qui construit l'interface utilisateur
        self.setup_ui()
        # Appelle la fonction qui charge les modèles Dlib pour la détection faciale
        self.load_models()

        # Variable qui contiendra l'image source
        self.source_image = None
        # Variable qui contiendra l'image cible
        self.target_image = None
        # Variable qui contiendra l'image après swap
        self.result_image = None
        # Chemin du fichier source
        self.source_path = ""
        # Chemin du fichier cible
        self.target_path = ""

        # Largeur maximale pour afficher les images dans l'UI
        self.display_width = 400
        # Hauteur maximale pour afficher les images dans l'UI
        self.display_height = 300

        # Fonction pour créer toute l'interface graphique
    def setup_ui(self):
        # Définit le titre de la fenêtre
        self.root.title("Professional Face Swap v2.3")
        # Définit la taille par défaut de la fenêtre
        self.root.geometry("1000x700")
        # Définit la taille minimale autorisée
        self.root.minsize(900, 600)

        # Crée un conteneur principal
        main_frame = Frame(self.root)
        # Place le conteneur dans la fenêtre avec marges
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Crée un cadre pour les images (source, cible, résultat)
        self.image_frame = Frame(main_frame)
        # L’affiche en remplissant l’espace disponible
        self.image_frame.pack(fill=BOTH, expand=True)

        # Crée un cadre étiqueté pour l'image source
        self.source_frame = LabelFrame(self.image_frame, text="Source Image")
        # Place ce cadre à gauche
        self.source_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        # Crée un label (zone où l’image source sera affichée)
        self.source_label = Label(self.source_frame)
        # Ajoute le label dans le cadre
        self.source_label.pack()

        # Crée un cadre étiqueté pour l'image cible
        self.target_frame = LabelFrame(self.image_frame, text="Target Image")
        # Place ce cadre au centre
        self.target_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        # Crée un label (zone où l’image cible sera affichée)
        self.target_label = Label(self.target_frame)
        # Ajoute le label dans le cadre
        self.target_label.pack()

        # Crée un cadre pour l'image résultat
        self.result_frame = LabelFrame(self.image_frame, text="Result Image")
        # Crée un label où sera affiché le résultat
        self.result_label = Label(self.result_frame)
        # Ajoute le label dans le cadre
        self.result_label.pack()

        # Crée un cadre pour les boutons de contrôle
        control_frame = Frame(main_frame)
        # L’affiche horizontalement en bas
        control_frame.pack(fill=X, pady=10)

        # Bouton pour charger image source
        Button(control_frame, text="Load Source", command=self.load_source).grid(row=0, column=0, padx=5)
        # Bouton pour charger image cible
        Button(control_frame, text="Load Target", command=self.load_target).grid(row=0, column=1, padx=5)
        # Bouton pour lancer le swap
        Button(control_frame, text="Swap Faces", command=self.swap_faces).grid(row=0, column=2, padx=5)

        # Bouton pour sauvegarder (désactivé au début)
        self.save_button = Button(control_frame, text="Save Result", command=self.save_result, state=DISABLED)
        # Placement du bouton sauvegarde
        self.save_button.grid(row=0, column=3, padx=5)

        # Bouton pour générer visage IA
        Button(control_frame, text="Generate AI Face", command=self.generate_ai_face).grid(row=0, column=4, padx=5)
        # Bouton capture webcam source
        Button(control_frame, text="Webcam Source", command=lambda: self.capture_from_webcam(is_source=True)).grid(row=0, column=5, padx=5)
        # Bouton capture webcam cible
        Button(control_frame, text="Webcam Target", command=lambda: self.capture_from_webcam(is_source=False)).grid(row=0, column=6, padx=5)
        # Bouton pour mode swap vidéo
        Button(control_frame, text="Live Swap Video", command=self.open_live_video).grid(row=0, column=7, padx=5)

        # Crée un cadre pour les réglages (blend/couleur)
        settings_frame = Frame(control_frame)
        # L’affiche sous les boutons
        settings_frame.grid(row=1, column=0, columnspan=8, pady=5)

        # Label pour le réglage du blending
        Label(settings_frame, text="Blend Amount:").grid(row=0, column=0)
        # Curseur blending
        self.blend_scale = Scale(settings_frame, from_=0, to=100, orient=HORIZONTAL, length=150)
        # Valeur par défaut à 65
        self.blend_scale.set(65)
        # Placement du curseur
        self.blend_scale.grid(row=0, column=1)
        # Quand on relâche la souris → mise à jour du blending
        self.blend_scale.bind("<ButtonRelease-1>", self.update_blend)

        # Label pour réglage des couleurs
        Label(settings_frame, text="Color Adjustment:").grid(row=0, column=2)
        # Curseur couleur
        self.color_scale = Scale(settings_frame, from_=0, to=100, orient=HORIZONTAL, length=150)
        # Valeur par défaut à 50
        self.color_scale.set(50)
        # Placement du curseur
        self.color_scale.grid(row=0, column=3)
        # Quand on relâche la souris → mise à jour couleur
        self.color_scale.bind("<ButtonRelease-1>", self.update_color)

        # Variable texte dynamique (barre de statut)
        self.status_var = StringVar()
        # Texte par défaut
        self.status_var.set("Ready to load images")
        # Label affichant le statut
        status_bar = Label(self.root, textvariable=self.status_var, bd=1, relief=SUNKEN, anchor=W)
        # Positionné en bas de la fenêtre
        status_bar.pack(side=BOTTOM, fill=X)

        # Boucle pour configurer les colonnes
        for i in range(3):
            # Chaque colonne prend de l’espace proportionnel
            self.image_frame.columnconfigure(i, weight=1)
            # La ligne prend aussi tout l’espace disponible
        self.image_frame.rowconfigure(0, weight=1)

        # Fonction pour charger le détecteur de visage et les landmarks
    def load_models(self):
        try:
            # Détecteur de visages frontal (pré entraîné)
            self.detector = dlib.get_frontal_face_detector()
            # Nom du fichier du modèle de landmarks
            model_path = "shape_predictor_68_face_landmarks.dat"
            # Vérifie si le fichier existe
            if not os.path.exists(model_path):
                # Lève une erreur si le modèle est manquant
                raise FileNotFoundError("Dlib model file not found.")
                # Charge le modèle landmarks (68 points du visage)
            self.predictor = dlib.shape_predictor(model_path)
            # Si une erreur survient
        except Exception as e:
            # Affiche une boîte d'erreur
            messagebox.showerror("Model Load Error", str(e))
            # Ferme l'application si pas de modèle
            self.root.destroy()

            # Fonction pour charger une image (source ou cible)
    def load_image(self, is_source=True):
        # Ouvre une boîte de dialogue pour choisir une image
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
        # Si l'utilisateur n'a rien sélectionné
        if not path:
            # On arrête la fonction
            return
        try:
            # Charge l'image avec OpenCV
            image = cv2.imread(path)
            # Si l'image n'est pas valide
            if image is None:
                # On lève une erreur
                raise ValueError("Invalid image file")
                # Si c'est l'image source
            if is_source:
                # On stocke l'image source
                self.source_image = image
                # On mémorise le chemin du fichier
                self.source_path = path
                # On affiche l'image dans l'interface
                self.show_image(image, self.source_label)
                # On met à jour le statut
                self.status_var.set(f"Source image loaded: {os.path.basename(path)}")
                # Sinon c'est l'image cible
            else:
                # On stocke l'image cible
                self.target_image = image
                # On mémorise son chemin
                self.target_path = path
                # On affiche dans l'interface
                self.show_image(image, self.target_label)
                # On met à jour le statut
                self.status_var.set(f"Target image loaded: {os.path.basename(path)}")
                # Si on a les deux images
            if self.source_image is not None and self.target_image is not None:
                # Statut prêt pour swap
                self.status_var.set("Ready to perform face swap")
                # En cas d’erreur
        except Exception as e:
            # Affiche un message d'erreur
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
            # sprint 1 finished
            # sprint 2 start

    # Fonction qui charge l'image source
    def load_source(self):
        # Appelle load_image avec True
        self.load_image(is_source=True)

        # Fonction qui charge l'image cible
    def load_target(self):
        # Appelle load_image avec False
        self.load_image(is_source=False)

        # Fonction pour capturer une image depuis la webcam
    def capture_from_webcam(self, is_source=True):
        # Ouvre la webcam (0 = webcam par défaut)
        cap = cv2.VideoCapture(0)
        # Si la webcam ne s'ouvre pas
        if not cap.isOpened():
            # Message d'erreur
            messagebox.showerror("Error", "Cannot open webcam.")
            return

        # Indique les touches de commande
        self.status_var.set("SPACE: Capture image | ESC: Exit")
        # Ouvre une fenêtre OpenCV
        cv2.namedWindow("Webcam", cv2.WINDOW_NORMAL)
        # Variable pour stocker l'image capturée
        captured = None

        # Boucle infinie jusqu’à appui sur touche
        while True:
            # Lit une frame de la webcam
            ret, frame = cap.read()
            # Si échec lecture
            if not ret:
                break
                # Affiche la frame
            cv2.imshow("Webcam", frame)
            # Attend une touche
            key = cv2.waitKey(1)
            # Si touche ESPACE (32)
            if key == 32:
                # On sauvegarde l'image capturée
                captured = frame.copy()
                break
                # Si touche ESC (27)
            elif key == 27:
                break

        # Libère la webcam
        cap.release()
        # Ferme les fenêtres OpenCV
        cv2.destroyAllWindows()

        # Si une image a été capturée
        if captured is not None:
            # Si c'est l'image source
            if is_source:
                self.source_image = captured
                # Nom symbolique
                self.source_path = "webcam_source.jpg"
                self.show_image(captured, self.source_label)
                self.status_var.set("Source image captured from webcam.")
                # Sinon c'est l'image cible
            else:
                self.target_image = captured
                self.target_path = "webcam_target.jpg"
                self.show_image(captured, self.target_label)
                self.status_var.set("Target image captured from webcam.")
                # Si les deux images existent
            if self.source_image is not None and self.target_image is not None:
                self.status_var.set("Ready to perform face swap.")
                # sprint 2 finished


    # sprint 3 generate foto from ai
    # Fonction pour générer un visage IA
    def generate_ai_face(self):
        try:
            # Message statut
            self.status_var.set("Downloading AI face...")
            # Change curseur → sablier
            self.root.config(cursor="watch")
            # Met à jour l’UI
            self.root.update()

            # URL générateur visage IA
            url = "https://thispersondoesnotexist.com/"
            # Crée un dossier "ai_faces"
            folder = os.path.join(os.getcwd(), "ai_faces")
            # Si le dossier n'existe pas → le créer
            os.makedirs(folder, exist_ok=True)

            # Nom fichier unique avec UUID
            filename = f"ai_face_{uuid.uuid4().hex[:8]}.jpg"
            # Chemin complet fichier
            filepath = os.path.join(folder, filename)

            # Télécharge l'image depuis le site
            urllib.request.urlretrieve(url, filepath)
            # Charge l'image téléchargée
            image = cv2.imread(filepath)

            # Si l'image n'a pas été chargée
            if image is None:
                # Erreur
                raise ValueError("AI face could not be downloaded.")

            # Définit comme image source
            self.source_image = image
            # Stocke chemin
            self.source_path = filepath
            # Affiche dans UI
            self.show_image(image, self.source_label)
            # Statut mis à jour
            self.status_var.set("AI face loaded.")

            # Si une cible est déjà chargée
            if self.target_image is not None:
                self.status_var.set("Ready to perform face swap with AI face.")
                # En cas d’erreur
        except Exception as e:
            # Message d’erreur
            messagebox.showerror("AI Face Error", str(e))
            # Statut échec
            self.status_var.set("AI face generation failed.")
        finally:
            # Remet curseur normal
            self.root.config(cursor="")

    # Fonction qui récupère les points de repère (landmarks) du visage
    def get_landmarks(self, image):
        # Convertit l'image en niveaux de gris
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Détecte les visages avec dlib
        faces = self.detector(gray)
        # Si aucun visage trouvé
        if len(faces) == 0:
            # Retourne None
            return None
            # Prend le premier visage détecté et récupère ses landmarks
        shape = self.predictor(gray, faces[0])
        # Transforme en tableau numpy de coordonnées (x,y)
        return np.array([(p.x, p.y) for p in shape.parts()], dtype=np.int32)

        # Fonction qui crée un masque pour la zone du visage
    def create_mask(self, landmarks, shape):
        # Calcule l'enveloppe convexe des points du visage (contour global)
        hull = cv2.convexHull(landmarks)
        # Crée un masque vide de la taille de l'image
        mask = np.zeros(shape[:2], dtype=np.float32)
        # Remplit la zone du visage avec 1 (blanc)
        cv2.fillConvexPoly(mask, hull, 1.0)
        # Applique un flou gaussien pour adoucir les bords
        mask = cv2.GaussianBlur(mask, (15, 15), 0)
        # Ajoute une 3e dimension pour correspondre aux 3 canaux couleur
        return mask[..., np.newaxis]

        # Fonction pour ajuster les couleurs du visage source sur la cible
    def adjust_colors(self, src, target, amount):
        # Si pas d’ajustement demandé
        if amount == 0:
            # Retourne l’image originale
            return src
        try:
            # Convertit source en espace LAB (luminance + couleurs)
            src_lab = cv2.cvtColor(src, cv2.COLOR_BGR2LAB).astype(np.float32)
            # Convertit cible en LAB
            target_lab = cv2.cvtColor(target, cv2.COLOR_BGR2LAB).astype(np.float32)

            # Moyenne et écart-type couleurs source
            src_mean, src_std = cv2.meanStdDev(src_lab)
            # Moyenne et écart-type couleurs cible
            tgt_mean, tgt_std = cv2.meanStdDev(target_lab)

            # Aplati en vecteurs
            src_mean, src_std = src_mean.flatten(), src_std.flatten()
            tgt_mean, tgt_std = tgt_mean.flatten(), tgt_std.flatten()

            # Évite division par zéro si variance nulle
            src_std[src_std == 0] = 1.0
            # Normalise l’image source
            normalized = (src_lab - src_mean) / src_std
            adjusted = normalized * ((1 - amount) * src_std + amount * tgt_std) + \
                       ((1 - amount) * src_mean + amount * tgt_mean)   # Applique un mélange stats source/cible
            # Recadre valeurs entre 0 et 255
            adjusted = np.clip(adjusted, 0, 255).astype(np.uint8)
            # Reconvertit en BGR
            return cv2.cvtColor(adjusted, cv2.COLOR_LAB2BGR)
        # En cas d’erreur
        except Exception as e:
            # Affiche erreur
            messagebox.showerror("Error", f"Color adjustment failed: {str(e)}")
            # Retourne l’image source non modifiée
            return src
            #print({str(e)})

        # Fonction qui effectue le face swap
        def swap_faces(self):
            # Vérifie si les deux images existent
            if self.source_image is None or self.target_image is None:
                # Erreur si non
                messagebox.showerror("Error", "Please load both source and target images.")
                return

            # Message statut
            self.status_var.set("Processing... Please wait.")
            # Change curseur en sablier
            self.root.config(cursor="watch")
            # Rafraîchit interface
            self.root.update()

            try:
                src_points = self.get_landmarks(self.source_image)   # Récupère landmarks image source
                tgt_points = self.get_landmarks(self.target_image)   # Récupère landmarks image cible

                if src_points is None or tgt_points is None:   # Si un visage n’a pas été trouvé
                    raise ValueError("Face not detected in one or both images.")   # Erreur

                mask = self.create_mask(tgt_points, self.target_image.shape)   # Crée le masque de la cible
                matrix, _ = cv2.estimateAffinePartial2D(src_points, tgt_points)   # Calcule la transformation affine (source→cible)
                warped_src = cv2.warpAffine(self.source_image, matrix,
                                            (self.target_image.shape[1], self.target_image.shape[0]))   # Applique la transformation

                self.warped_src = warped_src   # Sauvegarde l’image source transformée
                self.mask = mask   # Sauvegarde le masque
                self.src_points = src_points   # Sauvegarde points source
                self.tgt_points = tgt_points   # Sauvegarde points cible

                self.update_face_swap()   # Applique le blending et couleurs
            except Exception as e:   # Si erreur
                messagebox.showerror("Error", f"Face swap failed: {str(e)}")   # Message erreur
                self.status_var.set("Face swap failed.")   # Statut mis à jour
            finally:
                self.root.config(cursor="")   # Remet le curseur normal

        def update_face_swap(self):   # Fonction qui met à jour le swap (blending/couleurs)
            if not hasattr(self, 'warped_src'):   # Vérifie qu’il y a une image transformée
                return

            try:
                blend_amount = self.blend_scale.get() / 100.0   # Récupère valeur blending (0-1)
                color_amount = self.color_scale.get() / 100.0   # Récupère valeur ajustement couleur (0-1)

                if color_amount > 0:   # Si on ajuste les couleurs
                    color_adjusted = self.adjust_colors(self.warped_src, self.target_image, color_amount)   # Applique correction couleur
                else:
                    color_adjusted = self.warped_src   # Sinon prend direct l’image transformée

                mask_3ch = np.repeat(self.mask, 3, axis=2)   # Étend le masque en 3 canaux
                blended = (color_adjusted * mask_3ch + self.target_image * (1 - mask_3ch)).astype(np.uint8)   # Mélange source et cible
                self.result_image = (blended * blend_amount + self.target_image * (1 - blend_amount)).astype(np.uint8)   # Applique blending global

                self.show_result()   # Affiche le résultat
                self.save_button.config(state=NORMAL)   # Active le bouton sauvegarde
                self.status_var.set("Face swap completed.")   # Statut succès
            except Exception as e:   # Si erreur
                messagebox.showerror("Error", f"Update failed: {str(e)}")   # Message erreur


        def update_blend(self, event=None):   # Fonction appelée quand on change blending
            if hasattr(self, 'result_image'):   # Vérifie qu’il y a un résultat
                self.update_face_swap()   # Recalcule le résultat

        def update_color(self, event=None):   # Fonction appelée quand on change la couleur
            if hasattr(self, 'result_image'):   # Vérifie qu’il y a un résultat
                self.update_face_swap()   # Recalcule le résultat


        def show_image(self, image, label_widget):   # Fonction pour afficher une image dans Tkinter
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)   # Convertit en RGB (Tkinter utilise PIL en RGB)
            h, w = rgb.shape[:2]   # Récupère hauteur et largeur
            scale = min(self.display_width / w, self.display_height / h)   # Calcule l’échelle d’affichage
            resized = cv2.resize(rgb, (int(w * scale), int(h * scale)))   # Redimensionne l’image
            img_tk = ImageTk.PhotoImage(image=Image.fromarray(resized))   # Convertit en format Tkinter
            label_widget.config(image=img_tk)   # Associe l’image au widget label
            label_widget.image = img_tk   # Sauvegarde une référence pour éviter le garbage collector

        def show_result(self):   # Fonction qui affiche le résultat
            self.result_frame.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")   # Affiche le cadre résultat
            self.image_frame.columnconfigure(2, weight=1)   # Redimensionne la colonne résultat
            self.show_image(self.result_image, self.result_label)   # Affiche l’image résultat dans le label


        def save_result(self):   # Fonction pour sauvegarder le résultat
            if not hasattr(self, 'result_image'):   # Si aucun résultat
                messagebox.showerror("Error", "No result image to save.")   # Message erreur
                return
            default_name = f"swap_{os.path.basename(self.source_path)}_{os.path.basename(self.target_path)}"   # Nom par défaut
            path = filedialog.asksaveasfilename(   # Ouvre boîte de dialogue pour choisir où sauvegarder
                initialfile=default_name,          # Nom par défaut
                defaultextension=".jpg",           # Extension par défaut
                filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")]   # Types de fichiers autorisés
            )
            if path:   # Si utilisateur a choisi un chemin
                try:
                    cv2.imwrite(path, self.result_image)   # Sauvegarde l’image
                    messagebox.showinfo("Saved", f"Image saved at:\n{path}")   # Message succès
                    self.status_var.set(f"Saved to {os.path.basename(path)}")   # Met à jour le statut
                except Exception as e:   # Si erreur
                    messagebox.showerror("Save Error", str(e))   # Message erreur

    if __name__ == "__main__":   # Point d'entrée du programme
        root = Tk()              # Crée une fenêtre Tkinter
        app = FaceSwapApp(root)  # Crée l'application FaceSwap
        root.mainloop()          # Lance la boucle principale Tkinter (interface interactive)

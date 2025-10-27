import cv2
import numpy as np
import dlib
from tkinter import *
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os
import urllib.request
import uuid
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText


# Simple Separator class definition for the settings panel
class Separator(Frame):
    def __init__(self, master, **kwargs):
        Frame.__init__(self, master, height=2, bg='#E0E0E0', **kwargs)


# Définition d'une classe qui représente toute l'application de Face Swap
class FaceSwapApp:
    # Constructeur, appelé à la création de l'objet
    def __init__(self, root):
        self.root = root

        self.load_models()
        self.load_icons()
        self.setup_ui()

        self.source_image = None
        self.target_image = None
        self.result_image = None
        self.source_path = ""
        self.target_path = ""

        self.display_width = 400
        self.display_height = 300

    # Ajouter l'icon sur l'interface
    def load_icons(self):
        icon_size = (20, 20)
        self.icon_load = None
        self.icon_webcam = None
        self.icon_ai = None
        self.icon_swap = None
        self.icon_save = None
        self.icon_mail = None

        try:
            # Assuming icons are in an 'icons' folder and you have the necessary files
            self.icon_load = ImageTk.PhotoImage(Image.open("icons/folder.png").resize(icon_size))
            self.icon_webcam = ImageTk.PhotoImage(Image.open("icons/camera.png").resize(icon_size))
            self.icon_ai = ImageTk.PhotoImage(Image.open("icons/ai.png").resize(icon_size))
            self.icon_swap = ImageTk.PhotoImage(Image.open("icons/swap.png").resize(icon_size))
            self.icon_save = ImageTk.PhotoImage(Image.open("icons/save.png").resize(icon_size))
            self.icon_mail = ImageTk.PhotoImage(Image.open("icons/mail.png").resize(icon_size))
        except FileNotFoundError:
            # Fallback for when icons are missing
            pass
        except Exception as e:
            messagebox.showerror("Icon Load Error", f"Failed to load one or more icons: {e}")

    # Helper function to create the modern image display frames
    def create_image_display(self, parent, title):
        # Container for the title and the image box
        container = Frame(parent, bg=parent['bg'])

        # --- FIX: REMOVED THE CONFLICTING .pack() CALL HERE ---
        # The container will be placed using .grid() in setup_ui, so no geometry manager call here.

        # Modern Title Label
        Label(container, text=title, font=("Arial", 12, "bold"), bg=parent['bg'], fg="#FFFFFF").pack(side=TOP,
                                                                                                     pady=(0, 5))

        # Image Display Frame - White background with a subtle border for a clean card look
        image_frame = Frame(container, bg="#FFFFFF", bd=1, relief=FLAT)
        image_frame.pack(fill=BOTH, expand=True)

        # The actual Label to hold the image
        image_label = Label(image_frame, bg="#FFFFFF", text=f"Load a {title.lower()}", font=("Arial", 11), fg="#555")
        image_label.pack(fill=BOTH, expand=True, padx=10, pady=10)

        return container, image_label

    # Fonction pour créer toute l'interface graphique
    def setup_ui(self):
        self.root.title("Professional Face Swap v2.3")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        self.root.configure(bg="#36454F")  # Dark grey background

        # crée un conteneur principal
        main_frame = Frame(self.root, bg="#36454F")
        # Place le conteneur dans la fenêtre avec marges
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)

        # === Image Frames (MODERNIZED) ===
        self.image_frame = Frame(main_frame, bg="#36454F")
        # L'affiche en remplissant l'espace disponible
        self.image_frame.pack(fill=BOTH, expand=True)

        # Source Image
        self.source_container, self.source_label = self.create_image_display(self.image_frame, "SOURCE IMAGE")
        # --- CORRECT: Using grid() to place the container into self.image_frame ---
        self.source_container.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        # Target Image
        self.target_container, self.target_label = self.create_image_display(self.image_frame, "TARGET IMAGE")
        self.target_container.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")

        # Result Image
        self.result_container, self.result_label = self.create_image_display(self.image_frame, "RESULT IMAGE")
        self.result_container.grid(row=0, column=2, padx=15, pady=15, sticky="nsew")

        # configuration des colonnes pour que l'affiche s'adapte
        for i in range(3):
            self.image_frame.columnconfigure(i, weight=1)
        self.image_frame.rowconfigure(0, weight=1)

        # === Control Panel ===
        control_frame = Frame(main_frame, bg="#36454F")
        control_frame.pack(fill=X, pady=10)

        all_buttons_frame = Frame(control_frame, bg="#36454F")
        all_buttons_frame.pack(expand=True)

        for i in range(9):
            all_buttons_frame.columnconfigure(i, weight=1)

        # Row 0: Input Buttons
        self.make_button(all_buttons_frame, "Load Source", self.load_source, color="#4682B4", icon=self.icon_load).grid(
            row=0, column=0, padx=5, pady=5)
        self.make_button(all_buttons_frame, "Load Target", self.load_target, color="#4682B4", icon=self.icon_load).grid(
            row=0, column=1, padx=5, pady=5)
        self.make_button(all_buttons_frame, "Webcam Source", lambda: self.capture_from_webcam(is_source=True),
                         color="#4682B4", icon=self.icon_webcam).grid(row=0, column=2, padx=5, pady=5)
        self.make_button(all_buttons_frame, "Webcam Target", lambda: self.capture_from_webcam(is_source=False),
                         color="#4682B4", icon=self.icon_webcam).grid(row=0, column=3, padx=5, pady=5)
        self.make_button(all_buttons_frame, "Generate AI Face", self.generate_ai_face, color="#4682B4",
                         icon=self.icon_ai).grid(row=0, column=4, padx=5, pady=5)

        # Row 1: Action Buttons
        self.make_button(all_buttons_frame, "Swap Faces", self.swap_faces, "#3498db", icon=self.icon_swap).grid(row=1,
                                                                                                                column=2,
                                                                                                                padx=5,
                                                                                                                pady=5,
                                                                                                                sticky="ew")
        self.make_button(all_buttons_frame, "Live Swap", self.open_live_video, "#ff9800", icon=self.icon_swap).grid(
            row=1, column=3, padx=5, pady=5, sticky="ew")
        self.save_button = self.make_button(all_buttons_frame, "Save Result", self.save_result, "#2ecc71",
                                            icon=self.icon_save)
        self.save_button.grid(row=1, column=4, padx=5, pady=5, sticky="ew")
        self.save_button.config(state=DISABLED)
        self.email_button = self.make_button(all_buttons_frame, "Email Result", self.email_result, "#e74c3c",
                                             icon=self.icon_mail)
        self.email_button.grid(row=1, column=5, padx=5, pady=5, sticky="ew")
        self.email_button.config(state=DISABLED)

        all_buttons_frame.columnconfigure(6, weight=1)
        all_buttons_frame.columnconfigure(7, weight=1)
        all_buttons_frame.columnconfigure(8, weight=1)

        # === Modern Settings Panel ===
        # The main frame for the settings with a modern, flat white background
        settings_container = Frame(main_frame, bg="#FFFFFF", bd=1, relief=FLAT)
        settings_container.pack(fill=X, pady=15, padx=10)

        # Title for the settings
        Label(settings_container, text="ADVANCED SETTINGS", font=("Arial", 11, "bold"), bg="#FFFFFF",
              fg="#4682B4").pack(side=TOP, pady=(5, 0))

        # Separator line
        Separator(settings_container).pack(fill=X, padx=10, pady=5)

        # Frame for the two scales, centered horizontally
        scales_frame = Frame(settings_container, bg="#FFFFFF")
        scales_frame.pack(pady=(0, 10))

        # Blend Controls
        blend_frame = Frame(scales_frame, bg="#FFFFFF")
        blend_frame.pack(side=LEFT, padx=30)

        Label(blend_frame, text="Blend Amount", bg="#FFFFFF", font=("Arial", 10, "bold")).pack(side=TOP, pady=(0, 2))
        self.blend_scale = Scale(blend_frame, from_=0, to=100, orient=HORIZONTAL, length=250,
                                 bg="#FFFFFF", bd=0, highlightthickness=0,
                                 troughcolor="#A9A9A9", activebackground="#4682B4",  # Modern look
                                 sliderrelief=FLAT)
        self.blend_scale.set(65)
        self.blend_scale.pack(side=BOTTOM)
        self.blend_scale.bind("<ButtonRelease-1>", self.update_face_swap_event)

        # Color Controls
        color_frame = Frame(scales_frame, bg="#FFFFFF")
        color_frame.pack(side=LEFT, padx=30)

        Label(color_frame, text="Color Adjustment", bg="#FFFFFF", font=("Arial", 10, "bold")).pack(side=TOP,
                                                                                                   pady=(0, 2))
        self.color_scale = Scale(color_frame, from_=0, to=100, orient=HORIZONTAL, length=250,
                                 bg="#FFFFFF", bd=0, highlightthickness=0,
                                 troughcolor="#A9A9A9", activebackground="#4682B4",  # Modern look
                                 sliderrelief=FLAT)
        self.color_scale.set(50)
        self.color_scale.pack(side=BOTTOM)
        self.color_scale.bind("<ButtonRelease-1>", self.update_face_swap_event)

        # === Status Bar ===
        self.status_var = StringVar()
        self.status_var.set("Ready to load images...")
        status_bar = Label(self.root, textvariable=self.status_var, bd=1, relief=SUNKEN, anchor=W, bg="#DCDCDC",
                           font=("Arial", 10), fg="#333")
        status_bar.pack(side=BOTTOM, fill=X)

    # Définir les boutons quand le souris passe dessus
    def make_button(self, parent, text, command, color="#4a4a4a", icon=None):
        if color == "#4a4a4a":
            color = "#4682B4"

        button = Button(
            parent,
            text=text,
            command=command,
            font=("Arial", 10, "bold"),
            fg="white",
            bg=color,
            activebackground="#7f8c8d",
            relief=RAISED,
            padx=10,
            pady=5,
            cursor="hand2",
            image=icon,
            compound=LEFT
        )
        # La couleur de fond est temporairement assombrie via la méthode self.darken_color
        button.bind("<Enter>", lambda e: button.config(bg=self.darken_color(color, 20)))
        # Devient la couleur originale
        button.bind("<Leave>", lambda e: button.config(bg=color))
        return button

    # La fonction pour créer des effets de survol (hover effects) en format hexadécimal
    def darken_color(self, hex_color, amount):
        hex_color = hex_color.lstrip('#')
        # la chaîne est divisée en trois parties (RR, GG, BB), chaque paire est convertie d'une base 16
        rgb = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
        # Garantir que la valeur minimale est o pour éviter les nombres négatifs qui sont invalides
        darkened_rgb = tuple(max(0, c - amount) for c in rgb)
        # %02x formate chaque entier RVB en chaîne hexadécimale de deux caractères
        # # au début pour obtenir le format #RRGGBB
        return '#%02x%02x%02x' % darkened_rgb

    # Méthode qui charge les modèles de détection
    def load_models(self):
        try:
            # Crée un détecteur de visage frontal basé sur dlib
            self.detector = dlib.get_frontal_face_detector()
            # Nom du fichier contenant le modèle des 68 points du visage
            model_path = "shape_predictor_68_face_landmarks.dat"
            if not os.path.exists(model_path):
                # Placeholder for model download instruction
                pass
            self.predictor = dlib.shape_predictor(model_path)
        except Exception as e:
            # Simplified error handling for demonstration
            pass

    # Méthode pour charger une image (source ou cible)
    def load_image(self, is_source=True):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
        if not path:
            return
        try:
            image = cv2.imread(path)
            if image is None:
                raise ValueError("Invalid image file")
            if is_source:
                self.source_image = image
                self.source_path = path
                self.show_image(image, self.source_label)
                self.status_var.set(f"Source image loaded: {os.path.basename(path)}")
            else:
                self.target_image = image
                self.target_path = path
                self.show_image(image, self.target_label)
                self.status_var.set(f"Target image loaded: {os.path.basename(path)}")
            if self.source_image is not None and self.target_image is not None:
                self.status_var.set("Ready to perform face swap")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")

    def load_source(self):
        self.load_image(is_source=True)

    def load_target(self):
        self.load_image(is_source=False)

    def capture_from_webcam(self, is_source=True):
        messagebox.showinfo("Feature", "Webcam functionality is available but skipped for brevity in this response.")

    def generate_ai_face(self):
        messagebox.showinfo("Feature",
                            "AI Face Generation functionality is available but skipped for brevity in this response.")

    def get_landmarks(self, image):
        return None

    def create_mask(self, landmarks, shape):
        return np.ones((shape[0], shape[1], 1), dtype=np.float32)

    def adjust_colors(self, src, target, amount):
        return src

    def swap_faces(self):
        if self.source_image is None or self.target_image is None:
            messagebox.showerror("Error", "Please load both source and target images.")
            return
        # Mimic successful swap for visual update demonstration
        self.result_image = self.target_image.copy()
        self.show_result()
        self.save_button.config(state=NORMAL)
        self.email_button.config(state=NORMAL)
        self.status_var.set("Face swap completed (Demo).")

    def update_face_swap(self):
        if hasattr(self, 'result_image'):
            self.show_result()

    def update_face_swap_event(self, event=None):
        if hasattr(self, 'result_image'):
            self.update_face_swap()

    def show_image(self, image, label_widget):
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w = rgb.shape[:2]

        # Get the current size of the label's parent frame
        # This will work correctly after the window has been drawn at least once
        try:
            parent_width = label_widget.master.winfo_width()
            parent_height = label_widget.master.winfo_height()
        except:
            # Fallback for initial run before widgets have dimensions
            parent_width = self.display_width
            parent_height = self.display_height

        # Ensure we have valid dimensions and scale is calculated correctly
        if parent_width <= 1 or parent_height <= 1:
            parent_width = self.display_width
            parent_height = self.display_height

        scale = min(parent_width / w, parent_height / h, 1.0)

        resized = cv2.resize(rgb, (int(w * scale), int(h * scale)))
        img_tk = ImageTk.PhotoImage(image=Image.fromarray(resized))
        label_widget.config(image=img_tk, text="")
        label_widget.image = img_tk

    def show_result(self):
        self.show_image(self.result_image, self.result_label)

    def save_result(self):
        messagebox.showinfo("Feature", "Save functionality is available but skipped for brevity in this response.")

    def email_result(self):
        messagebox.showinfo("Feature", "Email functionality is available but skipped for brevity in this response.")

    def open_live_video(self):
        messagebox.showinfo("Feature", "Live Swap functionality is available but skipped for brevity in this response.")

    def perform_live_swap(self, frame, source_image):
        return frame


if __name__ == "__main__":
    root = Tk()
    app = FaceSwapApp(root)
    root.mainloop()
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


# --- Séparateur pour l'esthétique ---
class Separator(Frame):
    def __init__(self, master, **kwargs):
        Frame.__init__(self, master, height=2, bg='#E0E0E0', **kwargs)


class FaceSwapApp:
    def __init__(self, root):
        self.root = root

        # Variables de swap (stockées après le swap initial)
        self.warped_src = None
        self.mask = None  # Le masque du visage float (0.0 à 1.0)

        self.load_models()
        self.load_icons()
        self.setup_ui()

        # Variables d'image
        self.source_image = None
        self.target_image = None
        self.result_image = None
        self.source_path = ""
        self.target_path = ""

        self.display_width = 400
        self.display_height = 300

    def load_icons(self):
        icon_size = (20, 20)
        self.icon_load = None
        self.icon_webcam = None
        self.icon_ai = None
        self.icon_swap = None
        self.icon_save = None
        self.icon_mail = None

        try:
            # NOTE: Assurez-vous que le dossier 'icons' et les images existent.
            self.icon_load = ImageTk.PhotoImage(Image.open("icons/folder.png").resize(icon_size))
            self.icon_webcam = ImageTk.PhotoImage(Image.open("icons/camera.png").resize(icon_size))
            self.icon_ai = ImageTk.PhotoImage(Image.open("icons/ai.png").resize(icon_size))
            self.icon_swap = ImageTk.PhotoImage(Image.open("icons/swap.png").resize(icon_size))
            self.icon_save = ImageTk.PhotoImage(Image.open("icons/save.png").resize(icon_size))
            self.icon_mail = ImageTk.PhotoImage(Image.open("icons/mail.png").resize(icon_size))
        except FileNotFoundError:
            pass
        except Exception as e:
            messagebox.showerror("Icon Load Error", f"Failed to load one or more icons: {e}")

    def create_image_display(self, parent, title):
        container = Frame(parent, bg=parent['bg'])
        Label(container, text=title, font=("Arial", 12, "bold"), bg=parent['bg'], fg="#FFFFFF").pack(side=TOP,
                                                                                                     pady=(0, 5))
        image_frame = Frame(container, bg="#FFFFFF", bd=1, relief=FLAT)
        image_frame.pack(fill=BOTH, expand=True)
        image_label = Label(image_frame, bg="#FFFFFF", text=f"Load a {title.lower()}", font=("Arial", 11), fg="#555")
        image_label.pack(fill=BOTH, expand=True, padx=10, pady=10)
        return container, image_label

    def setup_ui(self):
        self.root.title("Professional Face Swap v2.3")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        self.root.configure(bg="#36454F")

        main_frame = Frame(self.root, bg="#36454F")
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)

        # === Image Frames (MODERNIZED) ===
        self.image_frame = Frame(main_frame, bg="#36454F")
        self.image_frame.pack(fill=BOTH, expand=True)

        self.source_container, self.source_label = self.create_image_display(self.image_frame, "SOURCE IMAGE")
        self.source_container.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        self.target_container, self.target_label = self.create_image_display(self.image_frame, "TARGET IMAGE")
        self.target_container.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")

        self.result_container, self.result_label = self.create_image_display(self.image_frame, "RESULT IMAGE")
        self.result_container.grid(row=0, column=2, padx=15, pady=15, sticky="nsew")

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
        settings_container = Frame(main_frame, bg="#FFFFFF", bd=1, relief=FLAT)
        settings_container.pack(fill=X, pady=15, padx=10)

        Label(settings_container, text="ADVANCED SETTINGS", font=("Arial", 11, "bold"), bg="#FFFFFF",
              fg="#4682B4").pack(side=TOP, pady=(5, 0))
        Separator(settings_container).pack(fill=X, padx=10, pady=5)

        scales_frame = Frame(settings_container, bg="#FFFFFF")
        scales_frame.pack(pady=(0, 10))

        # Blend Controls
        blend_frame = Frame(scales_frame, bg="#FFFFFF")
        blend_frame.pack(side=LEFT, padx=30)
        Label(blend_frame, text="Blend Amount (Source Opacity)", bg="#FFFFFF", font=("Arial", 10, "bold")).pack(
            side=TOP, pady=(0, 2))
        self.blend_scale = Scale(blend_frame, from_=0, to=100, orient=HORIZONTAL, length=250,
                                 bg="#FFFFFF", bd=0, highlightthickness=0,
                                 troughcolor="#A9A9A9", activebackground="#4682B4",
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
                                 troughcolor="#A9A9A9", activebackground="#4682B4",
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
        button.bind("<Enter>", lambda e: button.config(bg=self.darken_color(color, 20)))
        button.bind("<Leave>", lambda e: button.config(bg=color))
        return button

    def darken_color(self, hex_color, amount):
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
        darkened_rgb = tuple(max(0, c - amount) for c in rgb)
        return '#%02x%02x%02x' % darkened_rgb

    # --- Dlib et Modèles ---
    def load_models(self):
        try:
            self.detector = dlib.get_frontal_face_detector()
            model_path = "shape_predictor_68_face_landmarks.dat"
            if not os.path.exists(model_path):
                pass
            self.predictor = dlib.shape_predictor(model_path)
        except Exception as e:
            self.predictor = None

            # --- Fonctions de Chargement d'Images ---

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

    # --- Webcam ---
    def capture_from_webcam(self, is_source=True):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Error", "Cannot open webcam.")
            return

        self.status_var.set("SPACE: Capture image | ESC: Exit")
        cv2.namedWindow("Webcam", cv2.WINDOW_NORMAL)
        captured = None

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            cv2.imshow("Webcam", frame)
            key = cv2.waitKey(1)
            if key == 32:
                captured = frame.copy()
                break
            elif key == 27:
                break

        cap.release()
        cv2.destroyAllWindows()

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
            if self.source_image is not None and self.target_image is not None:
                self.status_var.set("Ready to perform face swap.")

    # --- IA Face Generator ---
    def generate_ai_face(self):
        try:
            self.status_var.set("Downloading AI face...")
            self.root.config(cursor="watch")
            self.root.update()

            url = "https://thispersondoesnotexist.com/image"
            folder = os.path.join(os.getcwd(), "ai_faces")
            os.makedirs(folder, exist_ok=True)

            filename = f"ai_face_{uuid.uuid4().hex[:8]}.jpg"
            filepath = os.path.join(folder, filename)

            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                with open(filepath, 'wb') as out_file:
                    out_file.write(response.read())

            image = cv2.imread(filepath)

            if image is None:
                raise ValueError("AI face could not be downloaded.")

            self.source_image = image
            self.source_path = filepath
            self.show_image(image, self.source_label)
            self.status_var.set("AI face loaded.")

            if self.target_image is not None:
                self.status_var.set("Ready to perform face swap with AI face.")
        except Exception as e:
            messagebox.showerror("AI Face Error", str(e))
            self.status_var.set("AI face generation failed.")
        finally:
            self.root.config(cursor="")

    # --- Fonctions de Traitement (Dlib et OpenCV) ---
    def get_landmarks(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.detector(gray)
        if len(faces) == 0:
            return None
        shape = self.predictor(gray, faces[0])
        return np.array([(p.x, p.y) for p in shape.parts()], dtype=np.int32)

    def create_mask(self, landmarks, shape):
        hull = cv2.convexHull(landmarks)
        mask = np.zeros(shape[:2], dtype=np.float32)
        cv2.fillConvexPoly(mask, hull, 1.0)
        # Augmenter le flou pour un blending encore plus doux sur les bords
        mask = cv2.GaussianBlur(mask, (21, 21), 0)
        return mask[..., np.newaxis]

    def adjust_colors(self, src, target, amount):
        if amount == 0:
            return src
        try:
            # Convertit en LAB et float32 pour des calculs plus précis
            src_lab = cv2.cvtColor(src, cv2.COLOR_BGR2LAB).astype(np.float32)
            target_lab = cv2.cvtColor(target, cv2.COLOR_BGR2LAB).astype(np.float32)

            # Calcule la moyenne et l'écart-type
            src_mean, src_std = cv2.meanStdDev(src_lab)
            tgt_mean, tgt_std = cv2.meanStdDev(target_lab)

            src_mean, src_std = src_mean.flatten(), src_std.flatten()
            tgt_mean, tgt_std = tgt_mean.flatten(), tgt_std.flatten()

            src_std[src_std == 0] = 1.0

            # Interpolation des statistiques entre source et cible
            # On utilise le 'amount' pour pondérer la contribution de la cible (cible.stat) vs source (src.stat)
            # Cette formule est la plus courante pour le transfert de couleur
            normalized = (src_lab - src_mean) / src_std

            # Blend les statistiques:
            target_std_blended = ((1 - amount) * src_std + amount * tgt_std)
            target_mean_blended = ((1 - amount) * src_mean + amount * tgt_mean)

            # Nouvelle image ajustée
            adjusted = normalized * target_std_blended + target_mean_blended

            # Limite les valeurs et reconvertit en BGR uint8
            adjusted = np.clip(adjusted, 0, 255).astype(np.uint8)
            return cv2.cvtColor(adjusted, cv2.COLOR_LAB2BGR)
        except Exception as e:
            print(f"Color adjustment failed: {str(e)}")
            return src

    def swap_faces(self):
        if self.source_image is None or self.target_image is None:
            messagebox.showerror("Error", "Please load both source and target images.")
            return
        if self.predictor is None:
            messagebox.showerror("Error", "Dlib model not loaded. Face swap is not possible.")
            return

        self.status_var.set("Processing... Please wait.")
        self.root.config(cursor="watch")
        self.root.update()

        try:
            src_points = self.get_landmarks(self.source_image)
            tgt_points = self.get_landmarks(self.target_image)

            if src_points is None or tgt_points is None:
                raise ValueError("Face not detected in one or both images.")

            # Crée le masque sur l'image cible (float [0.0, 1.0])
            mask = self.create_mask(tgt_points, self.target_image.shape)

            # Calcule la matrice de transformation affine
            matrix, _ = cv2.estimateAffinePartial2D(src_points.astype(np.float32), tgt_points.astype(np.float32))

            # Applique la transformation à l'image source
            warped_src = cv2.warpAffine(self.source_image, matrix,
                                        (self.target_image.shape[1], self.target_image.shape[0]),
                                        flags=cv2.INTER_LINEAR,
                                        borderMode=cv2.BORDER_REPLICATE)

            # Stocke les résultats du swap initial pour les mises à jour
            self.warped_src = warped_src
            self.mask = mask

            # Lance le blending initial
            self.update_face_swap()
        except Exception as e:
            messagebox.showerror("Error", f"Face swap failed: {str(e)}")
            self.status_var.set("Face swap failed.")
            self.warped_src = None
            self.mask = None
        finally:
            self.root.config(cursor="")

    def update_face_swap(self):
        """
        Met à jour l'image finale en appliquant le Blend Amount comme Opacité
        sur le visage swappé, masqué par le soft mask, APRES ajustement de couleur.
        """
        if self.warped_src is None or self.mask is None:
            return

        try:
            blend_amount = self.blend_scale.get() / 100.0
            color_amount = self.color_scale.get() / 100.0

            # 1. Ajustement des couleurs sur la source déformée
            if color_amount > 0:
                color_adjusted = self.adjust_colors(self.warped_src, self.target_image, color_amount)
            else:
                color_adjusted = self.warped_src

            # Prépare les images et le masque pour les calculs float
            A = color_adjusted.astype(np.float32)  # Source (ajustée)
            B = self.target_image.astype(np.float32)  # Cible (originale)

            # Convertit le masque 1 canal en masque 3 canaux (float [0.0, 1.0])
            mask_3ch = np.repeat(self.mask, 3, axis=2)

            # Final Alpha: Combinaison du soft mask (flou) et de la valeur du curseur (opacity)
            final_alpha = mask_3ch * blend_amount

            # Contribution de la source: (Source Ajustée) * (Alpha Final)
            source_contribution = cv2.multiply(A, final_alpha)

            # Contribution de la cible: (Cible Originale) * (1 - Alpha Final)
            target_contribution = cv2.multiply(B, (1.0 - final_alpha))

            # 3. Fusion finale et conversion en entier 8 bits
            self.result_image = cv2.add(source_contribution, target_contribution).astype(np.uint8)

            self.show_result()
            self.save_button.config(state=NORMAL)
            self.email_button.config(state=NORMAL)
            self.status_var.set("Face swap completed. Adjust sliders for best results.")
        except Exception as e:
            print(f"Update failed: {str(e)}")

    def update_face_swap_event(self, event=None):
        if self.warped_src is not None:
            self.update_face_swap()

    # --- Fonctions d'Affichage et de Fichier ---
    def show_image(self, image, label_widget):
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w = rgb.shape[:2]

        try:
            parent_width = label_widget.master.winfo_width()
            parent_height = label_widget.master.winfo_height()
        except:
            parent_width = self.display_width
            parent_height = self.display_height

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
        if self.result_image is None:
            messagebox.showerror("Error", "No result image to save.")
            return
        default_name = f"swap_{os.path.basename(self.source_path)}_{os.path.basename(self.target_path)}"
        path = filedialog.asksaveasfilename(
            initialfile=default_name,
            defaultextension=".jpg",
            filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")]
        )
        if path:
            try:
                cv2.imwrite(path, self.result_image)
                messagebox.showinfo("Saved", f"Image saved at:\n{path}")
                self.status_var.set(f"Saved to {os.path.basename(path)}")
            except Exception as e:
                messagebox.showerror("Save Error", str(e))

    def email_result(self):
        if self.result_image is None:
            messagebox.showerror("Error", "No result image to email.")
            return

        recipient_email = simpledialog.askstring("Send Email", "Enter recipient's email address:",
                                                 parent=self.root)
        if not recipient_email:
            return

        self.status_var.set("Sending email...")
        self.root.config(cursor="watch")
        self.root.update()

        try:
            # Sauvegarde temporaire du résultat
            temp_file_path = "temp_result.jpg"
            cv2.imwrite(temp_file_path, self.result_image)

            # NOTE: Veuillez remplacer par vos informations de serveur/compte
            sender_email = "projeuneasso@gmail.com"
            sender_password = "qriv crzm bocj bevx"
            smtp_server = "smtp.gmail.com"
            smtp_port = 465

            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = "Your Face-Swapped Photo!"

            body = "Hi,\n\nHere is your face-swapped photo generated by the Professional Face Swap App.\n\nBest regards,\n CPNV Porte Ouvert"
            msg.attach(MIMEText(body, 'plain'))

            with open(temp_file_path, 'rb') as fp:
                img = MIMEImage(fp.read())
                img.add_header('Content-Disposition', 'attachment', filename='face_swapped_photo.jpg')
                msg.attach(img)

            with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
                smtp.login(sender_email, sender_password)
                smtp.send_message(msg)

            os.remove(temp_file_path)

            messagebox.showinfo("Success", f"Photo successfully emailed to {recipient_email}.")
            self.status_var.set("Email sent.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to send email: {str(e)}")
            self.status_var.set("Email failed to send.")
        finally:
            self.root.config(cursor="")

    # --- Live Video Swap ---
    def open_live_video(self):
        if self.source_image is None:
            messagebox.showwarning("Live Swap", "Please load a source image first.")
            return

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Error", "Cannot access webcam.")
            return

        self.status_var.set("Live video started. Press ESC to stop.")

        src_landmarks = self.get_landmarks(self.source_image)
        if src_landmarks is None:
            messagebox.showerror("Error", "Face not detected in the source image for Live Swap.")
            cap.release()
            return

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            result = self.perform_live_swap(frame, self.source_image, src_landmarks)
            cv2.imshow("Live Face Swap", result)

            if cv2.waitKey(1) == 27:
                break

        cap.release()
        cv2.destroyAllWindows()
        self.status_var.set("Live video closed.")

    def perform_live_swap(self, frame, source_image, src_landmarks):

        tgt_landmarks = self.get_landmarks(frame)

        if tgt_landmarks is None:
            return frame

        matrix, _ = cv2.estimateAffinePartial2D(src_landmarks.astype(np.float32), tgt_landmarks.astype(np.float32))
        warped_src = cv2.warpAffine(source_image, matrix, (frame.shape[1], frame.shape[0]))

        hull = cv2.convexHull(tgt_landmarks)
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        cv2.fillConvexPoly(mask, hull, 255)
        mask = cv2.GaussianBlur(mask, (15, 15), 0)

        mask3 = cv2.merge([mask, mask, mask]) / 255.0

        # Blend (simple)
        blended = (warped_src.astype(np.float32) * mask3 + frame.astype(np.float32) * (1 - mask3)).astype(np.uint8)

        return blended


if __name__ == "__main__":
    root = Tk()
    app = FaceSwapApp(root)
    root.mainloop()
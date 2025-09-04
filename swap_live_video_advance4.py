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


class FaceSwapApp:
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

    def load_icons(self):
        icon_size = (20, 20)
        self.icon_load = None
        self.icon_webcam = None
        self.icon_ai = None
        self.icon_swap = None
        self.icon_save = None
        self.icon_mail = None

        try:
            self.icon_load = ImageTk.PhotoImage(Image.open("icons/folder.png").resize(icon_size))
            self.icon_webcam = ImageTk.PhotoImage(Image.open("icons/camera.png").resize(icon_size))
            self.icon_ai = ImageTk.PhotoImage(Image.open("icons/ai.png").resize(icon_size))
            self.icon_swap = ImageTk.PhotoImage(Image.open("icons/swap.png").resize(icon_size))
            self.icon_save = ImageTk.PhotoImage(Image.open("icons/save.png").resize(icon_size))
            self.icon_mail = ImageTk.PhotoImage(Image.open("icons/mail.png").resize(icon_size))
        except FileNotFoundError:
            messagebox.showwarning("Icon Error",
                                   "Icons not found. Please make sure the 'icons' folder exists and contains all required .png files.")
        except Exception as e:
            messagebox.showerror("Icon Load Error", f"Failed to load one or more icons: {e}")

    def setup_ui(self):
        self.root.title("Professional Face Swap v2.3")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        self.root.configure(bg="#e9ebee")

        main_frame = Frame(self.root, bg="#e9ebee")
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)

        # === Image Frames ===
        self.image_frame = Frame(main_frame, bg="#e9ebee")
        self.image_frame.pack(fill=BOTH, expand=True)

        self.source_frame = LabelFrame(self.image_frame, text="Source Image", font=("Arial", 12, "bold"), bg="white",
                                       bd=2, relief=GROOVE)
        self.source_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        self.source_label = Label(self.source_frame, bg="white", text="Load a source image", font=("Arial", 11),
                                  fg="#555")
        self.source_label.pack(fill=BOTH, expand=True, padx=10, pady=10)

        self.target_frame = LabelFrame(self.image_frame, text="Target Image", font=("Arial", 12, "bold"), bg="white",
                                       bd=2, relief=GROOVE)
        self.target_frame.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        self.target_label = Label(self.target_frame, bg="white", text="Load a target image", font=("Arial", 11),
                                  fg="#555")
        self.target_label.pack(fill=BOTH, expand=True, padx=10, pady=10)

        self.result_frame = LabelFrame(self.image_frame, text="Result Image", font=("Arial", 12, "bold"), bg="white",
                                       bd=2, relief=GROOVE)
        self.result_frame.grid(row=0, column=2, padx=15, pady=15, sticky="nsew")
        self.result_label = Label(self.result_frame, bg="white", text="Swapped image will appear here",
                                  font=("Arial", 11), fg="#555")
        self.result_label.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # === Control Panel ===
        control_frame = Frame(main_frame, bg="#e9ebee")
        control_frame.pack(fill=X, pady=10)

        # Buton grupları
        input_buttons = Frame(control_frame, bg="#e9ebee")
        input_buttons.pack(side=LEFT, padx=10)
        self.make_button(input_buttons, "Load Source", self.load_source, icon=self.icon_load).pack(side=LEFT, padx=5)
        self.make_button(input_buttons, "Load Target", self.load_target, icon=self.icon_load).pack(side=LEFT, padx=5)
        self.make_button(input_buttons, "Webcam Source", lambda: self.capture_from_webcam(is_source=True),
                         icon=self.icon_webcam).pack(side=LEFT, padx=5)
        self.make_button(input_buttons, "Webcam Target", lambda: self.capture_from_webcam(is_source=False),
                         icon=self.icon_webcam).pack(side=LEFT, padx=5)
        self.make_button(input_buttons, "Generate AI Face", self.generate_ai_face, icon=self.icon_ai).pack(side=LEFT,
                                                                                                           padx=5)

        action_buttons = Frame(control_frame, bg="#e9ebee")
        action_buttons.pack(side=RIGHT, padx=10)
        self.make_button(action_buttons, "Swap Faces", self.swap_faces, "#3498db", icon=self.icon_swap).pack(side=LEFT,
                                                                                                             padx=5)
        self.make_button(action_buttons, "Live Swap", self.open_live_video, "#ff9800", icon=self.icon_swap).pack(
            side=LEFT, padx=5)
        self.save_button = self.make_button(action_buttons, "Save Result", self.save_result, "#2ecc71",
                                            icon=self.icon_save)
        self.save_button.pack(side=LEFT, padx=5)
        self.save_button.config(state=DISABLED)
        self.email_button = self.make_button(action_buttons, "Email Result", self.email_result, "#e74c3c",
                                             icon=self.icon_mail)
        self.email_button.pack(side=LEFT, padx=5)
        self.email_button.config(state=DISABLED)

        # === Settings ===
        settings_frame = LabelFrame(main_frame, text="Advanced Settings", font=("Arial", 12, "bold"), bg="white", bd=2,
                                    relief=GROOVE)
        settings_frame.pack(fill=X, pady=15, padx=10)

        blend_frame = Frame(settings_frame, bg="white")
        blend_frame.pack(side=LEFT, padx=20, pady=10)
        Label(blend_frame, text="Blend Amount", bg="white", font=("Arial", 10)).pack()
        self.blend_scale = Scale(blend_frame, from_=0, to=100, orient=HORIZONTAL, length=200, bg="#f0f2f5", bd=0,
                                 highlightthickness=0, troughcolor="#bdc3c7")
        self.blend_scale.set(65)
        self.blend_scale.pack()
        self.blend_scale.bind("<ButtonRelease-1>", self.update_face_swap_event)

        color_frame = Frame(settings_frame, bg="white")
        color_frame.pack(side=LEFT, padx=20, pady=10)
        Label(color_frame, text="Color Adjustment", bg="white", font=("Arial", 10)).pack()
        self.color_scale = Scale(color_frame, from_=0, to=100, orient=HORIZONTAL, length=200, bg="#f0f2f5", bd=0,
                                 highlightthickness=0, troughcolor="#bdc3c7")
        self.color_scale.set(50)
        self.color_scale.pack()
        self.color_scale.bind("<ButtonRelease-1>", self.update_face_swap_event)

        # === Status Bar ===
        self.status_var = StringVar()
        self.status_var.set("Ready to load images...")
        status_bar = Label(self.root, textvariable=self.status_var, bd=1, relief=SUNKEN, anchor=W, bg="white",
                           font=("Arial", 10))
        status_bar.pack(side=BOTTOM, fill=X)

        for i in range(3):
            self.image_frame.columnconfigure(i, weight=1)
        self.image_frame.rowconfigure(0, weight=1)

    def make_button(self, parent, text, command, color="#4a4a4a", icon=None):
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

    def load_models(self):
        try:
            self.detector = dlib.get_frontal_face_detector()
            model_path = "shape_predictor_68_face_landmarks.dat"
            if not os.path.exists(model_path):
                raise FileNotFoundError(
                    "Dlib model file not found. Please download it from http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2 and place it in the same directory.")
            self.predictor = dlib.shape_predictor(model_path)
        except Exception as e:
            messagebox.showerror("Model Load Error", str(e))
            self.root.destroy()

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

    def generate_ai_face(self):
        try:
            self.status_var.set("Downloading AI face...")
            self.root.config(cursor="watch")
            self.root.update()

            url = "https://thispersondoesnotexist.com/"
            folder = os.path.join(os.getcwd(), "ai_faces")
            os.makedirs(folder, exist_ok=True)

            filename = f"ai_face_{uuid.uuid4().hex[:8]}.jpg"
            filepath = os.path.join(folder, filename)

            urllib.request.urlretrieve(url, filepath)
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
        mask = cv2.GaussianBlur(mask, (15, 15), 0)
        return mask[..., np.newaxis]

    def adjust_colors(self, src, target, amount):
        if amount == 0:
            return src
        try:
            src_lab = cv2.cvtColor(src, cv2.COLOR_BGR2LAB).astype(np.float32)
            target_lab = cv2.cvtColor(target, cv2.COLOR_BGR2LAB).astype(np.float32)

            src_mean, src_std = cv2.meanStdDev(src_lab)
            tgt_mean, tgt_std = cv2.meanStdDev(target_lab)

            src_mean, src_std = src_mean.flatten(), src_std.flatten()
            tgt_mean, tgt_std = tgt_mean.flatten(), tgt_std.flatten()

            src_std[src_std == 0] = 1.0
            normalized = (src_lab - src_mean) / src_std
            adjusted = normalized * ((1 - amount) * src_std + amount * tgt_std) + \
                       ((1 - amount) * src_mean + amount * tgt_mean)
            adjusted = np.clip(adjusted, 0, 255).astype(np.uint8)
            return cv2.cvtColor(adjusted, cv2.COLOR_LAB2BGR)
        except Exception as e:
            messagebox.showerror("Error", f"Color adjustment failed: {str(e)}")
            return src

    def swap_faces(self):
        if self.source_image is None or self.target_image is None:
            messagebox.showerror("Error", "Please load both source and target images.")
            return

        self.status_var.set("Processing... Please wait.")
        self.root.config(cursor="watch")
        self.root.update()

        try:
            src_points = self.get_landmarks(self.source_image)
            tgt_points = self.get_landmarks(self.target_image)

            if src_points is None or tgt_points is None:
                raise ValueError("Face not detected in one or both images.")

            mask = self.create_mask(tgt_points, self.target_image.shape)
            matrix, _ = cv2.estimateAffinePartial2D(src_points, tgt_points)
            warped_src = cv2.warpAffine(self.source_image, matrix,
                                        (self.target_image.shape[1], self.target_image.shape[0]))

            self.warped_src = warped_src
            self.mask = mask
            self.src_points = src_points
            self.tgt_points = tgt_points

            self.update_face_swap()
        except Exception as e:
            messagebox.showerror("Error", f"Face swap failed: {str(e)}")
            self.status_var.set("Face swap failed.")
        finally:
            self.root.config(cursor="")

    def update_face_swap(self):
        if not hasattr(self, 'warped_src'):
            return

        try:
            blend_amount = self.blend_scale.get() / 100.0
            color_amount = self.color_scale.get() / 100.0

            if color_amount > 0:
                color_adjusted = self.adjust_colors(self.warped_src, self.target_image, color_amount)
            else:
                color_adjusted = self.warped_src

            mask_3ch = np.repeat(self.mask, 3, axis=2)
            blended = (color_adjusted * mask_3ch + self.target_image * (1 - mask_3ch)).astype(np.uint8)
            self.result_image = (blended * blend_amount + self.target_image * (1 - blend_amount)).astype(np.uint8)

            self.show_result()
            self.save_button.config(state=NORMAL)
            self.email_button.config(state=NORMAL)
            self.status_var.set("Face swap completed.")
        except Exception as e:
            messagebox.showerror("Error", f"Update failed: {str(e)}")

    def update_face_swap_event(self, event=None):
        if hasattr(self, 'result_image'):
            self.update_face_swap()

    def show_image(self, image, label_widget):
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w = rgb.shape[:2]
        scale = min(self.display_width / w, self.display_height / h)
        resized = cv2.resize(rgb, (int(w * scale), int(h * scale)))
        img_tk = ImageTk.PhotoImage(image=Image.fromarray(resized))
        label_widget.config(image=img_tk, text="")
        label_widget.image = img_tk

    def show_result(self):
        self.show_image(self.result_image, self.result_label)

    def save_result(self):
        if not hasattr(self, 'result_image'):
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
        if not hasattr(self, 'result_image') or self.result_image is None:
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
            # Save the result image to a temporary file
            temp_file_path = "temp_result.jpg"
            cv2.imwrite(temp_file_path, self.result_image)

            # Email details. You MUST use an app-specific password for security.
            # See https://support.google.com/accounts/answer/185833
            sender_email = "projeuneasso@gmail.com"  # Your email address
            sender_password = "qriv crzm bocj bevx"  # Your app password
            smtp_server = "smtp.gmail.com"
            smtp_port = 465  # SSL port

            # Create a multipart message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = "Your Face-Swapped Photo!"

            # Attach the text body
            body = "Hi,\n\nHere is your face-swapped photo generated by the Professional Face Swap App.\n\nBest regards,\n CPNV Porte Ouvert"
            msg.attach(MIMEText(body, 'plain'))

            # Attach the image
            with open(temp_file_path, 'rb') as fp:
                img = MIMEImage(fp.read())
                img.add_header('Content-Disposition', 'attachment', filename='face_swapped_photo.jpg')
                msg.attach(img)

            # Connect to the SMTP server and send the email
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
                smtp.login(sender_email, sender_password)
                smtp.send_message(msg)

            os.remove(temp_file_path)  # Clean up the temporary file

            messagebox.showinfo("Success", f"Photo successfully emailed to {recipient_email}.")
            self.status_var.set("Email sent.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to send email: {str(e)}")
            self.status_var.set("Email failed to send.")
        finally:
            self.root.config(cursor="")
            # print(self.status_var) # control status

    def open_live_video(self):
        if self.source_image is None:
            messagebox.showwarning("Live Swap", "Please load a source image first.")
            return

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Error", "Cannot access webcam.")
            return

        self.status_var.set("Live video started. Press ESC to stop.")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            result = self.perform_live_swap(frame, self.source_image)
            cv2.imshow("Live Face Swap", result)

            if cv2.waitKey(1) == 27:
                break

        cap.release()
        cv2.destroyAllWindows()
        self.status_var.set("Live video closed.")

    def perform_live_swap(self, frame, source_image):
        src_landmarks = self.get_landmarks(source_image)
        tgt_landmarks = self.get_landmarks(frame)

        if src_landmarks is None or tgt_landmarks is None:
            return frame

        matrix, _ = cv2.estimateAffinePartial2D(src_landmarks, tgt_landmarks)
        warped_src = cv2.warpAffine(source_image, matrix, (frame.shape[1], frame.shape[0]))

        hull = cv2.convexHull(tgt_landmarks)
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        cv2.fillConvexPoly(mask, hull, 255)
        mask = cv2.GaussianBlur(mask, (15, 15), 0)

        mask3 = cv2.merge([mask, mask, mask]) / 255.0
        blended = (warped_src * mask3 + frame * (1 - mask3)).astype(np.uint8)

        return blended


if __name__ == "__main__":
    root = Tk()
    app = FaceSwapApp(root)
    root.mainloop()
# Imports the OpenCV library for image and video processing.
import cv2
# Imports the NumPy library for efficient array and matrix operations.
import numpy as np
# Imports the Dlib library for face detection and landmark prediction.
import dlib
# Imports all necessary components from the Tkinter library for GUI creation.
from tkinter import *
# Imports specific dialog box functions from Tkinter.
from tkinter import filedialog, messagebox, simpledialog
# Imports image handling modules from the PIL/Pillow library.
from PIL import Image, ImageTk, ImageDraw, ImageFont
# Imports the operating system module for file path operations.
import os
# Imports the urllib.request module for fetching data from URLs (e.g., AI face).
import urllib.request
# Imports the uuid module for generating universally unique identifiers.
import uuid
# Imports the smtplib module for sending emails using SMTP.
import smtplib
# Imports MIMEMultipart for creating email messages with multiple parts (text, image).
from email.mime.multipart import MIMEMultipart
# Imports MIMEImage for attaching images to email messages.
from email.mime.image import MIMEImage
# Imports MIMEText for attaching plain text bodies to email messages.
from email.mime.text import MIMEText



# Defines a class for a simple visual separator line in the Tkinter GUI.
class Separator(Frame):
    # Sets the docstring describing the class's purpose.
    """Classe simple pour dessiner une ligne de séparation dans l'interface."""

    # Defines the constructor method for the Separator class.
    def __init__(self, master, **kwargs):
        # Calls the Frame constructor, setting fixed height and background color for the separator.
        Frame.__init__(self, master, height=2, bg='#E0E0E0', **kwargs)


# Defines the main application class for the Face Swap tool.
class FaceSwapApp:
    # Defines the constructor method for the FaceSwapApp class.
    def __init__(self, root):
        # Stores the root Tkinter window object.
        self.root = root

        # Variables de swap (stockées après le swap initial)
        # Initializes a variable to store the warped (transformed) source image (None initially).
        self.warped_src = None  # Image source déformée
        # Initializes a variable to store the face mask (None initially).
        self.mask = None  # Masque du visage float (0.0 à 1.0)

        # Chargement des modèles et de l'interface
        # Calls a method to load Dlib's models (face detector and landmark predictor).
        self.load_models()
        # Calls a method to load icons for the application buttons.
        self.load_icons()
        # Calls a method to set up and configure the graphical user interface.
        self.setup_ui()

        # Variables d'image et de chemins
        # Initializes the OpenCV source image object (None initially).
        self.source_image = None
        # Initializes the OpenCV target image object (None initially).
        self.target_image = None
        # Initializes the OpenCV result image object (None initially).
        self.result_image = None
        # Initializes the file path for the source image (empty string initially).
        self.source_path = ""
        # Initializes the file path for the target image (empty string initially).
        self.target_path = ""

        # Sets a default width for image display in case sizing fails.
        self.display_width = 400
        # Sets a default height for image display in case sizing fails.
        self.display_height = 300

    # Defines the method to load and prepare button icons.
    def load_icons(self):
        # Sets the desired size for all icons.
        icon_size = (20, 20)
        # Initializes the load icon variable.
        self.icon_load = None
        # Initializes the webcam icon variable.
        self.icon_webcam = None
        # Initializes the AI icon variable.
        self.icon_ai = None
        # Initializes the swap icon variable.
        self.icon_swap = None
        # Initializes the save icon variable.
        self.icon_save = None
        # Initializes the mail icon variable.
        self.icon_mail = None

        # Starts a try block to handle potential file errors during loading.
        try:
            # NOTE: Assurez-vous que le dossier 'icons' et les images existent.
            # Loads and resizes the folder icon for the load buttons.
            self.icon_load = ImageTk.PhotoImage(Image.open("icons/folder.png").resize(icon_size))
            # Loads and resizes the camera icon for the webcam buttons.
            self.icon_webcam = ImageTk.PhotoImage(Image.open("icons/camera.png").resize(icon_size))
            # Loads and resizes the AI icon for the AI face generation button.
            self.icon_ai = ImageTk.PhotoImage(Image.open("icons/ai.png").resize(icon_size))
            # Loads and resizes the swap icon for the swap buttons.
            self.icon_swap = ImageTk.PhotoImage(Image.open("icons/swap.png").resize(icon_size))
            # Loads and resizes the save icon for the save button.
            self.icon_save = ImageTk.PhotoImage(Image.open("icons/save.png").resize(icon_size))
            # Loads and resizes the mail icon for the email button.
            self.icon_mail = ImageTk.PhotoImage(Image.open("icons/mail.png").resize(icon_size))
        # Catches the error if icon files are missing.
        except FileNotFoundError:
            # Passes silently if icons aren't found, relying on text labels.
            pass
        # Catches any other unexpected exceptions during icon loading.
        except Exception as e:
            # Shows an error message to the user.
            messagebox.showerror("Icon Load Error", f"Failed to load one or more icons: {e}")

    # Defines the method to create a standardized display area for an image.
    def create_image_display(self, parent, title):
        # Sets the docstring for the method.
        """Crée un cadre pour afficher une image avec un titre."""
        # Creates a Frame container with the parent's background color.
        container = Frame(parent, bg=parent['bg'])
        # Creates a Label for the title and packs it at the top.
        Label(container, text=title, font=("Arial", 12, "bold"), bg=parent['bg'], fg="#FFFFFF").pack(side=TOP,
                                                                                                     pady=(0, 5))
        # Creates an inner Frame with a white background for the actual image.
        image_frame = Frame(container, bg="#FFFFFF", bd=1, relief=FLAT)
        # Packs the inner frame, filling and expanding within the container.
        image_frame.pack(fill=BOTH, expand=True)
        # Creates a Label that will hold the image (initially shows placeholder text).
        image_label = Label(image_frame, bg="#FFFFFF", text=f"Load a {title.lower()}", font=("Arial", 11), fg="#555")
        # Packs the image label, expanding to fill the image frame.
        image_label.pack(fill=BOTH, expand=True, padx=10, pady=10)
        # Returns the outer container and the image label widget.
        return container, image_label

    # Defines the method to set up the main GUI structure.
    def setup_ui(self):
        # Sets the docstring for the method.
        """Configure la structure principale de l'interface graphique."""
        # Sets the title of the main window.
        self.root.title("Professional Face Swap v2.3")
        # Sets the initial size of the window.
        self.root.geometry("1200x800")
        # Sets the minimum allowable size for the window.
        self.root.minsize(1000, 700)
        # Configures the background color of the root window.
        self.root.configure(bg="#36454F")

        # Creates the main frame that holds all other elements.
        main_frame = Frame(self.root, bg="#36454F")
        # Packs the main frame, expanding to fill the root window with padding.
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)

        # === Image Frames (MODERNIZED) ===
        # Creates a frame specifically for holding the three image displays.
        self.image_frame = Frame(main_frame, bg="#36454F")
        # Packs the image frame, allowing it to fill and expand.
        self.image_frame.pack(fill=BOTH, expand=True)

        # Creates the display for the source image and grids it.
        self.source_container, self.source_label = self.create_image_display(self.image_frame, "SOURCE IMAGE")
        self.source_container.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        # Creates the display for the target image and grids it.
        self.target_container, self.target_label = self.create_image_display(self.image_frame, "TARGET IMAGE")
        self.target_container.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")

        # Creates the display for the result image and grids it.
        self.result_container, self.result_label = self.create_image_display(self.image_frame, "RESULT IMAGE")
        self.result_container.grid(row=0, column=2, padx=15, pady=15, sticky="nsew")

        # ---------------------------------------------------------------------
        # FIX FOR WINDOW RESIZE: Added 'minsize=400' to row 0.
        # This prevents the image area from expanding uncontrollably
        # when the sliders trigger image updates, keeping the settings panel visible.
        # ---------------------------------------------------------------------
        # Configures all three columns in the image frame to have equal width (weight=1).
        for i in range(3):
            self.image_frame.columnconfigure(i, weight=1)
        # Configures the row holding the images to expand vertically, but sets a minimum size of 400 pixels.
        self.image_frame.rowconfigure(0, weight=1, minsize=400)  # MODIFIED LINE

        # === Control Panel ===
        # Creates a frame for all control buttons and settings.
        control_frame = Frame(main_frame, bg="#36454F")
        # Packs the control frame to fill the width.
        control_frame.pack(fill=X, pady=10)

        # Creates a sub-frame to center the buttons horizontally.
        all_buttons_frame = Frame(control_frame, bg="#36454F")
        # Packs the button frame, allowing it to expand and push buttons to the center.
        all_buttons_frame.pack(expand=True)
        # Configures 9 columns (for padding and button alignment) to have equal weight.
        for i in range(9):
            all_buttons_frame.columnconfigure(i, weight=1)

        # Row 0: Input Buttons
        # Creates and grids the "Load Source" button.
        self.make_button(all_buttons_frame, "Load Source", self.load_source, color="#4682B4", icon=self.icon_load).grid(
            row=0, column=0, padx=5, pady=5)
        # Creates and grids the "Load Target" button.
        self.make_button(all_buttons_frame, "Load Target", self.load_target, color="#4682B4", icon=self.icon_load).grid(
            row=0, column=1, padx=5, pady=5)
        # Creates and grids the "Webcam Source" button using a lambda function.
        self.make_button(all_buttons_frame, "Webcam Source", lambda: self.capture_from_webcam(is_source=True),
                         color="#4682B4", icon=self.icon_webcam).grid(row=0, column=2, padx=5, pady=5)
        # Creates and grids the "Webcam Target" button using a lambda function.
        self.make_button(all_buttons_frame, "Webcam Target", lambda: self.capture_from_webcam(is_source=False),
                         color="#4682B4", icon=self.icon_webcam).grid(row=0, column=3, padx=5, pady=5)
        # Creates and grids the "Generate AI Face" button.
        self.make_button(all_buttons_frame, "Generate AI Face", self.generate_ai_face, color="#4682B4",
                         icon=self.icon_ai).grid(row=0, column=4, padx=5, pady=5)

        # Row 1: Action Buttons
        # Creates and grids the main "Swap Faces" button.
        self.make_button(all_buttons_frame, "Swap Faces", self.swap_faces, "#3498db", icon=self.icon_swap).grid(row=1,
                                                                                                                column=2,
                                                                                                                padx=5,
                                                                                                                pady=5,
                                                                                                                sticky="ew")
        # Creates and grids the "Live Swap" button.
        self.make_button(all_buttons_frame, "Live Swap", self.open_live_video, "#ff9800", icon=self.icon_swap).grid(
            row=1, column=3, padx=5, pady=5, sticky="ew")
        # Creates the "Save Result" button and stores its reference.
        self.save_button = self.make_button(all_buttons_frame, "Save Result", self.save_result, "#2ecc71",
                                            icon=self.icon_save)
        # Grids the "Save Result" button.
        self.save_button.grid(row=1, column=4, padx=5, pady=5, sticky="ew")
        # Disables the save button initially.
        self.save_button.config(state=DISABLED)
        # Creates the "Email Result" button and stores its reference.
        self.email_button = self.make_button(all_buttons_frame, "Email Result", self.email_result, "#e74c3c",
                                             icon=self.icon_mail)
        # Grids the "Email Result" button.
        self.email_button.grid(row=1, column=5, padx=5, pady=5, sticky="ew")
        # Disables the email button initially.
        self.email_button.config(state=DISABLED)

        # Configures columns 6, 7, and 8 to act as flexible spacers.
        all_buttons_frame.columnconfigure(6, weight=1)
        all_buttons_frame.columnconfigure(7, weight=1)
        all_buttons_frame.columnconfigure(8, weight=1)

        # === Modern Settings Panel ===
        # Creates a container frame for the advanced settings sliders.
        settings_container = Frame(main_frame, bg="#FFFFFF", bd=1, relief=FLAT)
        # Packs the settings container to fill the width.
        settings_container.pack(fill=X, pady=15, padx=10)

        # Creates and packs the title label for the advanced settings.
        Label(settings_container, text="ADVANCED SETTINGS", font=("Arial", 11, "bold"), bg="#FFFFFF",
              fg="#4682B4").pack(side=TOP, pady=(5, 0))
        # Creates and packs a separator line.
        Separator(settings_container).pack(fill=X, padx=10, pady=5)

        # Creates a frame to hold the sliders side-by-side.
        scales_frame = Frame(settings_container, bg="#FFFFFF")
        # Packs the scales frame.
        scales_frame.pack(pady=(0, 10))

        # Blend Controls
        # Creates a frame for the blend slider.
        blend_frame = Frame(scales_frame, bg="#FFFFFF")
        # Packs the blend frame to the left.
        blend_frame.pack(side=LEFT, padx=30)
        # Creates and packs the label for the blend slider.
        Label(blend_frame, text="Blend Amount (Source Opacity)", bg="#FFFFFF", font=("Arial", 10, "bold")).pack(
            side=TOP, pady=(0, 2))
        # Creates the horizontal blend scale (slider).
        self.blend_scale = Scale(blend_frame, from_=0, to=100, orient=HORIZONTAL, length=250,
                                 bg="#FFFFFF", bd=0, highlightthickness=0,
                                 troughcolor="#A9A9A9", activebackground="#4682B4",
                                 sliderrelief=FLAT)
        # Sets the default value of the blend scale to 65.
        self.blend_scale.set(65)
        # Packs the blend scale.
        self.blend_scale.pack(side=BOTTOM)
        # Binds the mouse button release event to trigger the face swap update.
        self.blend_scale.bind("<ButtonRelease-1>", self.update_face_swap_event)

        # Color Controls
        # Creates a frame for the color slider.
        color_frame = Frame(scales_frame, bg="#FFFFFF")
        # Packs the color frame to the left.
        color_frame.pack(side=LEFT, padx=30)
        # Creates and packs the label for the color slider.
        Label(color_frame, text="Color Adjustment", bg="#FFFFFF", font=("Arial", 10, "bold")).pack(side=TOP,
                                                                                                   pady=(0, 2))
        # Creates the horizontal color scale (slider).
        self.color_scale = Scale(color_frame, from_=0, to=100, orient=HORIZONTAL, length=250,
                                 bg="#FFFFFF", bd=0, highlightthickness=0,
                                 troughcolor="#A9A9A9", activebackground="#4682B4",
                                 sliderrelief=FLAT)
        # Sets the default value of the color scale to 50.
        self.color_scale.set(50)
        # Packs the color scale.
        self.color_scale.pack(side=BOTTOM)
        # Binds the mouse button release event to trigger the face swap update.
        self.color_scale.bind("<ButtonRelease-1>", self.update_face_swap_event)

        # === Status Bar ===
        # Creates a StringVar to hold the status message text.
        self.status_var = StringVar()
        # Sets the initial status message.
        self.status_var.set("Ready to load images...")
        # Creates the status bar Label widget.
        status_bar = Label(self.root, textvariable=self.status_var, bd=1, relief=SUNKEN, anchor=W, bg="#DCDCDC",
                           font=("Arial", 10), fg="#333")
        # Packs the status bar at the bottom, filling the width.
        status_bar.pack(side=BOTTOM, fill=X)

    # Defines a helper method to create stylized buttons.
    def make_button(self, parent, text, command, color="#4a4a4a", icon=None):
        # Sets the docstring for the method.
        """Crée un bouton stylisé avec gestion des couleurs."""
        # Checks if the default color was passed and updates it to a custom gray-blue if so.
        if color == "#4a4a4a":
            # Sets the default blue color.
            color = "#4682B4"

        # Creates the Button widget with all styling and properties.
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
        # Binds the mouse entry event to darken the button color (hover effect).
        button.bind("<Enter>", lambda e: button.config(bg=self.darken_color(color, 20)))
        # Binds the mouse exit event to restore the original button color.
        button.bind("<Leave>", lambda e: button.config(bg=color))
        # Returns the created button object.
        return button

    # Defines a utility method to programmatically darken a hex color.
    def darken_color(self, hex_color, amount):
        # Sets the docstring for the method.
        """Assombrit une couleur hexadécimale."""
        # Removes the '#' from the hexadecimal string.
        hex_color = hex_color.lstrip('#')
        # Converts the hex string to an RGB tuple of integers.
        rgb = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
        # Subtracts the 'amount' from each RGB component, ensuring the minimum is 0.
        darkened_rgb = tuple(max(0, c - amount) for c in rgb)
        # Converts the darkened RGB tuple back into a hex string format.
        return '#%02x%02x%02x' % darkened_rgb

    # --- Dlib et Modèles ---
    # Defines the method to load Dlib models.
    def load_models(self):
        # Sets the docstring for the method.
        """Charge le détecteur de visage Dlib et le prédicteur de points de repère."""
        # Starts a try block to handle model loading errors.
        try:
            # Initializes Dlib's frontal face detector.
            self.detector = dlib.get_frontal_face_detector()
            # Defines the path to the landmark prediction model file.
            model_path = "shape_predictor_68_face_landmarks.dat"
            # Checks if the model file exists (though the next line might fail if it doesn't).
            if not os.path.exists(model_path):
                # Passes silently if the model file is not found (assuming it might be loaded later or handled by the next exception).
                pass
            # Initializes Dlib's shape predictor with the 68-point model.
            self.predictor = dlib.shape_predictor(model_path)
        # Catches any exception during model loading.
        except Exception as e:
            # If loading fails, sets the predictor to None.
            self.predictor = None

            # --- Fonctions de Chargement d'Images ---

    # Defines the generic method to load an image from a file dialog.
    def load_image(self, is_source=True):
        # Sets the docstring for the method.
        """Charge une image à partir d'un fichier."""
        # Opens the file dialog, allowing selection of image files.
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
        # Returns if the user cancels the dialog.
        if not path:
            return
        # Starts a try block for image loading and processing.
        try:
            # Reads the image file using OpenCV.
            image = cv2.imread(path)
            # Raises an error if OpenCV failed to load the image (e.g., corrupted file).
            if image is None:
                raise ValueError("Invalid image file")
            # Checks if the image is meant for the source display.
            if is_source:
                # Stores the loaded image as the source image.
                self.source_image = image
                # Stores the file path.
                self.source_path = path
                # Calls the method to display the image in the source label.
                self.show_image(image, self.source_label)
                # Updates the status bar.
                self.status_var.set(f"Source image loaded: {os.path.basename(path)}")
            # Executes if the image is meant for the target display.
            else:
                # Stores the loaded image as the target image.
                self.target_image = image
                # Stores the file path.
                self.target_path = path
                # Calls the method to display the image in the target label.
                self.show_image(image, self.target_label)
                # Updates the status bar.
                self.status_var.set(f"Target image loaded: {os.path.basename(path)}")
            # Checks if both source and target images are loaded.
            if self.source_image is not None and self.target_image is not None:
                # Updates the status bar to prompt for a swap operation.
                self.status_var.set("Ready to perform face swap")
        # Catches any exceptions during the loading process.
        except Exception as e:
            # Shows an error message.
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")

    # Defines a wrapper method for loading the source image.
    def load_source(self):
        # Calls the generic loader, specifying it's for the source.
        self.load_image(is_source=True)

    # Defines a wrapper method for loading the target image.
    def load_target(self):
        # Calls the generic loader, specifying it's for the target.
        self.load_image(is_source=False)

    # --- Webcam ---
    # Defines the method to capture a still image from the webcam.
    def capture_from_webcam(self, is_source=True):
        # Sets the docstring for the method.
        """Capture une image fixe à partir de la webcam."""
        # Opens the first available video capture device (webcam).
        cap = cv2.VideoCapture(0)
        # Checks if the camera opened successfully.
        if not cap.isOpened():
            # Shows an error message and returns if the webcam cannot be opened.
            messagebox.showerror("Error", "Cannot open webcam.")
            return

        # Updates the status bar with capture instructions.
        self.status_var.set("SPACE: Capture image | ESC: Exit")
        # Creates a resizable window for the webcam feed.
        cv2.namedWindow("Webcam", cv2.WINDOW_NORMAL)
        # Initializes the captured image variable.
        captured = None

        # Starts an infinite loop for the video feed.
        while True:
            # Reads a frame from the camera (ret is success flag, frame is the image).
            ret, frame = cap.read()
            # Breaks the loop if reading failed (e.g., camera disconnected).
            if not ret:
                break
            # Displays the current frame in the window.
            cv2.imshow("Webcam", frame)
            # Waits 1ms for a key press.
            key = cv2.waitKey(1)
            # Checks if the Spacebar (key code 32) was pressed.
            if key == 32:
                # Stores a copy of the current frame.
                captured = frame.copy()
                # Breaks the loop.
                break
            # Checks if the Escape key (key code 27) was pressed.
            elif key == 27:
                # Breaks the loop.
                break

        # Releases the webcam resource.
        cap.release()
        # Closes all OpenCV windows.
        cv2.destroyAllWindows()

        # Proceeds if an image was successfully captured.
        if captured is not None:
            # Checks if the captured image is for the source.
            if is_source:
                # Stores the captured image as source.
                self.source_image = captured
                # Assigns a temporary path name.
                self.source_path = "webcam_source.jpg"
                # Displays the image in the source label.
                self.show_image(captured, self.source_label)
                # Updates the status bar.
                self.status_var.set("Source image captured from webcam.")
            # Executes if the captured image is for the target.
            else:
                # Stores the captured image as target.
                self.target_image = captured
                # Assigns a temporary path name.
                self.target_path = "webcam_target.jpg"
                # Displays the image in the target label.
                self.show_image(captured, self.target_label)
                # Updates the status bar.
                self.status_var.set("Target image captured from webcam.")
            # Checks if both images are now loaded.
            if self.source_image is not None and self.target_image is not None:
                # Updates the status bar.
                self.status_var.set("Ready to perform face swap.")

    # --- IA Face Generator ---
    # Defines the method to download an AI-generated face.
    def generate_ai_face(self):
        # Sets the docstring for the method.
        """Télécharge un visage généré par IA et l'utilise comme source."""
        # Starts a try block for the download process.
        try:
            # Updates the status bar.
            self.status_var.set("Downloading AI face...")
            # Changes the cursor to a watch/busy indicator.
            self.root.config(cursor="watch")
            # Forces the GUI to update immediately.
            self.root.update()

            # Defines the URL for the AI-generated person image.
            url = "https://thispersondoesnotexist.com/image"
            # Defines the path for the 'ai_faces' folder in the current directory.
            folder = os.path.join(os.getcwd(), "ai_faces")
            # Creates the folder if it does not exist.
            os.makedirs(folder, exist_ok=True)

            # Generates a unique filename using a UUID.
            filename = f"ai_face_{uuid.uuid4().hex[:8]}.jpg"
            # Constructs the full file path.
            filepath = os.path.join(folder, filename)

            # Creates a request object with a User-Agent header to mimic a browser.
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            # Opens the URL request.
            with urllib.request.urlopen(req) as response:
                # Opens the local file for writing in binary mode.
                with open(filepath, 'wb') as out_file:
                    # Reads the content from the response and writes it to the file.
                    out_file.write(response.read())

            # Reads the downloaded image using OpenCV.
            image = cv2.imread(filepath)

            # Checks if the image was read successfully.
            if image is None:
                # Raises an error if the image data was invalid.
                raise ValueError("AI face could not be downloaded.")

            # Sets the downloaded image as the source image.
            self.source_image = image
            # Sets the file path.
            self.source_path = filepath
            # Displays the image in the source label.
            self.show_image(image, self.source_label)
            # Updates the status bar.
            self.status_var.set("AI face loaded.")

            # Checks if the target image is also present.
            if self.target_image is not None:
                # Updates the status bar to prompt for a swap.
                self.status_var.set("Ready to perform face swap with AI face.")
        # Catches exceptions during the download or loading process.
        except Exception as e:
            # Shows an error message.
            messagebox.showerror("AI Face Error", str(e))
            # Updates the status bar.
            self.status_var.set("AI face generation failed.")
        # Executes regardless of try/except outcome.
        finally:
            # Restores the cursor to normal.
            self.root.config(cursor="")

    # --- Fonctions de Traitement (Dlib et OpenCV) ---
    # Defines the method to get 68 facial landmarks.
    def get_landmarks(self, image):
        # Sets the docstring for the method.
        """Détecte les visages et retourne les 68 points de repère."""
        # Converts the image to grayscale, which is required by Dlib's detector.
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Detects faces in the grayscale image.
        faces = self.detector(gray)
        # Returns None if no faces are detected.
        if len(faces) == 0:
            return None
        # Gets the 68 landmarks for the first detected face.
        shape = self.predictor(gray, faces[0])
        # Converts the Dlib shape object into a NumPy array of (x, y) coordinates.
        return np.array([(p.x, p.y) for p in shape.parts()], dtype=np.int32)

    # Defines the method to create a soft, expanded mask around the face.
    def create_mask(self, landmarks, shape):
        # Sets the docstring for the method.
        """Crée un masque doux (soft mask) élargi."""
        # Calculates the convex hull (the tightest convex boundary) of the landmarks.
        hull = cv2.convexHull(landmarks)

        # 1. Calcule le centre du Convex Hull (zone du visage)
        # Calculates the moments of the hull (used to find the center).
        M = cv2.moments(hull)
        # Fallback if the moment calculation is invalid (division by zero).
        if M['m00'] == 0:
            # Returns a full white mask (1.0) if center calculation fails.
            return np.ones(shape[:2], dtype=np.float32)[..., np.newaxis]

        # Calculates the X coordinate of the hull's center.
        cX = int(M['m10'] / M['m00'])
        # Calculates the Y coordinate of the hull's center.
        cY = int(M['m01'] / M['m00'])

        # 2. Élargit le hull de 15% (scale_factor = 1.15)
        # Sets the factor to expand the hull size.
        scale_factor = 1.15
        # Expands the hull points by moving them away from the center.
        hull_expanded = np.array([
            [
                cX + int((point[0][0] - cX) * scale_factor),
                cY + int((point[0][1] - cY) * scale_factor)
            ]
            # Iterates through the points in the original hull.
            for point in hull
        ])

        # 3. Crée le masque binaire avec le hull élargi
        # Creates a black mask (0.0) with the shape of the image.
        mask = np.zeros(shape[:2], dtype=np.float32)
        # Fills the expanded convex hull area with white (1.0).
        cv2.fillConvexPoly(mask, hull_expanded, 1.0)

        # 4. Applique un Flou Gaussien (25x25) pour une transition très douce
        # Applies a large Gaussian blur to create very soft edges (the "soft mask").
        mask = cv2.GaussianBlur(mask, (25, 25), 0)
        # Adds an extra dimension to the mask (making it [H, W, 1]) for easier color channel broadcasting.
        return mask[..., np.newaxis]

    # Defines the method for color correction/adjustment.
    def adjust_colors(self, src, target, amount):
        # Sets the docstring for the method.
        """Ajuste les couleurs de la source déformée pour correspondre à la cible."""
        # Returns the source image unmodified if the adjustment amount is 0.
        if amount == 0:
            return src
        # Starts a try block for the color adjustment process.
        try:
            # Converts the source image to LAB color space (float32).
            src_lab = cv2.cvtColor(src, cv2.COLOR_BGR2LAB).astype(np.float32)
            # Converts the target image to LAB color space (float32).
            target_lab = cv2.cvtColor(target, cv2.COLOR_BGR2LAB).astype(np.float32)

            # Utilise self.mask pour isoler le visage de la cible
            # Creates an 8-bit mask of the face area (255 where self.mask is 1.0).
            mask_target = self.mask.astype(np.uint8) * 255

            # Calcul des statistiques
            # Calculates the Mean and Standard Deviation of the target's face area (using the mask).
            tgt_mean, tgt_std = cv2.meanStdDev(target_lab, mask=mask_target)
            # Calculates the Mean and Standard Deviation of the entire source image.
            src_mean, src_std = cv2.meanStdDev(src_lab)

            # Flattens the mean and std arrays for easier mathematical operations.
            src_mean, src_std = src_mean.flatten(), src_std.flatten()
            # Flattens the mean and std arrays for the target.
            tgt_mean, tgt_std = tgt_mean.flatten(), tgt_std.flatten()

            # Prevents division by zero errors by replacing zero std dev with 1.0.
            src_std[src_std == 0] = 1.0

            # Normalisation et transfert de couleur pondéré
            # Normalizes the source image color channels (subtract mean, divide by std dev).
            normalized = (src_lab - src_mean) / src_std

            # Blends the source and target standard deviations based on the 'amount'.
            target_std_blended = ((1 - amount) * src_std + amount * tgt_std)
            # Blends the source and target means based on the 'amount'.
            target_mean_blended = ((1 - amount) * src_mean + amount * tgt_mean)

            # Applies the blended statistics (std dev and mean) to the normalized source.
            adjusted = normalized * target_std_blended + target_mean_blended

            # Conversion finale
            # Clamps the values to the valid 0-255 range and converts back to 8-bit integers.
            adjusted = np.clip(adjusted, 0, 255).astype(np.uint8)
            # Converts the adjusted LAB image back to BGR color space.
            return cv2.cvtColor(adjusted, cv2.COLOR_LAB2BGR)
        # Catches any error during color adjustment.
        except Exception as e:
            # Prints the error and returns the source image unadjusted.
            print(f"Color adjustment failed: {str(e)}")
            return src

    # Defines the primary method to perform the initial face swap calculation.
    def swap_faces(self):
        # Sets the docstring for the method.
        """Exécute l'opération initiale de détection, warping et masquage."""
        # Checks if both required images are loaded.
        if self.source_image is None or self.target_image is None:
            # Shows an error if images are missing.
            messagebox.showerror("Error", "Please load both source and target images.")
            return
        # Checks if the Dlib model was successfully loaded.
        if self.predictor is None:
            # Shows an error if the Dlib model is missing.
            messagebox.showerror("Error", "Dlib model not loaded. Face swap is not possible.")
            return

        # Updates the status bar to indicate processing.
        self.status_var.set("Processing... Please wait.")
        # Changes the cursor to a watch/busy indicator.
        self.root.config(cursor="watch")
        # Forces the GUI to update immediately.
        self.root.update()

        # Starts a try block for the complex image processing.
        try:
            # Gets the landmarks for the source image.
            src_points = self.get_landmarks(self.source_image)
            # Gets the landmarks for the target image.
            tgt_points = self.get_landmarks(self.target_image)

            # Checks if faces were detected in both images.
            if src_points is None or tgt_points is None:
                # Raises an error if face detection failed.
                raise ValueError("Face not detected in one or both images.")

            # Crée le masque (amélioré) sur l'image cible
            # Creates the soft, expanded mask based on the target face landmarks.
            mask = self.create_mask(tgt_points, self.target_image.shape)

            # Calcule la matrice de transformation affine
            # Estimates the affine (translation, rotation, scale) transformation matrix.
            matrix, _ = cv2.estimateAffinePartial2D(src_points.astype(np.float32), tgt_points.astype(np.float32))

            # Applique la transformation à l'image source
            # Performs the warping (transformation) of the source image onto the target space.
            warped_src = cv2.warpAffine(self.source_image, matrix,
                                        (self.target_image.shape[1], self.target_image.shape[0]),
                                        flags=cv2.INTER_LINEAR,
                                        # Uses BORDER_REPLICATE to fill empty areas with surrounding pixel colors (no black borders).
                                        borderMode=cv2.BORDER_REPLICATE)

            # Stocke les résultats pour les mises à jour en direct via les sliders
            # Stores the warped source image.
            self.warped_src = warped_src
            # Stores the generated mask.
            self.mask = mask

            # Lance le blending initial
            # Calls the method to perform the final blending and display the result.
            self.update_face_swap()
        # Catches any error during the swap process.
        except Exception as e:
            # Shows an error message.
            messagebox.showerror("Error", f"Face swap failed: {str(e)}")
            # Updates the status bar.
            self.status_var.set("Face swap failed.")
            # Clears stored intermediate results.
            self.warped_src = None
            self.mask = None
        # Executes regardless of try/except outcome.
        finally:
            # Restores the cursor to normal.
            self.root.config(cursor="")

    # Defines the method to update the final result based on slider values.
    def update_face_swap(self):
        # Sets the docstring for the method.
        """Met à jour l'image finale avec les ajustements de couleur et de blend."""
        # Returns immediately if the necessary intermediate data is missing.
        if self.warped_src is None or self.mask is None:
            return

        # Starts a try block for the update logic.
        try:
            # Gets the blend slider value (0.0 to 1.0).
            blend_amount = self.blend_scale.get() / 100.0
            # Gets the color slider value (0.0 to 1.0).
            color_amount = self.color_scale.get() / 100.0

            # 1. Ajustement des couleurs
            # Checks if color adjustment is needed.
            if color_amount > 0:
                # Performs color adjustment on the warped source.
                color_adjusted = self.adjust_colors(self.warped_src, self.target_image, color_amount)
            # Executes if no color adjustment is needed.
            else:
                # Uses the original warped source image.
                color_adjusted = self.warped_src

            # Prépare les images et le masque pour les calculs float
            # Gets the color-adjusted source image as float32.
            A = color_adjusted.astype(np.float32)  # Source (ajustée en couleur)
            # Gets the original target image as float32.
            B = self.target_image.astype(np.float32)  # Cible (originale)

            # Convertit le masque 1 canal en masque 3 canaux
            # Repeats the 1-channel mask 3 times to match the BGR color channels.
            mask_3ch = np.repeat(self.mask, 3, axis=2)

            # Final Alpha: Masque doux multiplié par la quantité de blend (opacité)
            # Calculates the final weighted mask (softness * opacity).
            final_alpha = mask_3ch * blend_amount

            # 2. Blend pondéré (weighted blend)
            # Calculates the contribution of the source image (Source * Alpha).
            source_contribution = cv2.multiply(A, final_alpha)
            # Calculates the contribution of the target image (Target * (1 - Alpha)).
            target_contribution = cv2.multiply(B, (1.0 - final_alpha))

            # 3. Fusion finale
            # Adds the two contributions and converts the result back to 8-bit integers.
            self.result_image = cv2.add(source_contribution, target_contribution).astype(np.uint8)

            # Displays the final result image.
            self.show_result()
            # Enables the save button.
            self.save_button.config(state=NORMAL)
            # Enables the email button.
            self.email_button.config(state=NORMAL)
            # Updates the status bar.
            self.status_var.set("Face swap completed. Adjust sliders for best results.")
        # Catches any error during the update process.
        except Exception as e:
            # Prints the error to the console.
            print(f"Update failed: {str(e)}")

    # Defines the event handler for slider release.
    def update_face_swap_event(self, event=None):
        # Sets the docstring for the method.
        """Déclenche la mise à jour lorsque le slider est relâché."""
        # Checks if the swap data is available.
        if self.warped_src is not None:
            # Calls the main update function.
            self.update_face_swap()

    # --- Fonctions d'Affichage et de Fichier ---
    # Defines the method to display an OpenCV image in a Tkinter Label.
    def show_image(self, image, label_widget):
        # Sets the docstring for the method.
        """Affiche une image OpenCV dans un widget Label Tkinter."""
        # Converts the image from BGR (OpenCV default) to RGB (PIL/Tkinter requirement).
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # Gets the height and width of the image.
        h, w = rgb.shape[:2]

        # Tries to get the current dimensions of the parent frame dynamically.
        try:
            # Gets the width of the parent frame.
            parent_width = label_widget.master.winfo_width()
            # Gets the height of the parent frame.
            parent_height = label_widget.master.winfo_height()
        # Executes if getting dimensions fails (e.g., window not fully rendered).
        except:
            # Uses the default display width.
            parent_width = self.display_width
            # Uses the default display height.
            parent_height = self.display_height

        # Ensures dimensions are positive; falls back to defaults if they are not.
        if parent_width <= 1 or parent_height <= 1:
            parent_width = self.display_width
            parent_height = self.display_height

        # Calcule le facteur d'échelle
        # Calculates the scaling factor to fit the image inside the parent frame, without exceeding 1.0 (no upscaling).
        scale = min(parent_width / w, parent_height / h, 1.0)

        # Resizes the image using the calculated scale factor.
        resized = cv2.resize(rgb, (int(w * scale), int(h * scale)))
        # Converts the resized NumPy array into a Tkinter PhotoImage object via PIL.
        img_tk = ImageTk.PhotoImage(image=Image.fromarray(resized))
        # Updates the label's image and clears any text.
        label_widget.config(image=img_tk, text="")
        # Stores a reference to the PhotoImage object to prevent it from being garbage collected.
        label_widget.image = img_tk

    # Defines a wrapper method to display the result image.
    def show_result(self):
        # Calls the generic image display method for the result image.
        self.show_image(self.result_image, self.result_label)

    # Defines the method to save the result image to a file.
    def save_result(self):
        # Sets the docstring for the method.
        """Sauvegarde l'image résultat."""
        # Checks if a result image exists.
        if self.result_image is None:
            # Shows an error if no result is available.
            messagebox.showerror("Error", "No result image to save.")
            return
        # Creates a default filename based on the source and target file names.
        default_name = f"swap_{os.path.basename(self.source_path)}_{os.path.basename(self.target_path)}"
        # Opens the save file dialog.
        path = filedialog.asksaveasfilename(
            # Sets the initial suggested filename.
            initialfile=default_name,
            # Sets the default file extension.
            defaultextension=".jpg",
            # Filters the file types shown in the dialog.
            filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")]
        )
        # Proceeds if the user selected a path.
        if path:
            # Starts a try block for file writing.
            try:
                # Writes the result image to the specified path using OpenCV.
                cv2.imwrite(path, self.result_image)
                # Shows a success message.
                messagebox.showinfo("Saved", f"Image saved at:\n{path}")
                # Updates the status bar.
                self.status_var.set(f"Saved to {os.path.basename(path)}")
            # Catches any error during saving.
            except Exception as e:
                # Shows an error message.
                messagebox.showerror("Save Error", str(e))

    # Defines the method to email the result image.
    def email_result(self):
        # Sets the docstring for the method.
        """Envoie l'image résultat par e-mail."""
        # Checks if a result image exists.
        if self.result_image is None:
            # Shows an error if no result is available.
            messagebox.showerror("Error", "No result image to email.")
            return

        # Opens a simple dialog to ask for the recipient's email address.
        recipient_email = simpledialog.askstring("Send Email", "Enter recipient's email address:",
                                                 parent=self.root)
        # Returns if the user cancels the dialog or enters nothing.
        if not recipient_email:
            return

        # Updates the status bar.
        self.status_var.set("Sending email...")
        # Changes the cursor to a watch/busy indicator.
        self.root.config(cursor="watch")
        # Forces the GUI to update immediately.
        self.root.update()

        # Starts a try block for the emailing process.
        try:
            # Sauvegarde temporaire du résultat
            # Defines a temporary filename.
            temp_file_path = "temp_result.jpg"
            # Saves the result image temporarily.
            cv2.imwrite(temp_file_path, self.result_image)

            # NOTE: Remplacer par vos informations de serveur/compte
            # Defines the sender's email address.
            sender_email = "projeuneasso@gmail.com"
            # Defines the sender's email password (App Password recommended for Gmail).
            sender_password = "qriv crzm bocj bevx"
            # Defines the SMTP server address.
            smtp_server = "smtp.gmail.com"
            # Defines the secure SMTP port number.
            smtp_port = 465

            # Creates a multipart email message object.
            msg = MIMEMultipart()
            # Sets the sender's address.
            msg['From'] = sender_email
            # Sets the recipient's address.
            msg['To'] = recipient_email
            # Sets the email subject line.
            msg['Subject'] = "Your Face-Swapped Photo!"

            # Defines the email body text.
            body = "Hi,\n\nHere is your face-swapped photo generated by the Professional Face Swap App.\n\nBest regards,\n CPNV Porte Ouvert"
            # Attaches the body text as plain text.
            msg.attach(MIMEText(body, 'plain'))

            # Opens the temporary image file in binary read mode.
            with open(temp_file_path, 'rb') as fp:
                # Creates an MIMEImage object from the file content.
                img = MIMEImage(fp.read())
                # Adds a header to specify the filename for the attachment.
                img.add_header('Content-Disposition', 'attachment', filename='face_swapped_photo.jpg')
                # Attaches the image to the email.
                msg.attach(img)

            # Connects to the SMTP server using SSL/TLS (secure connection).
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
                # Logs in to the SMTP account.
                smtp.login(sender_email, sender_password)
                # Sends the email message.
                smtp.send_message(msg)

            # Deletes the temporary image file.
            os.remove(temp_file_path)

            # Shows a success message.
            messagebox.showinfo("Success", f"Photo successfully emailed to {recipient_email}.")
            # Updates the status bar.
            self.status_var.set("Email sent.")

        # Catches any error during the emailing process.
        except Exception as e:
            # Shows an error message.
            messagebox.showerror("Error", f"Failed to send email: {str(e)}")
            # Updates the status bar.
            self.status_var.set("Email failed to send.")
        # Executes regardless of try/except outcome.
        finally:
            # Restores the cursor to normal.
            self.root.config(cursor="")

    # --- Live Video Swap ---
    # Defines the method to open the webcam for live face swapping.
    def open_live_video(self):
        # Sets the docstring for the method.
        """Ouvre la webcam pour l'échange de visage en temps réel."""
        # Checks if a source image has been loaded for the face to be swapped in.
        if self.source_image is None:
            # Shows a warning if the source image is missing.
            messagebox.showwarning("Live Swap", "Please load a source image first.")
            return

        # Opens the webcam.
        cap = cv2.VideoCapture(0)
        # Checks if the camera opened successfully.
        if not cap.isOpened():
            # Shows an error if the webcam cannot be accessed.
            messagebox.showerror("Error", "Cannot access webcam.")
            return

        # Updates the status bar.
        self.status_var.set("Live video started. Press ESC to stop.")

        # Gets the landmarks for the static source image.
        src_landmarks = self.get_landmarks(self.source_image)
        # Checks if a face was detected in the source image.
        if src_landmarks is None:
            # Shows an error if no face is found in the source.
            messagebox.showerror("Error", "Face not detected in the source image for Live Swap.")
            # Releases the camera.
            cap.release()
            return

        # Starts the loop for the live video feed.
        while True:
            # Reads a frame from the webcam.
            ret, frame = cap.read()
            # Breaks the loop if reading failed.
            if not ret:
                break

            # Calls the method to perform the live swap on the current frame.
            result = self.perform_live_swap(frame, self.source_image, src_landmarks)
            # Displays the result in a new window.
            cv2.imshow("Live Face Swap", result)

            # Checks if the Escape key (key code 27) was pressed.
            if cv2.waitKey(1) == 27:
                # Breaks the loop to stop the live feed.
                break

        # Releases the camera resource.
        cap.release()
        # Closes all OpenCV windows.
        cv2.destroyAllWindows()
        # Updates the status bar.
        self.status_var.set("Live video closed.")

    # Defines the method that handles the actual face swap logic for one frame.
    def perform_live_swap(self, frame, source_image, src_landmarks):
        # Sets the docstring for the method.
        """Effectue le swap sur une seule image (frame) pour le mode Live."""
        # Gets the landmarks for the face in the live video frame (the target).
        tgt_landmarks = self.get_landmarks(frame)

        # Returns the original frame if no face is detected in the target.
        if tgt_landmarks is None:
            return frame

        # Calculates the affine transformation matrix to align source to target.
        matrix, _ = cv2.estimateAffinePartial2D(src_landmarks.astype(np.float32), tgt_landmarks.astype(np.float32))

        # Utilisation de BORDER_REPLICATE.
        # Warps the source image onto the target position.
        warped_src = cv2.warpAffine(source_image, matrix, (frame.shape[1], frame.shape[0]),
                                    borderMode=cv2.BORDER_REPLICATE)

        # Création du masque (simple) pour le live
        # Calculates the convex hull of the target face.
        hull = cv2.convexHull(tgt_landmarks)
        # Creates a black mask.
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        # Fills the hull with white (255).
        cv2.fillConvexPoly(mask, hull, 255)
        # Applies a small Gaussian blur for a basic blend.
        mask = cv2.GaussianBlur(mask, (15, 15), 0)

        # Converts the 1-channel mask to a 3-channel float mask (0.0 to 1.0).
        mask3 = cv2.merge([mask, mask, mask]) / 255.0

        # Blend
        # Performs a simple weighted average blend between the warped source and the target frame.
        blended = (warped_src.astype(np.float32) * mask3 + frame.astype(np.float32) * (1 - mask3)).astype(np.uint8)

        # Returns the final blended frame.
        return blended


# Checks if the script is being run directly (not imported as a module).
if __name__ == "__main__":
    # Creates the main Tkinter window instance.
    root = Tk()
    # Creates an instance of the FaceSwapApp, passing the root window.
    app = FaceSwapApp(root)
    # Starts the Tkinter event loop, making the application run.
    root.mainloop()
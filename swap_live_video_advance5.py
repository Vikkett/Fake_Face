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

        # 🔹 Limiter la taille maximale à 512x512
        max_size = 512
        h, w = image.shape[:2]
        if h > max_size or w > max_size:
            scale = min(max_size / h, max_size / w)
            image = cv2.resize(image, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)

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

import cv2
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import numpy as np
import time

class WebcamAppFixed:
    def __init__(self, root):
        self.root = root
        self.root.title("Konix Webcam ")
        
        # Configuration initiale
        self.target_fps = 25
        self.display_size = (640, 480)
        
        # Initialisation webcam
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Erreur", "Webcam non disponible")
            self.root.destroy()
            return
        
        # Paramètres de réglage
        self.brightness = 128
        self.contrast = 128
        self.sharpness = 0
        
        # Configuration initiale
        self.setup_camera()
        self.create_widgets()
        
        # Démarrer la capture
        self.running = True
        self.update_frame()

    def setup_camera(self):
        """Configure les paramètres de la webcam"""
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.display_size[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.display_size[1])
        self.cap.set(cv2.CAP_PROP_FPS, self.target_fps)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)

    def create_widgets(self):
        """Crée l'interface utilisateur"""
        # Frame vidéo
        self.video_label = ttk.Label(self.root)
        self.video_label.pack(pady=10)
        
        # Cadre de contrôle
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Luminosité
        ttk.Label(control_frame, text="Luminosité").grid(row=0, column=0)
        self.bright_slider = ttk.Scale(control_frame, from_=0, to=255)
        self.bright_slider.set(self.brightness)
        self.bright_slider.grid(row=1, column=0, padx=5)
        self.bright_slider.bind("<Motion>", lambda e: self.set_brightness())
        
        # Contraste
        ttk.Label(control_frame, text="Contraste").grid(row=0, column=1)
        self.contrast_slider = ttk.Scale(control_frame, from_=0, to=255)
        self.contrast_slider.set(self.contrast)
        self.contrast_slider.grid(row=1, column=1, padx=5)
        self.contrast_slider.bind("<Motion>", lambda e: self.set_contrast())
        
        # Netteté
        ttk.Label(control_frame, text="Netteté").grid(row=0, column=2)
        self.sharp_slider = ttk.Scale(control_frame, from_=0, to=100)
        self.sharp_slider.set(self.sharpness)
        self.sharp_slider.grid(row=1, column=2, padx=5)
        self.sharp_slider.bind("<Motion>", lambda e: self.set_sharpness())
        
        # Bouton Quitter
        ttk.Button(control_frame, text="Quitter", command=self.quit).grid(row=0, column=3, rowspan=2, padx=10)

    def set_brightness(self):
        self.brightness = float(self.bright_slider.get())

    def set_contrast(self):
        self.contrast = float(self.contrast_slider.get())

    def set_sharpness(self):
        self.sharpness = float(self.sharp_slider.get())

    def update_frame(self):
        """Mise à jour optimisée de l'image"""
        if not self.running:
            return
            
        start_time = time.time()
        
        # Lire un frame
        ret, frame = self.cap.read()
        if not ret:
            self.root.after(10, self.update_frame)
            return
        
        try:
            # Appliquer les réglages
            frame = cv2.convertScaleAbs(frame,
                                      alpha=self.contrast/128,
                                      beta=self.brightness-128)
            
            # Appliquer la netteté
            if self.sharpness > 0:
                kernel = np.array([[-1, -1, -1],
                                 [-1, 9 + self.sharpness/20, -1],
                                 [-1, -1, -1]])
                frame = cv2.filter2D(frame, -1, kernel)
            
            # Redimensionner et convertir
            frame = cv2.resize(frame, self.display_size)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = ImageTk.PhotoImage(image=Image.fromarray(frame))
            
            # Mettre à jour l'affichage
            self.video_label.config(image=img)
            self.video_label.image = img
            
        except Exception as e:
            print(f"Erreur: {e}")
        
        # Contrôle du FPS
        elapsed = (time.time() - start_time) * 1000
        delay = max(1, int(1000/self.target_fps - elapsed))
        self.root.after(delay, self.update_frame)

    def quit(self):
        """Arrêt propre"""
        self.running = False
        if self.cap.isOpened():
            self.cap.release()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = WebcamAppFixed(root)
    root.mainloop()
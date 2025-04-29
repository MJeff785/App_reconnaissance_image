import cv2
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
import time

class CameraInterface:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Prendre une Photo")
        self.window.geometry("700x600")
        
        # Affichage de la caméra
        self.camera_frame = ttk.Frame(self.window)
        self.camera_frame.pack(pady=10)
        
        self.camera_label = ttk.Label(self.camera_frame)
        self.camera_label.pack()
        
        # Cadre de saisie du nom
        name_frame = ttk.Frame(self.window)
        name_frame.pack(pady=5)
        
        ttk.Label(name_frame, text="Nom de la photo:").pack(side='left', padx=5)
        self.name_entry = ttk.Entry(name_frame, width=30)
        self.name_entry.pack(side='left', padx=5)
        
        # Cadre des boutons
        button_frame = ttk.Frame(self.window)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Prendre Photo", 
                  command=self.take_photo).pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Quitter", 
                  command=self.close_camera).pack(side='left', padx=5)
        
        self.cap = None
        self.start_camera()

    def take_photo(self):
        if self.cap is not None:
            ret, frame = self.cap.read()
            if ret:
                try:
                    # Créer le répertoire photos s'il n'existe pas
                    if not os.path.exists('photos'):
                        os.makedirs('photos')
                    
                    # Obtenir le nom de la photo depuis le champ de saisie
                    photo_name = self.name_entry.get().strip()
                    if not photo_name:
                        photo_name = time.strftime("%Y%m%d-%H%M%S")
                    
                    # Sauvegarder la photo avec le nom et l'horodatage
                    timestamp = time.strftime("%Y%m%d-%H%M%S")
                    photo_path = os.path.join('photos', f'{photo_name}_{timestamp}.jpg')
                    cv2.imwrite(photo_path, frame)
                    
                    messagebox.showinfo("Succès", f"Photo sauvegardée: {photo_path}")
                    self.name_entry.delete(0, 'end')  # Effacer le champ après la sauvegarde
                    
                except Exception as e:
                    messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde: {str(e)}")
    
    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.update_camera()

    def update_camera(self):
        if self.cap is not None:
            ret, frame = self.cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(frame_rgb)
                image = image.resize((640, 480))
                self.photo = ImageTk.PhotoImage(image=image)
                
                self.camera_label.configure(image=self.photo)
                
                self.window.after(10, self.update_camera)
    
    def close_camera(self):
        if self.cap is not None:
            self.cap.release()
        self.window.destroy()

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    camera = CameraInterface()
    camera.run()
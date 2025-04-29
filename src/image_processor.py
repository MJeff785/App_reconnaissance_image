import cv2
import numpy as np
from PIL import Image
import os

class ImageProcessor:
    def __init__(self):
        # Utiliser le fichier cascade local au lieu du chemin d'installation d'OpenCV
        cascade_path = os.path.join(os.path.dirname(__file__), 'cascades', 'haarcascade_frontalface_default.xml')
        if not os.path.exists(cascade_path):
            raise FileNotFoundError(f"Haar cascade file not found at: {cascade_path}")
            
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        if self.face_cascade.empty():
            raise ValueError("Failed to load Haar cascade classifier")
    
    def detect_face(self, image_input):
        # Gérer à la fois les chemins de fichiers et les tableaux numpy
        if isinstance(image_input, str):
            image = cv2.imread(image_input)
            if image is None:
                raise ValueError("Unable to read image file")
        else:
            image = image_input
            
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) == 0:
            raise ValueError("No face detected in the image")
        elif len(faces) > 1:
            raise ValueError("Multiple faces detected in the image")
        
        return faces[0]  # Returns (x, y, w, h)
    
    def extract_features(self, image_input, face_coords):
        # Gérer à la fois les chemins de fichiers et les tableaux numpy
        if isinstance(image_input, str):
            image = cv2.imread(image_input)
        else:
            image = image_input
            
        x, y, w, h = face_coords
        face = image[y:y+h, x:x+w]
        face_gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
        face_resized = cv2.resize(face_gray, (128, 128))
        return face_resized.flatten().tolist()
    
    def save_face_image(self, image_path, student_data):
        # Créer le répertoire principal s'il n'existe pas
        if not os.path.exists('faces_imgs'):
            os.makedirs('faces_imgs')
        
        # Créer le répertoire de la classe (remplacer les espaces par des underscores)
        class_name = student_data['classe_nom'].replace(' ', '_')
        class_dir = os.path.join('faces_imgs', class_name)
        if not os.path.exists(class_dir):
            os.makedirs(class_dir)
        
        # Créer le répertoire de l'étudiant
        student_name = f"{student_data['nom']}_{student_data['prenom']}"
        student_name = "".join(c for c in student_name if c.isalnum() or c in ('_', '-')).lower()
        student_dir = os.path.join(class_dir, student_name)
        if not os.path.exists(student_dir):
            os.makedirs(student_dir)
        
        # Trouver le prochain numéro disponible pour l'image
        i = 1
        while True:
            new_filename = f"{student_name}{i}.jpg"
            new_path = os.path.join(student_dir, new_filename)
            if not os.path.exists(new_path):
                break
            i += 1
        
        # Copier et redimensionner l'image
        image = Image.open(image_path)
        image = image.resize((200, 200))
        image.save(new_path)
        
        return new_path
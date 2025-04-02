import cv2
import numpy as np
from PIL import Image
import os

class ImageProcessor:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
    
    def detect_face(self, image_input):
        # Handle both file paths and numpy arrays
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
        # Handle both file paths and numpy arrays
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
        # Create main directory if it doesn't exist
        if not os.path.exists('faces_imgs'):
            os.makedirs('faces_imgs')
        
        # Create class directory (replace spaces with underscores)
        class_name = student_data['classe_nom'].replace(' ', '_')
        class_dir = os.path.join('faces_imgs', class_name)
        if not os.path.exists(class_dir):
            os.makedirs(class_dir)
        
        # Create student directory
        student_name = f"{student_data['nom']}_{student_data['prenom']}"
        student_name = "".join(c for c in student_name if c.isalnum() or c in ('_', '-')).lower()
        student_dir = os.path.join(class_dir, student_name)
        if not os.path.exists(student_dir):
            os.makedirs(student_dir)
        
        # Find next available number for image
        i = 1
        while True:
            new_filename = f"{student_name}{i}.jpg"
            new_path = os.path.join(student_dir, new_filename)
            if not os.path.exists(new_path):
                break
            i += 1
        
        # Copy and resize image
        image = Image.open(image_path)
        image = image.resize((200, 200))
        image.save(new_path)
        
        return new_path
import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import pickle
import os

class FaceRecognition:
    def __init__(self, db_connection, image_processor):
        self.db = db_connection
        self.image_processor = image_processor
        self.cap = None
        
    def setup_ui(self, parent_frame):
        self.parent_frame = parent_frame
        
        # Camera display
        self.camera_label = ttk.Label(parent_frame)
        self.camera_label.pack(pady=10)
        
        # Confidence display
        self.confidence_label = ttk.Label(parent_frame, text="Correspondance: ---%", font=('Arial', 12))
        self.confidence_label.pack(pady=5)
        
        # Capture button
        ttk.Button(parent_frame, text="Capturer", 
                  command=self.capture_face).pack(pady=10)
        
        # Start camera
        self.start_camera()
    
    def update_camera(self):
        if self.cap is not None:
            ret, frame = self.cap.read()
            if ret:
                try:
                    # Process face and update confidence
                    face_coords = self.image_processor.detect_face(frame)
                    face_features = self.image_processor.extract_features(frame, face_coords)
                    
                    # Get database faces and find best match
                    results = self.db.execute_query("""
                        SELECT e.nom_famille, e.prenom, f.face_encoding, c.nom_classe
                        FROM Etudiants e
                        JOIN FaceFeatures f ON e.id = f.etudiant_id
                        JOIN Classe c ON e.id_classe = c.id
                    """)
                    
                    highest_confidence = 0
                    best_name = ""
                    
                    for result in results:
                        try:
                            stored_encoding = np.frombuffer(result[2], dtype=np.float64)
                            confidence = self.compare_faces(face_features, stored_encoding)
                            if confidence > highest_confidence:
                                highest_confidence = confidence
                                best_name = f"{result[1]} {result[0]}"
                        except Exception as e:
                            print(f"Error processing encoding: {e}")
                    
                    # Update confidence label
                    self.confidence_label.config(
                        text=f"Correspondance ({best_name}): {highest_confidence:.1f}%",
                        foreground='green' if highest_confidence > 60 else 'red'
                    )
                except:
                    # Reset confidence if no face detected
                    self.confidence_label.config(text="Correspondance: ---%", foreground='black')
                
                # Update camera display
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(frame_rgb)
                image = image.resize((640, 480))
                self.photo = ImageTk.PhotoImage(image=image)  # Store as instance variable
                
                self.camera_label.configure(image=self.photo)
                
                self.parent_frame.after(10, self.update_camera)
    
    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.update_camera()
    
    def process_image(self, image_path):
        face_coords = self.image_processor.detect_face(image_path)
        return {
            'path': image_path,
            'coords': face_coords,
            'encoding': self.image_processor.extract_features(image_path, face_coords)
        }
    
    def save_student(self, student_data, image_data):
        # Save image to directory
        new_image_path = self.image_processor.save_face_image(
            image_data['path'], 
            student_data
        )
        
        # Update image path
        image_data['path'] = new_image_path
        
        # Save to database
        self.db.save_student_face(student_data, image_data)
    
    def capture_face(self):
        if self.cap is not None:
            ret, frame = self.cap.read()
            if ret:
                try:
                    # Detect and process face
                    face_coords = self.image_processor.detect_face(frame)
                    face_features = self.image_processor.extract_features(frame, face_coords)
                    
                    # Get database faces
                    results = self.db.execute_query("""
                        SELECT e.nom_famille, e.prenom, f.face_encoding, c.nom_classe
                        FROM Etudiants e
                        JOIN FaceFeatures f ON e.id = f.etudiant_id
                        JOIN Classe c ON e.id_classe = c.id
                    """)
                    
                    # Find best match
                    best_match = None
                    highest_confidence = 0
                    
                    for result in results:
                        stored_encoding = pickle.loads(result[2])
                        confidence = self.compare_faces(face_features, stored_encoding)
                        
                        if confidence > highest_confidence:
                            highest_confidence = confidence
                            best_match = result
                    
                    # Show results
                    if highest_confidence > 60:
                        messagebox.showinfo("Reconnaissance Réussie", 
                            f"Étudiant identifié :\n"
                            f"Nom : {best_match[0] if best_match else 'Non reconnu'}\n"
                            f"Prénom : {best_match[1] if best_match else 'Non reconnu'}\n"
                            f"Classe : {best_match[3] if best_match else 'Non reconnu'}\n"
                            f"Confiance : {highest_confidence:.2f}%"
                        )
                    else:
                        messagebox.showinfo("Non Reconnu", 
                            "Aucune correspondance trouvée avec un niveau de confiance suffisant."
                        )
                    
                except Exception as e:
                    messagebox.showerror("Erreur", str(e))
    
    def compare_faces(self, face1_features, face2_features):
        try:
            # Ensure both arrays have the same shape
            face1 = np.array(face1_features).flatten()
            face2 = np.array(face2_features).flatten()
            
            # Resize shorter array to match longer one if needed
            if len(face1) != len(face2):
                target_size = max(len(face1), len(face2))
                if len(face1) < target_size:
                    face1 = np.resize(face1, target_size)
                if len(face2) < target_size:
                    face2 = np.resize(face2, target_size)
            
            correlation = np.corrcoef(face1, face2)[0, 1]
            confidence = (correlation + 1) * 50
            return confidence
            
        except Exception as e:
            print(f"Error in compare_faces: {e}")
            return 0  # Return 0 confidence on error
    
    def stop_camera(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
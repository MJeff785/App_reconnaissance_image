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
        if self.cap is not None and not hasattr(self, '_stopping'):
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
                            # Use pickle.loads instead of np.frombuffer
                            stored_encoding = pickle.loads(result[2])
                            confidence = self.compare_faces(face_features, stored_encoding)
                            if confidence > highest_confidence:
                                highest_confidence = confidence
                                best_name = f"{result[1]} {result[0]}"
                        except Exception as e:
                            print(f"Error processing encoding: {e}")
                    
                    # Update confidence label if it still exists
                    if hasattr(self, 'confidence_label') and self.confidence_label.winfo_exists():
                        self.confidence_label.config(
                            text=f"Correspondance ({best_name}): {highest_confidence:.1f}%",
                            foreground='green' if highest_confidence > 60 else 'red'
                        )
                except ValueError:
                    # No face detected - update label if it exists
                    if hasattr(self, 'confidence_label') and self.confidence_label.winfo_exists():
                        self.confidence_label.config(text="Aucun visage détecté", foreground='black')
                except Exception as e:
                    print(f"Error in face recognition: {e}")
                
                # Update camera display
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(frame_rgb)
                image = image.resize((640, 480))
                self.photo = ImageTk.PhotoImage(image=image)
                
                if hasattr(self, 'camera_label') and self.camera_label.winfo_exists():
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
            
            # Check for zero variance and handle edge cases
            std1 = np.std(face1)
            std2 = np.std(face2)
            if std1 < 1e-7 or std2 < 1e-7:
                return 0  # Return 0 confidence if either array has near-zero variance
            
            # Normalize the arrays before correlation
            face1_norm = (face1 - np.mean(face1)) / std1
            face2_norm = (face2 - np.mean(face2)) / std2
            
            # Calculate correlation using cosine similarity for better accuracy
            norm1 = np.linalg.norm(face1_norm)
            norm2 = np.linalg.norm(face2_norm)
            if norm1 == 0 or norm2 == 0:
                return 0
                
            cosine_similarity = np.dot(face1_norm, face2_norm) / (norm1 * norm2)
            confidence = (cosine_similarity + 1) * 50
            return max(0, min(100, confidence))
            
        except Exception as e:
            print(f"Error in compare_faces: {e}")
            return 0
    
    def stop_camera(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
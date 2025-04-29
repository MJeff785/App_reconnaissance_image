import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import pickle
import os
import time  # Ajout de l'import time
import datetime  # Ajout pour formater la date et l'heure

class FaceRecognition:
    def __init__(self, db_connection, image_processor):
        self.db = db_connection
        self.image_processor = image_processor
        self.cap = None
        self.last_detection_time = 0  # Initialize the last detection time
    
    def setup_ui(self, parent_frame, ui_manager):
        self.parent_frame = parent_frame
        self.ui_manager = ui_manager  # Store UI manager reference
        
        # Affichage de la caméra
        self.camera_label = ttk.Label(parent_frame)
        self.camera_label.pack(pady=10)
        
        # Démarrer la caméra
        self.start_camera()

    def update_camera(self):
        if self.cap is not None and not hasattr(self, '_stopping'):
            ret, frame = self.cap.read()
            if ret:
                try:
                    current_time = time.time()
                    # Process face and update confidence
                    face_coords = self.image_processor.detect_face(frame)
                    face_features = self.image_processor.extract_features(frame, face_coords)
                    
                    # Get database faces and find best match
                    results = self.db.execute_query("""
                        SELECT e.id, e.nom_famille, e.prenom, f.face_encoding, c.nom_classe
                        FROM Etudiants e
                        JOIN FaceFeatures f ON e.id = f.etudiant_id
                        JOIN Classe c ON e.id_classe = c.id
                    """)
                    
                    highest_confidence = 0
                    best_match = None
                    
                    for result in results:
                        try:
                            stored_encoding = pickle.loads(result[3])
                            confidence = self.compare_faces(face_features, stored_encoding)
                            if confidence > highest_confidence:
                                highest_confidence = confidence
                                best_match = result
                        except Exception as e:
                            print(f"Error processing encoding: {e}")
                    
                    # Mark presence if confidence > 95%
                    if highest_confidence > 95 and best_match:
                        # Vérifier le délai depuis la dernière détection (3 secondes minimum)
                        if current_time - self.last_detection_time > 3:
                            # Obtenir la date et l'heure formatées (sans secondes)
                            now = datetime.datetime.now()
                            formatted_date = now.strftime("%d/%m/%Y")
                            formatted_time = now.strftime("%H:%M")
                            
                            student_data = {
                                'id': best_match[0],
                                'nom': best_match[1],
                                'prenom': best_match[2],
                                'classe_nom': best_match[4],
                                'date': formatted_date,
                                'heure': formatted_time
                            }
                            if hasattr(self, 'ui_manager'):
                                self.ui_manager.mark_student_present(student_data)
                                self.last_detection_time = current_time
                            
                except ValueError:
                    pass
                except Exception as e:
                    print(f"Error in face recognition: {e}")
                
                # Update camera display
                try:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    image = Image.fromarray(frame_rgb)
                    image = image.resize((640, 480))
                    self.current_photo = ImageTk.PhotoImage(image=image)
                    self.camera_label.configure(image=self.current_photo)
                except Exception as e:
                    print(f"Error updating camera display: {e}")
                
                # Schedule next update only once
                if hasattr(self, 'camera_label') and self.camera_label.winfo_exists():
                    self.camera_label.after(10, self.update_camera)
    
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
                        SELECT e.id, e.nom_famille, e.prenom, f.face_encoding, c.nom_classe
                        FROM Etudiants e
                        JOIN FaceFeatures f ON e.id = f.etudiant_id
                        JOIN Classe c ON e.id_classe = c.id
                    """)
                    
                    # Find best match
                    best_match = None
                    highest_confidence = 0
                    
                    for result in results:
                        stored_encoding = pickle.loads(result[3])
                        confidence = self.compare_faces(face_features, stored_encoding)
                        
                        if confidence > highest_confidence:
                            highest_confidence = confidence
                            best_match = result
                    
                    # Show results and update presence if confidence is high enough
                    if highest_confidence > 60:
                        # Obtenir la date et l'heure formatées au moment de la capture
                        now = datetime.datetime.now()
                        formatted_date = now.strftime("%d/%m/%Y")
                        formatted_time = now.strftime("%H:%M")
                        
                        student_data = {
                            'id': best_match[0],
                            'nom': best_match[1],
                            'prenom': best_match[2],
                            'classe_nom': best_match[4],
                            'date': formatted_date,
                            'heure': formatted_time
                        }
                        # Call the UI manager's method directly
                        if hasattr(self, 'ui_manager'):
                            self.ui_manager.mark_student_present(student_data)
                        
                        messagebox.showinfo("Reconnaissance Réussie", 
                            f"Étudiant identifié :\n"
                            f"Nom : {best_match[1]}\n"
                            f"Prénom : {best_match[2]}\n"
                            f"Classe : {best_match[4]}\n"
                            f"Date : {formatted_date}\n"
                            f"Heure : {formatted_time}\n"
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
            face1 = np.array(face1_features).flatten()
            face2 = np.array(face2_features).flatten()
            
            # Augmenter le seuil de normalisation
            std1 = np.std(face1)
            std2 = np.std(face2)
            if std1 < 1e-6 or std2 < 1e-6:  # Augmenté de 1e-7 à 1e-6
                return 0
            
            face1_norm = (face1 - np.mean(face1)) / std1
            face2_norm = (face2 - np.mean(face2)) / std2
            
            # Ajout d'une vérification supplémentaire de similarité
            if np.mean(np.abs(face1_norm - face2_norm)) > 0.5:
                return 0
                
            cosine_similarity = np.dot(face1_norm, face2_norm) / (np.linalg.norm(face1_norm) * np.linalg.norm(face2_norm))
            confidence = (cosine_similarity + 1) * 50
            
            # Ajout d'un facteur de pénalité pour les correspondances faibles
            if confidence < 75:
                confidence *= 0.8
                
            return max(0, min(100, confidence))
            
        except Exception as e:
            print(f"Error in compare_faces: {e}")
            return 0
    
    def stop_camera(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def on_student_detected(self, student_data):
        # When a student is detected, call the UIManager's method
        if hasattr(self, 'ui_manager'):
            self.ui_manager.on_student_detected(student_data)
            
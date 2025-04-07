import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import cv2
import numpy as np
import pickle
from face_recognition import FaceRecognition  # Add this import
from styles import ModernStyle

class UIManager:
    def __init__(self, db_connection, image_processor, face_db):
        self.db = db_connection
        self.image_processor = image_processor
        self.face_db = face_db
        self.face_recognition = FaceRecognition(db_connection, image_processor)
        
        self.window = tk.Tk()
        self.window.title("Reconnaissance Faciale - Lycée Melkior")
        self.window.geometry("1000x800")
        
        # Apply modern styles
        ModernStyle.apply(self.window)
        
        # Main container
        self.main_frame = ttk.Frame(self.window, style='Modern.TFrame', padding=20)
        self.main_frame.pack(expand=True, fill='both')
        
        # Content frame
        self.content_frame = ttk.Frame(self.main_frame, style='Surface.TFrame')
        self.content_frame.pack(expand=True, fill='both', pady=20)
        
        # Create navigation and show welcome screen
        self.create_nav_buttons()
        self.show_welcome()

    def create_nav_buttons(self):
        nav_frame = ttk.Frame(self.main_frame, style='Modern.TFrame')
        nav_frame.pack(fill='x', pady=20)
        
        # Center buttons with grid
        nav_frame.grid_columnconfigure(0, weight=1)
        nav_frame.grid_columnconfigure(4, weight=1)
        
        buttons = [
            ("Ajouter Élève", self.show_add_student),
            ("Rajouter Image", self.show_add_image),
            ("Activer Reconnaissance", self.show_recognition)
        ]
        
        for i, (text, command) in enumerate(buttons, 1):
            ttk.Button(nav_frame, 
                      text=text,
                      command=command,
                      style='Modern.TButton').grid(row=0, column=i, padx=10)

    def show_welcome_screen(self):
        self.clear_content()
        
        # Create a modern welcome frame
        welcome_frame = ttk.Frame(self.content_frame, style='Modern.TFrame')
        welcome_frame.pack(expand=True, fill='both')
        
        # Add a title
        title_label = ttk.Label(
            welcome_frame,
            text="Système de Reconnaissance Faciale",
            font=('Helvetica', 24, 'bold'),
            style='Modern.TLabel'
        )
        title_label.pack(pady=(50, 20))
        
        # Add a subtitle
        subtitle_label = ttk.Label(
            welcome_frame,
            text="Lycée Melkior Garré",
            font=('Helvetica', 18),
            style='Modern.TLabel'
        )
        subtitle_label.pack(pady=(0, 40))
        
        # Add instructions
        instructions_label = ttk.Label(
            welcome_frame,
            text="Sélectionnez une option dans le menu ci-dessus pour commencer",
            font=('Helvetica', 12),
            style='Modern.TLabel'
        )
        instructions_label.pack(pady=20)
    
    def show_add_image(self):
        self.clear_content()
        
        # Create frame for student selection
        select_frame = ttk.LabelFrame(self.content_frame, text="Sélectionner l'étudiant", padding="10")
        select_frame.pack(fill='x', pady=10)
        
        # Get all students
        students = self.db.execute_query("""
            SELECT e.id, e.nom_famille, e.prenom, c.nom_classe 
            FROM Etudiants e
            JOIN Classe c ON e.id_classe = c.id
            ORDER BY nom_famille, prenom
        """)
        
        # Create student selection combobox
        ttk.Label(select_frame, text="Étudiant:").pack(pady=5)
        self.student_combo = ttk.Combobox(select_frame, 
            values=[f"{s[0]} - {s[1]} {s[2]} ({s[3]})" for s in students],
            state='readonly')
        self.student_combo.pack(pady=5)
        
        # Create preview frame
        self.create_preview()
        
        # Create buttons
        btn_frame = ttk.Frame(self.content_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Sélectionner image", 
                   command=self.select_additional_image).pack(side='left', padx=5)
        
        ttk.Button(btn_frame, text="Enregistrer", 
                   command=self.save_additional_image).pack(side='left', padx=5)
    
    def select_additional_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg")]
        )
        if file_path:
            try:
                self.current_image = self.face_recognition.process_image(file_path)
                
                # Show preview
                preview = Image.open(file_path)
                preview.thumbnail((300, 300))
                photo = ImageTk.PhotoImage(preview)
                self.preview_label.configure(image=photo)
                # Store photo reference to prevent garbage collection
                setattr(self.preview_label, '_photo', photo)
                
            except Exception as e:
                messagebox.showerror("Erreur", str(e))
    
    def save_additional_image(self):
        if not hasattr(self, 'current_image'):
            messagebox.showerror("Erreur", "Veuillez sélectionner une image")
            return
            
        if not self.student_combo.get():
            messagebox.showerror("Erreur", "Veuillez sélectionner un étudiant")
            return
            
        try:
            # Get student ID from combo selection
            student_id = self.student_combo.get().split(' - ')[0]
            
            # Get student data
            student = self.db.execute_query("""
                SELECT e.nom_famille, e.prenom, c.nom_classe
                FROM Etudiants e
                JOIN Classe c ON e.id_classe = c.id
                WHERE e.id = %s
            """, (student_id,))[0]
            
            # Prepare student data for saving
            student_data = {
                'nom': student[0],
                'prenom': student[1],
                'classe_nom': student[2]
            }
            
            # Save new image
            new_image_path = self.image_processor.save_face_image(
                self.current_image['path'],
                student_data
            )
            
            # Save to database
            self.db.execute_query("""
                INSERT INTO FaceFeatures (etudiant_id, image_path, face_encoding)
                VALUES (%s, %s, %s)
            """, (
                student_id,
                new_image_path,
                pickle.dumps(self.current_image['encoding'])
            ))
            
            messagebox.showinfo("Succès", "Image ajoutée avec succès")
            
            # Clear the form
            self.student_combo.set('')
            self.preview_label.configure(image='')
            if hasattr(self, 'current_image'):
                del self.current_image
            
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
    
    def show_welcome(self):
        self.clear_content()
        welcome_label = ttk.Label(
            self.content_frame, 
            text="Bienvenue dans l'application de reconnaissance faciale\n\nChoisissez une option ci-dessus",
            font=('Arial', 14)
        )
        welcome_label.pack(expand=True)
    
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_add_student(self):
        self.clear_content()
        self.create_form()
        self.create_preview()
        self.create_buttons()
    
    def show_recognition(self):
        self.clear_content()
        self.face_recognition.setup_ui(self.content_frame)
    
    def create_form(self):
        form_frame = ttk.LabelFrame(
            self.content_frame, 
            text="Informations de l'étudiant",
            style='Modern.TLabelframe'
        )
        form_frame.pack(fill='x', pady=20, padx=50)
        
        # Configure grid
        form_frame.columnconfigure(1, weight=1)
        
        # Form fields with grid layout
        ttk.Label(form_frame, text="Nom:", style='Modern.TLabel').grid(
            row=0, column=0, pady=10, padx=10, sticky='e')
        self.nom_entry = ttk.Entry(form_frame, font=('Helvetica', 11))
        self.nom_entry.grid(row=0, column=1, pady=10, padx=10, sticky='ew')
        
        ttk.Label(form_frame, text="Prénom:", style='Modern.TLabel').grid(
            row=1, column=0, pady=10, padx=10, sticky='e')
        self.prenom_entry = ttk.Entry(form_frame, font=('Helvetica', 11))
        self.prenom_entry.grid(row=1, column=1, pady=10, padx=10, sticky='ew')
        
        ttk.Label(form_frame, text="Classe:", style='Modern.TLabel').grid(
            row=2, column=0, pady=10, padx=10, sticky='e')
        classes = self.db.execute_query("SELECT id, nom_classe FROM Classe")
        self.classe_combo = ttk.Combobox(
            form_frame, 
            values=[f"{c[0]} - {c[1]}" for c in classes],
            state='readonly',
            font=('Helvetica', 11)
        )
        self.classe_combo.grid(row=2, column=1, pady=10, padx=10, sticky='ew')
        
        ttk.Label(form_frame, text="Année scolaire:", style='Modern.TLabel').grid(
            row=3, column=0, pady=10, padx=10, sticky='e')
        self.annee_combo = ttk.Combobox(
            form_frame, 
            values=['2023-2024', '2024-2025', '2025-2026'],
            state='readonly',
            font=('Helvetica', 11)
        )
        self.annee_combo.set('2023-2024')
        self.annee_combo.grid(row=3, column=1, pady=10, padx=10, sticky='ew')
    
    def create_preview(self):
        self.preview_frame = ttk.LabelFrame(self.content_frame, text="Aperçu de l'image", padding="10")
        self.preview_frame.pack(fill='both', expand=True, pady=10)
        
        self.preview_label = ttk.Label(self.preview_frame)
        self.preview_label.pack(pady=10)
    
    def create_buttons(self):
        btn_frame = ttk.Frame(self.content_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Sélectionner image", 
                   command=self.select_image).pack(side='left', padx=5)
        
        ttk.Button(btn_frame, text="Enregistrer", 
                   command=self.save_student).pack(side='left', padx=5)
    
    def select_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg")]
        )
        if file_path:
            try:
                self.current_image = self.face_recognition.process_image(file_path)
                
                # Show preview
                preview = Image.open(file_path)
                preview.thumbnail((300, 300))
                photo = ImageTk.PhotoImage(preview)
                self.preview_label.configure(image=photo)
                # Store photo reference to prevent garbage collection
                setattr(self.preview_label, '_photo', photo)
                
            except Exception as e:
                messagebox.showerror("Erreur", str(e))
    
    def save_student(self):
        if not all([self.nom_entry.get(), self.prenom_entry.get(), 
                   self.classe_combo.get(), self.annee_combo.get()]):
            messagebox.showerror("Erreur", "Tous les champs sont obligatoires")
            return
            
        if not hasattr(self, 'current_image'):
            messagebox.showerror("Erreur", "Veuillez sélectionner une image")
            return
        
        try:
            classe_info = self.classe_combo.get().split(' - ')
            student_data = {
                'nom': self.nom_entry.get().strip(),
                'prenom': self.prenom_entry.get().strip(),
                'classe_id': classe_info[0],
                'classe_nom': classe_info[1],
                'annee': self.annee_combo.get()
            }
            
            self.face_db.save_student_face(student_data, self.current_image)
            messagebox.showinfo("Succès", "Étudiant enregistré avec succès!")
            self.clear_form()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement: {str(e)}")
    
    def clear_form(self):
        self.nom_entry.delete(0, 'end')
        self.prenom_entry.delete(0, 'end')
        self.classe_combo.set('')
        self.preview_label.configure(image='')
        if hasattr(self, 'current_image'):
            del self.current_image
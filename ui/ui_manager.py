import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import cv2
import numpy as np
import pickle
from src.face_recognition import FaceRecognition  # Add this import
from styles import ModernStyle

class UIManager:
    def __init__(self, db_connection, image_processor, face_db):
        self.db = db_connection
        self.image_processor = image_processor
        self.face_db = face_db
        self.face_recognition = FaceRecognition(db_connection, image_processor)
        self.present_students = []  # Liste des élèves présents
        self.window = tk.Tk()
        self.window.title("EduFace Manager")
        self.window.geometry("1000x800")
        
        # Set window icon
        try:
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'edu_face_logo.png')
            if os.path.exists(icon_path):
                icon_image = Image.open(icon_path)
                icon_image = icon_image.resize((32, 32))
                icon_photo = ImageTk.PhotoImage(icon_image)
                self.window.iconphoto(False, icon_photo)
                self._icon_photo = icon_photo  # Keep a reference
        except Exception as e:
            print(f"Error loading window icon: {e}")
        
        # Apply modern styles
        ModernStyle.apply(self.window)
        
        # Main container
        self.main_frame = ttk.Frame(self.window, style='Modern.TFrame', padding=20)
        self.main_frame.pack(expand=True, fill='both')
        self.show_present_btn = ttk.Button(self.main_frame, text="Présents", command=self.show_present_students_window)
        self.show_present_btn.pack(anchor='ne', padx=10, pady=5)
        
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
        
        # Create welcome frame
        welcome_frame = ttk.Frame(self.content_frame, style='Modern.TFrame')
        welcome_frame.pack(expand=True)
        
        # Add title
        welcome_label = ttk.Label(
            welcome_frame,
            text="Bienvenue dans EduFace Manager",
            style='Title.TLabel'
        )
        welcome_label.pack(pady=(20, 10))
        
        # Add logo
        try:
            logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'edu_face_logo.png')
            logo_image = Image.open(logo_path)
            logo_image = logo_image.resize((400, 400))  # Adjust size as needed
            self.logo_photo = ImageTk.PhotoImage(logo_image)
            logo_label = ttk.Label(welcome_frame, image=self.logo_photo)
            logo_label.pack(pady=(0, 20))
        except Exception as e:
            print(f"Error loading logo: {e}")
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
        # Pass self as the UI manager reference
        self.face_recognition.setup_ui(self.content_frame, self)
    
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

    def mark_student_present(self, student_data):
        # Définir les horaires de début de cours pour différentes plages horaires
        horaires_cours = {
            "Matin": {"debut": "08:00", "fin": "12:00"},
            "Après-midi": {"debut": "13:30", "fin": "17:30"}
        }
        
        # Obtenir l'heure actuelle
        heure_actuelle = student_data['heure']
        
        # Déterminer la période de cours actuelle
        periode_actuelle = None
        for periode, horaires in horaires_cours.items():
            if horaires["debut"] <= heure_actuelle <= horaires["fin"]:
                periode_actuelle = periode
                break
        
        # Déterminer si l'étudiant est en retard
        est_en_retard = False
        if periode_actuelle:
            # Tolérance de 10 minutes (à ajuster selon les règles de l'établissement)
            heure_limite = horaires_cours[periode_actuelle]["debut"]
            
            # Convertir les heures en minutes depuis minuit pour faciliter la comparaison
            h_limite, m_limite = map(int, heure_limite.split(':'))
            h_actuelle, m_actuelle = map(int, heure_actuelle.split(':'))
            
            minutes_limite = h_limite * 60 + m_limite + 10  # 10 minutes de tolérance
            minutes_actuelle = h_actuelle * 60 + m_actuelle
            
            est_en_retard = minutes_actuelle > minutes_limite
        
        # Ajouter l'information de retard et la période au dictionnaire student_data
        student_data['periode'] = periode_actuelle if periode_actuelle else "Hors cours"
        student_data['statut'] = "Retard" if est_en_retard else "À l'heure"
        
        # Ajoute l'élève à la liste des présents s'il n'y est pas déjà
        if student_data not in self.present_students:
            self.present_students.append(student_data)
            # Optionnel : mettre à jour l'affichage
            self.update_present_list_display()

    def update_present_list_display(self):
        # Méthode pour afficher la liste des présents dans l'interface (à adapter selon votre UI)
        if not hasattr(self, 'present_listbox'):
            self.present_listbox = tk.Listbox(self.content_frame, height=10)
            self.present_listbox.pack(pady=10)
        self.present_listbox.delete(0, tk.END)
        for student in self.present_students:
            self.present_listbox.insert(tk.END, f"{student['nom']} {student['prenom']} ({student['classe_nom']})")

    # Exemple d'appel après détection (à placer dans la fonction de capture/détection)
    def on_student_detected(self, student_data):
        self.mark_student_present(student_data)
        # ... autres actions (sauvegarde, affichage, etc.) ...

    

    def show_present_students_window(self):
        # Create a new window
        window = tk.Toplevel(self.window)
        window.title("Liste des élèves présents")
        window.geometry("800x400")  # Augmenté la taille pour accommoder plus de colonnes
        
        # Create a Treeview for tabular display
        columns = ("Nom", "Prénom", "Classe", "Date", "Heure", "Période", "Statut")
        tree = ttk.Treeview(window, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col)
        tree.column("Nom", width=120)
        tree.column("Prénom", width=120)
        tree.column("Classe", width=100)
        tree.column("Date", width=80)
        tree.column("Heure", width=60)
        tree.column("Période", width=100)
        tree.column("Statut", width=80)
        
        # Insert present students with date, time and status
        for student in self.present_students:
            # Définir la couleur en fonction du statut
            tag = "retard" if student.get('statut') == "Retard" else "present"
            
            tree.insert('', tk.END, values=(
                student['nom'], 
                student['prenom'], 
                student['classe_nom'],
                student.get('date', ''),
                student.get('heure', ''),
                student.get('periode', 'Non défini'),
                student.get('statut', '')
            ), tags=(tag,))
        
        # Configurer les couleurs pour les tags
        tree.tag_configure('retard', background='#ffcccc')  # Rouge clair pour les retards
        tree.tag_configure('present', background='#ccffcc')  # Vert clair pour les présents
        
        # Ajouter une scrollbar
        scrollbar = ttk.Scrollbar(window, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        
        tree.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Optional: add a close button
        ttk.Button(window, text="Fermer", command=window.destroy).pack(pady=5)
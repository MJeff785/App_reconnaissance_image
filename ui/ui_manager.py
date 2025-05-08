import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import cv2
import numpy as np
import pickle
from src.face_recognition import FaceRecognition  # Add this import
from styles import ModernStyle
import time

class UIManager:
    def __init__(self, db_connection, image_processor, face_db):
        self.db = db_connection
        self.image_processor = image_processor
        self.face_db = face_db
        self.face_recognition = FaceRecognition(db_connection, image_processor, self)  # Passer self comme référence
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
        
        # Créer un cadre pour les contrôles
        control_frame = ttk.Frame(self.content_frame)
        control_frame.pack(fill='x', pady=10)
        
        # Ajouter le filtre de classe
        ttk.Label(control_frame, text="Filtrer par classe:").pack(side='left', padx=5)
        classes = self.db.execute_query("SELECT id, nom_classe FROM Classe")
        self.classe_filter = ttk.Combobox(
            control_frame,
            values=['Toutes les classes'] + [c[1] for c in classes],
            state='readonly',
            width=30
        )
        self.classe_filter.set('Toutes les classes')
        self.classe_filter.pack(side='left', padx=5)
        self.classe_filter.bind('<<ComboboxSelected>>', lambda e: self.update_present_list_display())
        
        # Ajouter les boutons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(side='right')
        
        ttk.Button(
            button_frame,
            text="Exporter CSV",
            command=self.export_to_csv,
            style='Modern.TButton'
        ).pack(side='right', padx=5)
        
        ttk.Button(
            button_frame,
            text="Vérifier les absents",
            command=self.check_absences,
            style='Modern.TButton'
        ).pack(side='right', padx=5)
        
        # Configuration de la caméra
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

    def mark_student_present(self, student_data):
        """Marque un étudiant comme présent et met à jour la liste des présences"""
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
        
        # Créer une clé unique pour l'étudiant
        student_key = f"{student_data['nom']}_{student_data['prenom']}_{student_data['classe_nom']}"
        
        # Vérifier si l'étudiant n'est pas déjà marqué comme présent
        if student_key not in [f"{s['nom']}_{s['prenom']}_{s['classe_nom']}" for s in self.present_students]:
            # Ajouter l'étudiant à la liste des présents
            self.present_students.append(student_data)
            
            # Enregistrer la présence dans la base de données
            self.db.execute_query("""
                INSERT INTO Presences (etudiant_id, date_presence, heure_presence, statut)
                SELECT e.id, %s, %s, %s
                FROM Etudiants e
                WHERE e.nom_famille = %s AND e.prenom = %s AND e.id_classe = %s
            """, (
                student_data['date'],
                student_data['heure'],
                student_data['statut'],  # Ajout du statut
                student_data['nom'],
                student_data['prenom'],
                student_data['classe_id']
            ))
            
            # Créer une fenêtre temporaire pour afficher la notification
            notification_window = tk.Toplevel(self.window)
            notification_window.title("Présence enregistrée")
            notification_window.geometry("400x100")
            
            # Message de confirmation
            message = f"{student_data['prenom']} {student_data['nom']} ({student_data['classe_nom']}) a été marqué comme {student_data['statut']}"
            ttk.Label(notification_window, text=message, wraplength=350).pack(pady=20)
            
            # Fermer automatiquement après 3 secondes
            notification_window.after(3000, notification_window.destroy)
            
            # Mettre à jour l'affichage des présents immédiatement
            self.update_present_list_display()
            
            print(f"Présence enregistrée pour {student_data['prenom']} {student_data['nom']}")

    def get_current_period(self):
        """Détermine la période actuelle (Matin ou Après-midi)"""
        horaires_cours = {
            "Matin": {"debut": "08:00", "fin": "12:00"},
            "Après-midi": {"debut": "13:30", "fin": "17:30"}
        }
        
        heure_actuelle = time.strftime('%H:%M')
        
        for periode, horaires in horaires_cours.items():
            if horaires["debut"] <= heure_actuelle <= horaires["fin"]:
                return periode
        return "Hors cours"

    def update_presence_status(self):
        """Met à jour le statut des présences en fonction de l'heure"""
        current_time = time.strftime('%H:%M')
        
        # Mettre à jour les statuts des présences terminées
        self.db.execute_query("""
            UPDATE Presences 
            SET statut = 'Terminé'
            WHERE date_presence = CURRENT_DATE
            AND heure_fin <= %s
            AND statut IN ('Présent', 'Retard')
        """, (current_time,))
        
        # Mettre à jour la liste d'affichage
        periode_actuelle = self.get_current_period()
        self.present_students = [s for s in self.present_students 
                               if s['periode'] == periode_actuelle]
        self.update_present_list_display()

    def update_present_list_display(self):
        # Créer la listbox si elle n'existe pas déjà
        if not hasattr(self, 'present_listbox'):
            self.present_listbox = ttk.Treeview(self.content_frame, columns=("Nom", "Prénom", "Classe", "Date", "Heure", "Statut"))
            self.present_listbox.heading("Nom", text="Nom")
            self.present_listbox.heading("Prénom", text="Prénom")
            self.present_listbox.heading("Classe", text="Classe")
            self.present_listbox.heading("Date", text="Date")
            self.present_listbox.heading("Heure", text="Heure")
            self.present_listbox.heading("Statut", text="Statut")
            
            # Masquer la colonne d'index
            self.present_listbox["show"] = "headings"
            
            # Définir les tags de couleur
            self.present_listbox.tag_configure('present', background='#90EE90')  # Vert clair
            self.present_listbox.tag_configure('retard', background='#FFD700')   # Jaune
            self.present_listbox.tag_configure('absent', background='#FFB6C6')   # Rouge clair
            
            self.present_listbox.pack(fill='both', expand=True, pady=10)
        
        try:
            # Effacer les entrées existantes
            for item in self.present_listbox.get_children():
                self.present_listbox.delete(item)
            
            # Filtrer les étudiants selon la classe sélectionnée
            filtered_students = self.present_students
            if hasattr(self, 'classe_filter') and self.classe_filter.get() != 'Toutes les classes':
                filtered_students = [s for s in self.present_students 
                               if s['classe_nom'] == self.classe_filter.get()]
            
            # Ajouter les étudiants filtrés
            for student in filtered_students:
                tag = 'present'
                if student['statut'] == 'Retard':
                    tag = 'retard'
                elif student['statut'] == 'Absent':
                    tag = 'absent'
                
                self.present_listbox.insert('', 'end', values=(
                    student['nom'],
                    student['prenom'],
                    student['classe_nom'],
                    student['date'],
                    student['heure'],
                    student['statut']
                ), tags=(tag,))
                
        except Exception as e:
            print(f"Erreur lors de la mise à jour de l'affichage: {e}")
        except tk.TclError:
            # Si le widget n'existe plus, on ne fait rien
            pass

    # Exemple d'appel après détection (à placer dans la fonction de capture/détection)
    def on_student_detected(self, student_data):
        self.mark_student_present(student_data)
        # ... autres actions (sauvegarde, affichage, etc.) 

    def check_absences(self):
        """Vérifie et marque les élèves absents"""
        # Obtenir la période actuelle
        periode_actuelle = self.get_current_period()
        if periode_actuelle == "Hors cours":
            messagebox.showinfo("Information", "Aucun cours n'est prévu à cette heure")
            return
        
        # Obtenir la date du jour
        date_actuelle = time.strftime('%Y-%m-%d')
        
        # Construire la requête SQL en fonction du filtre de classe
        classe_filter = self.classe_filter.get()
        if classe_filter == 'Toutes les classes':
            query = """
                SELECT e.id, e.nom_famille, e.prenom, c.id as classe_id, c.nom_classe
                FROM Etudiants e
                JOIN Classe c ON e.id_classe = c.id
                WHERE e.actif = 1
            """
            params = ()
        else:
            query = """
                SELECT e.id, e.nom_famille, e.prenom, c.id as classe_id, c.nom_classe
                FROM Etudiants e
                JOIN Classe c ON e.id_classe = c.id
                WHERE e.actif = 1 AND c.nom_classe = %s
            """
            params = (classe_filter,)
        
        # Récupérer tous les élèves qui devraient être présents
        eleves_attendus = self.db.execute_query(query, params) or []  # Retourne une liste vide si None
        
        if not eleves_attendus:
            messagebox.showinfo("Information", "Aucun élève trouvé pour cette classe")
            return
        
        # Vérifier les présences
        for eleve in eleves_attendus:
            eleve_present = False
            for present in self.present_students:
                if (present['nom'] == eleve[1] and 
                    present['prenom'] == eleve[2]):
                    eleve_present = True
                    break
            
            if not eleve_present:
                # Ajouter l'élève comme absent dans la base de données
                self.db.execute_query("""
                    INSERT INTO Presences (etudiant_id, date_presence, heure_presence, statut)
                    VALUES (%s, %s, %s, 'Absent')
                    ON DUPLICATE KEY UPDATE statut = 'Absent'
                """, (eleve[0], date_actuelle, time.strftime('%H:%M')))
                
                # Ajouter à la liste d'affichage
                self.present_students.append({
                    'nom': eleve[1],
                    'prenom': eleve[2],
                    'classe_id': str(eleve[3]),
                    'classe_nom': eleve[4],
                    'date': date_actuelle,
                    'heure': time.strftime('%H:%M'),
                    'statut': 'Absent',
                    'periode': periode_actuelle
                })
        
        # Mettre à jour l'affichage
        self.update_present_list_display()
        messagebox.showinfo("Information", "Vérification des absences terminée")

    def export_to_csv(self):
        """Exporte les données du tableau en CSV"""
        try:
            # Demander à l'utilisateur où sauvegarder le fichier
            file_path = filedialog.asksaveasfilename(
                defaultextension='.csv',
                filetypes=[("CSV files", "*.csv")],
                initialfile=f'presences_{time.strftime("%Y%m%d")}.csv'
            )
            
            if file_path:
                # Récupérer les en-têtes
                headers = [self.present_listbox.heading(col)["text"] 
                          for col in self.present_listbox["columns"]]
                
                # Récupérer toutes les lignes
                rows = [self.present_listbox.item(item)["values"] 
                       for item in self.present_listbox.get_children()]
                
                # Écrire dans le fichier CSV
                with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                    import csv
                    writer = csv.writer(f, delimiter=';')  # Utiliser ; comme séparateur pour Excel
                    writer.writerow(headers)
                    writer.writerows(rows)
                
                messagebox.showinfo("Succès", "Export CSV réussi!")
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'export: {str(e)}")

    

    
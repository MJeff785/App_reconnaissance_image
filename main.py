from database.connection import DatabaseConnection
from src.image_processor import ImageProcessor
from database.face_database import FaceDatabase
from ui.ui_manager import UIManager
from tkinter import messagebox

def main():
    try:
        # Demande à l'utilisateur s'il veut utiliser la base de données locale ou MySQL
        use_local = messagebox.askyesno(
            "Sélection de la base de données",
            "Veut-tu utiliser la base de donnée local?\n\nOui = Local Database\nNon = MySQL Database"
        )
        
        # Initialisation de la base de données et du gestionnaire d'interface utilisateur
        db = DatabaseConnection(use_local=use_local)
        image_processor = ImageProcessor()
        face_db = FaceDatabase(db)
        
        # Démarrage de l'application avec le gestionnaire d'interface utilisateur
        app = UIManager(db, image_processor, face_db)
        app.window.mainloop()
        
    except Exception as e:
        print(f"Error starting application: {str(e)}")

if __name__ == "__main__":
    main()
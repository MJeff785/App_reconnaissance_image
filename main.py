from database.connection import DatabaseConnection
from src.image_processor import ImageProcessor
from database.face_database import FaceDatabase
from ui.ui_manager import UIManager
from tkinter import messagebox

def main():
    try:
        # Ask user for database choice
        use_local = messagebox.askyesno(
            "Database Selection",
            "Do you want to use local database?\n\nYes = Local Database\nNo = MySQL Database"
        )
        
        # Initialize components
        db = DatabaseConnection(use_local=use_local)
        image_processor = ImageProcessor()
        face_db = FaceDatabase(db)
        
        # Start UI
        app = UIManager(db, image_processor, face_db)
        app.window.mainloop()
        
    except Exception as e:
        print(f"Error starting application: {str(e)}")

if __name__ == "__main__":
    main()
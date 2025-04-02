from connection import DatabaseConnection
from image_processor import ImageProcessor
from face_database import FaceDatabase
from ui_manager import UIManager

def main():
    try:
        # Initialize components
        db = DatabaseConnection()
        image_processor = ImageProcessor()
        face_db = FaceDatabase(db)
        
        # Start UI
        app = UIManager(db, image_processor, face_db)
        app.window.mainloop()
        
    except Exception as e:
        print(f"Error starting application: {str(e)}")

if __name__ == "__main__":
    main()
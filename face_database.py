import pickle

class FaceDatabase:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def save_student_face(self, student_data, face_data):
        try:
            # Save student info
            self.db.execute_query(
                """INSERT INTO Etudiants 
                   (nom_famille, prenom, id_classe, annee_scolaire, photo_path) 
                   VALUES (%s, %s, %s, %s, %s)""",
                (student_data['nom'], student_data['prenom'], 
                 student_data['classe_id'], student_data['annee'], 
                 face_data['path'])  # Changed from image_path to path
            )
            
            student_id = self.db.execute_query("SELECT LAST_INSERT_ID()")[0][0]
            
            # Save face features
            self.db.execute_query(
                """INSERT INTO FaceFeatures 
                   (etudiant_id, image_path, face_encoding) 
                   VALUES (%s, %s, %s)""",
                (student_id, face_data['path'],  # Changed from image_path to path
                 pickle.dumps(face_data['encoding']))
            )
            
            return True
            
        except Exception as e:
            raise Exception(f"Error saving to database: {str(e)}")
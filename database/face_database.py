import pickle

class FaceDatabase:
    def __init__(self, db_connection):
        # Initialise la connexion à la base de données
        self.db = db_connection
    
    def save_student_face(self, student_data, face_data):
        try:
            # Enregistre les informations de l'étudiant dans la table Etudiants
            self.db.execute_query(
                """INSERT INTO Etudiants 
                   (nom_famille, prenom, id_classe, annee_scolaire, photo_path) 
                   VALUES (%s, %s, %s, %s, %s)""",
                (student_data['nom'], student_data['prenom'], 
                 student_data['classe_id'], student_data['annee'], 
                 face_data['path'])  # Utilise le chemin de l'image du visage
            )
            
            # Récupère l'ID de l'étudiant nouvellement créé
            student_id = self.db.execute_query("SELECT LAST_INSERT_ID()")[0][0]
            
            # Enregistre les caractéristiques du visage dans la table FaceFeatures
            self.db.execute_query(
                """INSERT INTO FaceFeatures 
                   (etudiant_id, image_path, face_encoding) 
                   VALUES (%s, %s, %s)""",
                (student_id, face_data['path'],  # Associe l'image au nouvel étudiant
                 pickle.dumps(face_data['encoding']))  # Sérialise l'encodage du visage
            )
            
            return True
            
        except Exception as e:
            raise Exception(f"Erreur lors de l'enregistrement dans la base de données: {str(e)}")
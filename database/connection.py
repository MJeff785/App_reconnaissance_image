import mysql.connector
from mysql.connector import Error
from tkinter import messagebox
import sqlite3
import os
import sys

class DatabaseConnection:
    def __init__(self, use_local=False):
        self.use_local = use_local
        if use_local:
            self.config = {
                'database': 'local.db'
            }
        else:
            self.config = {
                'host': 'localhost',
                'user': 'root',
                'password': '',
                'database': 'lycee_melkior'
            }

    def connect(self):
        try:
            if self.use_local:
                # Obtenir le chemin correct pour la base de données locale lors du packaging
                if getattr(sys, 'frozen', False):
                    application_path = os.path.dirname(sys.executable)
                else:
                    application_path = os.path.dirname(os.path.abspath(__file__))
                
                db_path = os.path.join(application_path, self.config['database'])
                connection = sqlite3.connect(db_path)
                cursor = connection.cursor()
                
                # Activer les clés étrangères
                cursor.execute("PRAGMA foreign_keys = ON")
                
                # Créer les tables
                cursor.executescript('''
                    CREATE TABLE IF NOT EXISTS Classe (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nom_classe TEXT NOT NULL,
                        niveau TEXT NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS Etudiants (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        prenom TEXT NOT NULL,
                        nom_famille TEXT NOT NULL,
                        id_classe INTEGER NOT NULL,
                        annee_scolaire TEXT NOT NULL,
                        photo_path TEXT,
                        FOREIGN KEY (id_classe) REFERENCES Classe(id)
                    );

                    CREATE TABLE IF NOT EXISTS FaceFeatures (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        etudiant_id INTEGER NOT NULL,
                        image_path TEXT NOT NULL UNIQUE,
                        face_encoding BLOB NOT NULL,
                        date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (etudiant_id) REFERENCES Etudiants(id)
                    );
                ''')
                
                # Vérifier si la table Classe est vide et insérer les données par défaut
                cursor.execute("SELECT COUNT(*) FROM Classe")
                if cursor.fetchone()[0] == 0:
                    cursor.execute('''
                        INSERT INTO Classe (nom_classe, niveau) VALUES 
                        ('BTS SIO', '1ere année'),
                        ('BTS SIO', '2eme année'),
                        ('Terminale', '2'),
                        ('BTS Commerce', '1')
                    ''')
                
                connection.commit()
                return connection
            else:
                connection = mysql.connector.connect(**self.config)
                if connection.is_connected():
                    return connection
        except Exception as e:
            messagebox.showerror("Erreur de Connexion", f"Erreur: {e}")
            return None

    def execute_query(self, query, params=None):
        connection = self.connect()
        cursor = None
        if connection:
            try:
                cursor = connection.cursor()
                
                # Adapter la requête pour SQLite si utilisation de la base de données locale
                if self.use_local:
                    # Remplacer MySQL LAST_INSERT_ID() par SQLite last_insert_rowid()
                    query = query.replace('LAST_INSERT_ID()', 'last_insert_rowid()')
                    # Remplacer % par ? pour la paramétrisation SQLite
                    query = query.replace('%s', '?')
                
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                result = cursor.fetchall() if cursor.description else None
                
                # Pour les requêtes INSERT, retourner le dernier ID inséré
                if query.strip().upper().startswith('INSERT'):
                    if self.use_local:
                        result = [(cursor.lastrowid,)]
                    else:
                        cursor.execute("SELECT LAST_INSERT_ID()")
                        result = cursor.fetchall()
                
                connection.commit()
                return result
            except Exception as e:
                messagebox.showerror("Erreur de Requête", f"Erreur: {e}")
                return None
            finally:
                if cursor:
                    cursor.close()
                connection.close()
        return None

    def test_connection(self):
        connection = self.connect()
        if connection:
            messagebox.showinfo("Succès", "Connexion à la base de données réussie !")
            connection.close()
-- Création de la base de données local_db si elle n'existe pas déjà
CREATE DATABASE IF NOT EXISTS local_db;
USE local_db;

CREATE TABLE IF NOT EXISTS Classe (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nom_classe VARCHAR(50) NOT NULL,
    niveau VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS Etudiants (
    id INT PRIMARY KEY AUTO_INCREMENT,
    prenom VARCHAR(50) NOT NULL,
    nom_famille VARCHAR(50) NOT NULL,
    id_classe INT NOT NULL,
    annee_scolaire VARCHAR(9) NOT NULL,
    photo_path VARCHAR(255),
    FOREIGN KEY (id_classe) REFERENCES Classe(id)
);


CREATE TABLE IF NOT EXISTS FaceFeatures (
    id INT PRIMARY KEY AUTO_INCREMENT,
    etudiant_id INT NOT NULL,
    image_path VARCHAR(100) NOT NULL,
    face_encoding MEDIUMBLOB NOT NULL,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (etudiant_id) REFERENCES Etudiants(id),
    UNIQUE (image_path)
);
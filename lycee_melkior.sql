-- Create database
CREATE DATABASE IF NOT EXISTS lycee_melkior;
USE lycee_melkior;

-- Create Classe table
CREATE TABLE Classe (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nom_classe VARCHAR(50) NOT NULL,
    niveau VARCHAR(20) NOT NULL
);

-- Create Etudiants table
CREATE TABLE Etudiants (
    id INT PRIMARY KEY AUTO_INCREMENT,
    prenom VARCHAR(50) NOT NULL,
    nom_famille VARCHAR(50) NOT NULL,
    id_classe INT NOT NULL,
    annee_scolaire VARCHAR(9) NOT NULL,
    photo_path VARCHAR(255),
    FOREIGN KEY (id_classe) REFERENCES Classe(id)
);

-- Create FaceFeatures table
CREATE TABLE FaceFeatures (
    id INT PRIMARY KEY AUTO_INCREMENT,
    etudiant_id INT NOT NULL,
    image_path VARCHAR(100) NOT NULL,  -- Reduced from 255 to 100
    face_encoding MEDIUMBLOB NOT NULL,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (etudiant_id) REFERENCES Etudiants(id),
    UNIQUE (image_path)
);
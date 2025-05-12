

# EduFace Manager - Système de Reconnaissance Faciale pour la Gestion des Présences

## Présentation

EduFace Manager est une application Python permettant la gestion automatisée des présences dans un établissement scolaire grâce à la reconnaissance faciale. Elle propose une interface graphique moderne, l’enregistrement des étudiants avec photo, la détection en temps réel via webcam, et l’export des présences.

## Fonctionnalités

- **Ajout d’étudiants** avec photo et informations (nom, prénom, classe, année)
- **Reconnaissance faciale** en temps réel via webcam (OpenCV)
- **Gestion des présences** : marquage automatique des présents, retards, absents
- **Base de données** locale (SQLite) ou distante (MySQL)
- **Export des présences** au format CSV
- **Interface graphique** intuitive avec Tkinter

## Installation

1. **Cloner le dépôt :**
   ```bash
   git clone <url-du-repo>
   cd 1.1_App_reconnaissance_image
   ```

2. **Installer les dépendances :**
   ```bash
   pip install -r requirements.txt
   ```

3. **Lancer l’application :**
   ```bash
   python main.py
   ```

## Structure du projet

- `main.py` : Point d’entrée de l’application
- `ui/` : Interface graphique (Tkinter)
- `database/` : Connexion et gestion de la base de données
- `src/` : Modules de reconnaissance faciale et logique métier
- `cascades/haarcascade_frontalface_default.xml` : Classificateur pré-entraîné pour la détection de visages
- `requirements.txt` : Dépendances Python

## Prérequis

- Python 3.8 ou supérieur
- Webcam fonctionnelle
- Accès à une base de données MySQL (optionnel)

## Ressources utilisées

- **Frameworks** : Tkinter, OpenCV, Pillow, NumPy, MySQL Connector
- **IDE recommandé** : Visual Studio Code

## Remarques

- Le fichier `haarcascade_frontalface_default.xml` est inclus dans le dossier `cascades` et ne nécessite pas d’être généré.
- Les fichiers de base de données (`.db`, `.sql`) sont exclus du dépôt pour des raisons de confidentialité.
- Pour toute contribution, merci de respecter la structure du projet et de documenter vos ajouts.

---

        
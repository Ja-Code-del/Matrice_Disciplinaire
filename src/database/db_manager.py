import os
import sqlite3
from contextlib import contextmanager
import pandas as pd


# Fonction pour vérifier la présence des colonnes
def check_required_columns(df, required_columns):
    """Vérifie si les colonnes requises sont présentes dans le DataFrame"""
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"Colonnes manquantes dans le fichier : {missing_columns}")
        return False
    return True


class DatabaseManager:
    def __init__(self, db_name="gendarmes.db"):
        # Trouver le répertoire racine du projet
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        # Construire le chemin vers la DB
        self.db_name = os.path.join(project_root, db_name)
        print(f"Chemin complet de la DB: {self.db_name}")  # Debug

    @contextmanager
    def get_connection(self):
        """Crée et gère la connexion à la base de données"""
        conn = sqlite3.connect(self.db_name)
        try:
            yield conn
        finally:
            conn.close()

    def create_tables(self):
        """Crée les tables de la base de données"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Suppression des tables existantes si elles existent
            cursor.execute("DROP TABLE IF EXISTS sanctions")
            cursor.execute("DROP TABLE IF EXISTS gendarmes_etat")

            # Table des gendarmes (reste inchangée)
            cursor.execute('''CREATE TABLE IF NOT EXISTS gendarmes_etat (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                matricule TEXT UNIQUE,
                nom TEXT,
                prenoms TEXT,
                date_naissance DATE,
                lieu_naissance TEXT,
                date_entree_service DATE,
                sexe TEXT
            )''')

            # Table sanctions avec les nouveaux champs
            cursor.execute('''CREATE TABLE IF NOT EXISTS sanctions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_radiation TEXT,
                numero_dossier TEXT,
                annee INTEGER,
                date_enregistrement DATE,
                numero TEXT,
                gendarme_id INTEGER,
                date_faits DATE,
                faute_commise TEXT,
                categorie TEXT,
                statut TEXT,
                reference_statut TEXT,
                taux_jar INTEGER,
                comite TEXT,
                annee_faits INTEGER,
                FOREIGN KEY (gendarme_id) REFERENCES gendarmes_etat(id)
            )''')

            # Table principale des gendarmes
            cursor.execute('''CREATE TABLE IF NOT EXISTS gendarmes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_radiation TEXT,
                numero_dossier TEXT,
                mle TEXT,
                nom_prenoms TEXT,
                grade TEXT,
                sexe TEXT,
                date_naissance TEXT,
                age INTEGER,
                unite TEXT,
                leg TEXT,
                sub TEXT,
                rg TEXT,
                legions TEXT,
                subdiv TEXT,
                regions TEXT,
                date_entree_gie TEXT,
                annee_service INTEGER,
                situation_matrimoniale TEXT,
                nb_enfants INTEGER)''')

            conn.commit()

    def insert_gendarmes_from_excel(self, file_path):
        """Insère les données du fichier Excel dans la base de données après vérification des colonnes"""
        required_columns = [
            "N° DOSSIER", "ANNEE DE PUNITION", "NOM", "GRADE",
            # Ajouter toutes les colonnes nécessaires pour l'insertion
        ]

        # Charger le fichier Excel dans un DataFrame
        df = pd.read_excel(file_path)

        # Vérifier la présence des colonnes nécessaires
        if not check_required_columns(df, required_columns):
            print("Erreur : le fichier Excel ne contient pas toutes les colonnes nécessaires.")
            return

        # Insertion ligne par ligne avec gestion d'erreurs
        for index, row in df.iterrows():
            try:
                # Exemple d'insertion (à adapter selon votre structure)
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO gendarmes (numero_dossier, annee_punition, nom_prenoms, grade)
                        VALUES (?, ?, ?, ?)
                    ''', (row["N° DOSSIER"], row["ANNEE DE PUNITION"], row["NOM"], row["GRADE"]))
                    conn.commit()
            except KeyError as e:
                print(f"Erreur sur la ligne {index + 1}: Colonne manquante - {e}")
            except Exception as e:
                print(f"Erreur sur la ligne {index + 1}: {e}")

    def get_all_gendarmes(self):
        """Récupère tous les gendarmes de la base de données"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM gendarmes ORDER BY nom_prenoms")
            return cursor.fetchall()

    def get_gendarme_by_mle(self, mle):
        """Récupère un gendarme par son matricule"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM gendarmes WHERE mle = ?", (mle,))
            return cursor.fetchone()

    def get_gendarme_by_name(self, name):
        """Récupère un gendarme par son nom"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM gendarmes WHERE nom_prenoms LIKE ?", (f"%{name}%",))
            return cursor.fetchall()

    def get_sanctions_by_gendarme_id(self, gendarme_id):
        """Récupère toutes les sanctions d'un gendarme"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM sanctions 
                WHERE gendarme_id = ? 
                ORDER BY date_enr DESC
            """, (gendarme_id,))
            return cursor.fetchall()

    def get_statistics(self):
        """Récupère des statistiques générales"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            stats = {}

            # Nombre total de gendarmes
            cursor.execute("SELECT COUNT(*) FROM gendarmes")
            stats['total_gendarmes'] = cursor.fetchone()[0]

            # Nombre total de sanctions
            cursor.execute("SELECT COUNT(*) FROM sanctions")
            stats['total_sanctions'] = cursor.fetchone()[0]

            # Moyenne des sanctions par gendarme
            if stats['total_gendarmes'] > 0:
                stats['moyenne_sanctions'] = stats['total_sanctions'] / stats['total_gendarmes']
            else:
                stats['moyenne_sanctions'] = 0

            return stats

# Exemple d'utilisation :
# db_manager = DatabaseManager()
# db_manager.create_tables()
# db_manager.insert_gendarmes_from_excel("votre_fichier.xlsx")

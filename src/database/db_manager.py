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

            # Table des gendarmes
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

            # Table sanctions
            cursor.execute('''CREATE TABLE IF NOT EXISTS sanctions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_dossier TEXT,
                annee_punition INTEGER,
                numero_ordre INTEGER,
                date_enr DATE,
                matricule INTEGER,
                faute_commise TEXT,
                date_faits DATE,
                categorie INTEGER,
                statut TEXT,
                reference_statut TEXT,
                taux_jar TEXT,
                comite INTEGER,
                annee_faits INTEGER,
                numero_decision,
                FOREIGN KEY (matricule) REFERENCES gendarmes_etat(matricule)
            )''')

            # Table principale des gendarmes
            cursor.execute('''CREATE TABLE IF NOT EXISTS gendarmes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mle TEXT,
                nom_prenoms TEXT,
                grade TEXT,
                sexe TEXT,
                date_naissance TEXT,
                age INTEGER,
                unite TEXT,
                legions TEXT,
                subdiv TEXT,
                regions TEXT,
                date_entree_gie TEXT,
                annee_service INTEGER,
                situation_matrimoniale TEXT,
                nb_enfants INTEGER)''')

            conn.commit()

    def get_all_gendarmes(self):
        """Récupère tous les gendarmes de la base de données"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM gendarmes ORDER BY nom_prenoms")
            return cursor.fetchall()

    def get_sanctions_by_gendarme_id(self, matricule):
        """Récupère toutes les sanctions d'un gendarme"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM sanctions 
                WHERE matricule = ? 
                ORDER BY date_enr DESC
            """, (matricule,))
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

    def is_connected(self):
        """Vérifie si la connexion à la base de données est active."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                return True
        except Exception as e:
            print(f"Erreur de connexion : {str(e)}")
            return False

    def table_exists(self, table_name):
        """Vérifie si une table existe dans la base de données."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                       SELECT name FROM sqlite_master 
                       WHERE type='table' AND name=?
                   """, (table_name,))
                result = cursor.fetchone()
                return result is not None
        except Exception as e:
            print(f"Erreur lors de la vérification de la table {table_name}: {str(e)}")
            return False

    def count_records(self, table_name):
        """Compte le nombre d'enregistrements dans une table."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception as e:
            print(f"Erreur lors du comptage des enregistrements de {table_name}: {str(e)}")
            return 0

    def check_sanctions_duplicates(self):
        """Vérifie la présence de doublons dans la table sanctions."""
        try:
            with self.get_connection() as conn:
                query_check = """
                SELECT 
                    s.numero_dossier, 
                    s.matricule,
                    s.date_faits,
                    s.faute_commise,
                    COUNT(*) as occurrence_count
                FROM sanctions s
                GROUP BY s.numero_dossier, s.matricule, s.date_faits, s.faute_commise
                HAVING COUNT(*) > 1
                """
                cursor = conn.cursor()
                cursor.execute(query_check)
                duplicates = cursor.fetchall()
                return duplicates
        except Exception as e:
            print(f"Erreur lors de la vérification des doublons : {str(e)}")
            return None

    def run_sanctions_diagnostic(self):
        """Exécute un diagnostic complet de la table sanctions."""
        debug_queries = [
            # 1. Total des dossiers uniques
            """
            SELECT COUNT(DISTINCT numero_dossier) as total_unique_dossiers 
            FROM sanctions;
            """,

            # 2. Détail des doublons par numéro de dossier
            """
            SELECT 
                numero_dossier,
                COUNT(*) as occurrences,
                GROUP_CONCAT(matricule) as matricules
            FROM sanctions
            GROUP BY numero_dossier
            HAVING COUNT(*) > 1
            ORDER BY occurrences DESC;
            """,

            # 3. Vérification des champs NULL ou vides
            """
            SELECT 
                COUNT(*) as total,
                COUNT(NULLIF(numero_dossier, '')) as dossiers_non_vides,
                COUNT(NULLIF(matricule, '')) as matricules_non_vides
            FROM sanctions;
            """,

            # 4. Les enregistrements qui posent problème
            """
            SELECT s1.*
            FROM sanctions s1
            WHERE EXISTS (
                SELECT 1
                FROM sanctions s2
                WHERE s1.numero_dossier = s2.numero_dossier
                AND s1.rowid != s2.rowid
            )
            ORDER BY numero_dossier;
            """,

            # Ajouter cette requête comme Diagnostic 5
            """
            SELECT 
                s.numero_dossier,
                s.matricule,
                s.date_faits,
                s.faute_commise
            FROM sanctions s
            ORDER BY s.date_faits DESC;
            """
        ]

        results = {}
        print("=== DIAGNOSTIC DES DONNÉES ===")
        with self.get_connection() as conn:
            cursor = conn.cursor()

            for i, query in enumerate(debug_queries, 1):
                try:
                    print(f"\n--- Diagnostic {i} ---")
                    cursor.execute(query)
                    results = cursor.fetchall()

                    if i == 1:  # Total des dossiers uniques
                        print(f"Nombre total de dossiers uniques : {results[0][0]}")

                    elif i == 2:  # Détail des doublons
                        print("Doublons trouvés :")
                        if not results:
                            print("Aucun doublon trouvé")
                        for row in results:
                            print(f"Dossier: {row[0]}")
                            print(f"Nombre d'occurrences: {row[1]}")
                            print(f"Matricules concernés: {row[2]}\n")

                    elif i == 3:  # Vérification des champs NULL
                        row = results[0]
                        print(f"Total des enregistrements : {row[0]}")
                        print(f"Dossiers non vides : {row[1]}")
                        print(f"Matricules non vides : {row[2]}")

                    elif i == 4:  # Enregistrements problématiques
                        print("Enregistrements avec même numéro de dossier :")
                        if not results:
                            print("Aucun enregistrement problématique trouvé")
                        for row in results:
                            print(f"Dossier: {row[0]}, Matricule: {row[1]}")

                    elif i == 5:  # Liste détaillée des sanctions
                        print("Détail des sanctions :")
                        print("Num Dossier | Matricule | Date faits | Faute ")
                        print("-" * 70)
                        for row in results:
                            print(f"{row[0]:<12} | {row[1]:<10} | {row[2]:<11} | {row[3]} ")
                        print(f"\nNombre total d'enregistrements : {len(results)}")

                except Exception as e:
                    print(f"Erreur lors du diagnostic {i}: {str(e)}")
                    continue

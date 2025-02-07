import os
import sqlite3
from contextlib import contextmanager



# Fonction pour vérifier la présence des colonnes
def check_required_columns(df, required_columns):
    """Vérifie si les colonnes requises sont présentes dans le DataFrame"""
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"Colonnes manquantes dans le fichier : {missing_columns}")
        return False
    return True


class DatabaseManager:
    def __init__(self, db_name="gend.db"):
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
            cursor.execute("DROP TABLE IF EXISTS main_tab")

            # Table gendarme
            cursor.execute('''CREATE TABLE IF NOT EXISTS gendarmes (
                matricule TEXT PRIMARY KEY
                nom_prenoms TEXT,
                sexe TEXT,
                date_entree_gie DATE,
                nb_enfants INTEGER
            )''')

            # Table gendarmes_etat
            cursor.execute('''CREATE TABLE IF NOT EXISTS gendarmes_etat (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                matricule TEXT UNIQUE,
                nom TEXT,
                prenoms TEXT,
                date_naissance DATE,
                lieu_naissance TEXT,
                date_entree_service DATE,
                sexe TEXT,
                FOREIGN KEY(matricule) REFERENCES gendarmes(matricule)
            )''')

            # Table Dossier
            cursor.execute('''CREATE TABLE IF NOT EXISTS Dossiers(
            numero_inc INTEGER,
            matricule_dossier TEXT UNIQUE,
            reference TEXT UNIQUE,
            date_enr DATE,
            date_faits DATE,
            numero_annee INTEGER,
            annee_enr INTEGER,
            grade_id INTEGER,
            situation_mat_id INTEGER,
            unite_id INTEGER,
            legion_id INTEGER,
            subdiv_id INTEGER,
            rg_id INTEGER,
            faute_id INTEGER,
        
            PRIMARY KEY(numero_inc, matricule_dossier, reference),
            FOREIGN KEY(matricule_dossier) REFERENCES gendarmes(matricule),
            FOREIGN KEY(grade_id) REFERENCES Grade(id_grade),
            FOREIGN KEY(situation_mat_id) REFERENCES Situation_mat(id_sit_mat),
            FOREIGN KEY(unite_id) REFERENCES Unite(id_unite),
            FOREIGN KEY(legion_id) REFERENCES Legion(id_legion),
            FOREIGN KEY(subdiv_id) REFERENCES Subdiv(id_subdiv),
            FOREIGN KEY(rg_id) REFERENCES Regions(id_rg),
            FOREIGN KEY(faute_id) REFERENCES Faute(id_faute)
            )''')

            

            conn.commit()

    def get_all_gendarmes(self):
        """Récupère tous les gendarmes de la base de données"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM main_tab ORDER BY numero_dossier")
            return cursor.fetchall()

    #Changer le nom de cette méthode en get_sanctions_by_folder_num plus tard
    def get_sanctions_by_gendarme_id(self, num_dossier):
        """Récupère toutes les sanctions d'un gendarme"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM main_tab 
                WHERE numero_dossier = ? 
                ORDER BY date_enr DESC
            """, (num_dossier,))
            return cursor.fetchall()

    def get_statistics(self):
        """Récupère des statistiques générales"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            stats = {}

            # Nombre total de gendarmes
            cursor.execute("SELECT COUNT (DISTINCT matricule) FROM main_tab")
            stats['total_gendarmes'] = cursor.fetchone()[0]

            # Nombre total de sanctions
            cursor.execute("SELECT COUNT(*) FROM main_tab")
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
                    m.numero_dossier, 
                    m.matricule,
                    m.date_faits,
                    m.faute_commise,
                    COUNT(*) as occurrence_count
                FROM main_tab m
                GROUP BY m.numero_dossier, m.matricule, m.date_faits, m.faute_commise
                HAVING COUNT(*) > 1
                """

                with conn.cursor() as cursor:  # Utilisation du contexte pour fermer automatiquement le curseur
                    cursor.execute(query_check)
                    return cursor.fetchall()

        except Exception as e:
            print(f"Erreur lors de la vérification des doublons : {str(e)}")
            return None

    def run_sanctions_diagnostic(self):
        """Exécute un diagnostic complet de la table principale."""
        debug_queries = {
            1: """
                SELECT COUNT(DISTINCT numero_dossier) as total_unique_dossiers 
                FROM main_tab;
            """,
            2: """
                SELECT 
                    numero_dossier,
                    COUNT(*) as occurrences,
                    GROUP_CONCAT(matricule SEPARATOR ' | ') as matricules
                FROM main_tab
                GROUP BY numero_dossier
                HAVING COUNT(*) > 1
                ORDER BY occurrences DESC;
            """,
            3: """
                SELECT 
                    COUNT(*) as total,
                    COUNT(NULLIF(numero_dossier, '')) as dossiers_non_vides,
                    COUNT(NULLIF(matricule, '')) as matricules_non_vides
                FROM main_tab;
            """,
            4: """
                SELECT 
                    m1.numero_dossier, m1.matricule, m1.date_faits, m1.faute_commise
                FROM main_tab m1
                WHERE EXISTS (
                    SELECT 1
                    FROM main_tab m2
                    WHERE m1.matricule = m2.matricule
                    AND m1.rowid != m2.rowid
                )
                ORDER BY numero_dossier;
            """,
            5: """
                SELECT 
                    m.numero_dossier, m.matricule, m.date_faits, m.faute_commise
                FROM main_tab m
                ORDER BY m.date_faits DESC;
            """
        }

        results = {}  # Stocke tous les résultats
        print("=== 📊 DIAGNOSTIC DES DONNÉES ===")

        with self.get_connection() as conn:
            cursor = conn.cursor()

            for i, (num, query) in enumerate(debug_queries.items(), 1):
                try:
                    print(f"\n--- 🔍 Diagnostic {num} ---")
                    cursor.execute(query)
                    results[num] = cursor.fetchall()

                    if num == 1:  # Total des dossiers uniques
                        print(f"📌 Nombre total de dossiers uniques : {results[num][0][0]}")

                    elif num == 2:  # Détail des doublons
                        print("🟠 Doublons trouvés :")
                        if not results[num]:
                            print("✅ Aucun doublon trouvé.")
                        else:
                            for row in results[num]:
                                print(f"Dossier: {row[0]}, Occurrences: {row[1]}")
                                print(f"Matricules concernés: {row[2]}\n")

                    elif num == 3:  # Vérification des champs NULL
                        row = results[num][0]
                        print(f"📊 Total des enregistrements : {row[0]}")
                        print(f"✅ Dossiers non vides : {row[1]}")
                        print(f"✅ Matricules non vides : {row[2]}")

                    elif num == 4:  # Enregistrements problématiques
                        print("⚠️ Enregistrements suspects (matricules en double) :")
                        if not results[num]:
                            print("✅ Aucun enregistrement problématique trouvé.")
                        else:
                            for row in results[num]:
                                print(f"Dossier: {row[0]}, Matricule: {row[1]}, Date: {row[2]}, Faute: {row[3]}")

                    elif num == 5:  # Liste détaillée des sanctions
                        print("📜 Détail des sanctions (triées par date) :")
                        print("Num Dossier | Matricule  | Date faits  | Faute")
                        print("-" * 70)
                        for row in results[num]:
                            print(f"{row[0]:<12} | {row[1]:<10} | {row[2]:<11} | {row[3]}")
                        print(f"\n📌 Nombre total d'enregistrements : {len(results[num])}")

                except Exception as e:
                    print(f"❌ Erreur lors du diagnostic {num}: {str(e)}")
                    continue

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
            #cursor.execute(f"DROP TABLE IF EXISTS Gendarmes, gendarmes_etat, Dossiers, Fautes, Sanctions,  ")

            # Table gendarmes_etat contenant les infos complete des gendarmes
            cursor.execute('''CREATE TABLE IF NOT EXISTS gendarmes_etat (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                matricule TEXT UNIQUE NOT NULL,
                nom TEXT,
                prenoms TEXT,
                date_naissance DATE,
                lieu_naissance TEXT,
                date_entree_service DATE,
                sexe TEXT
            )''')

            # Table gendarme (simplifiée pour les dossiers disciplinaires)
            cursor.execute('''CREATE TABLE IF NOT EXISTS Gendarmes (
                id_gendarme INTEGER PRIMARY KEY AUTOINCREMENT,
                matricule TEXT,
                nom_prenoms TEXT,
                sexe TEXT,
                date_entree_gie DATE,
                nb_enfants INTEGER,
                FOREIGN KEY (matricule) REFERENCES gendarmes_etat(matricule) ON DELETE CASCADE
            )''')

            #Table Statut
            cursor.execute('''CREATE TABLE IF NOT EXISTS Statut(
                            id_statut INTEGER PRIMARY KEY AUTOINCREMENT,
                            lib_statut TEXT NOT NULL UNIQUE
                        )''')

            #Table Type_sanctions
            cursor.execute('''CREATE TABLE IF NOT EXISTS Type_sanctions(
                id_type_sanction  INTEGER PRIMARY KEY AUTOINCREMENT,
                lib_type_sanction TEXT NOT NULL UNIQUE
            )''')

            # Table Dossiers
            cursor.execute('''CREATE TABLE IF NOT EXISTS Dossiers(
                numero_inc INTEGER PRIMARY KEY AUTOINCREMENT,
                id_dossier TEXT NOT NULL,
                matricule_dossier TEXT NOT NULL,
                reference TEXT UNIQUE NOT NULL,
                date_enr DATE NOT NULL,
                date_faits DATE NOT NULL,
                numero_annee INTEGER NOT NULL,
                annee_enr INTEGER NOT NULL,
                sanction_id INTEGER NOT NULL,
                grade_id INTEGER,
                situation_mat_id INTEGER,
                unite_id INTEGER,
                legion_id INTEGER,
                subdiv_id INTEGER,
                rg_id INTEGER,
                faute_id INTEGER NOT NULL,
                libelle TEXT,
                statut_id INTEGER NOT NULL,
         
                FOREIGN KEY(matricule_dossier) REFERENCES Gendarmes(matricule) ON DELETE CASCADE,
                FOREIGN KEY(grade_id) REFERENCES Grade(id_grade),
                FOREIGN KEY(situation_mat_id) REFERENCES Sit_mat(id_sit_mat),
                FOREIGN KEY(unite_id) REFERENCES Unite(id_unite),
                FOREIGN KEY(legion_id) REFERENCES Legion(id_legion),
                FOREIGN KEY(subdiv_id) REFERENCES Subdiv(id_subdiv),
                FOREIGN KEY(rg_id) REFERENCES Regions(id_rg),
                FOREIGN KEY(faute_id) REFERENCES Fautes(id_faute),
                FOREIGN KEY(sanction_id) REFERENCES Sanctions(id_sanction),
                FOREIGN KEY(statut_id) REFERENCES Statut(id_statut)
            )''')

            cursor.execute('''CREATE TRIGGER generate_id_dossier AFTER
                INSERT ON Dossiers
                BEGIN
                    UPDATE Dossiers
                    SET id_dossier = NEW.numero_inc || '/' || NEW.annee_enr
                    WHERE numero_inc = NEW.numero_inc AND matricule_dossier = NEW.matricule_dossier
                END
            )''')


            # Table Sanctions
            cursor.execute('''CREATE TABLE IF NOT EXISTS Sanctions(
                id_sanction INTEGER PRIMARY KEY AUTOINCREMENT,
                type_sanction_id INTEGER,
                num_inc INTEGER,
                taux TEXT,
                numero_decision TEXT,
                numero_arrete TEXT,
                annee_radiation INTEGER,
                ref_statut TEXT,
                comite TEXT,
                FOREIGN KEY (num_inc) REFERENCES Dossiers(numero_inc) ON DELETE CASCADE,
                FOREIGN KEY (type_sanction_id) REFERENCES Type_sanctions(id_type_sanction)
            )''')

            #Table Fautes
            cursor.execute('''CREATE TABLE IF NOT EXISTS Fautes(
                id_faute INTEGER PRIMARY KEY AUTOINCREMENT,
                lib_faute TEXT NOT NULL UNIQUE,
                cat_id INTEGER NOT NULL,
                FOREIGN KEY cat_id REFERENCES Categories(id_categorie)
            )''')

            cursor.execute('''CREATE TABLE IF NOT EXISTS Categories(
                id_categorie INTEGER PRIMARY KEY AUTOINCREMENT,
                lib_categorie TEXT NOT NULL UNIQUE
            )''')

            cursor.execute('''CREATE TABLE IF NOT EXISTS Grade(
                id_grade INTEGER PRIMARY KEY AUTOINCREMENT,
                lib_grade TEXT NOT NULL UNIQUE
            )''')

            cursor.execute('''CREATE TABLE IF NOT EXISTS Sit_mat(
                id_sit_mat INTEGER PRIMARY KEY AUTOINCREMENT,
                lib_sit_mat TEXT NOT NULL UNIQUE
            )''')

            cursor.execute('''CREATE TABLE IF NOT EXISTS Unite(
                id_unite INTEGER PRIMARY KEY AUTOINCREMENT,
                lib_unite TEXT NOT NULL UNIQUE
            )''')

            cursor.execute('''CREATE TABLE IF NOT EXISTS Legion(
                id_legion INTEGER PRIMARY KEY AUTOINCREMENT,
                lib_legion TEXT NOT NULL UNIQUE
            )''')

            cursor.execute('''CREATE TABLE IF NOT EXISTS Subdiv(
                id_subdiv  INTEGER PRIMARY KEY AUTOINCREMENT,
                lib_subdiv TEXT NOT NULL UNIQUE
            )''')

            cursor.execute('''CREATE TABLE IF NOT EXISTS Region(
                id_rg  INTEGER PRIMARY KEY AUTOINCREMENT,
                lib_rg TEXT NOT NULL UNIQUE
            )''')

            conn.commit()

    def create_indexes(self):
        """Crée les index pour optimiser les performances"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('CREATE INDEX IF NOT EXISTS idx_gendarmes_matricule ON Gendarmes(matricule)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_dossiers_matricule ON Dossiers(matricule_dossier)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sanctions_num_inc ON Sanctions(num_inc)')

            conn.commit()

    def add_data(self, table, data):
        """
        Ajoute des données dans n'importe quelle table
        :param table: Nom de la table
        :param data: Dictionnaire {colonne: valeur}
        """
        columns = ', '.join(data.keys())  # Ex: "numero_inc, id_dossier"
        placeholders = ', '.join(['?' for _ in data])  # Ex: "?, ?"
        values = tuple(data.values())  # Ex: ("1", "1/2025")

        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        try:
            self.cursor.execute(query, values)
            self.conn.commit()
        except sqlite3.IntegrityError as e:
            print(f"⚠ Erreur d'insertion dans {table}: {e}")

    def get_foreign_key_id(self, table, column, value):
        """
        Récupère l'ID d'une valeur dans une table étrangère, l'ajoute si elle n'existe pas.
        :param table: Nom de la table étrangère
        :param column: Colonne contenant la valeur recherchée
        :param value: Valeur à rechercher
        :return: ID de la valeur
        """
        self.cursor.execute(f"SELECT id_{table.lower()} FROM {table} WHERE {column} = ?", (value,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            # Ajouter la valeur si elle n'existe pas
            self.cursor.execute(f"INSERT INTO {table} ({column}) VALUES (?)", (value,))
            self.conn.commit()
            return self.cursor.lastrowid  # Récupérer l'ID nouvellement inséré

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

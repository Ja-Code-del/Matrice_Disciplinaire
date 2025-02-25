import os
import sqlite3
from contextlib import contextmanager

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, db_name="gend.db"):
        # Trouver le répertoire racine du projet
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        # Construire le chemin vers la DB
        self.db_name = os.path.join(project_root, db_name)
        logger.info(f"Chemin complet de la DB: {self.db_name}")
        #print(f"Chemin complet de la DB: {self.db_name}")  # Debug

    @contextmanager
    def get_connection(self):
        """Crée et gère la connexion à la base de données"""
        try:
            self.conn = sqlite3.connect(self.db_name)
            yield self.conn
        except sqlite3.Error as e:
            print(f"Erreur de connexion à la base de données: {e}")
            raise
        finally:
            self.conn.close()

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
                age INTEGER,
                sexe TEXT,
                date_entree_gie DATE,
                annee_service INTEGER, 
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
                id_dossier TEXT,
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

            # cursor.execute('''CREATE TRIGGER generate_id_dossier AFTER
            #     INSERT ON Dossiers
            #     BEGIN
            #         UPDATE Dossiers
            #         SET id_dossier = NEW.numero_inc || '/' || NEW.annee_enr
            #         WHERE numero_inc = NEW.numero_inc AND matricule_dossier = NEW.matricule_dossier;
            #     END''')


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
                cat_id INTEGER,
                FOREIGN KEY (cat_id) REFERENCES Categories(id_categorie)
            )''')

            #Table Categories
            cursor.execute('''CREATE TABLE IF NOT EXISTS Categories(
                id_categorie INTEGER PRIMARY KEY AUTOINCREMENT,
                lib_categorie TEXT NOT NULL UNIQUE
            )''')

            #Table Grade
            cursor.execute('''CREATE TABLE IF NOT EXISTS Grade(
                id_grade INTEGER PRIMARY KEY AUTOINCREMENT,
                lib_grade TEXT NOT NULL UNIQUE
            )''')

            #Table Situation matrimoniale
            cursor.execute('''CREATE TABLE IF NOT EXISTS Sit_mat(
                id_sit_mat INTEGER PRIMARY KEY AUTOINCREMENT,
                lib_sit_mat TEXT NOT NULL UNIQUE
            )''')

            #Table Unite
            cursor.execute('''CREATE TABLE IF NOT EXISTS Unite(
                id_unite INTEGER PRIMARY KEY AUTOINCREMENT,
                lib_unite TEXT NOT NULL UNIQUE
            )''')

            #Table Legion
            cursor.execute('''CREATE TABLE IF NOT EXISTS Legion(
                id_legion INTEGER PRIMARY KEY AUTOINCREMENT,
                lib_legion TEXT NOT NULL UNIQUE
            )''')

            #Table Subdiv
            cursor.execute('''CREATE TABLE IF NOT EXISTS Subdiv(
                id_subdiv  INTEGER PRIMARY KEY AUTOINCREMENT,
                lib_subdiv TEXT NOT NULL UNIQUE
            )''')

            #Table region
            cursor.execute('''CREATE TABLE IF NOT EXISTS Region(
                id_rg  INTEGER PRIMARY KEY AUTOINCREMENT,
                lib_rg TEXT NOT NULL UNIQUE
            )''')

            self.ensure_triggers()

            conn.commit()

    def ensure_triggers(self):
        """Assure la création des triggers nécessaires"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Vérifier si le trigger existe
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='trigger' AND name='generate_id_dossier'
            """)

            if not cursor.fetchone():
                # Créer le trigger s'il n'existe pas
                cursor.execute('''CREATE TRIGGER generate_id_dossier AFTER
                    INSERT ON Dossiers
                    BEGIN
                        UPDATE Dossiers
                        SET id_dossier = NEW.numero_inc || '/' || NEW.annee_enr
                        WHERE numero_inc = NEW.numero_inc AND matricule_dossier = NEW.matricule_dossier;
                    END''')

                logger.info("Trigger generate_id_dossier créé avec succès")
            else:
                logger.info("Trigger generate_id_dossier existe déjà")

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
        Ajoute des données dans une table spécifique.

        Args:
            table (str): Nom de la table
            data (Dict[str, Any]): Dictionnaire des données {colonne: valeur}

        Raises:
            ValueError: Si la table n'est pas autorisée
            sqlite3.IntegrityError: Si une contrainte d'intégrité est violée
        """

        # Liste blanche des tables autorisées
        allowed_tables = {
            "Gendarmes", "Statut", "Type_sanctions", "Fautes",
            "Categories", "Grade", "Sit_mat", "Unite", "Legion", "Subdiv",
            "Region", "Dossiers", "Sanctions"
        }

        # Vérification si la table est autorisée
        if table not in allowed_tables:
            raise ValueError(f"Table '{table}' non autorisée")

        if not data:
            raise ValueError("Les données fournies sont vides")

        columns = ', '.join(f'"{col}"' for col in data.keys())  # Protection des noms de colonnes
        placeholders = ', '.join(['?' for _ in data])  # Génération des placeholders pour éviter l'injection SQL
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        values = tuple(data.values())

        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query, values)
                conn.commit()
                return cursor.lastrowid  # Retourne l'ID de la ligne insérée si applicable
            except sqlite3.IntegrityError as e:
                print(f"⚠ Erreur d'insertion dans {table}: {e}")
                return None  # Retourne None en cas d'erreur d'intégrité

    def get_foreign_key_id(self, table, column, value):
        """
        Récupère l'ID d'une valeur dans une table étrangère, l'ajoute si elle n'existe pas.
        :param table: Nom de la table étrangère
        :param column: Colonne contenant la valeur recherchée
        :param value: Valeur à rechercher
        :return: ID de la valeur
        """

        # Dictionnaire des tables autorisées et de leurs colonnes clés
        valid_tables = {
            "Statut": "id_statut",
            "Type_sanctions": "id_type_sanction",
            "Fautes": "id_faute",
            "Categories": "id_categorie",
            "Grade": "id_grade",
            "Sit_mat": "id_sit_mat",
            "Unite": "id_unite",
            "Legion": "id_legion",
            "Subdiv": "id_subdiv",
            "Region": "id_rg"
        }

        # Vérification de la validité de la table
        if table not in valid_tables:
            raise ValueError(f"Table non autorisée : {table}")

        id_column = valid_tables[table]  # Récupération du nom de l'ID dans la table

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Vérifier si la valeur existe déjà
            query = f"SELECT {id_column} FROM {table} WHERE {column} = ?"
            cursor.execute(query, (value,))
            result = cursor.fetchone()

            if result:
                return result[0]
            else:
                # Insérer la nouvelle valeur
                insert_query = f"INSERT INTO {table} ({column}) VALUES (?)"
                cursor.execute(insert_query, (value,))
                conn.commit()
                return cursor.lastrowid  # Retourne l'ID inséré

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

    def close(self):
        """Ferme la connexion"""
        self.conn.close()

    def add_case_and_sanction(self, dossier_data, sanction_data=None):
        """
        Ajoute un dossier et sa sanction associée dans une transaction unique

        Args:
            dossier_data (dict): Données du dossier
            sanction_data (dict, optional): Données de la sanction. Si None, une sanction par défaut est créée.

        Returns:
            tuple: (dossier_id, sanction_id) ou (None, None) en cas d'erreur
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("BEGIN TRANSACTION")

                try:
                    # Préparer les données de sanction par défaut si non fournies
                    if sanction_data is None:
                        sanction_data = {}

                    # Gérer le type de sanction en fonction du statut
                    if "statut_id" in dossier_data:
                        # Récupérer le libellé du statut
                        cursor.execute("SELECT lib_statut FROM Statut WHERE id_statut = ?",
                                       (dossier_data["statut_id"],))
                        statut_result = cursor.fetchone()

                        if statut_result:
                            statut_lib = statut_result[0]

                            # Définir le type de sanction selon le statut
                            if statut_lib == "EN COURS" and "type_sanction_id" not in sanction_data:
                                # Pour les dossiers "EN COURS", utiliser le type "EN INSTANCE" (ID: 6)
                                sanction_data["type_sanction_id"] = 6

                    # Assurer que le comité a une valeur par défaut
                    if "comite" not in sanction_data or not sanction_data["comite"]:
                        sanction_data["comite"] = "0"

                    # Assurer que le taux a une valeur par défaut
                    if "taux" not in sanction_data or not sanction_data["taux"]:
                        sanction_data["taux"] = "0"

                    # 1. Insérer la sanction
                    sanction_columns = ', '.join(f'"{col}"' for col in sanction_data.keys())
                    sanction_placeholders = ', '.join(['?' for _ in sanction_data])
                    sanction_query = f"INSERT INTO Sanctions ({sanction_columns}) VALUES ({sanction_placeholders})"

                    cursor.execute(sanction_query, tuple(sanction_data.values()))
                    sanction_id = cursor.lastrowid

                    # 2. Ajouter l'ID de sanction au dossier
                    dossier_data["sanction_id"] = sanction_id

                    # 3. Insérer le dossier
                    dossier_columns = ', '.join(f'"{col}"' for col in dossier_data.keys())
                    dossier_placeholders = ', '.join(['?' for _ in dossier_data])
                    dossier_query = f"INSERT INTO Dossiers ({dossier_columns}) VALUES ({dossier_placeholders})"

                    cursor.execute(dossier_query, tuple(dossier_data.values()))
                    dossier_id = cursor.lastrowid

                    # 4. Mettre à jour le num_inc dans la sanction
                    cursor.execute("UPDATE Sanctions SET num_inc = ? WHERE id_sanction = ?",
                                   (dossier_id, sanction_id))

                    # 5. Valider la transaction
                    cursor.execute("COMMIT")
                    return dossier_id, sanction_id

                except Exception as e:
                    cursor.execute("ROLLBACK")
                    logger.error(f"Erreur lors de l'ajout du dossier et de la sanction : {str(e)}")
                    raise

        except Exception as e:
            logger.error(f"Erreur lors de l'ajout du dossier et de la sanction : {str(e)}")
            return None, None

    def update_case_and_sanction(self, matricule, reference, dossier_data, sanction_data=None):
        """
        Met à jour un dossier et sa sanction associée dans une transaction unique

        Args:
            matricule (str): Matricule du gendarme
            reference (str): Référence du dossier
            dossier_data (dict): Données du dossier à mettre à jour
            sanction_data (dict, optional): Données de la sanction à mettre à jour

        Returns:
            bool: True si la mise à jour a réussi, False sinon
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # 1. Vérifier si le dossier existe et récupérer l'ID de sa sanction
                cursor.execute("""
                    SELECT numero_inc, sanction_id 
                    FROM Dossiers 
                    WHERE matricule_dossier = ? AND reference = ?
                """, (matricule, reference))

                result = cursor.fetchone()
                if not result:
                    logger.error(f"Dossier {reference} non trouvé pour le matricule {matricule}")
                    return False

                numero_inc, sanction_id = result

                # 2. Démarrer la transaction
                cursor.execute("BEGIN TRANSACTION")

                try:
                    # 3. Gérer le type de sanction en fonction du statut
                    if sanction_data is None:
                        sanction_data = {}

                    if "statut_id" in dossier_data:
                        # Récupérer le libellé du statut
                        cursor.execute("SELECT lib_statut FROM Statut WHERE id_statut = ?",
                                       (dossier_data["statut_id"],))
                        statut_result = cursor.fetchone()

                        if statut_result:
                            statut_lib = statut_result[0]

                            # Définir le type de sanction selon le statut
                            if statut_lib == "EN COURS" and "type_sanction_id" not in sanction_data:
                                # Pour les dossiers "EN COURS", utiliser le type "EN INSTANCE" (ID: 6)
                                sanction_data["type_sanction_id"] = 6

                    # Assurer que le comité a une valeur
                    if "comite" not in sanction_data or not sanction_data["comite"]:
                        sanction_data["comite"] = "0"

                    # Assurer que le taux a une valeur
                    if "taux" not in sanction_data or not sanction_data["taux"]:
                        sanction_data["taux"] = "0"

                    # 4. Mettre à jour la sanction si des données sont fournies
                    if sanction_data and sanction_id:
                        update_parts = []
                        update_values = []

                        for col, val in sanction_data.items():
                            update_parts.append(f"{col} = ?")
                            update_values.append(val)

                        if update_parts:
                            update_query = f"UPDATE Sanctions SET {', '.join(update_parts)} WHERE id_sanction = ?"
                            update_values.append(sanction_id)
                            cursor.execute(update_query, tuple(update_values))

                    # 5. Mettre à jour le dossier si des données sont fournies
                    if dossier_data:
                        update_parts = []
                        update_values = []

                        for col, val in dossier_data.items():
                            update_parts.append(f"{col} = ?")
                            update_values.append(val)

                        if update_parts:
                            update_query = f"UPDATE Dossiers SET {', '.join(update_parts)} WHERE matricule_dossier = ? AND reference = ?"
                            update_values.extend([matricule, reference])
                            cursor.execute(update_query, tuple(update_values))

                    # 6. Valider la transaction
                    cursor.execute("COMMIT")
                    logger.info(f"Dossier {reference} et sa sanction mis à jour avec succès")
                    return True

                except Exception as e:
                    cursor.execute("ROLLBACK")
                    logger.error(f"Erreur lors de la mise à jour du dossier et de la sanction : {str(e)}")
                    raise

        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du dossier et de la sanction : {str(e)}")
            return False

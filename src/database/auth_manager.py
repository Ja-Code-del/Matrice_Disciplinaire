# src/database/auth_manager.py

import sqlite3
import hashlib
import os
import json


class AuthManager:
    def __init__(self):
        self.db_path = "src/data/database/users.db"
        self.config_path = "src/data/database/auth_config.json"
        self.init_db()
        self.check_first_run()

    def init_db(self):
        """Initialise la base de données avec les tables nécessaires"""
        if not os.path.exists(os.path.dirname(self.db_path)):
            os.makedirs(os.path.dirname(self.db_path))

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Création de la table users avec la colonne approved_by
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                approved_by INTEGER,
                FOREIGN KEY (approved_by) REFERENCES users(id)
            )
        ''')

        # Création de la table pending_users
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pending_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def check_first_run(self):
        """Vérifie si c'est la première exécution"""
        if not os.path.exists(self.config_path):
            config = {"first_run": True}
            with open(self.config_path, 'w') as f:
                json.dump(config, f)
            return True

        with open(self.config_path, 'r') as f:
            config = json.load(f)
            return config.get("first_run", False)

    def set_first_run_completed(self):
        """Marque la première exécution comme terminée"""
        config = {"first_run": False}
        with open(self.config_path, 'w') as f:
            json.dump(config, f)

    def hash_password(self, password):
        """Hash le mot de passe avec SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def create_admin(self, username, password):
        """Crée le compte administrateur initial"""
        if not self.check_first_run():
            return False, "Un administrateur existe déjà"

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        password_hash = self.hash_password(password)

        try:
            cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, 'admin')",
                (username, password_hash)
            )
            conn.commit()
            self.set_first_run_completed()
            return True, "Administrateur créé avec succès"
        except sqlite3.IntegrityError:
            return False, "Erreur lors de la création de l'administrateur"
        finally:
            conn.close()

    def verify_credentials(self, username, password):
        """Vérifie les identifiants de connexion"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        password_hash = self.hash_password(password)

        cursor.execute(
            "SELECT id, username, role FROM users WHERE username=? AND password_hash=?",
            (username, password_hash)
        )

        user = cursor.fetchone()
        conn.close()

        if user:
            return True, {"id": user[0], "username": user[1], "role": user[2]}
        return False, None

    def request_account(self, username, password):
        """Crée une demande de compte"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        password_hash = self.hash_password(password)

        try:
            cursor.execute(
                "INSERT INTO pending_users (username, password_hash) VALUES (?, ?)",
                (username, password_hash)
            )
            conn.commit()
            return True, "Demande de compte créée avec succès"
        except sqlite3.IntegrityError:
            return False, "Nom d'utilisateur déjà utilisé"
        finally:
            conn.close()

    def get_pending_requests(self):
        """Récupère toutes les demandes de compte en attente"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT id, username, request_date FROM pending_users")
        requests = cursor.fetchall()

        conn.close()
        return requests

    def approve_user(self, request_id, admin_id, role='membre'):
        """
        Approuve une demande de compte utilisateur

        Args:
            request_id (int): L'ID de la demande à approuver
            admin_id (int): L'ID de l'admin qui approuve
            role (str): Le rôle à attribuer ('membre' ou 'admin')

        Returns:
            tuple: (success: bool, message: str)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT username, password_hash FROM pending_users WHERE id = ?",
                (request_id,)
            )
            user_info = cursor.fetchone()

            if user_info:
                cursor.execute(
                    "INSERT INTO users (username, password_hash, role, approved_by) VALUES (?, ?, ?, ?)",
                    (user_info[0], user_info[1], role, admin_id)
                )

                cursor.execute("DELETE FROM pending_users WHERE id = ?", (request_id,))

                conn.commit()
                return True, "Compte utilisateur approuvé"
            return False, "Demande non trouvée"

        except sqlite3.IntegrityError:
            return False, "Nom d'utilisateur déjà existant"
        except sqlite3.Error as e:
            return False, f"Erreur lors de l'approbation: {str(e)}"
        finally:
            conn.close()

    def reject_user(self, request_id):
        """Rejette une demande de compte"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM pending_users WHERE id = ?", (request_id,))
            conn.commit()
            return True
        except sqlite3.Error:
            return False
        finally:
            conn.close()



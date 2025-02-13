import os
import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QFileDialog,
                             QProgressBar, QMessageBox)
from src.database.db_manager import DatabaseManager
from src.utils.date_utils import adapt_date, calculate_age, parse_annee_service
import pandas as pd


class ImportWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IMPORT DU FICHIER EXCEL")
        self.setMinimumSize(600, 400)
        self.db_manager = DatabaseManager()

        # Ajout d'un fichier de log pour les erreurs
        self.log_file = "import_errors.txt"

        # Widget principal
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Bouton d'import
        import_button = QPushButton("Sélectionner le fichier Excel")
        import_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        import_button.clicked.connect(self.import_excel)
        layout.addWidget(import_button)

        # Barre de progression
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Label pour le statut
        self.status_label = QLabel()
        layout.addWidget(self.status_label)

        # Création de la base de données
        self.db_manager.create_tables()
        # Creation des index dans la BD
        self.db_manager.create_indexes()

    def import_excel(self):
        """Importe les données depuis le fichier Excel"""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner le fichier Excel",
            "",
            "Excel files (*.xlsx *.xls)"
        )

        if not file_name:
            return  # Si aucun fichier sélectionné, on annule l'import.

        try:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.status_label.setText("Lecture du fichier Excel...")

            df = pd.read_excel(file_name)
            total_rows = len(df)
            self.progress_bar.setMaximum(total_rows)

            # Supprimer les doublons avant conversion en CSV
            df = df.drop_duplicates()

            required_columns = {'REFERENCE', 'ANNEE DE PUNITION', 'N° ORDRE', 'N° ANNEE', 'ID DOSSIER', 'DATE ENR', 'MLE',
                               'NOM ET PRENOMS', 'GRADE', 'SEXE', 'DATE DE NAISSANCE', 'AGE', 'UNITE', 'LEGIONS', 'SUBDIV',
                               'REGIONS', 'DATE D\'ENTREE GIE', 'ANNEE DE SERVICE', 'SITUATION MATRIMONIALE', 'NB ENF',
                               'FAUTE COMMISE', 'DATE DES FAITS', 'LIBELLE', 'N° CAT', 'TYPE SANCTION', 'REFERENCE DU STATUT',
                               'N° DECISION', 'N° ARRETE', 'TAUX (JAR)', 'ANNEE DES FAITS', 'ANNEE RADIATION', 'COMITE',
                               'STATUT DOSSIER'}

            if not required_columns.issubset(df.columns):
                QMessageBox.critical(self, "Erreur", f"Le fichier Excel doit contenir les colonnes: {required_columns}")
                return

            # Créer un fichier CSV temporaire
            csv_file = file_name.replace('.xlsx', '.csv').replace('.xls', '.csv')
            df.to_csv(csv_file, index=False, sep=';', encoding='utf-8')

            # Convertir les colonnes de dates
            date_columns = ['DATE ENR', 'DATE DE NAISSANCE', 'DATE D\'ENTREE GIE', 'DATE DES FAITS', ]
            for col in date_columns:
                df[col] = df[col].apply(adapt_date)

            # Extraire l'année pour les colonnes qui doivent être des années
            df['ANNEE DES FAITS'] = df['ANNEE DES FAITS'].fillna(0).astype(int)  # Corrige float64 en int64
            df['ANNEE RADIATION'] = df['ANNEE RADIATION'].fillna(0).astype(int)

            # Convertir `AGE` en nombre entier
            df['AGE'] = pd.to_numeric(df['AGE'], errors='coerce').fillna(0).astype(int)

            # Vérifier si certaines colonnes censées être numériques contiennent des valeurs erronées
            cols_to_int = ['ANNEE DE PUNITION', 'N° ORDRE', 'MLE', 'AGE', 'ANNEE DE SERVICE', 'NB ENF', 'N° CAT',
                           'ANNEE DES FAITS', 'ANNEE RADIATION']
            for col in cols_to_int:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

            success_count = 0
            error_count = 0

            db = DatabaseManager()

            # Préparation des données sous forme de liste de tuples pour executemany()
            data = []
            for _, row in df.iterrows():
                try:
                    # Vérifier et récupérer les IDs des clés étrangères
                    statut_id = db.get_foreign_key_id("Statut", "lib_statut", row["Statut"])
                    sanction_id = db.get_foreign_key_id("Type_sanctions", "lib_type_sanction", row["Type de Sanction"])
                    grade_id = db.get_foreign_key_id("Grade", "lib_grade", row["Grade"])
                    faute_id = db.get_foreign_key_id("Fautes", "lib_faute", row["Faute"])

                    #TODO AJOUTER LES LIGNES POUR LES AUTRES TABLES DE REFERENCE ET CONTINUER A MODIFIER IMPORT AVEC
                    # NOTAMMMENT LA METHODE ADD_DATA

                    if not (statut_id and sanction_id and grade_id and faute_id):
                        raise ValueError("Une ou plusieurs valeurs de référence sont inconnues.")

                    success_count += 1
                except Exception as e:
                    error_count += 1
                    print(f"Erreur sur la ligne {_ + 2}: {str(e)}")

                # Mise à jour de la barre de progression en direct
                self.progress_bar.setValue(success_count + error_count)

            # Connexion à la base de données
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                query = '''
                        INSERT INTO main_tab (
                            numero_dossier, annee_punition, numero_ordre, date_enr, matricule,
                            nom_prenoms, grade, sexe, age, date_naissance, unite, legions,
                            subdiv, regions, date_entree_gie, annee_service, situation_matrimoniale,
                            nb_enfants, faute_commise, date_faits, categorie, statut,
                            reference_statut, taux_jar, comite, annee_faits
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    '''

                # Exécution avec executemany() et transaction
                try:
                    cursor.executemany(query, data)
                    conn.commit()
                    self.progress_bar.setValue(100)
                    self.status_label.setText("Import terminé avec succès!")
                    QMessageBox.information(self, "Succès", "Les données ont été importées avec succès!")
                except Exception as e:
                    conn.rollback()  # Rollback en cas d'erreur
                    QMessageBox.critical(self, "Erreur", f"Erreur lors de l'import : {str(e)}")
                    self.status_label.setText("Erreur lors de l'import")
                    print(f"Erreur détaillée : {str(e)}")

            # Supprimer le fichier CSV temporaire
            os.remove(csv_file)

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'import : {str(e)}")
            self.status_label.setText("Erreur lors de l'import")
            print(f"Erreur détaillée : {str(e)}")

    def update_stats(self, total, success, errors):
        """
        Met à jour les statistiques d'import en temps réel
        Args:
            total: Nombre total de lignes à traiter
            success: Nombre de lignes importées avec succès
            errors: Nombre d'erreurs
        """
        progress = (success + errors) * 100 // total if total > 0 else 0
        self.progress_bar.setValue(progress)
        self.status_label.setText(
            f"Total : {total} | "
            f"Succès : {success} | "
            f"Erreurs : {errors} | "
            f"Progression : {progress}%"
        )




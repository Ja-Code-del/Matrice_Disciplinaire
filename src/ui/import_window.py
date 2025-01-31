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
        self.setWindowTitle("Import des données gendarmes")
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

            # Créer un fichier CSV temporaire
            csv_file = file_name.replace('.xlsx', '.csv').replace('.xls', '.csv')
            df.to_csv(csv_file, index=False, sep=';', encoding='utf-8')

            # Convertir les colonnes de dates
            date_columns = ['DATE ENR', 'DATE DE NAISSANCE', 'DATE D\'ENTREE GIE', 'DATE DES FAITS']
            for col in date_columns:
                df[col] = df[col].apply(adapt_date)

            success_count = 0
            error_count = 0

            # Préparation des données sous forme de liste de tuples pour executemany()
            data = []
            for _, row in df.iterrows():
                try:
                    data.append((
                        str(row['N° DOSSIER']),
                        int(row['ANNEE DE PUNITION']) if pd.notna(row['ANNEE DE PUNITION']) else None,
                        int(row['N° ORDRE']) if pd.notna(row['N° ORDRE']) else None,
                        row['DATE ENR'] if pd.notna(row['DATE ENR']) else None,
                        int(row['MLE']) if pd.notna(row['MLE']) else None,
                        str(row['NOM ET PRENOMS']) if pd.notna(row['NOM ET PRENOMS']) else None,
                        str(row['GRADE']) if pd.notna(row['GRADE']) else None,
                        str(row['SEXE']) if pd.notna(row['SEXE']) else None,
                        row['DATE DE NAISSANCE'] if pd.notna(row['DATE DE NAISSANCE']) else None,
                        int(row['AGE']) if pd.notna(row['AGE']) else None,
                        str(row['UNITE']) if pd.notna(row['UNITE']) else None,
                        str(row['LEGIONS']) if pd.notna(row['LEGIONS']) else None,
                        str(row['SUBDIV']) if pd.notna(row['SUBDIV']) else None,
                        str(row['REGIONS']) if pd.notna(row['REGIONS']) else None,
                        row['DATE D\'ENTREE GIE'] if pd.notna(row['DATE D\'ENTREE GIE']) else None,
                        int(row['ANNEE DE SERVICE']) if pd.notna(row['ANNEE DE SERVICE']) else None,
                        str(row['SITUATION MATRIMONIALE']) if pd.notna(row['SITUATION MATRIMONIALE']) else None,
                        int(row['NB ENF']) if pd.notna(row['NB ENF']) else None,
                        str(row['FAUTE COMMISE']) if pd.notna(row['FAUTE COMMISE']) else None,
                        row['DATE DES FAITS'] if pd.notna(row['DATE DES FAITS']) else None,
                        int(row['N° CAT']) if pd.notna(row['N° CAT']) else None,
                        str(row['STATUT']) if pd.notna(row['STATUT']) else None,
                        str(row['REFERENCE DU STATUT']) if pd.notna(row['REFERENCE DU STATUT']) else None,
                        str(row['TAUX (JAR)']) if pd.notna(row['TAUX (JAR)']) else None,
                        str(row['COMITE']) if pd.notna(row['COMITE']) else None,
                        int(row['ANNEE DES FAITS']) if pd.notna(row['ANNEE DES FAITS']) else None
                    ))
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
                            nom_prenoms, grade, sexe, date_naissance, age, unite, legions,
                            subdiv, regions, date_entree_gie, annee_service, situation_matrimoniale,
                            nb_enfants, faute_commise, date_faits, categorie, statut,
                            reference_statut, taux_jar, comite, annee_faits
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    '''

                # Exécution en batch avec executemany() et transaction
                try:
                    cursor.executemany(query, data)
                    conn.commit()
                    self.status_label.setText("Import terminé avec succès!")
                    QMessageBox.information(self, "Succès", "Les données ont été importées avec succès!")
                except Exception as e:
                    conn.rollback()  # Rollback en cas d'erreur
                    QMessageBox.critical(self, "Erreur", f"Erreur lors de l'import : {str(e)}")
                    self.status_label.setText("Erreur lors de l'import")
                    print(f"Erreur détaillée : {str(e)}")

            self.progress_bar.setValue(100)

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




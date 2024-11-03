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

        if file_name:
            try:
                self.progress_bar.setVisible(True)
                self.progress_bar.setValue(0)
                self.status_label.setText("Lecture du fichier Excel...")

                df = pd.read_excel(file_name)
                total_rows = len(df)
                self.progress_bar.setMaximum(100)

                success_count = 0
                error_count = 0

                with self.db_manager.get_connection() as conn:
                    cursor = conn.cursor()

                    # Préparation des données des sanctions (informations uniques)
                    sanctions_df = df[[
                        'N° DOSSIER',
                        'ANNEE DE PUNITION',
                        'N° ORDRE',
                        'DATE ENR',
                        'MLE',
                        'FAUTE COMMISE',
                        'DATE DES FAITS',
                        'N° CAT',
                        'STATUT',
                        'REFERENCE DU STATUT',
                        'TAUX (JAR)',
                        'COMITE',
                        'ANNEE DES FAITS'
                    ]].drop_duplicates()

                    self.progress_bar.setValue(30)
                    self.status_label.setText("Import des données gendarmes...")

                    # Import des gendarmes
                    for _, row in sanctions_df.iterrows():
                        try:
                            print("On est avant execute")
                            cursor.execute('''
                                INSERT INTO sanctions (
                                    numero_dossier,
                                    annee_punition,
                                    numero_ordre,
                                    date_enr,
                                    matricule,
                                    faute_commise,
                                    date_faits,
                                    categorie,
                                    statut,
                                    reference_statut,
                                    taux_jar,
                                    comite,
                                    annee_faits
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (
                                str(row['N° DOSSIER']),
                                int(row['ANNEE DE PUNITION']) if pd.notna(row['ANNEE DE PUNITION']) else None,
                                int(row['N° ORDRE']) if pd.notna(row['N° ORDRE']) else None,
                                adapt_date(row['DATE ENR']) if pd.notna(row['DATE ENR']) else None,
                                int(row['MLE']) if pd.notna(row['MLE']) else None,
                                #str(row['NOM ET PRENOMS']),
                                # str(row['GRADE']),
                                # str(row['SEXE']),
                                # adapt_date(row['DATE DE NAISSANCE']),
                                # int(row['AGE']) if pd.notna(row['AGE']) else None,
                                # str(row['UNITE']),
                                # str(row['LEGIONS']),
                                # str(row['SUBDIV']),
                                # str(row['REGIONS']),
                                # adapt_date(row['DATE D\'ENTREE GIE']),
                                # str(row['ANNEE DE SERVICE']),
                                # str(row['SITUATION MATRIMONIALE']),
                                # int(row['NB ENF']) if pd.notna(row['NB ENF']) else None,
                                str(row['FAUTE COMMISE']) if pd.notna(row['FAUTE COMMISE']) else None,
                                adapt_date(row['DATE DES FAITS']) if pd.notna(row['DATE DES FAITS']) else None,
                                int(row['N° CAT']) if pd.notna(row['N° CAT']) else None,
                                str(row['STATUT']) if pd.notna(row['STATUT']) else None,
                                str(row['REFERENCE DU STATUT']) if pd.notna(row['REFERENCE DU STATUT']) else None,
                                str(row['TAUX (JAR)']) if pd.notna(row['TAUX (JAR)']) else None,
                                str(row['COMITE']) if pd.notna(row['COMITE']) else None,
                                int(row['ANNEE DES FAITS']) if pd.notna(row['ANNEE DES FAITS']) else None
                            ))
                            print(f'{success_count} tache terminée')
                            success_count += 1
                            self.progress_bar.setValue(success_count)
                            self.update_stats(total_rows, success_count, error_count)

                        except Exception as e:
                            error_count += 1
                            print(f"Erreur sur la ligne {_ + 2}: {str(e)}")

                    conn.commit()

                    self.progress_bar.setValue(100)
                    self.status_label.setText("Import terminé avec succès!")
                    QMessageBox.information(self, "Succès", "Les données ont été importées avec succès!")

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

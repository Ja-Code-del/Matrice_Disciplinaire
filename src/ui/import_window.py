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
                self.progress_bar.setMaximum(total_rows)

                success_count = 0
                error_count = 0

                with self.db_manager.get_connection() as conn:
                    cursor = conn.cursor()

                    # Préparation des données gendarmes (informations uniques)
                    gendarmes_df = df[[
                        'N° DE RADIATION',
                        'MLE',
                        'NOM ET PRENOMS',
                        'GRADE',
                        'SEXE',
                        'DATE DE NAISSANCE',
                        'AGE',
                        'UNITE',
                        'LEG',
                        'SUB',
                        'RG',
                        'LEGIONS',
                        'SUBDIV',
                        'REGIONS',
                        'DATE D\'ENTREE GIE',
                        'ANNEE DE SERVICE',
                        'SITUATION MATRIMONIALE',
                        'NB ENF'
                    ]].drop_duplicates()

                    self.progress_bar.setValue(30)
                    self.status_label.setText("Import des données gendarmes...")

                    # Import des gendarmes
                    for _, row in gendarmes_df.iterrows():
                        try:
                            cursor.execute('''
                                INSERT OR REPLACE INTO sanctions (
                                    numero_dossier,
                                    numero_radiation,
                                    annee_punition,
                                    numero,
                                    numero_l,
                                    date_enr,
                                    matricule,
                                    nom_prenoms,
                                    grade,
                                    sexe,
                                    date_naissance,
                                    age,
                                    unite,
                                    leg,
                                    sub,
                                    rg,
                                    legions,
                                    subdiv,
                                    regions,
                                    date_entree_gie,
                                    annee_service,
                                    situation_matrimoniale,
                                    nb_enfants,
                                    faute_commise,
                                    date_faits,
                                    numero_cat,
                                    statut,
                                    reference_statut,
                                    taux_jar,
                                    comite,
                                    annee_faits
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                str(row['N° DOSSIER']),
                                str(row['N° DE RADIATION']),
                                int(row['ANNEE DE PUNITION']) if pd.notna(row['ANNEE DE PUNITION']) else None,
                                str(row['N°']),
                                str(row['N° L']),
                                adapt_date(row['DATE ENR']),
                                str(row['MLE']),
                                str(row['NOM ET PRENOMS']),
                                str(row['GRADE']),
                                str(row['SEXE']),
                                adapt_date(row['DATE DE NAISSANCE']),
                                int(row['AGE']) if pd.notna(row['AGE']) else None,
                                str(row['UNITE']),
                                str(row['LEG']),
                                str(row['SUB']),
                                str(row['RG']),
                                str(row['LEGIONS']),
                                str(row['SUBDIV']),
                                str(row['REGIONS']),
                                adapt_date(row['DATE D\'ENTREE GIE']),
                                str(row['ANNEE DE SERVICE']),
                                str(row['SITUATION MATRIMONIALE']),
                                int(row['NB ENF']) if pd.notna(row['NB ENF']) else None,
                                str(row['FAUTE COMMISE']),
                                adapt_date(row['DATE DES FAITS']),
                                str(row['N° CAT']),
                                str(row['STATUT']),
                                str(row['REFERENCE DU STATUT']),
                                str(row['TAUX (JAR)']) if pd.notna(row['TAUX (JAR)']) else None,
                                str(row['COMITE']),
                                int(row['ANNEE DES FAITS']) if pd.notna(row['ANNEE DES FAITS']) else None
                            ))
                            success_count += 1

                        except Exception as e:
                            error_count += 1
                            print(f"Erreur sur la ligne {_ + 2}: {str(e)}")

                        self.progress_bar.setValue(success_count)
                        self.update_stats(total_rows, success_count, error_count)

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

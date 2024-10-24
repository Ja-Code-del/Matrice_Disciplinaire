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

                # Lecture du fichier Excel
                df = pd.read_excel(file_name)

                with self.db_manager.get_connection() as conn:
                    cursor = conn.cursor()

                    # Préparation des données gendarmes (informations uniques)
                    gendarmes_df = df[[
                        'N° DE RADIATION', 'MLE', 'NOM ET PRENOMS', 'GRADE', 'SEXE',
                        'DATE DE NAISSANCE', 'AGE', 'UNITE', 'LEG', 'SUB', 'RG',
                        'LEGIONS', 'SUBDIV', 'REGIONS', 'DATE D\'ENTREE GIE',
                        'ANNEE DE SERVICE', 'SITUATION MATRIMONIALE', 'NB ENF'
                    ]].drop_duplicates()

                    self.progress_bar.setValue(30)
                    self.status_label.setText("Import des données gendarmes...")

                    # Import des gendarmes
                    for _, row in gendarmes_df.iterrows():
                        try:
                            date_naissance = row['DATE DE NAISSANCE']
                            age = calculate_age(date_naissance)
                            if age is None and date_naissance:  # Si la date existe mais n'est pas valide
                                print(
                                    f"Attention : Date de naissance invalide pour {row['NOM ET PRENOMS']} ({date_naissance})")

                            cursor.execute('''
                                INSERT OR IGNORE INTO gendarmes (
                                    numero_radiation, mle, nom_prenoms, grade, sexe,
                                    date_naissance, age, unite, leg, sub, rg,
                                    legions, subdiv, regions, date_entree_gie,
                                    annee_service, situation_matrimoniale, nb_enfants
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                str(row['N° DE RADIATION']), str(row['MLE']), str(row['NOM ET PRENOMS']),
                                str(row['GRADE']), str(row['SEXE']), date_naissance,
                                age,  # Sera None si la date est invalide
                                str(row['UNITE']), str(row['LEG']), str(row['SUB']),
                                str(row['RG']), str(row['LEGIONS']), str(row['SUBDIV']), str(row['REGIONS']),
                                adapt_date(row['DATE D\'ENTREE GIE']),
                                parse_annee_service(row['ANNEE DE SERVICE']),
                                str(row['SITUATION MATRIMONIALE']),
                                int(row['NB ENF']) if pd.notna(row['NB ENF']) else None
                            ))
                        except Exception as e:
                            print(f"Erreur lors du traitement de la ligne pour {row['NOM ET PRENOMS']}: {str(e)}")
                            continue

                    self.progress_bar.setValue(60)
                    self.status_label.setText("Import des sanctions...")

                    sanctions_count = 0
                    failed_sanctions = []

                    # Import des sanctions
                    for _, row in df.iterrows():
                        try:
                            # Récupération de l'ID du gendarme
                            cursor.execute(
                                "SELECT id FROM gendarmes WHERE numero_radiation = ? AND mle = ?",
                                (str(row['N° DE RADIATION']), str(row['MLE']))
                            )
                            result = cursor.fetchone()

                            if result:
                                gendarme_id = result[0]
                                try:
                                    cursor.execute('''
                                        INSERT INTO sanctions (
                                            gendarme_id, annee_punition, numero, numero_l,
                                            date_enr, faute_commise, date_faits, numero_cat,
                                            statut, reference_statut, taux_jar, comite,
                                            annee_faits
                                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                    ''', (
                                        gendarme_id,
                                        int(row['ANNEE DE PUNITION']) if pd.notna(row['ANNEE DE PUNITION']) else None,
                                        str(row['N°']),
                                        str(row['N° L']),
                                        adapt_date(row['DATE ENR']),
                                        str(row['FAUTE COMMISE']),
                                        adapt_date(row['DATE DES FAITS']),
                                        str(row['N° CAT']),
                                        str(row['STATUT']),
                                        str(row['REFERENCE DU STATUT']),
                                        int(row['TAUX (JAR)']) if pd.notna(row['TAUX (JAR)']) else None,
                                        str(row['COMITE']),
                                        int(row['ANNEE DES FAITS']) if pd.notna(row['ANNEE DES FAITS']) else None
                                    ))
                                    sanctions_count += 1
                                except Exception as e:
                                    error_info = {
                                        'n_radiation': row['N° DE RADIATION'],
                                        'mle': row['MLE'],
                                        'error': str(e)
                                    }
                                    failed_sanctions.append(error_info)
                            else:
                                error_info = {
                                    'n_radiation': row['N° DE RADIATION'],
                                    'mle': row['MLE'],
                                    'error': "Gendarme non trouvé"
                                }
                                failed_sanctions.append(error_info)

                        except Exception as e:
                            error_info = {
                                'n_radiation': row['N° DE RADIATION'],
                                'mle': row['MLE'],
                                'error': f"Erreur générale: {str(e)}"
                            }
                            failed_sanctions.append(error_info)

                    # Écriture des erreurs dans un fichier
                    if failed_sanctions:
                        with open(self.log_file, 'w', encoding='utf-8') as f:
                            f.write("=== Sanctions non importées ===\n\n")
                            for error in failed_sanctions:
                                f.write(f"N° Radiation: {error['n_radiation']}\n")
                                f.write(f"MLE: {error['mle']}\n")
                                f.write(f"Erreur: {error['error']}\n")
                                f.write("-" * 50 + "\n")

                        print(f"Nombre de sanctions importées avec succès: {sanctions_count}")
                        print(f"Nombre de sanctions non importées: {len(failed_sanctions)}")
                        print(f"Les détails des erreurs ont été enregistrés dans {self.log_file}")

                        QMessageBox.warning(
                            self,
                            "Import partiel",
                            f"{sanctions_count} sanctions importées avec succès.\n"
                            f"{len(failed_sanctions)} sanctions n'ont pas pu être importées.\n"
                            f"Consultez le fichier {self.log_file} pour plus de détails."
                        )

                    conn.commit()
                    self.progress_bar.setValue(100)
                    self.status_label.setText("Import terminé avec succès!")
                    QMessageBox.information(self, "Succès", "Les données ont été importées avec succès!")

            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de l'import : {str(e)}")
                self.status_label.setText("Erreur lors de l'import")
                print(f"Erreur détaillée : {str(e)}")
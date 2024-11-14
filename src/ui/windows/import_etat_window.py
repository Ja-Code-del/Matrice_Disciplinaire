#import_etat_window

import pandas as pd
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMessageBox, QWidget, QGridLayout, QProgressBar, QLabel, QVBoxLayout, QMainWindow


class ImportEtatCompletWindow(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setWindowTitle("Importer Matrice Gendarmes")
        self.setMinimumSize(600, 300)
        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Status label
        self.status_label = QLabel("Préparation de l'import...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(self.status_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ccc;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #007bff;
            }
        """)
        layout.addWidget(self.progress_bar)

        # Stats labels avec style moderne
        stats_container = QWidget()
        stats_layout = QGridLayout(stats_container)

        self.total_label = QLabel()
        self.success_label = QLabel()
        self.error_label = QLabel()

        for label in [self.total_label, self.success_label, self.error_label]:
            label.setStyleSheet("""
                QLabel {
                    padding: 10px;
                    background: #f8f9fa;
                    border-radius: 5px;
                    margin: 5px;
                }
            """)

        stats_layout.addWidget(self.total_label, 0, 0)
        stats_layout.addWidget(self.success_label, 0, 1)
        stats_layout.addWidget(self.error_label, 0, 2)

        layout.addWidget(stats_container)

    def import_file(self, file_path):
        try:
            self.status_label.setText("Lecture du fichier Excel...")
            df = pd.read_excel(file_path)
            total_rows = len(df)
            self.progress_bar.setMaximum(total_rows)

            success_count = 0
            error_count = 0

            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()

                # Création de la table avec les bonnes colonnes
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS gendarmes_etat (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        matricule TEXT UNIQUE,
                        nom TEXT,
                        prenoms TEXT,
                        date_naissance DATE,
                        lieu_naissance TEXT,
                        date_entree_service DATE,
                        sexe TEXT
                    )
                """)

                for index, row in df.iterrows():
                    try:
                        cursor.execute("""
                            INSERT OR REPLACE INTO gendarmes_etat (
                                nom, prenoms, matricule, date_naissance,
                                lieu_naissance, date_entree_service, sexe
                            ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            str(row['NOM']),
                            str(row['PRENOMS']),
                            str(row['MATRICULE']),
                            pd.to_datetime(row['DATE DE NAISSANCE']) if pd.notna(row['DATE DE NAISSANCE']) else None,
                            str(row['LIEU DE NAISSANCE']),
                            pd.to_datetime(row['DATE ENTREE GIE']) if pd.notna(row['DATE ENTREE GIE']) else None,
                            str(row['SEXE'])
                        ))
                        success_count += 1

                    except Exception as e:
                        error_count += 1
                        print(
                            f"Erreur sur la ligne {index + 2}: {str(e)}")  # +2 car Excel commence à 1 et il y a l'entête

                    self.progress_bar.setValue(index + 1)
                    self.update_stats(total_rows, success_count, error_count)

                conn.commit()

            if error_count == 0:
                QMessageBox.information(self, "Succès",
                                        f"Import terminé avec succès!\n{success_count} gendarmes importés dans la base.")
            else:
                QMessageBox.warning(self, "Import partiel",
                                    f"Import terminé avec {error_count} erreurs.\n"
                                    f"{success_count} gendarmes importés avec succès.\n"
                                    "Consultez la console pour les détails des erreurs.")

        except Exception as e:
            QMessageBox.critical(self, "Erreur",
                                 f"Erreur lors de l'import : {str(e)}")
            print(f"Erreur détaillée : {str(e)}")

        finally:
            self.status_label.setText("Import terminé")

    def update_stats(self, total, success, errors):
        self.total_label.setText(f"📊 Total : {total}")
        self.success_label.setText(f"✅ Succès : {success}")
        self.error_label.setText(f"❌ Erreurs : {errors}")

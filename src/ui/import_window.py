import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QFileDialog,
                             QProgressBar, QMessageBox)
from src.database.db_manager import DatabaseManager
from src.utils.date_utils import adapt_date, calculate_age, parse_annee_service
from PyQt6.QtCore import QThread, pyqtSignal
import pandas as pd


class DataImportThread(QThread):
    progress = pyqtSignal(int)  # Signal pour mettre à jour la progression
    status = pyqtSignal(str)  # Signal pour mettre à jour le statut
    finished = pyqtSignal(bool, str)  # Signal pour indiquer la fin ou l'annulation

    def __init__(self, db_manager, file_name, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.file_name = file_name
        self.is_cancelled = False  # Drapeau pour annuler l'opération

    def run(self):
        try:
            # Lecture du fichier Excel
            self.status.emit("Lecture du fichier Excel...")
            df = pd.read_excel(self.file_name)

            # Vérification des colonnes
            required_columns = ['N° DOSSIER', 'ANNEE DE PUNITION', 'MLE']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Colonnes manquantes : {', '.join(missing_columns)}")

            total_rows = len(df)
            if total_rows == 0:
                raise ValueError("Le fichier Excel est vide.")

            self.status.emit("Préparation des données...")
            sanctions = self.prepare_sanctions(df)

            # Connexion à la base de données
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                for i, row in enumerate(sanctions):
                    if self.is_cancelled:  # Vérifier si l'annulation a été demandée
                        self.status.emit("Import annulé par l'utilisateur.")
                        self.finished.emit(False, "Importation annulée.")
                        return

                    # Insertion dans la base
                    cursor.execute(
                        "INSERT INTO sanctions (numero_dossier, annee_punition, matricule) VALUES (?, ?, ?)",
                        (row['N° DOSSIER'], row['ANNEE DE PUNITION'], row['MLE'])
                    )

                    # Mise à jour de la progression
                    progress = (i + 1) * 100 // total_rows
                    self.progress.emit(progress)

                conn.commit()

            self.status.emit("Import terminé avec succès!")
            self.finished.emit(True, "Les données ont été importées avec succès!")

        except Exception as e:
            self.finished.emit(False, f"Erreur : {str(e)}")

    def prepare_sanctions(self, df):
        return df[['N° DOSSIER', 'ANNEE DE PUNITION', 'MLE']].drop_duplicates().to_dict('records')

    def cancel(self):
        """Définit le drapeau d'annulation à True pour interrompre le thread."""
        self.is_cancelled = True


class ImportWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Import des données gendarmes")
        self.setMinimumSize(600, 400)
        self.db_manager = DatabaseManager()

        # UI setup
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        self.import_button = QPushButton("Sélectionner le fichier Excel")
        self.import_button.clicked.connect(self.select_file)
        layout.addWidget(self.import_button)

        self.cancel_button = QPushButton("Annuler l'import")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self.confirm_cancel)
        layout.addWidget(self.cancel_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel()
        layout.addWidget(self.status_label)

        self.db_manager.create_tables()
        self.thread = None

    def select_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Sélectionner le fichier Excel", "", "Excel files (*.xlsx *.xls)"
        )
        if file_name:
            self.start_import(file_name)

    def start_import(self, file_name):
        # Préparer l'interface
        self.import_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Démarrage de l'import...")

        # Démarrer le thread
        self.thread = DataImportThread(self.db_manager, file_name)
        self.thread.progress.connect(self.progress_bar.setValue)
        self.thread.status.connect(self.status_label.setText)
        self.thread.finished.connect(self.import_finished)
        self.thread.start()

    def confirm_cancel(self):
        """Affiche une boîte de confirmation avant d'annuler."""
        reply = QMessageBox.question(
            self,
            "Confirmer l'annulation",
            "Voulez-vous vraiment annuler l'importation ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.cancel_import()

    def cancel_import(self):
        """Interrompt le processus d'import en cours."""
        if self.thread:
            self.thread.cancel()
            self.status_label.setText("Annulation en cours...")

    def import_finished(self, success, message):
        # Nettoyage du thread
        self.thread = None

        # Mettre à jour l'interface
        self.import_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.progress_bar.setVisible(False)

        if success:
            QMessageBox.information(self, "Succès", message)
        else:
            QMessageBox.warning(self, "Annulation", message)


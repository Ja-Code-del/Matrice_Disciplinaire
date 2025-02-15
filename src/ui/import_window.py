from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                             QPushButton, QLabel, QFileDialog,
                             QProgressBar, QMessageBox)
from PyQt6.QtCore import QThread, pyqtSignal
from src.database.db_manager import DatabaseManager
from .excel_import import DataImporter, ImportResult


class ImportThread(QThread):
    progress = pyqtSignal(int, int, int)  # total, success, errors
    finished = pyqtSignal(object)  # ImportResult

    def __init__(self, importer, file_path):
        super().__init__()
        self.importer = importer
        self.file_path = file_path

    def run(self):
        result = self.importer.import_excel_file(
            self.file_path,
            progress_callback=lambda t, s, e: self.progress.emit(t, s, e)
        )
        self.finished.emit(result)


class ImportWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Import du fichier Excel")
        self.setMinimumSize(600, 400)

        # Initialisation des gestionnaires
        self.db_manager = DatabaseManager()
        self.data_importer = DataImporter(self.db_manager)

        # Configuration de l'interface
        self.setup_ui()

        # Création de la base de données et des index
        self.db_manager.create_tables()
        self.db_manager.create_indexes()

    def setup_ui(self):
        """Configure l'interface utilisateur"""
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
        import_button.clicked.connect(self.start_import)
        layout.addWidget(import_button)

        # Barre de progression
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Label pour le statut
        self.status_label = QLabel()
        layout.addWidget(self.status_label)

    def start_import(self):
        """Démarre le processus d'import"""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner le fichier Excel",
            "",
            "Excel files (*.xlsx *.xls)"
        )

        if not file_name:
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Import en cours...")

        # Création et démarrage du thread d'import
        self.import_thread = ImportThread(self.data_importer, file_name)
        self.import_thread.progress.connect(self.update_progress)
        self.import_thread.finished.connect(self.import_finished)
        self.import_thread.start()

    def update_progress(self, total, success, errors):
        """Met à jour la barre de progression et les statistiques d'import"""
        if total > 0:
            progress = ((success + errors) * 100) // total
            self.progress_bar.setValue(progress)
            self.status_label.setText(
                f"Total : {total} | "
                f"Succès : {success} | "
                f"Erreurs : {errors} | "
                f"Progression : {progress}%"
            )

    def import_finished(self, result: ImportResult):
        """Gère la fin de l'import"""
        if result.success:
            self.progress_bar.setValue(100)
            details = result.details
            message = (
                f"Import terminé avec succès!\n"
                f"Total traité : {details['total_rows']} lignes\n"
                f"Succès : {details['success_count']} lignes\n"
                f"Erreurs : {details['error_count']} lignes"
            )
            QMessageBox.information(self, "Succès", message)
        else:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'import : {result.message}")

        self.status_label.setText("Import terminé")
        self.progress_bar.setVisible(False)


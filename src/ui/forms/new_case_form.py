# src/ui/forms/new_case_form.py

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                             QLabel, QMessageBox)


class NewCaseForm(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setWindowTitle("Nouveau Dossier de Sanction")
        self.setMinimumSize(1200, 800)
        self.init_ui()

    def init_ui(self):
        # Widget principal
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Message temporaire
        temp_label = QLabel("Formulaire en construction...")
        temp_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #666;
                padding: 20px;
            }
        """)
        layout.addWidget(temp_label)

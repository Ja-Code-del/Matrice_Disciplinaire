from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTableWidget, QTableWidgetItem, \
    QPushButton, QMessageBox


class DeleteCaseDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("Supprimer un dossier")
        self.setMinimumSize(800, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Champ de recherche
        search_layout = QHBoxLayout()
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Entrez le numéro de dossier ou le matricule")
        search_button = QPushButton("Rechercher")
        search_button.clicked.connect(self.search_cases)
        search_layout.addWidget(self.search_field)
        search_layout.addWidget(search_button)
        layout.addLayout(search_layout)

        # Tableau des résultats
        self.cases_table = QTableWidget()
        self.cases_table.setColumnCount(5)
        self.cases_table.setHorizontalHeaderLabels(
            ["Numéro Dossier", "Matricule", "Faute Commise", "Statut", "Sélectionner"])
        self.cases_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.cases_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.cases_table)

        # Boutons
        button_layout = QHBoxLayout()
        self.delete_button = QPushButton("Supprimer")
        self.delete_button.clicked.connect(self.delete_selected_cases)
        self.cancel_button = QPushButton("Annuler")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.delete_button)
        layout.addLayout(button_layout)

    def search_cases(self):
        """Effectue la recherche de dossiers et remplit le tableau"""
        # Implémentez la logique de recherche dans la base de données ici
        pass

    def delete_selected_cases(self):
        """Supprime les dossiers sélectionnés"""
        # Implémentez la logique de suppression des dossiers ici
        pass

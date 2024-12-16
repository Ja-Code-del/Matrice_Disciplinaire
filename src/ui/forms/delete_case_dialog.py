from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTableWidget, QTableWidgetItem, \
    QPushButton, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal


class DeleteCaseDialog(QDialog):
    case_deleted = pyqtSignal()  # Signal émis quand un dossier est supprimé

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
        search_text = self.search_field.text().strip()
        if not search_text:
            QMessageBox.warning(self, "Attention", "Veuillez entrer un numéro de dossier ou un matricule")
            return

        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()

                # Recherche par numéro de dossier ou matricule
                query = """
                    SELECT s.numero_dossier, s.matricule, s.faute_commise, s.statut
                    FROM sanctions s
                    WHERE s.numero_dossier LIKE ? OR s.matricule LIKE ?
                    ORDER BY s.date_enr DESC
                """
                cursor.execute(query, (f"%{search_text}%", f"%{search_text}%"))
                results = cursor.fetchall()

                # Remplir le tableau avec les résultats
                self.cases_table.setRowCount(len(results))
                for row, result in enumerate(results):
                    for col, value in enumerate(result):
                        item = QTableWidgetItem(str(value))
                        self.cases_table.setItem(row, col, item)

                    # Ajouter une case à cocher dans la dernière colonne
                    checkbox = QTableWidgetItem()
                    checkbox.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
                    checkbox.setCheckState(Qt.CheckState.Unchecked)
                    self.cases_table.setItem(row, 4, checkbox)

                if not results:
                    QMessageBox.information(self, "Information", "Aucun dossier trouvé")

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la recherche : {str(e)}")

    def delete_selected_cases(self):
        """Supprime les dossiers sélectionnés"""
        selected_rows = []
        for row in range(self.cases_table.rowCount()):
            checkbox_item = self.cases_table.item(row, 4)
            if checkbox_item and checkbox_item.checkState() == Qt.CheckState.Checked:
                numero_dossier = self.cases_table.item(row, 0).text()
                selected_rows.append((row, numero_dossier))

        if not selected_rows:
            QMessageBox.warning(self, "Attention", "Veuillez sélectionner au moins un dossier à supprimer")
            return

        # Confirmation de suppression
        confirm = QMessageBox.question(
            self,
            "Confirmation",
            f"Êtes-vous sûr de vouloir supprimer {len(selected_rows)} dossier(s) ?\n"
            "Cette action est irréversible.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                with self.db_manager.get_connection() as conn:
                    cursor = conn.cursor()

                    for _, numero_dossier in selected_rows:
                        # Supprimer les enregistrements liés au dossier
                        cursor.execute(
                            "DELETE FROM sanctions WHERE numero_dossier = ?",
                            (numero_dossier,)
                        )

                    conn.commit()

                    QMessageBox.information(
                        self,
                        "Succès",
                        f"{len(selected_rows)} dossier(s) supprimé(s) avec succès"
                    )

                    # Rafraîchir la recherche
                    self.case_deleted.emit()  # Émettre le signal après une suppression réussie
                    self.search_cases()

            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Erreur",
                    f"Erreur lors de la suppression : {str(e)}"
                )

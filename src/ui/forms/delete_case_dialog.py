from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTableWidget, QTableWidgetItem, \
    QPushButton, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal
import logging

logger = logging.getLogger(__name__)


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
        self.search_field.setPlaceholderText("Entrez le numéro de dossier ou le matricule à supprimer")
        self.search_field.returnPressed.connect(self.search_cases)
        search_button = QPushButton("Rechercher")
        search_button.clicked.connect(self.search_cases)
        search_layout.addWidget(self.search_field)
        search_layout.addWidget(search_button)
        layout.addLayout(search_layout)

        # Tableau des résultats
        self.cases_table = QTableWidget()
        self.cases_table.setColumnCount(6)
        self.cases_table.setHorizontalHeaderLabels(
            ["Référence", "Matricule", "Faute Commise", "Statut", "Numéro Inc", "Sélectionner"])
        self.cases_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.cases_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.cases_table.hideColumn(4)  # Cacher la colonne Numéro Inc
        layout.addWidget(self.cases_table)

        # Boutons
        button_layout = QHBoxLayout()
        self.delete_button = QPushButton("Supprimer")
        self.delete_button.setStyleSheet("background-color: #f44336; color: white;")
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

                # Recherche dans les tables Dossiers, Gendarmes, Fautes et Statut
                query = """
                    SELECT 
                        d.reference, 
                        d.matricule_dossier, 
                        f.lib_faute, 
                        s.lib_statut,
                        d.numero_inc
                    FROM Dossiers d
                    JOIN Gendarmes g ON d.matricule_dossier = g.matricule
                    JOIN Fautes f ON d.faute_id = f.id_faute
                    JOIN Statut s ON d.statut_id = s.id_statut
                    WHERE d.reference LIKE ? 
                       OR d.matricule_dossier LIKE ?
                       OR g.nom_prenoms LIKE ?
                    ORDER BY d.date_enr DESC
                """
                cursor.execute(query, (f"%{search_text}%", f"%{search_text}%", f"%{search_text}%"))
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
                    self.cases_table.setItem(row, 5, checkbox)

                if not results:
                    QMessageBox.information(self, "Information", "Aucun dossier trouvé")

        except Exception as e:
            logger.error(f"Erreur lors de la recherche : {str(e)}")
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la recherche : {str(e)}")

    def delete_selected_cases(self):
        """Supprime les dossiers sélectionnés avec gestion des relations"""
        selected_rows = []
        for row in range(self.cases_table.rowCount()):
            checkbox_item = self.cases_table.item(row, 5)
            if checkbox_item and checkbox_item.checkState() == Qt.CheckState.Checked:
                reference = self.cases_table.item(row, 0).text()
                matricule = self.cases_table.item(row, 1).text()
                numero_inc = self.cases_table.item(row, 4).text()
                selected_rows.append((row, reference, matricule, numero_inc))

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
                    cursor.execute("BEGIN TRANSACTION")

                    try:
                        for _, reference, matricule, numero_inc in selected_rows:
                            # 1. Récupérer l'ID de la sanction associée au dossier
                            cursor.execute(
                                "SELECT sanction_id FROM Dossiers WHERE matricule_dossier = ? AND reference = ?",
                                (matricule, reference)
                            )
                            result = cursor.fetchone()
                            if result:
                                sanction_id = result[0]

                                # 2. Supprimer le dossier
                                cursor.execute(
                                    "DELETE FROM Dossiers WHERE matricule_dossier = ? AND reference = ?",
                                    (matricule, reference)
                                )

                                # 3. Supprimer la sanction si elle existe
                                if sanction_id:
                                    cursor.execute(
                                        "DELETE FROM Sanctions WHERE id_sanction = ?",
                                        (sanction_id,)
                                    )

                        # Commit uniquement si tout s'est bien passé
                        cursor.execute("COMMIT")

                        QMessageBox.information(
                            self,
                            "Succès",
                            f"{len(selected_rows)} dossier(s) supprimé(s) avec succès"
                        )

                        # Émettre le signal et rafraîchir la recherche
                        self.case_deleted.emit()
                        self.search_cases()

                    except Exception as e:
                        # Annuler la transaction en cas d'erreur
                        cursor.execute("ROLLBACK")
                        raise e

            except Exception as e:
                logger.error(f"Erreur lors de la suppression : {str(e)}")
                QMessageBox.critical(
                    self,
                    "Erreur",
                    f"Erreur lors de la suppression : {str(e)}"
                )
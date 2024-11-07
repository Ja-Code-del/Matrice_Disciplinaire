# src/ui/windows/statistics/subject_dialog.py

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QComboBox, QPushButton, QGroupBox, QRadioButton,
                             QDialogButtonBox)
from PyQt6.QtCore import Qt
import pandas as pd


class SubjectDialog(QDialog):
    """Dialogue pour le choix du sujet d'analyse statistique."""

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("Analyse par sujet")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Groupe de choix du type d'analyse
        type_group = QGroupBox("Type d'analyse")
        type_layout = QVBoxLayout()

        self.radio_annees = QRadioButton("Analyse par années")
        self.radio_punitions = QRadioButton("Analyse par punitions")
        self.radio_fautes = QRadioButton("Analyse par fautes")

        type_layout.addWidget(self.radio_annees)
        type_layout.addWidget(self.radio_punitions)
        type_layout.addWidget(self.radio_fautes)

        type_group.setLayout(type_layout)
        layout.addWidget(type_group)

        # Sélection détaillée
        detail_layout = QHBoxLayout()
        self.detail_label = QLabel("Sélectionner :")
        self.detail_combo = QComboBox()
        detail_layout.addWidget(self.detail_label)
        detail_layout.addWidget(self.detail_combo)
        layout.addLayout(detail_layout)

        # Connexion des signaux
        self.radio_annees.toggled.connect(lambda: self.update_detail_combo("annees"))
        self.radio_punitions.toggled.connect(lambda: self.update_detail_combo("punitions"))
        self.radio_fautes.toggled.connect(lambda: self.update_detail_combo("fautes"))

        # Boutons standard
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # Sélection par défaut
        self.radio_annees.setChecked(True)

    def update_detail_combo(self, type_analyse):
        """Met à jour le combo en fonction du type d'analyse sélectionné."""
        self.detail_combo.clear()

        try:
            if type_analyse == "annees":
                query = "SELECT DISTINCT annee_punition FROM sanctions ORDER BY annee_punition DESC"
                results = self.db_manager.execute_query(query).fetchall()
                self.detail_combo.addItems([str(r[0]) for r in results])

            elif type_analyse == "punitions":
                query = "SELECT DISTINCT categorie FROM sanctions ORDER BY categorie"
                results = self.db_manager.execute_query(query).fetchall()
                self.detail_combo.addItems([str(r[0]) for r in results])

            elif type_analyse == "fautes":
                query = "SELECT DISTINCT faute_commise FROM sanctions ORDER BY faute_commise"
                results = self.db_manager.execute_query(query).fetchall()
                self.detail_combo.addItems([r[0] for r in results if r[0]])

        except Exception as e:
            print(f"Erreur lors de la mise à jour du combo: {str(e)}")

    def get_selection(self):
        """Retourne la sélection actuelle."""
        type_analyse = ""
        if self.radio_annees.isChecked():
            type_analyse = "annees"
        elif self.radio_punitions.isChecked():
            type_analyse = "punitions"
        elif self.radio_fautes.isChecked():
            type_analyse = "fautes"

        return {
            "type": type_analyse,
            "valeur": self.detail_combo.currentText()
        }
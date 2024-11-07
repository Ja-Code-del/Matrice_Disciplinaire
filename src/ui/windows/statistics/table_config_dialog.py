# src/ui/windows/statistics/table_config_dialog.py

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QComboBox, QPushButton, QGroupBox,
                             QDialogButtonBox, QCheckBox)
from PyQt6.QtCore import Qt


class TableConfigDialog(QDialog):
    """Dialogue pour la configuration des tableaux statistiques."""

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("Configuration du tableau")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Configuration des axes
        axes_group = QGroupBox("Configuration des axes")
        axes_layout = QVBoxLayout()

        # Axe X
        x_layout = QHBoxLayout()
        x_layout.addWidget(QLabel("Axe X (abscisse) :"))
        self.x_combo = QComboBox()
        x_layout.addWidget(self.x_combo)
        axes_layout.addLayout(x_layout)

        # Axe Y
        y_layout = QHBoxLayout()
        y_layout.addWidget(QLabel("Axe Y (ordonnée) :"))
        self.y_combo = QComboBox()
        y_layout.addWidget(self.y_combo)
        axes_layout.addLayout(y_layout)

        axes_group.setLayout(axes_layout)
        layout.addWidget(axes_group)

        # Options supplémentaires
        options_group = QGroupBox("Options d'affichage")
        options_layout = QVBoxLayout()

        self.show_percentages = QCheckBox("Afficher les pourcentages")
        self.show_totals = QCheckBox("Afficher les totaux")
        self.cumulative = QCheckBox("Valeurs cumulatives")

        options_layout.addWidget(self.show_percentages)
        options_layout.addWidget(self.show_totals)
        options_layout.addWidget(self.cumulative)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Boutons standard
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # Remplissage des combos
        self.populate_combos()

    def populate_combos(self):
        """Remplit les combobox avec les champs disponibles."""
        fields = [
            ("annee_punition", "Année"),
            ("categorie", "Catégorie de sanction"),
            ("statut", "Statut"),
            ("grade", "Grade"),
            ("legions", "Légion"),
            ("regions", "Région"),
            ("annee_service", "Années de service")
        ]

        for value, label in fields:
            self.x_combo.addItem(label, value)
            self.y_combo.addItem(label, value)

    def get_configuration(self):
        """Retourne la configuration actuelle."""
        return {
            "x_axis": self.x_combo.currentData(),
            "y_axis": self.y_combo.currentData(),
            "options": {
                "show_percentages": self.show_percentages.isChecked(),
                "show_totals": self.show_totals.isChecked(),
                "cumulative": self.cumulative.isChecked()
            }
        }
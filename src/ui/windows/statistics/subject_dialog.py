# src/ui/windows/statistics/subject_dialog.py

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QComboBox, QPushButton, QGroupBox, QRadioButton,
                             QDialogButtonBox, QWidget, QFrame, QTableWidget, QTableWidgetItem)
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtCore import Qt
import pandas as pd

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QComboBox, QDialogButtonBox, QGroupBox)
from PyQt6.QtCore import Qt
from src.data.gendarmerie.structure import SUBDIVISIONS, SERVICE_RANGES, ANALYSIS_THEMES


class SubjectDialog(QDialog):
    """Dialogue pour le choix du sujet d'analyse statistique."""

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("Analyse par sujet")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Groupe pour le choix du thème
        theme_group = QGroupBox("Choix du thème d'analyse")
        theme_layout = QVBoxLayout()

        # Sélection du thème principal
        theme_hlayout = QHBoxLayout()
        theme_hlayout.addWidget(QLabel("Thème :"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(ANALYSIS_THEMES.keys())
        self.theme_combo.currentIndexChanged.connect(self.update_value_combo)
        theme_hlayout.addWidget(self.theme_combo)
        theme_layout.addLayout(theme_hlayout)

        # Sélection de la valeur spécifique
        value_hlayout = QHBoxLayout()
        value_hlayout.addWidget(QLabel("Valeur :"))
        self.value_combo = QComboBox()
        value_hlayout.addWidget(self.value_combo)
        theme_layout.addLayout(value_hlayout)

        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)

        # Groupe pour les sous-thèmes disponibles
        subtheme_group = QGroupBox("Sous-thèmes disponibles")
        subtheme_layout = QVBoxLayout()
        self.subtheme_label = QLabel()
        subtheme_layout.addWidget(self.subtheme_label)
        subtheme_group.setLayout(subtheme_layout)
        layout.addWidget(subtheme_group)

        # Boutons standard
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # Initialisation des données
        self.update_value_combo()

    def update_value_combo(self):
        """Met à jour le combo des valeurs en fonction du thème sélectionné."""
        current_theme = self.theme_combo.currentText()
        self.value_combo.clear()

        if current_theme in ANALYSIS_THEMES:
            field = ANALYSIS_THEMES[current_theme]["field"]
            # Ajouter l'option "Tous"
            self.value_combo.addItem(f"Tous les {current_theme.lower()}")

            try:
                with self.db_manager.get_connection() as conn:
                    cursor = conn.cursor()

                    if current_theme == "Subdivision":
                        # Utiliser les subdivisions prédéfinies
                        for subdiv in SUBDIVISIONS:
                            self.value_combo.addItem(subdiv)

                    elif current_theme == "Tranches années service":
                        # Utiliser les tranches d'années prédéfinies
                        for service_range in SERVICE_RANGES:
                            self.value_combo.addItem(service_range)

                    else:
                        # Récupérer les valeurs de la base de données
                        table = "gendarmes" if field in ["situation_matrimoniale", "annee_service"] else "sanctions"
                        query = f"SELECT DISTINCT {field} FROM {table} WHERE {field} IS NOT NULL ORDER BY {field}"
                        cursor.execute(query)
                        values = cursor.fetchall()
                        for value in values:
                            if value[0]:  # Ignorer les valeurs NULL
                                self.value_combo.addItem(str(value[0]))

            except Exception as e:
                print(f"Erreur lors de la récupération des valeurs : {str(e)}")

            # Mise à jour des sous-thèmes disponibles
            subthemes = ANALYSIS_THEMES[current_theme]["subfields"]
            self.subtheme_label.setText("Sous-thèmes disponibles :\n• " + "\n• ".join(subthemes))

    def get_selection(self):
        """Retourne la sélection actuelle."""
        return {
            "theme": self.theme_combo.currentText(),
            "value": self.value_combo.currentText(),
            "field": ANALYSIS_THEMES[self.theme_combo.currentText()]["field"]
        }

    def get_available_subthemes(self):
        """Retourne la liste des sous-thèmes disponibles pour le thème sélectionné."""
        current_theme = self.theme_combo.currentText()
        if current_theme in ANALYSIS_THEMES:
            return ANALYSIS_THEMES[current_theme]["subfields"]
        return []

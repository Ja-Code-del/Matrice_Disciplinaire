# src/ui/windows/statistics/table_config_dialog.py
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QComboBox, QPushButton, QGroupBox,
                             QDialogButtonBox, QCheckBox, QWidget, QFrame, QTableWidget, QTableWidgetItem)
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from src.data.gendarmerie.structure import SUBDIVISIONS, SERVICE_RANGES, ANALYSIS_THEMES
from src.ui.windows.statistics.chart_selection_dialog import ChartSelectionDialog


class TableConfigDialog(QDialog):
    THEMES = ANALYSIS_THEMES

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
        x_layout = QVBoxLayout()
        x_layout.addWidget(QLabel("Axe X (abscisse) :"))

        x_theme_layout = QHBoxLayout()
        self.x_theme_combo = QComboBox()
        self.x_value_combo = QComboBox()

        x_theme_layout.addWidget(QLabel("Thème:"))
        x_theme_layout.addWidget(self.x_theme_combo)
        x_theme_layout.addWidget(QLabel("Valeur:"))
        x_theme_layout.addWidget(self.x_value_combo)

        x_layout.addLayout(x_theme_layout)
        axes_layout.addLayout(x_layout)

        # Axe Y
        y_layout = QVBoxLayout()
        y_layout.addWidget(QLabel("Axe Y (ordonnée) :"))

        y_theme_layout = QHBoxLayout()
        self.y_theme_combo = QComboBox()
        self.y_value_combo = QComboBox()

        y_theme_layout.addWidget(QLabel("Thème:"))
        y_theme_layout.addWidget(self.y_theme_combo)
        y_theme_layout.addWidget(QLabel("Valeur:"))
        y_theme_layout.addWidget(self.y_value_combo)

        y_layout.addLayout(y_theme_layout)
        axes_layout.addLayout(y_layout)

        axes_group.setLayout(axes_layout)
        layout.addWidget(axes_group)

        # Boutons standard
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # Connexion des signaux
        self.x_theme_combo.currentIndexChanged.connect(
            lambda: self.update_value_combo(self.x_theme_combo, self.x_value_combo))
        self.y_theme_combo.currentIndexChanged.connect(
            lambda: self.update_value_combo(self.y_theme_combo, self.y_value_combo))

        # Remplissage initial des combos
        self.populate_theme_combos()

    def populate_theme_combos(self):
        """Remplit les combos des thèmes."""
        themes = list(self.THEMES.keys())
        self.x_theme_combo.addItems(themes)
        self.y_theme_combo.addItems(themes)

    def update_value_combo(self, theme_combo, value_combo):
        """Met à jour le combo des valeurs en fonction du thème sélectionné."""
        theme = theme_combo.currentText()
        value_combo.clear()

        if theme in self.THEMES:
            field = self.THEMES[theme]["field"]
            # Ajouter "Tous" comme première option
            value_combo.addItem(f"Tous les {theme.lower()}")

            if theme == "Tranches années service":
                # Utiliser les tranches prédéfinies
                for tranche in SERVICE_RANGES:
                    value_combo.addItem(tranche)
            elif field == "subdiv":
                # Utiliser les subdivisions prédéfinies
                for subdiv in SUBDIVISIONS:
                    value_combo.addItem(subdiv)
            elif field == "grade":
                # Récupérer tous les grades disponibles
                with self.db_manager.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT DISTINCT grade FROM gendarmes ORDER BY grade")
                    grades = cursor.fetchall()
                    for grade in grades:
                        if grade[0]:  # Ignorer les valeurs NULL
                            value_combo.addItem(str(grade[0]))
            else:
                # Récupérer les valeurs de la base de données
                with self.db_manager.get_connection() as conn:
                    cursor = conn.cursor()
                    table = "gendarmes" if field in ["situation_matrimoniale", "annee_service",
                                                     "grade"] else "sanctions"
                    query = f"SELECT DISTINCT {field} FROM {table} WHERE {field} IS NOT NULL ORDER BY {field}"
                    cursor.execute(query)
                    values = cursor.fetchall()
                    for value in values:
                        if value[0]:  # Ignorer les valeurs NULL
                            value_combo.addItem(str(value[0]))

    def accept(self):
        """Appelé quand l'utilisateur valide la configuration."""
        super().accept()

    def get_configuration(self):
        """Retourne la configuration actuelle."""
        config = {
            "x_axis": {
                "theme": self.x_theme_combo.currentText(),
                "field": self.THEMES[self.x_theme_combo.currentText()]["field"],
                "value": self.x_value_combo.currentText()
            },
            "y_axis": {
                "theme": self.y_theme_combo.currentText(),
                "field": self.THEMES[self.y_theme_combo.currentText()]["field"],
                "value": self.y_value_combo.currentText()
            }
        }
        # if hasattr(self, 'chart_dialog') and self.chart_dialog:
        #     config['chart_type'] = self.chart_dialog.get_selected_chart()

        return config


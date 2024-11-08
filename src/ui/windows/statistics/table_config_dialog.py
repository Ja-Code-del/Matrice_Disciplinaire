# src/ui/windows/statistics/table_config_dialog.py
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QComboBox, QPushButton, QGroupBox,
                             QDialogButtonBox, QCheckBox, QWidget, QFrame, QTableWidget, QTableWidgetItem)
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from src.data.gendarmerie.structure import SUBDIVISIONS, SERVICE_RANGES, ANALYSIS_THEMES


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

    def get_configuration(self):
        """Retourne la configuration actuelle."""
        return {
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



# class TableConfigDialog(QDialog):
#     """Dialogue pour la configuration des tableaux statistiques."""
#
#     def __init__(self, db_manager, parent=None):
#         super().__init__(parent)
#         self.db_manager = db_manager
#         self.setWindowTitle("Configuration du tableau")
#         self.setModal(True)
#         self.setMinimumWidth(500)
#         self.setup_ui()
#
#     def setup_ui(self):
#         layout = QVBoxLayout(self)
#
#         # Configuration des axes
#         axes_group = QGroupBox("Configuration des axes")
#         axes_layout = QVBoxLayout()
#
#         # Axe X
#         x_layout = QHBoxLayout()
#         x_layout.addWidget(QLabel("Axe X (abscisse) :"))
#         self.x_combo = QComboBox()
#         x_layout.addWidget(self.x_combo)
#         axes_layout.addLayout(x_layout)
#
#         # Axe Y
#         y_layout = QHBoxLayout()
#         y_layout.addWidget(QLabel("Axe Y (ordonnée) :"))
#         self.y_combo = QComboBox()
#         y_layout.addWidget(self.y_combo)
#         axes_layout.addLayout(y_layout)
#
#         axes_group.setLayout(axes_layout)
#         layout.addWidget(axes_group)
#
#         # Options supplémentaires
#         options_group = QGroupBox("Options d'affichage")
#         options_layout = QVBoxLayout()
#
#         self.show_percentages = QCheckBox("Afficher les pourcentages")
#         self.show_totals = QCheckBox("Afficher les totaux")
#         self.cumulative = QCheckBox("Valeurs cumulatives")
#
#         options_layout.addWidget(self.show_percentages)
#         options_layout.addWidget(self.show_totals)
#         options_layout.addWidget(self.cumulative)
#
#         options_group.setLayout(options_layout)
#         layout.addWidget(options_group)
#
#         # Boutons standard
#         buttons = QDialogButtonBox(
#             QDialogButtonBox.StandardButton.Ok |
#             QDialogButtonBox.StandardButton.Cancel
#         )
#         buttons.accepted.connect(self.accept)
#         buttons.rejected.connect(self.reject)
#         layout.addWidget(buttons)
#
#         # Remplissage des combos
#         self.populate_combos()
#
#     def populate_combos(self):
#         """Remplit les combobox avec les champs disponibles."""
#         fields = [
#             ("annee_punition", "Année"),
#             ("categorie", "Catégorie de sanction"),
#             ("statut", "Statut"),
#             ("grade", "Grade"),
#             ("legions", "Légion"),
#             ("regions", "Région"),
#             ("annee_service", "Années de service")
#         ]
#
#         for value, label in fields:
#             self.x_combo.addItem(label, value)
#             self.y_combo.addItem(label, value)
#
#     def get_configuration(self):
#         """Retourne la configuration actuelle."""
#         return {
#             "x_axis": self.x_combo.currentData(),
#             "y_axis": self.y_combo.currentData(),
#             "options": {
#                 "show_percentages": self.show_percentages.isChecked(),
#                 "show_totals": self.show_totals.isChecked(),
#                 "cumulative": self.cumulative.isChecked()
#             }
#         }
#
#     def load_field_values(self):
#         """Charge les valeurs possibles pour les champs disponibles."""
#         try:
#             with self.db_manager.get_connection() as conn:
#                 cursor = conn.cursor()
#
#                 # Récupérer les valeurs uniques pour chaque champ
#                 for field in self.available_fields:
#                     if field.get('has_values', False):
#                         query = f"SELECT DISTINCT {field['name']} FROM {field['table']} ORDER BY {field['name']}"
#                         cursor.execute(query)
#                         values = cursor.fetchall()
#                         field['values'] = [str(v[0]) for v in values if v[0] is not None]
#
#         except Exception as e:
#             QMessageBox.critical(
#                 self,
#                 "Erreur",
#                 f"Erreur lors du chargement des valeurs: {str(e)}"
#             )
#         def update_value_combo(self, theme_combo, value_combo):
#             """Met à jour le combo des valeurs en fonction du thème sélectionné."""
#             theme = theme_combo.currentText()
#             value_combo.clear()
#
#             if theme in self.THEMES:
#                 field = self.THEMES[theme]["field"]
#                 # Ajouter "Tous" comme première option
#                 value_combo.addItem(f"Tous les {theme.lower()}")
#
#                 # Récupérer les valeurs spécifiques de la base de données
#                 with self.db_manager.get_connection() as conn:
#                     cursor = conn.cursor()
#                     if field == "subdiv":
#                         # Utiliser les subdivisions prédéfinies
#                         for subdiv in SUBDIVISIONS:
#                             value_combo.addItem(subdiv)
#                     else:
#                         # Récupérer les valeurs de la base de données
#                         table = "gendarmes" if field in ["situation_matrimoniale", "annee_service"] else "sanctions"
#                         query = f"SELECT DISTINCT {field} FROM {table} WHERE {field} IS NOT NULL ORDER BY {field}"
#                         cursor.execute(query)
#                         values = cursor.fetchall()
#                         for value in values:
#                             if value[0]:  # Ignorer les valeurs NULL
#                                 value_combo.addItem(str(value[0]))
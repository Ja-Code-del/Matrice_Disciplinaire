# src/ui/windows/statistics/table_config_dialog.py
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QComboBox, QPushButton, QGroupBox,
                             QDialogButtonBox, QCheckBox, QWidget, QFrame, QTableWidget, QTableWidgetItem, QMessageBox)
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from src.data.gendarmerie.structure import SERVICE_RANGES, ANALYSIS_THEMES
from src.ui.windows.statistics.chart_selection_dialog import ChartSelectionDialog


class TableConfigDialog(QDialog):
    THEMES = ANALYSIS_THEMES

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("Configuration du tableau")
        self.setModal(True)
        self.setMinimumWidth(500)

        # Récupérer le sujet sélectionné
        self.current_subject = parent.current_subject

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Afficher le sujet sélectionné
        subject_info = QLabel(f"Sujet d'analyse: {self.current_subject['theme']} - {self.current_subject['value']}")
        subject_info.setStyleSheet("font-weight: bold; color: #0066cc;")
        layout.addWidget(subject_info)

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
        """Remplit les combos des thèmes en excluant le thème déjà sélectionné."""
        themes = list(ANALYSIS_THEMES.keys())
        # Retirer le thème déjà sélectionné des options
        if self.current_subject['theme'] in themes:
            themes.remove(self.current_subject['theme'])

        self.x_theme_combo.addItems(themes)
        self.y_theme_combo.addItems(themes)

    def get_configuration(self):
        """Retourne la configuration complète."""
        config = {
            "subject_selection": self.current_subject,
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
        return config

    def update_value_combo(self, theme_combo, value_combo):
        """Met à jour le combo des valeurs en fonction du thème sélectionné."""
        current_theme = theme_combo.currentText()
        value_combo.clear()

        if current_theme in ANALYSIS_THEMES:
            # Ajouter l'option "Tous"
            value_combo.addItem(f"Tou(te)s les {current_theme.lower()}")

            try:
                with self.db_manager.get_connection() as conn:
                    cursor = conn.cursor()

                    # Gestion des cas particuliers (Tranches d'années de service)
                    if current_theme == "Tranches années service":
                        for service_range in SERVICE_RANGES:
                            value_combo.addItem(service_range)

                    else:
                        # Correspondance entre les thèmes et les tables de la base de données
                        table_mapping = {
                            "Année": ("Dossiers d", "d.annee_enr"),
                            "Grades": ("Grade gr", "gr.lib_grade"),
                            "Unite": ("Unite u", "u.lib_unite"),
                            "Légion": ("Legion l", "l.lib_legion"),
                            "Subdivision": ("Subdiv su", "su.lib_subdiv"),
                            "Région": ("Region r", "r.lib_rg"),
                            "Situation matrimoniale": ("Sit_mat st", "st.lib_sit_mat"),
                            "Fautes commises": ("Fautes f", "f.lib_faute"),
                            "Catégorie de Fautes": ("Categories c", "c.id_categorie"),
                            "Type de sanction": ("Type_sanctions ts", "ts.lib_type_sanction"),
                            "Statut": ("Statut st", "st.lib_statut")
                        }

                        if current_theme in table_mapping.keys():
                            table, column = table_mapping[current_theme]
                            query = f"SELECT DISTINCT {column} FROM {table} WHERE {column} IS NOT NULL ORDER BY {column}"
                            cursor.execute(query)
                            values = cursor.fetchall()
                            print(values)

                            for value in values:
                                value_combo.addItem(str(value[0]))

            except Exception as e:
                print(f"Erreur lors de la récupération des valeurs : {str(e)}")

    def accept(self):
        """Appelé quand l'utilisateur valide la configuration."""
        super().accept()


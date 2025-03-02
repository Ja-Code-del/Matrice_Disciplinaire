# src/ui/windows/statistics/subject_dialog.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QComboBox, QPushButton, QGroupBox, QRadioButton,
                             QDialogButtonBox, QWidget, QFrame, QTableWidget, QTableWidgetItem,
                             QMessageBox, QHeaderView)
from PyQt6.QtCore import QTimer
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtCore import Qt
import pandas as pd

from src.data.gendarmerie.structure import SUBDIVISIONS, SERVICE_RANGES, ANALYSIS_THEMES
from src.ui.windows.statistics.visualization_window import VisualizationWindow


class SubjectDialog(QDialog):
    """Dialogue pour le choix du sujet d'analyse statistique."""

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.graph_data = None
        self.db_manager = db_manager
        self.stats_window = parent
        print(f"Initialisation de SubjectDialog - Parent: {parent}")

        self.setWindowTitle("Analyse par sujet")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setup_ui()
        self.results_table = None
        #self.theme_combo = QComboBox()

    # Dans SubjectDialog
    def analyze_subject(self):
        """Analyse le sujet sélectionné."""
        try:
            # Récupérer la sélection
            selection = self.get_selection()
            print(f"Sélection effectuée: {selection}")  # Debug

            # Vérification de la sélection
            if selection['value'].startswith('Tou(tes)'):
                QMessageBox.warning(
                    self,
                    "Attention",
                    "Veuillez sélectionner une valeur spécifique pour l'analyse."
                )
                return

            # Vérification de la référence à la fenêtre principale
            if self.stats_window is None:
                raise Exception("Fenêtre parente (StatistiquesWindow) non trouvée")

            # Stockage de la sélection
            self.stats_window.current_subject = selection

            # Fermer cette fenêtre
            self.close()  # Utiliser close() au lieu de accept()

            # Ouvrir directement la configuration des tableaux
            self.stats_window.show_table_config()

        except Exception as e:
            error_msg = f"Erreur lors de l'analyse: {str(e)}"
            print(f"Erreur dans analyze_subject: {error_msg}")
            QMessageBox.critical(
                self,
                "Erreur",
                error_msg
            )

    def get_selection(self):
        """Retourne la sélection actuelle."""
        return {
            "theme": self.theme_combo.currentText(),
            "value": self.value_combo.currentText(),
            "field": ANALYSIS_THEMES[self.theme_combo.currentText()]["field"]
        }

    def display_results(self, stats):
        """Affiche les résultats de l'analyse."""
        try:
            # Créer une nouvelle fenêtre pour les résultats si elle n'existe pas
            if not self.results_table:
                self.results_table = QTableWidget(self)
                self.layout().addWidget(self.results_table)

            # Configuration du tableau
            headers = ['Catégorie', 'Détails']
            self.results_table.setColumnCount(len(headers))
            self.results_table.setHorizontalHeaderLabels(headers)

            # Déterminer le nombre de lignes nécessaires
            total_rows = sum(1 + len(v) if isinstance(v, dict) else 1
                             for v in stats.values())
            self.results_table.setRowCount(total_rows)

            # Remplissage des données
            current_row = 0
            for key, value in stats.items():
                # Titre de la catégorie
                category_name = key.replace('_', ' ').title()
                self.results_table.setItem(
                    current_row,
                    0,
                    QTableWidgetItem(category_name)
                )

                if isinstance(value, dict):
                    # Pour les dictionnaires de valeurs
                    details = '\n'.join([f"{k}: {v:,}" for k, v in value.items()])
                    self.results_table.setItem(
                        current_row,
                        1,
                        QTableWidgetItem(details)
                    )
                    current_row += 1
                else:
                    # Pour les valeurs simples (comme le total)
                    self.results_table.setItem(
                        current_row,
                        1,
                        QTableWidgetItem(f"{value:,}")
                    )
                    current_row += 1

            # Style du tableau
            for i in range(self.results_table.rowCount()):
                for j in range(self.results_table.columnCount()):
                    item = self.results_table.item(i, j)
                    if item:
                        item.setTextAlignment(Qt.AlignmentFlag.AlignLeft |
                                              Qt.AlignmentFlag.AlignVCenter)

            # Ajustement des dimensions
            self.results_table.horizontalHeader().setSectionResizeMode(
                0, QHeaderView.ResizeMode.ResizeToContents)
            self.results_table.horizontalHeader().setSectionResizeMode(
                1, QHeaderView.ResizeMode.Stretch)
            self.results_table.resizeRowsToContents()

        except Exception as e:
            print(f"Erreur dans display_results: {str(e)}")
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors de l'affichage des résultats: {str(e)}"
            )

    def accept(self):
        """Appelé quand l'utilisateur valide la sélection."""
        self.analyze_subject()  # Lancer l'analyse avant de fermer
        super().accept()

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
            # Ajouter l'option "Tous"
            self.value_combo.addItem(f"Tou(te)s les {current_theme.lower()}")

            try:
                with self.db_manager.get_connection() as conn:
                    cursor = conn.cursor()

                    # Gestion des cas particuliers (Tranches d'années de service)
                    if current_theme == "Tranches années service":
                        for service_range in SERVICE_RANGES:
                            self.value_combo.addItem(service_range)

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
                                self.value_combo.addItem(str(value[0]))

            except Exception as e:
                print(f"Erreur lors de la récupération des valeurs : {str(e)}")

            # Mise à jour des sous-thèmes disponibles
            subthemes = ANALYSIS_THEMES[current_theme]["subfields"]
            self.subtheme_label.setText("Sous-thèmes disponibles :\n• " + "\n• ".join(subthemes))

    def get_available_subthemes(self):
        """Retourne la liste des sous-thèmes disponibles pour le thème sélectionné."""
        current_theme = self.theme_combo.currentText()
        if current_theme in ANALYSIS_THEMES:
            return ANALYSIS_THEMES[current_theme]["subfields"]
        return []

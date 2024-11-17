# src/ui/windows/statistics/subject_dialog.py

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QComboBox, QPushButton, QGroupBox, QRadioButton,
                             QDialogButtonBox, QWidget, QFrame, QTableWidget, QTableWidgetItem,
                             QMessageBox, QHeaderView)
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtCore import Qt
import pandas as pd

from src.data.gendarmerie.structure import SUBDIVISIONS, SERVICE_RANGES, ANALYSIS_THEMES


class SubjectDialog(QDialog):
    """Dialogue pour le choix du sujet d'analyse statistique."""

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.graph_data = None
        self.db_manager = db_manager
        self.setWindowTitle("Analyse par sujet")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setup_ui()
        self.results_table = None

    def analyze_subject(self):
        """Analyse le sujet sélectionné avec la nouvelle approche."""
        selection = self.get_selection()

        try:
            with self.db_manager.get_connection() as conn:
                # Requête pour obtenir les sanctions uniques
                sanctions_query = """
                WITH unique_sanctions AS (
                    SELECT DISTINCT 
                        COALESCE(numero_dossier, 'SANS_NUMERO_' || id) as numero_dossier,
                        MIN(id) as id,
                        MIN(date_enr) as date_enr
                    FROM sanctions
                    GROUP BY COALESCE(numero_dossier, 'SANS_NUMERO_' || id)
                )
                SELECT s.*
                FROM sanctions s
                INNER JOIN unique_sanctions us 
                    ON COALESCE(s.numero_dossier, 'SANS_NUMERO_' || s.id) = us.numero_dossier 
                    AND s.id = us.id
                    AND s.date_enr = us.date_enr
                """

                # Récupérer les données des sanctions
                sanctions_df = pd.read_sql_query(sanctions_query, conn)

                # Récupérer les données des gendarmes
                gendarmes_query = """
                SELECT 
                    id, 
                    grade,
                    subdiv,
                    annee_service,
                    situation_matrimoniale
                FROM gendarmes
                """
                gendarmes_df = pd.read_sql_query(gendarmes_query, conn)

                # Fusion des données
                df = sanctions_df.merge(
                    gendarmes_df,
                    left_on='id',
                    right_on='id',
                    how='left'
                )

                # Traitement des années de service si nécessaire
                if selection['field'] == 'annee_service':
                    df['service_range'] = pd.cut(
                        df['annee_service'],
                        bins=[0, 5, 10, 15, 20, 25, 30, 35, 40],
                        labels=['0-5 ANS', '6-10 ANS', '11-15 ANS', '16-20 ANS',
                                '21-25 ANS', '26-30 ANS', '31-35 ANS', '36-40 ANS']
                    )

                # Filtrage selon la sélection
                if not selection['value'].startswith('Tous'):
                    if selection['field'] == 'annee_service':
                        df = df[df['service_range'] == selection['value']]
                    else:
                        df = df[df[selection['field']] == selection['value']]

                # Calculer les statistiques pour ce sujet
                stats = {
                    'total': len(df),
                    'par_categorie': df['categorie'].value_counts().to_dict(),
                    'par_annee': df['annee_punition'].value_counts().to_dict(),
                    'par_statut': df['statut'].value_counts().to_dict(),
                    'par_grade': df['grade'].value_counts().to_dict(),
                    'par_subdivision': df['subdiv'].value_counts().to_dict()
                }

                # Créer les données pour les graphiques si nécessaire
                self.graph_data = df

                # Afficher les résultats
                self.display_results(stats)

        except Exception as e:
            print(f"Erreur dans analyze_subject: {str(e)}")
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors de l'analyse: {str(e)}"
            )

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

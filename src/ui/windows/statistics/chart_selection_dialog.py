# src/ui/windows/statistics/chart_selection_dialog.py

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QGroupBox, QRadioButton,
                             QDialogButtonBox, QLabel)


# class ChartSelectionDialog(QDialog):
#     def __init__(self, data_config, parent=None):
#         super().__init__(parent)
#         self.data_config = data_config
#         self.setWindowTitle("Sélection du type de graphique")
#         self.setModal(True)
#         self.setup_ui()
#
#     def setup_ui(self):
#         layout = QVBoxLayout(self)
#
#         # Label explicatif
#         layout.addWidget(QLabel("Choisissez le type de graphique adapté à votre analyse :"))
#
#         # Groupe de graphiques disponibles
#         self.chart_group = QGroupBox("Types de graphiques disponibles")
#         chart_layout = QVBoxLayout()
#
#         # On détermine les graphiques pertinents selon la configuration
#         available_charts = self.get_available_charts()
#
#         self.chart_buttons = {}
#         for chart_id, chart_info in available_charts.items():
#             radio = QRadioButton(chart_info['name'])
#             radio.setToolTip(chart_info['description'])
#             self.chart_buttons[chart_id] = radio
#             chart_layout.addWidget(radio)
#
#         # Sélectionner le premier par défaut
#         if self.chart_buttons:
#             first_button = list(self.chart_buttons.values())[0]
#             first_button.setChecked(True)
#
#         self.chart_group.setLayout(chart_layout)
#         layout.addWidget(self.chart_group)
#
#         # Boutons OK/Cancel
#         buttons = QDialogButtonBox(
#             QDialogButtonBox.StandardButton.Ok |
#             QDialogButtonBox.StandardButton.Cancel
#         )
#         buttons.accepted.connect(self.accept)
#         buttons.rejected.connect(self.reject)
#         layout.addWidget(buttons)
#
#     def get_available_charts(self):
#         """Détermine les graphiques disponibles selon la configuration."""
#         charts = {}
#
#         # Graphiques toujours disponibles
#         charts['bar_stacked'] = {
#             'name': 'Barres empilées',
#             'description': 'Graphique à barres empilées montrant la répartition'
#         }
#
#         charts['bar_grouped'] = {
#             'name': 'Barres groupées',
#             'description': 'Graphique à barres groupées pour comparaison'
#         }
#
#         # Si moins de 8 catégories, proposer les graphiques circulaires
#         if len(self.data_config.get('categories', [])) < 8:
#             charts['pie'] = {
#                 'name': 'Camembert',
#                 'description': 'Graphique circulaire montrant les proportions'
#             }
#             charts['donut'] = {
#                 'name': 'Anneau',
#                 'description': 'Version moderne du camembert avec un trou au centre'
#             }
#
#         # Pour les données temporelles
#         if any('annee' in field for field in [self.data_config['x_axis']['field'],
#                                               self.data_config['y_axis']['field']]):
#             charts['line'] = {
#                 'name': 'Courbe',
#                 'description': 'Graphique linéaire pour montrer l\'évolution'
#             }
#
#         # Autres types de visualisation
#         charts['heatmap'] = {
#             'name': 'Carte de chaleur',
#             'description': 'Visualisation de la densité des données'
#         }
#
#         charts['box'] = {
#             'name': 'Boîte à moustaches',
#             'description': 'Distribution statistique des données'
#         }
#
#         return charts
#
#     def get_selected_chart(self):
#         """Retourne le type de graphique sélectionné."""
#         for chart_id, radio in self.chart_buttons.items():
#             if radio.isChecked():
#                 return chart_id
#         return 'bar_stacked'  # Type par défaut

class ChartSelectionDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Sélection du type de graphique")
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Label explicatif
        subject_info = QLabel(
            f"Sujet d'analyse: {self.config['subject_selection']['theme']} - "
            f"{self.config['subject_selection']['value']}"
        )
        subject_info.setStyleSheet("font-weight: bold; color: #0066cc;")
        layout.addWidget(subject_info)

        layout.addWidget(QLabel("Choisissez le type de graphique adapté à votre analyse :"))

        # Groupe de graphiques disponibles
        self.chart_group = QGroupBox("Types de graphiques disponibles")
        chart_layout = QVBoxLayout()

        self.chart_buttons = {}
        available_charts = self.get_available_charts()

        for chart_id, chart_info in available_charts.items():
            radio = QRadioButton(chart_info['name'])
            radio.setToolTip(chart_info['description'])
            self.chart_buttons[chart_id] = radio
            chart_layout.addWidget(radio)

            # Ajouter les options d'axe pour les graphiques qui le nécessitent
            if chart_id in ['bar_simple', 'pie', 'donut']:
                axis_group = QGroupBox("Choisir l'axe à afficher")
                axis_layout = QVBoxLayout()

                self.x_axis_radio = QRadioButton(f"Axe X: {self.config['x_axis']['theme']}")
                self.y_axis_radio = QRadioButton(f"Axe Y: {self.config['y_axis']['theme']}")

                axis_layout.addWidget(self.x_axis_radio)
                axis_layout.addWidget(self.y_axis_radio)

                axis_group.setLayout(axis_layout)
                axis_group.setVisible(False)  # Caché par défaut
                chart_layout.addWidget(axis_group)

                # Connecter le signal pour afficher/masquer les options
                radio.toggled.connect(lambda checked, g=axis_group: g.setVisible(checked))

        self.chart_group.setLayout(chart_layout)
        layout.addWidget(self.chart_group)

        # Boutons OK/Cancel
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_available_charts(self):
        """Détermine les graphiques disponibles selon la configuration."""
        charts = {}

        # Graphiques nécessitant le choix d'un axe
        charts['bar_simple'] = {
            'name': 'Histogramme simple',
            'description': 'Graphique en barres montrant les totaux'
        }

        charts['pie'] = {
            'name': 'Camembert',
            'description': 'Graphique circulaire montrant la répartition'
        }

        charts['donut'] = {
            'name': 'Anneau',
            'description': 'Version moderne du camembert avec un trou au centre'
        }

        # Graphiques standards
        charts['bar_stacked'] = {
            'name': 'Barres empilées',
            'description': 'Graphique à barres empilées montrant la répartition'
        }

        charts['heatmap'] = {
            'name': 'Carte de chaleur',
            'description': 'Visualisation de la densité des données'
        }

        #graphique à barres groupées
        charts['bar_grouped'] = {
            'name': 'Barres groupées',
            'description': 'Graphique à barres groupées pour comparaison directe'
        }

        return charts

    def get_selected_chart(self):
        """Retourne le type de graphique sélectionné et l'axe si pertinent."""
        selected_type = None
        for chart_id, radio in self.chart_buttons.items():
            if radio.isChecked():
                selected_type = chart_id
                break

        # Si c'est un type qui nécessite le choix d'un axe
        if selected_type in ['bar_simple', 'pie', 'donut']:
            return {
                'type': selected_type,
                'axis': 'x' if self.x_axis_radio.isChecked() else 'y'
            }

        return {'type': selected_type}
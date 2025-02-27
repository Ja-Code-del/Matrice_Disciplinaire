from PyQt6.QtWidgets import (QMainWindow, QWidget, QDialog, QVBoxLayout, QPushButton, QGridLayout,
                             QHBoxLayout, QLabel, QSizePolicy, QMessageBox, QFrame, QTableWidget, QTableWidgetItem,
                             QInputDialog)
from PyQt6.QtCore import pyqtSignal, Qt, QSize
from PyQt6.QtGui import QIcon

import pandas as pd

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from .subject_dialog import SubjectDialog
from .table_config_dialog import TableConfigDialog
from .visualization_window import VisualizationWindow
from .full_list_window import FullListWindow
from .chart_selection_dialog import ChartSelectionDialog

from datetime import datetime

from .yearly_trends_window import YearlyTrendsWindow


class StatistiquesWindow(QMainWindow):
    """Fenêtre principale des statistiques."""

    closed = pyqtSignal()

    def __init__(self, db_manager):
        super().__init__()
        self.total_gendarmes_label = None
        self.total_sanctions_label = None
        self.db_manager = db_manager
        self.setWindowTitle("Statistiques")
        self.setMinimumSize(1000, 750)
        self.resize(1280, 800)

        # Style commun pour les cartes
        self.card_style = """
                QFrame {
                    background-color: white;
                    border-radius: 15px;
                    padding: 15px;
                    color : black;
                }
                QFrame:hover {
                    border: 1px solid #6C63FF;
                    font-size: 43px;
                }
            """

        # Création des cartes dès l'initialisation
        self.total_card = self._create_trend_card(
            "-", "Dossiers disciplinaires pour cette année", self.card_style, large=True)
        self.grade_card = self._create_trend_card(
            "-", "Le grade enregistrant le plus\ngrand nombre de sanctions", self.card_style)
        self.service_card = self._create_trend_card(
            "-", "La tranche d'année de service majoritaire dans les fautes", self.card_style, large=True)
        self.graph_card = self._create_graph_card()
        self.subdiv_card = self._create_trend_card(
            "-", "La subdivision enregistrant le\nplus grand nombre de fautes", self.card_style)
        self.absence_card = self._create_trend_card(
            "-", "Le nombre de dossiers d'absence\nirrégulière prolongée cette année", self.card_style)

        # Stockage des fenêtres actives
        self.subject_window = None
        self.visualization_window = None
        self.list_window = None
        self.chart_dialog = None
        self.config_dialog = None

        self.setup_ui()

    def _create_trend_card(self, initial_value, description, style, large=False):
        """Crée une carte de tendance."""
        card = QFrame()
        card.setStyleSheet(style)

        # Layout vertical pour la carte
        layout = QVBoxLayout(card)
        layout.setSpacing(5)

        # Valeur principale
        value_label = QLabel(initial_value)
        value_label.setStyleSheet("""
            font-size: 40px; 
            font-weight: bold;
            font-family: 'Space_Grotesk';
        """
            )
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label)

        # Description
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            font-size: 12px; 
            color: #666666;"
            font-family: 'Space_Grotesk';
        """
        )
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc_label)

        # Définir la taille minimale selon le type de carte
        if large:
            card.setMinimumSize(300, 150)
        else:
            card.setMinimumSize(200, 150)

        # Garder une référence aux labels pour les mises à jour
        card.value_label = value_label
        card.desc_label = desc_label

        return card

    def _create_graph_card(self):
        """Crée la carte avec le graphique."""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #1C1C1E;
                border-radius: 15px;
                padding: 15px;
            }
        """)

        layout = QVBoxLayout(card)

        # Création du graphique
        figure = Figure(figsize=(6, 3), facecolor='#1C1C1E')
        canvas = FigureCanvas(figure)
        canvas.setStyleSheet("background-color: #1C1C1E;")
        layout.addWidget(canvas)

        # Garder les références pour les mises à jour
        card.figure = figure
        card.canvas = canvas

        card.setMinimumSize(400, 200)
        return card

    def setup_ui(self):
        """Configure l'interface utilisateur."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal vertical
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Titre
        title_label = QLabel("Statistiques")
        title_label.setStyleSheet("font-size: 28px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # Container pour les tendances
        trends_container = QFrame()
        trends_container.setStyleSheet("""
                   QFrame {
                       background-color: #E5E5E5;
                       border-radius: 20px;
                       padding: 15px;
                   }
               """)
        trends_layout = QGridLayout(trends_container)
        trends_layout.setSpacing(15)

        # Placement des cartes déjà créées
        trends_layout.addWidget(self.total_card, 0, 0)
        trends_layout.addWidget(self.grade_card, 0, 1)
        trends_layout.addWidget(self.service_card, 0, 2, 1, 2)
        trends_layout.addWidget(self.graph_card, 1, 0, 1, 2)
        trends_layout.addWidget(self.subdiv_card, 1, 2)
        trends_layout.addWidget(self.absence_card, 1, 3)

        main_layout.addWidget(trends_container)

        # Boutons
        buttons_config = [
            {
                "text": "Analyse par sujet",
                "icon": "../resources/icons/analytics.png",
                "callback": self.show_subject_analysis
            },
            {
                "text": "Configuration des tableaux",
                "icon": "../resources/icons/table.png",
                "callback": self.show_table_config
            },
            {
                "text": "Liste exhaustive",
                "icon": "../resources/icons/list.png",
                "callback": self.show_full_list
            },
            {
                "text": "Tendances par année",
                "icon": "../resources/icons/trends.png",
                "callback": self.show_yearly_trends
            }
        ]

        # Style commun pour les boutons
        common_style = """
            QPushButton {
                font-size: 21px;
                text-align: left;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 15px;
                background-color: #D1D5DB;
                min-height: 50px;
                color: #1C1C1E
            }
            QPushButton:hover {
                background-color: #0A84FF;
                font-size: 24px;
                color: #edef7f
            }
            QPushButton:pressed {
                background-color: #dee2e6;
            }
        """

        # Création des boutons
        for btn_config in buttons_config:
            button = QPushButton(btn_config["text"])
            if "icon" in btn_config:
                button.setIcon(QIcon(btn_config["icon"]))
                button.setIconSize(QSize(32, 32))

            button.setStyleSheet(common_style)
            button.setSizePolicy(QSizePolicy.Policy.Expanding,
                                 QSizePolicy.Policy.Fixed)

            if btn_config["callback"]:
                button.clicked.connect(btn_config["callback"])

            main_layout.addWidget(button)

    def update_trends(self):
        """Met à jour toutes les tendances avec les données actuelles."""
        try:
            with self.db_manager.get_connection() as conn:
                current_year = datetime.now().year

                # 1. Total des dossiers de l'année en cours
                total_query = """
                    SELECT MAX(Dossiers.numero_annee )
                    FROM Dossiers
                    WHERE Dossiers.annee_enr = ?
                """
                cursor = conn.cursor()
                cursor.execute(total_query, (str(current_year),))
                total = cursor.fetchone()[0]
                self.total_card.value_label.setText(str(total))

                # 2. Grade le plus sanctionné
                grade_query = """
                    SELECT G.lib_grade, COUNT(D.grade_id ) AS count
                    FROM Dossiers D
                    JOIN Grade G ON D.grade_id  = G.id_grade
                    WHERE D.annee_enr = ?
                    GROUP BY G.lib_grade
                    ORDER BY count  DESC
                    LIMIT 1
                """
                cursor.execute(grade_query, (str(current_year),))
                grade_result = cursor.fetchone()
                if grade_result:
                    self.grade_card.value_label.setText(grade_result[0])

                # 3. Tranche d'années de service la plus fréquente
                service_query = """
                    WITH service_ranges AS (
                      SELECT
                        CASE
                          WHEN g.annee_service BETWEEN 0 AND 5 THEN '0-5ans'
                          WHEN g.annee_service BETWEEN 6 AND 10 THEN '6-10ans'
                          WHEN g.annee_service BETWEEN 11 AND 15 THEN '11-15ans'
                          WHEN g.annee_service BETWEEN 16 AND 20 THEN '16-20ans'
                          WHEN g.annee_service BETWEEN 21 AND 25 THEN '21-25ans'
                          WHEN g.annee_service > 25 THEN '25+ans'
                          ELSE 'Non défini'
                        END AS range,
                        COUNT(*) AS count
                      FROM Gendarmes g
                      JOIN Dossiers d ON g.matricule = d.matricule_dossier
                      WHERE d.annee_enr = ?
                      GROUP BY range
                    )
                    SELECT range, count
                    FROM service_ranges
                    WHERE range != 'Non défini'
                    ORDER BY count DESC
                    LIMIT 1
                """
                cursor.execute(service_query, (str(current_year),))
                service_result = cursor.fetchone()
                if service_result:
                    self.service_card.value_label.setText(service_result[0])

                # 4. Subdivision la plus sanctionnée
                subdiv_query = """
                    SELECT s.lib_subdiv, COUNT (d.subdiv_id) AS count
                    FROM Dossiers d 
                    JOIN Subdiv s ON d.subdiv_id = s.id_subdiv 
                    WHERE d.annee_enr = ?
                    GROUP BY s.lib_subdiv
                    ORDER BY count DESC
                    LIMIT 1
                """
                cursor.execute(subdiv_query, (str(current_year),))
                subdiv_result = cursor.fetchone()
                if subdiv_result:
                    self.subdiv_card.value_label.setText(subdiv_result[0])

                # 5. Nombre de dossiers d'absence irrégulière prolongée
                absence_query = """
                    SELECT f.lib_faute, COUNT(d.faute_id) AS count
                    FROM Dossiers d 
                    JOIN Fautes f ON d.faute_id = f.id_faute 
                    WHERE d.annee_enr = ?
                    AND f.lib_faute = 'ABSENCE IRREGULIERE PROLONGEE'
                """
                cursor.execute(absence_query, (str(current_year),))
                absence_count = cursor.fetchone()[1]
                print(f"Absence irrégulière prolongée count: {absence_count}")  # Pour debug
                self.absence_card.value_label.setText(str(absence_count))

                # 6. Graphique d'évolution
                evolution_query = """
                    SELECT 
                        strftime('%m', date_enr) as mois,
                        CASE strftime('%m', date_enr)
                            WHEN '01' THEN 'Janvier'
                            WHEN '02' THEN 'Février'
                            WHEN '03' THEN 'Mars'
                            WHEN '04' THEN 'Avril'
                            WHEN '05' THEN 'Mai'
                            WHEN '06' THEN 'Juin'
                            WHEN '07' THEN 'Juillet'
                            WHEN '08' THEN 'Août'
                            WHEN '09' THEN 'Septembre'
                            WHEN '10' THEN 'Octobre'
                            WHEN '11' THEN 'Novembre'
                            WHEN '12' THEN 'Décembre'
                        END as mois_nom,
                        COUNT(DISTINCT numero_inc) as count
                    FROM Dossiers d 
                    WHERE d.annee_enr = ?               
                    GROUP BY mois
                    ORDER BY mois
                """
                evolution_df = pd.read_sql_query(evolution_query, conn, params=(str(current_year),))

                # Mise à jour du graphique
                self.graph_card.figure.clear()
                ax = self.graph_card.figure.add_subplot(111)

                # Configuration du style du graphique
                ax.set_facecolor('#1C1C1E')
                ax.spines['bottom'].set_color('#666666')
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_color('#666666')
                ax.tick_params(colors='#666666')

                # Tracer la ligne avec zone d'ombre
                line = ax.plot(evolution_df['mois_nom'], evolution_df['count'],
                               color='#6C63FF', linewidth=2, marker='o')

                # Ajouter l'ombre sous la courbe
                ax.fill_between(evolution_df['mois_nom'], evolution_df['count'],
                                color='#6C63FF', alpha=0.2)

                # Se limiter au mois actuel
                current_month = datetime.now().month
                ax.set_xlim(-0.5, current_month - 0.5)

                # Rotation des labels de mois pour meilleure lisibilité
                plt.xticks(rotation=45, ha='right')

                # Personnalisation finale
                ax.grid(True, linestyle='--', alpha=0.1)
                self.graph_card.canvas.draw()

        except Exception as e:
            print(f"Erreur dans update_trends: {str(e)}")
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors de la mise à jour des tendances : {str(e)}"
            )

    #     # Ajout du bouton de diagnostic
    #     debug_button = QPushButton("Diagnostic des données")
    #     debug_button.setStyleSheet(common_style)
    #     debug_button.setSizePolicy(QSizePolicy.Policy.Expanding,
    #                              QSizePolicy.Policy.Fixed)
    #     debug_button.clicked.connect(self.run_diagnostic)
    #     main_layout.addWidget(debug_button)
    #
    #     # Espacement en bas
    #     main_layout.addStretch()
    #
    # def run_diagnostic(self):
    #     """Lance le diagnostic des données."""
    #     try:
    #         self.db_manager.run_sanctions_diagnostic()
    #         QMessageBox.information(
    #             self,
    #             "Diagnostic terminé",
    #             "Le diagnostic a été effectué. Consultez la console pour les résultats."
    #         )
    #     except Exception as e:
    #         QMessageBox.critical(
    #             self,
    #             "Erreur",
    #             f"Erreur lors du diagnostic : {str(e)}"
    #         )

    def showEvent(self, event):
        """Surcharge de l'événement d'affichage pour mettre à jour les tendances."""
        super().showEvent(event)
        self.update_trends()  # Met à jour les tendances à chaque affichage

    def show_subject_analysis(self):
        """Ouvre la fenêtre d'analyse par sujet."""
        try:
            if not hasattr(self, 'subject_window') or not self.subject_window:
                self.subject_window = SubjectDialog(self.db_manager, self)  # Passer self explicitement

            self.subject_window.show()

        except Exception as e:
            print(f"Erreur dans show_subject_analysis: {str(e)}")
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors de l'ouverture de l'analyse par sujet: {str(e)}"
            )

    # Dans StatistiquesWindow
    def show_table_config(self):
        """Ouvre la fenêtre de configuration des tableaux."""
        try:
            # Vérifier si un sujet a été sélectionné
            if not hasattr(self, 'current_subject'):
                QMessageBox.warning(
                    self,
                    "Attention",
                    "Veuillez d'abord sélectionner un sujet d'analyse."
                )
                return

            # Créer et configurer la boîte de dialogue
            config_dialog = TableConfigDialog(self.db_manager, self)

            # Exécuter la boîte de dialogue
            if config_dialog.exec() == QDialog.DialogCode.Accepted:
                config = config_dialog.get_configuration()
                config['subject_selection'] = self.current_subject

                # Sélection du type de graphique
                chart_dialog = ChartSelectionDialog(config, self)
                if chart_dialog.exec() == QDialog.DialogCode.Accepted:
                    chart_config = chart_dialog.get_selected_chart()

                    # Fermer l'ancienne fenêtre de visualisation si elle existe
                    if hasattr(self, 'visualization_window') and self.visualization_window:
                        self.visualization_window.close()
                        self.visualization_window = None

                    # Créer la nouvelle fenêtre de visualisation
                    self.visualization_window = VisualizationWindow(
                        self.db_manager,
                        config,
                        self
                    )

                    # Positionner et afficher la fenêtre
                    if self.isVisible():
                        geometry = self.geometry()
                        self.visualization_window.move(
                            geometry.x() + 50,
                            geometry.y() + 50
                        )

                    # Charger et afficher les données
                    self.visualization_window.load_data()
                    if hasattr(self.visualization_window, 'df') and self.visualization_window.df is not None:
                        self.visualization_window.update_graph(
                            self.visualization_window.df,
                            chart_config
                        )
                        self.visualization_window.show()
                    else:
                        QMessageBox.critical(
                            self,
                            "Erreur",
                            "Erreur lors du chargement des données"
                        )

        except Exception as e:
            print(f"Erreur dans show_table_config: {str(e)}")
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors de la création de la visualisation : {str(e)}"
            )

    def show_full_list(self):
        """Ouvre la fenêtre de liste exhaustive."""
        if not self.list_window:
            self.list_window = FullListWindow(self.db_manager)
        self.list_window.show()

    def on_visualization_closed(self):
        """Appelé quand la fenêtre de visualisation est fermée."""
        self.visualization_window = None

    def closeEvent(self, event):
        """Gère la fermeture de la fenêtre."""
        # Fermeture de toutes les fenêtres enfants
        windows_to_close = [
            self.subject_window,
            self.visualization_window,
            self.list_window
        ]

        for window in windows_to_close:
            if window and window.isVisible():
                window.close()

        self.closed.emit()
        event.accept()

    def load_global_stats(self):
        """Charge les statistiques globales."""
        try:
            # Utiliser la nouvelle méthode pour récupérer les données
            df = self.get_statistics_data()
            if df is not None:
                stats = self.calculate_statistics()

                if stats:
                    # Requête modifiée pour éviter les doublons en utilisant les données calculées
                    total_sanctions = stats['total_sanctions']
                    total_gendarmes = stats['unique_gendarmes']

                    self.update_stats_labels(total_sanctions, total_gendarmes)

            else:
                # Fallback sur la méthode originale si get_statistics_data échoue
                with self.db_manager.get_connection() as conn:
                    cursor = conn.cursor()

                    # Requête modifiée pour éviter les doublons
                    cursor.execute("""
                        SELECT MAX(d.numero_inc)
                        FROM Dossiers d
                    """)
                    total_sanctions = cursor.fetchone()[0]

                    # Total des gendarmes sanctionnés
                    cursor.execute("""
                        SELECT COUNT(DISTINCT g.matricule)
                        FROM Gendarmes g
                    """)
                    total_gendarmes = cursor.fetchone()[0]

                    self.update_stats_labels(total_sanctions, total_gendarmes)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors du chargement des statistiques: {str(e)}"
            )

    def update_stats_labels(self, total_sanctions, total_gendarmes):
        """Met à jour les labels des statistiques dans l'interface."""
        try:
            self.total_sanctions_label.setText(f"Nombre total de sanctions : {total_sanctions:,}")
            self.total_gendarmes_label.setText(f"Nombre de gendarmes sanctionnés : {total_gendarmes:,}")
        except Exception as e:
            print(f"Erreur dans update_stats_labels: {str(e)}")
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors de la mise à jour des statistiques: {str(e)}"
            )

    def get_statistics_data(self):
        """Récupère et organise les données pour les statistiques"""
        try:
            # Requête mise à jour avec toutes les colonnes directement issues de main_tab
            sanctions_query = """
                        SELECT DISTINCT
                            d.numero_inc,
                            d.id_dossier,
                            d.matricule_dossier,
                            d.reference,
                            d.date_faits,
                            d.annee_enr,
                            gr.lib_grade,
                            u.lib_unite,
                            l.lib_legion,
                            s.lib_subdiv,
                            r.lib_rg,
                            sm.lib_sit_mat,
                            f.lib_faute,
                            c.id_categorie,
                            ts.lib_type_sanction,
                            sa.taux,
                            sa.comite,
                            s2.lib_statut
                        FROM Dossiers d
                        LEFT JOIN Grade gr ON d.grade_id = gr.id_grade
                        LEFT JOIN Unite u ON d.unite_id = u.id_unite
                        LEFT JOIN Legion l ON d.legion_id = l.id_legion
                        LEFT JOIN Subdiv s ON d.subdiv_id = s.id_subdiv
                        LEFT JOIN Region r ON d.rg_id = r.id_rg
                        LEFT JOIN Sit_mat sm ON d.situation_mat_id = sm.id_sit_mat
                        LEFT JOIN Fautes f ON d.faute_id = f.id_faute
                        LEFT JOIN Categories c ON f.cat_id = c.id_categorie
                        LEFT JOIN Sanctions sa ON d.numero_inc = sa.num_inc
                        LEFT JOIN Type_sanctions ts ON sa.type_sanction_id = ts.id_type_sanction
                        LEFT JOIN Statut s2 ON d.statut_id = s2.id_statut 
                        WHERE 1 = 1
                        GROUP BY d.numero_inc  -- Groupe par le numéro d'incrémentation unique
                        ORDER BY d.numero_inc DESC
            """

            with self.db_manager.get_connection() as conn:
                # Récupérer directement toutes les données en une seule requête
                stats_df = pd.read_sql_query(sanctions_query, conn)

            return stats_df

        except Exception as e:
            print(f"Erreur dans get_statistics_data: {str(e)}")
            return None

    def calculate_statistics(self):
        """Calcule les différentes statistiques sur les sanctions"""
        df = self.get_statistics_data()

        if df is None or df.empty:
            print("⚠️ Aucune donnée disponible pour les statistiques.")
            return None

        try:
            stats = {
                'total_sanctions': len(df),
                'unique_gendarmes': df['matricule_dossier'].nunique(),
                'par_categorie': df['id_categorie'].value_counts().to_dict() if 'categorie' in df else {},
                'par_grade': df['lib_grade'].value_counts().to_dict() if 'grade' in df else {},
                'par_subdivision': df['lib_subdiv'].value_counts().to_dict() if 'subdiv' in df else {},
                'par_annee': df['annee_enr'].value_counts().to_dict() if 'annee_enr' in df else {},
                'par_statut': df['lib_statut'].value_counts().to_dict() if 'statut' in df else {},
            }
            return stats

        except Exception as e:
            print(f"❌ Erreur lors du calcul des statistiques : {str(e)}")
            return None

    def show_yearly_trends(self):
        """Ouvre la fenêtre des tendances annuelles"""
        try:
            year, ok = QInputDialog.getInt(
                self,
                'Sélection Année',
                'Entrez l\'année souhaitée:',
                2024,  # valeur par défaut
                2000,  # minimum
                2100  # maximum
            )
            if ok:
                self.trends_window = YearlyTrendsWindow(self.db_manager, year, self)
                # Positionner la fenêtre
                if self.isVisible():
                    geometry = self.geometry()
                    self.trends_window.move(
                        geometry.x() + 50,
                        geometry.y() + 50
                    )
                self.trends_window.show()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors de l'ouverture des tendances: {str(e)}"
            )
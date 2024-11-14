from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton,
                             QHBoxLayout, QLabel, QSizePolicy, QMessageBox, QFrame, QTableWidget, QTableWidgetItem)
from PyQt6.QtCore import pyqtSignal, Qt, QSize
from PyQt6.QtGui import QIcon
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from .subject_dialog import SubjectDialog
from .table_config_dialog import TableConfigDialog
from .visualization_window import VisualizationWindow
from .full_list_window import FullListWindow
from .chart_selection_dialog import ChartSelectionDialog


# ... (imports existants restent identiques)

class StatistiquesWindow(QMainWindow):
    """Fenêtre principale des statistiques."""

    closed = pyqtSignal()

    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setWindowTitle("Statistiques")
        self.setMinimumSize(800, 600)

        # Stockage des fenêtres actives
        self.subject_window = None
        self.visualization_window = None
        self.list_window = None
        self.chart_dialog = None
        self.config_dialog = None

        self.setup_ui()

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

        # Ajout du bouton de diagnostic
        debug_button = QPushButton("Diagnostic des données")
        debug_button.setStyleSheet(common_style)
        debug_button.setSizePolicy(QSizePolicy.Policy.Expanding,
                                 QSizePolicy.Policy.Fixed)
        debug_button.clicked.connect(self.run_diagnostic)
        main_layout.addWidget(debug_button)

        # Espacement en bas
        main_layout.addStretch()

    def run_diagnostic(self):
        """Lance le diagnostic des données."""
        try:
            self.db_manager.run_sanctions_diagnostic()
            QMessageBox.information(
                self,
                "Diagnostic terminé",
                "Le diagnostic a été effectué. Consultez la console pour les résultats."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors du diagnostic : {str(e)}"
            )

    def show_subject_analysis(self):
        """Ouvre la fenêtre d'analyse par sujet."""
        if not self.subject_window:
            self.subject_window = SubjectDialog(self.db_manager)
        self.subject_window.show()

    def show_table_config(self):
        """Ouvre la fenêtre de configuration des tableaux."""
        try:
            # Ouverture unique de la boîte de dialogue de configuration
            config_dialog = TableConfigDialog(self.db_manager, self)
            if config_dialog.exec():
                config = config_dialog.get_configuration()

                # Création d'une seule instance du sélecteur de graphiques
                chart_dialog = ChartSelectionDialog(config, self)
                result = chart_dialog.exec()

                if result == QDialog.DialogCode.Accepted:
                    chart_config = chart_dialog.get_selected_chart()

                    # Fermeture de l'ancienne fenêtre de visualisation si elle existe
                    if hasattr(self, 'visualization_window') and self.visualization_window:
                        self.visualization_window.close()
                        self.visualization_window = None

                    # Création d'une nouvelle fenêtre de visualisation
                    self.visualization_window = VisualizationWindow(
                        self.db_manager,
                        config,
                        self
                    )

                    # Positionnement de la fenêtre
                    if self.isVisible():
                        geometry = self.geometry()
                        self.visualization_window.move(
                            geometry.x() + 50,
                            geometry.y() + 50
                        )

                    # Configuration et affichage
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
            print(f"Erreur dans show_table_config: {str(e)}")  # Debug
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
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()

                # Requête modifiée pour éviter les doublons
                cursor.execute("""
                    WITH unique_sanctions AS (
                        SELECT DISTINCT 
                            numero_dossier,
                            MIN(matricule) as matricule,
                            MIN(date_enr) as date_enr,
                            MIN(unite) as unite,
                            MIN(subdivision) as subdivision
                        FROM sanctions
                        GROUP BY numero_dossier
                    )
                    SELECT COUNT(*) as total_sanctions
                    FROM unique_sanctions
                """)
                total_sanctions = cursor.fetchone()[0]

                # Total des gendarmes sanctionnés
                cursor.execute("""
                    SELECT COUNT(DISTINCT matricule)
                    FROM sanctions
                """)
                total_gendarmes = cursor.fetchone()[0]

                self.update_stats_labels(total_sanctions, total_gendarmes)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors du chargement des statistiques: {str(e)}"
            )
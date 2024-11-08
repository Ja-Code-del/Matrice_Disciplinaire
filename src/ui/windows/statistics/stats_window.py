# from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton,
#                              QHBoxLayout, QLabel, QSizePolicy, QMessageBox, QDialog)
# from PyQt6.QtCore import pyqtSignal, Qt, QSize
# from PyQt6.QtGui import QIcon
# from .subject_dialog import SubjectDialog
# from .table_config_dialog import TableConfigDialog
# from .visualization_window import VisualizationWindow
# from .full_list_window import FullListWindow
#
#
# class StatistiquesWindow(QMainWindow):
#     """Fenêtre principale des statistiques."""
#
#     closed = pyqtSignal()
#
#     def __init__(self, db_manager):
#         super().__init__()
#         self.db_manager = db_manager
#         self.setWindowTitle("Statistiques")
#         self.setMinimumSize(800, 600)
#
#         # Stockage des fenêtres actives
#         self.subject_window = None
#         self.visualization_window = None
#         self.list_window = None
#
#         self.setup_ui()
#
#     def setup_ui(self):
#         """Configure l'interface utilisateur."""
#         central_widget = QWidget()
#         self.setCentralWidget(central_widget)
#
#         # Layout principal vertical
#         main_layout = QVBoxLayout(central_widget)
#         main_layout.setSpacing(20)
#         main_layout.setContentsMargins(20, 20, 20, 20)
#
#         # Titre
#         title_label = QLabel("Statistiques")
#         title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
#         title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         main_layout.addWidget(title_label)
#
#         # Boutons
#         buttons_config = [
#             {
#                 "text": "Analyse par sujet",
#                 "icon": "../resources/icons/analytics.png",
#                 "callback": self.show_subject_analysis
#             },
#             {
#                 "text": "Configuration des tableaux",
#                 "icon": "../resources/icons/table.png",
#                 "callback": self.show_table_config
#             },
#             {
#                 "text": "Liste exhaustive",
#                 "icon": "../resources/icons/list.png",
#                 "callback": self.show_full_list
#             }
#         ]
#
#         # Style commun pour les boutons
#         common_style = """
#             QPushButton {
#                 text-align: left;
#                 padding: 10px;
#                 border: 1px solid #ccc;
#                 border-radius: 5px;
#                 background-color: #f8f9fa;
#                 min-height: 50px;
#             }
#             QPushButton:hover {
#                 background-color: #e9ecef;
#             }
#             QPushButton:pressed {
#                 background-color: #dee2e6;
#             }
#         """
#
#         # Création des boutons
#         for btn_config in buttons_config:
#             button = QPushButton(btn_config["text"])
#             if "icon" in btn_config:
#                 button.setIcon(QIcon(btn_config["icon"]))
#                 button.setIconSize(QSize(32, 32))
#
#             button.setStyleSheet(common_style)
#             button.setSizePolicy(QSizePolicy.Policy.Expanding,
#                                  QSizePolicy.Policy.Fixed)
#
#             if btn_config["callback"]:
#                 button.clicked.connect(btn_config["callback"])
#
#             main_layout.addWidget(button)
#
#         # Espacement en bas
#         main_layout.addStretch()
#
#     def show_subject_analysis(self):
#         """Ouvre la fenêtre d'analyse par sujet."""
#         if not self.subject_window:
#             self.subject_window = SubjectDialog(self.db_manager)
#         self.subject_window.show()
#
#     def show_table_config(self):
#         """Ouvre la fenêtre de configuration des tableaux."""
#         try:
#             dialog = TableConfigDialog(self.db_manager, self)
#             if dialog.exec():
#                 # Récupération de la configuration
#                 config = dialog.get_configuration()
#
#                 # Fermeture de la fenêtre de visualisation précédente si elle existe
#                 if self.visualization_window:
#                     self.visualization_window.close()
#
#                 # Création de la nouvelle fenêtre de visualisation
#                 self.visualization_window = VisualizationWindow(
#                     self.db_manager,
#                     config,
#                     self
#                 )
#
#                 # Positionnement de la fenêtre
#                 if self.isVisible():
#                     geometry = self.geometry()
#                     self.visualization_window.move(
#                         geometry.x() + 50,
#                         geometry.y() + 50
#                     )
#
#                 # Configuration des signaux
#                 self.visualization_window.closed.connect(self.on_visualization_closed)
#
#                 # Affichage de la fenêtre
#                 self.visualization_window.show()
#
#         except Exception as e:
#             print(f"Erreur lors de la création de la visualisation : {str(e)}")
#             # Réaffichage de la boîte de dialogue de configuration en cas d'erreur
#             self.show_table_config()
#
#     def show_full_list(self):
#         """Ouvre la fenêtre de liste exhaustive."""
#         if not self.list_window:
#             self.list_window = FullListWindow(self.db_manager)
#         self.list_window.show()
#
#     def on_visualization_closed(self):
#         """Appelé quand la fenêtre de visualisation est fermée."""
#         self.visualization_window = None
#
#     def closeEvent(self, event):
#         """Gère la fermeture de la fenêtre."""
#         # Fermeture de toutes les fenêtres enfants
#         windows_to_close = [
#             self.subject_window,
#             self.visualization_window,
#             self.list_window
#         ]
#
#         for window in windows_to_close:
#             if window and window.isVisible():
#                 window.close()
#
#         self.closed.emit()
#         event.accept()

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
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
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
                text-align: left;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #f8f9fa;
                min-height: 50px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
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

        # Espacement en bas
        main_layout.addStretch()

    def show_subject_analysis(self):
        """Ouvre la fenêtre d'analyse par sujet."""
        if not self.subject_window:
            self.subject_window = SubjectDialog(self.db_manager)
        self.subject_window.show()

    def show_table_config(self):
        """Ouvre la fenêtre de configuration des tableaux."""
        try:
            # Création et affichage du dialogue de configuration
            dialog = TableConfigDialog(self.db_manager, self)
            if dialog.exec():
                # Récupération de la configuration
                config = dialog.get_configuration()

                # Fermeture de la fenêtre de visualisation précédente si elle existe
                if self.visualization_window:
                    self.visualization_window.close()

                # Création de la nouvelle fenêtre de visualisation
                self.visualization_window = VisualizationWindow(
                    self.db_manager,
                    config,
                    self
                )

                # Positionnement de la fenêtre
                if self.isVisible():
                    # Positionnement relatif à la fenêtre principale
                    geometry = self.geometry()
                    self.visualization_window.move(
                        geometry.x() + 50,
                        geometry.y() + 50
                    )

                # Configuration des signaux
                self.visualization_window.closed.connect(self.on_visualization_closed)

                # Affichage de la fenêtre
                self.visualization_window.show()

        except Exception as e:
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
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()

                # Total des sanctions
                cursor.execute("SELECT COUNT(*) FROM sanctions")
                total_sanctions = cursor.fetchone()[0]

                # Total des gendarmes sanctionnés
                cursor.execute("""
                    SELECT COUNT(DISTINCT matricule)
                    FROM sanctions
                """)
                total_gendarmes = cursor.fetchone()[0]

                # Mise à jour des labels
                self.update_stats_labels(total_sanctions, total_gendarmes)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors du chargement des statistiques: {str(e)}"
            )
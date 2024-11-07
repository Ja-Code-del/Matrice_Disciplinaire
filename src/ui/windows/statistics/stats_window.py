# src/ui/windows/statistics/stats_window.py

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton,
                             QHBoxLayout, QLabel, QSizePolicy)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QIcon, QSize
from .subject_dialog import SubjectDialog
from .table_config_dialog import TableConfigDialog
from .full_list_window import FullListWindow


class StatistiquesWindow(QMainWindow):
    """Fenêtre principale des statistiques."""

    closed = pyqtSignal()  # Signal émis à la fermeture

    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setWindowTitle("Statistiques")
        self.setMinimumSize(800, 600)

        # Stockage des sous-fenêtres
        self.subject_window = None
        self.table_window = None
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
        dialog = TableConfigDialog(self.db_manager, self)
        if dialog.exec():
            # Si l'utilisateur valide, récupérer la config et créer la visualisation
            config = dialog.get_configuration()
            # TODO: Créer la fenêtre de visualisation avec la config

    def show_full_list(self):
        """Ouvre la fenêtre de liste exhaustive."""
        if not self.list_window:
            self.list_window = FullListWindow(self.db_manager)
        self.list_window.show()

    def closeEvent(self, event):
        """Gère la fermeture de la fenêtre."""
        # Fermer toutes les sous-fenêtres
        for window in [self.subject_window, self.table_window, self.list_window]:
            if window:
                window.close()

        self.closed.emit()
        event.accept()
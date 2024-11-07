# src/ui/handlers/stats_handler.py

from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QObject, pyqtSignal
from ..windows.statistics.stats_window import StatistiquesWindow
from ...database.db_manager import DatabaseManager
from typing import Optional
import logging


class StatsHandler(QObject):
    """Gestionnaire pour la partie statistiques de l'application."""

    # Signaux
    statsWindowClosed = pyqtSignal()
    databaseError = pyqtSignal(str)

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.stats_window: Optional[StatistiquesWindow] = None
        self.db_manager = DatabaseManager()

        # Configuration du logging
        self.logger = logging.getLogger(__name__)

        # Connexion des signaux
        self.databaseError.connect(self._show_database_error)

    def check_database(self) -> bool:
        """Vérifie l'état de la base de données."""
        try:
            if not self.db_manager.is_connected():
                raise Exception("La base de données n'est pas connectée")

            required_tables = ['sanctions', 'gendarmes']
            for table in required_tables:
                if not self.db_manager.table_exists(table):
                    raise Exception(f"La table {table} n'existe pas")

            self._verify_data_integrity()
            return True

        except Exception as e:
            self.logger.error(f"Erreur base de données: {str(e)}")
            self.databaseError.emit(str(e))
            return False

    def _verify_data_integrity(self):
        """Vérifie l'intégrité des données."""
        try:
            sanctions_count = self.db_manager.count_records('sanctions')
            gendarmes_count = self.db_manager.count_records('gendarmes')

            if sanctions_count == 0:
                raise Exception("Aucune sanction enregistrée")
            if gendarmes_count == 0:
                raise Exception("Aucun gendarme enregistré")

            self._check_relations()

        except Exception as e:
            raise Exception(f"Erreur d'intégrité: {str(e)}")

    def _check_relations(self):
        """Vérifie les relations entre tables."""
        query = """
        SELECT COUNT(*) FROM sanctions s 
        LEFT JOIN gendarmes g ON CAST(s.matricule AS TEXT) = g.mle 
        WHERE g.mle IS NULL
        """
        orphan_count = self.db_manager.execute_query(query).fetchone()[0]

        if orphan_count > 0:
            self.logger.warning(f"{orphan_count} sanctions sans gendarme associé")

    def open_statistics(self):
        """Ouvre la fenêtre des statistiques."""
        try:
            if not self.check_database():
                return

            if self.stats_window is not None and self.stats_window.isVisible():
                self.stats_window.activateWindow()
                self.stats_window.raise_()
                return

            self.stats_window = StatistiquesWindow(self.db_manager)
            self.stats_window.closed.connect(self._on_stats_window_closed)
            self._setup_stats_window()
            self.stats_window.show()

        except Exception as e:
            self.logger.error(f"Erreur ouverture stats: {str(e)}")
            self._show_error("Erreur", str(e))

    def _setup_stats_window(self):
        """Configure la position de la fenêtre."""
        if self.stats_window and self.main_window:
            geometry = self.main_window.geometry()
            self.stats_window.move(
                geometry.x() + 50,
                geometry.y() + 50
            )

    def _on_stats_window_closed(self):
        """Gère la fermeture de la fenêtre."""
        self.stats_window = None
        self.statsWindowClosed.emit()

    def close_statistics(self):
        """Ferme la fenêtre des statistiques."""
        if self.stats_window:
            self.stats_window.close()
            self.stats_window = None

    def _show_database_error(self, message: str):
        """Affiche une erreur de base de données."""
        QMessageBox.critical(
            self.main_window,
            "Erreur de base de données",
            f"Erreur d'accès à la base de données:\n{message}"
        )

    def _show_error(self, title: str, message: str):
        """Affiche une erreur générique."""
        QMessageBox.critical(self.main_window, title, message)

    def cleanup(self):
        """Nettoie les ressources."""
        self.close_statistics()
        self.db_manager = None
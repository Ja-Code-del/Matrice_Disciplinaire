from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QObject, pyqtSignal
from matplotlib import pyplot as plt

from ..windows.statistics.stats_window import StatistiquesWindow
import logging

# Cache global
_global_cache = {
    'data': {},
    'charts': {},
    'queries': {}
}

class StatsHandler(QObject):
    """Gestionnaire pour la partie statistiques de l'application."""

    _cache = {}  # Pour stocker les données fréquemment utilisées

    # Signaux
    statsWindowClosed = pyqtSignal()
    databaseError = pyqtSignal(str)

    def __init__(self, main_window):
        """
        Initialise le gestionnaire de statistiques.

        Args:
            main_window: La fenêtre principale de l'application
        """
        print("\n=== Initialisation StatsHandler ===")
        super().__init__()
        self.main_window = main_window
        print(f"Main window type: {type(self.main_window)}")

        if hasattr(self.main_window, 'db_manager'):
            print("✓ db_manager trouvé dans main_window")
            print(f"Type de db_manager: {type(self.main_window.db_manager)}")
        else:
            print("✗ ERREUR: pas de db_manager dans main_window")

        self.stats_window = None

        # Configuration du logging
        self.logger = logging.getLogger(__name__)

        # Connexion des signaux
        self.databaseError.connect(self._show_database_error)
        print("=== Fin Initialisation StatsHandler ===\n")

    def check_database(self) -> bool:
        """Vérifie l'état de la base de données."""
        print("\n=== Début check_database ===")
        try:
            print("1. Vérification de la présence du db_manager...")
            if not hasattr(self.main_window, 'db_manager'):
                raise Exception("Pas de gestionnaire de base de données")

            print("2. Vérification de l'initialisation du db_manager...")
            if not self.main_window.db_manager:
                raise Exception("Le gestionnaire de base de données n'est pas initialisé")

            print("3. Test de connexion...")
            if not self.main_window.db_manager.is_connected():
                raise Exception("La base de données n'est pas connectée")

            print("4. Vérification des tables...")
            required_tables = ['main_tab']
            for table in required_tables:
                print(f"   Vérification de la table {table}...")
                if not self.main_window.db_manager.table_exists(table):
                    raise Exception(f"La table {table} n'existe pas")

                print(f"   Comptage des enregistrements dans {table}...")
                count = self.main_window.db_manager.count_records(table)
                print(f"   → {count} enregistrements trouvés dans {table}")
                if count == 0:
                    raise Exception(f"La table {table} est vide")

            print("✓ Toutes les vérifications sont OK")
            return True

        except Exception as e:
            print(f"✗ Erreur dans check_database: {str(e)}")
            self.logger.error(f"Erreur lors de la vérification de la base de données: {str(e)}")
            self.databaseError.emit(str(e))
            return False
        finally:
            print("=== Fin check_database ===\n")

    def open_statistics(self):
        """Ouvre la fenêtre des statistiques."""
        print("\n=== Début open_statistics ===")
        try:
            print("1. Vérification de la base de données...")
            if not self.check_database():
                print("✗ Échec de la vérification de la base de données")
                return

            print("2. Vérification de la fenêtre existante...")
            if self.stats_window is not None and self.stats_window.isVisible():
                print("→ Fenêtre existante trouvée, mise au premier plan")
                self.stats_window.activateWindow()
                self.stats_window.raise_()
                return

            print("3. Création de la nouvelle fenêtre...")
            self.stats_window = StatistiquesWindow(self.main_window.db_manager)

            print("4. Configuration des signaux...")
            self.stats_window.closed.connect(self._on_stats_window_closed)

            print("5. Configuration de la position...")
            self._setup_stats_window()

            print("6. Affichage de la fenêtre")
            self.stats_window.show()
            print("✓ Fenêtre affichée avec succès")

        except Exception as e:
            print(f"✗ Erreur dans open_statistics: {str(e)}")
            self.logger.error(f"Erreur lors de l'ouverture des statistiques: {str(e)}")
            self._show_error("Erreur", f"Impossible d'ouvrir les statistiques: {str(e)}")
        finally:
            print("=== Fin open_statistics ===\n")

    def _setup_stats_window(self):
        """Configure la fenêtre des statistiques."""
        print("=== Configuration de la fenêtre ===")
        if self.stats_window is None:
            print("✗ Pas de fenêtre à configurer")
            return

        if self.main_window is not None:
            geometry = self.main_window.geometry()
            print(f"Position de la fenêtre principale: {geometry.x()}, {geometry.y()}")
            self.stats_window.move(
                geometry.x() + 50,
                geometry.y() + 50
            )
            print("✓ Position de la fenêtre configurée")

    def _on_stats_window_closed(self):
        """Gestionnaire appelé lors de la fermeture de la fenêtre des statistiques."""
        print("=== Fermeture de la fenêtre des statistiques ===")
        self.stats_window = None
        self.statsWindowClosed.emit()
        print("✓ Nettoyage effectué")

    def close_statistics(self):
        """Ferme proprement la fenêtre des statistiques si elle est ouverte."""
        print("=== Demande de fermeture des statistiques ===")
        if self.stats_window is not None:
            print("→ Fermeture de la fenêtre")
            self.stats_window.close()
            self.stats_window = None
            print("✓ Fenêtre fermée")
        else:
            print("→ Pas de fenêtre à fermer")

    def _show_database_error(self, message: str):
        """
        Affiche une boîte de dialogue d'erreur pour les problèmes de base de données.

        Args:
            message: Le message d'erreur à afficher
        """
        print(f"=== Affichage erreur base de données: {message} ===")
        QMessageBox.critical(
            self.main_window,
            "Erreur de base de données",
            f"Erreur d'accès à la base de données:\n{message}"
        )

    def _show_error(self, title: str, message: str):
        """
        Affiche une boîte de dialogue d'erreur générique.

        Args:
            title: Le titre de la boîte de dialogue
            message: Le message d'erreur à afficher
        """
        print(f"=== Affichage erreur: {title} - {message} ===")
        QMessageBox.critical(self.main_window, title, message)

    def cleanup(self):
        """Nettoyage amélioré des ressources"""
        self._cache.clear()
        if self.stats_window:
            self.stats_window.close()
            self.stats_window = None
        print("✓ Nettoyage complet effectué")

    # def cleanup(self):
    #     """
    #     Nettoie les ressources utilisées par le handler.
    #     À appeler avant la fermeture de l'application.
    #     """
    #     print("=== Nettoyage du StatsHandler ===")
    #     self.close_statistics()
    #     print("✓ Nettoyage terminé")

    def get_current_stats_window(self):
        """Retourne la fenêtre des statistiques si elle est ouverte."""
        if hasattr(self, 'statistics_window') and self.statistics_window:
            return self.statistics_window
        return None
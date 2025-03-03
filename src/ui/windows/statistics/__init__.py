# src/ui/windows/statistics/__init__.py

"""
Package de gestion des statistiques pour l'application Gend_Track.
Ce module contient toutes les fenêtres et composants nécessaires
à l'affichage et l'analyse des statistiques.
"""

from .stats_window import StatistiquesWindow
from .subject_dialog import SubjectDialog
from .table_config_dialog import TableConfigDialog
from .visualization_window import VisualizationWindow
from .full_list_window import FullListWindow
from .yearly_trends_window import YearlyTrendsWindow

__all__ = [
    'StatistiquesWindow',
    'SubjectDialog',
    'TableConfigDialog',
    'VisualizationWindow',
    'FullListWindow',
    'YearlyTrendsWindow'
]

# Version du module
__version__ = '2.0.0'

# Méta-données du package
__author__ = 'Bret Walda'
__email__ = 'qafamunto@gmail.com'
__status__ = 'Development'

# Description des composants
COMPONENTS = {
    'StatistiquesWindow': 'Fenêtre principale des statistiques',
    'SubjectDialog': 'Boîte de dialogue pour le choix du sujet d\'analyse',
    'TableConfigDialog': 'Configuration des tableaux de statistiques',
    'VisualizationWindow': 'Affichage des graphiques et tableaux',
    'FullListWindow': 'Liste exhaustive des sanctionnés avec filtres',
    'YearlyTrendsWindow': 'Affichage global des données par année.'
}
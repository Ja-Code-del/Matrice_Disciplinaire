from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                             QPushButton, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from src.ui.styles.styles import Styles


class StatsWindow(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setWindowTitle("Menu des Statistiques")
        self.setMinimumSize(600, 800)  # Plus haut pour les boutons empilés
        self.init_ui()

    def init_ui(self):
        # Widget principal centré
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)  # Espace entre les boutons

        # Liste des options avec leurs icônes
        options = [
            ("📊 Statistiques Globales", "global_stats", self.show_global_stats),
            ("🏢 Classement des Subdivisions", "subdiv_stats", self.show_subdiv_stats),
            ("📈 Évolution Temporelle", "time_stats", self.show_time_stats),
            ("👥 Statistiques par Grade", "grade_stats", self.show_grade_stats),
            ("⚖️ Types de Fautes", "fault_stats", self.show_fault_stats),
            ("📅 Périodes des Sanctions", "period_stats", self.show_period_stats),
        ]

        # Création des boutons stylés
        for text, name, callback in options:
            btn = self.create_menu_button(text, callback)
            layout.addWidget(btn)

    def create_menu_button(self, text, callback):
        """Crée un bouton stylé avec effet hover"""
        btn = QPushButton(text)
        btn.setFixedSize(400, 80)  # Taille fixe pour tous les boutons
        btn.setCursor(Qt.CursorShape.PointingHandCursor)  # Curseur main au survol

        # Style de base
        btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                padding: 15px;
                font-size: 16px;
                text-align: left;
                padding-left: 20px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
                border: 2px solid #007bff;
                transform: scale(1.05);
            }
        """)

        # Effet d'ombre
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 0)
        shadow.setColor(Qt.GlobalColor.gray)
        btn.setGraphicsEffect(shadow)

        # Connection du callback
        btn.clicked.connect(callback)

        return btn

    # Méthodes pour chaque type de stats
    def show_global_stats(self):
        """Affiche les stats globales"""
        from src.ui.stats_views.global_stats import GlobalStatsWindow
        self.global_stats = GlobalStatsWindow(self.db_manager)
        self.global_stats.show()

    def show_subdiv_stats(self):
        """Affiche les stats par subdivision"""
        from src.ui.stats_views.subdiv_stats import SubdivStatsWindow
        self.subdiv_stats = SubdivStatsWindow(self.db_manager)
        self.subdiv_stats.show()

    def show_time_stats(self):
        """Affiche l'évolution temporelle"""
        from src.ui.stats_views.time_stats import TimeStatsWindow
        self.time_stats = TimeStatsWindow(self.db_manager)
        self.time_stats.show()

    def show_grade_stats(self):
        """Affiche les stats par grade"""
        from src.ui.stats_views.grade_stats import GradeStatsWindow
        self.grade_stats = GradeStatsWindow(self.db_manager)
        self.grade_stats.show()

    def show_fault_stats(self):
        """Affiche les stats par type de faute"""
        from src.ui.stats_views.fault_stats import FaultStatsWindow
        self.fault_stats = FaultStatsWindow(self.db_manager)
        self.fault_stats.show()

    def show_period_stats(self):
        """Affiche les stats par période"""
        from src.ui.stats_views.period_stats import PeriodStatsWindow
        self.period_stats = PeriodStatsWindow(self.db_manager)
        self.period_stats.show()
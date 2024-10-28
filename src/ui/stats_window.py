from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                             QPushButton, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt

from src.ui.stats_views.global_stats import GlobalStatsWindow
from src.ui.styles.styles import Styles
from src.ui.stats_views.global_stats import GlobalStatsWindow


class StatsWindow(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        self.punis_list = None
        self.global_stats = None
        self.db_manager = db_manager
        self.setWindowTitle("Menu des Statistiques")
        self.setMinimumSize(600, 800)  # Plus haut pour les boutons empilés
        self.is_dark_mode = False
        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        # Style de la fenêtre adapté au thème
        if self.is_dark_mode:
            # Style camouflage pour le mode sombre
            self.setStyleSheet("""
                  QMainWindow {
                      background-color: #1e4785;
                      background-image: qradialgradient(
                          cx: 0.5, cy: 0.5, radius: 1.5,
                          fx: 0.5, fy: 0.5,
                          stop: 0 #1e4785,
                          stop: 0.3 #2c5aa0,
                          stop: 0.6 #7691c1,
                          stop: 0.9 #b7c9e5,
                          stop: 1 #1e4785
                      );
                  }
                  QWidget {
                      background: transparent;
                  }
              """)
        else:
            # Style Anthropic pour le mode clair
            self.setStyleSheet("""
                  QMainWindow {
                      background-color: #ffffff;
                  }
                  QWidget {
                      background: transparent;
                  }
              """)

        # Liste des options avec leurs icônes
        options = [
            ("📊 Statistiques Globales", "global_stats", self.show_global_stats),
            ("🏢 Classement des Subdivisions", "subdiv_stats", self.show_subdiv_stats),
            ("📈 Évolution Temporelle", "time_stats", self.show_time_stats),
            ("👥 Statistiques par Grade", "grade_stats", self.show_grade_stats),
            ("⚖️ Types de Fautes", "fault_stats", self.show_fault_stats),
            ("📅 Périodes des Sanctions", "period_stats", self.show_period_stats),
            ("👥 Liste Complète des Punis", "punis_list", self.show_punis_list),
        ]

        # Création des boutons stylés
        for text, name, callback in options:
            btn = self.create_menu_button(text, callback)
            layout.addWidget(btn)

    def create_menu_button(self, text, callback):
        btn = QPushButton(text)
        btn.setFixedSize(400, 80)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)

        # Style conditionnel selon le thème
        if self.is_dark_mode:
            # Notre style camouflage actuel pour le mode sombre
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #1e4785;
                    border: none;
                    border-radius: 10px;
                    padding: 15px;
                    font-size: 16px;
                    font-weight: bold;
                    text-align: left;
                    padding-left: 20px;
                    color: white;
                    background: qradialgradient(
                        cx: 0.5, cy: 0.5, radius: 1,
                        fx: 0.5, fy: 0.5,
                        stop: 0 #1e4785,
                        stop: 0.4 #2c5aa0,
                        stop: 0.6 #7691c1,
                        stop: 0.8 #b7c9e5,
                        stop: 1 #1e4785
                    );
                }
                QPushButton:hover {
                    background: qradialgradient(
                        cx: 0.5, cy: 0.5, radius: 1,
                        fx: 0.5, fy: 0.5,
                        stop: 0 #2c5aa0,
                        stop: 0.4 #7691c1,
                        stop: 0.6 #b7c9e5,
                        stop: 0.8 #ffffff,
                        stop: 1 #2c5aa0
                    );
                }
            """)
        else:
            # Style Anthropic pour le mode clair
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #ffffff;
                    border: 1px solid #e5e5e5;
                    border-radius: 10px;
                    padding: 15px;
                    font-size: 16px;
                    font-weight: 500;
                    text-align: left;
                    padding-left: 20px;
                    color: #333333;
                }
                QPushButton:hover {
                    background-color: #f5f5f5;
                    border: 1px solid #d0d0d0;
                    transform: translateY(-2px);
                }
            """)

        # Effet d'ombre adapté au thème
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 4)
        shadow.setColor(Qt.GlobalColor.darkBlue if self.is_dark_mode else Qt.GlobalColor.gray)
        btn.setGraphicsEffect(shadow)

        btn.clicked.connect(callback)
        return btn

    #Méthodes pour chaque type de stats
    def show_global_stats(self):
        """Affiche les stats globales"""
        self.global_stats = GlobalStatsWindow(self.db_manager)
        self.global_stats.show()

    #
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

    def show_punis_list(self):
        """Affiche la liste complète des punis"""
        from src.ui.stats_views.punis_list import PunisListWindow
        self.punis_list = PunisListWindow(self.db_manager)
        self.punis_list.show()

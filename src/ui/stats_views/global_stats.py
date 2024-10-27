from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QGroupBox)
from PyQt6.QtCharts import QChart, QChartView, QBarSet, QBarSeries, QPieSeries
from PyQt6.QtGui import QPainter
from PyQt6.QtCore import Qt
from src.ui.styles.styles import Styles


class GlobalStatsWindow(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setWindowTitle("Statistiques Globales")
        self.setMinimumSize(1200, 800)
        self.init_ui()
        self.load_stats()

    def init_ui(self):
        """Initialise l'interface utilisateur"""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # En-tête avec les chiffres clés
        header = QGroupBox("Chiffres Clés")
        header_layout = QHBoxLayout()

        # Widgets pour les stats rapides
        self.total_sanctions = self.create_stat_widget("Total Sanctions", "0")
        self.top_type = self.create_stat_widget("Type le plus fréquent", "-")
        self.moy_jar = self.create_stat_widget("Moyenne JAR", "0")

        header_layout.addWidget(self.total_sanctions)
        header_layout.addWidget(self.top_type)
        header_layout.addWidget(self.moy_jar)
        header.setLayout(header_layout)

        layout.addWidget(header)

        # Zone des graphiques
        charts_container = QGroupBox("Visualisations")
        charts_layout = QHBoxLayout()

        # On préparera les graphiques ici

        charts_container.setLayout(charts_layout)
        layout.addWidget(charts_container)

    def create_stat_widget(self, title, value):
        """Crée un widget pour afficher une statistique"""
        widget = QWidget()
        layout = QVBoxLayout()

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #007bff;
            }
        """)

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        widget.setLayout(layout)

        return widget

    def load_stats(self):
        """Charge les statistiques depuis la base de données"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()

                # Total des sanctions
                cursor.execute("SELECT COUNT(*) FROM sanctions")
                total = cursor.fetchone()[0]
                self.total_sanctions.findChild(QLabel, "", options=Qt.FindChildOption.FindChildrenRecursively)[
                    -1].setText(str(total))

                # Type le plus fréquent
                cursor.execute("""
                    SELECT statut, COUNT(*) as count
                    FROM sanctions
                    GROUP BY statut
                    ORDER BY count DESC
                    LIMIT 1
                """)
                result = cursor.fetchone()
                if result:
                    self.top_type.findChild(QLabel, "", options=Qt.FindChildOption.FindChildrenRecursively)[-1].setText(
                        result[0])

                # Moyenne JAR
                cursor.execute("""
                    SELECT ROUND(AVG(taux_jar), 1)
                    FROM sanctions 
                    WHERE taux_jar IS NOT NULL
                """)
                moyenne = cursor.fetchone()[0] or 0
                self.moy_jar.findChild(QLabel, "", options=Qt.FindChildOption.FindChildrenRecursively)[-1].setText(
                    f"{moyenne} jours")

        except Exception as e:
            print(f"Erreur lors du chargement des stats : {str(e)}")
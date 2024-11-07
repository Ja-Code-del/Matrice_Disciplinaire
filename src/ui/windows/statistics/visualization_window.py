# src/ui/windows/statistics/visualization_window.py

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QLabel, QFrame)
from PyQt6.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd


class VisualizationWindow(QMainWindow):
    """Fenêtre de visualisation des données statistiques."""

    def __init__(self, db_manager, config, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.config = config
        self.setWindowTitle("Visualisation des statistiques")
        self.setMinimumSize(1000, 800)

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # En-tête avec informations
        header = QFrame()
        header.setFrameStyle(QFrame.Shape.StyledPanel)
        header_layout = QVBoxLayout(header)

        self.title_label = QLabel("Analyse statistique")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        header_layout.addWidget(self.title_label)

        self.info_label = QLabel()
        header_layout.addWidget(self.info_label)

        main_layout.addWidget(header)

        # Tableau de données
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        main_layout.addWidget(self.table)

        # Zone du graphique
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        main_layout.addWidget(self.canvas)

        # Boutons d'export
        export_layout = QHBoxLayout()

        self.btn_excel = QPushButton("Exporter Excel")
        self.btn_excel.clicked.connect(self.export_excel)

        self.btn_pdf = QPushButton("Exporter PDF")
        self.btn_pdf.clicked.connect(self.export_pdf)

        self.btn_pptx = QPushButton("Exporter PowerPoint")
        self.btn_pptx.clicked.connect(self.export_pptx)

        export_layout.addWidget(self.btn_excel)
        export_layout.addWidget(self.btn_pdf)
        export_layout.addWidget(self.btn_pptx)
        export_layout.addStretch()

        main_layout.addLayout(export_layout)

    def load_data(self):
        """Charge et affiche les données selon la configuration."""
        try:
            # Construction de la requête
            x_field = self.config["x_axis"]
            y_field = self.config["y_axis"]

            query = f"""
            SELECT s.{x_field}, s.{y_field}, COUNT(*) as count
            FROM sanctions s
            LEFT JOIN gendarmes g ON CAST(s.matricule AS TEXT) = g.mle
            GROUP BY s.{x_field}, s.{y_field}
            ORDER BY s.{x_field}, s.{y_field}
            """

            # Exécution de la requête
            df = pd.read_sql_query(query, self.db_manager.get_connection())

            # Mise à jour du tableau
            self.update_table(df)

            # Mise à jour du graphique
            self.update_graph(df)

            # Mise à jour des informations
            self.update_info(df)

        except Exception as e:
            print(f"Erreur lors du chargement des données: {str(e)}")

    def update_table(self, df):
        """Met à jour le tableau avec les données."""
        # Configuration du tableau
        self.table.setRowCount(len(df))
        self.table.setColumnCount(len(df.columns))
        self.table.setHorizontalHeaderLabels(df.columns)

        # Remplissage des données
        for i in range(len(df)):
            for j in range(len(df.columns)):
                item = QTableWidgetItem(str(df.iloc[i, j]))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(i, j, item)

        self.table.resizeColumnsToContents()

    def update_graph(self, df):
        """Met à jour le graphique avec les données."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # Création du graphique (à adapter selon les données)
        if self.config.get("options", {}).get("cumulative"):
            df.plot(kind='line', ax=ax)
        else:
            df.plot(kind='bar', ax=ax)

        ax.set_xlabel(self.config["x_axis"])
        ax.set_ylabel(self.config["y_axis"])
        ax.set_title("Analyse statistique")

        self.figure.tight_layout()
        self.canvas.draw()

    def update_info(self, df):
        """Met à jour les informations d'en-tête."""
        total = df['count'].sum()
        self.info_label.setText(f"Total des enregistrements : {total}")

    def export_excel(self):
        """Exporte les données vers Excel."""
        # TODO: Implémenter l'export Excel
        pass

    def export_pdf(self):
        """Exporte les données vers PDF."""
        # TODO: Implémenter l'export PDF
        pass

    def export_pptx(self):
        """Exporte les données vers PowerPoint."""
        # TODO: Implémenter l'export PowerPoint
        pass
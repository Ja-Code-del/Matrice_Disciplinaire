# src/ui/windows/statistics/visualization_window.py
import os
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (QFileDialog, QMessageBox, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel,
                             QTableWidget, QPushButton, QTableWidgetItem)
#pour excel
import pandas as pd
#pour les pdf
from reportlab.lib import colors, utils
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
#pour powerpoint
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.oxml import parse_xml
#pour les graphiques et les tableaux
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from datetime import datetime

from src.data.gendarmerie.structure import SUBDIVISIONS, SERVICE_RANGES, ANALYSIS_THEMES

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QLabel, QFrame, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
from src.data.gendarmerie.structure import SUBDIVISIONS, SERVICE_RANGES, ANALYSIS_THEMES


class VisualizationWindow(QMainWindow):
    """Fenêtre de visualisation des données statistiques."""

    closed = pyqtSignal()

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
            x_config = self.config["x_axis"]
            y_config = self.config["y_axis"]

            # Fonction pour construire la clause CASE pour les années de service
            def get_service_years_case():
                return """
                CASE 
                    WHEN g.annee_service BETWEEN 0 AND 5 THEN '0-5 ANS'
                    WHEN g.annee_service BETWEEN 6 AND 10 THEN '6-10 ANS'
                    WHEN g.annee_service BETWEEN 11 AND 15 THEN '11-15 ANS'
                    WHEN g.annee_service BETWEEN 16 AND 20 THEN '16-20 ANS'
                    WHEN g.annee_service BETWEEN 21 AND 25 THEN '21-25 ANS'
                    WHEN g.annee_service BETWEEN 26 AND 30 THEN '26-30 ANS'
                    WHEN g.annee_service BETWEEN 31 AND 35 THEN '31-35 ANS'
                    WHEN g.annee_service BETWEEN 36 AND 40 THEN '36-40 ANS'
                END
                """

            # Construction des champs pour la requête
            def get_field_expression(config):
                field = config["field"]
                if field == "annee_service":
                    return get_service_years_case()
                elif field in ["grade", "situation_matrimoniale", "subdiv"]:
                    return f"g.{field}"
                else:
                    return f"s.{field}"

            x_expr = get_field_expression(x_config)
            y_expr = get_field_expression(y_config)

            # Construction de la requête
            query = f"""
            SELECT 
                {x_expr} as x_value,
                {y_expr} as y_value,
                COUNT(*) as count
            FROM sanctions s
            LEFT JOIN gendarmes g ON CAST(s.matricule AS TEXT) = g.mle
            WHERE 1=1
            """

            params = []

            # Ajout des conditions de filtrage
            def add_filter_condition(config, expr):
                nonlocal query, params
                value = config.get("value", "")
                if value and not value.startswith("Tous"):
                    if config["field"] == "annee_service":
                        start, end = map(int, value.split("-")[0:2])
                        query += f" AND g.annee_service BETWEEN ? AND ?"
                        params.extend([start, end])
                    else:
                        table_prefix = "g" if config["field"] in ["grade", "situation_matrimoniale", "subdiv"] else "s"
                        query += f" AND {table_prefix}.{config['field']} = ?"
                        params.append(value)

            add_filter_condition(x_config, x_expr)
            add_filter_condition(y_config, y_expr)

            query += """
            GROUP BY x_value, y_value
            ORDER BY x_value, y_value
            """

            print(f"Executing query: {query}")  # Pour le débogage
            print(f"With parameters: {params}")  # Pour le débogage

            # Exécution de la requête
            with self.db_manager.get_connection() as conn:
                df = pd.read_sql_query(query, conn, params=params)

            print(f"Query results:\n{df}")  # Pour le débogage

            # Mise à jour des composants visuels
            self.update_table(df)
            self.update_graph(df)
            self.update_info(df)

        except Exception as e:
            print(f"Error in load_data: {str(e)}")  # Pour le débogage
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors du chargement des données: {str(e)}"
            )

    def update_table(self, df):
        """Met à jour le tableau avec les données."""
        self.table.setRowCount(len(df))
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['X', 'Y', 'Nombre'])

        for i in range(len(df)):
            for j, col in enumerate(['x_value', 'y_value', 'count']):
                item = QTableWidgetItem(str(df.iloc[i][col]))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(i, j, item)

        self.table.resizeColumnsToContents()

    def update_graph(self, df):
        """Met à jour le graphique avec les données."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        if len(df) > 10:  # Si beaucoup de données, utiliser un graphique en barres vertical
            df.plot(kind='bar', x='x_value', y='count', ax=ax)
            plt.xticks(rotation=45)
        else:  # Sinon utiliser un graphique en barres horizontal
            df.plot(kind='barh', x='x_value', y='count', ax=ax)

        ax.set_title(f"{self.config['y_axis']['theme']} par {self.config['x_axis']['theme']}")
        ax.set_xlabel(self.config['x_axis']['theme'])
        ax.set_ylabel('Nombre')

        self.figure.tight_layout()
        self.canvas.draw()

    def update_info(self, df):
        """Met à jour les informations d'en-tête."""
        total = df['count'].sum()
        self.info_label.setText(
            f"Total: {total} | "
            f"Moyenne: {df['count'].mean():.2f} | "
            f"Maximum: {df['count'].max()} | "
            f"Minimum: {df['count'].min()}"
        )

    def export_excel(self):
        """Exporte les données vers Excel avec mise en forme."""
        try:
            # Demander à l'utilisateur où sauvegarder le fichier
            default_name = f"statistiques_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Enregistrer le fichier Excel",
                default_name,
                "Excel Files (*.xlsx)"
            )

            if not file_path:  # L'utilisateur a annulé
                return

            # Création d'un writer Excel avec le moteur XlsxWriter pour la prise en charge d'insert_image
            with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
                # Récupération des données du tableau
                table_data = []
                headers = [self.table.horizontalHeaderItem(j).text() for j in range(self.table.columnCount())]

                for i in range(self.table.rowCount()):
                    row = [self.table.item(i, j).text() if self.table.item(i, j) else "" for j in
                           range(self.table.columnCount())]
                    table_data.append(row)

                # Création du DataFrame
                df = pd.DataFrame(table_data, columns=headers)

                # Export du DataFrame vers Excel
                df.to_excel(writer, sheet_name='Données', index=False)

                # Sauvegarde temporaire du graphique en tant qu'image
                self.figure.savefig('temp_chart.png')

                # Accès à la feuille de calcul et insertion de l'image
                worksheet = writer.sheets['Données']
                worksheet.insert_image('A' + str(len(df) + 3), 'temp_chart.png')

                # Ajustement de la largeur des colonnes
                for i, col in enumerate(df.columns):
                    max_length = max(df[col].astype(str).apply(len).max(), len(col))
                    worksheet.set_column(i, i, max_length + 2)

            # Suppression du fichier d'image temporaire
            if os.path.exists('temp_chart.png'):
                os.remove('temp_chart.png')

            # Message de succès
            QMessageBox.information(
                self,
                "Succès",
                f"Les données ont été exportées vers:\n{file_path}"
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors de l'export Excel:\n{str(e)}"
            )

    def export_pdf(self):
        """Exporte les données vers PDF avec mise en forme."""
        try:
            # Demander à l'utilisateur où sauvegarder le fichier
            default_name = f"statistiques_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Enregistrer le fichier PDF",
                default_name,
                "PDF Files (*.pdf)"
            )

            if not file_path:  # L'utilisateur a annulé
                return

            # Création du document PDF
            doc = SimpleDocTemplate(
                file_path,
                pagesize=landscape(letter),
                rightMargin=30,
                leftMargin=30,
                topMargin=30,
                bottomMargin=30
            )

            # Liste des éléments à ajouter au PDF
            elements = []
            styles = getSampleStyleSheet()

            # Titre
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30
            )
            title = Paragraph(
                "Rapport Statistique",
                title_style
            )
            elements.append(title)

            # Sous-titre avec date et informations
            subtitle_style = ParagraphStyle(
                'CustomSubTitle',
                parent=styles['Normal'],
                fontSize=12,
                spaceAfter=20
            )
            subtitle = Paragraph(
                f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
                subtitle_style
            )
            elements.append(subtitle)

            # Informations sur les axes
            info = Paragraph(
                f"Analyse: {self.config['x_axis']} par {self.config['y_axis']}",
                subtitle_style
            )
            elements.append(info)
            elements.append(Spacer(1, 20))

            # Création des données du tableau
            table_data = []
            headers = []

            # En-têtes
            for j in range(self.table.columnCount()):
                headers.append(self.table.horizontalHeaderItem(j).text())
            table_data.append(headers)

            # Données
            for i in range(self.table.rowCount()):
                row = []
                for j in range(self.table.columnCount()):
                    item = self.table.item(i, j)
                    row.append(item.text() if item else "")
                table_data.append(row)

            # Style du tableau
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWHEIGHT', (0, 0), (-1, -1), 25),
            ])

            # Création et style du tableau
            pdf_table = Table(table_data, repeatRows=1)
            pdf_table.setStyle(table_style)
            elements.append(pdf_table)

            # Ajout du graphique
            elements.append(Spacer(1, 30))

            # Sauvegarde temporaire du graphique
            graph_path = 'temp_graph.png'
            self.figure.savefig(graph_path, format='png', dpi=300, bbox_inches='tight')

            # Ajout du graphique au PDF avec une taille maximale
            max_width = 500
            img = utils.ImageReader(graph_path)
            img_width, img_height = img.getSize()
            aspect = img_height / float(img_width)

            elements.append(Image(graph_path, width=max_width, height=max_width * aspect))

            # Construction du document
            doc.build(elements)

            # Nettoyage
            if os.path.exists(graph_path):
                os.remove(graph_path)

            QMessageBox.information(
                self,
                "Succès",
                f"Les données ont été exportées vers:\n{file_path}"
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors de l'export PDF:\n{str(e)}"
            )

    def export_pptx(self):
        """Exporte les données vers PowerPoint avec mise en forme."""
        try:
            # Demander à l'utilisateur où sauvegarder le fichier
            default_name = f"statistiques_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pptx"
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Enregistrer la présentation PowerPoint",
                default_name,
                "PowerPoint Files (*.pptx)"
            )

            if not file_path:  # L'utilisateur a annulé
                return

            # Création de la présentation
            prs = Presentation()

            # Définir la taille des diapositives (16:9)
            prs.slide_width = Inches(13.333)
            prs.slide_height = Inches(7.5)

            # Slide de titre
            title_slide_layout = prs.slide_layouts[0]
            slide = prs.slides.add_slide(title_slide_layout)
            title = slide.shapes.title
            subtitle = slide.placeholders[1]

            title.text = "Rapport Statistique"
            subtitle.text = f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}"

            # Slide d'information
            bullet_slide_layout = prs.slide_layouts[1]
            slide = prs.slides.add_slide(bullet_slide_layout)
            shapes = slide.shapes

            title_shape = shapes.title
            body_shape = shapes.placeholders[1]

            title_shape.text = "Informations de l'analyse"

            tf = body_shape.text_frame
            tf.text = f"Analyse des données"

            p = tf.add_paragraph()
            p.text = f"Axe X: {str(self.config['x_axis'])}"
            p.level = 1

            p = tf.add_paragraph()
            p.text = f"Axe Y: {str(self.config['y_axis'])}"
            p.level = 1

            # Slide des données
            slide = prs.slides.add_slide(prs.slide_layouts[5])
            shapes = slide.shapes

            title = shapes.title
            title.text = "Données"

            # Ajout du tableau
            rows = self.table.rowCount() + 1  # +1 pour l'en-tête
            cols = self.table.columnCount()

            left = Inches(1)
            top = Inches(2)
            width = prs.slide_width - Inches(2)
            height = prs.slide_height - Inches(3)

            table = shapes.add_table(rows, cols, left, top, width, height).table

            # Remplissage des en-têtes
            for col in range(cols):
                # S'assurer que l'en-tête existe et le convertir en string
                header_item = self.table.horizontalHeaderItem(col)
                header_text = str(header_item.text()) if header_item else f"Colonne {col + 1}"

                cell = table.cell(0, col)
                cell.text = header_text

                # Style de l'en-tête
                paragraph = cell.text_frame.paragraphs[0]
                paragraph.font.size = Pt(11)
                paragraph.font.bold = True
                paragraph.font.color.rgb = RGBColor(255, 255, 255)
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(44, 62, 80)

            # Remplissage des données
            for row in range(self.table.rowCount()):
                for col in range(cols):
                    # S'assurer que la cellule existe et convertir son contenu en string
                    item = self.table.item(row, col)
                    cell_text = str(item.text()) if item else ""

                    table_cell = table.cell(row + 1, col)
                    table_cell.text = cell_text

                    # Style des données
                    paragraph = table_cell.text_frame.paragraphs[0]
                    paragraph.font.size = Pt(10)
                    paragraph.alignment = PP_ALIGN.CENTER

            # Slide du graphique
            slide = prs.slides.add_slide(prs.slide_layouts[5])
            shapes = slide.shapes
            title = shapes.title
            title.text = "Visualisation"

            # Sauvegarde temporaire du graphique
            graph_path = 'temp_graph.png'
            self.figure.savefig(graph_path, format='png', dpi=300, bbox_inches='tight')

            # Ajout du graphique
            left = Inches(1)
            top = Inches(2)
            pic = slide.shapes.add_picture(
                graph_path,
                left,
                top,
                width=prs.slide_width - Inches(2)
            )

            # Sauvegarde de la présentation
            prs.save(file_path)

            # Nettoyage
            if os.path.exists(graph_path):
                os.remove(graph_path)

            QMessageBox.information(
                self,
                "Succès",
                f"Les données ont été exportées vers:\n{file_path}"
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors de l'export PowerPoint:\n{str(e)}"
            )


# class VisualizationWindow(QMainWindow):
#     """Fenêtre de visualisation des données statistiques."""
#
#     # Ajout du signal
#     closed = pyqtSignal()
#
#     def __init__(self, db_manager, config, parent=None):
#         super().__init__(parent)
#         self.db_manager = db_manager
#         self.config = config
#         self.setWindowTitle("Visualisation des statistiques")
#         self.setMinimumSize(1000, 800)
#
#         self.setup_ui()
#         self.load_data()
#
#     def setup_ui(self):
#         central_widget = QWidget()
#         self.setCentralWidget(central_widget)
#         main_layout = QVBoxLayout(central_widget)
#
#         # En-tête avec informations
#         header = QFrame()
#         header.setFrameStyle(QFrame.Shape.StyledPanel)
#         header_layout = QVBoxLayout(header)
#
#         self.title_label = QLabel("Analyse statistique")
#         self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
#         header_layout.addWidget(self.title_label)
#
#         self.info_label = QLabel()
#         header_layout.addWidget(self.info_label)
#
#         main_layout.addWidget(header)
#
#         # Tableau de données
#         self.table = QTableWidget()
#         self.table.setAlternatingRowColors(True)
#         main_layout.addWidget(self.table)
#
#         # Zone du graphique
#         self.figure = Figure(figsize=(8, 6))
#         self.canvas = FigureCanvas(self.figure)
#         main_layout.addWidget(self.canvas)
#
#         # Boutons d'export
#         export_layout = QHBoxLayout()
#
#         self.btn_excel = QPushButton("Exporter Excel")
#         self.btn_excel.clicked.connect(self.export_excel)
#
#         self.btn_pdf = QPushButton("Exporter PDF")
#         self.btn_pdf.clicked.connect(self.export_pdf)
#
#         self.btn_pptx = QPushButton("Exporter PowerPoint")
#         self.btn_pptx.clicked.connect(self.export_pptx)
#
#         export_layout.addWidget(self.btn_excel)
#         export_layout.addWidget(self.btn_pdf)
#         export_layout.addWidget(self.btn_pptx)
#         export_layout.addStretch()
#
#         main_layout.addLayout(export_layout)
#
#     def load_data(self):
#         """Charge et affiche les données selon la configuration."""
#         try:
#             x_config = self.config["x_axis"]
#             y_config = self.config["y_axis"]
#
#             # Fonction pour construire la clause CASE pour les années de service
#             def get_service_years_case():
#                 return """
#                 CASE
#                     WHEN annee_service BETWEEN 0 AND 5 THEN '0-5 ANS'
#                     WHEN annee_service BETWEEN 6 AND 10 THEN '6-10 ANS'
#                     WHEN annee_service BETWEEN 11 AND 15 THEN '11-15 ANS'
#                     WHEN annee_service BETWEEN 16 AND 20 THEN '16-20 ANS'
#                     WHEN annee_service BETWEEN 21 AND 25 THEN '21-25 ANS'
#                     WHEN annee_service BETWEEN 26 AND 30 THEN '26-30 ANS'
#                     WHEN annee_service BETWEEN 31 AND 35 THEN '31-35 ANS'
#                     WHEN annee_service BETWEEN 36 AND 40 THEN '36-40 ANS'
#                 END
#                 """
#
#             # Construction des champs pour la requête
#             def get_field_expression(config):
#                 field = config["field"]
#                 if field == "annee_service":
#                     return get_service_years_case()
#                 return field
#
#             x_field = get_field_expression(x_config)
#             y_field = get_field_expression(y_config)
#
#             # Déterminer la table source pour chaque champ
#             x_table = "g" if x_config["field"] in ["grade", "subdiv", "annee_service",
#                                                    "situation_matrimoniale"] else "s"
#             y_table = "g" if y_config["field"] in ["grade", "subdiv", "annee_service",
#                                                    "situation_matrimoniale"] else "s"
#
#             # Construction de la requête
#             query = f"""
#             SELECT
#                 {x_table}.{x_field} as x_value,
#                 {y_table}.{y_field} as y_value,
#                 COUNT(*) as count
#             FROM sanctions s
#             LEFT JOIN gendarmes g ON CAST(s.matricule AS TEXT) = g.mle
#             WHERE 1=1
#             """
#
#             # Ajout des conditions de filtrage si nécessaire
#             if x_config["value"] != f"Tous les {x_config['theme'].lower()}":
#                 query += f" AND {x_table}.{x_config['field']} = ?"
#                 params.append(x_config["value"])
#
#             if y_config["value"] != f"Tous les {y_config['theme'].lower()}":
#                 query += f" AND {y_table}.{y_config['field']} = ?"
#                 params.append(y_config["value"])
#
#             query += f"""
#             GROUP BY x_value, y_value
#             ORDER BY x_value, y_value
#             """
#
#             with self.db_manager.get_connection() as conn:
#                 df = pd.read_sql_query(query, conn, params=params)
#
#             self.update_table(df)
#             self.update_graph(df)
#             self.update_info(df)
#
#         except Exception as e:
#             QMessageBox.critical(self, "Erreur",
#                                  f"Erreur lors du chargement des données: {str(e)}")
#
#     def closeEvent(self, event):
#         """Gère la fermeture de la fenêtre."""
#         self.closed.emit()
#         event.accept()
#
#     def update_table(self, df):
#         """Met à jour le tableau avec les données."""
#         # Configuration du tableau
#         self.table.setRowCount(len(df))
#         self.table.setColumnCount(len(df.columns))
#         self.table.setHorizontalHeaderLabels(df.columns)
#
#         # Remplissage des données
#         for i in range(len(df)):
#             for j in range(len(df.columns)):
#                 item = QTableWidgetItem(str(df.iloc[i, j]))
#                 item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
#                 self.table.setItem(i, j, item)
#
#         self.table.resizeColumnsToContents()
#
#     def update_graph(self, df):
#         """Met à jour le graphique avec les données."""
#         self.figure.clear()
#         ax = self.figure.add_subplot(111)
#
#         # Création du graphique (à adapter selon les données)
#         if self.config.get("options", {}).get("cumulative"):
#             df.plot(kind='line', ax=ax)
#         else:
#             df.plot(kind='bar', ax=ax)
#
#         ax.set_xlabel(self.config["x_axis"])
#         ax.set_ylabel(self.config["y_axis"])
#         ax.set_title("Analyse statistique")
#
#         self.figure.tight_layout()
#         self.canvas.draw()
#
#     def update_info(self, df):
#         """Met à jour les informations d'en-tête."""
#         total = df['count'].sum()
#         self.info_label.setText(f"Total des enregistrements : {total}")
#
#     def export_excel(self):
#         """Exporte les données vers Excel avec mise en forme."""
#         try:
#             # Demander à l'utilisateur où sauvegarder le fichier
#             default_name = f"statistiques_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
#             file_path, _ = QFileDialog.getSaveFileName(
#                 self,
#                 "Enregistrer le fichier Excel",
#                 default_name,
#                 "Excel Files (*.xlsx)"
#             )
#
#             if not file_path:  # L'utilisateur a annulé
#                 return
#
#             # Création d'un writer Excel avec le moteur XlsxWriter pour la prise en charge d'insert_image
#             with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
#                 # Récupération des données du tableau
#                 table_data = []
#                 headers = [self.table.horizontalHeaderItem(j).text() for j in range(self.table.columnCount())]
#
#                 for i in range(self.table.rowCount()):
#                     row = [self.table.item(i, j).text() if self.table.item(i, j) else "" for j in
#                            range(self.table.columnCount())]
#                     table_data.append(row)
#
#                 # Création du DataFrame
#                 df = pd.DataFrame(table_data, columns=headers)
#
#                 # Export du DataFrame vers Excel
#                 df.to_excel(writer, sheet_name='Données', index=False)
#
#                 # Sauvegarde temporaire du graphique en tant qu'image
#                 self.figure.savefig('temp_chart.png')
#
#                 # Accès à la feuille de calcul et insertion de l'image
#                 worksheet = writer.sheets['Données']
#                 worksheet.insert_image('A' + str(len(df) + 3), 'temp_chart.png')
#
#                 # Ajustement de la largeur des colonnes
#                 for i, col in enumerate(df.columns):
#                     max_length = max(df[col].astype(str).apply(len).max(), len(col))
#                     worksheet.set_column(i, i, max_length + 2)
#
#             # Suppression du fichier d'image temporaire
#             if os.path.exists('temp_chart.png'):
#                 os.remove('temp_chart.png')
#
#             # Message de succès
#             QMessageBox.information(
#                 self,
#                 "Succès",
#                 f"Les données ont été exportées vers:\n{file_path}"
#             )
#
#         except Exception as e:
#             QMessageBox.critical(
#                 self,
#                 "Erreur",
#                 f"Erreur lors de l'export Excel:\n{str(e)}"
#             )
#
#     def export_pdf(self):
#         """Exporte les données vers PDF avec mise en forme."""
#         try:
#             # Demander à l'utilisateur où sauvegarder le fichier
#             default_name = f"statistiques_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
#             file_path, _ = QFileDialog.getSaveFileName(
#                 self,
#                 "Enregistrer le fichier PDF",
#                 default_name,
#                 "PDF Files (*.pdf)"
#             )
#
#             if not file_path:  # L'utilisateur a annulé
#                 return
#
#             # Création du document PDF
#             doc = SimpleDocTemplate(
#                 file_path,
#                 pagesize=landscape(letter),
#                 rightMargin=30,
#                 leftMargin=30,
#                 topMargin=30,
#                 bottomMargin=30
#             )
#
#             # Liste des éléments à ajouter au PDF
#             elements = []
#             styles = getSampleStyleSheet()
#
#             # Titre
#             title_style = ParagraphStyle(
#                 'CustomTitle',
#                 parent=styles['Heading1'],
#                 fontSize=16,
#                 spaceAfter=30
#             )
#             title = Paragraph(
#                 "Rapport Statistique",
#                 title_style
#             )
#             elements.append(title)
#
#             # Sous-titre avec date et informations
#             subtitle_style = ParagraphStyle(
#                 'CustomSubTitle',
#                 parent=styles['Normal'],
#                 fontSize=12,
#                 spaceAfter=20
#             )
#             subtitle = Paragraph(
#                 f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
#                 subtitle_style
#             )
#             elements.append(subtitle)
#
#             # Informations sur les axes
#             info = Paragraph(
#                 f"Analyse: {self.config['x_axis']} par {self.config['y_axis']}",
#                 subtitle_style
#             )
#             elements.append(info)
#             elements.append(Spacer(1, 20))
#
#             # Création des données du tableau
#             table_data = []
#             headers = []
#
#             # En-têtes
#             for j in range(self.table.columnCount()):
#                 headers.append(self.table.horizontalHeaderItem(j).text())
#             table_data.append(headers)
#
#             # Données
#             for i in range(self.table.rowCount()):
#                 row = []
#                 for j in range(self.table.columnCount()):
#                     item = self.table.item(i, j)
#                     row.append(item.text() if item else "")
#                 table_data.append(row)
#
#             # Style du tableau
#             table_style = TableStyle([
#                 ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
#                 ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                 ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                 ('FONTSIZE', (0, 0), (-1, 0), 12),
#                 ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#                 ('BACKGROUND', (0, 1), (-1, -1), colors.white),
#                 ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
#                 ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
#                 ('FONTSIZE', (0, 1), (-1, -1), 10),
#                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                 ('GRID', (0, 0), (-1, -1), 1, colors.black),
#                 ('ROWHEIGHT', (0, 0), (-1, -1), 25),
#             ])
#
#             # Création et style du tableau
#             pdf_table = Table(table_data, repeatRows=1)
#             pdf_table.setStyle(table_style)
#             elements.append(pdf_table)
#
#             # Ajout du graphique
#             elements.append(Spacer(1, 30))
#
#             # Sauvegarde temporaire du graphique
#             graph_path = 'temp_graph.png'
#             self.figure.savefig(graph_path, format='png', dpi=300, bbox_inches='tight')
#
#             # Ajout du graphique au PDF avec une taille maximale
#             max_width = 500
#             img = utils.ImageReader(graph_path)
#             img_width, img_height = img.getSize()
#             aspect = img_height / float(img_width)
#
#             elements.append(Image(graph_path, width=max_width, height=max_width * aspect))
#
#             # Construction du document
#             doc.build(elements)
#
#             # Nettoyage
#             if os.path.exists(graph_path):
#                 os.remove(graph_path)
#
#             QMessageBox.information(
#                 self,
#                 "Succès",
#                 f"Les données ont été exportées vers:\n{file_path}"
#             )
#
#         except Exception as e:
#             QMessageBox.critical(
#                 self,
#                 "Erreur",
#                 f"Erreur lors de l'export PDF:\n{str(e)}"
#             )
#
#     def export_pptx(self):
#         """Exporte les données vers PowerPoint avec mise en forme."""
#         try:
#             # Demander à l'utilisateur où sauvegarder le fichier
#             default_name = f"statistiques_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pptx"
#             file_path, _ = QFileDialog.getSaveFileName(
#                 self,
#                 "Enregistrer la présentation PowerPoint",
#                 default_name,
#                 "PowerPoint Files (*.pptx)"
#             )
#
#             if not file_path:  # L'utilisateur a annulé
#                 return
#
#             # Création de la présentation
#             prs = Presentation()
#
#             # Définir la taille des diapositives (16:9)
#             prs.slide_width = Inches(13.333)
#             prs.slide_height = Inches(7.5)
#
#             # Slide de titre
#             title_slide_layout = prs.slide_layouts[0]
#             slide = prs.slides.add_slide(title_slide_layout)
#             title = slide.shapes.title
#             subtitle = slide.placeholders[1]
#
#             title.text = "Rapport Statistique"
#             subtitle.text = f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}"
#
#             # Slide d'information
#             bullet_slide_layout = prs.slide_layouts[1]
#             slide = prs.slides.add_slide(bullet_slide_layout)
#             shapes = slide.shapes
#
#             title_shape = shapes.title
#             body_shape = shapes.placeholders[1]
#
#             title_shape.text = "Informations de l'analyse"
#
#             tf = body_shape.text_frame
#             tf.text = f"Analyse des données"
#
#             p = tf.add_paragraph()
#             p.text = f"Axe X: {str(self.config['x_axis'])}"
#             p.level = 1
#
#             p = tf.add_paragraph()
#             p.text = f"Axe Y: {str(self.config['y_axis'])}"
#             p.level = 1
#
#             # Slide des données
#             slide = prs.slides.add_slide(prs.slide_layouts[5])
#             shapes = slide.shapes
#
#             title = shapes.title
#             title.text = "Données"
#
#             # Ajout du tableau
#             rows = self.table.rowCount() + 1  # +1 pour l'en-tête
#             cols = self.table.columnCount()
#
#             left = Inches(1)
#             top = Inches(2)
#             width = prs.slide_width - Inches(2)
#             height = prs.slide_height - Inches(3)
#
#             table = shapes.add_table(rows, cols, left, top, width, height).table
#
#             # Remplissage des en-têtes
#             for col in range(cols):
#                 # S'assurer que l'en-tête existe et le convertir en string
#                 header_item = self.table.horizontalHeaderItem(col)
#                 header_text = str(header_item.text()) if header_item else f"Colonne {col + 1}"
#
#                 cell = table.cell(0, col)
#                 cell.text = header_text
#
#                 # Style de l'en-tête
#                 paragraph = cell.text_frame.paragraphs[0]
#                 paragraph.font.size = Pt(11)
#                 paragraph.font.bold = True
#                 paragraph.font.color.rgb = RGBColor(255, 255, 255)
#                 cell.fill.solid()
#                 cell.fill.fore_color.rgb = RGBColor(44, 62, 80)
#
#             # Remplissage des données
#             for row in range(self.table.rowCount()):
#                 for col in range(cols):
#                     # S'assurer que la cellule existe et convertir son contenu en string
#                     item = self.table.item(row, col)
#                     cell_text = str(item.text()) if item else ""
#
#                     table_cell = table.cell(row + 1, col)
#                     table_cell.text = cell_text
#
#                     # Style des données
#                     paragraph = table_cell.text_frame.paragraphs[0]
#                     paragraph.font.size = Pt(10)
#                     paragraph.alignment = PP_ALIGN.CENTER
#
#             # Slide du graphique
#             slide = prs.slides.add_slide(prs.slide_layouts[5])
#             shapes = slide.shapes
#             title = shapes.title
#             title.text = "Visualisation"
#
#             # Sauvegarde temporaire du graphique
#             graph_path = 'temp_graph.png'
#             self.figure.savefig(graph_path, format='png', dpi=300, bbox_inches='tight')
#
#             # Ajout du graphique
#             left = Inches(1)
#             top = Inches(2)
#             pic = slide.shapes.add_picture(
#                 graph_path,
#                 left,
#                 top,
#                 width=prs.slide_width - Inches(2)
#             )
#
#             # Sauvegarde de la présentation
#             prs.save(file_path)
#
#             # Nettoyage
#             if os.path.exists(graph_path):
#                 os.remove(graph_path)
#
#             QMessageBox.information(
#                 self,
#                 "Succès",
#                 f"Les données ont été exportées vers:\n{file_path}"
#             )
#
#         except Exception as e:
#             QMessageBox.critical(
#                 self,
#                 "Erreur",
#                 f"Erreur lors de l'export PowerPoint:\n{str(e)}"
#             )

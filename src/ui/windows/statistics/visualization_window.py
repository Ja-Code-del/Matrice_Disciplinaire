# src/ui/windows/statistics/visualization_window.py
import os
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (QFileDialog, QMessageBox, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel,
                             QTableWidget, QPushButton, QTableWidgetItem, QHeaderView, QSizePolicy)
from PyQt6.QtGui import QColor
#pour les graphiques et les tableaux
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import seaborn as sns

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

from src.data.gendarmerie.structure import SUBDIVISIONS, SERVICE_RANGES, ANALYSIS_THEMES

from datetime import datetime

from openpyxl.utils import get_column_letter
from openpyxl.styles import Font, PatternFill


class VisualizationWindow(QMainWindow):
    """Fenêtre de visualisation des données statistiques."""

    closed = pyqtSignal()

    def __init__(self, db_manager, config, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.config = config
        self.setWindowTitle("Visualisation des statistiques")
        self.setMinimumSize(1000, 800)

        # Configuration du style Seaborn
        sns.set_style("whitegrid")
        sns.set_palette("husl")

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Configure l'interface utilisateur."""
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
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                gridline-color: black;
                border: 1px solid black;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """)
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

            print(f"Executing query: {query}")  # Débogage
            print(f"With parameters: {params}")  # Débogage

            with self.db_manager.get_connection() as conn:
                df = pd.read_sql_query(query, conn, params=params)

            print(f"Query results:\n{df}")  # Débogage

            # Mise à jour des composants visuels
            self.update_table(df)
            self.update_graph(df, 'bar_stacked')  # Type de graphique par défaut
            self.update_info(df)

        except Exception as e:
            print(f"Error in load_data: {str(e)}")
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors du chargement des données: {str(e)}"
            )

    def update_table(self, df):
        """Met à jour le tableau avec les données sous forme de tableau croisé."""
        try:
            # Création du tableau croisé dynamique
            pivot_table = pd.pivot_table(
                df,
                values='count',
                index='y_value',
                columns='x_value',
                fill_value=0,
                margins=True,
                margins_name='TOTAL'
            )

            # Configuration du tableau
            self.table.clear()
            self.table.setRowCount(len(pivot_table.index))
            self.table.setColumnCount(len(pivot_table.columns))

            # En-têtes
            self.table.setHorizontalHeaderLabels(pivot_table.columns.astype(str))
            self.table.setVerticalHeaderLabels(pivot_table.index.astype(str))

            # Remplissage des données
            for i in range(len(pivot_table.index)):
                for j in range(len(pivot_table.columns)):
                    value = pivot_table.iloc[i, j]
                    item = QTableWidgetItem(str(int(value)))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                    # Style pour les totaux
                    if (pivot_table.index[i] == 'TOTAL' or
                            pivot_table.columns[j] == 'TOTAL'):
                        item.setBackground(QColor(128, 128, 128))
                        item.setForeground(QColor(255, 255, 255))
                        font = item.font()
                        font.setBold(True)
                        item.setFont(font)
                    else:
                        item.setBackground(QColor(220, 220, 220))

                    self.table.setItem(i, j, item)

            # Style des en-têtes
            header_style = """
                QHeaderView::section {
                    background-color: rgb(0, 85, 127);
                    color: white;
                    padding: 6px;
                    border: 1px solid #005580;
                    font-weight: bold;
                }
            """
            self.table.horizontalHeader().setStyleSheet(header_style)
            self.table.verticalHeader().setStyleSheet(header_style)

            # Ajustement des dimensions
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

            self.table.setShowGrid(True)
            self.table.setGridStyle(Qt.PenStyle.SolidLine)

        except Exception as e:
            print(f"Erreur dans update_table: {str(e)}")
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors de la mise à jour du tableau: {str(e)}"
            )

    def update_graph(self, df, chart_type='bar_stacked'):
        """Met à jour le graphique selon le type choisi avec Seaborn."""
        try:
            # Nettoyage du graphique précédent
            self.figure.clear()
            ax = self.figure.add_subplot(111)

            # Configuration du style Seaborn
            sns.set_style("whitegrid")
            sns.set_palette("husl")

            # Création du pivot pour le graphique si nécessaire
            pivot_table = pd.pivot_table(
                df,
                values='count',
                index='y_value',
                columns='x_value',
                fill_value=0
            )

            if chart_type == 'bar_stacked':
                self._create_stacked_bar_sns(ax, pivot_table)
            elif chart_type == 'bar_grouped':
                self._create_grouped_bar_sns(ax, df)
            elif chart_type == 'pie':
                self._create_pie_chart_sns(ax, df)
            elif chart_type == 'donut':
                self._create_donut_chart_sns(ax, df)
            elif chart_type == 'bar_stacked':
                self._create_stacked_bar_sns(ax, pivot_table)
            elif chart_type == 'line':
                self._create_line_chart_sns(ax, pivot_table)
            elif chart_type == 'heatmap':
                self._create_heatmap_sns(ax, pivot_table)
            elif chart_type == 'violin':
                self._create_violin_plot_sns(ax, df)
            elif chart_type == 'swarm':
                self._create_swarm_plot_sns(ax, df)
            elif chart_type == 'box':
                self._create_box_plot_sns(ax, df)
            elif chart_type == 'kde':
                self._create_kde_plot_sns(ax, df)
            elif chart_type == 'bar_count':
                self._create_count_plot_sns(ax, df)
            elif chart_type == 'strip':
                self._create_strip_plot_sns(ax, df)
            else:
                self._create_stacked_bar_sns(ax, pivot_table)

            # Ajustement de la mise en page
            self.figure.tight_layout()
            self.canvas.draw()

        except Exception as e:
            print(f"Erreur dans update_graph: {str(e)}")
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors de la mise à jour du graphique: {str(e)}"
            )

    # Méthodes de création des différents types de graphiques
    def _create_stacked_bar_sns(self, ax, pivot_table):
        """Crée un graphique à barres empilées avec Seaborn."""
        pivot_table.plot(kind='bar', stacked=True, ax=ax)
        ax.set_ylabel('Nombre')
        ax.legend(title='Catégories', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.xticks(rotation=45)

    def _create_grouped_bar_sns(self, ax, df):
        """Crée un graphique à barres groupées avec Seaborn."""
        sns.barplot(data=df, x='x_value', y='count', hue='y_value', ax=ax)
        ax.set_ylabel('Nombre')
        ax.legend(title='Catégories', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.xticks(rotation=45)

    def _create_line_chart_sns(self, ax, pivot_table):
        """Crée un graphique linéaire avec Seaborn."""
        for column in pivot_table.columns:
            sns.lineplot(data=pivot_table[column], marker='o', ax=ax)
        ax.set_ylabel('Nombre')
        ax.legend(title='Catégories', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.xticks(rotation=45)

    def _create_heatmap_sns(self, ax, pivot_table):
        """Crée une heatmap avec Seaborn."""
        sns.heatmap(pivot_table, annot=True, fmt='g', cmap='YlOrRd', ax=ax)
        plt.xticks(rotation=45)
        plt.yticks(rotation=0)

    def _create_violin_plot_sns(self, ax, df):
        """Crée un violin plot avec Seaborn."""
        sns.violinplot(data=df, x='x_value', y='count', hue='y_value', ax=ax)
        ax.set_ylabel('Distribution')
        plt.xticks(rotation=45)

    def _create_swarm_plot_sns(self, ax, df):
        """Crée un swarm plot avec Seaborn."""
        sns.swarmplot(data=df, x='x_value', y='count', hue='y_value', ax=ax)
        ax.set_ylabel('Distribution')
        plt.xticks(rotation=45)

    def _create_box_plot_sns(self, ax, df):
        """Crée une boîte à moustaches avec Seaborn."""
        sns.boxplot(data=df, x='x_value', y='count', hue='y_value', ax=ax)
        ax.set_ylabel('Distribution')
        plt.xticks(rotation=45)

    def _create_kde_plot_sns(self, ax, df):
        """Crée un KDE plot avec Seaborn."""
        for category in df['y_value'].unique():
            subset = df[df['y_value'] == category]
            sns.kdeplot(data=subset, x='count', label=category, ax=ax)
        ax.set_ylabel('Densité')
        ax.legend(title='Catégories', bbox_to_anchor=(1.05, 1), loc='upper left')

    def _create_count_plot_sns(self, ax, df):
        """Crée un count plot avec Seaborn."""
        sns.countplot(data=df, x='x_value', hue='y_value', ax=ax)
        ax.set_ylabel('Nombre')
        plt.xticks(rotation=45)

    def _create_strip_plot_sns(self, ax, df):
        """Crée un strip plot avec Seaborn."""
        sns.stripplot(data=df, x='x_value', y='count', hue='y_value', ax=ax, jitter=True)
        ax.set_ylabel('Distribution')
        plt.xticks(rotation=45)

    def _create_pie_chart_sns(self, ax, df):
        """Crée un graphique en camembert avec Seaborn."""
        try:
            # Calcul des totaux par catégorie
            totals = df.groupby('x_value')['count'].sum()

            # Configuration des couleurs
            colors = sns.color_palette("husl", n_colors=len(totals))

            # Création du camembert
            wedges, texts, autotexts = ax.pie(
                totals,
                labels=totals.index,
                colors=colors,
                autopct='%1.1f%%',  # Affichage des pourcentages
                pctdistance=0.85,
                startangle=90
            )

            # Personnalisation du style
            plt.setp(autotexts, size=8, weight="bold")
            plt.setp(texts, size=9)

            # Ajout du titre
            ax.set_title(f"Répartition par {self.config['x_axis']['theme']}")

            # Égaliser les axes pour obtenir un cercle parfait
            ax.axis('equal')

        except Exception as e:
            print(f"Erreur dans _create_pie_chart_sns: {str(e)}")

    def _create_donut_chart_sns(self, ax, df):
        """Crée un graphique en anneau (donut) avec Seaborn."""
        try:
            # Calcul des totaux par catégorie
            totals = df.groupby('x_value')['count'].sum()

            # Configuration des couleurs
            colors = sns.color_palette("husl", n_colors=len(totals))

            # Création du donut
            wedges, texts, autotexts = ax.pie(
                totals,
                labels=totals.index,
                colors=colors,
                autopct='%1.1f%%',
                pctdistance=0.75,
                startangle=90,
                wedgeprops=dict(width=0.5)  # Cette propriété crée le trou au centre
            )

            # Personnalisation du style
            plt.setp(autotexts, size=8, weight="bold")
            plt.setp(texts, size=9)

            # Ajout du titre
            ax.set_title(f"Répartition par {self.config['x_axis']['theme']}")

            # Égaliser les axes pour obtenir un cercle parfait
            ax.axis('equal')

            # Ajout du total au centre
            centre_circle = plt.Circle((0, 0), 0.50, fc='white')
            ax.add_artist(centre_circle)
            total = totals.sum()
            ax.text(0, 0, f'Total\n{total}',
                    ha='center', va='center',
                    fontsize=12, fontweight='bold')

        except Exception as e:
            print(f"Erreur dans _create_donut_chart_sns: {str(e)}")

    def update_info(self, df):
        """Met à jour les informations d'en-tête."""
        total = df['count'].sum()
        moyenne = df['count'].mean()
        maximum = df['count'].max()
        minimum = df['count'].min()

        self.info_label.setText(
            f"Total: {total} | "
            f"Moyenne: {moyenne:.2f} | "
            f"Maximum: {maximum} | "
            f"Minimum: {minimum}"
        )

    # Méthodes d'export
    def export_excel(self):
        """Exporte les données vers Excel."""
        try:
            # Nom du fichier par défaut
            default_name = f"statistiques_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Enregistrer le fichier Excel",
                default_name,
                "Excel Files (*.xlsx)"
            )

            if not file_path:  # L'utilisateur a annulé
                return

            # Création du writer Excel
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # Récupération des données du tableau
                data = []
                headers = []

                # En-têtes
                for j in range(self.table.columnCount()):
                    headers.append(self.table.horizontalHeaderItem(j).text())

                # Données
                for i in range(self.table.rowCount()):
                    row = []
                    for j in range(self.table.columnCount()):
                        item = self.table.item(i, j)
                        row.append(item.text() if item else "")
                    data.append(row)

                # Création du DataFrame
                df = pd.DataFrame(data, columns=headers)

                # Export vers Excel avec mise en forme
                df.to_excel(writer, sheet_name='Données', index=False)
                worksheet = writer.sheets['Données']

                # Ajustement des colonnes
                for idx, col in enumerate(df.columns):
                    max_length = max(
                        df[col].astype(str).apply(len).max(),
                        len(str(col))
                    ) + 2
                    # Convertir en largeur Excel
                    worksheet.column_dimensions[get_column_letter(idx + 1)].width = max_length

                # Style pour les totaux
                for row in worksheet.iter_rows():
                    for cell in row:
                        if 'TOTAL' in str(cell.value):
                            cell.font = Font(bold=True)
                            cell.fill = PatternFill(start_color="808080",
                                                    end_color="808080",
                                                    fill_type="solid")

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

            # Titre du document
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=1  # Centre
            )
            title = Paragraph("Rapport Statistique", title_style)
            elements.append(title)

            # Date et informations
            date_style = ParagraphStyle(
                'DateStyle',
                parent=styles['Normal'],
                fontSize=12,
                spaceAfter=20
            )
            date_text = Paragraph(
                f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
                date_style
            )
            elements.append(date_text)

            # Informations de configuration
            config_style = ParagraphStyle(
                'ConfigStyle',
                parent=styles['Normal'],
                fontSize=12,
                spaceAfter=20
            )
            config_text = Paragraph(
                f"Analyse: {self.config['x_axis']['theme']} par {self.config['y_axis']['theme']}",
                config_style
            )
            elements.append(config_text)
            elements.append(Spacer(1, 20))

            # Statistiques globales
            stats_text = self.info_label.text()
            stats_para = Paragraph(stats_text, styles['Normal'])
            elements.append(stats_para)
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
                # En-têtes
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#005580')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                # Corps du tableau
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                # Ligne totaux
                ('BACKGROUND', (-1, -1), (-1, -1), colors.grey),
                ('TEXTCOLOR', (-1, -1), (-1, -1), colors.whitesmoke),
                ('FONTNAME', (-1, -1), (-1, -1), 'Helvetica-Bold'),
            ])

            # Création du tableau PDF
            pdf_table = Table(table_data, repeatRows=1)
            pdf_table.setStyle(table_style)
            elements.append(pdf_table)

            # Ajout du graphique
            elements.append(Spacer(1, 30))

            # Sauvegarde temporaire du graphique
            graph_path = 'temp_graph.png'
            self.figure.savefig(graph_path, dpi=300, bbox_inches='tight')

            # Ajout de l'image au PDF
            img = Image(graph_path, width=500, height=300)
            elements.append(img)

            # Construction du document
            doc.build(elements)

            # Nettoyage du fichier temporaire
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
            slide_layout = prs.slide_layouts[0]
            slide = prs.slides.add_slide(slide_layout)
            title = slide.shapes.title
            subtitle = slide.placeholders[1]

            title.text = "Rapport Statistique"
            subtitle.text = f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}"

            # Slide d'information
            slide = prs.slides.add_slide(prs.slide_layouts[1])
            shapes = slide.shapes

            title_shape = shapes.title
            body_shape = shapes.placeholders[1]

            title_shape.text = "Informations de l'analyse"

            tf = body_shape.text_frame
            tf.text = f"Analyse: {self.config['x_axis']['theme']} par {self.config['y_axis']['theme']}"

            p = tf.add_paragraph()
            p.text = self.info_label.text()

            # Slide avec le tableau
            slide = prs.slides.add_slide(prs.slide_layouts[5])
            shapes = slide.shapes
            title = shapes.title
            title.text = "Données"

            # Création du tableau
            rows = self.table.rowCount()
            cols = self.table.columnCount()

            left = Inches(0.5)
            top = Inches(1.5)
            width = prs.slide_width - Inches(1)
            height = Inches(0.3 * rows)

            table = shapes.add_table(rows, cols, left, top, width, height).table

            # Style de l'en-tête
            for i in range(cols):
                cell = table.cell(0, i)
                cell.text = self.table.horizontalHeaderItem(i).text()

                paragraph = cell.text_frame.paragraphs[0]
                paragraph.font.bold = True
                paragraph.font.size = Pt(11)
                paragraph.alignment = PP_ALIGN.CENTER

                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(0, 85, 128)
                paragraph.font.color.rgb = RGBColor(255, 255, 255)

            # Remplissage des données
            for i in range(1, rows):
                for j in range(cols):
                    cell = table.cell(i, j)
                    item = self.table.item(i - 1, j)
                    cell.text = item.text() if item else ""

                    paragraph = cell.text_frame.paragraphs[0]
                    paragraph.font.size = Pt(10)
                    paragraph.alignment = PP_ALIGN.CENTER

                    # Style pour la ligne des totaux
                    if i == rows - 1:
                        paragraph.font.bold = True
                        cell.fill.solid()
                        cell.fill.fore_color.rgb = RGBColor(128, 128, 128)
                        paragraph.font.color.rgb = RGBColor(255, 255, 255)

            # Slide avec le graphique
            slide = prs.slides.add_slide(prs.slide_layouts[5])
            shapes = slide.shapes
            title = shapes.title
            title.text = "Visualisation"

            # Sauvegarde temporaire du graphique
            graph_path = 'temp_graph.png'
            self.figure.savefig(graph_path, dpi=300, bbox_inches='tight')

            # Ajout du graphique
            left = Inches(1)
            top = Inches(1.5)
            pic = slide.shapes.add_picture(
                graph_path,
                left,
                top,
                width=prs.slide_width - Inches(2)
            )

            # Sauvegarde de la présentation
            prs.save(file_path)

            # Nettoyage du fichier temporaire
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

# src/ui/windows/statistics/full_list_window.py

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QLabel, QComboBox, QLineEdit, QFrame,
                             QHeaderView, QMessageBox)
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
import pandas as pd

from datetime import datetime

from src.data.gendarmerie.structure import SUBDIVISIONS, SERVICE_RANGES

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

import openpyxl
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment


class FullListWindow(QMainWindow):
    """Fenêtre affichant la liste exhaustive des sanctionnés avec filtres."""

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("Liste exhaustive des sanctionnés")
        self.setMinimumSize(1200, 800)

        self.setup_ui()
        self.load_filters()
        self.load_data()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Zone de filtres
        filter_frame = QFrame()
        filter_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        filter_layout = QVBoxLayout(filter_frame)

        # Première ligne de filtres
        filter_row1 = QHBoxLayout()

        # Filtre par grade
        self.grade_combo = QComboBox()
        grade_layout = QVBoxLayout()
        grade_layout.addWidget(QLabel("Grade:"))
        grade_layout.addWidget(self.grade_combo)
        filter_row1.addLayout(grade_layout)

        # Filtre par subdivision (au lieu de région)
        self.subdiv_combo = QComboBox()
        subdiv_layout = QVBoxLayout()
        subdiv_layout.addWidget(QLabel("Subdivision:"))
        subdiv_layout.addWidget(self.subdiv_combo)
        filter_row1.addLayout(subdiv_layout)

        # Filtre par année
        self.annee_combo = QComboBox()
        annee_layout = QVBoxLayout()
        annee_layout.addWidget(QLabel("Année:"))
        annee_layout.addWidget(self.annee_combo)
        filter_row1.addLayout(annee_layout)

        filter_layout.addLayout(filter_row1)

        # Deuxième ligne de filtres
        filter_row2 = QHBoxLayout()

        # Recherche par matricule
        self.matricule_edit = QLineEdit()
        self.matricule_edit.setPlaceholderText("Rechercher par matricule...")
        matricule_layout = QVBoxLayout()
        matricule_layout.addWidget(QLabel("Matricule:"))
        matricule_layout.addWidget(self.matricule_edit)
        filter_row2.addLayout(matricule_layout)

        # Filtre par catégorie de sanction
        self.sanction_combo = QComboBox()
        sanction_layout = QVBoxLayout()
        sanction_layout.addWidget(QLabel("Catégorie de sanction:"))
        sanction_layout.addWidget(self.sanction_combo)
        filter_row2.addLayout(sanction_layout)

        # Filtre par tranches d'années de service
        self.service_combo = QComboBox()
        service_layout = QVBoxLayout()
        service_layout.addWidget(QLabel("Années de service:"))
        service_layout.addWidget(self.service_combo)
        filter_row2.addLayout(service_layout)

        filter_layout.addLayout(filter_row2)

        # Boutons d'application des filtres
        btn_layout = QHBoxLayout()
        self.apply_filter_btn = QPushButton("Appliquer les filtres")
        self.apply_filter_btn.clicked.connect(self.apply_filters)
        self.reset_filter_btn = QPushButton("Réinitialiser")
        self.reset_filter_btn.clicked.connect(self.reset_filters)

        btn_layout.addWidget(self.apply_filter_btn)
        btn_layout.addWidget(self.reset_filter_btn)
        btn_layout.addStretch()

        filter_layout.addLayout(btn_layout)
        main_layout.addWidget(filter_frame)

        # Label pour le nombre de résultats
        self.result_label = QLabel()
        main_layout.addWidget(self.result_label)

        # Tableau des données
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)

        headers = ["Matricule", "Nom et Prénoms", "Grade", "Région",
                   "Date des faits", "Faute commise", "Catégorie", "Statut", "N° Dossier"]  # Mise à jour des en-têtes
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        main_layout.addWidget(self.table)

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

    def load_filters(self):
        """Charge les valeurs des filtres."""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()

                # Grades
                cursor.execute("SELECT DISTINCT grade FROM gendarmes ORDER BY grade")
                grades = cursor.fetchall()
                self.grade_combo.addItem("Tous les grades")
                self.grade_combo.addItems([g[0] for g in grades if g[0]])

                # Subdivisions
                self.subdiv_combo.addItem("Toutes les subdivisions")
                self.subdiv_combo.addItems(SUBDIVISIONS)

                # Années
                cursor.execute("SELECT DISTINCT annee_punition FROM sanctions ORDER BY annee_punition DESC")
                annees = cursor.fetchall()
                self.annee_combo.addItem("Toutes les années")
                self.annee_combo.addItems([str(a[0]) for a in annees if a[0]])

                # Catégories de sanctions
                cursor.execute("SELECT DISTINCT categorie FROM sanctions ORDER BY categorie")
                sanctions = cursor.fetchall()
                self.sanction_combo.addItem("Toutes les catégories")
                self.sanction_combo.addItems([str(s[0]) for s in sanctions if s[0]])

                # Tranches d'années de service
                self.service_combo.addItem("Toutes les tranches")
                self.service_combo.addItems(SERVICE_RANGES)

        except Exception as e:
            QMessageBox.critical(self, "Erreur",
                                 f"Erreur lors du chargement des filtres: {str(e)}")

    def load_data(self):
        """Charge les données filtrées dans le tableau."""
        try:
            query = """
            SELECT DISTINCT
                s.matricule,
                g.nom_prenoms,
                g.grade,
                g.subdiv,
                s.date_faits,
                s.faute_commise,
                s.categorie,
                s.statut,
                s.numero_dossier,
                g.annee_service
            FROM sanctions s
            LEFT JOIN gendarmes g ON CAST(s.matricule AS TEXT) = g.mle
            WHERE 1=1
            """
            params = []

            # Application des filtres
            if self.grade_combo.currentText() != "Tous les grades":
                query += " AND g.grade = ?"
                params.append(self.grade_combo.currentText())

            if self.subdiv_combo.currentText() != "Toutes les subdivisions":
                query += " AND g.subdiv = ?"
                params.append(self.subdiv_combo.currentText())

            if self.annee_combo.currentText() != "Toutes les années":
                query += " AND s.annee_punition = ?"
                params.append(int(self.annee_combo.currentText()))

            if self.matricule_edit.text():
                query += " AND s.matricule LIKE ?"
                params.append(f"%{self.matricule_edit.text()}%")

            if self.sanction_combo.currentText() != "Toutes les catégories":
                query += " AND s.categorie = ?"
                params.append(self.sanction_combo.currentText())

            if self.service_combo.currentText() != "Toutes les tranches":
                range_text = self.service_combo.currentText()
                start, end = map(int, range_text.split("-")[0:2])
                query += " AND g.annee_service BETWEEN ? AND ?"
                params.extend([start, end])

            query += " ORDER BY s.date_faits DESC"

            # Exécution de la requête
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                results = cursor.fetchall()

            # Configuration du tableau
            headers = ["Matricule", "Nom et Prénoms", "Grade", "Subdivision",
                       "Date des faits", "Faute commise", "Catégorie", "Statut",
                       "N° Dossier", "Années de service"]

            self.table.setRowCount(len(results))
            self.table.setColumnCount(len(headers))
            self.table.setHorizontalHeaderLabels(headers)

            # Remplissage des données
            for i, row in enumerate(results):
                for j, value in enumerate(row):
                    if j == 4:  # Formatage de la date
                        try:
                            date = datetime.strptime(value, "%Y-%m-%d")
                            value = date.strftime("%d/%m/%Y")
                        except:
                            pass

                    item = QTableWidgetItem(str(value) if value else "")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(i, j, item)

            # Ajustement des colonnes
            self.table.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.ResizeToContents
            )

            # Mise à jour du label de résultats
            self.result_label.setText(f"Nombre de résultats : {len(results)}")

        except Exception as e:
            QMessageBox.critical(self, "Erreur",
                                 f"Erreur lors du chargement des données: {str(e)}")

    def apply_filters(self):
        """Applique les filtres sélectionnés."""
        self.load_data()

    def reset_filters(self):
        """Réinitialise tous les filtres."""
        self.grade_combo.setCurrentIndex(0)
        self.subdiv_combo.setCurrentIndex(0)
        self.annee_combo.setCurrentIndex(0)
        self.sanction_combo.setCurrentIndex(0)
        self.service_combo.setCurrentIndex(0)
        self.matricule_edit.clear()
        self.load_data()

    def export_excel(self):
        """Exporte les données vers Excel avec mise en forme."""
        try:
            # Demander à l'utilisateur où sauvegarder le fichier
            default_name = f"liste_sanctions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Enregistrer le fichier Excel",
                default_name,
                "Excel Files (*.xlsx)"
            )

            if not file_path:  # L'utilisateur a annulé
                return

            # Création d'un writer Excel
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # Récupération des données du tableau
                data = []
                headers = []

                # Récupération des en-têtes
                for j in range(self.table.columnCount()):
                    headers.append(self.table.horizontalHeaderItem(j).text())

                # Récupération des données
                for i in range(self.table.rowCount()):
                    row = []
                    for j in range(self.table.columnCount()):
                        item = self.table.item(i, j)
                        row.append(item.text() if item else "")
                    data.append(row)

                # Création du DataFrame
                df = pd.DataFrame(data, columns=headers)

                # Export vers Excel avec mise en forme
                df.to_excel(writer, sheet_name='Liste des sanctions', index=False)
                worksheet = writer.sheets['Liste des sanctions']

                # Ajustement des colonnes
                for idx, col in enumerate(df.columns):
                    max_length = max(
                        df[col].astype(str).apply(len).max(),
                        len(str(col))
                    ) + 2
                    worksheet.column_dimensions[openpyxl.utils.get_column_letter(idx + 1)].width = max_length

                # Style pour l'en-tête
                for cell in worksheet[1]:
                    cell.font = openpyxl.styles.Font(bold=True)
                    cell.fill = openpyxl.styles.PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")

                # Bordures et alignement
                thin_border = openpyxl.styles.borders.Border(
                    left=openpyxl.styles.borders.Side(style='thin'),
                    right=openpyxl.styles.borders.Side(style='thin'),
                    top=openpyxl.styles.borders.Side(style='thin'),
                    bottom=openpyxl.styles.borders.Side(style='thin')
                )

                for row in worksheet.iter_rows(min_row=1, max_row=len(data) + 1):
                    for cell in row:
                        cell.border = thin_border
                        cell.alignment = openpyxl.styles.Alignment(horizontal='center', vertical='center')

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
            default_name = f"liste_sanctions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
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
            title = Paragraph("Liste des Sanctions", title_style)
            elements.append(title)

            # Informations sur les filtres appliqués
            filter_info = []
            if self.grade_combo.currentText() != "Tous les grades":
                filter_info.append(f"Grade: {self.grade_combo.currentText()}")
            if self.subdiv_combo.currentText() != "Toutes les subdivisions":
                filter_info.append(f"Subdivision: {self.subdiv_combo.currentText()}")
            if self.annee_combo.currentText() != "Toutes les années":
                filter_info.append(f"Année: {self.annee_combo.currentText()}")
            if self.sanction_combo.currentText() != "Toutes les catégories":
                filter_info.append(f"Catégorie: {self.sanction_combo.currentText()}")
            if self.service_combo.currentText() != "Toutes les tranches":
                filter_info.append(f"Années de service: {self.service_combo.currentText()}")

            if filter_info:
                filter_text = "Filtres appliqués: " + ", ".join(filter_info)
                elements.append(Paragraph(filter_text, styles['Normal']))
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
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWHEIGHT', (0, 0), (-1, -1), 20)
            ])

            pdf_table = Table(table_data, repeatRows=1)
            pdf_table.setStyle(table_style)
            elements.append(pdf_table)

            # Informations de pagination
            def add_page_number(canvas, doc):
                page_num = canvas.getPageNumber()
                text = f"Page {page_num}"
                canvas.saveState()
                canvas.setFont('Helvetica', 8)
                canvas.drawRightString(doc.pagesize[0] - 30, 30, text)
                canvas.restoreState()

            # Construction du document
            doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)

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
            default_name = f"liste_sanctions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pptx"
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
            prs.slide_width = Inches(13.333)
            prs.slide_height = Inches(7.5)

            # Slide de titre
            slide_layout = prs.slide_layouts[0]
            slide = prs.slides.add_slide(slide_layout)
            title = slide.shapes.title
            subtitle = slide.placeholders[1]

            title.text = "Liste des Sanctions"
            subtitle.text = f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}"

            # Slide d'information sur les filtres
            bullet_layout = prs.slide_layouts[1]
            slide = prs.slides.add_slide(bullet_layout)
            shapes = slide.shapes

            title_shape = shapes.title
            body_shape = shapes.placeholders[1]
            title_shape.text = "Filtres appliqués"

            tf = body_shape.text_frame

            if self.grade_combo.currentText() != "Tous les grades":
                p = tf.add_paragraph()
                p.text = f"Grade: {self.grade_combo.currentText()}"
            if self.subdiv_combo.currentText() != "Toutes les subdivisions":
                p = tf.add_paragraph()
                p.text = f"Subdivision: {self.subdiv_combo.currentText()}"
            if self.annee_combo.currentText() != "Toutes les années":
                p = tf.add_paragraph()
                p.text = f"Année: {self.annee_combo.currentText()}"
            if self.sanction_combo.currentText() != "Toutes les catégories":
                p = tf.add_paragraph()
                p.text = f"Catégorie: {self.sanction_combo.currentText()}"
            if self.service_combo.currentText() != "Toutes les tranches":
                p = tf.add_paragraph()
                p.text = f"Années de service: {self.service_combo.currentText()}"

            # Slides de données
            rows_per_slide = 10
            total_rows = self.table.rowCount()
            num_slides = (total_rows + rows_per_slide - 1) // rows_per_slide

            headers = [self.table.horizontalHeaderItem(j).text()
                       for j in range(self.table.columnCount())]

            for slide_num in range(num_slides):
                slide = prs.slides.add_slide(prs.slide_layouts[5])
                shapes = slide.shapes

                title = shapes.title
                title.text = f"Liste des Sanctions ({slide_num + 1}/{num_slides})"

                # Indices de début et fin pour ce slide
                start_idx = slide_num * rows_per_slide
                end_idx = min((slide_num + 1) * rows_per_slide, total_rows)

                # Création du tableau
                rows = end_idx - start_idx + 1
                cols = self.table.columnCount()

                left = Inches(0.5)
                top = Inches(1.5)
                width = prs.slide_width - Inches(1)
                height = Inches(0.3 * rows)

                table = shapes.add_table(rows, cols, left, top, width, height).table

                # Style de l'en-tête
                for i, header in enumerate(headers):
                    cell = table.cell(0, i)
                    cell.text = header
                    cell.fill.solid()
                    cell.fill.fore_color.rgb = RGBColor(128, 128, 128)

                    paragraph = cell.text_frame.paragraphs[0]
                    paragraph.font.size = Pt(10)
                    paragraph.font.bold = True
                    paragraph.font.color.rgb = RGBColor(255, 255, 255)

                # Données
                for i in range(start_idx, end_idx):
                    for j in range(cols):
                        cell = table.cell(i - start_idx + 1, j)
                        item = self.table.item(i, j)
                        cell.text = item.text() if item else ""

                        paragraph = cell.text_frame.paragraphs[0]
                        paragraph.font.size = Pt(9)
                        paragraph.alignment = PP_ALIGN.CENTER

            # Sauvegarde de la présentation
            prs.save(file_path)

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



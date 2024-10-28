from datetime import datetime

import pandas as pd
from PyQt6.QtGui import QFont, QAction, QTextDocument
from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTableWidget,
                             QTableWidgetItem, QHeaderView, QLabel, QHBoxLayout,
                             QLineEdit, QPushButton, QComboBox, QGroupBox, QGridLayout, QMenu, QToolBar, QMessageBox,
                             QFileDialog)
from PyQt6.QtCore import Qt

from src.ui.styles import styles
from src.ui.styles.styles import Styles


class PunisListWindow(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        self.search_input = None
        self.db_manager = db_manager
        self.setWindowTitle("Liste Complète des Punis")
        self.setMinimumSize(1400, 800)
        self.init_ui()
        self.load_data()

    def init_ui(self):

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Zone de recherche améliorée
        search_group = QGroupBox("Recherche et Filtres")
        search_group.setFont(QFont('Helvetica', 14, QFont.Weight.Bold))
        search_layout = QGridLayout()

        # Recherche par nom ou matricule
        self.search_type = QComboBox()
        self.search_type.addItems(["Nom", "Matricule"])
        search_layout.addWidget(self.search_type, 0, 0)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher...")
        self.search_input.textChanged.connect(self.filter_data)
        search_layout.addWidget(self.search_input, 0, 1, 1, 2)

        # Filtres
        filter_layout = QHBoxLayout()

        # Filtre par type de faute
        self.faute_filter = QComboBox()
        self.faute_filter.addItem("Toutes les fautes")
        self.load_fautes_types()  # On va créer cette méthode
        self.faute_filter.currentTextChanged.connect(self.filter_data)
        filter_layout.addWidget(QLabel("Type de faute:"))
        filter_layout.addWidget(self.faute_filter)

        # Filtre par année
        self.annee_filter = QComboBox()
        self.annee_filter.addItem("Toutes les années")
        self.load_annees()  # On va créer cette méthode
        self.annee_filter.currentTextChanged.connect(self.filter_data)
        filter_layout.addWidget(QLabel("Année:"))
        filter_layout.addWidget(self.annee_filter)

        # Filtre par grade
        self.grade_filter = QComboBox()
        self.grade_filter.addItem("Tous les grades")
        self.load_grades()  # On va créer cette méthode
        self.grade_filter.currentTextChanged.connect(self.filter_data)
        filter_layout.addWidget(QLabel("Grade:"))
        filter_layout.addWidget(self.grade_filter)

        # Bouton de réinitialisation
        reset_button = QPushButton("Réinitialiser les filtres")
        reset_button.clicked.connect(self.reset_filters)
        filter_layout.addWidget(reset_button)

        search_layout.addLayout(filter_layout, 1, 0, 1, 3)
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)

        # Toolbar pour les actions
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Bouton Export
        export_menu = QMenu()

        export_excel_action = QAction("Exporter en Excel", self)
        export_excel_action.triggered.connect(self.export_to_excel)
        export_menu.addAction(export_excel_action)

        export_pdf_action = QAction("Exporter en PDF", self)
        export_pdf_action.triggered.connect(self.export_to_pdf)
        export_menu.addAction(export_pdf_action)

        export_button = QPushButton("Exporter")
        export_button.setMenu(export_menu)
        toolbar.addWidget(export_button)

        # Table des punis
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        headers = ["Matricule", "Nom et Prénoms", "Grade", "Unité",
                   "Légion", "Date des faits", "Type Sanction", "Durée (JAR)", "Motif"]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        # Compteur en bas
        self.counter_label = QLabel()
        layout.addWidget(self.counter_label)

        # Appliquer le style
        self.apply_theme()

    def load_data(self):
        """Charge toutes les sanctions avec les infos des gendarmes"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT g.mle, g.nom_prenoms, g.grade, g.unite, g.legions,
                           s.date_faits, s.statut, s.taux_jar, s.faute_commise
                    FROM gendarmes g
                    JOIN sanctions s ON g.id = s.gendarme_id
                    ORDER BY s.date_faits DESC
                """)
                self.all_data = cursor.fetchall()
                self.display_data(self.all_data)

        except Exception as e:
            print(f"Erreur lors du chargement des données : {str(e)}")

    def display_data(self, data):
        """Affiche les données dans la table"""
        self.table.setRowCount(len(data))
        for i, row in enumerate(data):
            for j, value in enumerate(row):
                # Créer un nouvel item à chaque fois
                item = QTableWidgetItem()
                item.setData(Qt.ItemDataRole.DisplayRole, str(value if value is not None else ""))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                # Tooltip détaillé pour la faute commise (colonne 8)
                if j == 8:  # Index de la colonne faute_commise
                    tooltip = f"""
                                Détails de la sanction:
                                Date: {row[5]}
                                Type: {row[6]}
                                Durée: {row[7]} jours
                                Motif complet: {value}
                                """
                    item.setToolTip(tooltip)

                self.table.setItem(i, j, item)

        # Mise à jour du compteur
        self.counter_label.setText(f"Total : {len(data)} dossiers disciplinaires")

    def load_fautes_types(self):
        """Charge les types de fautes uniques"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT statut FROM sanctions ORDER BY statut")
                fautes = [row[0] for row in cursor.fetchall()]
                self.faute_filter.addItems(fautes)
        except Exception as e:
            print(f"Erreur lors du chargement des types de fautes : {str(e)}")

    def load_annees(self):
        """Charge les années uniques"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT annee_faits FROM sanctions ORDER BY annee_faits DESC")
                annees = [str(row[0]) for row in cursor.fetchall() if row[0]]
                self.annee_filter.addItems(annees)
        except Exception as e:
            print(f"Erreur lors du chargement des années : {str(e)}")

    def load_grades(self):
        """Charge les grades uniques"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT grade FROM gendarmes ORDER BY grade")
                grades = [row[0] for row in cursor.fetchall()]
                self.grade_filter.addItems(grades)
        except Exception as e:
            print(f"Erreur lors du chargement des grades : {str(e)}")

    def filter_data(self):
        """Filtre les données selon tous les critères"""
        search_text = self.search_input.text().lower()
        search_type = self.search_type.currentText()
        faute = self.faute_filter.currentText()
        annee = self.annee_filter.currentText()
        grade = self.grade_filter.currentText()

        filtered_data = self.all_data

        # Filtre par recherche (nom ou matricule)
        if search_text:
            if search_type == "Nom":
                filtered_data = [row for row in filtered_data
                                 if search_text in str(row[1]).lower()]
            else:  # Matricule
                filtered_data = [row for row in filtered_data
                                 if search_text in str(row[0]).lower()]

        # Filtre par type de faute
        if faute != "Toutes les fautes":
            filtered_data = [row for row in filtered_data
                             if row[6] == faute]

        # Filtre par année
        if annee != "Toutes les années":
            filtered_data = [row for row in filtered_data
                             if str(row[5]).startswith(annee)]

        # Filtre par grade
        if grade != "Tous les grades":
            filtered_data = [row for row in filtered_data
                             if row[2] == grade]

        self.display_data(filtered_data)

    def reset_filters(self):
        """Réinitialise tous les filtres"""
        self.search_input.clear()
        self.search_type.setCurrentIndex(0)
        self.faute_filter.setCurrentIndex(0)
        self.annee_filter.setCurrentIndex(0)
        self.grade_filter.setCurrentIndex(0)
        self.display_data(self.all_data)

    def export_to_pdf(self):
        """Exporte les données filtrées en PDF"""
        try:
            file_name, _ = QFileDialog.getSaveFileName(
                self, "Exporter en PDF", "", "PDF files (*.pdf)"
            )

            if file_name:
                if not file_name.endswith('.pdf'):
                    file_name += '.pdf'

                printer = QPrinter(QPrinter.PrinterMode.HighResolution)
                printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
                printer.setOutputFileName(file_name)

                doc = QTextDocument()
                html = """
                <h2 style='text-align: center;'>Liste des Sanctions</h2>
                <p style='text-align: center;'><small>Exporté le {}</small></p>
                <table border='1' cellspacing='0' cellpadding='4' width='100%'>
                <tr style='background-color: #f0f0f0;'>
                """.format(datetime.now().strftime("%d/%m/%Y à %H:%M"))

                # Headers
                for col in range(self.table.columnCount()):
                    html += f"<th>{self.table.horizontalHeaderItem(col).text()}</th>"
                html += "</tr>"

                # Data
                for row in range(self.table.rowCount()):
                    html += "<tr>"
                    for col in range(self.table.columnCount()):
                        item = self.table.item(row, col)
                        html += f"<td>{item.text() if item else ''}</td>"
                    html += "</tr>"

                html += "</table>"
                doc.setHtml(html)
                doc.print(printer)

                QMessageBox.information(self, "Succès", "Export PDF réussi!")

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'export : {str(e)}")

    def export_to_excel(self):
        """Exporte les données filtrées en Excel"""
        try:
            file_name, _ = QFileDialog.getSaveFileName(
                self, "Exporter en Excel", "", "Excel files (*.xlsx)"
            )

            if file_name:
                if not file_name.endswith('.xlsx'):
                    file_name += '.xlsx'

                # Création du DataFrame
                headers = ["Matricule", "Nom et Prénoms", "Grade", "Unité",
                           "Légion", "Date Sanction", "Type Sanction",
                           "Durée (JAR)", "Motif"]

                data = []
                for row in range(self.table.rowCount()):
                    row_data = []
                    for col in range(self.table.columnCount()):
                        item = self.table.item(row, col)
                        row_data.append(item.text() if item else "")
                    data.append(row_data)

                df = pd.DataFrame(data, columns=headers)
                df.to_excel(file_name, index=False)

                QMessageBox.information(self, "Succès", "Export Excel réussi!")

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'export : {str(e)}")

    def apply_theme(self):
        """Applique le thème actuel"""
        styles = Styles.get_styles(True)  # Pour l'instant en mode clair
        self.setStyleSheet(styles['MAIN_WINDOW'])
        self.search_input.setStyleSheet(styles['INPUT'])
        self.table.setStyleSheet(styles['TABLE'])

# src/ui/windows/statistics/full_list_window.py

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QLabel, QComboBox, QLineEdit, QFrame,
                             QHeaderView, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
import pandas as pd
from datetime import datetime


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

        # Filtre par région
        self.region_combo = QComboBox()
        region_layout = QVBoxLayout()
        region_layout.addWidget(QLabel("Région:"))
        region_layout.addWidget(self.region_combo)
        filter_row1.addLayout(region_layout)

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

        # Filtre par type de sanction
        self.sanction_combo = QComboBox()
        sanction_layout = QVBoxLayout()
        sanction_layout.addWidget(QLabel("Type de sanction:"))
        sanction_layout.addWidget(self.sanction_combo)
        filter_row2.addLayout(sanction_layout)

        filter_layout.addLayout(filter_row2)

        # Bouton d'application des filtres
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

        # Information sur le nombre de résultats
        self.result_label = QLabel()
        main_layout.addWidget(self.result_label)

        # Tableau des données
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        main_layout.addWidget(self.table)

        # Boutons d'export
        export_layout = QHBoxLayout()

        self.btn_excel = QPushButton("Exporter Excel")
        self.btn_excel.clicked.connect(self.export_excel)
        self.btn_excel.setIcon(QIcon("../resources/icons/excel.png"))

        self.btn_pdf = QPushButton("Exporter PDF")
        self.btn_pdf.clicked.connect(self.export_pdf)
        self.btn_pdf.setIcon(QIcon("../resources/icons/pdf.png"))

        self.btn_pptx = QPushButton("Exporter PowerPoint")
        self.btn_pptx.clicked.connect(self.export_pptx)
        self.btn_pptx.setIcon(QIcon("../resources/icons/powerpoint.png"))

        export_layout.addWidget(self.btn_excel)
        export_layout.addWidget(self.btn_pdf)
        export_layout.addWidget(self.btn_pptx)
        export_layout.addStretch()

        main_layout.addLayout(export_layout)

    def load_filters(self):
        """Charge les valeurs des filtres depuis la base de données."""
        try:
            # Chargement des grades
            query = "SELECT DISTINCT grade FROM gendarmes ORDER BY grade"
            grades = self.db_manager.execute_query(query).fetchall()
            self.grade_combo.addItem("Tous les grades")
            self.grade_combo.addItems([g[0] for g in grades if g[0]])

            # Chargement des régions
            query = "SELECT DISTINCT regions FROM gendarmes ORDER BY regions"
            regions = self.db_manager.execute_query(query).fetchall()
            self.region_combo.addItem("Toutes les régions")
            self.region_combo.addItems([r[0] for r in regions if r[0]])

            # Chargement des années
            query = "SELECT DISTINCT annee_punition FROM sanctions ORDER BY annee_punition DESC"
            annees = self.db_manager.execute_query(query).fetchall()
            self.annee_combo.addItem("Toutes les années")
            self.annee_combo.addItems([str(a[0]) for a in annees if a[0]])

            # Chargement des types de sanctions
            query = "SELECT DISTINCT categorie FROM sanctions ORDER BY categorie"
            sanctions = self.db_manager.execute_query(query).fetchall()
            self.sanction_combo.addItem("Toutes les sanctions")
            self.sanction_combo.addItems([str(s[0]) for s in sanctions if s[0]])

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement des filtres: {str(e)}")

    def apply_filters(self):
        """Applique les filtres sélectionnés."""
        self.load_data()

    def reset_filters(self):
        """Réinitialise tous les filtres."""
        self.grade_combo.setCurrentIndex(0)
        self.region_combo.setCurrentIndex(0)
        self.annee_combo.setCurrentIndex(0)
        self.sanction_combo.setCurrentIndex(0)
        self.matricule_edit.clear()
        self.load_data()

    def load_data(self):
        """Charge les données filtrées dans le tableau."""
        try:
            # Construction de la requête avec filtres
            query = """
            SELECT 
                s.matricule,
                g.nom_prenoms,
                g.grade,
                g.regions,
                s.date_faits,
                s.faute_commise,
                s.categorie,
                s.statut
            FROM sanctions s
            LEFT JOIN gendarmes g ON CAST(s.matricule AS TEXT) = g.mle
            WHERE 1=1
            """
            params = []

            # Ajout des conditions selon les filtres
            if self.grade_combo.currentText() != "Tous les grades":
                query += " AND g.grade = ?"
                params.append(self.grade_combo.currentText())

            if self.region_combo.currentText() != "Toutes les régions":
                query += " AND g.regions = ?"
                params.append(self.region_combo.currentText())

            if self.annee_combo.currentText() != "Toutes les années":
                query += " AND s.annee_punition = ?"
                params.append(int(self.annee_combo.currentText()))

            if self.matricule_edit.text():
                query += " AND s.matricule LIKE ?"
                params.append(f"%{self.matricule_edit.text()}%")

            if self.sanction_combo.currentText() != "Toutes les sanctions":
                query += " AND s.categorie = ?"
                params.append(self.sanction_combo.currentText())

            # Ajout de l'ordre
            query += " ORDER BY s.date_faits DESC"

            # Exécution de la requête
            results = self.db_manager.execute_query(query, params).fetchall()

            # Mise à jour du tableau
            headers = ["Matricule", "Nom et Prénoms", "Grade", "Région",
                       "Date des faits", "Faute commise", "Catégorie", "Statut"]

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

    def export_excel(self):
        """Exporte les données vers Excel."""
        try:
            # Création d'un DataFrame à partir des données du tableau
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

            df = pd.DataFrame(data, columns=headers)

            # Export vers Excel
            filename = f"liste_sanctionnes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            df.to_excel(filename, index=False)

            QMessageBox.information(self, "Succès",
                                    f"Les données ont été exportées vers {filename}")

        except Exception as e:
            QMessageBox.critical(self, "Erreur",
                                 f"Erreur lors de l'export Excel: {str(e)}")

    def export_pdf(self):
        """Exporte les données vers PDF."""
        # TODO: Implémenter l'export PDF
        QMessageBox.information(self, "Information",
                                "L'export PDF sera disponible prochainement")

    def export_pptx(self):
        """Exporte les données vers PowerPoint."""
        # TODO: Implémenter l'export PowerPoint
        QMessageBox.information(self, "Information",
                                "L'export PowerPoint sera disponible prochainement")

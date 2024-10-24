from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLineEdit, QPushButton, QLabel,
                             QTableWidget, QTableWidgetItem, QTabWidget,
                             QComboBox, QGroupBox, QGridLayout, QMessageBox,
                             QHeaderView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from src.database.db_manager import DatabaseManager
from src.ui.styles.styles import Styles
from src.database.models import GendarmeRepository, SanctionRepository


class MainGendarmeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestion des Gendarmes")
        self.setMinimumSize(1200, 800)
        self.db_manager = DatabaseManager()
        self.gendarme_repository = GendarmeRepository(self.db_manager)
        self.sanction_repository = SanctionRepository(self.db_manager)

        # Widget principal
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Zone de recherche
        search_group = QGroupBox("Recherche")
        search_layout = QHBoxLayout()

        self.search_type = QComboBox()
        self.search_type.addItems(["Matricule (MLE)", "Nom"])
        self.search_type.setStyleSheet(Styles.COMBO_BOX)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Entrez votre recherche...")
        self.search_input.setStyleSheet(Styles.SEARCH_INPUT)

        search_button = QPushButton("Rechercher")
        search_button.setStyleSheet(Styles.SEARCH_BUTTON)
        search_button.clicked.connect(self.search_gendarme)

        search_layout.addWidget(self.search_type)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        search_layout.addStretch()
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)

        # Informations du gendarme
        info_group = QGroupBox("Informations du gendarme")
        info_layout = QGridLayout()

        # Création des labels pour les informations
        self.info_labels = {}
        info_fields = [
            ('numero_radiation', 'N° de radiation'),
            ('mle', 'Matricule'),
            ('nom_prenoms', 'Nom et Prénoms'),
            ('grade', 'Grade'),
            ('sexe', 'Sexe'),
            ('date_naissance', 'Date de naissance'),
            ('age', 'Age'),
            ('unite', 'Unité'),
            ('leg', 'LEG'),
            ('sub', 'SUB'),
            ('rg', 'RG'),
            ('legions', 'Légion'),
            ('subdiv', 'Subdivision'),
            ('regions', 'Région'),
            ('date_entree_gie', 'Date d\'entrée GIE'),
            ('annee_service', 'Années de service'),
            ('situation_matrimoniale', 'Situation matrimoniale'),
            ('nb_enfants', 'Nombre d\'enfants')
        ]

        for i, (field_id, field_name) in enumerate(info_fields):
            label = QLabel(f"{field_name}:")
            label.setFont(QFont('Arial', 10, QFont.Weight.Bold))
            value_label = QLabel()
            value_label.setStyleSheet("""
                padding: 5px;
                background: #f8f9fa;
                border-radius: 3px;
                min-width: 200px;
            """)
            self.info_labels[field_id] = value_label
            row = i // 3
            col = (i % 3) * 2
            info_layout.addWidget(label, row, col)
            info_layout.addWidget(value_label, row, col + 1)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Tableau des sanctions
        sanctions_group = QGroupBox("Sanctions")
        sanctions_layout = QVBoxLayout()

        self.sanctions_table = QTableWidget()
        self.sanctions_table.setColumnCount(8)
        headers = ["Date", "Type de faute", "Sanction", "Référence",
                   "Taux (JAR)", "Comité", "Année", "N° Dossier"]
        self.sanctions_table.setHorizontalHeaderLabels(headers)
        self.sanctions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.sanctions_table.setStyleSheet(Styles.TABLE)

        sanctions_layout.addWidget(self.sanctions_table)
        sanctions_group.setLayout(sanctions_layout)
        layout.addWidget(sanctions_group)

        # Barre de statut
        self.statusBar().showMessage("Prêt")

    def search_gendarme(self):
        """Recherche un gendarme selon le critère sélectionné"""
        search_text = self.search_input.text().strip()
        if not search_text:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer un critère de recherche")
            return

        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()

                # Construction de la requête selon le type de recherche
                if self.search_type.currentText() == "Matricule (MLE)":
                    where_clause = "WHERE mle = ?"
                else:  # Recherche par nom
                    where_clause = "WHERE nom_prenoms LIKE ?"
                    search_text = f"%{search_text}%"

                # Recherche du gendarme
                cursor.execute(f"""
                    SELECT * FROM gendarmes {where_clause}
                """, (search_text,))

                gendarme = cursor.fetchone()

                if gendarme:
                    # Mise à jour des informations
                    field_names = [description[0] for description in cursor.description]
                    for field_name, value in zip(field_names[1:], gendarme[1:]):  # Skip id
                        if field_name in self.info_labels:
                            self.info_labels[field_name].setText(str(value if value is not None else ""))

                    # Ajout d'un print pour déboguer
                    print(f"ID du gendarme trouvé : {gendarme[0]}")

                    # Recherche des sanctions avec une requête modifiée
                    cursor.execute("""
                        SELECT date_faits, faute_commise, statut, reference_statut,
                               taux_jar, comite, annee_faits, numero
                        FROM sanctions
                        WHERE gendarme_id = ?
                        ORDER BY date_faits DESC
                    """, (gendarme[0],))

                    sanctions = cursor.fetchall()
                    print(f"Nombre de sanctions trouvées : {len(sanctions)}")  # Débogage

                    self.sanctions_table.setRowCount(len(sanctions))

                    for i, sanction in enumerate(sanctions):
                        for j, value in enumerate(sanction):
                            item = QTableWidgetItem(str(value if value is not None else ""))
                            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                            self.sanctions_table.setItem(i, j, item)
                            print(f"Sanction {i}, colonne {j}: {value}")  # Débogage

                    self.statusBar().showMessage(f"Gendarme trouvé : {gendarme[3]}")
                else:
                    # Effacer les informations précédentes
                    for label in self.info_labels.values():
                        label.clear()
                    self.sanctions_table.setRowCount(0)
                    self.statusBar().showMessage("Aucun gendarme trouvé")
                    QMessageBox.information(self, "Résultat", "Aucun gendarme trouvé")

        except Exception as e:
            print(f"Erreur détaillée lors de la recherche : {str(e)}")  # Débogage
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la recherche : {str(e)}")

    # def search_gendarme(self):
    #     """Recherche un gendarme selon le critère sélectionné"""
    #     search_text = self.search_input.text().strip()
    #     if not search_text:
    #         QMessageBox.warning(self, "Erreur", "Veuillez entrer un critère de recherche")
    #         return
    #
    #     try:
    #         # Utilisation des repositories pour la recherche
    #         if self.search_type.currentText() == "Matricule (MLE)":
    #             gendarme = self.gendarme_repository.get_by_mle(search_text)
    #             gendarmes = [gendarme] if gendarme else []
    #         else:
    #             gendarmes = self.gendarme_repository.get_by_name(search_text)
    #
    #         if gendarmes:
    #             gendarme = gendarmes[0]  # On prend le premier si plusieurs résultats
    #             # Mise à jour des informations
    #             for field_name, label in self.info_labels.items():
    #                 value = getattr(gendarme, field_name, "")
    #                 label.setText(str(value if value is not None else ""))
    #
    #             # Recherche des sanctions
    #             sanctions = self.sanction_repository.get_by_gendarme(gendarme.id)
    #             self.sanctions_table.setRowCount(len(sanctions))
    #
    #             for i, sanction in enumerate(sanctions):
    #                 self.sanctions_table.setItem(i, 0, QTableWidgetItem(str(sanction.date_faits)))
    #                 self.sanctions_table.setItem(i, 1, QTableWidgetItem(sanction.faute_commise))
    #                 self.sanctions_table.setItem(i, 2, QTableWidgetItem(sanction.statut))
    #                 self.sanctions_table.setItem(i, 3, QTableWidgetItem(sanction.reference_statut))
    #                 self.sanctions_table.setItem(i, 4, QTableWidgetItem(str(sanction.taux_jar)))
    #                 self.sanctions_table.setItem(i, 5, QTableWidgetItem(sanction.comite))
    #                 self.sanctions_table.setItem(i, 6, QTableWidgetItem(str(sanction.annee_faits)))
    #                 self.sanctions_table.setItem(i, 7, QTableWidgetItem(sanction.numero))
    #
    #                 # Rendre les cellules non éditables
    #                 for j in range(8):
    #                     item = self.sanctions_table.item(i, j)
    #                     if item:
    #                         item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
    #
    #             self.statusBar().showMessage(f"Gendarme trouvé : {gendarme.nom_prenoms}")
    #         else:
    #             # Effacer les informations précédentes
    #             for label in self.info_labels.values():
    #                 label.clear()
    #             self.sanctions_table.setRowCount(0)
    #             self.statusBar().showMessage("Aucun gendarme trouvé")
    #             QMessageBox.information(self, "Résultat", "Aucun gendarme trouvé")
    #
    #     except Exception as e:
    #         QMessageBox.critical(self, "Erreur", f"Erreur lors de la recherche : {str(e)}")
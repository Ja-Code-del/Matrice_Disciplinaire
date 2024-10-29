import pandas as pd
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLineEdit, QPushButton, QLabel,
                             QTableWidget, QTableWidgetItem, QTabWidget,
                             QComboBox, QGroupBox, QGridLayout, QMessageBox,
                             QHeaderView, QToolBar, QFileDialog)

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
from src.database.db_manager import DatabaseManager
from src.ui.styles.styles import Styles
from src.database.models import GendarmeRepository, SanctionRepository
from src.ui.windows.import_etat_window import ImportEtatCompletWindow


class MainGendarmeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.sanctions_table = None
        self.search_input = None
        self.toolbar = None
        self.theme_button = None
        self.info_labels = None
        self.is_dark_mode = False
        self.db_manager = DatabaseManager()
        self.gendarme_repository = GendarmeRepository(self.db_manager)
        self.sanction_repository = SanctionRepository(self.db_manager)

        # Définir info_fields comme attribut de classe
        self.info_fields = [
            ('numero_radiation', 'N° de radiation'),
            ('mle', 'Matricule'),
            ('nom_prenoms', 'Nom et Prénoms'),
            ('grade', 'Grade'),
            ('sexe', 'Sexe'),
            ('date_naissance', 'Date de naissance'),
            ('age', 'Age'),
            ('unite', 'Unité'),
            # ('leg', 'LEG'),
            # ('sub', 'SUB'),
            # ('rg', 'RG'),
            ('legions', 'Légion'),
            ('subdiv', 'Subdivision'),
            ('regions', 'Région'),
            ('date_entree_gie', 'Date d\'entrée GIE'),
            ('annee_service', 'Années de service'),
            ('situation_matrimoniale', 'Situation matrimoniale'),
            ('nb_enfants', 'Nombre d\'enfants')
        ]

        self.init_ui()

    def init_ui(self):
        """Initialise l'interface utilisateur"""
        self.setWindowTitle("Gestion des Gendarmes")
        self.setMinimumSize(1200, 800)

        # Widget principal
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Zone de recherche
        search_group = QGroupBox("Recherche")
        search_layout = QHBoxLayout()

        self.search_type = QComboBox()
        self.search_type.addItems(["Matricule (MLE)", "Nom"])

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Entrez votre recherche...")

        search_button = QPushButton("Rechercher")
        search_button.clicked.connect(self.search_gendarme)
        search_group.setFont(QFont('Helvetica', 18, QFont.Weight.Bold))

        search_layout.addWidget(self.search_type)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        search_layout.addStretch()
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)

        # Ajout de la barre d'outils avec les boutons d'import et de thème
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Bouton Import État Complet
        import_etat_button = QPushButton("📋 Importer Matrice Gendarmes")
        import_etat_button.clicked.connect(self.import_etat_complet)
        toolbar.addWidget(import_etat_button)

        # Bouton Nouveau Dossier
        new_case_button = QPushButton("📝 Nouveau Dossier")
        new_case_button.clicked.connect(self.show_new_case_form)
        toolbar.addWidget(new_case_button)

        # Bouton d'import
        import_button = QPushButton("Importer Matrice Disciplinaire")
        import_button.clicked.connect(self.show_import_window)
        toolbar.addWidget(import_button)

        # Bouton de stats
        stats_button = QPushButton("📊 Statistiques")
        stats_button.clicked.connect(self.show_stats_window)
        toolbar.addWidget(stats_button)

        # Bouton de thème
        self.theme_button = QPushButton()
        self.theme_button.setIcon(QIcon("../resources/icons/light_mode.png"))
        self.theme_button.setToolTip("Changer le thème")
        self.theme_button.clicked.connect(self.toggle_theme)
        toolbar.addWidget(self.theme_button)

        # Informations du gendarme
        info_group = QGroupBox("Informations du gendarme")
        info_layout = QGridLayout()
        info_group.setFont(QFont('Helvetica', 18, QFont.Weight.Bold))

        # Création des labels pour les informations
        self.info_labels = {}

        for i, (field_id, field_name) in enumerate(self.info_fields):
            label = QLabel(f"{field_name}:")
            label.setFont(QFont('Helvetica', 11, QFont.Weight.Bold))
            value_label = QLabel()
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
        sanctions_group.setFont(QFont('Helvetica', 18, QFont.Weight.Bold))

        self.sanctions_table = QTableWidget()
        self.sanctions_table.setColumnCount(8)
        headers = ["Date des faits", "Type de faute", "Sanction", "Référence",
                   "Taux (JAR)", "Comité", "Année", "N° Dossier"]
        self.sanctions_table.setHorizontalHeaderLabels(headers)
        self.sanctions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        sanctions_layout.addWidget(self.sanctions_table)
        sanctions_group.setLayout(sanctions_layout)
        layout.addWidget(sanctions_group)

        # Barre de statut
        self.statusBar().showMessage("Prêt")

        # Appliquer le thème
        self.apply_theme()

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
                            # Formatage spécial pour les dates
                            if field_name in ['date_naissance', 'date_entree_gie'] and value:
                                try:
                                    # Convertit la date en format DD/MM/YYYY
                                    date_obj = pd.to_datetime(value)
                                    formatted_value = date_obj.strftime('%d/%m/%Y')
                                    self.info_labels[field_name].setText(formatted_value)
                                except:
                                    self.info_labels[field_name].setText(str(value if value is not None else ""))
                            else:
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

    def apply_theme(self):
        """Applique le thème actuel à tous les widgets"""
        styles = Styles.get_styles(self.is_dark_mode)

        # Application des styles
        self.setStyleSheet(styles['MAIN_WINDOW'])
        self.search_input.setStyleSheet(styles['INPUT'])
        self.search_type.setStyleSheet(styles['COMBO_BOX'])
        self.sanctions_table.setStyleSheet(styles['TABLE'])

        #pour les boutons
        for button in self.findChildren(QPushButton):
            if button == self.theme_button:
                button.setStyleSheet(styles['THEME_BUTTON'])
            else:
                button.setStyleSheet(styles['BUTTON'])

        # Pour les GroupBox
        for group_box in self.findChildren(QGroupBox):
            group_box.setStyleSheet(styles['GROUP_BOX'])

        # Pour les labels d'information et leurs valeurs
        fields_dict = dict(self.info_fields)
        for field_id, value_label in self.info_labels.items():
            # Trouve le label titre correspondant
            for widget in self.findChildren(QLabel):
                if widget.text() == f"{fields_dict[field_id]}:":
                    widget.setStyleSheet(f"""
                        QLabel {{
                            color: {'white' if self.is_dark_mode else '#333333'};
                            font-weight: bold;
                        }}
                    """)
            # Style pour le label valeur
            value_label.setStyleSheet(f"""
                QLabel {{
                    padding: 5px;
                    background: {styles['SURFACE_COLOR']};
                    color: {'white' if self.is_dark_mode else '#333333'};
                    border-radius: 3px;
                    min-width: 200px;
                }}
            """)

    def show_stats_window(self):
        """Ouvre la fenêtre des statistiques"""
        from src.ui.stats_window import StatsWindow
        self.stats_window = StatsWindow(self.db_manager)
        self.stats_window.show()

    def show_import_window(self):
        """Ouvre la fenêtre d'import"""
        from src.ui.import_window import ImportWindow
        self.import_window = ImportWindow()
        self.import_window.show()

    def show_new_case_form(self):
        """Ouvre le formulaire nouveau dossier"""
        try:
            from src.ui.forms.new_case_form import NewCaseForm
            self.new_case_form = NewCaseForm(self.db_manager)
            self.new_case_form.show()
        except Exception as e:
            print(f"Erreur lors de l'ouverture du formulaire : {str(e)}")
            QMessageBox.critical(
                self,
                "Erreur",
                "Impossible d'ouvrir le formulaire nouveau dossier."
            )

    def import_etat_complet(self):
        """Import de l'état complet des gendarmes"""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Importer l'état complet",
            "",
            "Excel files (*.xlsx *.xls)"
        )
        if file_name:
            self.import_window = ImportEtatCompletWindow(self.db_manager)
            self.import_window.import_file(file_name)

    def toggle_theme(self):
        """Bascule entre les thèmes clair et sombre"""
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()
        # Change l'icône selon le thème
        icon_name = "dark_mode.png" if self.is_dark_mode else "light_mode.png"
        self.theme_button.setIcon(QIcon(f"../resources/icons/{icon_name}"))

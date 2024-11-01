import pandas as pd
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLineEdit, QPushButton, QLabel,
                             QTableWidget, QTableWidgetItem, QTabWidget,
                             QComboBox, QGroupBox, QGridLayout, QMessageBox,
                             QHeaderView, QToolBar, QFileDialog, QDockWidget)

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon, QPixmap
from src.database.db_manager import DatabaseManager
from src.ui.styles.styles import Styles
from src.database.models import GendarmeRepository, SanctionRepository
from src.ui.windows.import_etat_window import ImportEtatCompletWindow


class MainGendarmeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logo_label = QLabel()  # Ajouter pour le logo
        # Autres initialisations
        self.sanctions_table = None
        self.search_input = None
        self.toolbar = None
        self.theme_button = None
        self.info_labels = None
        self.is_dark_mode = False
        self.db_manager = DatabaseManager()
        self.gendarme_repository = GendarmeRepository(self.db_manager)
        self.sanction_repository = SanctionRepository(self.db_manager)
        self.info_group = None  # Correction : Attribut de classe pour info_group
        self.sanctions_group = None  # Correction : Attribut de classe pour sanctions_group

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

        # Configuration de la barre de recherche avec logo
        search_group = QGroupBox("Recherche")
        search_layout = QHBoxLayout()
        self.search_type = QComboBox()
        self.search_type.addItems(["Matricule (MLE)", "Nom"])
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Entrez votre recherche...")
        search_button = QPushButton("Rechercher")
        search_button.clicked.connect(self.search_gendarme)
        layout.addWidget(search_group, alignment=Qt.AlignmentFlag.AlignTop)

        # Ajouter le logo et cacher lors d'une recherche
        logo_pixmap = QPixmap("../resources/icons/logo.png")  # Chemin de l'image du logo
        self.logo_label.setPixmap(logo_pixmap)
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centrer le logo
        self.logo_label.setFixedSize(1000, 600)
        self.logo_label.setScaledContents(True)
        layout.addWidget(self.logo_label)

        search_layout.addWidget(self.search_type)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        search_layout.addStretch()
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)
        layout.addWidget(self.logo_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Déplacement de la barre d'outils à gauche
        dock_widget = QDockWidget("Options", self)
        dock_widget.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock_widget)

        toolbar = QToolBar("Toolbar")
        toolbar.setOrientation(Qt.Orientation.Vertical)

        # Boutons "Statistiques" et "Nouveau dossier" avec icônes et labels
        stats_button = QPushButton("Statistiques")
        stats_button.setIcon(QIcon("../resources/icons/statistics_icon.png"))
        stats_button.setStyleSheet("text-align: left; padding: 5px;")
        stats_button.clicked.connect(self.show_stats_window)

        new_case_button = QPushButton("Nouveau Dossier")
        new_case_button.setIcon(QIcon("../resources/icons/new_case_icon.png"))
        new_case_button.setStyleSheet("text-align: left; padding: 5px;")
        new_case_button.clicked.connect(self.show_new_case_form)

        toolbar.addWidget(stats_button)
        toolbar.addWidget(new_case_button)
        dock_widget.setWidget(toolbar)

        settings_button = QPushButton("Réglages")
        settings_button.clicked.connect(self.open_settings_window)
        toolbar.addWidget(settings_button)

        # Informations du gendarme
        self.info_group = QGroupBox("Informations du gendarme")  # Correction : Déclaration de self.info_group
        self.info_group.setVisible(False)  # Cacher au départ
        info_layout = QGridLayout()
        self.info_group.setFont(QFont('Helvetica', 18, QFont.Weight.Bold))

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

        self.info_group.setLayout(info_layout)
        layout.addWidget(self.info_group)

        # Tableau des sanctions
        self.sanctions_group = QGroupBox("Sanctions")  # Correction : Déclaration de self.sanctions_group
        self.sanctions_group.setVisible(False)
        sanctions_layout = QVBoxLayout()
        self.sanctions_group.setFont(QFont('Helvetica', 18, QFont.Weight.Bold))

        self.sanctions_table = QTableWidget()
        self.sanctions_table.setColumnCount(8)
        headers = ["Date des faits", "Type de faute", "Sanction", "Référence",
                   "Taux (JAR)", "Comité", "Année", "N° Dossier"]
        self.sanctions_table.setHorizontalHeaderLabels(headers)
        self.sanctions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        sanctions_layout.addWidget(self.sanctions_table)
        self.sanctions_group.setLayout(sanctions_layout)
        layout.addWidget(self.sanctions_group)

        self.statusBar().showMessage("Prêt")
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

                if self.search_type.currentText() == "Matricule (MLE)":
                    where_clause = "WHERE mle = ?"
                else:
                    where_clause = "WHERE nom_prenoms LIKE ?"
                    search_text = f"%{search_text}%"

                cursor.execute(f"SELECT * FROM gendarmes {where_clause}", (search_text,))
                gendarme = cursor.fetchall()

                if gendarme:
                    self.logo_label.setVisible(False)
                    self.info_group.setVisible(True)
                    self.sanctions_group.setVisible(True)

                    field_names = [description[0] for description in cursor.description]
                    for field_name, value in zip(field_names[1:], gendarme[1:]):
                        if field_name in self.info_labels:
                            if field_name in ['date_naissance', 'date_entree_gie'] and value:
                                try:
                                    date_obj = pd.to_datetime(value)
                                    formatted_value = date_obj.strftime('%d/%m/%Y')
                                    self.info_labels[field_name].setText(formatted_value)
                                except:
                                    self.info_labels[field_name].setText(str(value if value is not None else ""))
                            else:
                                self.info_labels[field_name].setText(str(value if value is not None else ""))

                    cursor.execute("""
                        SELECT date_faits, faute_commise, statut, reference_statut,
                               taux_jar, comite, annee_faits, numero_dossier
                        FROM sanctions
                        WHERE gendarme_id = ?
                        ORDER BY date_faits DESC
                    """, (gendarme[0],))

                    sanctions = cursor.fetchall()
                    self.sanctions_table.setRowCount(len(sanctions))
                    for row, sanction in enumerate(sanctions):
                        for col, value in enumerate(sanction):
                            self.sanctions_table.setItem(row, col, QTableWidgetItem(str(value)))
                else:
                    QMessageBox.information(self, "Résultat", "Aucun gendarme trouvé.")

        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

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
            self.new_case_form.is_dark_mode = self.is_dark_mode
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

    def open_settings_window(self):
        """Ouvre une fenêtre de réglages"""
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)

        import_etat_button = QPushButton("Importer Matrice Gendarmes")
        import_etat_button.clicked.connect(self.import_etat_complet)
        theme_button = QPushButton("Changer le thème")
        theme_button.clicked.connect(self.toggle_theme)
        import_button = QPushButton("Importer Matrice Disciplinaire")
        import_button.clicked.connect(self.show_import_window)

        settings_layout.addWidget(import_etat_button)
        settings_layout.addWidget(theme_button)
        settings_layout.addWidget(import_button)

        self.settings_window = QMainWindow()
        self.settings_window.setWindowTitle("Réglages")
        self.settings_window.setCentralWidget(settings_widget)
        self.settings_window.setGeometry(100, 100, 300, 200)
        self.settings_window.show()

    def toggle_theme(self):
        """Bascule entre les thèmes clair et sombre"""
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()
        # Change l'icône selon le thème
        # icon_name = "dark_mode.png" if self.is_dark_mode else "light_mode.png"
        # self.theme_button.setIcon(QIcon(f"../resources/icons/{icon_name}"))

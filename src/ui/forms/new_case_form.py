import sqlite3
from datetime import datetime, date
from typing import Tuple



from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QFrame, QPushButton, QScrollArea, QGraphicsOpacityEffect, QApplication, QLineEdit,
                             QFormLayout, QComboBox, QSpinBox, QDateEdit, QMessageBox, QTextEdit)
from PyQt6.QtCore import Qt, QDate, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QTimer, QSize, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

from src.data.gendarmerie import STRUCTURE_UNITE
from src.data.gendarmerie.utilities import FAULT_ITEMS, MATRIMONIAL_ITEMS, GENDER_ITEMS, RANKS_ITEMS, STATUT_ITEMS
from src.data.gendarmerie.structure import (get_all_unit_names, get_unit_by_name, get_all_regions, get_all_subdivisions,
                                            get_all_legions, Unit)
from src.database.models import GendarmesRepository, DossiersRepository, SanctionsRepository
from src.ui.styles.styles import Styles  # On va ajouter des styles dédiés
from src.ui.forms.unit_search_dialog import UnitSearchDialog
from src.ui.windows.statistics import StatistiquesWindow
from src.utils.combobox_handler import ComboBoxHandler, logger
from src.utils.date_utils import qdate_to_date, calculate_age, calculate_service_years, validate_date_order, \
    is_valid_age_range, str_to_date, to_db_format, get_date_value, adapt_date


class NewCaseForm(QMainWindow):
    """Formulaire de création d'un nouveau dossier de sanction"""

    case_added = pyqtSignal()

    def __init__(self, db_manager):
        """
                Initialise le formulaire
                Args:
                    db_manager: Instance du gestionnaire de base de données
                """
        super().__init__()
        self.db_manager = db_manager
        self.setWindowTitle("Page enregistrement de dossier")
        self.setMinimumSize(1200, 800)
        self.combo_handler = ComboBoxHandler(self.db_manager)
        self.is_dark_mode = False
        self.styles = Styles.get_styles(self.is_dark_mode)
        self.setStyleSheet(self.styles["MAIN_WINDOW"])
        self.current_section = 0  # Pour tracker la section active
        self.init_ui()
        self.gendarmes_repo = GendarmesRepository(self.db_manager)
        self.dossiers_repo = DossiersRepository(self.db_manager)
        self.sanctions_repo = SanctionsRepository(self.db_manager)

    def setup_comboboxes(self):
        """Configure toutes les combobox du formulaire"""
        # Situation matrimoniale
        self.situation_matrimoniale.setProperty("table_name", "Sit_mat")
        self.situation_matrimoniale.setProperty("value_column", "lib_sit_mat")
        self.combo_handler.setup_db_combobox(
            self.situation_matrimoniale,
            "Sit_mat",
            "lib_sit_mat",
            "id_sit_mat",
            order_by="lib_sit_mat"
        )

        # Unité
        self.unite.setProperty("table_name", "Unite")
        self.unite.setProperty("value_column", "lib_unite")
        self.combo_handler.setup_db_combobox(
            self.unite,
            "Unite",
            "lib_unite",
            "id_unite",
            order_by="lib_unite"
        )

        # Légion
        self.legion.setProperty("table_name", "Legion")
        self.legion.setProperty("value_column", "lib_legion")
        self.combo_handler.setup_db_combobox(
            self.legion,
            "Legion",
            "lib_legion",
            "id_legion",
            order_by="lib_legion"
        )

        # Subdivision
        self.subdivision.setProperty("table_name", "Subdiv")
        self.subdivision.setProperty("value_column", "lib_subdiv")
        self.combo_handler.setup_db_combobox(
            self.subdivision,
            "Subdiv",
            "lib_subdiv",
            "id_subdiv",
            order_by="lib_subdiv"
        )

        # Région
        self.region.setProperty("table_name", "Region")
        self.region.setProperty("value_column", "lib_rg")
        self.combo_handler.setup_db_combobox(
            self.region,
            "Region",
            "lib_rg",
            "id_rg",
            order_by="lib_rg"
        )

        # Grade
        self.grade.setProperty("table_name", "Grade")
        self.grade.setProperty("value_column", "lib_grade")
        self.combo_handler.setup_db_combobox(
            self.grade,
            "Grade",
            "lib_grade",
            "id_grade",
            order_by="lib_grade"
        )

        # Type de sanction
        self.type_sanction.setProperty("table_name", "Type_sanctions")
        self.type_sanction.setProperty("value_column", "lib_type_sanction")
        self.combo_handler.setup_db_combobox(
            self.type_sanction,
            "Type_sanctions",
            "lib_type_sanction",
            "id_type_sanction",
            order_by="lib_type_sanction"
        )

        # Faute
        self.faute_commise.setProperty("table_name", "Fautes")
        self.faute_commise.setProperty("value_column", "lib_faute")
        self.combo_handler.setup_db_combobox(
            self.faute_commise,
            "Fautes",
            "lib_faute",
            "id_faute",
            order_by="lib_faute"
        )

        # Statut
        self.statut.setProperty("table_name", "Statut")
        self.statut.setProperty("value_column", "lib_statut")
        self.combo_handler.setup_db_combobox(
            self.statut,
            "Statut",
            "lib_statut",
            "id_statut",
            order_by="lib_statut"
        )

    # Ajout des méthodes de gestion
    def setup_sanction_fields(self):
        """Configure les champs liés aux sanctions"""
        # Configuration initiale du type de sanction
        self.combo_handler.setup_db_combobox(
            self.type_sanction,
            "Type_sanctions",
            "lib_type_sanction",
            "id_type_sanction",
            order_by="lib_type_sanction"
        )

        # Connexion des signaux
        self.statut.currentTextChanged.connect(self.on_statut_change)
        self.type_sanction.currentTextChanged.connect(self.on_type_sanction_change)

    def setup_unite_hierarchy(self):
        """Configure la hiérarchie unité -> région -> subdivision -> légion"""
        # Chargement initial des unités
        self.combo_handler.setup_db_combobox(
            self.unite,
            "Unite",
            "lib_unite",
            "id_unite",
            order_by="lib_unite"
        )

        # Connexion des signaux
        self.unite.currentTextChanged.connect(self.on_unite_changed)
        self.region.currentTextChanged.connect(self.on_region_changed)
        self.subdivision.currentTextChanged.connect(self.on_subdivision_changed)

    def on_unite_changed(self, unite_value: str):
        """Gestionnaire de changement d'unité"""
        self.combo_handler.load_hierarchical_data(
            self.region,
            "Region",
            "lib_rg",
            "unite",
            unite_value
        )
        # Réinitialiser les combobox enfants
        self.subdivision.clear()
        self.legion.clear()

    def on_region_changed(self, region_value: str):
        """Gestionnaire de changement de région"""
        self.combo_handler.load_hierarchical_data(
            self.subdivision,
            "Subdiv",
            "lib_subdiv",
            "region",
            region_value
        )
        self.legion.clear()

    def on_subdivision_changed(self, subdiv_value: str):
        """Gestionnaire de changement de subdivision"""
        self.combo_handler.load_hierarchical_data(
            self.legion,
            "Legion",
            "lib_legion",
            "subdivision",
            subdiv_value
        )

    def init_ui(self):

        # Widget principal avec scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.setCentralWidget(scroll)

        main_widget = QWidget()
        scroll.setWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Titre du formulaire
        title = QLabel("Nouveau Dossier Disciplinaire")
        title.setFont(QFont('Helvetica', 36, QFont.Weight.Bold))
        title.setStyleSheet("color: #FFFFFF; margin-bottom: 20px;")
        layout.addWidget(title)

        # Conteneur des sections
        self.sections_container = QWidget()
        self.sections_container.setStyleSheet(self.styles['MAIN_WINDOW'])
        sections_layout = QHBoxLayout(self.sections_container)
        sections_layout.setSpacing(20)

        # Les trois sections
        #prevoir mettre les subtitles en tooltip
        self.section1 = self.create_section("📝 Informations du Dossier", "Numéro, dates et détails administratifs")
        self.section2 = self.create_section("👤 Informations du Mis en Cause", "Identité et affectation du gendarme")
        self.section3 = self.create_section("⚖️ Informations sur la Faute", "Nature et détails de la sanction")

        #Reglage initial : les deux autres fenêtres sont cachees
        self.section2.setVisible(False)
        self.section3.setVisible(False)

        sections_layout.addWidget(self.section1)
        sections_layout.addWidget(self.section3)
        sections_layout.addWidget(self.section2)

        layout.addWidget(self.sections_container)

        # Configuration des combobox
        self.setup_comboboxes()

        #Configuration champs de sanctions
        self.setup_sanction_fields()

        # Configuration des champs de radiation
        self.setup_radiation_fields()

        # Boutons de navigation
        nav_layout = QHBoxLayout()
        self.prev_button = QPushButton("← Précédent")
        self.next_button = QPushButton("Suivant →")
        self.submit_button = QPushButton("Enregistrer")

        for btn in [self.prev_button, self.next_button, self.submit_button]:
            btn.setStyleSheet("""
                QPushButton {
                    padding: 10px 20px;
                    border-radius: 5px;
                    font-size: 14px;
                    min-width: 120px;
                }
            """)

        self.prev_button.setStyleSheet(self.prev_button.styleSheet() + """
            QPushButton {
                background-color: #e0e0e0;
                color: #333;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
        """)

        self.next_button.setStyleSheet(self.next_button.styleSheet() + """
            QPushButton {
                background-color: #2196f3;
                color: white;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
        """)

        self.submit_button.setStyleSheet(self.submit_button.styleSheet() + """
            QPushButton {
                background-color: #4caf50;
                color: white;
            }
            QPushButton:hover {
                background-color: #43a047;
            }
        """)

        nav_layout.addWidget(self.prev_button)
        nav_layout.addStretch()
        nav_layout.addWidget(self.next_button)
        nav_layout.addWidget(self.submit_button)
        layout.addLayout(nav_layout)

        # Initial state
        self.prev_button.setVisible(False)
        self.submit_button.setVisible(False)
        self.update_navigation()

        # Connexions
        self.prev_button.clicked.connect(self.previous_section)
        self.next_button.clicked.connect(self.next_section)
        self.submit_button.clicked.connect(self.submit_form)
        # Connexion du signal de changement de statut
        self.statut.currentTextChanged.connect(self.on_statut_change)

    def create_section(self, title, subtitle=""):
        """
                Crée une section du formulaire
                Args:
                    title: Titre de la section
                    subtitle: Sous-titre de la section (optionnel)
                Returns:
                    QFrame: La section créée avec son contenu
                """
        section = QFrame()
        section.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 10px;
                padding: 20px;
            }
            QFrame:hover {
                border : 1px solid #d1d1d1
            }
        """)

        layout = QVBoxLayout(section)

        # Titre avec icon
        title_label = QLabel(title)
        title_label.setFont(QFont('Helvetica', 18, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #1976d2; margin-bottom: 5px;")
        layout.addWidget(title_label)

        # Sous-titre
        if title.startswith("📝"):  # Section Info Dossier
            content = self.create_case_info_section()
            layout.addWidget(content)
        elif title.startswith("👤"):  # Section Info Mis en cause
            content = self.create_suspect_info_section()
            layout.addWidget(content)
        else:
            #title.startswith("⚖️"):  # Section Info Faute
            content = self.create_fault_info_section()
            layout.addWidget(content)

        layout.addStretch()
        return section

    def update_navigation(self):
        self.prev_button.setVisible(self.current_section > 0)
        self.next_button.setVisible(self.current_section < 2)
        self.submit_button.setVisible(self.current_section == 2)

    def switch_section(self, index):
        """
                Gère la transition entre les sections
                Args:
                    index: Index de la section à afficher
                """
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        # Animation des sections
        for i, section in enumerate([self.section1, self.section3, self.section2]):
            # Création d'un groupe d'animations pour synchroniser les animations de taille, opacité et position
            animation_group = QParallelAnimationGroup()

            # Animation de la taille
            size_animation = QPropertyAnimation(section, b"maximumWidth")
            size_animation.setDuration(900)
            size_animation.setEasingCurve(QEasingCurve.Type.InOutQuint)

            # Définir la taille en fonction de l'index de la section active
            if i == index:
                # Section active
                size_animation.setStartValue(section.width())
                size_animation.setEndValue(section.width() * 2.2)
                section.setStyleSheet("""
                    QFrame {
                        background: white;
                        border-radius: 10px;
                        padding: 20px;
                        border: 1px solid #2196f3;
                        opacity : 1;
                        z-index: 1000;
                        position: relative;
                    }
                """)
                section.raise_()  # Met la section au premier plan
            else:
                # Sections inactives
                size_animation.setStartValue(section.width())
                size_animation.setEndValue(section.width() // 2.5)
                section.setStyleSheet("""
                    QFrame {
                        background: #f5f7fa;
                        border-radius: 10px;
                        padding: 20px;
                        border: none;
                        opacity: 0.5;
                        z-index: 1;
                    }
                """)
                section.lower()  # Met les sections inactives en arrière-plan

            # Ajouter l'animation de taille au groupe
            animation_group.addAnimation(size_animation)

            # Animation de l'opacité
            opacity_effect = QGraphicsOpacityEffect(section)
            section.setGraphicsEffect(opacity_effect)
            opacity_animation = QPropertyAnimation(opacity_effect, b"opacity")
            opacity_animation.setDuration(600)
            opacity_animation.setEasingCurve(QEasingCurve.Type.InOutQuint)

            if i == index:
                opacity_animation.setStartValue(0.7)
                opacity_animation.setEndValue(1.0)
            else:
                opacity_animation.setStartValue(1.0)
                opacity_animation.setEndValue(0.7)

            # Ajouter l'animation d'opacité au groupe
            animation_group.addAnimation(opacity_animation)

            # Animation de translation verticale pour la section active
            if i == index:
                position_animation = QPropertyAnimation(section, b"geometry")
                position_animation.setDuration(300)
                position_animation.setEasingCurve(QEasingCurve.Type.InOutQuint)
                position_animation.setStartValue(section.geometry())
                # Translation de -10 pixels vers le haut
                position_animation.setEndValue(section.geometry().adjusted(0, -10, 0, -10))
                # Ajouter l'animation de position au groupe
                animation_group.addAnimation(position_animation)

            # Démarrer le groupe d'animations pour chaque section
            animation_group.start()
        QTimer.singleShot(1800, lambda: QApplication.restoreOverrideCursor())

    def display_section(self, current_sect):
        for i, section in enumerate([self.section1, self.section3, self.section2]):
            if i == current_sect:
                section.setVisible(True)
            else:
                section.setVisible(False)

    def next_section(self):
        if self.current_section < 2:
            self.current_section += 1
            self.display_section(self.current_section)
            #self.switch_section(self.current_section)
            self.update_navigation()

    def previous_section(self):
        if self.current_section > 0:
            self.current_section -= 1
            self.display_section(self.current_section)
            #self.switch_section(self.current_section)
            self.update_navigation()

    #PREMIERE SECTION
    def create_case_info_section(self):
        """Crée le contenu de la section Informations du Dossier"""
        container = QWidget()
        layout = QFormLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)  # Marges uniformes
        layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)  # Alignement gauche des labels

        # Style commun pour les QLineEdit
        line_edit_style = """
            QLineEdit {
                padding: 20px 20px; 
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background: white;
                min-width: 300px;  
                min-height: 20px; 
                font-size: 16px;  
                color: #333;
                margin-left: 0px;  
            }
            QLineEdit:focus {
                border-color: #2196f3;
                background: #f1f4f8;
            }
            QLineEdit:disabled {
                background: #f5f5f5;
                color: #888;
            }
            QLineEdit::placeholder {
                color: #888;  
                font-style: italic;  
                font-size: 15px;  
            }
        """
        # Style pour les ComboBox
        combo_style = """
                QComboBox {
                    padding: 11px 20px;
                    border: 2px solid #e0e0e0;
                    border-radius: 5px;
                    background: white;
                    min-width: 300px;
                    font-size: 14px;
                    color: #555;
                }
                QComboBox:hover {
                    border-color: #2196f3;
                }
                QComboBox:focus {
                    border-color: #2196f3;
                    background: white;
                }
                QComboBox::drop-down {
                    border: none;
                    padding-right: 20px;
                }
                QComboBox::down-arrow {
                    image: url(../resources/icons/down-arrow.png);
                    width: 12px;
                    height: 12px;
                }
                QComboBox QAbstractItemView {
                    border: 1px solid #e0e0e0;
                    border-radius: 5px;
                    background: white;
                    selection-background-color: #2196f3;
                    selection-color: white;
                    color: #000;
                }
                QComboBox QAbstractItemView::item {
                    padding: 8px 20px;
                    min-height: 30px;
                }
                QComboBox QAbstractItemView::item:hover {
                    background-color: #e3f2fd;
                    color: #1976d2;
                }
            """

        # Style pour les labels
        label_style = """
            QLabel {
                font-size: 15px;  
                font-weight: 600;
                color: #555;  
                padding: 8px 0;  
                min-width: 200px;  
            }
        """

        def create_row(label_text, widget, with_info=False):
            """
                    Crée une ligne de formulaire avec label et widget
                    Args:
                        label_text: Texte du label
                        widget: Widget à afficher (QLineEdit, etc.)
                        with_info: Booléen pour ajouter une icône d'info
                    Returns:
                        QWidget: La ligne complète du formulaire
                    """
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(10)

            label = QLabel(label_text)
            label.setStyleSheet(label_style)
            row_layout.addWidget(label)

            widget.setStyleSheet(line_edit_style)
            row_layout.addWidget(widget)

            if with_info:
                info_icon = QPushButton("ℹ️")
                info_icon.setToolTip("Remplir uniquement en cas de radiation")
                info_icon.setStyleSheet("""
                    QPushButton {
                        border: none;
                        background: transparent;
                        font-size: 16px;
                        color: #2196f3;
                        margin: 0 5px;
                    }
                    QPushButton:hover {
                        color: #1769aa;
                    }
                """)
                row_layout.addWidget(info_icon)

            row_layout.addStretch()
            return row_widget

        # N° Dossier
        self.num_dossier = QLineEdit()
        self.num_dossier.setPlaceholderText("Entrez le N° de dossier")
        layout.addRow(create_row("N° Dossier", self.num_dossier))

        # Année
        self.annee_punition = QLineEdit()
        self.annee_punition.setText(str(datetime.now().year))
        self.annee_punition.setReadOnly(True)
        layout.addRow(create_row("Année en cours", self.annee_punition))

        # Date d'enregistrement
        self.date_enr = QDateEdit()
        self.date_enr.setCalendarPopup(True)
        self.date_enr.setDate(QDate.currentDate())
        self.date_enr.dateChanged.connect(self.update_annee_enr)
        self.date_enr.setStyleSheet(self.styles['DATE_EDIT'])

        today_button = QPushButton("Aujourd'hui")
        today_button.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                background-color: #2196f3;
                color: white;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
        """)
        today_button.clicked.connect(lambda: self.date_enr.setDate(QDate.currentDate()))

        date_enr_layout = QHBoxLayout()
        date_enr_layout.addWidget(self.date_enr)
        date_enr_layout.addWidget(today_button)
        date_enr_container = QWidget()
        date_enr_container.setLayout(date_enr_layout)
        layout.addRow(create_row("Date d'enregistrement", date_enr_container))

        # N° enregistrement
        self.num_enr = QLineEdit()
        self.num_enr.setReadOnly(True)
        self.get_next_num_enr()
        layout.addRow(create_row("N° enregistrement", self.num_enr))

        container.setLayout(layout)
        return container

    def update_annee_enr(self):
        """Met à jour l'année d'enregistrement automatiquement"""
        self.annee_punition.setText(str(self.date_enr.date().year()))

    def create_label(self, text):
        """Crée un label stylé"""
        label = QLabel(text)
        label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #333;
                min-width: 150px;
            }
        """)
        return label

    def get_next_num_enr(self):
        """Récupère le prochain numéro d'enregistrement"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                # Récupère le plus grand numéro pour l'année en cours
                cursor.execute("""
                     SELECT MAX(numero_inc)
                     FROM Dossiers
                     WHERE strftime('%Y', date_enr) = ?
                 """, (str(datetime.now().year),))

                last_num = cursor.fetchone()[0]
                next_num = 1 if last_num is None else last_num + 1
                self.num_enr.setText(str(next_num))

        except Exception as e:
            logger.error(f"Erreur lors de la récupération du numéro : {str(e)}")
            self.num_enr.setText("1")

    #DEUXIEME SECTION
    def create_fault_info_section(self):
        """
        Crée la section des informations sur la faute
        Returns:
            QWidget: Container contenant les informations sur la faute
        """

        def create_row(label_text, widget):
            """
            Crée une ligne de formulaire avec label et widget
            Args:
                label_text: Texte du label
                widget: Widget à afficher (QLineEdit, QComboBox, etc.)
            Returns:
                QWidget: La ligne complète du formulaire
            """
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(10)

            label = QLabel(label_text)
            label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    font-weight: 800;
                    color: #333;
                    padding: 8px 0;
                    min-width: 200px;
                }
            """)
            row_layout.addWidget(label)
            row_layout.addWidget(widget)
            row_layout.addStretch()
            return row_widget

        container = QWidget()
        layout = QFormLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        # Date des faits avec calendrier
        self.date_faits = QDateEdit()
        self.date_faits.setCalendarPopup(True)
        self.date_faits.setDate(QDate.currentDate())
        self.date_faits.dateChanged.connect(self.update_annee_faits)
        self.date_faits.setStyleSheet(self.styles['DATE_EDIT'])
        layout.addRow(create_row("Date des faits", self.date_faits))

        # Faute commise (ComboBox)
        self.faute_commise = QComboBox()
        self.faute_commise.addItems(FAULT_ITEMS)
        self.faute_commise.setStyleSheet(self.styles['COMBO_BOX'])
        layout.addRow(create_row("Faute commise", self.faute_commise))

        # Libellé
        self.libelle = QTextEdit()  # On utilise QTextEdit pour permettre plusieurs lignes
        self.libelle.setStyleSheet("""
            QTextEdit {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 10px;
                background: white;
                min-height: 100px;
                font-size: 14px;
            }
            QTextEdit:focus {
                border-color: #2196f3;
                background: #f8f9fa;
            }
        """)
        self.libelle.setPlaceholderText("Entrez le libellé détaillé de la faute...")
        layout.addRow(create_row("Libellé", self.libelle))

        # Catégorie
        self.categorie = QLineEdit()
        self.categorie.setStyleSheet(self.styles['INPUT'])
        layout.addRow(create_row("Catégorie", self.categorie))

        # Statut du dossier
        self.statut = QComboBox()
        self.statut.addItems(STATUT_ITEMS)
        #self.statut.currentTextChanged.connect(self.on_statut_change)
        self.statut.setStyleSheet(self.styles['COMBO_BOX'])
        layout.addRow(create_row("Statut du dossier", self.statut))

        # Type de sanction (initialement désactivé)
        self.type_sanction = QComboBox()
        self.type_sanction.setEnabled(False)  # Désactivé par défaut
        self.type_sanction.setStyleSheet(self.styles['COMBO_BOX'])
        layout.addRow(create_row("Type de sanction", self.type_sanction))

        # Décision de radiation
        self.num_decision = QLineEdit()
        self.num_decision.setEnabled(False)
        self.num_decision.setPlaceholderText("Numéro de décision (si disponible)")
        self.num_decision.setStyleSheet(self.styles['INPUT'])
        layout.addRow(create_row("Numéro de décision", self.num_decision))

        # Arrêté de radiation
        self.num_arrete = QLineEdit()
        self.num_arrete.setEnabled(False)
        self.num_arrete.setPlaceholderText("Numéro d'arrêté (si disponible)")
        self.num_arrete.setStyleSheet(self.styles['INPUT'])
        layout.addRow(create_row("Numéro d'arrêté", self.num_arrete))

        # Référence du statut
        self.ref_statut = QLineEdit()
        self.ref_statut.setStyleSheet(self.styles['INPUT'])
        self.ref_statut.setPlaceholderText("Référence de radiation")
        layout.addRow(create_row("Référence du statut", self.ref_statut))


        # TAUX (JAR)
        self.taux_jar = QSpinBox()
        self.taux_jar.setMinimum(0)
        self.taux_jar.setMaximum(365)
        self.taux_jar.setStyleSheet(self.styles['SPIN_BOX'])
        layout.addRow(create_row("TAUX (JAR)", self.taux_jar))

        # COMITE
        self.comite = QLineEdit()
        self.comite.setStyleSheet(self.styles['INPUT'])
        layout.addRow(create_row("COMITE", self.comite))

        # ANNEE DES FAITS (auto)
        self.annee_faits = QLineEdit()
        self.annee_faits.setReadOnly(True)
        self.annee_faits.setStyleSheet(self.styles['INPUT'])
        layout.addRow(create_row("ANNEE DES FAITS", self.annee_faits))

        container.setLayout(layout)
        return container

    def update_annee_faits(self):
        """Met à jour l'année des faits automatiquement"""
        self.annee_faits.setText(str(self.date_faits.date().year()))

    def setup_radiation_fields(self):
        """Configure le conteneur pour les champs de radiation"""
        # On utilise les champs existants
        radiation_fields = [
            self.ref_statut,
            self.num_decision,
            self.num_arrete
        ]

        # Cache initialement tous les champs de radiation
        for field in radiation_fields:
            field.setVisible(False)

    def on_statut_change(self, statut: str):
        """
        Gère le changement de statut et ses effets sur les autres champs
        Args:
            statut: Le statut sélectionné
        """
        # Activation/désactivation du type de sanction selon le statut
        self.type_sanction.setEnabled(True)  # On active toujours la combobox

        if statut == "EN COURS":
            # Sélectionner "EN INSTANCE" et désactiver les champs liés
            index = self.type_sanction.findText("EN INSTANCE")
            if index >= 0:
                self.type_sanction.setCurrentIndex(index)
            self.type_sanction.setEnabled(False)  # Verrouiller sur "EN INSTANCE"

            # Réinitialiser et désactiver les champs liés
            self.num_decision.clear()
            self.num_arrete.clear()
            self.num_decision.setEnabled(False)
            self.num_arrete.setEnabled(False)
            self.taux_jar.setValue(0)
            self.taux_jar.setEnabled(False)

        elif statut == "SANCTIONNE":
            # Activer tous les champs nécessaires
            self.type_sanction.setEnabled(True)
            self.taux_jar.setEnabled(True)
            # La gestion des champs de radiation se fait dans on_type_sanction_change

        else:
            # Pour tout autre statut, réinitialiser
            self.type_sanction.setCurrentIndex(0)
            self.type_sanction.setEnabled(False)
            self.num_decision.clear()
            self.num_arrete.clear()
            self.num_decision.setEnabled(False)
            self.num_arrete.setEnabled(False)
            self.taux_jar.setValue(0)
            self.taux_jar.setEnabled(False)


    def on_type_sanction_change(self, type_sanction: str):
        """Gère le changement de type de sanction"""
        is_radiation = type_sanction == "RADIATION"
        self.num_decision.setEnabled(is_radiation)
        self.num_arrete.setEnabled(is_radiation)
        self.ref_statut.setEnabled(is_radiation)

        if not is_radiation:
            self.num_decision.clear()
            self.num_arrete.clear()
            self.ref_statut.clear()

    # TROISIEME SECTION
    def on_matricule_change(self, matricule: str):
        """
        Gère l'auto-complétion lors de la saisie du matricule
        Args:
            matricule: Matricule saisi
        """
        if len(matricule) >= 4:
            try:
                print(f"Recherche du matricule : {matricule}")  # Debug
                result = self.gendarmes_repo.search_by_matricule(matricule)

                if result:
                    print(f"Résultat trouvé : {result}")  # Debug
                    # Mise à jour des champs avec les données trouvées
                    self.nom.setText(result.nom if result.nom else "")
                    self.prenoms.setText(result.prenoms if result.prenoms else "")

                    # Gestion de la date de naissance
                    if hasattr(result, 'date_naissance') and result.date_naissance:
                        date_str = result.date_naissance.strftime('%d/%m/%Y')
                        print(f"Date de naissance : {date_str}")  # Debug
                        self.date_naissance.setText(date_str)
                        self.update_age(result.date_naissance)

                    # Gestion de la date d'entrée en service
                    if hasattr(result, 'date_entree_service') and result.date_entree_service:
                        date_str = result.date_entree_service.strftime('%d/%m/%Y')
                        print(f"Date d'entrée : {date_str}")  # Debug
                        self.date_entree_gie.setText(date_str)
                        self.update_years_of_service(result.date_entree_service)

                    # Autres champs
                    if hasattr(result, 'sexe'):
                        self.sexe.setCurrentText(result.sexe if result.sexe else "")
                    if hasattr(result, 'lieu_naissance'):
                        self.lieu_naissance.setText(result.lieu_naissance if result.lieu_naissance else "")

                    # Informations optionnelles
                    if hasattr(result, 'nb_enfants') and result.nb_enfants is not None:
                        self.nb_enfants.setValue(result.nb_enfants)
                    if hasattr(result, 'annee_service') and result.annee_service is not None:
                        self.annee_service.setValue(result.annee_service)
                else:
                    print("Aucun résultat trouvé")  # Debug
                    # Ne pas effacer les champs si aucun résultat n'est trouvé
                    # self.clear_form_fields()  # Commenté pour éviter l'effacement

            except Exception as e:
                print(f"Erreur détaillée lors de la recherche du gendarme : {str(e)}")  # Debug détaillé
                logger.error(f"Erreur lors de la recherche du gendarme : {str(e)}")
                QMessageBox.warning(self, "Erreur",
                                    f"Une erreur est survenue lors de la recherche du gendarme : {str(e)}")

    def update_age(self, birth_date: date):
        """Met à jour l'âge en fonction de la date des faits"""
        faits_date = qdate_to_date(self.date_faits.date())
        age = calculate_age(birth_date, faits_date)
        self.age.setValue(age)

    def update_years_of_service(self, entry_date: date):
        """Met à jour les années de service en fonction de la date des faits"""
        faits_date = qdate_to_date(self.date_faits.date())
        years = calculate_service_years(entry_date, faits_date)
        self.annee_service.setValue(years)

    def validate_dates(self) -> Tuple[bool, str]:
        """Valide toutes les dates du formulaire"""
        date_faits = qdate_to_date(self.date_faits.date())
        date_enr = qdate_to_date(self.date_enr.date())

        # Vérification de l'ordre des dates
        valid, message = validate_date_order(date_faits, date_enr)
        if not valid:
            return False, message

        # Vérification de l'âge à la date des faits
        birth_date = str_to_date(self.date_naissance.text())
        if birth_date:
            valid, message = is_valid_age_range(birth_date, date_faits)
            if not valid:
                return False, message

        return True, ""

    def get_formatted_dates(self) -> dict:
        """Récupère toutes les dates du formulaire au format base de données"""
        return {
            'date_faits': to_db_format(qdate_to_date(self.date_faits.date())),
            'date_enr': to_db_format(qdate_to_date(self.date_enr.date())),
            'date_naissance': to_db_format(str_to_date(self.date_naissance.text())),
            'date_entree_service': to_db_format(str_to_date(self.date_entree_gie.text()))
        }

    def clear_form_fields(self):
        """Réinitialise tous les champs du formulaire"""
        # Informations du dossier
        self.num_dossier.clear()
        self.annee_punition.setText(str(datetime.now().year))
        self.date_enr.setDate(QDate.currentDate())
        self.num_enr.clear()

        # Informations du gendarme
        self.matricule.clear()
        self.nom.clear()
        self.prenoms.clear()
        self.date_naissance.clear()
        self.lieu_naissance.clear()
        self.sexe.setCurrentIndex(0)
        self.grade.setCurrentIndex(0)
        self.unite.setCurrentIndex(0)
        self.region.setCurrentIndex(0)
        self.subdivision.setCurrentIndex(0)
        self.legion.setCurrentIndex(0)
        self.situation_matrimoniale.setCurrentIndex(0)
        self.nb_enfants.setValue(0)
        self.age.setValue(0)
        self.date_entree_gie.clear()
        self.annee_service.setValue(0)

        # Informations sur la faute
        self.date_faits.setDate(QDate.currentDate())
        self.faute_commise.setCurrentIndex(0)
        self.categorie.clear()
        self.statut.setCurrentIndex(0)
        self.ref_statut.clear()
        self.annee_faits.setText(str(datetime.now().year))
        self.libelle.clear()

        # Réinitialisation des champs de sanction
        self.type_sanction.setCurrentIndex(0)
        self.type_sanction.setEnabled(False)
        self.num_decision.clear()
        self.num_decision.setEnabled(False)
        self.num_arrete.clear()
        self.num_arrete.setEnabled(False)
        self.taux_jar.setValue(0)
        self.comite.clear()

    def create_suspect_info_section(self):
        """
        Crée la section des informations du mis en cause avec auto-complétion
        Returns:
            QWidget: Container contenant les informations du gendarme
        """

        def create_row(label_text, widget):
            """
            Crée une ligne de formulaire avec label et widget
            Args:
                label_text: Texte du label
                widget: Widget à afficher (QLineEdit, QComboBox, etc.)
            Returns:
                QWidget: La ligne complète du formulaire
            """
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(10)

            label = QLabel(label_text)
            label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    font-weight: 800;
                    color: #333;
                    padding: 8px 0;
                    min-width: 200px;
                }
            """)
            row_layout.addWidget(label)
            row_layout.addWidget(widget)
            row_layout.addStretch()
            return row_widget

        container = QWidget()
        layout = QFormLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        # Récupération des styles
        #styles = Styles.get_styles(self.is_dark_mode)

        # Matricule avec auto-complétion
        self.matricule = QLineEdit()
        self.matricule.setPlaceholderText("Entrez le matricule")
        self.matricule.setStyleSheet(self.styles['INPUT'])
        self.matricule.textChanged.connect(self.on_matricule_change)
        layout.addRow(create_row("Matricule", self.matricule))

        # Champs auto-remplis
        self.nom = QLineEdit()
        self.nom.setReadOnly(True)
        self.nom.setStyleSheet(self.styles['INPUT'])
        layout.addRow(create_row("Nom", self.nom))

        self.prenoms = QLineEdit()
        self.prenoms.setReadOnly(True)
        self.prenoms.setStyleSheet(self.styles['INPUT'])
        layout.addRow(create_row("Prénoms", self.prenoms))

        #Date de naissance
        self.date_naissance = QLineEdit()
        self.date_naissance.setReadOnly(True)
        self.date_naissance.setStyleSheet(self.styles['INPUT'])
        layout.addRow(create_row("Date de naissance", self.date_naissance))

        # Lieu de naissance
        self.lieu_naissance = QLineEdit()
        self.lieu_naissance.setStyleSheet(self.styles['INPUT'])
        layout.addRow(create_row("Lieu de naissance", self.lieu_naissance))

        # Unité
        self.unite = QComboBox()
        self.unite.addItems(get_all_unit_names(STRUCTURE_UNITE))
        self.unite.setStyleSheet(self.styles['COMBO_BOX'])
        self.unite.currentTextChanged.connect(self.on_unit_selected)

        search_button = QPushButton()
        search_button.setIcon(QIcon("../resources/icons/search.png"))
        search_button.setIconSize(QSize(16, 16))
        search_button.setToolTip("Rechercher unité")
        search_button.setStyleSheet("""
                QPushButton {
                    padding: 8px;
                    border-radius: 3px;
                    background: #2196f3;
                    border: none;
                }
                QPushButton:hover {
                    background: #1976d2;
                }
            """)
        search_button.clicked.connect(self.on_unit_search)

        unite_layout = QHBoxLayout()
        unite_layout.addWidget(self.unite)
        unite_layout.addWidget(search_button)
        unite_container = QWidget()
        unite_container.setLayout(unite_layout)
        layout.addRow(create_row("Unité", unite_container))


        # Région/region
        self.region = QComboBox()
        self.region.setStyleSheet(self.styles['COMBO_BOX'])
        self.region.currentTextChanged.connect(self.on_region_change)
        layout.addRow(create_row("Région/region", self.region))

        # Subdivision
        self.subdivision = QComboBox()
        self.subdivision.setStyleSheet(self.styles['COMBO_BOX'])
        self.subdivision.currentTextChanged.connect(self.on_subdivision_change)
        layout.addRow(create_row("Subdivision", self.subdivision))

        # Légion/legion
        self.legion = QComboBox()
        self.legion.setStyleSheet(self.styles['COMBO_BOX'])
        self.legion.currentTextChanged.connect(self.on_legion_change)
        layout.addRow(create_row("Légion/Division", self.legion))


        # Nombre d'enfants
        self.nb_enfants = QSpinBox()
        self.nb_enfants.setStyleSheet(self.styles['SPIN_BOX'])
        self.nb_enfants.setMinimum(0)
        self.nb_enfants.setMaximum(99)
        layout.addRow(create_row("Nombre d'enfants", self.nb_enfants))

        # Grade
        self.grade = QComboBox()
        self.grade.addItems(RANKS_ITEMS)
        self.grade.setStyleSheet(self.styles['COMBO_BOX'])
        layout.addRow(create_row("Grade", self.grade))

        #Age
        self.age = QSpinBox()
        self.age.setRange(18, 65)
        self.age.setStyleSheet(self.styles['SPIN_BOX'])
        #self.age.setValue(self.update_age())
        layout.addRow(create_row("Age", self.age))

        #Date d'entrée gendarmerie
        self.date_entree_gie = QLineEdit()
        self.date_entree_gie.setReadOnly(True)
        self.date_entree_gie.setStyleSheet(self.styles['INPUT'])
        layout.addRow(create_row("Date d'entrée GIE", self.date_entree_gie))

        #Année service
        self.annee_service = QSpinBox()
        self.annee_service.setRange(0, 40)
        self.annee_service.setStyleSheet(self.styles['SPIN_BOX'])
        #self.date_faits.dateChanged.connect(self.update_years_of_service)
        layout.addRow(create_row("Années de service", self.annee_service))

        self.sexe = QComboBox()
        self.sexe.addItems(GENDER_ITEMS)
        self.sexe.setStyleSheet(self.styles['COMBO_BOX'])
        #self.sexe.setCurrentText(self.get_gendarme_sexe(m))
        layout.addRow(create_row("Sexe", self.sexe))

        self.situation_matrimoniale = QComboBox()
        self.situation_matrimoniale.addItems(MATRIMONIAL_ITEMS)
        self.situation_matrimoniale.setStyleSheet(self.styles['COMBO_BOX'])
        layout.addRow(create_row("Situation matrimoniale", self.situation_matrimoniale))

        container.setLayout(layout)
        return container

    def on_unit_selected(self, unit_name):
        """
        Gère la sélection d'une unité
        Args:
            unit_name: Nom de l'unité sélectionnée
        """
        if not unit_name or unit_name.strip() == "":
            # Réinitialiser les combobox dépendantes
            self.region.clear()
            self.subdivision.clear()
            self.legion.clear()
            return

        unit = get_unit_by_name(STRUCTURE_UNITE, unit_name.strip())
        if unit:
            self.update_unite(unit_name)
            self.update_region(unit.region)
            self.update_subdivision(unit.region, unit.subdivision)
            self.update_legion(unit.region, unit.subdivision, unit.legion)
        else:
            # Gestion du cas où l'unité n'est pas trouvée dans la structure
            QMessageBox.warning(self, "Unité non trouvée",
                                f"L'unité '{unit_name}' n'a pas été trouvée dans la structure.")
            # Réinitialiser les combobox dépendantes
            self.region.clear()
            self.subdivision.clear()
            self.legion.clear()

    def update_region(self, region):
        self.region.clear()
        regions = get_all_regions(STRUCTURE_UNITE)
        self.region.addItems(regions)
        region_index = self.region.findText(region)
        if region_index != -1:
            self.region.setCurrentIndex(region_index)

    def update_subdivision(self, region, subdivision):
        self.subdivision.clear()
        subdivisions = get_all_subdivisions(STRUCTURE_UNITE, region)
        self.subdivision.addItems(subdivisions)
        subdivision_index = self.subdivision.findText(subdivision)
        if subdivision_index != -1:
            self.subdivision.setCurrentIndex(subdivision_index)

    def update_legion(self, region, subdivision, legion):
        self.legion.clear()
        legions = get_all_legions(STRUCTURE_UNITE, region, subdivision)
        self.legion.addItems(legions)
        legion_index = self.legion.findText(legion)
        if legion_index != -1:
            self.legion.setCurrentIndex(legion_index)

    def update_unite(self, unit_name):
        self.unite.setCurrentText(unit_name)

    def calculate_age(self, date_naissance, date_faits):
        try:
            birth_date = QDate.fromString(date_naissance, "%d-%m-%Y")
            faits_date = QDate.fromString(date_faits, "%d-%m-%Y")
            age = faits_date.year() - birth_date.year()
            if faits_date.month() < birth_date.month() or (
                    faits_date.month() == birth_date.month() and faits_date.day() < birth_date.day()):
                age -= 1
            return age
        except Exception as e:
            print(f"Erreur lors du calcul de l'âge : {str(e)}")
            return 0

    def calculate_years_of_service(self, date_entree, date_faits):
        try:
            entree_date = QDate.fromString(date_entree, "yyyy-MM-dd")
            faits_date = QDate.fromString(date_faits, "yyyy-MM-dd")
            years_of_service = faits_date.year() - entree_date.year()
            if faits_date.month() < entree_date.month() or (
                    faits_date.month() == entree_date.month() and faits_date.day() < entree_date.day()):
                years_of_service -= 1
            return years_of_service
        except Exception as e:
            print(f"Erreur lors du calcul des années de service : {str(e)}")
            return 0

    def on_unit_search(self):
        """Ouvre une boîte de dialogue pour rechercher une unité"""
        dialog = UnitSearchDialog(self)
        if dialog.exec():
            unit_name = dialog.get_selected_unit()
            self.on_unit_selected(unit_name)

    def on_region_change(self, region):
        self.update_subdivision(region, "")
        self.update_legion(region, self.subdivision.currentText(), "")

    def on_subdivision_change(self, subdivision):
        self.update_legion(self.region.currentText(), subdivision, "")

    def on_legion_change(self, legion):
        # Aucune action supplémentaire nécessaire ici
        pass

    def get_form_data(self) -> dict:
        """
        Récupère toutes les données du formulaire
        Returns:
            dict: Dictionnaire contenant toutes les données du formulaire
        """
        from src.utils.date_utils import convert_for_db  # Pour la conversion des dates

        try:
            ##### POUR LES DEBUGS #################################################
            # Debug de la date d'entrée
            print("\nDEBUG date_entree_gie:")
            print(f"Type du widget date_entree_gie: {type(self.date_entree_gie)}")
            print(f"Valeur brute date_entree_gie: {self.date_entree_gie.text()}")

            # Pour QLineEdit
            if isinstance(self.date_entree_gie, QLineEdit):
                date_str = self.date_entree_gie.text().strip()
                print(f"Contenu du QLineEdit: {date_str}")
                print(f"Type du contenu: {type(date_str)}")
                # Utilisation directe de adapt_date
                #from src.utils.date_utils import adapt_date
                date_converted = adapt_date(date_str)
                print(f"Date après adapt_date: {date_converted}")
                print(f"Type après adapt_date: {type(date_converted)}")

            # Si c'est un autre type de widget
            else:
                print(
                    f"Contenu du widget: {self.date_entree_gie.text() if hasattr(self.date_entree_gie, 'text') else 'Méthode text() non disponible'}")

            # Récupération de la date après conversion
            date_entree = get_date_value(self.date_entree_gie)
            print(f"Date après get_date_value: {date_entree}")
            print(f"Type après get_date_value: {type(date_entree)}")

            #############################################################

            # Information du dossier
            dossier_data = {
                'id_dossier': f"{self.num_enr.text()}/{self.annee_punition.text()}",
                'matricule_dossier': self.matricule.text(),
                'reference': self.num_dossier.text(),
                'date_enr': get_date_value(self.date_enr),
                'date_faits': get_date_value(self.date_faits),
                'numero_inc': int(self.num_enr.text()) if self.num_enr.text().isdigit() else None,
                'numero_annee': int(self.num_enr.text()) if self.num_enr.text().isdigit() else None,
                'annee_enr': int(self.annee_punition.text()) if self.annee_punition.text().isdigit() else None,
                'libelle': self.libelle.toPlainText().strip()
            }

            # Pour le debug
            print("Date d'enregistrement avant insertion:", dossier_data['date_enr'])

            # Informations du gendarme
            gendarme_data = {
                'matricule': self.matricule.text().strip(),
                'nom_prenoms': f"{self.nom.text().strip()} {self.prenoms.text().strip()}",
                'sexe': self.sexe.currentText(),
                'age': self.age.value(),
                'date_entree_gie': adapt_date(self.date_entree_gie.text().strip()),
                'annee_service': self.annee_service.value(),
                'nb_enfants': self.nb_enfants.value(),
                'lieu_naissance': self.lieu_naissance.text().strip()
            }

            ###########################################DEBUG############
            print(f"Date finale dans gendarme_data: {gendarme_data['date_entree_gie']}")
            print(f"Type final dans gendarme_data: {type(gendarme_data['date_entree_gie'])}\n")
            ##########################################################

            # Debug des valeurs avant la récupération des IDs
            print("Valeurs sélectionnées dans les combobox:")
            print(f"Situation matrimoniale: {self.situation_matrimoniale.currentText()}")
            print(f"Unité: {self.unite.currentText()}")
            print(f"Légion: {self.legion.currentText()}")
            print(f"Subdivision: {self.subdivision.currentText()}")
            print(f"Région: {self.region.currentText()}")
            print(f"Type sanction: {self.type_sanction.currentText()}")

            # IDs des références (clés étrangères)
            foreign_keys = {
                'grade_id': self.combo_handler.get_selected_id(self.grade),
                'situation_mat_id': self.combo_handler.get_selected_id(self.situation_matrimoniale),
                'unite_id': self.combo_handler.get_selected_id(self.unite),
                'legion_id': self.combo_handler.get_selected_id(self.legion),
                'subdiv_id': self.combo_handler.get_selected_id(self.subdivision),
                'rg_id': self.combo_handler.get_selected_id(self.region),
                'faute_id': self.combo_handler.get_selected_id(self.faute_commise),
                'statut_id': self.combo_handler.get_selected_id(self.statut)
            }

            # Debug des IDs récupérés
            print("IDs récupérés:")
            for key, value in foreign_keys.items():
                print(f"{key}: {value}")

            # Informations de sanction
            sanction_data = {
                'type_sanction_id': self.combo_handler.get_selected_id(
                    self.type_sanction) if self.statut.currentText() == "SANCTIONNE" else None,
                'num_inc': int(self.num_enr.text()) if self.num_enr.text().isdigit() else None,
                'taux': str(self.taux_jar.value()) if self.statut.currentText() == "SANCTIONNE" else "0",
                'numero_decision': self.num_decision.text() if self.type_sanction.currentText() == "RADIATION" else None,
                'numero_arrete': self.num_arrete.text() if self.type_sanction.currentText() == "RADIATION" else None,
                'annee_radiation': int(
                    self.annee_punition.text()) if self.type_sanction.currentText() == "RADIATION" else None,
                'ref_statut': self.ref_statut.text(),
                'comite': self.comite.text()
            }

            # Combinaison de toutes les données
            form_data = {
                'dossier': dossier_data,
                'gendarme': gendarme_data,
                'foreign_keys': foreign_keys,
                'sanction': sanction_data
            }

            return form_data

        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données du formulaire : {str(e)}")
            raise

    def submit_form(self):
        """Enregistre les données du formulaire dans la base de données"""
        try:
            if not self.validate_form():
                return

            # Récupération des données
            try:
                form_data = self.get_form_data()
                print("Données du formulaire:", form_data)  # Debug

            except Exception as e:
                logger.error(f"Erreur lors de la récupération des données : {str(e)}")
                QMessageBox.critical(self, "Erreur",
                                     "Erreur lors de la récupération des données du formulaire.")
                return

            # Début de la transaction
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                try:
                    # 1. Insertion/Mise à jour du gendarme
                    cursor.execute("""
                        INSERT OR REPLACE INTO Gendarmes (
                            matricule, nom_prenoms, age, sexe,
                            date_entree_gie, annee_service, nb_enfants
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        form_data['gendarme']['matricule'],
                        form_data['gendarme']['nom_prenoms'],
                        form_data['gendarme']['age'],
                        form_data['gendarme']['sexe'],
                        form_data['gendarme']['date_entree_gie'],
                        form_data['gendarme']['annee_service'],
                        form_data['gendarme']['nb_enfants']
                    ))

                    # 2. Insérer la sanction
                    # Debug :
                    print("Données sanction à insérer:", {
                        'type_sanction_id': form_data['sanction']['type_sanction_id'],
                        'taux': form_data['sanction']['taux'],
                        'comite': form_data['sanction']['comite']
                    })
                    if form_data['sanction']['type_sanction_id']:
                        cursor.execute("""
                            INSERT INTO Sanctions (
                                type_sanction_id, taux, numero_decision, numero_arrete,
                                annee_radiation, ref_statut, comite
                            ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            form_data['sanction']['type_sanction_id'],
                            form_data['sanction']['taux'],
                            form_data['sanction']['numero_decision'],
                            form_data['sanction']['numero_arrete'],
                            form_data['sanction']['annee_radiation'],
                            form_data['sanction']['ref_statut'],
                            form_data['sanction']['comite']
                        ))
                        sanction_id = cursor.lastrowid
                    else:
                        # Si pas de sanction, on crée une entrée par défaut
                        cursor.execute("""
                            INSERT INTO Sanctions (type_sanction_id, taux) 
                            VALUES (?, ?)
                        """, (1, "0"))  # Utiliser un ID de type_sanction par défaut
                        sanction_id = cursor.lastrowid

                    # 3. Insertion du dossier avec toutes les références
                    print("Clés étrangères à insérer:", {
                        'grade_id': form_data['foreign_keys']['grade_id'],
                        'situation_mat_id': form_data['foreign_keys']['situation_mat_id'],
                        'unite_id': form_data['foreign_keys']['unite_id'],
                        'legion_id': form_data['foreign_keys']['legion_id'],
                        'subdiv_id': form_data['foreign_keys']['subdiv_id'],
                        'rg_id': form_data['foreign_keys']['rg_id'],
                        'faute_id': form_data['foreign_keys']['faute_id'],
                        'statut_id': form_data['foreign_keys']['statut_id']
                    })
                    cursor.execute("""
                        INSERT INTO Dossiers (
                            matricule_dossier, id_dossier, reference, date_enr, date_faits,
                            numero_inc, numero_annee, annee_enr, grade_id, situation_mat_id,
                            unite_id, legion_id, subdiv_id, rg_id, faute_id, libelle, 
                            statut_id, sanction_id
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        form_data['dossier']['matricule_dossier'],
                        form_data['dossier']['id_dossier'],
                        form_data['dossier']['reference'],
                        form_data['dossier']['date_enr'],
                        form_data['dossier']['date_faits'],
                        form_data['dossier']['numero_inc'],
                        form_data['dossier']['numero_annee'],
                        form_data['dossier']['annee_enr'],
                        form_data['foreign_keys']['grade_id'],
                        form_data['foreign_keys']['situation_mat_id'],
                        form_data['foreign_keys']['unite_id'],
                        form_data['foreign_keys']['legion_id'],
                        form_data['foreign_keys']['subdiv_id'],
                        form_data['foreign_keys']['rg_id'],
                        form_data['foreign_keys']['faute_id'],
                        form_data['dossier']['libelle'],
                        form_data['foreign_keys']['statut_id'],
                        sanction_id
                    ))

                    conn.commit()

                    QMessageBox.information(self, "Succès", "Dossier enregistré avec succès!")
                    self.case_added.emit()
                    self.close()

                except sqlite3.IntegrityError as e:
                    conn.rollback()
                    print(f"Erreur détaillée : {str(e)}")  # Debug
                    QMessageBox.critical(self, "Erreur",
                                         f"Erreur d'intégrité de la base de données: {str(e)}")
                    logger.error(f"Erreur d'intégrité : {str(e)}")

                except Exception as e:
                    conn.rollback()
                    print(f"Erreur détaillée : {str(e)}")  # Debug
                    QMessageBox.critical(self, "Erreur",
                                         f"Erreur lors de l'enregistrement : {str(e)}")
                    logger.error(f"Erreur lors de l'enregistrement : {str(e)}")

        except Exception as e:
            QMessageBox.critical(self, "Erreur",
                                 f"Erreur inattendue : {str(e)}")
            logger.error(f"Erreur inattendue : {str(e)}")

    def show_new_case_form(self):
        form = NewCaseForm(self.db_manager)
        form.case_added.connect(StatistiquesWindow.update_trends)  # Connexion du signal
        form.show()

    def validate_form(self):
        """
        Valide les champs obligatoires du formulaire et leur format
        Returns:
            bool: True si tous les champs obligatoires sont remplis et valides
        """
        # 1. Validation des champs obligatoires
        required_fields = {
            'Matricule': (self.matricule, QLineEdit),
            'Nom': (self.nom, QLineEdit),
            'Prénoms': (self.prenoms, QLineEdit),
            #'Date de naissance': (self.date_naissance, QLineEdit),
            #'Lieu de naissance': (self.lieu_naissance, QLineEdit),  # Ajout du lieu de naissance
            'Date des faits': (self.date_faits, QDateEdit),
            'Grade': (self.grade, QComboBox),
            'Unité': (self.unite, QComboBox),
            'Légion': (self.legion, QComboBox),
            'Subdivision': (self.subdivision, QComboBox),
            'Région': (self.region, QComboBox),
            'Faute commise': (self.faute_commise, QComboBox),
            #'Libellé': (self.libelle, QTextEdit),  # Ajout du libellé
            'Statut': (self.statut, QComboBox)
        }

        for field_name, (field, field_type) in required_fields.items():
            if field_type == QLineEdit and not field.text().strip():
                QMessageBox.warning(self, "Champs manquants",
                                    f"Le champ '{field_name}' est obligatoire.")
                field.setFocus()
                return False
            elif field_type == QComboBox and not field.currentText():
                QMessageBox.warning(self, "Champs manquants",
                                    f"Le champ '{field_name}' est obligatoire.")
                field.setFocus()
                return False
            elif field_type == QDateEdit and not field.date().isValid():
                QMessageBox.warning(self, "Date invalide",
                                    f"La {field_name} n'est pas valide.")
                field.setFocus()
                return False

        # 2. Validation du format du matricule
        if not self.matricule.text().isdigit():
            QMessageBox.warning(self, "Format invalide",
                                "Le matricule doit contenir uniquement des chiffres.")
            self.matricule.setFocus()
            return False

        # 3. Validation des dates
        date_faits = self.date_faits.date()
        date_enr = self.date_enr.date()

        if date_faits > date_enr:
            QMessageBox.warning(self, "Dates invalides",
                                "La date des faits ne peut pas être postérieure à la date d'enregistrement.")
            self.date_faits.setFocus()
            return False

        # 4. Validation spécifique pour le statut "RADIE"
        if self.statut.currentText() == "RADIE":
            radiation_fields = {
                'Numéro de décision': self.num_decision,
                'Numéro d\'arrêté': self.num_arrete,
                'Référence du statut': self.ref_statut
            }

            for field_name, field in radiation_fields.items():
                if not field.text().strip():
                    QMessageBox.warning(self, "Champs manquants",
                                        f"Pour une radiation, le champ '{field_name}' est obligatoire.")
                    field.setFocus()
                    return False

        # 5. Validation des valeurs numériques
        numeric_fields = {
            'Âge': (self.age, 18, 65),
            'Années de service': (self.annee_service, 0, 40),
            'Nombre d\'enfants': (self.nb_enfants, 0, 99),
            'Taux (JAR)': (self.taux_jar, 0, 365)
        }

        for field_name, (field, min_val, max_val) in numeric_fields.items():
            if not (min_val <= field.value() <= max_val):
                QMessageBox.warning(self, "Valeur invalide",
                                    f"La valeur du champ '{field_name}' doit être entre {min_val} et {max_val}.")
                field.setFocus()
                return False

        # 6. Vérification de l'unicité de la référence
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Dossiers WHERE reference = ?",
                           (self.num_dossier.text(),))
            if cursor.fetchone()[0] > 0:
                QMessageBox.warning(self, "Référence existante",
                                    f"La référence {self.num_dossier.text()} existe déjà.")
                self.num_dossier.setFocus()
                return False

        # 7. Validation de la longueur du libellé
        libelle_text = self.libelle.toPlainText().strip()
        if len(libelle_text) < 10:  # Par exemple, minimum 10 caractères
            QMessageBox.warning(self, "Libellé trop court",
                                "Le libellé doit contenir une description détaillée de la faute (minimum 10 caractères).")
            self.libelle.setFocus()
            return False

        # 8. Validation du type de sanction si le statut est 'SANCTIONNE'
        if self.statut.currentText() == "SANCTIONNE" and not self.type_sanction.currentText():
            QMessageBox.warning(self, "Champs manquants",
                                "Veuillez sélectionner un type de sanction.")
            self.type_sanction.setFocus()
            return False

        # 9. Validation spécifique pour les sanctions
        if self.statut.currentText() == "SANCTIONNE":
            if not self.type_sanction.currentText():
                QMessageBox.warning(self, "Champs manquants",
                                    "Le type de sanction est obligatoire pour un dossier sanctionné.")
                self.type_sanction.setFocus()
                return False

            if not self.taux_jar.value():
                QMessageBox.warning(self, "Champs manquants",
                                    "Le taux (JAR) est obligatoire pour un dossier sanctionné.")
                self.taux_jar.setFocus()
                return False

        return True

    def get_gendarme_id(self, matricule):
        """
        Récupère l'ID du gendarme à partir de son matricule
        Args:
            matricule: Matricule du gendarme
        Returns:
            int: ID du gendarme
        """
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM gendarmes_etat WHERE matricule = ?", (matricule,))
            result = cursor.fetchone()
            if result:
                return result[0]
            raise ValueError(f"Gendarme avec matricule {matricule} non trouvé")




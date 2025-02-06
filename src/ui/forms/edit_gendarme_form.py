import sqlite3
from datetime import datetime

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QFrame, QPushButton, QScrollArea, QLineEdit,
                             QFormLayout, QComboBox, QSpinBox, QDateEdit, QMessageBox,
                             QDialog, QGraphicsOpacityEffect, QApplication)
from PyQt6.QtCore import Qt, QDate, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QTimer, QSize
from PyQt6.QtGui import QFont, QColor, QIcon

from src.data.gendarmerie import STRUCTURE_PRINCIPALE
from src.data.gendarmerie.utilities import FAULT_ITEMS, MATRIMONIAL_ITEMS, RANKS_ITEMS, GENDER_ITEMS, STATUT_ITEMS
from src.ui.styles.styles import Styles

#Recherche d'unite

class SearchUniteDialog:
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Rechercher par unité")
        self.setMinimumWidth(300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Combo pour choisir l'unité
        self.unite_combo = QComboBox()
        self.unite_combo.setEditable(True)  # Permet la saisie libre
        self.unite_combo.setPlaceholderText("Entrez ou sélectionnez une unité")

        # Remplir avec toutes les unités disponibles
        all_unites = set()
        for region_data in STRUCTURE_PRINCIPALE["REGIONS"].values():
            for legion_data in region_data.values():
                if isinstance(legion_data, list):
                    all_unites.update(legion_data)
                else:
                    for cie_unites in legion_data.values():
                        all_unites.update(cie_unites)

        self.unite_combo.addItems(sorted(all_unites))
        layout.addWidget(self.unite_combo)

        # Boutons
        button_layout = QHBoxLayout()
        self.search_button = QPushButton("Rechercher")
        self.cancel_button = QPushButton("Annuler")

        self.search_button.setStyleSheet("""
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

        self.cancel_button.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                background-color: #e0e0e0;
                color: #333;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
        """)

        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.search_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Connexions
        self.search_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def get_unite(self):
        return self.unite_combo.currentText()

class SearchDossierDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("Recherche du dossier à modifier")
        self.setMinimumWidth(400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Titre
        title = QLabel("Recherche par matricule et numéro de dossier")
        title.setFont(QFont('Helvetica', 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #1976d2; margin-bottom: 20px;")
        layout.addWidget(title)

        # Champ de saisie du matricule
        self.matricule_input = QLineEdit()
        self.matricule_input.setPlaceholderText("Entrez le matricule")
        self.matricule_input.setStyleSheet("""
            QLineEdit {
                padding: 12px 20px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background: white;
                font-size: 16px;
                color: #333;
            }
            QLineEdit:focus {
                border-color: #2196f3;
                background: #f1f4f8;
            }
        """)
        layout.addWidget(self.matricule_input)

        # Champ de saisie du numéro de dossier
        self.num_dossier_input = QLineEdit()
        self.num_dossier_input.setPlaceholderText("Entrez le numéro de dossier")
        self.num_dossier_input.setStyleSheet("""
            QLineEdit {
                padding: 12px 20px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background: white;
                font-size: 16px;
                color: #333;
            }
            QLineEdit:focus {
                border-color: #2196f3;
                background: #f1f4f8;
            }
        """)
        layout.addWidget(self.num_dossier_input)

        # Boutons
        button_layout = QHBoxLayout()
        self.search_button = QPushButton("Rechercher")
        self.cancel_button = QPushButton("Annuler")

        for btn in [self.search_button, self.cancel_button]:
            btn.setStyleSheet("""
                QPushButton {
                    padding: 10px 20px;
                    border-radius: 5px;
                    font-size: 14px;
                    min-width: 120px;
                }
            """)

        self.search_button.setStyleSheet(self.search_button.styleSheet() + """
            QPushButton {
                background-color: #2196f3;
                color: white;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
        """)

        self.cancel_button.setStyleSheet(self.cancel_button.styleSheet() + """
            QPushButton {
                background-color: #e0e0e0;
                color: #333;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
        """)

        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.search_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Connexions
        self.search_button.clicked.connect(self.validate_and_accept)
        self.cancel_button.clicked.connect(self.reject)
        self.matricule_input.returnPressed.connect(self.validate_and_accept)
        self.num_dossier_input.returnPressed.connect(self.validate_and_accept)

    def validate_and_accept(self):
        """Valide les champs et recherche le dossier"""
        matricule = self.matricule_input.text().strip()
        num_dossier = self.num_dossier_input.text().strip()

        if not matricule or not num_dossier:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer un matricule et un numéro de dossier.")
            return

        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                # Vérifier dans la table main_tab
                cursor.execute("""
                    SELECT * 
                    FROM main_tab 
                    WHERE matricule = ? AND numero_dossier = ?
                """, (matricule, num_dossier))

                result = cursor.fetchone()

                if result:
                    self.accept()
                else:
                    QMessageBox.warning(self, "Erreur",
                                        f"Aucun dossier trouvé pour le matricule {matricule} et le numéro de dossier {num_dossier}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur",
                                 f"Erreur lors de la recherche : {str(e)}")
            print(f"Erreur détaillée : {str(e)}")

    def get_matricule(self):
        return self.matricule_input.text().strip()

    def get_num_dossier(self):
        return self.num_dossier_input.text().strip()


class EditCaseForm(QMainWindow):
    def __init__(self, matricule, num_dossier, db_manager):
        super().__init__()
        self.matricule = matricule
        self.num_dossier = num_dossier
        self.db_manager = db_manager
        self.setWindowTitle(f"Modification du dossier {num_dossier} - Matricule {matricule}")
        self.setMinimumSize(1200, 800)
        self.is_dark_mode = False
        self.current_section = 0
        self.init_ui()
        self.load_data()

    def create_form_row(self, label_text, widget, with_info=False):
        """Crée une ligne de formulaire avec label et widget"""
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(10)

        label = QLabel(label_text)
        label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #333;
                padding: 8px 0;
                min-width: 200px;
            }
        """)
        row_layout.addWidget(label)
        row_layout.addWidget(widget)

        if with_info:
            info_icon = QPushButton("ℹ️")
            info_icon.setToolTip("Information complémentaire")
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
        title = QLabel(f"Modification du Dossier {self.num_dossier} - Matricule: {self.matricule}")
        title.setFont(QFont('Helvetica', 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #FFFFFF; margin-bottom: 20px;")
        layout.addWidget(title)

        # Conteneur des sections
        self.sections_container = QWidget()
        sections_layout = QHBoxLayout(self.sections_container)
        sections_layout.setSpacing(20)

        # Les trois sections
        self.section1 = self.create_section("📝 Informations du Dossier", "Numéro, dates et détails administratifs")
        self.section2 = self.create_section("👤 Informations du Mis en Cause", "Identité et affectation du gendarme")
        self.section3 = self.create_section("⚖️ Informations sur la Faute", "Nature et détails de la sanction")

        sections_layout.addWidget(self.section1)
        sections_layout.addWidget(self.section2)
        sections_layout.addWidget(self.section3)

        layout.addWidget(self.sections_container)

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

        # État initial
        self.prev_button.setVisible(False)
        self.submit_button.setVisible(False)
        self.update_navigation()

        # Connexions
        self.prev_button.clicked.connect(self.previous_section)
        self.next_button.clicked.connect(self.next_section)
        self.submit_button.clicked.connect(self.submit_form)

    def create_section(self, title, subtitle=""):
        section = QFrame()
        section.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 10px;
                padding: 20px;
            }
            QFrame:hover {
                border: 1px solid #d1d1d1
            }
        """)

        layout = QVBoxLayout(section)

        # Titre avec icône
        title_label = QLabel(title)
        title_label.setFont(QFont('Helvetica', 18, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #1976d2; margin-bottom: 5px;")
        layout.addWidget(title_label)

        # Création du contenu selon le type de section
        if title.startswith("📝"):  # Section Info Dossier
            content = self.create_case_info_section()
        elif title.startswith("👤"):  # Section Info Mis en cause
            content = self.create_suspect_info_section()
        else:  # Section Info Faute
            content = self.create_fault_info_section()

        layout.addWidget(content)
        layout.addStretch()
        return section

    def create_case_info_section(self):
        """Crée la section des informations du dossier (table main_tab)"""
        container = QWidget()
        layout = QFormLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        styles = Styles.get_styles(self.is_dark_mode)

        # Numéro de dossier
        self.num_dossier = QLineEdit()
        self.num_dossier.setPlaceholderText("Entrez le N° de dossier")
        self.num_dossier.setStyleSheet(styles['INPUT'])
        layout.addRow(self.create_form_row("N° Dossier", self.num_dossier))

        # Année de punition
        self.annee_punition = QLineEdit()
        self.annee_punition.setReadOnly(True)
        self.annee_punition.setStyleSheet(styles['INPUT'] + """
            QLineEdit:read-only {
                background: #f5f5f5;
                color: #666;
            }
        """)
        layout.addRow(self.create_form_row("Année de punition", self.annee_punition))

        # Date d'enregistrement
        self.date_enr = QDateEdit()
        self.date_enr.setCalendarPopup(True)
        self.date_enr.setDate(QDate.currentDate())
        self.date_enr.setStyleSheet(styles['DATE_EDIT'])
        layout.addRow(self.create_form_row("Date d'enregistrement", self.date_enr))

        # Numéro d'ordre
        self.numero_ordre = QLineEdit()
        self.numero_ordre.setPlaceholderText("Numéro d'ordre")
        self.numero_ordre.setStyleSheet(styles['INPUT'])
        layout.addRow(self.create_form_row("N° d'ordre", self.numero_ordre))

        container.setLayout(layout)
        return container

    def create_suspect_info_section(self):
        """Crée la section des informations du mis en cause (table main_tab)"""
        container = QWidget()
        layout = QFormLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        styles = Styles.get_styles(self.is_dark_mode)

        # Matricule (mle)
        self.matricule_field = QLineEdit()
        self.matricule_field.setReadOnly(True)
        self.matricule_field.setStyleSheet(styles['INPUT'] + """
            QLineEdit:read-only {
                background: #f5f5f5;
                color: #666;
            }
        """)
        layout.addRow(self.create_form_row("Matricule", self.matricule_field))

        # Nom et prénoms (un seul champ)
        self.nom_prenoms = QLineEdit()
        self.nom_prenoms.setStyleSheet(styles['INPUT'])
        self.nom_prenoms.setPlaceholderText("Nom et Prénoms")
        layout.addRow(self.create_form_row("Nom et Prénoms", self.nom_prenoms))

        # Grade
        self.grade = QComboBox()
        self.grade.addItems(RANKS_ITEMS)
        self.grade.setStyleSheet(styles['COMBO_BOX'])
        layout.addRow(self.create_form_row("Grade", self.grade))

        # Sexe
        self.sexe = QComboBox()
        self.sexe.addItems(GENDER_ITEMS)
        self.sexe.setStyleSheet(styles['COMBO_BOX'])
        layout.addRow(self.create_form_row("Sexe", self.sexe))

        # Date de naissance
        self.date_naissance = QDateEdit()
        self.date_naissance.setCalendarPopup(True)
        self.date_naissance.setStyleSheet(styles['DATE_EDIT'])
        layout.addRow(self.create_form_row("Date de naissance", self.date_naissance))

        # Age
        self.age = QSpinBox()
        self.age.setRange(18, 65)
        self.age.setStyleSheet(styles['SPIN_BOX'])
        layout.addRow(self.create_form_row("Age", self.age))

        # Structure
        self.type_affectation = QComboBox()
        self.type_affectation.addItems(["REGIONS", "CSG"])
        self.type_affectation.setStyleSheet(styles['COMBO_BOX'])
        self.type_affectation.currentTextChanged.connect(self.on_affectation_change)
        layout.addRow(self.create_form_row("Type d'affectation", self.type_affectation))

        self.regions = QComboBox()
        self.regions.setStyleSheet(styles['COMBO_BOX'])
        self.regions.currentTextChanged.connect(self.on_region_change)
        layout.addRow(self.create_form_row("Région", self.regions))

        self.legions = QComboBox()
        self.legions.setStyleSheet(styles['COMBO_BOX'])
        self.legions.currentTextChanged.connect(self.on_legion_change)
        layout.addRow(self.create_form_row("Légion", self.legions))

        self.unite = QComboBox()
        self.unite.setStyleSheet(styles['COMBO_BOX'])
        # Création du layout horizontal pour l'unité et le bouton
        unite_layout = QHBoxLayout()
        unite_layout.addWidget(self.unite)

        # Ajout du bouton de recherche
        search_button = QPushButton()
        search_button.setIcon(QIcon("../resources/icons/search.png"))
        search_button.setIconSize(QSize(16, 16))
        search_button.setToolTip("Rechercher région/légion par unité")
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

        print("Connexion du bouton de recherche")  # Debug
        search_button.clicked.connect(self.on_unite_search)
        unite_layout.addWidget(search_button)

        # Ajout au layout principal avec le widget container
        unite_container = QWidget()
        unite_container.setLayout(unite_layout)
        layout.addRow(self.create_form_row("Unité", unite_container))

        # Informations supplémentaires
        self.subdiv = QLineEdit()
        self.subdiv.setStyleSheet(styles['INPUT'])
        layout.addRow(self.create_form_row("Subdivision", self.subdiv))

        self.date_entree_gie = QDateEdit()
        self.date_entree_gie.setCalendarPopup(True)
        self.date_entree_gie.setStyleSheet(styles['DATE_EDIT'])
        layout.addRow(self.create_form_row("Date d'entrée GIE", self.date_entree_gie))

        self.annee_service = QSpinBox()
        self.annee_service.setRange(0, 40)
        self.annee_service.setStyleSheet(styles['SPIN_BOX'])
        layout.addRow(self.create_form_row("Années de service", self.annee_service))

        self.situation_matrimoniale = QComboBox()
        self.situation_matrimoniale.addItems(MATRIMONIAL_ITEMS)
        self.situation_matrimoniale.setStyleSheet(styles['COMBO_BOX'])
        layout.addRow(self.create_form_row("Situation matrimoniale", self.situation_matrimoniale))

        self.nb_enfants = QSpinBox()
        self.nb_enfants.setRange(0, 20)
        self.nb_enfants.setStyleSheet(styles['SPIN_BOX'])
        layout.addRow(self.create_form_row("Nombre d'enfants", self.nb_enfants))

        container.setLayout(layout)
        return container

    def create_fault_info_section(self):
        """Crée la section des informations sur la faute (table main_tab)"""
        container = QWidget()
        layout = QFormLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        styles = Styles.get_styles(self.is_dark_mode)

        # Date des faits
        self.date_faits = QDateEdit()
        self.date_faits.setCalendarPopup(True)
        self.date_faits.setDate(QDate.currentDate())
        self.date_faits.dateChanged.connect(self.update_annee_faits)
        self.date_faits.setStyleSheet(styles['DATE_EDIT'])
        layout.addRow(self.create_form_row("Date des faits", self.date_faits))

        # Faute commise
        self.faute_commise = QComboBox()
        self.faute_commise.addItems(FAULT_ITEMS)
        self.faute_commise.setStyleSheet(styles['COMBO_BOX'])
        layout.addRow(self.create_form_row("Faute commise", self.faute_commise))

        # Catégorie (INTEGER)
        self.categorie = QSpinBox()
        self.categorie.setRange(1, 10)
        self.categorie.setStyleSheet(styles['SPIN_BOX'])
        layout.addRow(self.create_form_row("Catégorie", self.categorie))

        # Statut
        self.statut = QComboBox()
        self.statut.addItems(STATUT_ITEMS)
        self.statut.currentTextChanged.connect(self.on_statut_change)
        self.statut.setStyleSheet(styles['COMBO_BOX'])
        layout.addRow(self.create_form_row("Statut du dossier", self.statut))

        # Référence du statut (visible uniquement si RADIE)
        self.ref_statut = QLineEdit()
        self.ref_statut.setStyleSheet(styles['INPUT'])
        self.ref_statut.setPlaceholderText("Référence de radiation")
        self.ref_statut_container = QWidget()
        layout.addRow(self.create_form_row("Référence du statut", self.ref_statut))
        self.ref_statut_container.setVisible(False)

        # TAUX (JAR) - TEXT
        self.taux_jar = QLineEdit()
        self.taux_jar.setStyleSheet(styles['INPUT'])
        self.taux_jar.setPlaceholderText("Nombre de jours d'arrêt de rigueur")
        layout.addRow(self.create_form_row("TAUX (JAR)", self.taux_jar))

        # COMITE - INTEGER
        self.comite = QSpinBox()
        self.comite.setRange(0, 100)
        self.comite.setStyleSheet(styles['SPIN_BOX'])
        layout.addRow(self.create_form_row("COMITE", self.comite))

        # ANNEE DES FAITS (calculée automatiquement)
        self.annee_faits = QLineEdit()
        self.annee_faits.setReadOnly(True)
        self.annee_faits.setStyleSheet(styles['INPUT'] + """
            QLineEdit:read-only {
                background: #f5f5f5;
                color: #666;
            }
        """)
        layout.addRow(self.create_form_row("ANNEE DES FAITS", self.annee_faits))

        container.setLayout(layout)
        return container

    def switch_section(self, index):
        """Gère la transition entre les sections"""
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        for i, section in enumerate([self.section1, self.section2, self.section3]):
            animation_group = QParallelAnimationGroup()

            size_animation = QPropertyAnimation(section, b"maximumWidth")
            size_animation.setDuration(1800)
            size_animation.setEasingCurve(QEasingCurve.Type.InOutQuint)

            if i == index:
                size_animation.setStartValue(section.width())
                size_animation.setEndValue(section.width() * 2.2)
                section.setStyleSheet("""
                        QFrame {
                            background: white;
                            border-radius: 10px;
                            padding: 20px;
                            border: 1px solid #2196f3;
                            opacity: 1;
                            z-index: 1000;
                            position: relative;
                        }
                    """)
                section.raise_()
            else:
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
                section.lower()

            animation_group.addAnimation(size_animation)

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

            animation_group.addAnimation(opacity_animation)

            if i == index:
                position_animation = QPropertyAnimation(section, b"geometry")
                position_animation.setDuration(300)
                position_animation.setEasingCurve(QEasingCurve.Type.InOutQuint)
                position_animation.setStartValue(section.geometry())
                position_animation.setEndValue(section.geometry().adjusted(0, -10, 0, -10))
                animation_group.addAnimation(position_animation)

            animation_group.start()

        QTimer.singleShot(1800, lambda: QApplication.restoreOverrideCursor())

    def update_navigation(self):
        """Met à jour l'affichage des boutons de navigation"""
        self.prev_button.setVisible(self.current_section > 0)
        self.next_button.setVisible(self.current_section < 2)
        self.submit_button.setVisible(self.current_section == 2)

    def previous_section(self):
        """Passe à la section précédente"""
        if self.current_section > 0:
            self.current_section -= 1
            self.switch_section(self.current_section)
            self.update_navigation()

    def next_section(self):
        """Passe à la section suivante"""
        if self.current_section < 2:
            self.current_section += 1
            self.switch_section(self.current_section)
            self.update_navigation()

    def update_annee_faits(self):
        """Met à jour l'année des faits automatiquement"""
        self.annee_faits.setText(str(self.date_faits.date().year()))

    def on_affectation_change(self, affectation_type):
        """Met à jour les choix de région selon le type d'affectation"""
        self.regions.clear()
        self.legions.clear()
        self.unite.clear()

        if affectation_type == "REGIONS":
            regions = STRUCTURE_PRINCIPALE["REGIONS"].keys()
            self.regions.addItems(regions)
        else:  # CSG
            directions = STRUCTURE_PRINCIPALE["CSG"].keys()
            self.regions.addItems(directions)

        if hasattr(self, '_stored_direction') and self._stored_direction:
            index = self.regions.findText(self._stored_direction)
            if index >= 0:
                self.regions.setCurrentIndex(index)

    def on_region_change(self, region):
        """Met à jour les choix de légion selon la région"""
        self.legions.clear()
        self.unite.clear()

        affectation_type = self.type_affectation.currentText()
        if affectation_type == "REGIONS":
            if region in STRUCTURE_PRINCIPALE["REGIONS"]:
                legions = STRUCTURE_PRINCIPALE["REGIONS"][region].keys()
                self.legions.addItems(legions)
        else:  # CSG
            if region in STRUCTURE_PRINCIPALE["CSG"]:
                services = STRUCTURE_PRINCIPALE["CSG"][region]
                if services:
                    self.legions.addItems(services)

        if hasattr(self, '_stored_service') and self._stored_service:
            index = self.legions.findText(self._stored_service)
            if index >= 0:
                self.legions.setCurrentIndex(index)

    def on_legion_change(self, legion):
        """Met à jour les choix d'unité selon la légion"""
        self.unite.clear()

        affectation_type = self.type_affectation.currentText()
        region = self.regions.currentText()

        if affectation_type == "REGIONS" and region in STRUCTURE_PRINCIPALE["REGIONS"]:
            legion_data = STRUCTURE_PRINCIPALE["REGIONS"][region]
            if legion in legion_data:
                unites = []
                service_data = legion_data[legion]

                if isinstance(service_data, list):
                    unites = service_data
                else:
                    for cie, cie_unites in service_data.items():
                        unites.extend(cie_unites)

                self.unite.addItems(unites)

        if hasattr(self, '_stored_unite') and self._stored_unite:
            index = self.unite.findText(self._stored_unite)
            if index >= 0:
                self.unite.setCurrentIndex(index)

    def on_statut_change(self, statut):
        """Gère l'affichage du champ référence selon le statut"""
        self.ref_statut.setVisible(statut == "RADIE")

    def validate_form(self):
        """Valide les champs obligatoires du formulaire"""
        try:
            required_fields = {
                'Numéro de dossier': self.num_dossier.text(),
                'Date des faits': self.date_faits.date().toString("yyyy-MM-dd"),
                'Faute commise': self.faute_commise.currentText(),
                'Catégorie': self.categorie.value(),
                'Statut': self.statut.currentText(),
            }

            for field_name, value in required_fields.items():
                if not value or not str(value).strip():
                    QMessageBox.warning(self, "Champs manquants",
                                        f"Le champ '{field_name}' est obligatoire.")
                    return False

            if self.statut.currentText() == "RADIE" and not self.ref_statut.text().strip():
                QMessageBox.warning(self, "Champs manquants",
                                    "La référence du statut est obligatoire pour une radiation.")
                self.ref_statut.setFocus()
                return False

            try:
                if self.taux_jar.text().strip():
                    float(self.taux_jar.text())
            except ValueError:
                QMessageBox.warning(self, "Erreur de format",
                                    "Le taux JAR doit être un nombre.")
                self.taux_jar.setFocus()
                return False

            return True

        except Exception as e:
            QMessageBox.critical(self, "Erreur",
                                 f"Erreur lors de la validation : {str(e)}")
            return False

    def load_data(self):
        """Charge les données existantes du dossier"""
        try:
            with self.db_manager.get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # Charger les données de la table main_tab
                cursor.execute("""
                    SELECT * FROM main_tab 
                    WHERE matricule = ? AND numero_dossier = ?
                """, (self.matricule, self.num_dossier))
                main_sanction_data = cursor.fetchone()

                if main_sanction_data:
                    main_dict = dict(main_sanction_data)

                    # Section 1 : Informations du Dossier (depuis main_tab)
                    self.num_dossier.setText(str(main_dict.get('numero_dossier', '')))
                    self.annee_punition.setText(str(main_dict.get('annee_punition', '')))

                    # Gestion de la date d'enregistrement
                    date_enr = str(main_dict.get('date_enr', ''))
                    if date_enr:
                        try:
                            self.date_enr.setDate(QDate.fromString(date_enr, "yyyy-MM-dd"))
                        except Exception as e:
                            print(f"Erreur lors de la conversion de la date d'enregistrement: {e}")

                    self.numero_ordre.setText(str(main_dict.get('numero_ordre', '')))

                    # Section 2 : Informations du Mis en Cause
                    self.matricule_field.setText(main_dict.get('matricule', ''))
                    self.nom_prenoms.setText(main_dict.get('nom_prenoms', ''))

                    # Valeurs numériques depuis main_tab
                    try:
                        # Age
                        age_value = main_dict.get('age')
                        self.age.setValue(int(age_value) if age_value is not None else 0)

                        # Nombre d'enfants
                        nb_enfants_value = main_dict.get('nb_enfants')
                        self.nb_enfants.setValue(int(nb_enfants_value) if nb_enfants_value is not None else 0)

                        # Années de service
                        annee_service_value = main_dict.get('annee_service')
                        self.annee_service.setValue(
                            int(annee_service_value) if annee_service_value is not None else 0)
                    except (ValueError, TypeError) as e:
                        print(f"Erreur de conversion des valeurs numériques gendarmes: {str(e)}")

                    # Gestion des ComboBox
                    self.grade.setCurrentText(main_dict.get('grade', ''))
                    self.sexe.setCurrentText(main_dict.get('sexe', ''))

                    # Gestion de la date de naissance
                    date_naissance = str(main_dict.get('date_naissance', ''))
                    if date_naissance:
                        try:
                            self.date_naissance.setDate(QDate.fromString(date_naissance, "yyyy-MM-dd"))
                        except Exception as e:
                            print(f"Erreur lors de la conversion de la date de naissance: {e}")

                    # Chargement direct de la structure sans passer par la hiérarchie
                    self.type_affectation.blockSignals(True)
                    self.regions.blockSignals(True)
                    self.legions.blockSignals(True)
                    self.unite.blockSignals(True)

                    # Récupérer les valeurs existantes
                    current_region = main_dict.get('regions', '')
                    current_legion = main_dict.get('legions', '')
                    current_unite = main_dict.get('unite', '')

                    # Ajouter les valeurs existantes si elles ne sont pas dans les listes
                    if current_region and current_region not in [self.regions.itemText(i) for i in
                                                                 range(self.regions.count())]:
                        self.regions.addItem(current_region)
                    if current_legion and current_legion not in [self.legions.itemText(i) for i in
                                                                 range(self.legions.count())]:
                        self.legions.addItem(current_legion)
                    if current_unite and current_unite not in [self.unite.itemText(i) for i in
                                                               range(self.unite.count())]:
                        self.unite.addItem(current_unite)

                    # Sélectionner les valeurs
                    self.regions.setCurrentText(current_region)
                    self.legions.setCurrentText(current_legion)
                    self.unite.setCurrentText(current_unite)

                    # Réactiver les signaux
                    self.type_affectation.blockSignals(False)
                    self.regions.blockSignals(False)
                    self.legions.blockSignals(False)
                    self.unite.blockSignals(False)

                    # Informations supplémentaires
                    self.subdiv.setText(str(main_dict.get('subdiv', '')))

                    # Date d'entrée GIE
                    date_entree = str(main_dict.get('date_entree_gie', ''))
                    if date_entree:
                        try:
                            self.date_entree_gie.setDate(QDate.fromString(date_entree, "yyyy-MM-dd"))
                        except Exception as e:
                            print(f"Erreur lors de la conversion de la date d'entrée GIE: {e}")

                    self.situation_matrimoniale.setCurrentText(main_dict.get('situation_matrimoniale', ''))

                    # Section 3 : Informations sur la Faute (depuis main_tab)
                    date_faits = str(main_dict.get('date_faits', ''))
                    if date_faits:
                        try:
                            self.date_faits.setDate(QDate.fromString(date_faits, "yyyy-MM-dd"))
                        except Exception as e:
                            print(f"Erreur lors de la conversion de la date des faits: {e}")

                    self.faute_commise.setCurrentText(main_dict.get('faute_commise', ''))

                    # Conversion de la catégorie
                    try:
                        categorie_value = main_dict.get('categorie')
                        self.categorie.setValue(int(categorie_value) if categorie_value is not None else 1)
                    except (ValueError, TypeError) as e:
                        print(f"Erreur de conversion de la catégorie: {str(e)}")
                        self.categorie.setValue(1)

                    self.statut.setCurrentText(main_dict.get('statut', ''))
                    self.ref_statut.setText(main_dict.get('reference_statut', ''))
                    self.taux_jar.setText(str(main_dict.get('taux_jar', '')))

                    # Conversion du comité
                    try:
                        comite_value = main_dict.get('comite')
                        self.comite.setValue(int(comite_value) if comite_value is not None else 0)
                    except (ValueError, TypeError) as e:
                        print(f"Erreur de conversion du comité: {str(e)}")
                        self.comite.setValue(0)

                    self.annee_faits.setText(str(main_dict.get('annee_faits', '')))

                    # Mise à jour de l'interface selon le statut
                    self.on_statut_change(main_dict.get('statut', ''))

                else:
                    QMessageBox.warning(self, "Erreur",
                                        f"Aucune donnée trouvée pour le matricule {self.matricule} et le numéro de dossier {self.num_dossier}")
                    self.close()

        except Exception as e:
            QMessageBox.critical(self, "Erreur",
                                 f"Erreur lors du chargement des données : {str(e)}")
            print(f"Erreur détaillée : {str(e)}")
            self.close()

    def submit_form(self):
        """Enregistre les modifications dans la base de données"""
        try:
            if not self.validate_form():
                return

            reply = QMessageBox.question(self, "Confirmation",
                                         "Voulez-vous vraiment enregistrer ces modifications ?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.No:
                return

            # Préparation des données
            form_data = {
                # Section Info Dossier (table main_tab)
                'numero_dossier': self.num_dossier.text(),
                'annee_punition': self.annee_punition.text(),
                'numero_ordre': self.numero_ordre.text(),
                'date_enr': self.date_enr.date().toString("yyyy-MM-dd"),
                'matricule': self.matricule,

                # Section Info Mis en cause (table main_tab)
                'nom_prenoms': self.nom_prenoms.text().strip(),
                'grade': self.grade.currentText(),
                'sexe': self.sexe.currentText(),
                'age': self.age.value(),
                'date_naissance': self.date_naissance.date().toString("yyyy-MM-dd"),
                'unite': self.unite.currentText(),
                'legions': self.legions.currentText(),
                'subdiv': self.subdiv.text(),
                'regions': self.regions.currentText(),
                'date_entree_gie': self.date_entree_gie.date().toString("yyyy-MM-dd"),
                'annee_service': self.annee_service.value(),
                'situation_matrimoniale': self.situation_matrimoniale.currentText(),
                'nb_enfants': self.nb_enfants.value(),

                # Section Info Faute (table main_tab)
                'faute_commise': self.faute_commise.currentText(),
                'date_faits': self.date_faits.date().toString("yyyy-MM-dd"),
                'categorie': self.categorie.value(),
                'statut': self.statut.currentText(),
                'reference_statut': self.ref_statut.text() if self.statut.currentText() == "RADIE" else "",
                'taux_jar': self.taux_jar.text(),
                'comite': self.comite.value(),
                'annee_faits': int(self.annee_faits.text())
            }

            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()

                # Mise à jour de la table main_tab
                cursor.execute("""
                    UPDATE main_tab SET
                        numero_dossier = ?,
                        annee_punition = ?,
                        numero_ordre = ?,
                        date_enr = ?,
                        faute_commise = ?,
                        date_faits = ?,
                        categorie = ?,
                        statut = ?,
                        reference_statut = ?,
                        taux_jar = ?,
                        comite = ?,
                        annee_faits = ?,
                        nom_prenoms = ?,
                        grade = ?,
                        sexe = ?,
                        date_naissance = ?,
                        age = ?,
                        unite = ?,
                        legions = ?,
                        subdiv = ?,
                        regions = ?,
                        date_entree_gie = ?,
                        annee_service = ?,
                        situation_matrimoniale = ?,
                        nb_enfants = ?
                    WHERE matricule = ? AND numero_dossier = ?
                """, (
                    form_data['numero_dossier'],
                    form_data['annee_punition'],
                    form_data['numero_ordre'],
                    form_data['date_enr'],
                    form_data['faute_commise'],
                    form_data['date_faits'],
                    form_data['categorie'],
                    form_data['statut'],
                    form_data['reference_statut'],
                    form_data['taux_jar'],
                    form_data['comite'],
                    form_data['annee_faits'],
                    form_data['nom_prenoms'],
                    form_data['grade'],
                    form_data['sexe'],
                    form_data['date_naissance'],
                    form_data['age'],
                    form_data['unite'],
                    form_data['legions'],
                    form_data['subdiv'],
                    form_data['regions'],
                    form_data['date_entree_gie'],
                    form_data['annee_service'],
                    form_data['situation_matrimoniale'],
                    form_data['nb_enfants'],
                    form_data['matricule'],
                    self.num_dossier
                ))

                conn.commit()

                QMessageBox.information(self, "Succès",
                                        "Les modifications ont été enregistrées avec succès!")
                self.close()

        except Exception as e:
            QMessageBox.critical(self, "Erreur",
                                 f"Erreur lors de la mise à jour des données : {str(e)}")
            print(f"Erreur détaillée : {str(e)}")

    def on_unite_search(self):
        """Ouvre une boîte de dialogue pour rechercher une unité"""
        dialog = SearchUniteDialog(self)
        if dialog.exec():
            unite_recherchee = dialog.get_unite()
            if unite_recherchee:
                if not self.search_by_unite(unite_recherchee):
                    QMessageBox.warning(self, "Recherche",
                                        "Aucune correspondance trouvée pour cette unité.")

    def search_by_unite(self, unite_recherchee):
        """Recherche la région et la légion correspondant à une unité"""
        print(f"Recherche de l'unité : {unite_recherchee}")  # Debug

        # Parcourir la structure REGIONS
        for region, region_data in STRUCTURE_PRINCIPALE["REGIONS"].items():
            for legion, legion_data in region_data.items():
                unites = []
                if isinstance(legion_data, list):
                    unites = legion_data
                else:
                    for cie, cie_unites in legion_data.items():
                        unites.extend(cie_unites)

                if unite_recherchee in unites:
                    print(f"Unité trouvée dans {region} / {legion}")  # Debug

                    # Désactiver les signaux pour éviter les mises à jour en cascade
                    self.type_affectation.blockSignals(True)
                    self.regions.blockSignals(True)
                    self.legions.blockSignals(True)
                    self.unite.blockSignals(True)

                    # Mettre à jour type d'affectation
                    self.type_affectation.setCurrentText("REGIONS")

                    # Ajouter et sélectionner la région si elle n'existe pas déjà
                    if region not in [self.regions.itemText(i) for i in range(self.regions.count())]:
                        self.regions.addItem(region)
                    self.regions.setCurrentText(region)

                    # Ajouter et sélectionner la légion si elle n'existe pas déjà
                    if legion not in [self.legions.itemText(i) for i in range(self.legions.count())]:
                        self.legions.addItem(legion)
                    self.legions.setCurrentText(legion)

                    # Ajouter et sélectionner l'unité si elle n'existe pas déjà
                    if unite_recherchee not in [self.unite.itemText(i) for i in range(self.unite.count())]:
                        self.unite.addItem(unite_recherchee)
                    self.unite.setCurrentText(unite_recherchee)

                    # Réactiver les signaux
                    self.type_affectation.blockSignals(False)
                    self.regions.blockSignals(False)
                    self.legions.blockSignals(False)
                    self.unite.blockSignals(False)

                    return True

        # Vérifier aussi dans la structure CSG
        for direction, services in STRUCTURE_PRINCIPALE["CSG"].items():
            if isinstance(services, list) and unite_recherchee in services:
                # Désactiver les signaux
                self.type_affectation.blockSignals(True)
                self.regions.blockSignals(True)
                self.unite.blockSignals(True)

                # Mettre à jour type d'affectation
                self.type_affectation.setCurrentText("CSG")

                # Ajouter et sélectionner la direction si elle n'existe pas déjà
                if direction not in [self.regions.itemText(i) for i in range(self.regions.count())]:
                    self.regions.addItem(direction)
                self.regions.setCurrentText(direction)

                # Ajouter et sélectionner l'unité si elle n'existe pas déjà
                if unite_recherchee not in [self.unite.itemText(i) for i in range(self.unite.count())]:
                    self.unite.addItem(unite_recherchee)
                self.unite.setCurrentText(unite_recherchee)

                # Réactiver les signaux
                self.type_affectation.blockSignals(False)
                self.regions.blockSignals(False)
                self.unite.blockSignals(False)

                return True

        return False


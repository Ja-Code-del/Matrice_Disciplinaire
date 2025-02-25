import sqlite3
from datetime import datetime

from dateutil.relativedelta import relativedelta

from src.utils.date_utils import get_date_value, adapt_date
from src.utils.combobox_handler import ComboBoxHandler
import logging

logger = logging.getLogger(__name__)

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QFrame, QPushButton, QScrollArea, QLineEdit,
                             QFormLayout, QComboBox, QSpinBox, QDateEdit, QMessageBox,
                             QDialog, QGraphicsOpacityEffect, QApplication, QTextEdit)
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
        self.reference_dossier_input = QLineEdit()
        self.reference_dossier_input.setPlaceholderText("Entrez la reférence du dossier")
        self.reference_dossier_input.setStyleSheet("""
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
        layout.addWidget(self.reference_dossier_input)

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
        self.reference_dossier_input.returnPressed.connect(self.validate_and_accept)

    def validate_and_accept(self):
        """Valide les champs et recherche le dossier"""
        matricule = self.matricule_input.text().strip()
        ref_dossier = self.reference_dossier_input.text().strip()

        if not matricule or not ref_dossier:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer un matricule et un numéro de dossier.")
            return

        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                # Vérifier dans la nouvelle structure de la BD
                cursor.execute("""
                    SELECT d.* 
                    FROM Dossiers d
                    JOIN Gendarmes g ON d.matricule_dossier = g.matricule
                    WHERE d.matricule_dossier = ? AND d.reference = ?
                """, (matricule, ref_dossier))

                result = cursor.fetchone()

                if result:
                    self.accept()
                else:
                    QMessageBox.warning(self, "Erreur",
                                        f"Aucun dossier trouvé pour le matricule {matricule} et le numéro de dossier {ref_dossier}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur",
                                 f"Erreur lors de la recherche : {str(e)}")
            print(f"Erreur détaillée : {str(e)}")

    def get_matricule(self):
        return self.matricule_input.text().strip()

    def get_ref_dossier(self):
        return self.reference_dossier_input.text().strip()


class EditCaseForm(QMainWindow):
    def __init__(self, matricule, ref_dossier, db_manager):
        super().__init__()
        self.matricule = matricule
        self.reference_dossier = ref_dossier
        self.db_manager = db_manager

        self.setWindowTitle(f"Modification du dossier {ref_dossier} - Matricule {matricule}")
        self.setMinimumSize(1200, 800)

        self.is_dark_mode = False
        self.current_section = 0

        #Initialisation de l'interface
        self.init_ui()

        # Configuration des widgets
        self.setup_comboboxes()
        self.setup_date_connections()

        #Chargement des données
        self.load_data(self.matricule, ref_dossier)

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
        title = QLabel(f"Modification du Dossier {self.reference_dossier} - Matricule: {self.matricule}")
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

    # METHODE CREATION DES SECTIONS
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
        """Crée la section des informations du dossier"""
        container = QWidget()
        layout = QFormLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        styles = Styles.get_styles(self.is_dark_mode)

        # Reférence du dossier
        self.reference_dossier = QLineEdit()
        self.reference_dossier.setPlaceholderText("Entrez la référence du dossier")
        self.reference_dossier.setStyleSheet(styles['INPUT'])
        layout.addRow(self.create_form_row("Référence Dossier", self.reference_dossier))

        # Année
        self.annee_punition = QLineEdit()
        self.annee_punition.setText(str(datetime.now().year))
        self.annee_punition.setReadOnly(True)
        self.annee_punition.setStyleSheet(styles['INPUT'])
        layout.addRow(self.create_form_row("Année en cours", self.annee_punition))

        # Date d'enregistrement
        self.date_enr = QDateEdit()
        self.date_enr.setCalendarPopup(True)
        self.date_enr.setDate(QDate.currentDate())
        self.date_enr.dateChanged.connect(self.update_annee_enr)
        self.date_enr.setStyleSheet(styles['DATE_EDIT'])

        today_button = QPushButton("Aujourd'hui")
        today_button.setStyleSheet(styles['BUTTON'])
        today_button.clicked.connect(lambda: self.date_enr.setDate(QDate.currentDate()))

        date_enr_layout = QHBoxLayout()
        date_enr_layout.addWidget(self.date_enr)
        date_enr_layout.addWidget(today_button)
        date_enr_container = QWidget()
        date_enr_container.setLayout(date_enr_layout)
        layout.addRow(self.create_form_row("Date d'enregistrement", date_enr_container))

        # N° enregistrement
        self.num_enr = QLineEdit()
        self.num_enr.setReadOnly(True)
        self.num_enr.setStyleSheet(styles['INPUT'])
        layout.addRow(self.create_form_row("N° enregistrement", self.num_enr))

        container.setLayout(layout)
        return container

    def create_suspect_info_section(self):
        """Crée la section des informations du mis en cause"""
        container = QWidget()
        layout = QFormLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        styles = Styles.get_styles(self.is_dark_mode)

        # Matricule
        self.matricule_field = QLineEdit()
        self.matricule_field.setReadOnly(True)
        self.matricule_field.setStyleSheet(styles['INPUT'])
        layout.addRow(self.create_form_row("Matricule", self.matricule_field))

        # Nom et Prénoms
        self.nom = QLineEdit()
        self.nom.setStyleSheet(styles['INPUT'])
        layout.addRow(self.create_form_row("Nom", self.nom))

        self.prenoms = QLineEdit()
        self.prenoms.setStyleSheet(styles['INPUT'])
        layout.addRow(self.create_form_row("Prénoms", self.prenoms))

        # Date de naissance
        self.date_naissance = QLineEdit()
        self.date_naissance.setReadOnly(True)
        self.date_naissance.setStyleSheet(styles['INPUT'])
        layout.addRow(self.create_form_row("Date de naissance", self.date_naissance))

        # Lieu de naissance
        self.lieu_naissance = QLineEdit()
        self.lieu_naissance.setReadOnly(True)
        self.lieu_naissance.setStyleSheet(styles['INPUT'])
        layout.addRow(self.create_form_row("Lieu de naissance", self.lieu_naissance))

        # Date d'entrée GIE
        self.date_entree_gie = QDateEdit()
        self.date_entree_gie.setCalendarPopup(True)
        self.date_entree_gie.setStyleSheet(styles['DATE_EDIT'])
        layout.addRow(self.create_form_row("Date d'entrée gendarmerie", self.date_entree_gie))

        # Structure (hiérarchie)
        self.unite = QComboBox()
        self.unite.setStyleSheet(styles['COMBO_BOX'])
        layout.addRow(self.create_form_row("Unité", self.unite))

        self.legion = QComboBox()
        self.legion.setStyleSheet(styles['COMBO_BOX'])
        layout.addRow(self.create_form_row("Légion", self.legion))

        self.subdivision = QComboBox()
        self.subdivision.setStyleSheet(styles['COMBO_BOX'])
        layout.addRow(self.create_form_row("Subdivision", self.subdivision))

        self.region = QComboBox()
        self.region.setStyleSheet(styles['COMBO_BOX'])
        layout.addRow(self.create_form_row("Région", self.region))

        # Age
        self.age = QSpinBox()
        self.age.setRange(18, 65)
        self.age.setStyleSheet(styles['SPIN_BOX'])
        layout.addRow(self.create_form_row("Age", self.age))

        # Années de service
        self.annee_service = QSpinBox()
        self.annee_service.setRange(0, 40)
        self.annee_service.setStyleSheet(styles['SPIN_BOX'])
        layout.addRow(self.create_form_row("Années de service", self.annee_service))

        #Sexe
        self.sexe = QComboBox()
        self.sexe.addItems(GENDER_ITEMS)
        self.sexe.setStyleSheet(styles['COMBO_BOX'])
        layout.addRow(self.create_form_row("Sexe", self.sexe))

        # Grade
        self.grade = QComboBox()
        self.grade.addItems(RANKS_ITEMS)
        self.grade.setStyleSheet(styles['COMBO_BOX'])
        layout.addRow(self.create_form_row("Grade", self.grade))

        # Situation matrimoniale
        self.situation_matrimoniale = QComboBox()
        self.situation_matrimoniale.addItems(MATRIMONIAL_ITEMS)
        self.situation_matrimoniale.setStyleSheet(styles['COMBO_BOX'])
        layout.addRow(self.create_form_row("Situation matrimoniale", self.situation_matrimoniale))

        # Nombre d'enfants
        self.nb_enfants = QSpinBox()
        self.nb_enfants.setStyleSheet(styles['SPIN_BOX'])
        layout.addRow(self.create_form_row("Nombre d'enfants", self.nb_enfants))

        container.setLayout(layout)
        return container

    def create_fault_info_section(self):
        """Crée la section des informations sur la faute"""
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

        # Libellé de la faute
        self.libelle = QTextEdit()
        self.libelle.setStyleSheet(styles['TEXT_EDIT'])
        self.libelle.setPlaceholderText("Description détaillée de la faute...")
        layout.addRow(self.create_form_row("Libellé", self.libelle))

        # Statut du dossier
        self.statut = QComboBox()
        self.statut.addItems(STATUT_ITEMS)
        self.statut.currentTextChanged.connect(self.on_statut_change)
        self.statut.setStyleSheet(styles['COMBO_BOX'])
        layout.addRow(self.create_form_row("Statut du dossier", self.statut))

        # Type de sanction
        self.type_sanction = QComboBox()
        self.type_sanction.setEnabled(False)
        self.type_sanction.setStyleSheet(styles['COMBO_BOX'])
        layout.addRow(self.create_form_row("Type de sanction", self.type_sanction))

        # Référence du statut
        self.ref_statut = QLineEdit()
        self.ref_statut.setEnabled(False)
        self.ref_statut.setStyleSheet(styles['INPUT'])
        layout.addRow(self.create_form_row("Référence du statut", self.ref_statut))

        # Numéros (pour radiation)
        self.num_decision = QLineEdit()
        self.num_decision.setEnabled(False)
        self.num_decision.setStyleSheet(styles['INPUT'])
        layout.addRow(self.create_form_row("Numéro de décision", self.num_decision))

        self.num_arrete = QLineEdit()
        self.num_arrete.setEnabled(False)
        self.num_arrete.setStyleSheet(styles['INPUT'])
        layout.addRow(self.create_form_row("Numéro d'arrêté", self.num_arrete))

        # Comité
        self.comite = QLineEdit()
        self.comite.setStyleSheet(styles['INPUT'])
        layout.addRow(self.create_form_row("COMITE", self.comite))

        # TAUX (JAR)
        self.taux_jar = QLineEdit()
        self.taux_jar.setStyleSheet(styles['INPUT'])
        layout.addRow(self.create_form_row("TAUX (JAR)", self.taux_jar))

        # ANNEE DES FAITS
        self.annee_faits = QLineEdit()
        self.annee_faits.setReadOnly(True)
        self.annee_faits.setStyleSheet(styles['INPUT'])
        layout.addRow(self.create_form_row("ANNEE DES FAITS", self.annee_faits))

        container.setLayout(layout)
        return container

    #METHODE DE NAVIGATION ENTRE SECTIONS, GESTION DE L'INTERFACE
    def update_structure_fields(self, unite_text: str, region_text: str, legion_text: str, subdiv_text: str):
        """
        Met à jour les champs de structure (unité, région, légion) en évitant les signaux en cascade
        Args:
            unite_text: Nom de l'unité
            region_text: Nom de la région
            legion_text: Nom de la légion
        """
        try:
            # Bloquer les signaux pour éviter les mises à jour en cascade
            self.unite.blockSignals(True)
            self.region.blockSignals(True)
            self.legion.blockSignals(True)
            self.subdivision.blockSignals(True)

            # Mise à jour des valeurs
            if unite_text:
                if unite_text not in [self.unite.itemText(i) for i in range(self.unite.count())]:
                    self.unite.addItem(unite_text)
                self.unite.setCurrentText(unite_text)

            if region_text:
                if region_text not in [self.region.itemText(i) for i in range(self.region.count())]:
                    self.region.addItem(region_text)
                self.region.setCurrentText(region_text)

            if legion_text:
                if legion_text not in [self.legion.itemText(i) for i in range(self.legion.count())]:
                    self.legion.addItem(legion_text)
                self.legion.setCurrentText(legion_text)

            if subdiv_text:
                if subdiv_text not in [self.subdivision.itemText(i) for i in range(self.subdivision.count())]:
                    self.subdivision.addItem(subdiv_text)
                self.subdivision.setCurrentText(subdiv_text)

            # Réactiver les signaux
            self.unite.blockSignals(False)
            self.region.blockSignals(False)
            self.legion.blockSignals(False)
            self.subdivision.blockSignals(False)

        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour des champs de structure : {str(e)}")

    def switch_section(self, index):
        """
        Gère la transition entre les sections avec animation
        Args:
            index: Index de la section à afficher
        """
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            # Configuration des sections
            sections = [self.section1, self.section2, self.section3]
            section_widths = {
                'active': lambda w: w * 2.2,  # Section active : 220% de la largeur
                'inactive': lambda w: w // 2.5  # Section inactive : 40% de la largeur
            }

            for i, section in enumerate(sections):
                # Création du groupe d'animations
                animation_group = QParallelAnimationGroup()

                # Animation de la taille
                is_active = i == index
                target_width = section_widths['active' if is_active else 'inactive'](section.width())

                size_animation = QPropertyAnimation(section, b"maximumWidth")
                size_animation.setDuration(900)
                size_animation.setEasingCurve(QEasingCurve.Type.InOutQuint)
                size_animation.setStartValue(section.width())
                size_animation.setEndValue(target_width)
                animation_group.addAnimation(size_animation)

                # Animation de l'opacité
                opacity_effect = QGraphicsOpacityEffect(section)
                section.setGraphicsEffect(opacity_effect)
                opacity_animation = QPropertyAnimation(opacity_effect, b"opacity")
                opacity_animation.setDuration(600)
                opacity_animation.setEasingCurve(QEasingCurve.Type.InOutQuint)

                if is_active:
                    opacity_animation.setStartValue(0.7)
                    opacity_animation.setEndValue(1.0)
                    section.setStyleSheet("""
                        QFrame {
                            background: white;
                            border-radius: 10px;
                            padding: 20px;
                            border: 1px solid #2196f3;
                            opacity: 1;
                        }
                    """)
                    section.raise_()
                else:
                    opacity_animation.setStartValue(1.0)
                    opacity_animation.setEndValue(0.7)
                    section.setStyleSheet("""
                        QFrame {
                            background: #f5f7fa;
                            border-radius: 10px;
                            padding: 20px;
                            border: none;
                            opacity: 0.5;
                        }
                    """)
                    section.lower()

                animation_group.addAnimation(opacity_animation)
                animation_group.start()

            # Restaurer le curseur après l'animation
            QTimer.singleShot(1000, lambda: QApplication.restoreOverrideCursor())

        except Exception as e:
            logger.error(f"Erreur lors du changement de section : {str(e)}")
            QApplication.restoreOverrideCursor()

    def update_navigation(self):
        """Met à jour l'affichage des boutons de navigation"""
        try:
            self.prev_button.setVisible(self.current_section > 0)
            self.next_button.setVisible(self.current_section < 2)
            self.submit_button.setVisible(self.current_section == 2)
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de la navigation : {str(e)}")

    def next_section(self):
        """Passe à la section suivante"""
        if self.current_section < 2:
            self.current_section += 1
            self.switch_section(self.current_section)
            self.update_navigation()

    def previous_section(self):
        """Revient à la section précédente"""
        if self.current_section > 0:
            self.current_section -= 1
            self.switch_section(self.current_section)
            self.update_navigation()

    # METHODES DES DATES ET DES CALCULS AUTO
    def update_annee_faits(self):
        """Met à jour l'année des faits automatiquement"""
        self.annee_faits.setText(str(self.date_faits.date().year()))

    def update_annee_enr(self):
        """Met à jour l'année d'enregistrement automatiquement"""
        self.annee_punition.setText(str(self.date_enr.date().year()))

    def update_age_and_service(self):
        """
        Met à jour l'âge et les années de service en fonction
        de la date des faits
        """
        try:
            date_faits = self.date_faits.date().toPyDate()

            # Calcul de l'âge
            if hasattr(self, 'date_naissance') and self.date_naissance.text():
                birth_date_str = adapt_date(self.date_naissance.text())
                if birth_date_str:
                    birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
                    age = relativedelta(date_faits, birth_date).years
                    self.age.setValue(age)

            # Calcul des années de service
            if hasattr(self, 'date_entree_gie') and self.date_entree_gie.text():
                entry_date_str = adapt_date(self.date_entree_gie.text())
                if entry_date_str:
                    entry_date = datetime.strptime(entry_date_str, '%Y-%m-%d').date()
                    years = relativedelta(date_faits, entry_date).years
                    self.annee_service.setValue(years)

        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de l'âge et des années de service : {str(e)}")

    def setup_date_connections(self):
        """Configure les connexions pour les mises à jour automatiques des dates"""
        try:
            # Mise à jour de l'année d'enregistrement quand la date change
            self.date_enr.dateChanged.connect(self.update_annee_enr)

            # Mise à jour de l'année des faits et calculs associés
            self.date_faits.dateChanged.connect(self.update_annee_faits)
            self.date_faits.dateChanged.connect(self.update_age_and_service)

        except Exception as e:
            logger.error(f"Erreur lors de la configuration des connexions de dates : {str(e)}")

    def setup_comboboxes(self):
        """Configure toutes les combobox du formulaire"""
        try:
            self.combo_handler = ComboBoxHandler(self.db_manager)

            # Configuration des combobox avec données de la BD
            static_combos = [
                (self.statut, "Statut", "lib_statut", "id_statut"),
                (self.type_sanction, "Type_sanctions", "lib_type_sanction", "id_type_sanction"),
                (self.grade, "Grade", "lib_grade", "id_grade"),
                (self.unite, "Unite", "lib_unite", "id_unite"),
                (self.legion, "Legion", "lib_legion", "id_legion"),
                (self.subdivision, "Subdiv", "lib_subdiv", "id_subdiv"),
                (self.region, "Region", "lib_rg", "id_rg"),
                (self.faute_commise, "Fautes", "lib_faute", "id_faute"),
                (self.situation_matrimoniale, "Sit_mat", "lib_sit_mat", "id_sit_mat")
            ]

            for combo, table, value_col, id_col in static_combos:
                combo.setProperty("table_name", table)
                combo.setProperty("value_column", value_col)
                self.combo_handler.setup_db_combobox(combo, table, value_col, id_col, order_by=value_col)

            # Connexion des signaux de changement
            self.statut.currentTextChanged.connect(self.on_statut_change)
            self.type_sanction.currentTextChanged.connect(self.on_type_sanction_change)

        except Exception as e:
            logger.error(f"Erreur lors de la configuration des combobox : {str(e)}")

    # METHODES DE MISE_A_JOUR DES INFOS DU DOSSIER ET DU MIS EN CAUSE
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
            self.taux_jar.clear()
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
            self.taux_jar.clear()
            self.taux_jar.setEnabled(False)

    def on_type_sanction_change(self, type_sanction: str):
        """
        Gère le changement de type de sanction
        Args:
            type_sanction: Le type de sanction sélectionné
        """
        is_radiation = type_sanction == "RADIATION"
        self.num_decision.setEnabled(is_radiation)
        self.num_arrete.setEnabled(is_radiation)

        if not is_radiation:
            self.num_decision.clear()
            self.num_arrete.clear()

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

    # METHODES DE VALIDATION
    def validate_form(self):
        """Valide les champs obligatoires du formulaire"""
        try:
            # 1. Champs obligatoires de base
            required_fields = {
                'Matricule': (self.matricule_field, QLineEdit),
                'Nom': (self.nom, QLineEdit),
                'Prénoms': (self.prenoms, QLineEdit),
                'Date des faits': (self.date_faits, QDateEdit),
                'Grade': (self.grade, QComboBox),
                'Unité': (self.unite, QComboBox),
                'Faute commise': (self.faute_commise, QComboBox),
                'Libellé': (self.libelle, QTextEdit),
                'Statut': (self.statut, QComboBox)
            }

            for field_name, (field, field_type) in required_fields.items():
                if field_type == QLineEdit and not field.text().strip():
                    QMessageBox.warning(self, "Champs manquants",
                                        f"Le champ '{field_name}' est obligatoire.")
                    field.setFocus()
                    return False
                elif field_type == QComboBox and not field.currentText().strip():
                    QMessageBox.warning(self, "Champs manquants",
                                        f"Le champ '{field_name}' est obligatoire.")
                    field.setFocus()
                    return False
                elif field_type == QTextEdit and not field.toPlainText().strip():
                    QMessageBox.warning(self, "Champs manquants",
                                        f"Le champ '{field_name}' est obligatoire.")
                    field.setFocus()
                    return False
                elif field_type == QDateEdit and not field.date().isValid():
                    QMessageBox.warning(self, "Date invalide",
                                        f"La {field_name} n'est pas valide.")
                    field.setFocus()
                    return False

            # 2. Validation du libellé
            if len(self.libelle.toPlainText().strip()) < 10:
                QMessageBox.warning(self, "Libellé trop court",
                                    "Le libellé doit contenir une description détaillée (minimum 10 caractères).")
                self.libelle.setFocus()
                return False

            # 3. Validation des dates
            if not self.validate_dates():
                return False

            # 4. Validation spécifique pour le statut "SANCTIONNE"
            if self.statut.currentText() == "SANCTIONNE":
                if not self.type_sanction.currentText().strip():
                    QMessageBox.warning(self, "Champs manquants",
                                        "Le type de sanction est obligatoire pour un dossier sanctionné.")
                    self.type_sanction.setFocus()
                    return False

                if not self.taux_jar.text().strip():
                    QMessageBox.warning(self, "Champs manquants",
                                        "Le taux (JAR) est obligatoire pour un dossier sanctionné.")
                    self.taux_jar.setFocus()
                    return False

            return True

        except Exception as e:
            logger.error(f"Erreur lors de la validation du formulaire : {str(e)}")
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la validation : {str(e)}")
            return False

    def validate_dates(self):
        """Valide la cohérence des dates"""
        date_enr = self.date_enr.date().toPyDate()
        date_faits = self.date_faits.date().toPyDate()

        if date_faits > date_enr:
            QMessageBox.warning(self, "Dates invalides",
                                "La date des faits ne peut pas être postérieure à la date d'enregistrement.")
            self.date_faits.setFocus()
            return False

        return True

    # METHODES DE RECHERCHES
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

    # METHODES DE GESTION DES DONNEES
    def load_data(self, matricule, ref):
        """Charge les données existantes du dossier"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                print(f"Voici les arguments {matricule} et {ref}")

                # Requête pour récupérer toutes les informations nécessaires
                cursor.execute("""
                    SELECT 
                    d.*,
                    g.*,
                    s.*,
                    gr.lib_grade,
                    u.lib_unite,
                    l.lib_legion,
                    sb.lib_subdiv,
                    r.lib_rg,
                    sm.lib_sit_mat,
                    f.lib_faute,
                    c.lib_categorie,
                    ts.lib_type_sanction,
                    ge.date_naissance,
                    ge.lieu_naissance,
                    ge.nom as nom_etat,
                    ge.prenoms as prenoms_etat
                FROM Dossiers d
                    JOIN Gendarmes g ON d.matricule_dossier = g.matricule
                    LEFT JOIN gendarmes_etat ge ON g.matricule = ge.matricule
                    LEFT JOIN Sanctions s ON d.sanction_id = s.id_sanction
                    LEFT JOIN Grade gr ON d.grade_id = gr.id_grade
                    LEFT JOIN Unite u ON d.unite_id = u.id_unite
                    LEFT JOIN Legion l ON d.legion_id = l.id_legion
                    LEFT JOIN Subdiv sb ON d.subdiv_id = sb.id_subdiv
                    LEFT JOIN Region r ON d.rg_id = r.id_rg
                    LEFT JOIN Sit_mat sm ON d.situation_mat_id = sm.id_sit_mat
                    LEFT JOIN Fautes f ON d.faute_id = f.id_faute
                    LEFT JOIN Categories c ON f.cat_id = c.id_categorie
                    LEFT JOIN Type_sanctions ts ON s.type_sanction_id = ts.id_type_sanction
                    WHERE d.matricule_dossier = ? AND d.reference = ?
                """, (matricule, ref))

                result = cursor.fetchone()

                # Récupérer les noms des colonnes depuis la description du curseur
                columns = [desc[0] for desc in cursor.description]

                # Convertir le tuple en dictionnaire
                result_dict = dict(zip(columns, result)) if result else None

                print(f"Voici les resultats {result}")

                if result:
                    # Section 1 : Informations du Dossier
                    self.reference_dossier.setText(str(result_dict['reference']))
                    self.annee_punition.setText(str(result_dict['annee_enr']))

                    # Dates
                    if result_dict['date_enr']:
                        self.date_enr.setDate(QDate.fromString(result_dict['date_enr'], "yyyy-MM-dd"))

                    self.num_enr.setText(str(result_dict['numero_inc']))
                    self.date_naissance.setText(str(result_dict['date_naissance']) or "NEANT")

                    # Section 2 : Informations du Mis en Cause
                    self.matricule_field.setText(str(result_dict['matricule_dossier']))
                    self.lieu_naissance.setText(str(result_dict['lieu_naissance']) or "NEANT")

                    # Séparation du nom et prénoms
                    if result_dict['nom_etat'] and result_dict['prenoms_etat']:
                        self.nom.setText(str(result_dict['nom_etat']))
                        self.prenoms.setText(str(result_dict['prenoms_etat']))
                    else:
                        # Fallback sur nom_prenoms si nécessaire
                        nom_complet = result_dict['nom_prenoms']
                        if nom_complet:
                            # Suppose que le premier mot est le nom
                            parts = nom_complet.split(' ', 1)
                            self.nom.setText(str(parts[0]))
                            self.prenoms.setText(str(parts[1]) if len(parts) > 1 else "")

                    # Sexe : utilisation des GENDER_ITEMS
                    if result_dict['sexe']:
                        if result_dict['sexe'] in GENDER_ITEMS:
                            self.sexe.setCurrentText(result_dict['sexe'])
                        else:
                            # Gérer le cas où la valeur ne correspond pas aux items
                            print(f"Valeur de sexe non reconnue : {result_dict['sexe']}")
                            self.sexe.setCurrentIndex(0)  # Valeur par défaut

                    # ComboBox et autres champs comme avant
                    if result_dict['lib_grade']:
                        self.grade.setCurrentText(result_dict['lib_grade'])
                    if result_dict['lib_sit_mat']:
                        self.situation_matrimoniale.setCurrentText(result_dict['lib_sit_mat'])

                    # Valeurs numériques
                    self.age.setValue(result_dict['age'] or 0)
                    self.nb_enfants.setValue(result_dict['nb_enfants'] or 0)
                    self.annee_service.setValue(result_dict['annee_service'] or 0)

                    # Structure
                    if result_dict['lib_unite']:
                        unite_text = result_dict['lib_unite']
                        region_text = result_dict['lib_rg']
                        legion_text = result_dict['lib_legion']
                        subdiv_text = result_dict['lib_subdiv']
                        self.update_structure_fields(unite_text, region_text, legion_text, subdiv_text)

                    # Section 3 : Informations sur la Faute
                    if result_dict['date_faits']:
                        self.date_faits.setDate(QDate.fromString(result_dict['date_faits'], "yyyy-MM-dd"))

                    self.faute_commise.setCurrentText(result_dict['lib_faute'] or '')

                    # Sanction
                    if result_dict['lib_type_sanction']:
                        self.type_sanction.setCurrentText(result_dict['lib_type_sanction'])
                    self.taux_jar.setText(str(result_dict['taux'] or ''))
                    self.libelle.setText(result_dict['libelle'] or '')
                    self.ref_statut.setText(str(result_dict['ref_statut']) or '')
                    self.comite.setText(str(result_dict['comite']) if result_dict['comite'] else "0")

                else:
                    QMessageBox.warning(self, "Erreur",
                                        f"Aucune donnée trouvée pour le matricule {matricule} et le numéro de dossier {ref}")
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

            # Préparer les données du dossier à mettre à jour
            dossier_data = {
                "reference": self.reference_dossier.text(),
                "date_enr": get_date_value(self.date_enr),
                "date_faits": get_date_value(self.date_faits),
                "numero_annee": int(self.num_enr.text()),
                "annee_enr": int(self.annee_punition.text()),
                "grade_id": self.combo_handler.get_selected_id(self.grade),
                "situation_mat_id": self.combo_handler.get_selected_id(self.situation_matrimoniale),
                "unite_id": self.combo_handler.get_selected_id(self.unite),
                "legion_id": self.combo_handler.get_selected_id(self.legion),
                "subdiv_id": self.combo_handler.get_selected_id(self.subdivision),
                "rg_id": self.combo_handler.get_selected_id(self.region),
                "faute_id": self.combo_handler.get_selected_id(self.faute_commise),
                "libelle": self.libelle.toPlainText().strip(),
                "statut_id": self.combo_handler.get_selected_id(self.statut)
            }

            # Préparer les données de la sanction à mettre à jour
            current_statut = self.statut.currentText()

            # Déterminer le type de sanction en fonction du statut
            type_sanction_id = None
            if current_statut == "SANCTIONNE":
                # Utiliser le type sélectionné
                type_sanction_id = self.combo_handler.get_selected_id(self.type_sanction)
            elif current_statut == "EN COURS":
                # Utiliser l'ID 6 pour "EN INSTANCE"
                type_sanction_id = 6

            sanction_data = {
                "type_sanction_id": type_sanction_id,
                "taux": self.taux_jar.text() or "0",
                "numero_decision": self.num_decision.text() if self.type_sanction.currentText() == "RADIATION" else None,
                "numero_arrete": self.num_arrete.text() if self.type_sanction.currentText() == "RADIATION" else None,
                "annee_radiation": int(
                    self.annee_punition.text()) if self.type_sanction.currentText() == "RADIATION" else None,
                "ref_statut": self.ref_statut.text(),
                "comite": self.comite.text() or "0"
            }

            # Mettre à jour le gendarme
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE Gendarmes SET
                        nom_prenoms = ?,
                        age = ?,
                        sexe = ?,
                        date_entree_gie = ?,
                        annee_service = ?,
                        nb_enfants = ?
                    WHERE matricule = ?
                """, (
                    f"{self.nom.text().strip()} {self.prenoms.text().strip()}",
                    self.age.value(),
                    self.sexe.currentText(),
                    adapt_date(self.date_entree_gie.text().strip()),
                    self.annee_service.value(),
                    self.nb_enfants.value(),
                    self.matricule_field.text().strip()
                ))
                conn.commit()

            # Utiliser la nouvelle méthode du DatabaseManager pour mettre à jour le dossier et la sanction
            success = self.db_manager.update_case_and_sanction(
                self.matricule,
                self.reference_dossier.text(),
                dossier_data,
                sanction_data
            )

            if success:
                QMessageBox.information(self, "Succès", "Les modifications ont été enregistrées avec succès!")
                self.close()
            else:
                QMessageBox.critical(self, "Erreur", "Erreur lors de la mise à jour du dossier et de la sanction.")

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur inattendue : {str(e)}")
            print(f"Erreur détaillée : {str(e)}")


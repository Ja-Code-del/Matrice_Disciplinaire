from datetime import datetime

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QFrame, QPushButton, QScrollArea, QLineEdit,
                             QFormLayout, QComboBox, QSpinBox, QDateEdit, QMessageBox,
                             QDialog, QGraphicsOpacityEffect, QApplication)
from PyQt6.QtCore import Qt, QDate, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QTimer
from PyQt6.QtGui import QFont, QColor

from src.data.gendarmerie import STRUCTURE_PRINCIPALE
from src.ui.styles.styles import Styles


class SearchMatriculeDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("Recherche du gendarme à modifier")
        self.setMinimumWidth(400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Titre
        title = QLabel("Recherche par matricule")
        title.setFont(QFont('Helvetica', 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #1976d2; margin-bottom: 20px;")
        layout.addWidget(title)

        # Message d'instruction
        instruction = QLabel("Entrez le matricule du gendarme à modifier")
        instruction.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #555;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(instruction)

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

    def validate_and_accept(self):
        matricule = self.matricule_input.text().strip()
        if not matricule:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer un matricule.")
            return

        # Vérifier l'existence du matricule
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT matricule 
                    FROM sanctions 
                    WHERE matricule = ?
                """, (matricule,))
                if cursor.fetchone():
                    self.accept()
                else:
                    QMessageBox.warning(self, "Erreur",
                                        f"Aucun dossier trouvé pour le matricule {matricule}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur",
                                 f"Erreur lors de la recherche : {str(e)}")

    def get_matricule(self):
        return self.matricule_input.text().strip()


class EditCaseForm(QMainWindow):
    """Formulaire de modification d'un dossier de sanction existant"""

    def __init__(self, matricule, db_manager):
        """
        Initialise le formulaire de modification
        Args:
            matricule: Matricule du gendarme à modifier
            db_manager: Instance du gestionnaire de base de données
        """
        super().__init__()
        self.matricule = matricule
        self.db_manager = db_manager
        self.setWindowTitle("Modification du dossier")
        self.setMinimumSize(1200, 800)
        self.is_dark_mode = False
        self.current_section = 0
        self.init_ui()
        self.load_data()  # Nouvelle méthode pour charger les données existantes

        # Deactivate gendarmeID edition
        self.matricule.setEnabled(False)
        # change the color to show its deactivate
        self.matricule.setStyleSheet("QLineEdit { background-color: #f0f0f0; }")

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
        title = QLabel(f"Modification du Dossier - Matricule: {self.matricule}")
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

        # Initial state
        self.prev_button.setVisible(False)
        self.submit_button.setVisible(False)
        self.update_navigation()

        # Connexions
        self.prev_button.clicked.connect(self.previous_section)
        self.next_button.clicked.connect(self.next_section)
        self.submit_button.clicked.connect(self.submit_form)

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
            # title.startswith("⚖️"):  # Section Info Faute
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
        for i, section in enumerate([self.section1, self.section2, self.section3]):
            # Création d'un groupe d'animations pour synchroniser les animations de taille, opacité et position
            animation_group = QParallelAnimationGroup()

            # Animation de la taille
            size_animation = QPropertyAnimation(section, b"maximumWidth")
            size_animation.setDuration(1800)
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

    def next_section(self):
        if self.current_section < 2:
            self.current_section += 1
            self.switch_section(self.current_section)
            self.update_navigation()

    def previous_section(self):
        if self.current_section > 0:
            self.current_section -= 1
            self.switch_section(self.current_section)
            self.update_navigation()

    def on_matricule_change(self, matricule):
        """
        Gère l'auto-complétion lors de la saisie du matricule
        Args:
            matricule: Matricule saisi
        """
        if len(matricule) >= 4:  # On commence la recherche après 4 caractères
            try:
                with self.db_manager.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT nom, prenoms, date_naissance
                        FROM gendarmes_etat
                        WHERE matricule = ?
                    """, (matricule,))
                    result = cursor.fetchone()
                    if result:
                        self.nom.setText(result[0])
                        self.prenoms.setText(result[1])
                        self.date_naissance.setText(result[2])
            except Exception as e:
                print(f"Erreur lors de la recherche du gendarme : {str(e)}")

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

    # Même code que NewCaseForm.create_case_info_section()
    # Mais les champs seront modifiables (pas de setReadOnly)
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
            label.setStyleSheet("""
                QLabel {
                    font-size: 15px;  
                    font-weight: 600;
                    color: #555;  
                    padding: 8px 0;  
                    min-width: 200px;  
                }
            """)
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

        # N° Décision de radiation
        self.num_radiation = QLineEdit()
        self.num_radiation.setPlaceholderText("À remplir si radiation")
        layout.addRow(create_row("N° Décision de radiation", self.num_radiation, True))

        # Année - En lecture seule car c'est l'année de création
        self.annee = QLineEdit()
        self.annee.setReadOnly(True)  # L'année ne doit pas être modifiable
        self.annee.setStyleSheet(line_edit_style + """
            QLineEdit:read-only {
                background: #f5f5f5;
                color: #666;
            }
        """)
        layout.addRow(create_row("Année", self.annee))

        # Date d'enregistrement - En lecture seule
        self.date_enr = QLineEdit()
        self.date_enr.setReadOnly(True)  # La date d'enregistrement ne doit pas être modifiable
        self.date_enr.setStyleSheet(line_edit_style + """
            QLineEdit:read-only {
                background: #f5f5f5;
                color: #666;
            }
        """)
        layout.addRow(create_row("Date d'enregistrement", self.date_enr))

        # N° enregistrement - En lecture seule
        self.num_enr = QLineEdit()
        self.num_enr.setReadOnly(True)  # Le numéro d'enregistrement ne doit pas être modifiable
        self.num_enr.setStyleSheet(line_edit_style + """
            QLineEdit:read-only {
                background: #f5f5f5;
                color: #666;
            }
        """)
        layout.addRow(create_row("N° enregistrement", self.num_enr))

        container.setLayout(layout)
        return container

    def create_suspect_info_section(self):
        """Crée la section des informations du mis en cause"""

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
        styles = Styles.get_styles(self.is_dark_mode)

        # Matricule (en lecture seule car on ne peut pas le modifier)
        self.matricule = QLineEdit()
        self.matricule.setReadOnly(True)
        self.matricule.setStyleSheet(styles['INPUT'] + """
            QLineEdit:read-only {
                background: #f5f5f5;
                color: #666;
                border: 2px solid #ddd;
            }
        """)
        layout.addRow(create_row("Matricule", self.matricule))

        # Champs auto-remplis et en lecture seule
        self.nom = QLineEdit()
        self.nom.setReadOnly(True)
        self.nom.setStyleSheet(styles['INPUT'] + """
            QLineEdit:read-only {
                background: #f5f5f5;
                color: #666;
                border: 2px solid #ddd;
            }
        """)
        layout.addRow(create_row("Nom", self.nom))

        self.prenoms = QLineEdit()
        self.prenoms.setReadOnly(True)
        self.prenoms.setStyleSheet(styles['INPUT'] + """
            QLineEdit:read-only {
                background: #f5f5f5;
                color: #666;
                border: 2px solid #ddd;
            }
        """)
        layout.addRow(create_row("Prénoms", self.prenoms))

        self.date_naissance = QLineEdit()
        self.date_naissance.setReadOnly(True)
        self.date_naissance.setStyleSheet(styles['INPUT'] + """
            QLineEdit:read-only {
                background: #f5f5f5;
                color: #666;
                border: 2px solid #ddd;
            }
        """)
        layout.addRow(create_row("Date de naissance", self.date_naissance))

        # Type d'affectation
        self.type_affectation = QComboBox()
        self.type_affectation.addItems(["REGIONS", "CSG"])
        self.type_affectation.setStyleSheet(styles['COMBO_BOX'])
        self.type_affectation.currentTextChanged.connect(self.on_affectation_change)
        layout.addRow(create_row("Type d'affectation", self.type_affectation))

        # Région/Direction
        self.direction = QComboBox()
        self.direction.setStyleSheet(styles['COMBO_BOX'])
        self.direction.currentTextChanged.connect(self.on_direction_change)
        layout.addRow(create_row("Région/Direction", self.direction))

        # Légion/Service
        self.service = QComboBox()
        self.service.setStyleSheet(styles['COMBO_BOX'])
        self.service.currentTextChanged.connect(self.on_service_change)
        layout.addRow(create_row("Légion/Service", self.service))

        # Unité
        self.unite = QComboBox()
        self.unite.setStyleSheet(styles['COMBO_BOX'])
        layout.addRow(create_row("Unité", self.unite))

        # Nombre d'enfants
        self.nb_enfants = QSpinBox()
        self.nb_enfants.setStyleSheet(styles['SPIN_BOX'])
        self.nb_enfants.setMinimum(0)
        self.nb_enfants.setMaximum(99)
        layout.addRow(create_row("Nombre d'enfants", self.nb_enfants))

        container.setLayout(layout)
        return container

    def on_affectation_change(self, affectation_type):
        """Met à jour les choix de direction selon le type d'affectation"""
        print(f"Changement d'affectation: {affectation_type}")
        self.direction.clear()
        self.service.clear()
        self.unite.clear()

        if affectation_type == "REGIONS":
            regions = STRUCTURE_PRINCIPALE["REGIONS"].keys()
            self.direction.addItems(regions)
        else:  # CSG
            directions = STRUCTURE_PRINCIPALE["CSG"].keys()
            self.direction.addItems(directions)

        # Si on a des données existantes, on essaie de restaurer la sélection
        if hasattr(self, '_stored_direction') and self._stored_direction:
            index = self.direction.findText(self._stored_direction)
            if index >= 0:
                self.direction.setCurrentIndex(index)

    def on_direction_change(self, direction):
        """Met à jour les choix de service selon la direction"""
        print(f"Changement de direction: {direction}")
        self.service.clear()
        self.unite.clear()

        affectation_type = self.type_affectation.currentText()
        if affectation_type == "REGIONS":
            if direction in STRUCTURE_PRINCIPALE["REGIONS"]:
                legions = STRUCTURE_PRINCIPALE["REGIONS"][direction].keys()
                self.service.addItems(legions)
        else:  # CSG
            if direction in STRUCTURE_PRINCIPALE["CSG"]:
                services = STRUCTURE_PRINCIPALE["CSG"][direction]
                if services:
                    self.service.addItems(services)

        # Restaurer la sélection précédente si elle existe
        if hasattr(self, '_stored_service') and self._stored_service:
            index = self.service.findText(self._stored_service)
            if index >= 0:
                self.service.setCurrentIndex(index)

    def on_service_change(self, service):
        """Met à jour les choix d'unité selon le service"""
        print(f"Changement de service: {service}")
        self.unite.clear()

        affectation_type = self.type_affectation.currentText()
        direction = self.direction.currentText()

        if affectation_type == "REGIONS":
            if direction in STRUCTURE_PRINCIPALE["REGIONS"]:
                legion_data = STRUCTURE_PRINCIPALE["REGIONS"][direction]
                if service in legion_data:
                    unites = []
                    service_data = legion_data[service]

                    if isinstance(service_data, list):
                        unites = service_data
                    else:
                        for cie, cie_unites in service_data.items():
                            unites.extend(cie_unites)

                    self.unite.addItems(unites)

        # Restaurer la sélection précédente si elle existe
        if hasattr(self, '_stored_unite') and self._stored_unite:
            index = self.unite.findText(self._stored_unite)
            if index >= 0:
                self.unite.setCurrentIndex(index)

    def on_statut_change(self, statut):
        """Gère l'affichage du champ référence selon le statut"""
        self.ref_statut_container.setVisible(statut == "RADIE")

    def create_fault_info_section(self):
        """Crée la section des informations sur la faute"""
        container = QWidget()
        layout = QFormLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

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

        styles = Styles.get_styles(self.is_dark_mode)

        # Date des faits avec calendrier
        self.date_faits = QDateEdit()
        self.date_faits.setCalendarPopup(True)
        self.date_faits.setDate(QDate.currentDate())
        self.date_faits.dateChanged.connect(self.update_annee_faits)
        self.date_faits.setStyleSheet(styles['DATE_EDIT'])
        layout.addRow(create_row("Date des faits", self.date_faits))

        # Faute commise (ComboBox)
        self.faute_commise = QComboBox()
        self.faute_commise.addItems([
            "ABANDON DE POSTE",
            "NEGLIGENCE",
            "CORRUPTION",
            "DESERTION",
            # Ajoutez d'autres fautes ici
        ])
        self.faute_commise.setStyleSheet(styles['COMBO_BOX'])
        layout.addRow(create_row("Faute commise", self.faute_commise))

        # Catégorie
        self.categorie = QLineEdit()
        self.categorie.setStyleSheet(styles['INPUT'])
        layout.addRow(create_row("Catégorie", self.categorie))

        # Statut du dossier
        self.statut = QComboBox()
        self.statut.addItems(["EN COURS", "PUNI", "RADIE"])
        self.statut.currentTextChanged.connect(self.on_statut_change)
        self.statut.setStyleSheet(styles['COMBO_BOX'])
        layout.addRow(create_row("Statut du dossier", self.statut))

        # Référence du statut
        self.ref_statut = QLineEdit()
        self.ref_statut.setStyleSheet(styles['INPUT'])
        self.ref_statut.setPlaceholderText("Référence de radiation")
        layout.addRow(create_row("Référence du statut", self.ref_statut))

        # TAUX (JAR)
        self.taux_jar = QSpinBox()
        self.taux_jar.setMinimum(0)
        self.taux_jar.setMaximum(365)
        self.taux_jar.setStyleSheet(styles['SPIN_BOX'])
        layout.addRow(create_row("TAUX (JAR)", self.taux_jar))

        # COMITE
        self.comite = QLineEdit()
        self.comite.setStyleSheet(styles['INPUT'])
        layout.addRow(create_row("COMITE", self.comite))

        # ANNEE DES FAITS (auto)
        self.annee_faits = QLineEdit()
        self.annee_faits.setReadOnly(True)
        self.annee_faits.setStyleSheet(styles['INPUT'])
        layout.addRow(create_row("ANNEE DES FAITS", self.annee_faits))

        container.setLayout(layout)
        return container

    def update_annee_faits(self):
        """Met à jour l'année des faits automatiquement"""
        self.annee_faits.setText(str(self.date_faits.date().year()))

    def load_data(self):
        """Charge les données existantes du dossier"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()

                # Charger les données de la table sanctions
                cursor.execute("""
                    SELECT * FROM sanctions 
                    WHERE matricule = ?
                """, (self.matricule,))
                sanctions_data = cursor.fetchone()

                # Charger les données de la table gendarmes
                cursor.execute("""
                    SELECT * FROM gendarmes 
                    WHERE mle = ?
                """, (self.matricule,))
                gendarmes_data = cursor.fetchone()

                if sanctions_data and gendarmes_data:
                    # Stocker les valeurs pour la restauration ultérieure
                    self._stored_direction = sanctions_data['regions']
                    self._stored_service = sanctions_data['legions']
                    self._stored_unite = sanctions_data['unite']

                    # Section 1 : Informations du Dossier
                    self.num_dossier.setText(str(sanctions_data['numero_dossier']))
                    self.num_radiation.setText(str(sanctions_data['numero_radiation']))
                    self.annee.setText(str(sanctions_data['annee']))
                    self.date_enr.setText(str(sanctions_data['date_enregistrement']))
                    self.num_enr.setText(str(sanctions_data['numero']))

                    # Section 2 : Informations du Mis en Cause
                    self.matricule.setText(str(self.matricule))
                    nom_prenoms = gendarmes_data['nom_prenoms'].split(' ', 1)
                    self.nom.setText(nom_prenoms[0])
                    self.prenoms.setText(nom_prenoms[1] if len(nom_prenoms) > 1 else "")
                    self.grade.setCurrentText(gendarmes_data['grade'])
                    self.sexe.setCurrentText(gendarmes_data['sexe'])
                    self.date_naissance.setText(str(gendarmes_data['date_naissance']))
                    self.age.setValue(gendarmes_data['age'])

                    # Type d'affectation et structure
                    self.type_affectation.setCurrentText(sanctions_data['regions'])
                    # Les ComboBox seront mises à jour via les signaux

                    self.nb_enfants.setValue(gendarmes_data['nb_enfants'])

                    # Section 3 : Informations sur la Faute
                    self.date_faits.setDate(QDate.fromString(str(sanctions_data['date_faits']), "yyyy-MM-dd"))
                    self.faute_commise.setCurrentText(sanctions_data['faute_commise'])
                    self.categorie.setText(str(sanctions_data['categorie']))
                    self.statut.setCurrentText(sanctions_data['statut'])
                    self.ref_statut.setText(sanctions_data['reference_statut'])
                    self.taux_jar.setValue(int(sanctions_data['taux_jar']))
                    self.comite.setText(str(sanctions_data['comite']))
                    self.annee_faits.setText(str(sanctions_data['annee_faits']))

                    # Mise à jour de l'interface selon le statut
                    self.on_statut_change(sanctions_data['statut'])

                else:
                    QMessageBox.warning(self, "Erreur",
                                        f"Aucune donnée trouvée pour le matricule {self.matricule}")
                    self.close()

        except Exception as e:
            QMessageBox.critical(self, "Erreur",
                                 f"Erreur lors du chargement des données : {str(e)}")
            print(f"Erreur détaillée : {str(e)}")  # Pour le débogage
            self.close()

    def validate_form(self):
        """Valide les champs obligatoires du formulaire"""
        try:
            required_fields = {
                'Numéro de dossier': self.num_dossier.text(),
                'Date des faits': self.date_faits.text(),
                'Faute commise': self.faute_commise.currentText(),
                'Catégorie': self.categorie.text(),
                'Statut': self.statut.currentText()
            }

            for field_name, value in required_fields.items():
                if not value or not str(value).strip():
                    QMessageBox.warning(self, "Champs manquants",
                                        f"Le champ '{field_name}' est obligatoire.")
                    return False

            # Validation spécifique pour le statut RADIE
            if self.statut.currentText() == "RADIE" and not self.ref_statut.text().strip():
                QMessageBox.warning(self, "Champs manquants",
                                    "La référence du statut est obligatoire pour une radiation.")
                self.ref_statut.setFocus()
                return False

            return True

        except Exception as e:
            QMessageBox.critical(self, "Erreur",
                                 f"Erreur lors de la validation : {str(e)}")
            return False

    def submit_form(self):
        try:
            if not self.validate_form():
                return

            reply = QMessageBox.question(self, "Confirmation",
                                         "Voulez-vous vraiment enregistrer ces modifications ?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.No:
                return

            # Préparation des données avec les noms corrects
            form_data = {
                # Section Info Dossier
                'numero_dossier': self.num_dossier.text(),
                'numero_radiation': self.num_radiation.text(),
                'annee': self.annee.text(),
                'date_enregistrement': self.date_enr.text(),
                'numero_enregistrement': self.num_enr.text(),

                # Section Info Mis en cause
                'matricule': self.matricule.text(),
                'nom_prenoms': f"{self.nom.text()} {self.prenoms.text()}".strip(),
                'grade': self.grade.currentText(),
                'sexe': self.sexe.currentText(),
                'date_naissance': self.date_naissance.text(),
                'age': self.age.value(),
                'unite': self.unite.currentText(),
                'legions': self.service.currentText(),  # service devient légions
                'subdiv': self.direction.currentText(),  # direction devient subdiv
                'regions': self.type_affectation.currentText(),  # type_affectation devient regions
                'date_entree_gie': self.date_entree_gie.text(),
                'annee_service': self.annee_service.text(),
                'situation_matrimoniale': self.situation_matrimoniale.currentText(),
                'nb_enfants': self.nb_enfants.value(),

                # Section Info Faute
                'date_faits': self.date_faits.date().toString("yyyy-MM-dd"),
                'faute_commise': self.faute_commise.currentText(),
                'categorie': self.categorie.text(),
                'statut': self.statut.currentText(),
                'reference_statut': self.ref_statut.text() if self.statut.currentText() == "RADIE" else "",
                'taux_jar': self.taux_jar.value(),
                'comite': self.comite.text(),
                'annee_faits': self.annee_faits.text()
            }

            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()

                # 1. Mise à jour de la table sanctions
                cursor.execute("""
                    UPDATE sanctions SET
                        numero_dossier = ?,
                        numero_radiation = ?,
                        date_faits = ?,
                        faute_commise = ?,
                        categorie = ?,
                        statut = ?,
                        reference_statut = ?,
                        taux_jar = ?,
                        comite = ?,
                        annee_faits = ?,
                        unite = ?,
                        legions = ?,
                        subdiv = ?,
                        regions = ?
                    WHERE matricule = ?
                """, (
                    form_data['numero_dossier'],
                    form_data['numero_radiation'],
                    form_data['date_faits'],
                    form_data['faute_commise'],
                    form_data['categorie'],
                    form_data['statut'],
                    form_data['reference_statut'],
                    form_data['taux_jar'],
                    form_data['comite'],
                    form_data['annee_faits'],
                    form_data['unite'],
                    form_data['legions'],
                    form_data['subdiv'],
                    form_data['regions'],
                    form_data['matricule']
                ))

                # 2. Mise à jour de la table gendarmes
                cursor.execute("""
                    UPDATE gendarmes SET
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
                    WHERE mle = ?
                """, (
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
                    int(form_data['annee_service']),
                    form_data['situation_matrimoniale'],
                    form_data['nb_enfants'],
                    form_data['matricule']
                ))

                # 3. Mise à jour de la table gendarmes_etat
                cursor.execute("""
                    UPDATE gendarmes_etat SET
                        unite = ?,
                        legions = ?,
                        subdiv = ?,
                        regions = ?,
                        nb_enfants = ?
                    WHERE matricule = ?
                """, (
                    form_data['unite'],
                    form_data['legions'],
                    form_data['subdiv'],
                    form_data['regions'],
                    form_data['nb_enfants'],
                    form_data['matricule']
                ))

                conn.commit()

                QMessageBox.information(self, "Succès",
                                        "Les modifications ont été enregistrées avec succès!")
                self.close()

        except Exception as e:
            QMessageBox.critical(self, "Erreur",
                                 f"Erreur lors de la mise à jour des données : {str(e)}")
            print(f"Erreur détaillée : {str(e)}")


from datetime import datetime
from dateutil.relativedelta import relativedelta

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QFrame, QPushButton, QScrollArea, QGraphicsOpacityEffect, QApplication, QLineEdit,
                             QFormLayout, QComboBox, QSpinBox, QDateEdit, QMessageBox)
from PyQt6.QtCore import Qt, QDate, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QTimer, QSize, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QIcon

from src.data.gendarmerie import STRUCTURE_UNITE
from src.data.gendarmerie.structure import (get_all_unit_names, get_unit_by_name, get_all_regions, get_all_subdivisions,
                                            get_all_legions, Unit)
from src.ui.styles.styles import Styles  # On va ajouter des styles dédiés
from src.ui.forms.unit_search_dialog import UnitSearchDialog
from src.ui.windows.statistics import StatistiquesWindow


class NewCaseForm(QMainWindow):
    """Formulaire de création d'un nouveau dossier de sanction"""

    def __init__(self, db_manager):
        """
                Initialise le formulaire
                Args:
                    db_manager: Instance du gestionnaire de base de données
                """
        super().__init__()
        self.case_added = pyqtSignal()
        self.db_manager = db_manager
        self.setWindowTitle("Page enregistrement de dossier")
        self.setMinimumSize(1200, 800)
        self.is_dark_mode = False
        self.styles = Styles.get_styles(self.is_dark_mode)
        self.setStyleSheet(self.styles["MAIN_WINDOW"])
        self.current_section = 0  # Pour tracker la section active
        self.init_ui()

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
        self.section3 = self.create_section("⚖️ Informations sur la Faute", "Nature et détails de la sanction")
        self.section2 = self.create_section("👤 Informations du Mis en Cause", "Identité et affectation du gendarme")

        #Reglage initial : les deux autres fenêtres sont cachees
        self.section2.setVisible(False)
        self.section3.setVisible(False)

        sections_layout.addWidget(self.section1)
        sections_layout.addWidget(self.section3)
        sections_layout.addWidget(self.section2)

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

        # N° Décision de radiation
        self.num_decision = QLineEdit()
        self.num_decision.setPlaceholderText("À remplir si radié")
        layout.addRow(create_row("N° Décision de radiation", self.num_decision, True))

        # Année
        self.annee_punition = QLineEdit()
        self.annee_punition.setText(str(datetime.now().year))
        self.annee_punition.setReadOnly(True)
        layout.addRow(create_row("Année en cours", self.annee_punition))

        # Date d'enregistrement
        # self.date_enr = QLineEdit()
        # self.date_enr.setText(datetime.now().strftime("%d/%m/%Y"))
        # self.date_enr.setReadOnly(True)
        # layout.addRow(create_row("Date d'enregistrement", self.date_enr))
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
                    SELECT MAX(CAST(ID as INTEGER))
                    FROM sanctions
                    WHERE annee_faits = ?
                """, (datetime.now().year,))
                last_num = cursor.fetchone()[0]
                next_num = 1 if last_num is None else last_num + 1
                self.num_enr.setText(str(next_num))
        except Exception as e:
            print(f"Erreur lors de la récupération du numéro : {str(e)}")
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
        self.faute_commise.addItems([
            "ABANDON DE POSTE",
            "NEGLIGENCE",
            "CORRUPTION",
            "DESERTION",
            # ... ajoute ta liste complète de fautes ici
        ])
        self.faute_commise.setStyleSheet(self.styles['COMBO_BOX'])
        layout.addRow(create_row("Faute commise", self.faute_commise))

        # Catégorie
        self.categorie = QLineEdit()
        self.categorie.setStyleSheet(self.styles['INPUT'])
        layout.addRow(create_row("Catégorie", self.categorie))

        # Statut du dossier
        self.statut = QComboBox()
        self.statut.addItems(["EN COURS", "PUNI", "RADIE"])
        #self.statut.currentTextChanged.connect(self.on_statut_change)
        self.statut.setStyleSheet(self.styles['COMBO_BOX'])
        layout.addRow(create_row("Statut du dossier", self.statut))

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

    def on_statut_change(self, statut):
        """Gère l'affichage du champ référence selon le statut"""
        self.ref_statut_container.setVisible(statut == "RADIE")

    # TROISIEME SECTION
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
                        SELECT nom, prenoms, date_naissance, date_entree_service, sexe
                        FROM gendarmes_etat
                        WHERE matricule = ?
                    """, (matricule,))
                    result = cursor.fetchone()
                    if result:
                        self.nom.setText(result[0])
                        self.prenoms.setText(result[1])
                        self.date_naissance.setText(result[2])
                        self.date_entree_gie.setText(result[3])
                        self.sexe.setCurrentText(result[4])
                        self.update_age(result[2])
                        self.update_years_of_service(result[3])
            except Exception as e:
                print(f"Erreur lors de la recherche du gendarme : {str(e)}")

    def update_age(self, date_naissance):
        try:
            birth_date = datetime.strptime(date_naissance, "%d/%m/%Y").date()
            faits_date = self.date_faits.date().toPyDate()
            age = relativedelta(faits_date, birth_date)
            self.age.setValue(age.years)
        except Exception as e:
            print(f"Erreur lors du calcul de l'âge : {str(e)}")
            self.age.setValue(0)

    def update_years_of_service(self, date_entree_gie):
        try:
            entree_date = datetime.strptime(date_entree_gie, "%d/%m/%Y").date()
            faits_date = self.date_faits.date().toPyDate()
            years_of_service = relativedelta(faits_date, entree_date)
            self.annee_service.setValue(years_of_service.years if years_of_service else 0)
        except Exception as e:
            print(f"Erreur lors du calcul des années de service : {str(e)}")
            self.annee_service.setValue(0)

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

        self.date_naissance = QLineEdit()
        self.date_naissance.setReadOnly(True)
        self.date_naissance.setStyleSheet(self.styles['INPUT'])
        layout.addRow(create_row("Date de naissance", self.date_naissance))

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
        self.grade.addItems(["ESO", "MDL", "MDC", "ADJ", "ADC", "ACM"])
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
        self.sexe.addItems(["M", "F"])
        self.sexe.setStyleSheet(self.styles['COMBO_BOX'])
        #self.sexe.setCurrentText(self.get_gendarme_sexe(m))
        layout.addRow(create_row("Sexe", self.sexe))

        self.situation_matrimoniale = QComboBox()
        self.situation_matrimoniale.addItems(["CELIBATAIRE", "MARIE(E)", "VEUF(VE)"])
        self.situation_matrimoniale.setStyleSheet(self.styles['COMBO_BOX'])
        layout.addRow(create_row("Situation matrimoniale", self.situation_matrimoniale))

        container.setLayout(layout)
        return container

    def on_unit_selected(self, unit_name):
        unit = get_unit_by_name(STRUCTURE_UNITE, unit_name)
        if unit:
            self.update_unite(unit_name)
            self.update_region(unit.region)
            self.update_subdivision(unit.region, unit.subdivision)
            self.update_legion(unit.region, unit.subdivision, unit.legion)
        else:
            # Gestion du cas où l'unité n'est pas trouvée dans la structure
            QMessageBox.warning(self, "Unité non trouvée",
                                f"L'unité '{unit_name}' n'a pas été trouvée dans la structure.")

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

    def submit_form(self):
        """Enregistre les données du formulaire dans la base de données"""
        try:
            if not self.validate_form():
                return

            form_data = {
                'numero_dossier': self.num_dossier.text(),
                'annee_punition': int(self.annee_punition.text()),
                'date_enr': self.date_enr.date().toString("dd/MM/yyyy"),
                'numero_ordre': int(self.num_enr.text()),
                'matricule': int(self.matricule.text()),
                'mle': self.matricule.text(),
                'nom_prenoms': f"{self.nom.text()} {self.prenoms.text()}",
                'grade': self.grade.currentText(),
                'date_naissance': self.date_naissance.text(),
                'age': self.age.value(),
                'sexe': self.sexe.currentText(),
                'regions': self.region.currentText(),
                'subdiv': self.subdivision.currentText(),
                'legions': self.legion.currentText(),
                'unite': self.unite.currentText(),
                'date_entree_gie': self.date_entree_gie.text() or '01/01/1900',
                'annee_service': self.annee_service.value(),
                'situation_matrimoniale': self.situation_matrimoniale.currentText(),
                'nb_enfants': self.nb_enfants.value(),
                'date_faits': self.date_faits.date().toString("dd/MM/yyyy"),
                'faute_commise': self.faute_commise.currentText(),
                'categorie': self.categorie.text(),
                'statut': self.statut.currentText(),
                'reference_statut': self.ref_statut.text(),
                'taux_jar': self.taux_jar.value(),
                'comite': int(self.comite.text()),
                'annee_faits': int(self.annee_faits.text()),
                'numero_decision': self.num_decision.text() if self.statut.currentText() == "RADIE" else "NEANT"
            }

            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute("SELECT COUNT(*) FROM sanctions WHERE numero_dossier = ?",
                               (form_data['numero_dossier'],))
                if cursor.fetchone()[0] > 0:
                    QMessageBox.warning(self, "Erreur",
                                        f"Le numéro de dossier {form_data['numero_dossier']} existe déjà.")
                    return

                cursor.execute("""
                    INSERT INTO sanctions (
                        numero_dossier, annee_punition, numero_ordre, date_enr,
                        matricule, faute_commise, date_faits, categorie,
                        statut, reference_statut, taux_jar, comite, annee_faits, 'numero_decision'
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    form_data['numero_dossier'],
                    form_data['annee_punition'],
                    form_data['date_enr'],
                    form_data['numero_ordre'],
                    form_data['matricule'],
                    form_data['date_faits'],
                    form_data['faute_commise'],
                    form_data['categorie'],
                    form_data['statut'],
                    form_data['reference_statut'],
                    form_data['taux_jar'],
                    form_data['comite'],
                    form_data['annee_faits'],
                    form_data['numero_decision']
                ))

                cursor.execute("""
                    INSERT INTO gendarmes (
                        mle, nom_prenoms, grade, age, date_naissance, unite, legions, subdiv,
                        regions, date_entree_gie, annee_service, situation_matrimoniale,
                        nb_enfants
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    form_data['mle'],
                    form_data['nom_prenoms'],
                    form_data['grade'],
                    form_data['age'],
                    form_data['date_naissance'],
                    form_data['unite'],
                    form_data['legions'],
                    form_data['subdiv'],
                    form_data['regions'],
                    form_data['date_entree_gie'],
                    form_data['annee_service'],
                    form_data['situation_matrimoniale'],
                    form_data['nb_enfants']
                ))

                conn.commit()

            QMessageBox.information(self, "Succès", "Dossier enregistré avec succès!")
            self.case_added.emit()  # Émettre le signal
            self.close()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'enregistrement : {str(e)}")
            print(f"Erreur détaillée : {str(e)}")

    def show_new_case_form(self):
        form = NewCaseForm(self.db_manager)
        form.case_added.connect(StatistiquesWindow.update_trends)  # Connexion du signal
        form.show()

    def validate_form(self):
        """
        Valide les champs obligatoires du formulaire
        Returns:
            bool: True si tous les champs obligatoires sont remplis
        """
        required_fields = {
            'Numéro de dossier': self.num_dossier,
            'Matricule': self.matricule,
            'Date des faits': self.date_faits,
            'Faute commise': self.faute_commise,
            'Catégorie': self.categorie,
            'Statut': self.statut
        }

        for field_name, field in required_fields.items():
            if isinstance(field, QLineEdit) and not field.text().strip():
                QMessageBox.warning(self, "Champs manquants",
                                    f"Le champ '{field_name}' est obligatoire.")
                field.setFocus()
                return False
            elif isinstance(field, QComboBox) and not field.currentText():
                QMessageBox.warning(self, "Champs manquants",
                                    f"Le champ '{field_name}' est obligatoire.")
                field.setFocus()
                return False

        # Validation spécifique pour le statut RADIE
        if self.statut.currentText() == "RADIE" and not self.ref_statut.text().strip():
            QMessageBox.warning(self, "Champs manquants",
                                "La référence du statut est obligatoire pour une radiation.")
            self.ref_statut.setFocus()
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

from datetime import datetime

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QFrame, QPushButton, QScrollArea, QGraphicsOpacityEffect, QApplication, QLineEdit,
                             QFormLayout)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QTimer
from PyQt6.QtGui import QFont, QColor
from src.ui.styles.styles import Styles  # On va créer des styles dédiés


class NewCaseForm(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setWindowTitle("Page enregistrement de dossier")
        self.setMinimumSize(1200, 800)
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
        title.setFont(QFont('Helvetica', 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
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
        section = QFrame()
        section.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 10px;
                padding: 20px;
            }
            QFrame:hover {
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
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
        else:
            # Garde le placeholder pour les autres sections pour l'instant
            content = QLabel("Contenu à venir...")
            content.setAlignment(Qt.AlignmentFlag.AlignCenter)
            content.setStyleSheet("color: #999; padding: 40px;")
            layout.addWidget(content)

        # if subtitle:
        #     subtitle_label = QLabel(subtitle)
        #     subtitle_label.setStyleSheet("color: #666; margin-bottom: 20px;")
        #     layout.addWidget(subtitle_label)
        # 
        # # Placeholder pour le contenu
        # content = QLabel("Contenu à venir...")
        # content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # content.setStyleSheet("color: #999; padding: 40px;")
        # layout.addWidget(content)

        layout.addStretch()
        return section

    def update_navigation(self):
        self.prev_button.setVisible(self.current_section > 0)
        self.next_button.setVisible(self.current_section < 2)
        self.submit_button.setVisible(self.current_section == 2)

    def switch_section(self, index):
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
                        border: 2px solid #2196f3;
                        opacity : 1;
                        box-shadow: 0px 10px 20px rgba(0, 0, 0, 0.8);
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
        self.num_radiation = QLineEdit()
        self.num_radiation.setPlaceholderText("À remplir si radiation")
        layout.addRow(create_row("N° Décision de radiation", self.num_radiation, True))

        # Année
        self.annee = QLineEdit()
        self.annee.setText(str(datetime.now().year))
        self.annee.setReadOnly(True)
        layout.addRow(create_row("Année", self.annee))

        # Date d'enregistrement
        self.date_enr = QLineEdit()
        self.date_enr.setText(datetime.now().strftime("%d/%m/%Y"))
        self.date_enr.setReadOnly(True)
        layout.addRow(create_row("Date d'enregistrement", self.date_enr))

        # N° enregistrement
        self.num_enr = QLineEdit()
        self.num_enr.setReadOnly(True)
        self.get_next_num_enr()
        layout.addRow(create_row("N° enregistrement", self.num_enr))

        container.setLayout(layout)
        return container

    # def create_case_info_section(self):
    #     """Crée le contenu de la section Informations du Dossier"""
    #     container = QWidget()
    #     layout = QFormLayout()
    #     layout.setSpacing(20)
    #     layout.setContentsMargins(20, 20, 20, 20)  # Marges uniformes
    #     layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)  # Alignement gauche des labels
    #
    #     # Style commun pour les QLineEdit
    #     line_edit_style = """
    #         QLineEdit {
    #             padding: 12px 20px;
    #             border: 2px solid #e0e0e0;
    #             border-radius: 5px;
    #             background: white;
    #             min-width: 300px;  # Largeur uniforme
    #             font-size: 14px;
    #             margin-left: 0px;  # Alignement avec le label
    #         }
    #         QLineEdit:focus {
    #             border-color: #2196f3;
    #             background: #f8f9fa;
    #         }
    #         QLineEdit:disabled {
    #             background: #f5f5f5;
    #             color: #666;
    #         }
    #         QLineEdit::placeholder {
    #             color: #aaa;
    #             padding: 5px;
    #         }
    #     """
    #
    #     # Style pour les labels
    #     label_style = """
    #         QLabel {
    #             font-size: 14px;
    #             font-weight: 700;
    #             color: #333;
    #             padding: 8px 0;  # Padding vertical pour aligner avec les inputs
    #             min-width: 200px;  # Largeur fixe pour alignement
    #         }
    #     """
    #
    #     def create_row(label_text, widget, with_info=False):
    #         row_widget = QWidget()
    #         row_layout = QHBoxLayout(row_widget)
    #         row_layout.setContentsMargins(0, 0, 0, 0)
    #         row_layout.setSpacing(10)
    #
    #         label = QLabel(label_text)
    #         label.setStyleSheet(label_style)
    #         row_layout.addWidget(label)
    #
    #         widget.setStyleSheet(line_edit_style)
    #         row_layout.addWidget(widget)
    #
    #         if with_info:
    #             info_icon = QPushButton("ℹ️")
    #             info_icon.setToolTip("Remplir uniquement en cas de radiation")
    #             info_icon.setStyleSheet("""
    #                 QPushButton {
    #                     border: none;
    #                     background: transparent;
    #                     font-size: 16px;
    #                     margin: 0 5px;
    #                 }
    #             """)
    #             row_layout.addWidget(info_icon)
    #
    #         row_layout.addStretch()
    #         return row_widget
    #
    #     # N° Dossier
    #     self.num_dossier = QLineEdit()
    #     self.num_dossier.setPlaceholderText("Entrez le N° de dossier")
    #     layout.addRow(create_row("N° Dossier", self.num_dossier))
    #
    #     # N° Décision de radiation
    #     self.num_radiation = QLineEdit()
    #     self.num_radiation.setPlaceholderText("À remplir si radiation")
    #     layout.addRow(create_row("N° Décision de radiation", self.num_radiation, True))
    #
    #     # Année
    #     self.annee = QLineEdit()
    #     self.annee.setText(str(datetime.now().year))
    #     self.annee.setReadOnly(True)
    #     layout.addRow(create_row("Année", self.annee))
    #
    #     # Date d'enregistrement
    #     self.date_enr = QLineEdit()
    #     self.date_enr.setText(datetime.now().strftime("%d/%m/%Y"))
    #     self.date_enr.setReadOnly(True)
    #     layout.addRow(create_row("Date d'enregistrement", self.date_enr))
    #
    #     # N° enregistrement
    #     self.num_enr = QLineEdit()
    #     self.num_enr.setReadOnly(True)
    #     self.get_next_num_enr()
    #     layout.addRow(create_row("N° enregistrement", self.num_enr))
    #
    #     container.setLayout(layout)
    #     return container

    # def create_case_info_section(self):
    #     """Crée le contenu de la section Informations du Dossier"""
    #     container = QWidget()
    #     layout = QFormLayout()
    #     layout.setSpacing(15)
    #
    #     # Style commun pour les QLineEdit
    #     line_edit_style = """
    #         QLineEdit {
    #             padding: 8px;
    #             border: 2px solid #e0e0e0;
    #             border-radius: 5px;
    #             background: white;
    #             min-width: 200px;
    #             font-size: 14px;
    #         }
    #         QLineEdit:focus {
    #             border-color: #2196f3;
    #             background: #f8f9fa;
    #         }
    #         QLineEdit:disabled {
    #             background: #f5f5f5;
    #             color: #666;
    #         }
    #     """
    #
    #     # N° Dossier
    #     self.num_dossier = QLineEdit()
    #     self.num_dossier.setPlaceholderText("Entrez le N° de dossier")
    #     self.num_dossier.setStyleSheet(line_edit_style)
    #     layout.addRow(self.create_label("N° Dossier"), self.num_dossier)
    #
    #     # N° Décision de radiation (optionnel)
    #     self.num_radiation = QLineEdit()
    #     self.num_radiation.setPlaceholderText("À remplir si radiation")
    #     self.num_radiation.setStyleSheet(line_edit_style)
    #     radiation_container = QWidget()
    #     radiation_layout = QHBoxLayout(radiation_container)
    #     radiation_layout.setContentsMargins(0, 0, 0, 0)
    #     radiation_layout.addWidget(self.num_radiation)
    #     info_icon = QPushButton("ℹ️")
    #     info_icon.setToolTip("Remplir uniquement en cas de radiation")
    #     info_icon.setStyleSheet("""
    #         QPushButton {
    #             border: none;
    #             background: transparent;
    #             font-size: 16px;
    #         }
    #     """)
    #     radiation_layout.addWidget(info_icon)
    #     layout.addRow(self.create_label("N° Décision de radiation"), radiation_container)
    #
    #     # Année (auto)
    #     self.annee = QLineEdit()
    #     self.annee.setText(str(datetime.now().year))
    #     self.annee.setReadOnly(True)
    #     self.annee.setStyleSheet(line_edit_style)
    #     layout.addRow(self.create_label("Année"), self.annee)
    #
    #     # Date d'enregistrement (auto)
    #     self.date_enr = QLineEdit()
    #     self.date_enr.setText(datetime.now().strftime("%d/%m/%Y"))
    #     self.date_enr.setReadOnly(True)
    #     self.date_enr.setStyleSheet(line_edit_style)
    #     layout.addRow(self.create_label("Date d'enregistrement"), self.date_enr)
    #
    #     # N° enregistrement (auto)
    #     self.num_enr = QLineEdit()
    #     self.num_enr.setReadOnly(True)
    #     self.num_enr.setStyleSheet(line_edit_style)
    #     self.get_next_num_enr()  # Méthode à créer pour récupérer le prochain numéro
    #     layout.addRow(self.create_label("N° enregistrement"), self.num_enr)
    #
    #     container.setLayout(layout)
    #     return container

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
                    SELECT MAX(CAST(numero as INTEGER))
                    FROM sanctions
                    WHERE annee_faits = ?
                """, (datetime.now().year,))
                last_num = cursor.fetchone()[0]
                next_num = 1 if last_num is None else last_num + 1
                self.num_enr.setText(str(next_num))
        except Exception as e:
            print(f"Erreur lors de la récupération du numéro : {str(e)}")
            self.num_enr.setText("1")

    def submit_form(self):
        # À implémenter
        pass
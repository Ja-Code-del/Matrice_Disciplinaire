import sqlite3
from datetime import datetime

import pandas as pd
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLineEdit, QPushButton, QLabel,
                             QTableWidget, QTableWidgetItem, QTabWidget,
                             QComboBox, QGroupBox, QGridLayout, QMessageBox,
                             QHeaderView, QDialog, QToolBar, QFileDialog, QDockWidget, QSizePolicy, QFrame)

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon
from src.database.db_manager import DatabaseManager
from src.ui.styles.styles import Styles
from src.database.models import  GendarmesRepository, DossiersRepository, SanctionsRepository
from src.ui.windows.import_etat_window import ImportEtatCompletWindow
from src.ui.forms.edit_gendarme_form import SearchDossierDialog, EditCaseForm
from .forms.delete_case_dialog import DeleteCaseDialog
from .handlers.stats_handler import StatsHandler
from src.ui.widgets.user_info_widget import UserInfoWidget


class MainGendarmeApp(QMainWindow):
    def __init__(self, username=None):
        super().__init__()

        # Initialisation des attributs
        self.username = username
        self.search_type = None
        self.logo_label = QLabel('Bienvenue sur Gend-Track')
        self.sanctions_table = None
        self.search_input = QLineEdit()
        self.search_input.setMinimumHeight(40)
        self.toolbar = None
        self.theme_button = None
        self.info_labels = None
        self.is_dark_mode = False
        self.info_group = None
        self.sanctions_group = None

        # Initialisation des gestionnaires de données
        self.db_manager = DatabaseManager()
        self.gendarmes_repo = GendarmesRepository(self.db_manager)
        self.dossiers_repo = DossiersRepository(self.db_manager)
        self.sanctions_repo = SanctionsRepository(self.db_manager)

        # Initialisation du gestionnaire de statistiques
        self.stats_handler = StatsHandler(self)

        # Définition des champs d'information
        self.info_fields = [
            ('matricule', 'Matricule'),
            ('nom_prenoms', 'Nom et Prénoms'),
            ('sexe', 'Sexe'),
            ('date_naissance', 'Date de naissance'),
            ('date_entree_gie', 'Date d\'entrée GIE'),
            ('lieu_naissance', 'LIEU DE NAISSANCE')
        ]

        # Initialisation de l'interface
        self.init_ui()



    def init_ui(self):
        """Initialise interface utilisateur"""
        self.setWindowTitle("Matrice disciplinaire des Gendarmes")
        self.setMinimumSize(1000, 750)
        self.resize(1280, 800)

        # Widget principal
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        if self.username:
            header_layout = QHBoxLayout()
            user_info = UserInfoWidget(self.username)
            header_layout.addStretch()  # Pour pousser le widget vers la droite
            header_layout.addWidget(user_info)
            layout.addLayout(header_layout)

        self.search_input.setPlaceholderText("Rechercher par matricule...")
        self.search_input.setFixedHeight(40)
        self.search_input.setStyleSheet(
            "border : 5px solid #007aff"
        )

        self.search_input.returnPressed.connect(self.search_gendarme)  # Ajout de la recherche par Enter
        search_button = QPushButton("Rechercher")
        search_button.setFixedSize(300, 41)
        search_button.clicked.connect(self.search_gendarme)

        layout.addWidget(self.search_input)
        #layout.addWidget(search_button)

        #Layout pour centrer le bouton sous la barre
        button_layout = QHBoxLayout()
        button_layout.addStretch()  # Ajoute un espace à gauche
        button_layout.addWidget(search_button)  # Ajoute le bouton au centre
        button_layout.addStretch()  # Ajoute un espace à droite

        layout.addLayout(button_layout)

        # Ajouter le logo et cacher lors d'une recherche
        #logo_pixmap = QPixmap("../resources/icons/logo.png")  # Chemin de l'image du logo
        self.logo_label.setStyleSheet("font-size: 48px; color: #1c1c1e;")
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centrer le logo
        self.logo_label.setFixedSize(1000, 600)
        self.logo_label.setScaledContents(True)
        layout.addWidget(self.logo_label)


        layout.addWidget(self.logo_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # barre d'outils à gauche
        dock_widget = QDockWidget("MENU", self)
        dock_widget.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
        dock_widget.setMinimumWidth(220)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock_widget)

        toolbar = QToolBar("Toolbar")
        toolbar.setOrientation(Qt.Orientation.Vertical)
        # Ajoutez ces lignes pour que la toolbar prenne toute la largeur
        toolbar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        toolbar.setMinimumWidth(dock_widget.minimumWidth())

        #CSS style for the toolbar
        toolbar.setStyleSheet("""
        QTooBar{
            spacing: 15px;
            padding: 5px;
            background-color: #007aff;
            border: none;
        }
        QPushButton {
        text-align: left;

        margin: 0px;
        border: none;
        width: 100%;
        }
        """)

        # Buttons
        buttons_config = [
            {
                "text": "Nouveau Dossier",
                "icon": "../resources/icons/person_add.png",
                "callback": "show_new_case_form"
            },
            {
                "text": "Modifier un dossier",
                "icon": "../resources/icons/edit_note.png",
                "callback": "edit_gendarme"
            },
            {
                "text": "Statistiques",
                "icon": "../resources/icons/statistics_icon.png",
                "callback": "show_statistics"
            },
            {
                "text": "Supprimer un dossier",
                "icon": "../resources/icons/person_remove.png",
                "callback": "show_delete_case_dialog"
            },
            {
                "text": "Réglages",
                "icon": "../resources/icons/settings.png",
                "callback": "open_settings_window"
            }
        ]

        # Same style for button
        common_style = """
            QPushButton {
                text-align: left;

                border: none;
                width: 210px;  /* Largeur fixe pour tous les boutons */
            }
        """

        #common_style = "text-align: left; padding-left: 35px;"

        # Creation and config of button
        for button_config in buttons_config:
            button = QPushButton(button_config["text"])
            button.setIcon(QIcon(button_config["icon"]))
            button.setStyleSheet(common_style)
            button.setIconSize(QSize(32, 32))  # icons have same size

            button.setContentsMargins(0, 0, 0, 0)  # delete intern margin
            button.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            # Connection of callback if defined
            if button_config["callback"]:
                callback_method = getattr(self, button_config["callback"])
                button.clicked.connect(callback_method)

            # Add button to toolbar
            toolbar.addWidget(button)

        # Ajouter un espaceur pour pousser le widget utilisateur vers le bas
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        toolbar.addWidget(spacer)

        # Ajout du widget utilisateur en bas de la toolbar
        if self.username:
            user_container = QWidget()
            user_layout = QVBoxLayout(user_container)
            user_layout.setContentsMargins(5, 5, 5, 5)

            # Ligne de séparation
            separator = QFrame()
            separator.setFrameShape(QFrame.Shape.HLine)
            separator.setStyleSheet("background-color: #dee2e6;")
            user_layout.addWidget(separator)

            # Widget utilisateur
            user_info = UserInfoWidget(self.username)
            user_layout.addWidget(user_info)

            toolbar.addWidget(user_container)

        # Configuration of dock widget
        dock_widget.setWidget(toolbar)

        # Informations du gendarme
        self.info_group = QGroupBox("Informations du gendarme")  # Correction : Déclaration de self.info_group
        self.info_group.setVisible(False)  # Cacher au départ
        info_layout = QGridLayout()
        self.info_group.setFont(QFont('Helvetica', 18, QFont.Weight.Bold))

        self.info_labels = {}
        for i, (field_id, field_name) in enumerate(self.info_fields):
            label = QLabel(f"{field_name}:")
            label.setFont(QFont('Helvetica', 12, QFont.Weight.Bold))
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
        self.sanctions_table.setColumnCount(14)
        headers = [
            "N° ORDRE",
            "REFERENCE",
            "GRADE",
            "UNITE",
            "LEGION",
            "SUBDIVISION",
            "REGION",
            "SITUATION MAT.",
            "FAUTE COMMISE",
            "DATE FAITS",
            "CAT.FAUTE",
            "TYPE SANCTION",
            "TAUX (JAR)",
            "COMITE"
        ]
        self.sanctions_table.setHorizontalHeaderLabels(headers)
        #self.sanctions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # adapte la largeur des colonnes
        self.sanctions_table.resizeColumnToContents(1)
        sanctions_layout.addWidget(self.sanctions_table)
        self.sanctions_group.setLayout(sanctions_layout)
        layout.addWidget(self.sanctions_group)

        self.statusBar().showMessage("Prêt")
        self.apply_theme()

    def update_username(self, new_username):
        self.username = new_username
        # Met à jour uniquement la partie username de l'interface
        central_widget = self.centralWidget()
        main_layout = central_widget.layout()

        if hasattr(self, 'user_info_layout'):
            # Supprime l'ancien widget username s'il existe
            for i in reversed(range(self.user_info_layout.count())):
                self.user_info_layout.itemAt(i).widget().setParent(None)
        else:
            # Crée le layout pour le username s'il n'existe pas
            self.user_info_layout = QHBoxLayout()
            main_layout.insertLayout(0, self.user_info_layout)

        # Ajoute le nouveau widget username
        user_info = UserInfoWidget(self.username)
        self.user_info_layout.addStretch()
        self.user_info_layout.addWidget(user_info)

    def search_gendarme(self):
        """Recherche un gendarme et affiche ses dossiers disciplinaires"""

        search_text = self.search_input.text().strip()
        if not search_text:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer un critère de recherche")
            return

        try:
            # Récupération des dossiers selon le matricule
            if search_text:
                dossiers = self.dossiers_repo.get_dossiers_by_matricule(search_text)
            else:
                dossiers = self.dossiers_repo.get_dossiers_by_name(search_text)
                QMessageBox.information(self, "Oups!", "Veuillez entrer un matricule dans la barre de recherche")

            if not dossiers:
                QMessageBox.information(self, "Résultat", "Aucun dossier trouvé.")
                return

            # Masquer le logo et afficher les tableaux
            self.logo_label.setVisible(False)
            self.info_group.setVisible(True)
            self.sanctions_group.setVisible(True)

            # Récupérer les informations du gendarme en utilisant le matricule du premier dossier
            gendarme_by_mat = self.gendarmes_repo.get_by_matricule(str(search_text))
            if gendarme_by_mat:
                self._afficher_info_gendarme(gendarme_by_mat)

            # Afficher les dossiers dans le tableau
            self._afficher_dossiers(dossiers)

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue: {str(e)}")
            print(f"Erreur détaillée : {str(e)}")

    def _afficher_info_gendarme(self, gendarme):
        """Affiche les informations du gendarme"""
        for field_id, label in self.info_labels.items():
            value = getattr(gendarme, field_id, None)

            # Formatage spécial pour les dates
            if field_id in ['date_naissance', 'date_entree_gie'] and value:
                try:
                    formatted_value = value.strftime('%d/%m/%Y')
                    label.setText(formatted_value)
                except Exception as e:
                    print(f"Erreur date {field_id}: {e}")
                    label.setText(str(value))
            else:
                label.setText(str(value if value is not None else ""))

    def _afficher_dossiers(self, dossiers):
        """Affiche les dossiers dans le tableau des sanctions"""
        self.sanctions_table.setRowCount(len(dossiers))

        for row, dossier in enumerate(dossiers):
            # Formatage de la date si c'est une chaîne
            if dossier['date_faits']:
                try:
                    # Convertir la date du format SQLite en format français
                    date_obj = datetime.strptime(dossier['date_faits'], '%Y-%m-%d')
                    date_formatted = date_obj.strftime('%d/%m/%Y')
                except:
                    date_formatted = dossier['date_faits']
            else:
                date_formatted = ""

            colonnes = [
                str(dossier['numero_inc']),
                dossier['reference'],
                dossier['lib_grade'] or "",
                dossier['lib_unite'] or "",
                dossier['lib_legion'] or "",
                dossier['lib_subdiv'] or "",
                dossier['lib_rg'] or "",
                dossier['lib_sit_mat'] or "",
                dossier['lib_faute'] or "",
                date_formatted,
                dossier['id_categorie'] or "",
                dossier['lib_type_sanction'] or "",
                dossier['taux'] or "",
                dossier['comite'] or ""
            ]

            # Remplissage de la ligne
            for col, valeur in enumerate(colonnes):
                item = QTableWidgetItem(str(valeur))
                self.sanctions_table.setItem(row, col, item)

        # Ajuster la largeur des colonnes au contenu
        self.sanctions_table.resizeColumnsToContents()

    def apply_theme(self):
        """Applique le thème actuel à tous les widgets"""
        styles = Styles.get_styles(self.is_dark_mode)

        # Application des styles
        self.setStyleSheet(styles['MAIN_WINDOW'])
        self.search_input.setStyleSheet(styles['INPUT'])

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

    def edit_gendarme(self):
        dialog = SearchDossierDialog(self.db_manager, self)
        if dialog.exec():
            matricule_str = dialog.get_matricule()
            ref_dossier = dialog.get_ref_dossier()
            try:
                self.edit_form = EditCaseForm(matricule_str, ref_dossier, self.db_manager)
                self.edit_form.show()
            except ValueError:
                QMessageBox.warning(self, "Erreur",
                                    "Le matricule doit être un nombre valide.")

    def show_delete_case_dialog(self):
        """Affiche la boîte de dialogue de suppression de dossier."""
        try:
            dialog = DeleteCaseDialog(self.db_manager, self)

            # Connecter le signal à la méthode de rafraîchissement
            dialog.case_deleted.connect(self.refresh_after_deletion)

            dialog.exec()


        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors de l'ouverture de la fenêtre de suppression : {str(e)}"
            )

    def refresh_after_deletion(self):
        """Rafraîchit les données après une suppression."""
        try:
            # 1. Rafraîchir l'affichage principal si un gendarme est affiché
            current_matricule = self.info_labels.get('matricule').text() if self.info_group.isVisible() else None

            if current_matricule:
                # Refaire une recherche pour mettre à jour l'affichage
                self.search_input.setText(current_matricule)
                self.search_type.setCurrentText("Matricule (MLE)")
                self.search_gendarme()

            # 2. Rafraîchir les statistiques si elles sont ouvertes
            if hasattr(self, 'stats_handler') and self.stats_handler:
                stats_window = self.stats_handler.get_current_stats_window()
                if stats_window:
                    # Mettre à jour les tendances
                    if hasattr(stats_window, 'update_trends'):
                        stats_window.update_trends()

                    # Rafraîchir la liste exhaustive si elle est ouverte
                    if hasattr(stats_window, 'list_window') and stats_window.list_window:
                        stats_window.list_window.load_data()

                    # Rafraîchir toute autre fenêtre de visualisation ouverte
                    if hasattr(stats_window, 'visualization_window') and stats_window.visualization_window:
                        stats_window.visualization_window.load_data()

            # 3. Mettre à jour le statut
            self.statusBar().showMessage("Dossier(s) supprimé(s) avec succès et données mises à jour", 3000)

        except Exception as e:
            print(f"Erreur lors du rafraîchissement : {str(e)}")
            QMessageBox.warning(
                self,
                "Attention",
                "La suppression a réussi mais le rafraîchissement a échoué.\n"
                "Veuillez rafraîchir manuellement les fenêtres ouvertes."
            )

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
            #self.new_case_form.is_dark_mode = self.is_dark_mode
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
            "Importer l'état complet des Sous-officiers",
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
        import_etat_button.setStyleSheet("""
                                    QPushButton {
                                                background-color: #6C63FF;
                                                color: white;
                                                padding: 8px 15px;
                                                border-radius: 15px;
                                                font-weight: bold;
                                            }
                                            QPushButton:hover {
                                                background-color: #4B0082;
                                            }
                                            """)
        import_etat_button.clicked.connect(self.import_etat_complet)
        self.theme_button = QPushButton("Changer le thème")
        self.theme_button.setStyleSheet("""
                                    QPushButton {
                                                background-color: #6C63FF;
                                                color: white;
                                                padding: 8px 15px;
                                                border-radius: 15px;
                                                font-weight: bold;
                                            }
                                            QPushButton:hover {
                                                background-color: #4B0082;
                                            }
                                            """)
        self.theme_button.clicked.connect(self.toggle_theme)
        import_button = QPushButton("Importer Matrice Disciplinaire")
        import_button.setStyleSheet("""
                                    QPushButton {
                                                background-color: #6C63FF;
                                                color: white;
                                                padding: 8px 15px;
                                                border-radius: 15px;
                                                font-weight: bold;
                                            }
                                            QPushButton:hover {
                                                background-color: #4B0082;
                                            }
                                            """)
        import_button.clicked.connect(self.show_import_window)

        settings_layout.addWidget(import_etat_button)
        settings_layout.addWidget(self.theme_button)
        settings_layout.addWidget(import_button)

        self.settings_window = QMainWindow()
        self.settings_window.setWindowTitle("Réglages")
        self.settings_window.setCentralWidget(settings_widget)
        self.settings_window.setGeometry(100, 100, 300, 200)
        self.settings_window.show()

    def show_statistics(self):
        """
        Méthode appelée lors du clic sur le bouton statistiques.
        Délègue l'ouverture au gestionnaire de statistiques.
        """
        print("Ouverture des statistiques...")  # Pour le débogage
        if hasattr(self, 'stats_handler') and self.stats_handler:
            self.stats_handler.open_statistics()
        else:
            print("Erreur: stats_handler non initialisé")  # Pour le débogage

    def closeEvent(self, event):
        """Surcharge de la méthode de fermeture pour nettoyer les ressources."""
        # Nettoyage du gestionnaire de statistiques
        if hasattr(self, 'stats_handler') and self.stats_handler:
            self.stats_handler.cleanup()

        # Appel de la méthode parente ou votre code existant de fermeture
        super().closeEvent(event)

    def toggle_theme(self):
        """Bascule entre les thèmes clair et sombre"""
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()
        # Change l'icône selon le thème
        icon_name = "dark_mode.png" if self.is_dark_mode else "light_mode.png"
        self.theme_button.setIcon(QIcon(f"../resources/icons/{icon_name}"))
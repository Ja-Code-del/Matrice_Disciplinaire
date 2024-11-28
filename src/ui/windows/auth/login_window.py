# src/ui/windows/auth/login_window.py
import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QMessageBox, QDialog,
                             QListWidget)

from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

from src.database.auth_manager import AuthManager
from src.ui.widgets.welcome_widget import WelcomeWidget


class LoginWindow(QMainWindow):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.auth_manager = AuthManager()
        self.is_first_run = self.auth_manager.check_first_run()
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Configuration Admin" if self.is_first_run else "Connexion")
        self.setFixedSize(756, 567)

        # # Chemins absolus pour les ressources
        # base_dir = Path(__file__).resolve().parent.parent
        # resources_dir = base_dir / "resources" / "icons"
        #
        # logo_path = str(resources_dir / "logo_user.png")
        # user_path = str(resources_dir / "user.png")
        # lock_path = str(resources_dir / "lock.png")

        self.setStyleSheet("""
            QWidget {
                background-color: #0f172a;
                font-family: Helvetica, -apple-system, sans-serif;
                font-size: 14px;
                color: #e2e8f0;
            }

            QLineEdit {
                background-color: #1e293b;
                border: 2px solid #334155;
                border-radius: 6px;
                padding: 8px 12px 8px 36px;
                color: #e2e8f0;
                min-height: 24px;
            }

            QLineEdit:focus {
                border-color: #3b82f6;
                background-color: #1e293b;
                outline: 2px solid #1d4ed8;
            }

            QPushButton {
                background-color: #3b82f6;
                border: none;
                border-radius: 6px;
                color: white;
                padding: 8px 16px;
                font-weight: 600;
                min-height: 40px;
            }

            QPushButton:hover {
                background-color: #2563eb;
            }

            QPushButton:pressed {
                background-color: #1d4ed8;
            }

            QPushButton#request_account_button {
                background-color: transparent;
                border: 2px solid #3b82f6;
                color: #3b82f6;
            }

            QPushButton#request_account_button:hover {
                background-color: #1e293b;
            }

            QLabel {
                color: #94a3b8;
                font-weight: 500;
            }

            QMessageBox {
                background-color: #1e293b;
                border-radius: 8px;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        # Logo
        logo_label = QLabel()
        logo_label.setPixmap(QPixmap("../resources/icons/logo_user.png").scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio,
                                                       Qt.TransformationMode.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)

        # Welcome text
        welcome_text = ("Bienvenue ! Veuillez créer le compte administrateur."
                        if self.is_first_run else "Veuillez vous connecter")
        welcome_label = QLabel(welcome_text)
        welcome_label.setStyleSheet("font-size: 18px; font-weight: 600; color: #e2e8f0; margin: 16px 0;")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(welcome_label)

        # Username field avec icône intégrée
        self.username_label = QLabel("Nom d'utilisateur:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Entrez votre nom d'utilisateur")

        username_icon = QLabel(self.username_input)
        username_icon.setPixmap(QPixmap("../resources/icons/user.png").scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio,
                                                          Qt.TransformationMode.SmoothTransformation))
        username_icon.setStyleSheet("background: transparent;")
        username_icon.move(10, 6)  # Position de l'icône dans le QLineEdit

        # Password field avec icône intégrée
        self.password_label = QLabel("Mot de passe:")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Entrez votre mot de passe")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        password_icon = QLabel(self.password_input)
        password_icon.setPixmap(QPixmap("../resources/icons/lock.png").scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio,
                                                          Qt.TransformationMode.SmoothTransformation))
        password_icon.setStyleSheet("background: transparent; text-align: center;")
        password_icon.move(10, 6)  # Position de l'icône dans le QLineEdit

        # Layout des boutons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)

        self.login_button = QPushButton("Créer Admin" if self.is_first_run else "Se connecter")
        self.login_button.clicked.connect(self.handle_login)

        if not self.is_first_run:
            self.request_account_button = QPushButton("Demander un compte")
            self.request_account_button.setObjectName("request_account_button")
            self.request_account_button.clicked.connect(self.show_request_account_dialog)
            button_layout.addWidget(self.request_account_button)

        button_layout.addWidget(self.login_button)

        # Ajout des widgets au layout principal
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addSpacing(8)
        layout.addLayout(button_layout)

        central_widget.setLayout(layout)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs")
            return

        if self.is_first_run:
            success, message = self.auth_manager.create_admin(username, password)
            if success:
                welcome = WelcomeWidget(username)
                welcome.show()
                if self.main_app:
                    self.main_app.username = username  # Set username
                    self.main_app.update_username(username)
                    self.main_app.show()
                self.close()
            else:
                QMessageBox.warning(self, "Erreur", message)
        else:
            success, user_info = self.auth_manager.verify_credentials(username, password)
            if success:
                welcome = WelcomeWidget(user_info['username'])
                welcome.show()
                if user_info["role"] == "admin":
                    # Vérifier s'il y a des demandes en attente
                    pending_requests = self.auth_manager.get_pending_requests()
                    if pending_requests:  # N'ouvre le panneau que s'il y a des demandes
                        admin_panel = AdminPanel(self.auth_manager, user_info)
                        admin_panel.exec()
                if self.main_app:
                    self.main_app.update_username(user_info['username'])  # Utilise la nouvelle méthode
                    self.main_app.show()
                self.close()
            else:
                QMessageBox.warning(self, "Erreur", "Identifiants incorrects")

    def show_request_account_dialog(self):
        dialog = RequestAccountDialog(self)
        dialog.exec()

    def show_admin_panel(self, admin_info):
        panel = AdminPanel(self.auth_manager, admin_info)
        panel.exec()


class RequestAccountDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.auth_manager = parent.auth_manager
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Demande de compte")
        self.setFixedSize(320, 240)

        layout = QVBoxLayout()

        self.username_label = QLabel("Nom d'utilisateur souhaité:")
        self.username_input = QLineEdit()

        self.password_label = QLabel("Mot de passe:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.submit_button = QPushButton("Envoyer la demande")
        self.submit_button.clicked.connect(self.submit_request)

        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def submit_request(self):
        username = self.username_input.text()
        password = self.password_input.text()

        success, message = self.auth_manager.request_account(username, password)
        if success:
            QMessageBox.information(self, "Succès",
                                    "Votre demande a été enregistrée et sera examinée par un administrateur")
            self.accept()
        else:
            QMessageBox.warning(self, "Erreur", message)


class AdminPanel(QDialog):
    def __init__(self, auth_manager, admin_info):
        super().__init__()
        self.auth_manager = auth_manager
        self.admin_info = admin_info
        self.setup_ui()
        self.load_pending_requests()

    def setup_ui(self):
        self.setWindowTitle("Panneau Administrateur")
        self.setFixedSize(500, 400)

        layout = QVBoxLayout()

        # Liste des demandes en attente
        self.requests_label = QLabel("Demandes de compte en attente:")
        self.requests_list = QListWidget()

        # Boutons d'action
        button_layout = QHBoxLayout()
        self.approve_button = QPushButton("Approuver")
        self.approve_button.clicked.connect(self.approve_selected)
        self.reject_button = QPushButton("Rejeter")
        self.reject_button.clicked.connect(self.reject_selected)

        button_layout.addWidget(self.approve_button)
        button_layout.addWidget(self.reject_button)

        layout.addWidget(self.requests_label)
        layout.addWidget(self.requests_list)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_pending_requests(self):
        self.requests_list.clear()
        requests = self.auth_manager.get_pending_requests()
        for req in requests:
            self.requests_list.addItem(f"ID: {req[0]} - Utilisateur: {req[1]} - Date: {req[2]}")

    def approve_selected(self):
        current_item = self.requests_list.currentItem()
        if current_item:
            request_id = int(current_item.text().split('-')[0].replace('ID:', '').strip())
            success, message = self.auth_manager.approve_user(request_id, self.admin_info["id"])
            if success:
                QMessageBox.information(self, "Succès", "Compte approuvé")
                self.load_pending_requests()
            else:
                QMessageBox.warning(self, "Erreur", message)

    def reject_selected(self):
        current_item = self.requests_list.currentItem()
        if current_item:
            request_id = int(current_item.text().split('-')[0].replace('ID:', '').strip())
            # Supprime simplement la demande de la base de données
            success = self.auth_manager.reject_user(request_id)
            if success:
                QMessageBox.information(self, "Succès", "Demande rejetée")
                self.load_pending_requests()
            else:
                QMessageBox.warning(self, "Erreur", "Erreur lors du rejet de la demande")
# src/ui/windows/auth/login_window.py
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QMessageBox, QDialog,
                             QListWidget)
from PyQt6.QtCore import Qt
from src.database.auth_manager import AuthManager


class LoginWindow(QMainWindow):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.auth_manager = AuthManager()
        self.is_first_run = self.auth_manager.check_first_run()
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Configuration Admin" if self.is_first_run else "Connexion")
        self.setFixedSize(400, 250)

        self.setStyleSheet("""
                    /* Général */
            QWidget {
                background-color: #f4f4f4;
                font-family: 'Arial', sans-serif;
                font-size: 14px;
                color: #333;
            }
            
            /* QLineEdit - Style des champs de texte */
            QLineEdit {
                background-color: #fff;
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                color: #333;
            }
            
            /* Focus sur QLineEdit */
            QLineEdit:focus {
                border: 1px solid #0078d4;
                box-shadow: 0 0 5px rgba(0, 120, 212, 0.5);
                background-color: #f9f9f9;
            }
            
            /* QPushButton */
            QPushButton {
                background-color: #0078d4;
                border: none;
                border-radius: 8px;
                color: white;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #005bb5;
            }
            
            QPushButton:pressed {
                background-color: #004b99;
                border: 1px solid #003e80;
            }
            
            /* QLabel */
            QLabel {
                font-size: 14px;
                color: #444;
            }
            
            /* QMessageBox */
            QMessageBox {
                background-color: #fff;
                border-radius: 10px;
            }
            
            /* Scrollbars */
            QScrollBar:vertical {
                border: none;
                background: #eaeaea;
                width: 8px;
                margin: 0px 0px 0px 0px;
            }
            
            QScrollBar::handle:vertical {
                background: #0078d4;
                border-radius: 4px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: #005bb5;
            }
            
            QScrollBar::handle:vertical:pressed {
                background: #004b99;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        # Message d'accueil
        welcome_text = ("Bienvenue ! Veuillez créer le compte administrateur."
                        if self.is_first_run else "Veuillez vous connecter")
        welcome_label = QLabel(welcome_text)
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(welcome_label)

        # Champs de connexion
        self.username_label = QLabel("Nom d'utilisateur:")
        self.username_input = QLineEdit()

        self.password_label = QLabel("Mot de passe:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        # Boutons
        button_layout = QHBoxLayout()
        self.login_button = QPushButton("Créer Admin" if self.is_first_run else "Se connecter")
        self.login_button.clicked.connect(self.handle_login)

        if not self.is_first_run:
            self.request_account_button = QPushButton("Demander un compte")
            self.request_account_button.clicked.connect(self.show_request_account_dialog)
            button_layout.addWidget(self.request_account_button)

        button_layout.addWidget(self.login_button)

        # Ajout des widgets au layout
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addLayout(button_layout)

        central_widget.setLayout(layout)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if self.is_first_run:
            success, message = self.auth_manager.create_admin(username, password)
            if success:
                QMessageBox.information(self, "Succès", "Compte administrateur créé avec succès")
                self.main_app.show()
                self.close()
            else:
                QMessageBox.warning(self, "Erreur", message)
        else:
            success, user_info = self.auth_manager.verify_credentials(username, password)
            try:
                if success:
                    if user_info["role"] == "admin":
                        self.show_admin_panel(user_info)
                    self.main_app.show()
                    self.close()
                else:
                    QMessageBox.warning(self, "Erreur", "Identifiants incorrects")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Une erreur est survenue : {str(e)}")

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
        self.setFixedSize(300, 200)

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
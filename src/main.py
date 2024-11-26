from PyQt6.QtWidgets import QApplication
from src.ui.windows.auth.login_window import LoginWindow
from src.ui.main_window import MainGendarmeApp
from src.database.auth_manager import AuthManager
import sys

def init_application():
    """Ínitialise l'application et la base de donnees"""
    auth_manager = AuthManager()
    return auth_manager.check_first_run()


def main():
    app = QApplication(sys.argv)

    #Fenetre principale
    main_window = MainGendarmeApp()

    #Fenetre de Login
    login_window = LoginWindow(main_window)
    login_window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()

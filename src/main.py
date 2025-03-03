from PyQt6.QtWidgets import QApplication
# from src.ui.styles.styles import SPACE_GROTESK_LIGHT
from src.database.init_db import initialize_reference_tables
#from src.ui.windows.auth.login_window import LoginWindow
from src.ui.main_window import MainGendarmeApp
from src.database.auth_manager import AuthManager

import sys

def init_application():
    """Ínitialise l'application et la base de donnees"""
    auth_manager = AuthManager()
    return auth_manager.check_first_run()


def main():
    app = QApplication(sys.argv)
    initialize_reference_tables()
    #Fenetre principale
    main_window = MainGendarmeApp()
    main_window.show()

    #Fenetre de Login
    #login_window = LoginWindow(main_window)
    #login_window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()

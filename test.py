import sys
from PyQt6.QtWidgets import QApplication
from src.ui.import_window import ImportWindow
from src.ui.main_window import MainGendarmeApp


def test_import():
    """Test de la fenêtre d'import"""
    app = QApplication(sys.argv)
    window = ImportWindow()
    window.show()
    app.exec()


def test_main():
    """Test de la fenêtre principale"""
    app = QApplication(sys.argv)
    window = MainGendarmeApp()
    window.show()
    app.exec()


if __name__ == "__main__":
    print("1. Tester la fenêtre d'import")
    print("2. Tester la fenêtre principale")
    choice = input("Choisissez une option (1 ou 2) : ")

    if choice == "1":
        test_import()
    elif choice == "2":
        test_main()
    else:
        print("Option invalide")
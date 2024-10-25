import sys
from src.ui.main_window import MainGendarmeApp
from PyQt6.QtWidgets import QApplication


def main():
    app = QApplication(sys.argv)
    window = MainGendarmeApp()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

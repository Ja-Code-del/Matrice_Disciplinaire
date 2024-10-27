from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget


class FaultStatsWindow(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setWindowTitle("Types de Fautes")
        self.setMinimumSize(1200, 800)

        # Widget central
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Label temporaire
        layout.addWidget(QLabel("Types de Fautes - En construction"))
from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget


class GradeStatsWindow(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setWindowTitle("Statistiques par Grade")
        self.setMinimumSize(1200, 800)

        # Widget central
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Label temporaire
        layout.addWidget(QLabel("Stats par Grade - En construction"))
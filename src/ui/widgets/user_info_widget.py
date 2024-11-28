from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QLabel,
                            QVBoxLayout, QFrame)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt

class UserInfoWidget(QWidget):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.username = username
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(10, 5, 15, 5)

        # Création de l'icône utilisateur avec QPixmap
        icon_label = QLabel()
        pixmap = QPixmap("../resources/icons/user.png")
        scaled_pixmap = pixmap.scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        icon_label.setPixmap(scaled_pixmap)

        # Label pour le nom d'utilisateur
        username_label = QLabel(self.username)
        #username_label.setFont(QFont("Helvetica", 1))
        username_label.setStyleSheet("""
                                    color: #000000;
                                    font-weight: bold;
                                    font-family: "Apple SD Gothic Neo", "Segoe UI", system-ui, -apple-system, sans-serif;
                                    font-size: 18px   
                                     """)

        # Container avec bordure arrondie
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 5px;
            }
            QFrame:hover {
                background-color: #e9ecef;
            }
        """)
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(8, 4, 8, 4)
        container_layout.addWidget(icon_label)
        container_layout.addWidget(username_label)

        layout.addWidget(container)
        layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.setLayout(layout)
# src/ui/widgets/welcome_widget.py
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QRect
from PyQt6.QtGui import QPainter, QLinearGradient, QColor, QFont


class WelcomeWidget(QWidget):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.username = username
        self.setup_ui()
        self.setup_animation()

    def setup_ui(self):
        # Configuration de base du widget
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(640, 480)

        # Centrer le widget sur l'écran
        screen_geometry = self.screen().geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

        # Layout principal
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Label de bienvenue
        welcome_label = QLabel(f"Bienvenue sur GendTrack\n\n{self.username}")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setFont(QFont("Helvetica", 36, QFont.Weight.Bold))
        welcome_label.setStyleSheet("color: white;")

        layout.addWidget(welcome_label)
        self.setLayout(layout)

        # Timer pour fermer le widget
        QTimer.singleShot(3000, self.start_fade_out)

    def setup_animation(self):
        self.opacity = 1.0
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(500)
        self.fade_animation.finished.connect(self.close)

    def start_fade_out(self):
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Créer le gradient
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor("#111111"))
        gradient.setColorAt(0.46, QColor("#333333"))
        gradient.setColorAt(1, QColor("#111111"))

        # Dessiner le rectangle arrondi avec le gradient
        rect = self.rect().adjusted(20, 20, -20, -20)  # Marges de 20px
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(gradient)
        painter.drawRoundedRect(rect, 15, 15)  # Coins arrondis de 15px
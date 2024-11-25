class ThemeColors:
    """Couleurs pour les thèmes clair et sombre"""

    LIGHT = {
        'background': '#ffffff',  # blanc pur
        'surface': '#f2f2f7',  # gris clair pour les surfaces
        'primary': '#007aff',  # bleu standard Apple
        'primary_hover': '#005ecb',  # bleu plus foncé pour le hover
        'text': '#1c1c1e',  # gris foncé pour le texte principal
        'text_secondary': '#8e8e93',  # gris moyen pour le texte secondaire
        'border': '#d1d1d6',  # gris clair pour les bordures
        'error': '#ff3b30',  # rouge vif pour les erreurs
        'success': '#34c759'  # vert vif pour les succès
    }

    DARK = {
        'background': '#000000',  # noir pur pour le fond
        'surface': '#1c1c1e',  # gris foncé pour les surfaces
        'primary': '#0a84ff',  # bleu vif Apple pour le primaire
        'primary_hover': '#0066cc',  # bleu foncé pour le hover
        'text': '#ffffff',  # blanc pour le texte principal
        'text_secondary': '#8e8e93',  # gris pour le texte secondaire
        'border': '#3a3a3c',  # gris foncé pour les bordures
        'error': '#ff453a',  # rouge vif Apple pour les erreurs
        'success': '#30d158'  # vert Apple pour les succès
    }


class Styles:
    """Classe pour gérer les styles de l'application"""

    @staticmethod
    def get_styles(is_dark_mode=False):
        """Retourne les styles selon le mode choisi"""
        colors = ThemeColors.DARK if is_dark_mode else ThemeColors.LIGHT

        return {
            'MAIN_WINDOW': f"""
                QMainWindow {{
                    background-color: {colors['background']};
                    color: {colors['text']};
                }}
            """,

            'BUTTON': f"""
                QPushButton {{
                    background-color: {colors['primary']};
                    color: #ffffff;
                    padding: 8px 20px;
                    border: none;
                    border-radius: 4px;
                    font-size: 14px;
                    min-width: 100px;
                }}
                QPushButton:hover {{
                    background-color: {colors['primary_hover']};
                }}
            """,

            'INPUT': f"""
                QLineEdit {{
                    padding: 8px;
                    background-color: {colors['surface']};
                    color: {colors['text']};
                    border: 1px solid {colors['border']};
                    border-radius: 4px;
                    min-width: 300px;
                }}
                QLineEdit:focus {{
                    border-color: {colors['primary']};
                }}
            """,

            'COMBO_BOX': f"""
                QComboBox {{
                    padding: 11px 20px;
                    border: 1px solid {colors['border']};
                    border-radius: 5px;
                    background: {colors['surface']};
                    min-width: 300px;
                    font-size: 14px;
                    color: {colors['text']};
                }}
                QComboBox:hover {{
                    border-color: {colors['primary']};
                }}
                QComboBox::drop-down {{
                    border: none;
                    padding-right: 15px;
                }}
                QComboBox::down-arrow {{
                    image: url(../resources/icons/down_arrow.png);
                    width: 18px;
                    height: 18px;
                }}
                QComboBox QAbstractItemView {{
                    border: 1px solid {colors['border']};
                    border-radius: 5px;
                    background: {colors['surface']};
                    color: {colors['text']};
                }}
                QComboBox QAbstractItemView::item:hover {{
                    background-color: {colors['primary'] + '20'}; 
                    color: {colors['primary']};
                }}
            """,

            'SPIN_BOX': f"""
                QSpinBox {{
                    padding: 11px 20px;
                    border: 2px solid {colors['border']};
                    border-radius: 5px;
                    background: {colors['surface']};
                    min-width: 300px;
                    font-size: 14px;
                    color: {colors['text']};
                }}
                QSpinBox:hover {{
                    border-color: {colors['primary']};
                }}
                QSpinBox::up-button, QSpinBox::down-button {{
                    width: 25px;
                    background: {colors['primary']};
                    border-radius: 3px;
                }}
                QSpinBox::up-arrow {{
                    image: url(../resources/icons/up_arrow.png);
                    width: 18px;
                    height: 18px;
                }}
                QSpinBox::down-arrow {{
                    image: url(../resources/icons/down_arrow.png);
                    width: 18px;
                    height: 18px;
                }}
            """,

            'DATE_EDIT': f"""
                QDateEdit {{
                    padding: 11px 22px;
                    border: 1px solid {colors['border']};
                    border-radius: 8px;
                    background: {colors['surface']};
                    color: {colors['text']};
                }}
                QDateEdit::drop-down {{
                    border: none;
                    width: 20px;
                    padding-right: 20px;
                    border-radius: 0px 8px 8px 0px;
                }}
                QDateEdit::down-arrow {{
                    image: url(../resources/icons/calendar.png);
                    width: 18px;
                    height: 18px;
                }}
                QDateEdit:hover {{
                    border: 1px solid #a4b3c9;
                }}
            """,

            'TABLE': f"""
                QTableWidget {{
                    background-color: {colors['surface']};
                    color: {colors['text']};
                    gridline-color: {colors['border']};
                    border: none;
                }}
                QHeaderView::section {{
                    background-color: {colors['background']};
                    color: {colors['text']};
                    padding: 8px;
                    border: none;
                    border-bottom: 1px solid {colors['border']};
                }}
                QTableWidget QScrollBar {{
                    background-color: {colors['surface']};
                    width: 14px;
                    margin: 0px
                }}
                QTableWidget QScrollBar::handle {{
                    background-color: {colors['border']};
                    border-radius: 7px;
                    min-height: 30px;
                }}
                QTableWidget QScrollBar::handle:hover {{
                    background-color: {colors['primary']};
                }}
            """,

            'GROUP_BOX': f"""
                QGroupBox {{
                    background-color: {colors['surface']};
                    color: {colors['text']};
                    border: 1px solid {colors['border']};
                    border-radius: 4px;
                    margin-top: 1em;
                    padding: 15px;
                }}
                QGroupBox::title {{
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 15px;
                    letter-spacing: 0.5px;
                    color: {colors['text']};
                    font: bold 36px; "Helvetica Neue";
                }}
            """,

            'INFO_LABEL': f"""
                QLabel {{
                    padding: 5px;
                    background-color: {colors['surface']};
                    color: {colors['text']};
                    border-radius: 3px;
                }}
            """,

            'THEME_BUTTON': f"""
                QPushButton {{
                    background-color: transparent;
                    border: 1px solid {colors['border']};
                    border-radius: 4px;
                    padding: 5px;
                    icon-size: 20px 20px;
                }}
                QPushButton:hover {{
                    background-color: {colors['surface']};
                }}
            """,

            'STATUS_BAR': f"""
                QStatusBar {{
                    background-color: {colors['background']};
                    color: {colors['text_secondary']};
                }}
            """,

            'SURFACE_COLOR': colors['surface'],
            'TEXT_COLOR': colors['text'],

            'LABEL': f"""
                QLabel {{
                    color: {colors['text']};
                }}
            """
        }

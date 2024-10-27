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


    # LIGHT = {
    #     'background': '#ffffff',
    #     'surface': '#f8f9fa',
    #     'primary': '#007bff',
    #     'primary_hover': '#0056b3',
    #     'text': '#212529',
    #     'text_secondary': '#6c757d',
    #     'border': '#dee2e6',
    #     'error': '#dc3545',
    #     'success': '#28a745'
    # }
    #
    # DARK = {
    #     'background': '#1e1e1e',
    #     'surface': '#2d2d2d',
    #     'primary': '#007acc',
    #     'primary_hover': '#0098ff',
    #     'text': '#ffffff',
    #     'text_secondary': '#b0b0b0',
    #     'border': '#404040',
    #     'error': '#ff4444',
    #     'success': '#00c853'
    # }


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
                    color: {'#ffffff' if is_dark_mode else '#ffffff'};
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
                    padding: 8px;
                    background-color: {colors['surface']};
                    color: {colors['text']};
                    border: 1px solid {colors['border']};
                    border-radius: 4px;
                    min-width: 150px;
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
                    margin: 0px;
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
                    color: {colors['text']};
                    font-size: 16px;
                    font-weight: bold;
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
    # def get_styles(is_dark_mode=False):
    #     """Retourne les styles selon le mode choisi"""
    #     colors = ThemeColors.DARK if is_dark_mode else ThemeColors.LIGHT
    #
    #     return {
    #         'MAIN_WINDOW': f"""
    #             QMainWindow {{
    #                 background-color: {colors['background']};
    #                 color: {colors['text']};
    #             }}
    #         """,
    #
    #         'BUTTON': f"""
    #             QPushButton {{
    #                 background-color: {colors['primary']};
    #                 color: {'#ffffff' if is_dark_mode else '#ffffff'};
    #                 padding: 8px 20px;
    #                 border: none;
    #                 border-radius: 4px;
    #                 font-size: 14px;
    #                 min-width: 100px;
    #             }}
    #             QPushButton:hover {{
    #                 background-color: {colors['primary_hover']};
    #             }}
    #         """,
    #
    #         'INPUT': f"""
    #             QLineEdit {{
    #                 padding: 8px;
    #                 background-color: {colors['surface']};
    #                 color: {colors['text']};
    #                 border: 1px solid {colors['border']};
    #                 border-radius: 4px;
    #                 min-width: 300px;
    #             }}
    #             QLineEdit:focus {{
    #                 border-color: {colors['primary']};
    #             }}
    #         """,
    #
    #         'COMBO_BOX': f"""
    #             QComboBox {{
    #                 padding: 8px;
    #                 background-color: {colors['surface']};
    #                 color: {colors['text']};
    #                 border: 1px solid {colors['border']};
    #                 border-radius: 4px;
    #                 min-width: 150px;
    #             }}
    #         """,
    #
    #         'TABLE': f"""
    #             QTableWidget {{
    #                 background-color: {colors['surface']};
    #                 color: {colors['text']};
    #                 gridline-color: {colors['border']};
    #                 border: none;
    #             }}
    #             QHeaderView::section {{
    #                 background-color: {colors['background']};
    #                 color: {colors['text']};
    #                 padding: 8px;
    #                 border: none;
    #                 border-bottom: 1px solid {colors['border']};
    #             }}
    #         """,
    #
    #         'GROUP_BOX': f"""
    #             QGroupBox {{
    #                 background-color: {colors['surface']};
    #                 color: {colors['text']};
    #                 border: 1px solid {colors['border']};
    #                 border-radius: 4px;
    #                 margin-top: 1em;
    #                 padding: 15px;
    #             }}
    #             QGroupBox::title {{
    #                 subcontrol-origin: margin;
    #                 color: {colors['text']};
    #             }}
    #         """,
    #
    #         'INFO_LABEL': f"""
    #             QLabel {{
    #                 padding: 5px;
    #                 background-color: {colors['surface']};
    #                 color: {colors['text']};
    #                 border-radius: 3px;
    #             }}
    #         """,
    #
    #         'THEME_BUTTON': f"""
    #             QPushButton {{
    #                 background-color: transparent;
    #                 border: 1px solid {colors['border']};
    #                 border-radius: 4px;
    #                 padding: 5px;
    #                 icon-size: 20px 20px;
    #             }}
    #             QPushButton:hover {{
    #                 background-color: {colors['surface']};
    #             }}
    #         """,
    #
    #         # Ajout du style manquant pour la barre de statut
    #         'STATUS_BAR': f"""
    #             QStatusBar {{
    #                 background-color: {colors['background']};
    #                 color: {colors['text_secondary']};
    #             }}
    #         """
    #         'SURFACE_COLOR': '#2d2d2d' if is_dark_mode else '#f8f9fa',
    #         'TEXT_COLOR': 'white' if is_dark_mode else '#333333',
    #
    #          'INFO_LABEL': f"""
    #             QLabel {{
    #                 padding: 5px;
    #                 background-color: {colors['surface']};
    #                 color: {'white' if is_dark_mode else '#333333'};
    #                 border-radius: 3px;
    #             }}
    #          """
    #     }
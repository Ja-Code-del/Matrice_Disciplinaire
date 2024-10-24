class Styles:
    """Classe contenant tous les styles CSS de l'application"""

    # Style pour les boutons de recherche et d'action
    SEARCH_BUTTON = """
        QPushButton {
            background-color: #007bff;
            color: white;
            padding: 8px 20px;
            border: none;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #0056b3;
        }
    """

    # Style pour les champs de saisie
    SEARCH_INPUT = """
        QLineEdit {
            padding: 8px;
            border: 2px solid #ccc;
            border-radius: 4px;
            min-width: 300px;
        }
        QLineEdit:focus {
            border-color: #007bff;
        }
    """

    # Style pour les combos box
    COMBO_BOX = """
        QComboBox {
            padding: 8px;
            border: 2px solid #ccc;
            border-radius: 4px;
            min-width: 150px;
        }
    """

    # Style pour les tableaux
    TABLE = """
        QTableWidget {
            gridline-color: #ddd;
            border: none;
        }
        QHeaderView::section {
            background-color: #f8f9fa;
            padding: 6px;
            font-weight: bold;
            border: none;
            border-bottom: 1px solid #ddd;
        }
    """

    # Style pour les labels d'information
    INFO_LABEL = """
        QLabel {
            padding: 5px;
            background: #f8f9fa;
            border-radius: 3px;
            min-width: 200px;
        }
    """

    # Style pour les groupes
    GROUP_BOX = """
        QGroupBox {
            border: 1px solid #ddd;
            border-radius: 4px;
            margin-top: 1em;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            padding: 0 5px;
            color: #495057;
        }
    """
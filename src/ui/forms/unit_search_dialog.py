from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QListWidget, QAbstractItemView
from src.data.gendarmerie.structure import get_all_unit_names, get_unit_by_name
from src.data.gendarmerie.structure import STRUCTURE_UNITE


class UnitSearchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Recherche d'unité")
        self.setMinimumSize(600, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Rechercher une unité")
        self.search_field.textChanged.connect(self.filter_units)
        layout.addWidget(self.search_field)

        self.units_list = QListWidget()
        self.units_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.units_list.itemClicked.connect(self.on_unit_selected_in_dialog)
        layout.addWidget(self.units_list)

        self.filter_units("")

    def filter_units(self, search_text):
        self.units_list.clear()
        matching_units = [unit for unit in get_all_unit_names(STRUCTURE_UNITE) if search_text.lower() in unit.lower()]
        self.units_list.addItems(matching_units)

    def get_selected_unit(self):
        selected_items = self.units_list.selectedItems()
        print(selected_items[0].text())
        if selected_items:
            return selected_items[0].text()
        return None

    def on_unit_selected_in_dialog(self, item):
        self.accept()
        unit_name = item.text()
        self.parent().on_unit_selected(unit_name)

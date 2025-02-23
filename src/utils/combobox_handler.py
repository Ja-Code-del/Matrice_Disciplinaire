from typing import List, Dict, Optional, Any
from PyQt6.QtWidgets import QComboBox
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ComboBoxHandler:
    """Gestionnaire centralisé des ComboBox pour l'application"""

    def __init__(self, db_manager):
        self.db_manager = db_manager

    def setup_static_combobox(self, combobox: QComboBox, items: List[str], default_index: int = 0):
        """
        Configure une combobox avec des données statiques
        Args:
            combobox: La combobox à configurer
            items: Liste des éléments à ajouter
            default_index: Index de l'élément par défaut
        """
        try:
            combobox.clear()
            combobox.addItems(items)
            if 0 <= default_index < len(items):
                combobox.setCurrentIndex(default_index)
        except Exception as e:
            logger.error(f"Erreur lors de la configuration de la combobox statique : {str(e)}")

    def setup_db_combobox(self, combobox: QComboBox, table: str, value_column: str,
                          id_column: str = None, where_clause: str = None,
                          order_by: str = None) -> bool:
        """
        Configure une combobox avec des données de la base
        Args:
            combobox: La combobox à configurer
            table: Nom de la table
            value_column: Colonne contenant les valeurs à afficher
            id_column: Colonne contenant les IDs (optionnel)
            where_clause: Clause WHERE (optionnel)
            order_by: Clause ORDER BY (optionnel)
        Returns:
            bool: True si succès, False sinon
        """
        try:
            combobox.clear()

            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                query = f"SELECT {id_column + ', ' if id_column else ''}{value_column} FROM {table}"
                if where_clause:
                    query += f" WHERE {where_clause}"
                if order_by:
                    query += f" ORDER BY {order_by}"

                cursor.execute(query)
                results = cursor.fetchall()

                if id_column:
                    for id_val, text in results:
                        combobox.addItem(str(text), id_val)
                else:
                    combobox.addItems([str(row[0]) for row in results])

            return True
        except Exception as e:
            logger.error(f"Erreur lors du chargement des données pour {table}: {str(e)}")
            return False

    def load_hierarchical_data(self, child_combo: QComboBox, table: str,
                               value_column: str, parent_column: str,
                               parent_value: Any) -> bool:
        """
        Charge les données hiérarchiques dans une combobox enfant
        Args:
            child_combo: ComboBox enfant à remplir
            table: Nom de la table
            value_column: Colonne contenant les valeurs à afficher
            parent_column: Colonne contenant la référence au parent
            parent_value: Valeur du parent
        Returns:
            bool: True si succès, False sinon
        """
        try:
            child_combo.clear()

            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                query = f"""
                    SELECT DISTINCT {value_column} 
                    FROM {table} 
                    WHERE {parent_column} = ?
                    ORDER BY {value_column}
                """
                cursor.execute(query, (parent_value,))
                results = cursor.fetchall()

                child_combo.addItems([row[0] for row in results])
            return True
        except Exception as e:
            logger.error(f"Erreur lors du chargement des données hiérarchiques : {str(e)}")
            return False

    def set_value_by_id(self, combobox: QComboBox, id_value: int) -> bool:
        """
        Sélectionne un élément par son ID
        Args:
            combobox: La combobox
            id_value: L'ID à sélectionner
        Returns:
            bool: True si trouvé et sélectionné, False sinon
        """
        index = combobox.findData(id_value)
        if index >= 0:
            combobox.setCurrentIndex(index)
            return True
        return False

    def set_value_by_text(self, combobox: QComboBox, text: str) -> bool:
        """
        Sélectionne un élément par son texte
        Args:
            combobox: La combobox
            text: Le texte à sélectionner
        Returns:
            bool: True si trouvé et sélectionné, False sinon
        """
        index = combobox.findText(text)
        if index >= 0:
            combobox.setCurrentIndex(index)
            return True
        return False

    def get_selected_id(self, combobox: QComboBox) -> Optional[int]:
        """
        Récupère l'ID de l'élément sélectionné
        Args:
            combobox: La combobox
        Returns:
            int: L'ID sélectionné ou None
        """
        try:
            # Debug de la combobox
            print(f"ComboBox {combobox.objectName()}:")
            print(f"- Texte actuel: {combobox.currentText()}")
            print(f"- Index actuel: {combobox.currentIndex()}")
            print(f"- Data actuelle: {combobox.currentData()}")

            # Si aucun élément n'est sélectionné ou si la combobox est vide
            if combobox.currentIndex() == -1 or not combobox.currentText().strip():
                return None

            current_id = combobox.currentData()
            if current_id is not None:
                return int(current_id)

            # Si pas d'ID stocké, essayer de le récupérer depuis la base
            return self.get_foreign_key_id_by_value(
                combobox.property("table_name"),
                combobox.property("value_column"),
                combobox.currentText().strip()
            )
        except Exception as e:
            print(f"Erreur dans get_selected_id: {str(e)}")
            return None

    def get_foreign_key_id_by_value(self, table: str, value_column: str, value: str) -> Optional[int]:
        """
        Récupère l'ID d'une valeur dans une table
        Args:
            table: Nom de la table
            value_column: Nom de la colonne contenant la valeur
            value: Valeur à rechercher
        Returns:
            int: ID trouvé ou None
        """
        try:
            # Mapping des tables vers leurs colonnes ID
            id_columns = {
                'Grade': 'id_grade',
                'Sit_mat': 'id_sit_mat',
                'Unite': 'id_unite',
                'Legion': 'id_legion',
                'Subdiv': 'id_subdiv',
                'Region': 'id_rg',
                'Fautes': 'id_faute',
                'Statut': 'id_statut',  # Ajout de la table Statut
                'Categories': 'id_categorie',
                'Type_sanctions': 'id_type_sanction'
            }

            if table not in id_columns:
                print(f"Table {table} non trouvée dans le mapping")
                return None

            id_column = id_columns[table]

            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                query = f"SELECT {id_column} FROM {table} WHERE {value_column} = ?"
                print(f"Exécution de la requête: {query} avec la valeur: {value}")  # Debug

                cursor.execute(query, (value,))
                result = cursor.fetchone()

                if result:
                    return result[0]
                print(f"Aucun résultat trouvé pour {value} dans {table}")  # Debug
                return None

        except Exception as e:
            print(f"Erreur dans get_foreign_key_id_by_value pour {table}.{value_column}={value}: {str(e)}")
            return None
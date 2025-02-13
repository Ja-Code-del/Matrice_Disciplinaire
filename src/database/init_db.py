# init_db.py
from src.database.db_manager import DatabaseManager
from src.data.gendarmerie.utilities import (RANKS_ITEMS, SANCTIONS_ITEMS, FAULT_ITEMS, CATEGORIES_ITEMS, STATUT_ITEMS,
                                            UNITS_ITEMS, LEGIONS_ITEMS, SUBDIV_ITEMS, REGION_ITEMS)


def insert_if_empty(db, table, column, values):
    """
    Insère les valeurs dans `table` si elles n'existent pas.
    """
    db = DatabaseManager()

    print(f"🔄 Traitement de la table {table}...")
    for value in values:
        try:
            print(f"  ⏳ Tentative d'insertion de '{value}'...")
            if not db.get_foreign_key_id(table, column, value):
                db.add_data(table, {column: value})
                print(f"  ✅ '{value}' ajouté à {table}")
            else:
                print(f"  ℹ️ '{value}' existe déjà dans {table}")
        except Exception as e:
            print(f"  ❌ Erreur lors de l'insertion de '{value}' dans {table}: {str(e)}")
            raise


# def insert_if_empty(db, table, column, values):
#     """
#     Insère les valeurs dans `table` si elles n'existent pas.
#     :param db: Instance de DBManager
#     :param table: Nom de la table
#     :param column: Nom de la colonne contenant les valeurs
#     :param values: Liste des valeurs à insérer
#     """
#
#     db = DatabaseManager()
#
#     for value in values:
#         if not db.get_foreign_key_id(table, column, value):  # Vérifie si la valeur existe déjà
#             db.add_data(table, {column: value})
#             print(f"✅ {value} ajouté à {table}")

def initialize_reference_tables():
    """Remplit les tables de référence si elles sont vides"""
    db = DatabaseManager()

    # Créer les tables si elles n'existent pas
    db.create_tables()

    # Créer les index
    db.create_indexes()

    insert_if_empty(db, "Grade", "lib_grade", RANKS_ITEMS)
    insert_if_empty(db, "Type_sanctions", "lib_type_sanction", SANCTIONS_ITEMS)
    insert_if_empty(db, "Fautes", "lib_faute", FAULT_ITEMS)
    insert_if_empty(db, "Categories", "lib_categorie", CATEGORIES_ITEMS)
    insert_if_empty(db, "Statut", "lib_statut", STATUT_ITEMS)
    insert_if_empty(db, "Unite", "lib_unite", UNITS_ITEMS)
    insert_if_empty(db, "Legion", "lib_legion", LEGIONS_ITEMS)
    insert_if_empty(db, "Subdiv", "lib_subdiv", SUBDIV_ITEMS)
    insert_if_empty(db, "Region", "lib_rg", REGION_ITEMS)

    db.close()
    print("🎯 Initialisation terminée.")
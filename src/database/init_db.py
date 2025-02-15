# init_db.py
from src.database.db_manager import DatabaseManager
from src.data.gendarmerie.utilities import (RANKS_ITEMS, SANCTIONS_ITEMS, FAULT_ITEMS, CATEGORIES_ITEMS, STATUT_ITEMS,
                                            UNITS_ITEMS, LEGIONS_ITEMS, SUBDIV_ITEMS, REGION_ITEMS)


def insert_if_empty(db, table, column, values):
    """
    Insère les valeurs dans `table` si elles n'existent pas.
    """
    db = DatabaseManager()

    print("🔄 Initialisation des tables de référence...")

    # Étape 1 : Insérer les catégories (DOIT être fait avant les fautes)
    print("🔄 Traitement de la table Categories...")
    categories = {3: CATEGORIES_ITEMS[2], 2: CATEGORIES_ITEMS[2] , 4: CATEGORIES_ITEMS[3]}  # Juste pour info, on stocke les libellés
    for cat_id, lib_categorie in categories.items():
        db.add_data("Categories", {"id_categorie": cat_id, "lib_categorie": lib_categorie})
        print(f"✅ Catégorie {cat_id} ({lib_categorie}) ajoutée à Categories")

    # Étape 2 : Insérer les fautes avec les bonnes catégories (numériques)
    print("🔄 Traitement de la table Fautes...")
    fautes = [
        ("ABSENCE IRREGULIERE PROLONGEE", 3),
        ("FAUTE CONTRE L'HONNEUR", 2),
        ("NON - RESPECT DES CONSIGNES", 3),
        ("ABSENCE IRREGULIERE", 3),
        ("ABANDON DE POSTE", 3),
        ("FAUTE DE COMPORTEMENT", 4),
        ("FAUTE ET NEGLIGENCE PROFESSIONNELLE", 3)
    ]

    for lib_faute, cat_id in fautes:
        try:
            db.add_data("Fautes", {"lib_faute": lib_faute, "cat_id": cat_id})
            print(f"✅ {lib_faute} ajouté à Fautes (catégorie {cat_id})")
        except Exception as e:
            print(f"❌ Erreur lors de l'insertion de '{lib_faute}' : {e}")

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
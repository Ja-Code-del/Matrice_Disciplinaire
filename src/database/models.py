from dataclasses import dataclass, asdict
from datetime import datetime, date
from typing import Optional, List, Dict, Any


@dataclass
class Gendarmes:
    """Classe représentant un enregistrement de la table Gendarmes"""
    id_gendarme : int = None
    matricule : str = ""
    nom_prenoms : str = ""
    age : int = None
    sexe : str = ""
    date_entree_gie : date = None
    nb_enfants : Optional[int] = None

    def to_dict(self):
        """Retourne un dictionnaire sans les clés nulles"""
        return {k: v for k, v in asdict(self).items() if v is not None}

class GendarmesRepository:
    """Classe pour gerer les opérations dans la table gendarme"""
    def __init__(self, db_manager):
        self.db_manager = db_manager

@dataclass
class Dossiers:
    """Classe représentant un enregistrement de la table Dossiers"""
    numero_inc : int = None
    id_dossier : str = ""
    matricule_dossier : str = ""
    reference : str = ""
    date_enr : date = None
    date_faits : date = None
    numero_annee : int = None
    annee_enr : int = None
    sanction_id : int = None
    grade_id : int = None
    situation_mat_id : int = None
    unite_id : int = None
    legion_id : int = None
    subdiv_id : int = None
    rg_id : int = None
    faute_id : int = None
    libelle : str = ""
    statut_id : int = None

    def to_dict(self):
        """Retourne un dictionnaire sans les clés nulles"""
        return {k: v for k, v in asdict(self).items() if v is not None}

class DossiersRepository:
    """Classe pour gerer les méthodes dans Dossiers"""
    def __init__(self, db_manager):
        self.db_manager = db_manager

@dataclass
class Sanctions:
    """Classe représentant un enregistrement de la table Sanctions"""
    id_sanction : int = None
    type_sanction_id : int = None
    num_inc : int = None
    taux : str = ""
    numero_decision : str = ""
    numero_arrete : str = ""
    annee_radiation : int = None
    ref_statut : str = ""
    comite : str = ""

    def to_dict(self):
        """Retourne un dictionnaire sans les clés nulles"""
        return {k: v for k, v in asdict(self).items() if v is not None}

class SanctionsRepository:
    """Classe pour gérer les opérations dans Sanctions"""
    def __init__(self, db_manager):
        self.db_manager = db_manager

@dataclass
class Statut:
    """Classe représentant un enregistrement de la table Statut"""
    id_statut : int = None
    lib_statut : str = ""

    def to_dict(self):
        """Retourne un dictionnaire sans les clés nulles"""
        return {k: v for k, v in asdict(self).items() if v is not None}

@dataclass
class Type_sanctions:
    """Classe représentant un enregistrement de la table Type_sanctions"""
    id_type_sanction : int = None
    lib_type_sanction : str = ""

    def to_dict(self):
        """Retourne un dictionnaire sans les clés nulles"""
        return {k: v for k, v in asdict(self).items() if v is not None}

@dataclass
class Fautes:
    """Classe représentant un enregistrement de la table Fautes"""
    id_faute : int = None
    lib_faute : str = ""
    cat_id : int = None

    def to_dict(self):
        """Retourne un dictionnaire sans les clés nulles"""
        return {k: v for k, v in asdict(self).items() if v is not None}

@dataclass
class Categories:
    """Classe représentant un enregistrement de la table Categories"""
    id_categorie : int = None
    lib_categorie : str = ""

    def to_dict(self):
        """Retourne un dictionnaire sans les clés nulles"""
        return {k: v for k, v in asdict(self).items() if v is not None}

@dataclass
class Grades:
    """Classe représentant un enregistrement de la table Grades"""
    id_grade: int = None
    lib_grade: str = ""

    def to_dict(self):
        """Retourne un dictionnaire sans les clés nulles"""
        return {k: v for k, v in asdict(self).items() if v is not None}
@dataclass
class Sit_mat:
    """Classe représentant un enregistrement de la table Sit_mat"""
    id_sit_mat: int = None
    lib_sit_mat: str = ""

    def to_dict(self):
        """Retourne un dictionnaire sans les clés nulles"""
        return {k: v for k, v in asdict(self).items() if v is not None}

@dataclass
class Unite:
    """Classe représentant un enregistrement de la table Unite"""
    id_unite: int = None
    lib_unite: str = ""

    def to_dict(self):
        """Retourne un dictionnaire sans les clés nulles"""
        return {k: v for k, v in asdict(self).items() if v is not None}

@dataclass
class Legion:
    """Classe représentant un enregistrement de la table Legion"""
    id_legion: int = None
    lib_legion: str = ""

    def to_dict(self):
        """Retourne un dictionnaire sans les clés nulles"""
        return {k: v for k, v in asdict(self).items() if v is not None}

@dataclass
class Subdiv:
    """Classe représentant un enregistrement de la table Subdiv"""
    id_subdiv: int = None
    lib_subdiv: str = ""

    def to_dict(self):
        """Retourne un dictionnaire sans les clés nulles"""
        return {k: v for k, v in asdict(self).items() if v is not None}

@dataclass
class Region:
    """Classe représentant un enregistrement de la table Region"""
    id_rg: int = None
    lib_rg: str = ""

    def to_dict(self):
        """Retourne un dictionnaire sans les clés nulles"""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class StatisticsData:
    """Classe pour stocker les données statistiques"""
    title: str
    data: Dict[str, Any]
    type: str = "count"  # count, percentage, etc.


class StatisticsRepository:
    """Classe pour gérer les opérations statistiques dans la base de données"""

    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_sanctions_by_period(self, year: int = None) -> StatisticsData:
        """Récupère les statistiques des sanctions par période"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT strftime('%m', date_faits) as mois, COUNT(*) as nombre
                FROM main_tab 
                WHERE annee_faits = ?
                GROUP BY mois
                ORDER BY mois
            """
            cursor.execute(query, (year,))
            results = dict(cursor.fetchall())
            return StatisticsData(
                title=f"Sanctions par mois en {year}",
                data=results
            )

    def get_sanctions_by_grade(self) -> StatisticsData:
        """Récupère les statistiques des sanctions par grade"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT grade, COUNT(*) as count
                FROM main_tab
                GROUP BY grade
                ORDER BY count DESC
            """)
            results = dict(cursor.fetchall())
            return StatisticsData(
                title="Répartition des sanctions par grade",
                data=results
            )

    def get_sanctions_by_region(self) -> StatisticsData:
        """Récupère les statistiques des sanctions par région"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT regions, COUNT(*) as count
                FROM main_tab
                GROUP BY regions
                ORDER BY count DESC
            """)
            results = dict(cursor.fetchall())
            return StatisticsData(
                title="Répartition des sanctions par région",
                data=results
            )

    def get_sanctions_full_list(self, filters: Dict[str, Any] = None) -> List[tuple]:
        """Récupère la liste complète des sanctions avec filtres optionnels"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT 
                    matricule,
                    nom_prenoms,
                    grade,
                    regions,
                    date_faits,
                    faute_commise,
                    categorie,
                    statut
                FROM main_tab
                WHERE 1=1
            """
            params = []

            if filters:
                if filters.get('grade'):
                    query += " AND grade = ?"
                    params.append(filters['grade'])
                if filters.get('region'):
                    query += " AND regions = ?"
                    params.append(filters['region'])
                if filters.get('year'):
                    query += " AND annee_punition = ?"
                    params.append(filters['year'])
                if filters.get('matricule'):
                    query += " AND matricule LIKE ?"
                    params.append(f"%{filters['matricule']}%")
                if filters.get('categorie'):
                    query += " AND categorie = ?"
                    params.append(filters['categorie'])

            query += " ORDER BY date_faits DESC"
            cursor.execute(query, params)
            return cursor.fetchall()

    def get_available_filters(self) -> Dict[str, List[str]]:
        """Récupère les valeurs disponibles pour les filtres"""
        filters = {}
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()

            # Grades
            cursor.execute("SELECT DISTINCT grade FROM main_tab ORDER BY grade")
            filters['grades'] = [row[0] for row in cursor.fetchall() if row[0]]

            # Régions
            cursor.execute("SELECT DISTINCT regions FROM main_tab ORDER BY regions")
            filters['regions'] = [row[0] for row in cursor.fetchall() if row[0]]

            # Années
            cursor.execute("SELECT DISTINCT annee_punition FROM main_tab ORDER BY annee_punition DESC")
            filters['years'] = [row[0] for row in cursor.fetchall() if row[0]]

            # Catégories de sanctions
            cursor.execute("SELECT DISTINCT categorie FROM main_tab ORDER BY categorie")
            filters['categories'] = [row[0] for row in cursor.fetchall() if row[0]]

            return filters
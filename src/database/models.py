from dataclasses import dataclass, asdict
from datetime import datetime, date
from typing import Optional, List, Dict, Any

#TODO : AJOUTER LES AUTRES CLASSES ET LES METHODES

@dataclass
class Gendarmes:
    """Classe représentant un enregistrement de la table Gendarmes"""
    id_gendarme : Optional[int] = None
    matricule : str = ""
    nom_prenoms : str = ""
    sexe : str = ""
    date_entree_gie : date = None
    nb_enfants : Optional[int] = None

    def to_dict(self):
        """Retourne un dictionnaire sans les clés nulles"""
        return {k: v for k, v in asdict(self).items() if v is not None}

@dataclass
class Statut:
    """Classe représentant un enregistrement de la table Statut"""
    id_statut : Optional[int] = None
    lib_statut : str = ""

@dataclass
class Type_sanctions:
    """Classe représentant un enregistrement de la table Type_sanctions"""
    id_type_sanction : Optional[int] = None
    lib_type_sanction : str = ""

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
    libelle : int = None
    statut_id : int = None

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

@dataclass
class Fautes:
    """Classe représentant un enregistrement de la table Fautes"""

@dataclass
class Categories:
    """Classe représentant un enregistrement de la table Categories"""

@dataclass
class Grades:
    """Classe représentant un enregistrement de la table Grades"""

@dataclass
class Sit_mat:
    """Classe représentant un enregistrement de la table Sit_mat"""

@dataclass
class Unite:
    """Classe représentant un enregistrement de la table Unite"""

@dataclass
class Legion:
    """Classe représentant un enregistrement de la table Legion"""

@dataclass
class Subdiv:
    """Classe représentant un enregistrement de la table Subdiv"""

@dataclass
class Region:
    """Classe représentant un enregistrement de la table Region"""



class MainTabRepository:
    """Classe pour gérer les opérations sur la table main_tab"""

    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_all(self) -> List[MainTab]:
        """Récupère tous les enregistrements de la table main_tab"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM main_tab ORDER BY nom_prenoms")
            columns = [description[0] for description in cursor.description]
            return [MainTab.from_db_row(row, columns) for row in cursor.fetchall()]

    def get_by_numero_dossier(self, numero_dossier: str) -> Optional[MainTab]:
        """Récupère un enregistrement par son numéro de dossier"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM main_tab WHERE numero_dossier = ?", (numero_dossier,))
            row = cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                return MainTab.from_db_row(row, columns)
        return None

    def get_by_matricule(self, matricule: int) -> List[MainTab]:
        """Récupère les enregistrements par matricule"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM main_tab WHERE matricule = ?", (matricule,))
            columns = [description[0] for description in cursor.description]
            return [MainTab.from_db_row(row, columns) for row in cursor.fetchall()]

    def get_by_name(self, name: str) -> List[MainTab]:
        """Récupère les enregistrements par nom et prénoms"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM main_tab WHERE nom_prenoms LIKE ?", (f"%{name}%",))
            columns = [description[0] for description in cursor.description]
            return [MainTab.from_db_row(row, columns) for row in cursor.fetchall()]

    def get_statistics(self) -> dict:
        """Récupère des statistiques générales"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            stats = {}

            # Nombre total de gendarmes (distincts par matricule)
            cursor.execute("SELECT COUNT(DISTINCT matricule) FROM main_tab")
            stats['total_gendarmes'] = cursor.fetchone()[0]

            # Nombre total de sanctions
            cursor.execute("SELECT COUNT(*) FROM main_tab")
            stats['total_sanctions'] = cursor.fetchone()[0]

            # Moyenne des sanctions par gendarme
            if stats['total_gendarmes'] > 0:
                stats['moyenne_sanctions'] = stats['total_sanctions'] / stats['total_gendarmes']
            else:
                stats['moyenne_sanctions'] = 0

            return stats


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
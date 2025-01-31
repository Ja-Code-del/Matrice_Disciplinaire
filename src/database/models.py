from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any


@dataclass
class MainTab:
    """Classe représentant un enregistrement de la table main_tab"""
    id: Optional[int] = None
    numero_dossier: str = ""
    annee_punition: Optional[int] = None
    numero_ordre: Optional[int] = None
    date_enr: str = ""
    matricule: Optional[int] = None
    nom_prenoms: str = ""
    grade: str = ""
    sexe: str = ""
    date_naissance: str = ""
    age: Optional[int] = None
    unite: str = ""
    legions: str = ""
    subdiv: str = ""
    regions: str = ""
    date_entree_gie: str = ""
    annee_service: Optional[int] = None
    situation_matrimoniale: str = ""
    nb_enfants: Optional[int] = None
    faute_commise: str = ""
    date_faits: str = ""
    categorie: Optional[int] = None
    statut: str = ""
    reference_statut: str = ""
    taux_jar: str = ""
    comite: Optional[int] = None
    annee_faits: Optional[int] = None
    numero_arrete: str = ""
    numero_decision: str = ""

    @classmethod
    def from_db_row(cls, row: tuple, column_names: list):
        """Crée une instance de MainTab à partir d'une ligne de la base de données"""
        data = dict(zip(column_names, row))
        return cls(**data)

    def to_dict(self):
        """Convertit l'instance en dictionnaire"""
        return {
            'id': self.id,
            'numero_dossier': self.numero_dossier,
            'annee_punition': self.annee_punition,
            'numero_ordre': self.numero_ordre,
            'date_enr': self.date_enr,
            'matricule': self.matricule,
            'nom_prenoms': self.nom_prenoms,
            'grade': self.grade,
            'sexe': self.sexe,
            'date_naissance': self.date_naissance,
            'age': self.age,
            'unite': self.unite,
            'legions': self.legions,
            'subdiv': self.subdiv,
            'regions': self.regions,
            'date_entree_gie': self.date_entree_gie,
            'annee_service': self.annee_service,
            'situation_matrimoniale': self.situation_matrimoniale,
            'nb_enfants': self.nb_enfants,
            'faute_commise': self.faute_commise,
            'date_faits': self.date_faits,
            'categorie': self.categorie,
            'statut': self.statut,
            'reference_statut': self.reference_statut,
            'taux_jar': self.taux_jar,
            'comite': self.comite,
            'annee_faits': self.annee_faits,
            'numero_arrete': self.numero_arrete,
            'numero_decision': self.numero_decision
        }


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
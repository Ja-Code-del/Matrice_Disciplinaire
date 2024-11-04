from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class Gendarme:
    """Classe représentant un gendarme"""
    id: Optional[int] = None
    mle: str = ""
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
    sanctions: List['Sanction'] = None

    def __post_init__(self):
        if self.sanctions is None:
            self.sanctions = []

    @classmethod
    def from_db_row(cls, row: tuple, column_names: list):
        """Crée une instance de Gendarme à partir d'une ligne de la base de données"""
        data = dict(zip(column_names, row))
        return cls(**data)

    def to_dict(self):
        """Convertit l'instance en dictionnaire"""
        return {
            'id': self.id,
            'mle': self.mle,
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
            'nb_enfants': self.nb_enfants
        }


@dataclass
class Sanction:
    """Classe représentant une sanction"""
    id: Optional[int] = None
    numero_dossier: str = ""
    annee_punition: Optional[int] = None
    numero_ordre: int = ""
    date_enr: str = ""
    matricule: int = ""
    faute_commise: str = ""
    date_faits: str = ""
    numero_cat: str = ""
    statut: str = ""
    reference_statut: str = ""
    taux_jar: Optional[int] = None
    comite: str = ""
    annee_faits: Optional[int] = None

    @classmethod
    def from_db_row(cls, row: tuple, column_names: list):
        """Crée une instance de Sanction à partir d'une ligne de la base de données"""
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
            'faute_commise': self.faute_commise,
            'date_faits': self.date_faits,
            'numero_cat': self.numero_cat,
            'statut': self.statut,
            'reference_statut': self.reference_statut,
            'taux_jar': self.taux_jar,
            'comite': self.comite,
            'annee_faits': self.annee_faits
        }


class GendarmeRepository:
    """Classe pour gérer les opérations sur les gendarmes dans la base de données"""

    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_all(self) -> List[Gendarme]:
        """Récupère tous les gendarmes"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM gendarmes ORDER BY nom_prenoms")
            columns = [description[0] for description in cursor.description]
            return [Gendarme.from_db_row(row, columns) for row in cursor.fetchall()]

    def get_by_mle(self, mle: str) -> Optional[Gendarme]:
        """Récupère un gendarme par son matricule"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM gendarmes WHERE mle = ?", (mle,))
            row = cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                return Gendarme.from_db_row(row, columns)
        return None

    def get_by_name(self, name: str) -> List[Gendarme]:
        """Récupère les gendarmes par leur nom"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM gendarmes WHERE nom_prenoms LIKE ?", (f"%{name}%",))
            columns = [description[0] for description in cursor.description]
            return [Gendarme.from_db_row(row, columns) for row in cursor.fetchall()]


class SanctionRepository:
    """Classe pour gérer les opérations sur les sanctions dans la base de données"""

    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_by_gendarme(self, gendarme_id: int) -> List[Sanction]:
        """Récupère toutes les sanctions d'un gendarme"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM sanctions 
                WHERE matricule = ? 
                ORDER BY date_faits DESC
            """, (gendarme_id,))
            columns = [description[0] for description in cursor.description]
            return [Sanction.from_db_row(row, columns) for row in cursor.fetchall()]

    def get_statistics(self) -> dict:
        """Récupère des statistiques sur les sanctions"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            stats = {}

            # Nombre total de sanctions
            cursor.execute("SELECT COUNT(*) FROM sanctions")
            stats['total_sanctions'] = cursor.fetchone()[0]

            # Répartition par type
            cursor.execute("""
                SELECT statut, COUNT(*) as count 
                FROM sanctions 
                GROUP BY statut
                ORDER BY count DESC
            """)
            stats['repartition_par_type'] = dict(cursor.fetchall())

            return stats
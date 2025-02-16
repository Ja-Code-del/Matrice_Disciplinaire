from dataclasses import dataclass, asdict
from datetime import datetime, date
from typing import Optional, List, Dict, Any

from src.database.db_manager import logger


@dataclass
class Gendarmes:
    """Classe représentant un enregistrement de la table Gendarmes"""
    id_gendarme : int = None
    matricule : str = ""
    nom_prenoms : str = ""
    age : int = None
    sexe : str = ""
    date_entree_gie : date = None
    nb_enfants: Optional[int] = None
    # Champs additionnels pour l'affichage
    reference: str = ""
    date_naissance: date = None
    lieu_naissance : str = ""
    lib_unite: str = ""
    lib_legion: str = ""
    lib_subdiv: str = ""
    lib_rg: str = ""
    lib_grade: str = ""
    situation_matrimoniale: str = ""

    def to_dict(self):
        """Retourne un dictionnaire sans les clés nulles"""
        return {k: v for k, v in asdict(self).items() if v is not None}

    def format_date(self, date_value):
        """Formate une date en format français"""
        if isinstance(date_value, date):
            return date_value.strftime('%d/%m/%Y')
        return date_value if date_value else ""

    def get_formatted_date_naissance(self):
        """Retourne la date de naissance formatée"""
        return self.format_date(self.date_naissance)

    def get_formatted_date_entree(self):
        """Retourne la date d'entrée formatée"""
        return self.format_date(self.date_entree_gie)

@dataclass
class GendarmeSearchResult:
    """Classe pour stocker les résultats de recherche d'un gendarme"""
    matricule: str
    nom: str
    prenoms: str
    date_naissance: Optional[date]
    date_entree_service: Optional[date]
    sexe: str
    lieu_naissance: str
    nb_enfants: Optional[int]
    annee_service: Optional[int]

class GendarmesRepository:
    """Classe pour gerer les opérations dans la table gendarme"""
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_by_matricule(self, matricule: str) -> Optional[Gendarmes]:
        """
        Récupère les informations d'un gendarme par son matricule
        Args:
            matricule: Le matricule du gendarme
        Returns:
            Instance de Gendarmes ou None si non trouvé
        """
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    g.id_gendarme,
                    g.matricule,
                    g.nom_prenoms,
                    g.sexe,
                    g.date_entree_gie,
                    ge.date_naissance,
                    ge.lieu_naissance
                FROM Gendarmes g
                LEFT JOIN gendarmes_etat ge ON g.matricule = ge.matricule
                WHERE g.matricule = ?
                LIMIT 1
            """, (matricule,))

            row = cursor.fetchone()
            if row:
                # Création d'un dictionnaire avec les noms de colonnes
                column_names = [description[0] for description in cursor.description]
                gendarme_dict = dict(zip(column_names, row))

                # Conversion des dates si nécessaire
                for date_field in ['date_entree_gie', 'date_naissance']:
                    if gendarme_dict.get(date_field):
                        try:
                            gendarme_dict[date_field] = datetime.strptime(
                                gendarme_dict[date_field], '%Y-%m-%d'
                            ).date()
                        except:
                            gendarme_dict[date_field] = None

                return Gendarmes(**gendarme_dict)
            return None

    def search_by_matricule(self, matricule: str) -> Optional[GendarmeSearchResult]:
        """
        Recherche un gendarme par son matricule dans les tables gendarmes_etat et Gendarmes
        Args:
            matricule: Matricule du gendarme
        Returns:
            GendarmeSearchResult ou None si non trouvé
        """
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        ge.matricule,
                        ge.nom,
                        ge.prenoms,
                        ge.date_naissance,
                        ge.date_entree_service,
                        ge.sexe,
                        ge.lieu_naissance,
                        g.nb_enfants,
                        g.annee_service
                    FROM gendarmes_etat ge
                    LEFT JOIN Gendarmes g ON ge.matricule = g.matricule
                    WHERE ge.matricule = ?
                """, (matricule,))

                result = cursor.fetchone()
                if not result:
                    return None

                # Conversion des dates
                date_naissance = None
                date_entree = None

                if result[3]:  # date_naissance
                    try:
                        date_naissance = datetime.strptime(result[3], '%Y-%m-%d').date()
                    except:
                        pass

                if result[4]:  # date_entree_service
                    try:
                        date_entree = datetime.strptime(result[4], '%Y-%m-%d').date()
                    except:
                        pass

                return GendarmeSearchResult(
                    matricule=result[0],
                    nom=result[1] or "",
                    prenoms=result[2] or "",
                    date_naissance=date_naissance,
                    date_entree_service=date_entree,
                    sexe=result[5] or "",
                    lieu_naissance=result[6] or "",
                    nb_enfants=result[7],
                    annee_service=result[8]
                )

        except Exception as e:
            logger.error(f"Erreur lors de la recherche du gendarme : {str(e)}")
            raise



@dataclass
class Statut:
    """Classe représentant un enregistrement de la table Statut"""

    id_statut: int = None
    lib_statut: str = ""

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

    def get_dossiers_with_details(self, matricule=None, nom_prenoms=None):
        """
        Récupère les dossiers avec leurs détails associés
        Args:
            matricule: Matricule du gendarme (optionnel)
            nom_prenoms: Nom et prénoms du gendarme (optionnel)
        Returns:
            Liste de dictionnaires contenant les détails des dossiers
        """
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()

            query = """
                SELECT 
                    d.reference,
                    g.nom_prenoms,
                    d.date_faits,
                    f.lib_faute as faute_commise,
                    s.lib_statut as statut,
                    ts.lib_type_sanction as type_sanction
                FROM Dossiers d
                JOIN Gendarmes g ON d.matricule_dossier = g.matricule
                JOIN Fautes f ON d.faute_id = f.id_faute
                JOIN Statut s ON d.statut_id = s.id_statut
                JOIN Sanctions sa ON d.numero_inc = sa.num_inc
                JOIN Type_sanctions ts ON sa.type_sanction_id = ts.id_type_sanction
                WHERE 1=1
            """

            params = []
            if matricule:
                query += " AND d.matricule_dossier = ?"
                params.append(matricule)
            if nom_prenoms:
                query += " AND g.nom_prenoms LIKE ?"
                params.append(nom_prenoms)

            query += " ORDER BY d.numero_inc DESC"

            cursor.execute(query, params)

            columns = [desc[0] for desc in cursor.description]
            results = []

            for row in cursor.fetchall():
                result_dict = dict(zip(columns, row))
                results.append(result_dict)

            return results

    def get_dossiers_by_matricule(self, matricule: str) -> List[Dict]:
        """Récupère tous les dossiers d'un gendarme par matricule avec toutes les informations associées"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                        SELECT DISTINCT
                            d.numero_inc,
                            d.id_dossier,
                            d.reference,
                            d.date_faits,
                            gr.lib_grade,
                            u.lib_unite,
                            l.lib_legion,
                            s.lib_subdiv,
                            r.lib_rg,
                            sm.lib_sit_mat,
                            f.lib_faute,
                            c.id_categorie,
                            ts.lib_type_sanction,
                            sa.taux,
                            sa.comite
                        FROM Dossiers d
                        LEFT JOIN Grade gr ON d.grade_id = gr.id_grade
                        LEFT JOIN Unite u ON d.unite_id = u.id_unite
                        LEFT JOIN Legion l ON d.legion_id = l.id_legion
                        LEFT JOIN Subdiv s ON d.subdiv_id = s.id_subdiv
                        LEFT JOIN Region r ON d.rg_id = r.id_rg
                        LEFT JOIN Sit_mat sm ON d.situation_mat_id = sm.id_sit_mat
                        LEFT JOIN Fautes f ON d.faute_id = f.id_faute
                        LEFT JOIN Categories c ON f.cat_id = c.id_categorie
                        LEFT JOIN Sanctions sa ON d.numero_inc = sa.num_inc
                        LEFT JOIN Type_sanctions ts ON sa.type_sanction_id = ts.id_type_sanction
                        WHERE d.matricule_dossier = ?
                        GROUP BY d.numero_inc  -- Groupe par le numéro d'incrémentation unique
                        ORDER BY d.numero_inc DESC
                    """, (matricule,))

            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_dossiers_by_name(self, nom: str) -> List[Dict]:
        """Récupère tous les dossiers d'un gendarme par nom"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT
                    d.numero_inc,
                    d.id_dossier,
                    d.reference,
                    d.date_faits,
                    gr.lib_grade,
                    u.lib_unite,
                    l.lib_legion,
                    s.lib_subdiv,
                    r.lib_rg,
                    sm.lib_sit_mat,
                    f.lib_faute,
                    c.id_categorie,
                    ts.lib_type_sanction,
                    sa.taux,
                    sa.comite
                FROM Dossiers d
                JOIN Gendarmes g ON d.matricule_dossier = g.matricule
                LEFT JOIN Grade gr ON d.grade_id = gr.id_grade
                LEFT JOIN Unite u ON d.unite_id = u.id_unite
                LEFT JOIN Legion l ON d.legion_id = l.id_legion
                LEFT JOIN Subdiv s ON d.subdiv_id = s.id_subdiv
                LEFT JOIN Region r ON d.rg_id = r.id_rg
                LEFT JOIN Sit_mat sm ON d.situation_mat_id = sm.id_sit_mat
                LEFT JOIN Fautes f ON d.faute_id = f.id_faute
                LEFT JOIN Categories c ON f.cat_id = c.id_categorie
                LEFT JOIN Sanctions sa ON d.numero_inc = sa.num_inc
                LEFT JOIN Type_sanctions ts ON sa.type_sanction_id = ts.id_type_sanction
                WHERE g.nom_prenoms LIKE ?
                GROUP BY d.numero_inc
                ORDER BY d.numero_inc DESC
            """, (f"%{nom}%",))

            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_faute_info(self, faute_id: int) -> Optional[Fautes]:
        """
        Récupère les informations d'une faute et sa catégorie
        Args:
            faute_id: ID de la faute
        Returns:
            Instance de Fautes ou None si non trouvé
        """
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT f.*, c.lib_categorie 
                FROM Fautes f
                LEFT JOIN Categories c ON f.cat_id = c.id_categorie
                WHERE f.id_faute = ?
            """, (faute_id,))
            row = cursor.fetchone()

            if row:
                column_names = [description[0] for description in cursor.description]
                faute_dict = dict(zip(column_names, row))
                return Fautes(**faute_dict)
            return None

    def get_statut_info(self, statut_id: int) -> Optional[Statut]:
        """
        Récupère les informations d'un statut
        Args:
            statut_id: ID du statut
        Returns:
            Instance de Statut ou None si non trouvé
        """
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM Statut 
                WHERE id_statut = ?
            """, (statut_id,))
            row = cursor.fetchone()

            if row:
                column_names = [description[0] for description in cursor.description]
                statut_dict = dict(zip(column_names, row))
                return Statut(**statut_dict)
            return None

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

    def get_by_dossier(self, numero_inc: int) -> Optional[Sanctions]:
        """
        Récupère une sanction associée à un dossier
        Args:
            numero_inc: Numéro d'incrémentation du dossier
        Returns:
            Instance de Sanctions ou None si non trouvé
        """
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM Sanctions 
                WHERE num_inc = ?
            """, (numero_inc,))
            row = cursor.fetchone()

            if row:
                column_names = [description[0] for description in cursor.description]
                sanction_dict = dict(zip(column_names, row))
                return Sanctions(**sanction_dict)
            return None



@dataclass
class Type_sanctions:
    """Classe représentant un enregistrement de la table Type_sanctions"""
    id_type_sanction : int = None
    lib_type_sanction : str = ""

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
import pandas as pd
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from src.utils.date_utils import compute_values, adapt_date

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ImportResult:
    success: bool
    message: str
    details: Dict[str, Any] = None
    error: Exception = None


class DataValidator:
    """Classe responsable de la validation des données"""

    @staticmethod
    def validate_required_columns(df: pd.DataFrame) -> ImportResult:
        required_columns = {
            'REFERENCE', 'ANNEE DE PUNITION', 'N° ORDRE', 'N° ANNEE', 'ID DOSSIER',
            'DATE ENR', 'MLE', 'NOM ET PRENOMS', 'GRADE', 'SEXE', 'DATE DE NAISSANCE',
            'AGE', 'UNITE', 'LEGIONS', 'SUBDIV', 'REGIONS', 'DATE D\'ENTREE GIE',
            'ANNEE DE SERVICE', 'SITUATION MATRIMONIALE', 'NB ENF', 'FAUTE COMMISE',
            'DATE DES FAITS', 'LIBELLE', 'N° CAT', 'TYPE SANCTION', 'REFERENCE DU STATUT',
            'N° DECISION', 'N° ARRETE', 'TAUX (JAR)', 'ANNEE DES FAITS', 'ANNEE RADIATION',
            'COMITE', 'STATUT DOSSIER'
        }

        missing_columns = required_columns - set(df.columns)
        if missing_columns:
            return ImportResult(
                success=False,
                message=f"Colonnes manquantes: {', '.join(missing_columns)}"
            )
        return ImportResult(success=True, message="Validation des colonnes réussie")


class DataTransformer:
    """Classe responsable de la transformation des données"""
    # Convertir les colonnes de dates
    @staticmethod
    def transform_dates(df: pd.DataFrame) -> pd.DataFrame:
        date_columns = ['DATE ENR', 'DATE DE NAISSANCE', 'DATE D\'ENTREE GIE', 'DATE DES FAITS']

        for col in date_columns:
            df[col] = df[col].apply(adapt_date)

        # for col in date_columns:
        #     df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%Y-%m-%d')
        return df

    @staticmethod
    def transform_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
        numeric_columns = {
            'ANNEE DE PUNITION': 0, 'N° ORDRE': 0, 'MLE': 0, 'AGE': 0,
            'ANNEE DE SERVICE': 0, 'NB ENF': 0, 'N° CAT': 0,
            'ANNEE DES FAITS': 0, 'ANNEE RADIATION': 0
        }

        # Extraire l'année pour les colonnes qui doivent être des années
        df['ANNEE DES FAITS'] = df['ANNEE DES FAITS'].fillna(0).astype(int)  # Corrige float64 en int64

        for col, default in numeric_columns.items():
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(default).astype(int)
            # Vérifier si certaines colonnes censées être numériques contiennent des valeurs erronées
            cols_to_int = ['ANNEE DE PUNITION', 'N° ORDRE', 'MLE', 'AGE', 'ANNEE DE SERVICE', 'NB ENF', 'N° CAT']
            for col in cols_to_int:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

        return df

    @staticmethod
    def clean_text_columns(df: pd.DataFrame) -> pd.DataFrame:
        text_columns = df.select_dtypes(include=['object']).columns
        for col in text_columns:
            df[col] = df[col].astype(str).str.strip()
        return df


class DataImporter:
    """Classe principale pour gérer l'import des données"""

    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.validator = DataValidator()
        self.transformer = DataTransformer()



    def prepare_foreign_keys(self, row: pd.Series) -> Dict[str, int]:
        """Prépare les clés étrangères pour une ligne"""
        try:
            return {
                'statut_id': self.db_manager.get_foreign_key_id("Statut", "lib_statut", row['STATUT DOSSIER']),
                'type_sanction_id': self.db_manager.get_foreign_key_id("Type_sanctions", "lib_type_sanction",
                                                                       row['TYPE SANCTION']),
                'grade_id': self.db_manager.get_foreign_key_id("Grade", "lib_grade", row['GRADE']),
                'faute_id': self.db_manager.get_foreign_key_id("Fautes", "lib_faute", row['FAUTE COMMISE']),
                'sit_mat_id': self.db_manager.get_foreign_key_id("Sit_mat", "lib_sit_mat",
                                                                 row['SITUATION MATRIMONIALE']),
                'unite_id': self.db_manager.get_foreign_key_id("Unite", "lib_unite", row['UNITE']),
                'legion_id': self.db_manager.get_foreign_key_id("Legion", "lib_legion", row['LEGIONS']),
                'subdiv_id': self.db_manager.get_foreign_key_id("Subdiv", "lib_subdiv", row['SUBDIV']),
                'region_id': self.db_manager.get_foreign_key_id("Region", "lib_rg", row['REGIONS']),
                'categorie_id': self.db_manager.get_foreign_key_id("Categories", "lib_categorie", row['N° CAT'])
            }
        except Exception as e:
            logger.error(f"Erreur lors de la préparation des clés étrangères: {str(e)}")
            raise

    def prepare_gendarme_data(self, row: pd.Series) -> Dict[str, Any]:
        """Prépare les données pour la table Gendarmes"""
        # Calculer l'âge et la durée de service
        age, annee_service = compute_values(row)

        return {
            'matricule': str(row['MLE']).strip() if pd.notna(row['MLE']) else None,
            'nom_prenoms': str(row['NOM ET PRENOMS']).strip() if pd.notna(row['NOM ET PRENOMS']) else None,
            'age': int(row['AGE']) if pd.notna(row['AGE']) and str(
                row['AGE']).isdigit() else None,
            'sexe': str(row['SEXE']).strip() if pd.notna(row['SEXE']) else None,
            'date_entree_gie': str(row['DATE D\'ENTREE GIE']).strip() if pd.notna(row['DATE D\'ENTREE GIE']) else None,
            'annee_service': int(row['ANNEE DE SERVICE']) if pd.notna(row['ANNEE DE SERVICE']) and str(
                row['ANNEE DE SERVICE']).isdigit() else None,
            'nb_enfants': str(row['NB ENF']).strip() if pd.notna(row['NB ENF']) else None
        }

    def prepare_dossier_data(self, row: pd.Series, foreign_keys: Dict[str, int]) -> Dict[str, Any]:
        """Prépare les données pour la table Dossiers"""
        return {
            'matricule_dossier': str(row['MLE']).strip() if pd.notna(row['MLE']) else None,
            'reference': str(row['REFERENCE']).strip() if pd.notna(row['REFERENCE']) else None,
            'date_enr': str(row['DATE ENR']).strip() if pd.notna(row['DATE ENR']) else None,
            'date_faits': str(row['DATE DES FAITS']).strip() if pd.notna(row['DATE DES FAITS']) else None,
            'numero_inc': int(row['N° ORDRE']) if pd.notna(row['N° ORDRE']) and str(
                row['N° ORDRE']).isdigit() else None,
            'numero_annee': int(row['N° ANNEE']) if pd.notna(row['N° ANNEE']) and str(
                row['N° ANNEE']).isdigit() else None,
            'annee_enr': int(row['ANNEE DE PUNITION']) if pd.notna(row['ANNEE DE PUNITION']) and str(
                row['ANNEE DE PUNITION']).isdigit() else None,
            'libelle': str(row['LIBELLE']).strip() if pd.notna(row['LIBELLE']) else None,

            'grade_id': foreign_keys['grade_id'],
            'situation_mat_id': foreign_keys['sit_mat_id'],
            'unite_id': foreign_keys['unite_id'],
            'legion_id': foreign_keys['legion_id'],
            'subdiv_id': foreign_keys['subdiv_id'],
            'rg_id': foreign_keys['region_id'],
            'faute_id': foreign_keys['faute_id'],
            'sanction_id': foreign_keys['type_sanction_id'],
            'statut_id': foreign_keys['statut_id']
        }

    def prepare_sanction_data(self, row: pd.Series, foreign_keys: Dict[str, int]) -> Dict[str, Any]:
        """Prépare les données pour la table Sanctions"""
        return {
            'num_inc': str(row['N° ORDRE']).strip() if pd.notna(row['N° ORDRE']) else None,
            # ✅ Clé étrangère vers Dossiers
            'taux': str(row['TAUX (JAR)']).strip() if pd.notna(row['TAUX (JAR)']) else None,
            'numero_decision': str(row['N° DECISION']).strip() if pd.notna(row['N° DECISION']) else None,
            'numero_arrete': str(row['N° ARRETE']).strip() if pd.notna(row['N° ARRETE']) else None,
            'annee_radiation': str(row['ANNEE RADIATION']).strip() if pd.notna(row['ANNEE RADIATION']) else None,
            'ref_statut': str(row['REFERENCE DU STATUT']).strip() if pd.notna(row['REFERENCE DU STATUT']) else None,
            'comite': str(row['COMITE']).strip() if pd.notna(row['COMITE']) else None,

            'type_sanction_id': foreign_keys['type_sanction_id']
        }

    def import_excel_file(self, file_path: str, progress_callback=None) -> ImportResult:
        """Importe les données depuis un fichier Excel"""
        try:
            # Lecture du fichier Excel
            df = pd.read_excel(file_path)
            df = df.drop_duplicates()

            # Validation des colonnes
            validation_result = self.validator.validate_required_columns(df)
            if not validation_result.success:
                return validation_result

            # Transformation des données
            df = self.transformer.transform_dates(df)
            df = self.transformer.transform_numeric_columns(df)
            df = self.transformer.clean_text_columns(df)

            total_rows = len(df)
            success_count = 0
            error_count = 0

            for index, row in df.iterrows():
                try:
                    # Préparation des clés étrangères
                    foreign_keys = self.prepare_foreign_keys(row)

                    # Insertion des données dans les différentes tables
                    gendarme_data = self.prepare_gendarme_data(row)
                    dossier_data = self.prepare_dossier_data(row, foreign_keys)
                    sanction_data = self.prepare_sanction_data(row, foreign_keys)

                    self.db_manager.add_data("Gendarmes", gendarme_data)
                    self.db_manager.add_data("Dossiers", dossier_data)
                    self.db_manager.add_data("Sanctions", sanction_data)

                    success_count += 1

                except Exception as e:
                    error_count += 1
                    logger.error(f"Erreur à la ligne {index + 2}: {str(e)}")

                if progress_callback:
                    progress_callback(total_rows, success_count, error_count)

            return ImportResult(
                success=True,
                message="Import terminé",
                details={
                    'total_rows': total_rows,
                    'success_count': success_count,
                    'error_count': error_count
                }
            )

        except Exception as e:
            logger.error(f"Erreur lors de l'import: {str(e)}")
            return ImportResult(
                success=False,
                message=f"Erreur lors de l'import: {str(e)}",
                error=e
            )


# class DataImporter:
#     """Classe principale pour gérer l'import des données"""
#
#     def __init__(self, db_manager):
#         self.db_manager = db_manager
#         self.validator = DataValidator()
#         self.transformer = DataTransformer()
#
#     def prepare_foreign_keys(self, row: pd.Series) -> Dict[str, int]:
#         """Prépare les clés étrangères pour une ligne"""
#         try:
#             return {
#                 'statut_id': self.db_manager.get_foreign_key_id("Statut", "lib_statut", row['STATUT DOSSIER']),
#                 'type_sanction_id': self.db_manager.get_foreign_key_id("Type_sanctions", "lib_type_sanction",
#                                                                        row['TYPE SANCTION']),
#                 'grade_id': self.db_manager.get_foreign_key_id("Grade", "lib_grade", row['GRADE']),
#                 'faute_id': self.db_manager.get_foreign_key_id("Fautes", "lib_faute", row['FAUTE COMMISE']),
#                 'sit_mat_id': self.db_manager.get_foreign_key_id("Sit_mat", "lib_sit_mat",
#                                                                  row['SITUATION MATRIMONIALE']),
#                 'unite_id': self.db_manager.get_foreign_key_id("Unite", "lib_unite", row['UNITE']),
#                 'legion_id': self.db_manager.get_foreign_key_id("Legion", "lib_legion", row['LEGIONS']),
#                 'subdiv_id': self.db_manager.get_foreign_key_id("Subdiv", "lib_subdiv", row['SUBDIV']),
#                 'region_id': self.db_manager.get_foreign_key_id("Region", "lib_rg", row['REGIONS']),
#                 'categorie_id': self.db_manager.get_foreign_key_id("Categories", "lib_categorie", row['N° CAT'])
#             }
#         except Exception as e:
#             logger.error(f"Erreur lors de la préparation des clés étrangères: {str(e)}")
#             raise
#
#     def prepare_gendarme_data(self, row: pd.Series) -> Dict[str, Any]:
#         """Prépare les données pour la table Gendarmes"""
#         return {
#             'matricule': str(row['MLE']),
#             'nom_prenoms': str(row['NOM ET PRENOMS']),
#             'age': int(row['AGE']),
#             'sexe': str(row['SEXE']),
#             'date_entree_gie': str(row['DATE D\'ENTREE GIE']),
#             'annee_service': int(row['ANNEE DE SERVICE']),
#             'nb_enfants': int(row['NB ENF'])
#         }
#
#     def prepare_dossier_data(self, row: pd.Series, foreign_keys: Dict[str, int]) -> Dict[str, Any]:
#         """Prépare les données pour la table Dossiers"""
#         return {
#             'matricule_dossier': str(row['MLE']),
#             'reference': str(row['REFERENCE']),
#             'date_enr': str(row['DATE ENR']),
#             'date_faits': str(row['DATE DES FAITS']),
#             'numero_inc': int(row['N° ORDRE']),
#             'numero_annee': int(row['N° ANNEE']),
#             'annee_enr': int(row['ANNEE DE PUNITION']),
#             'libelle': str(row['LIBELLE']),
#             **foreign_keys
#         }
#
#     def prepare_sanction_data(self, row: pd.Series, foreign_keys: Dict[str, int]) -> Dict[str, Any]:
#         """Prépare les données pour la table Sanctions"""
#         return {
#             'type_sanction_id': foreign_keys['type_sanction_id'],
#             'num_inc': str(row['N° ORDRE']),
#             'taux': str(row['TAUX (JAR)']),
#             'numero_decision': str(row['N° DECISION']),
#             'numero_arrete': str(row['N° ARRETE']),
#             'annee_radiation': str(row['ANNEE RADIATION']),
#             'ref_statut': str(row['REFERENCE DU STATUT']),
#             'comite': str(row['COMITE'])
#         }
#
#     async def import_excel_file(self, file_path: str, progress_callback=None) -> ImportResult:
#         """Importe les données depuis un fichier Excel"""
#         try:
#             # Lecture du fichier Excel
#             df = pd.read_excel(file_path)
#             df = df.drop_duplicates()
#
#             # Validation des colonnes
#             validation_result = self.validator.validate_required_columns(df)
#             if not validation_result.success:
#                 return validation_result
#
#             # Transformation des données
#             df = self.transformer.transform_dates(df)
#             df = self.transformer.transform_numeric_columns(df)
#             df = self.transformer.clean_text_columns(df)
#
#             total_rows = len(df)
#             success_count = 0
#             error_count = 0
#
#             for index, row in df.iterrows():
#                 try:
#                     # Préparation des clés étrangères
#                     foreign_keys = self.prepare_foreign_keys(row)
#
#                     # Insertion des données dans les différentes tables
#                     gendarme_data = self.prepare_gendarme_data(row)
#                     dossier_data = self.prepare_dossier_data(row, foreign_keys)
#                     sanction_data = self.prepare_sanction_data(row, foreign_keys)
#
#                     self.db_manager.add_data("Gendarmes", gendarme_data)
#                     self.db_manager.add_data("Dossiers", dossier_data)
#                     self.db_manager.add_data("Sanctions", sanction_data)
#
#                     success_count += 1
#
#                 except Exception as e:
#                     error_count += 1
#                     logger.error(f"Erreur à la ligne {index + 2}: {str(e)}")
#
#                 if progress_callback:
#                     progress_callback(total_rows, success_count, error_count)
#
#             return ImportResult(
#                 success=True,
#                 message="Import terminé",
#                 details={
#                     'total_rows': total_rows,
#                     'success_count': success_count,
#                     'error_count': error_count
#                 }
#             )
#
#         except Exception as e:
#             logger.error(f"Erreur lors de l'import: {str(e)}")
#             return ImportResult(
#                 success=False,
#                 message=f"Erreur lors de l'import: {str(e)}",
#                 error=e
#             )
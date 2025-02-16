from typing import Tuple, Optional

import pandas as pd
from datetime import datetime, date

from PyQt6.QtCore import QDate
from dateutil.relativedelta import relativedelta


class DateHandler:
    """Classe utilitaire pour la gestion des dates"""

    FR_DATE_FORMAT = "%d/%m/%Y"
    DB_DATE_FORMAT = "%Y-%m-%d"


def adapt_date(val):
    """Convertit différents types de dates en format texte pour SQLite"""
    if pd.isna(val):  # Gestion des NaN
        return None
    if isinstance(val, pd.Timestamp):  # Format pandas
        return val.strftime('%Y-%m-%d')
    if isinstance(val, datetime):  # Format Python
        return val.strftime('%Y-%m-%d')
    if isinstance(val, str):  # Chaîne de caractères
        try:
            # Convertit les formats courants en dates (format français prioritaire)
            date_obj = pd.to_datetime(val, format='%d/%m/%Y', dayfirst=True)
            return date_obj.strftime('%Y-%m-%d')
        except ValueError:  # Si le format ne correspond pas
            try:
                # Autres formats possibles (exemple : ISO 8601)
                date_obj = pd.to_datetime(val)
                return date_obj.strftime('%Y-%m-%d')
            except Exception as e:
                print(f"Impossible de convertir {val} en date : {e}")
                return None  # Retourne None si la conversion échoue
    return None  # Retourne None pour les types non gérés

def calculate_age(birth_date, date_faits=None):
    """
    Calcule l'âge à partir d'une date de naissance et d'une date de référence (date des faits).
    Args:
        birth_date: Date de naissance
        date_faits: Date des faits (si None, utilise la date actuelle)
    Returns:
        int: Âge calculé ou None si erreur
    """
    if not birth_date:
        return None
    try:
        # Traitement de la date de naissance
        if isinstance(birth_date, str):
            # Vérification du format de la date
            if '00/' in birth_date or '/00' in birth_date:
                print(f"Date de naissance invalide : {birth_date}")
                return None

            # Si format français (DD/MM/YYYY)
            if '/' in birth_date:
                day, month, year = birth_date.split('/')
                # Vérification des valeurs
                if not (1 <= int(day) <= 31 and 1 <= int(month) <= 12 and len(year) == 4):
                    print(f"Date de naissance invalide : {birth_date}")
                    return None
                born = pd.Timestamp(int(year), int(month), int(day))
            else:
                born = pd.to_datetime(birth_date)
        else:
            born = pd.to_datetime(birth_date)

        # Traitement de la date des faits
        if date_faits:
            if isinstance(date_faits, str):
                reference_date = pd.to_datetime(date_faits)
            else:
                reference_date = pd.to_datetime(date_faits)
        else:
            reference_date = pd.Timestamp.now()

        # Calcul de l'âge
        age = reference_date.year - born.year

        # Ajustement si l'anniversaire n'est pas encore passé dans l'année de référence
        if (reference_date.month, reference_date.day) < (born.month, born.day):
            age -= 1

        return age

    except Exception as e:
        print(f"Erreur lors du calcul de l'âge pour la date {birth_date}: {str(e)}")
        return None

def compute_values(row):
    """Calcule l'âge et la durée de service à partir des dates"""
    # Utilisation de date_faits au lieu de today
    if "date_faits" in row and pd.notna(row["date_faits"]):
        try:
            reference_date = pd.to_datetime(row["date_faits"]).date()
        except Exception as e:
            print(f"⚠ Erreur dans la lecture de date_faits : {e}")
            return None, None
    else:
        print("⚠ La colonne date_faits est manquante ou vide")
        return None, None

    # Calcul de l'âge (si la date de naissance est fournie)
    age = None
    if "date_naissance" in row and pd.notna(row["date_naissance"]):
        try:
            birth_date = pd.to_datetime(row["date_naissance"]).date()
            age = reference_date.year - birth_date.year - ((reference_date.month, reference_date.day) < (birth_date.month, birth_date.day))
        except Exception as e:
            print(f"⚠ Erreur dans le calcul de l'âge : {e}")

    # Calcul de la durée de service (si la date d'entrée est fournie)
    duree_service = None
    if "date_entree_service" in row and pd.notna(row["date_entree_service"]):
        try:
            entry_date = pd.to_datetime(row["date_entree_service"]).date()
            duree_service = reference_date.year - entry_date.year - ((reference_date.month, reference_date.day) < (entry_date.month, entry_date.day))
        except Exception as e:
            print(f"⚠ Erreur dans le calcul de la durée de service : {e}")

    return age, duree_service


def parse_annee_service(val):
    """
    Parse les années de service en gérant tous les cas spéciaux
    Args:
        val: La valeur à convertir (peut être '50+RAD', '30-50', '30', etc.)
    Returns:
        int: Le nombre d'années de service, ou None si invalide
    """
    if pd.isna(val):
        return None
    try:
        val_str = str(val).strip()

        # Cas "50+RAD"
        if '+' in val_str:
            val_str = val_str.split('+')[0].strip()

        # Cas "30-50"
        elif '-' in val_str:
            # Prend la plus grande valeur
            parts = [int(x.strip()) for x in val_str.split('-')]
            return max(parts)

        return int(val_str)
    except Exception as e:
        print(f"Erreur lors du parsing de l'année de service '{val}': {str(e)}")
        return None


def to_french_format(date_value) -> str:
    """Convertit une date en format français"""
    if pd.isna(date_value):
        return ""
    try:
        if isinstance(date_value, (datetime, pd.Timestamp)):
            return date_value.strftime('%d/%m/%Y')
        elif isinstance(date_value, str):
            date_obj = pd.to_datetime(date_value)
            return date_obj.strftime('%d/%m/%Y')
        return ""
    except Exception as e:
        print(f"Erreur de conversion en format français : {str(e)}")
        return ""


def qdate_to_date(qdate: QDate) -> datetime:
    """Convertit un QDate en datetime Python"""
    return datetime(qdate.year(), qdate.month(), qdate.day())


def validate_date_order(date1, date2) -> Tuple[bool, str]:
    """
    Vérifie si date1 est antérieure ou égale à date2
    Args:
        date1: Première date (peut être str, datetime, Timestamp)
        date2: Deuxième date (peut être str, datetime, Timestamp)
    Returns:
        Tuple[bool, str]: (Validité, Message d'erreur)
    """
    try:
        # Conversion en datetime si nécessaire
        if isinstance(date1, str):
            date1 = pd.to_datetime(date1)
        if isinstance(date2, str):
            date2 = pd.to_datetime(date2)

        if date1 > date2:
            return False, f"La date {to_french_format(date1)} ne peut pas être postérieure à {to_french_format(date2)}"

        return True, ""
    except Exception as e:
        return False, f"Erreur de validation des dates : {str(e)}"


def is_valid_age_range(birth_date, reference_date, min_age: int = 18, max_age: int = 65) -> Tuple[bool, str]:
    """
    Vérifie si l'âge est dans une plage valide
    Args:
        birth_date: Date de naissance
        reference_date: Date de référence (date des faits)
        min_age: Âge minimum (défaut 18)
        max_age: Âge maximum (défaut 65)
    Returns:
        Tuple[bool, str]: (Validité, Message d'erreur)
    """
    try:
        age = calculate_age(birth_date, reference_date)
        if age is None:
            return False, "Impossible de calculer l'âge"

        if age < min_age:
            return False, f"L'âge ({age} ans) est inférieur à l'âge minimum requis ({min_age} ans)"
        if age > max_age:
            return False, f"L'âge ({age} ans) dépasse l'âge maximum autorisé ({max_age} ans)"

        return True, ""
    except Exception as e:
        return False, f"Erreur de validation de l'âge : {str(e)}"


def convert_for_db(date_value) -> Optional[str]:
    """
    Convertit une date dans le format attendu par la base de données
    Args:
        date_value: Date à convertir (peut être str, datetime, Timestamp, QDate)
    Returns:
        str: Date au format 'YYYY-MM-DD' ou None si invalide
    """
    try:
        if isinstance(date_value, QDate):
            date_value = qdate_to_date(date_value)

        return adapt_date(date_value)
    except Exception as e:
        print(f"Erreur de conversion pour la BD : {str(e)}")
        return None

def calculate_service_years(entry_date: date, reference_date: date = None) -> int:
    """
    Calcule les années de service
    Args:
        entry_date: Date d'entrée en service
        reference_date: Date de référence (par défaut date actuelle)
    Returns:
        int: Années de service calculées
    """
    if not entry_date:
        return 0

    if not reference_date:
        reference_date = date.today()

    try:
        return relativedelta(reference_date, entry_date).years
    except Exception:
        return 0

def to_db_format(date_value: date) -> str:
    """Convertit une date au format de la base de données"""
    try:
        if isinstance(date_value, date):
            return date_value.strftime(DateHandler.DB_DATE_FORMAT)
        return ""
    except Exception:
        return ""


def str_to_date(date_str: str, my_format: str = None) -> Optional[date]:
    """Convertit une chaîne en date"""
    if not date_str:
        return None

    formats_to_try = [my_format] if my_format else [
        DateHandler.FR_DATE_FORMAT,
        DateHandler.DB_DATE_FORMAT,
        "%Y-%m-%d %H:%M:%S",  # Format SQLite timestamp
        "%d-%m-%Y",
        "%Y/%m/%d"
    ]

    for fmt in formats_to_try:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None

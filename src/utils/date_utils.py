import pandas as pd
from datetime import datetime

# def adapt_date(val):
#     """Convertit différents types de dates en format texte pour SQLite"""
#     if pd.isna(val):
#         return None
#     if isinstance(val, pd.Timestamp):
#         return val.strftime('%Y-%m-%d')
#     if isinstance(val, datetime):
#         return val.strftime('%Y-%m-%d')
#     if isinstance(val, str):
#         try:
#             # Spécifie le format français des dates
#             date_obj = pd.to_datetime(val, format='%d/%m/%Y', dayfirst=True)
#             return date_obj.strftime('%Y-%m-%d')
#         except:
#             return val
#     return str(val)

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

def calculate_age(birth_date):
    """
    Calcule l'âge à partir d'une date de naissance.
    Retourne None pour les dates invalides sans bloquer le processus.
    """
    if not birth_date:
        return None
    try:
        # Vérification du format de la date
        if isinstance(birth_date, str):
            # Si la date contient des '00' ou n'est pas au bon format
            if '00/' in birth_date or '/00' in birth_date:
                print(f"Date de naissance invalide : {birth_date}")
                return None

            day, month, year = birth_date.split('/')
            # Vérification supplémentaire des valeurs
            if not (1 <= int(day) <= 31 and 1 <= int(month) <= 12 and len(year) == 4):
                print(f"Date de naissance invalide : {birth_date}")
                return None

            born = pd.Timestamp(int(year), int(month), int(day))
        else:
            born = pd.to_datetime(birth_date)

        today = pd.Timestamp.now()
        age = today.year - born.year

        if (today.month, today.day) < (born.month, born.day):
            age -= 1

        return age

    except Exception as e:
        print(f"Erreur lors du calcul de l'âge pour la date {birth_date}: {str(e)}")
        return None


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

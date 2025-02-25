import sqlite3
from PyQt6.QtWidgets import QMessageBox
import logging

logger = logging.getLogger(__name__)


class DeleteCase:
    """Classe autonome pour gérer la suppression de dossiers"""

    def __init__(self, db_manager):
        self.db_manager = db_manager

    def delete_case(self, matricule: str, reference: str) -> bool:
        """
        Supprime un dossier et ses enregistrements liés

        Args:
            matricule: Matricule du gendarme
            reference: Référence du dossier

        Returns:
            bool: True si la suppression a réussi, False sinon
        """
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()

                # 1. Récupérer l'ID de la sanction associée
                cursor.execute("""
                    SELECT sanction_id 
                    FROM Dossiers 
                    WHERE matricule_dossier = ? AND reference = ?
                """, (matricule, reference))

                result = cursor.fetchone()
                if not result:
                    logger.warning(f"Dossier {reference} non trouvé pour le matricule {matricule}")
                    return False

                sanction_id = result[0]

                # 2. Début de la transaction
                cursor.execute("BEGIN TRANSACTION")

                try:
                    # 3. Supprimer le dossier
                    cursor.execute("""
                        DELETE FROM Dossiers 
                        WHERE matricule_dossier = ? AND reference = ?
                    """, (matricule, reference))

                    # 4. Supprimer la sanction associée
                    if sanction_id:
                        cursor.execute("DELETE FROM Sanctions WHERE id_sanction = ?", (sanction_id,))

                    # 5. Supprimer de la table main_tab si elle existe
                    try:
                        cursor.execute("DELETE FROM main_tab WHERE numero_dossier = ?", (reference,))
                    except sqlite3.OperationalError:
                        # La table main_tab n'existe peut-être pas
                        pass

                    # 6. Valider la transaction
                    cursor.execute("COMMIT")
                    logger.info(f"Dossier {reference} supprimé avec succès")
                    return True

                except Exception as e:
                    # Annuler la transaction en cas d'erreur
                    cursor.execute("ROLLBACK")
                    logger.error(f"Erreur lors de la suppression: {str(e)}")
                    raise

        except Exception as e:
            logger.error(f"Erreur lors de la suppression du dossier: {str(e)}")
            return False

    def show_confirmation_dialog(self, matricule: str, reference: str) -> bool:
        """
        Affiche une boîte de dialogue de confirmation

        Args:
            matricule: Matricule du gendarme
            reference: Référence du dossier

        Returns:
            bool: True si l'utilisateur confirme, False sinon
        """
        reply = QMessageBox.question(
            None,
            "Confirmation de suppression",
            f"Voulez-vous vraiment supprimer le dossier {reference} du gendarme {matricule} ?\n\n"
            "Cette action est irréversible.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes

    def delete_cases_batch(self, cases_list: list) -> tuple:
        """
        Supprime plusieurs dossiers en lot

        Args:
            cases_list: Liste de tuples (matricule, reference)

        Returns:
            tuple: (nombre de réussites, nombre d'échecs)
        """
        success_count = 0
        failure_count = 0

        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("BEGIN TRANSACTION")

            try:
                for matricule, reference in cases_list:
                    # 1. Récupérer l'ID de la sanction associée
                    cursor.execute("""
                        SELECT sanction_id 
                        FROM Dossiers 
                        WHERE matricule_dossier = ? AND reference = ?
                    """, (matricule, reference))

                    result = cursor.fetchone()
                    if not result:
                        failure_count += 1
                        continue

                    sanction_id = result[0]

                    # 2. Supprimer le dossier
                    cursor.execute("""
                        DELETE FROM Dossiers 
                        WHERE matricule_dossier = ? AND reference = ?
                    """, (matricule, reference))

                    # 3. Supprimer la sanction associée
                    if sanction_id:
                        cursor.execute("DELETE FROM Sanctions WHERE id_sanction = ?", (sanction_id,))

                    # 4. Supprimer de la table main_tab si elle existe
                    try:
                        cursor.execute("DELETE FROM main_tab WHERE numero_dossier = ?", (reference,))
                    except sqlite3.OperationalError:
                        # La table main_tab n'existe peut-être pas
                        pass

                    success_count += 1

                # Valider toutes les suppressions
                cursor.execute("COMMIT")
                return success_count, failure_count

            except Exception as e:
                cursor.execute("ROLLBACK")
                logger.error(f"Erreur lors de la suppression par lot: {str(e)}")
                return success_count, len(cases_list) - success_count
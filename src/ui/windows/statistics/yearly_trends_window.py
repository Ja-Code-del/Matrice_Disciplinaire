# yearly_trends_window.py
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QGridLayout,
                             QLabel, QFrame, QMessageBox)
from PyQt6.QtCore import Qt



class YearlyTrendsWindow(QMainWindow):
    def __init__(self, db_manager, year, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.year = year
        self.setWindowTitle(f"Tendances {year}")
        self.setMinimumSize(1000, 600)

        # Style des cartes
        self.card_style = """
        QFrame {
            background-color: white;
            border-radius: 15px;
            padding: 20px;
            margin: 10px;
        }
        QFrame:hover {
            border: 2px solid #6C63FF;
        }
        """

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QGridLayout(central_widget)

        # Titre
        title = QLabel(f"Analyse des tendances {self.year}")
        title.setStyleSheet("font-size: 24px; font-weight: bold; padding: 20px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title, 0, 0, 1, 3)

        # Création des cartes
        self.sanctions_card = self._create_card("total_sanctions", "#FF6B6B")
        self.grade_card = self._create_card("grade_plus", "#4ECDC4")
        self.subdiv_card = self._create_card("subdiv_plus", "#45B7D1")
        self.age_card = self._create_card("tranche_age", "#96CEB4")
        self.faute_card = self._create_card("type_faute", "#FFEEAD")
        self.mois_card = self._create_card("mois_critique", "#D4A5A5")
        self.region_card = self._create_card("region_moins", "#A8D5BA")


        # Disposition des cartes (3x2)
        main_layout.addWidget(self.sanctions_card, 1, 0)
        main_layout.addWidget(self.grade_card, 1, 1)
        main_layout.addWidget(self.subdiv_card, 1, 2)
        main_layout.addWidget(self.age_card, 2, 0)
        main_layout.addWidget(self.faute_card, 2, 1)
        main_layout.addWidget(self.mois_card, 2, 2)
        main_layout.addWidget(self.region_card, 3, 1)

    # def _create_card(self, card_type, color):
    #     card = QFrame()
    #     card.setStyleSheet(f"""
    #         QFrame {{
    #             background-color: {color};
    #             border-radius: 15px;
    #             padding: 20px;
    #             margin: 10px;
    #         }}
    #         QFrame:hover {{
    #             border: 2px solid #6C63FF;
    #         }}
    #     """)
    #
    #     layout = QVBoxLayout(card)
    #
    #     # Labels pour le contenu
    #     title = QLabel()
    #     value = QLabel()
    #     detail = QLabel()
    #
    #     for label in [title, value, detail]:
    #         label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    #         layout.addWidget(label)
    #
    #     # Garder une référence aux labels
    #     card.title_label = title
    #     card.value_label = value
    #     card.detail_label = detail
    #
    #     return card

    def _create_card(self, card, color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 15px;
                padding: 15px;
                color: black;
            }}
            QFrame:hover {{
                border: 1px solid #6C63FF;
                font-size: 43px;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setSpacing(5)

        # Labels
        title = QLabel()
        title.setStyleSheet("""
            font-size: 12px; 
            color: #666666;
            font-family: "Apple SD Gothic Neo", "Segoe UI", system-ui, -apple-system, sans-serif;
        """)

        value = QLabel()
        value.setStyleSheet("""
            font-size: 40px; 
            font-weight: bold;
            font-family: "Apple SD Gothic Neo", "Segoe UI", system-ui, -apple-system, sans-serif;
        """)

        detail = QLabel()
        detail.setStyleSheet("""
            font-size: 12px; 
            color: #666666;
            font-family: "Apple SD Gothic Neo", "Segoe UI", system-ui, -apple-system, sans-serif;
        """)

        for label in [title, value, detail]:
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setWordWrap(True)
            layout.addWidget(label)

        card.title_label = title
        card.value_label = value
        card.detail_label = detail

        card.setMinimumSize(300, 150)

        return card

    def load_data(self):
        try:
            with self.db_manager.get_connection() as conn:
                # Charger et mettre à jour chaque carte
                self._update_sanctions_card(conn)
                self._update_grade_card(conn)
                self._update_subdiv_card(conn)
                self._update_age_card(conn)
                self._update_faute_card(conn)
                self._update_mois_card(conn)
                self._update_region_card(conn)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur de chargement: {str(e)}")

    def _update_sanctions_card(self, conn):
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(DISTINCT id_dossier)
            FROM Dossiers
            WHERE annee_enr = ?
        """, (str(self.year),))
        total = cursor.fetchone()[0]

        self.sanctions_card.title_label.setText("Total des sanctions")
        self.sanctions_card.value_label.setText(str(total))
        self.sanctions_card.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.sanctions_card.value_label.setStyleSheet("font-size: 40px; font-weight: bold;")

    # Implémentation des autres méthodes _update_*_card()...
    def _update_grade_card(self, conn):
        query = """
        SELECT g.lib_grade, COUNT(DISTINCT d.id_dossier) as count,
               ROUND(COUNT(DISTINCT d.id_dossier) * 100.0 / 
               (SELECT COUNT(DISTINCT id_dossier) FROM Dossiers d 
                WHERE strftime('%Y', date_enr) = ?), 2) as percentage
        FROM Dossiers d 
        JOIN Grade g  ON d.grade_id = g.id_grade 
        WHERE strftime('%Y', d.date_enr) = ?
        GROUP BY g.lib_grade
        ORDER BY count DESC
        LIMIT 1
        """

        cursor = conn.cursor()
        cursor.execute(query, (str(self.year), str(self.year)))
        grade, count, percentage = cursor.fetchone()

        self.grade_card.title_label.setText("Grade le plus sanctionné")
        self.grade_card.value_label.setText(grade)
        self.grade_card.detail_label.setText(f"{count} sanctions ({percentage}%)")
        self.grade_card.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.grade_card.value_label.setStyleSheet("font-size: 32px; font-weight: bold;")
        self.grade_card.detail_label.setStyleSheet("font-size: 14px;")

    def _update_subdiv_card(self, conn):
        query = """
       SELECT s.lib_subdiv, COUNT(DISTINCT d.id_dossier) as count,
               ROUND(COUNT(DISTINCT d.id_dossier) * 100.0 / 
               (SELECT COUNT(DISTINCT id_dossier) FROM Dossiers d 
                WHERE strftime('%Y', date_enr) = ?), 2) as percentage
        FROM Dossiers d 
        JOIN Subdiv s   ON d.subdiv_id  = s.id_subdiv 
        WHERE strftime('%Y', d.date_enr) = ?
        GROUP BY s.lib_subdiv
        ORDER BY count DESC
        LIMIT 1
       """

        cursor = conn.cursor()
        cursor.execute(query, (str(self.year), str(self.year)))
        subdiv, count, percentage = cursor.fetchone()

        self.subdiv_card.title_label.setText("Subdivision la plus touchée")
        self.subdiv_card.value_label.setText(subdiv)
        self.subdiv_card.detail_label.setText(f"{count} sanctions ({percentage}%)")
        self.subdiv_card.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.subdiv_card.value_label.setStyleSheet("font-size: 32px; font-weight: bold;")
        self.subdiv_card.detail_label.setStyleSheet("font-size: 14px;")

    def _update_age_card(self, conn):
        query = """
       WITH service_ranges AS (
           SELECT 
               CASE 
                   WHEN g.annee_service BETWEEN 0 AND 5 THEN '0-5 ans'
                   WHEN g.annee_service BETWEEN 6 AND 10 THEN '6-10 ans'
                   WHEN g.annee_service BETWEEN 11 AND 15 THEN '11-15 ans'
                   WHEN g.annee_service BETWEEN 16 AND 20 THEN '16-20 ans'
                   WHEN g.annee_service BETWEEN 21 AND 25 THEN '21-25 ans'
                   ELSE '25+ ans'
               END as tranche,
               COUNT(DISTINCT d.id_dossier) as count
           FROM Dossiers d
           JOIN gendarmes g ON d.matricule_dossier = g.matricule
           WHERE strftime('%Y', d.date_enr) = ?
           GROUP BY tranche
       )
       SELECT tranche, count, 
              ROUND(count * 100.0 / SUM(count) OVER(), 2) as percentage
       FROM service_ranges
       ORDER BY count DESC
       LIMIT 1
       """

        cursor = conn.cursor()
        cursor.execute(query, (str(self.year),))
        tranche, count, percentage = cursor.fetchone()

        self.age_card.title_label.setText("Tranche d'ancienneté critique")
        self.age_card.value_label.setText(tranche)
        self.age_card.detail_label.setText(f"{count} sanctions ({percentage}%)")
        self.age_card.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.age_card.value_label.setStyleSheet("font-size: 32px; font-weight: bold;")
        self.age_card.detail_label.setStyleSheet("font-size: 14px;")

    def _update_faute_card(self, conn):
        query = """
       SELECT f.lib_faute, COUNT(DISTINCT d.id_dossier) as count,
               ROUND(COUNT(DISTINCT d.id_dossier) * 100.0 / 
               (SELECT COUNT(DISTINCT id_dossier) FROM Dossiers d 
                WHERE strftime('%Y', date_enr) = ?), 2) as percentage
        FROM Dossiers d 
        JOIN Fautes f  ON d.faute_id  = f.id_faute
        WHERE strftime('%Y', d.date_enr) = ?
        GROUP BY f.lib_faute 
        ORDER BY count DESC
        LIMIT 1
       """

        cursor = conn.cursor()
        cursor.execute(query, (str(self.year), str(self.year)))
        faute, count, percentage = cursor.fetchone()

        self.faute_card.title_label.setText("Faute la plus commise")
        self.faute_card.value_label.setText(faute)
        self.faute_card.detail_label.setText(f"{count} cas ({percentage}%)")
        self.faute_card.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.faute_card.value_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.faute_card.detail_label.setStyleSheet("font-size: 14px;")

    def _update_mois_card(self, conn):
        query = """
           SELECT strftime('%m', date_enr) as mois, 
                  COUNT(DISTINCT id_dossier) as count,
                  ROUND(COUNT(DISTINCT id_dossier) * 100.0 / 
                  (SELECT COUNT(DISTINCT id_dossier) FROM Dossiers 
                   WHERE strftime('%Y', date_enr) = ?), 2) as percentage
           FROM Dossiers
           WHERE strftime('%Y', date_enr) = ?
           GROUP BY mois
           ORDER BY count DESC
           LIMIT 1
       """

        mois_dict = {
            '01': 'Janvier', '02': 'Février', '03': 'Mars', '04': 'Avril',
            '05': 'Mai', '06': 'Juin', '07': 'Juillet', '08': 'Août',
            '09': 'Septembre', '10': 'Octobre', '11': 'Novembre', '12': 'Décembre'
        }

        cursor = conn.cursor()
        cursor.execute(query, (str(self.year), str(self.year)))
        mois, count, percentage = cursor.fetchone()

        self.mois_card.title_label.setText("Mois avec le plus fort taux d'enregistrement")
        self.mois_card.value_label.setText(mois_dict[mois])
        self.mois_card.detail_label.setText(f"{count} sanctions ({percentage}%)")
        self.mois_card.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.mois_card.value_label.setStyleSheet("font-size: 32px; font-weight: bold;")
        self.mois_card.detail_label.setStyleSheet("font-size: 14px;")

    def _update_region_card(self, conn):
        query = """
           WITH region_counts AS (
               SELECT r.lib_rg, COUNT(DISTINCT d.id_dossier) AS count
               FROM Region r 
               LEFT JOIN Dossiers d ON CAST(d.rg_id AS TEXT) = r.id_rg
                   AND strftime('%Y', d.date_enr) = ?
               WHERE r.lib_rg IS NOT NULL
               GROUP BY r.lib_rg 
           )
           SELECT lib_rg, count,
                  ROUND(count * 100.0 / (SELECT SUM(count) FROM region_counts), 2) AS percentage
           FROM region_counts
           WHERE count = (SELECT MIN(count) FROM region_counts)
           ORDER BY count ASC;
        """

        cursor = conn.cursor()
        cursor.execute(query, (str(self.year),))
        results = cursor.fetchall()

        if not results:
            region_text = "Non spécifié"
            detail_text = "Aucune donnée disponible"
        else:
            # Extraire les informations
            regions = [row[0] for row in results]  # Liste des régions ayant le minimum
            count = results[0][1]  # Même count pour toutes
            percentage = results[0][2]  # Même pourcentage pour toutes

            # Construire l'affichage des régions
            region_text = regions[0]  # Affiche une région en titre
            other_regions = ", ".join(regions[1:])  # Liste des autres régions si elles existent

            if other_regions:
                detail_text = f"{count} sanctions ({percentage}%) - Autres : {other_regions}"
            else:
                detail_text = f"{count} sanctions ({percentage}%)"

        # Mise à jour des labels
        self.region_card.title_label.setText("Région la moins exposée")
        self.region_card.value_label.setText(region_text)
        self.region_card.detail_label.setText(detail_text)

        # Styles
        self.region_card.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.region_card.value_label.setStyleSheet("font-size: 32px; font-weight: bold;")
        self.region_card.detail_label.setStyleSheet("font-size: 14px;")








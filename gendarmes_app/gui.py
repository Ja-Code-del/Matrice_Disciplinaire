import tkinter as tk
from data_manager import add_gendarme, research_gendarme


def launch_app():
    # Créer la fenêtre principale
    root = tk.Tk()
    root.title("Gestion des Gendarmes Punis")

    # Fonction pour nettoyer la fenêtre (effacer les widgets existants)
    def clear_frame(frame):
        for widget in frame.winfo_children():
            widget.destroy()

    # Interface pour ajouter un gendarme
    def interface_ajouter():
        clear_frame(root)
        tk.Label(root, text="Ajouter un Gendarme").pack()

        tk.Label(root, text="MLE").pack()
        matricule_entry = tk.Entry(root)
        matricule_entry.pack()

        tk.Label(root, text="NOM ET PRENOMS").pack()
        nom_entry = tk.Entry(root)
        nom_entry.pack()

        tk.Label(root, text="FAUTE COMMISE").pack()
        motif_entry = tk.Entry(root)
        motif_entry.pack()

        # Ajouter le gendarme à l'appui du bouton
        tk.Button(root, text="Ajouter", command=lambda: add_gendarme(
            matricule_entry.get(), nom_entry.get(), motif_entry.get())
                  ).pack()

    # Interface pour rechercher un gendarme
    def interface_recherche():
        clear_frame(root)
        tk.Label(root, text="Rechercher un Gendarme").pack()
        tk.Label(root, text="Matricule").pack()
        matricule_entry = tk.Entry(root)
        matricule_entry.pack()

        result_label = tk.Label(root, text="")
        result_label.pack()

        # Rechercher le gendarme à l'appui du bouton
        def recherche_action():
            resultat = research_gendarme(matricule_entry.get())
            if resultat:
                result_label.config(text=f"Gendarme trouvé: {resultat['NOM ET PRENOMS']}, Motif: {resultat['FAUTE COMMISE']}")
            else:
                result_label.config(text="Aucun gendarme trouvé avec ce matricule.")

        tk.Button(root, text="Rechercher", command=recherche_action).pack()

    # Boutons pour naviguer entre les interfaces
    tk.Button(root, text="Ajouter Gendarme", command=interface_ajouter).pack()
    tk.Button(root, text="Rechercher Gendarme", command=interface_recherche).pack()

    # Lancer la boucle principale de l'application Tkinter
    root.mainloop()


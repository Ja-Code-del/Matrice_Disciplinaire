import pandas as pd

# Chemin du fichier Excel
file_path = "data/gendarmes_data.xlsx"

# Charger le fichier Excel
def load_data():
    try:
        return pd.read_excel(file_path)
    except FileNotFoundError:
        return pd.DataFrame(columns=["Matricule", "Nom", "Motif"])

df = load_data()

# Ajouter un nouveau gendarme
def add_gendarme(matricule, nom, motif):
    global df
    new_row = {"MLE": matricule, "NOM ET PRENOMS": nom, "FAUTE COMMISE": motif}
    df = df.append(new_row, ignore_index=True)
    df.to_excel(file_path, index=False)
    print(f"Gendarme {nom} ajouté avec succès.")

# Rechercher un gendarme par matricule
def research_gendarme(matricule):
    global df
    # S'assurer que les matricules sont comparés sous forme de chaîne de caractères
    df["Matricule"] = df["Matricule"].astype(str)  # Convertir toute la colonne Matricule en chaîne
    matricule = str(matricule)  # Convertir l'entrée utilisateur en chaîne de caractères

    gendarme = df[df["Matricule"] == matricule]
    if not gendarme.empty:
        return gendarme.iloc[0]  # Retourner la première correspondance
    else:
        return None



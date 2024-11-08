# src/data/gendarmerie/structure.py

from src.data.gendarmerie.regions import REGIONS_STRUCTURE
from src.data.gendarmerie.csg import CSG_STRUCTURE

STRUCTURE_PRINCIPALE = {
    "REGIONS": REGIONS_STRUCTURE,
    "CSG": CSG_STRUCTURE
}

# Subdivisions de la gendarmerie
SUBDIVISIONS = [
    "CSG",
    "GT",
    "GM",
    "GRURGN",
    "US",
    "CECF",
    "RG"
]

SERVICE_RANGES = [
    "0-5 ANS",
    "6-10 ANS",
    "11-15 ANS",
    "16-20 ANS",
    "21-25 ANS",
    "26-30 ANS",
    "31-35 ANS",
    "36-40 ANS"
]

# Thèmes d'analyse statistique
ANALYSIS_THEMES = {
    "Année": {
        "field": "annee_punition",
        "subfields": ["Fautes commises", "Statut", "Subdivision",
                      "Catégorie de Fautes", "Dossiers disciplinaires complet",
                      "Situation matrimoniale", "Tranches années service", "Grades"]
    },
    "Fautes commises": {
        "field": "faute_commise",
        "subfields": ["Statut", "Subdivision", "Catégorie de Fautes",
                      "Dossiers disciplinaires complet", "Situation matrimoniale",
                      "Tranches années service", "Grades", "Année"]
    },
    "Statut": {
        "field": "statut",
        "subfields": ["Subdivision", "Catégorie de Fautes",
                      "Dossiers disciplinaires complet", "Situation matrimoniale",
                      "Tranches années service", "Grades", "Année", "Fautes commises"]
    },
    "Subdivision": {
        "field": "subdiv",
        "subfields": ["Catégorie de Fautes", "Dossiers disciplinaires complet",
                      "Situation matrimoniale", "Tranches années service", "Grades",
                      "Année", "Fautes commises", "Statut"]
    },
    "Catégorie de Fautes": {
        "field": "categorie",
        "subfields": ["Dossiers disciplinaires complet", "Situation matrimoniale",
                      "Tranches années service", "Grades", "Année", "Fautes commises",
                      "Statut", "Subdivision"]
    },
    "Dossiers disciplinaires complet": {
        "field": "nom_prenoms",
        "subfields": ["Situation matrimoniale", "Tranches années service", "Grades",
                      "Année", "Fautes commises", "Statut", "Subdivision",
                      "Catégorie de Fautes"]
    },
    "Situation matrimoniale": {
        "field": "situation_matrimoniale",
        "subfields": ["Tranches années service", "Grades", "Année", "Fautes commises",
                      "Statut", "Subdivision", "Catégorie de Fautes",
                      "Dossiers disciplinaires complet"]
    },
    "Tranches années service": {
        "field": "annee_service",
        "subfields": ["Grades", "Année", "Fautes commises", "Statut", "Subdivision",
                      "Catégorie de Fautes", "Dossiers disciplinaires complet",
                      "Situation matrimoniale"]
    },
    "Grades": {
        "field": "grade",
        "subfields": ["Tranches années service", "Année", "Fautes commises", "Statut", "Subdivision",
                      "Catégorie de Fautes", "Dossiers disciplinaires complet",
                      "Situation matrimoniale"]
    }
}

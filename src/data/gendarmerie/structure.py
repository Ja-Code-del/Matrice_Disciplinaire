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
    "0-5",
    "6-10",
    "11-15",
    "16-20",
    "21-25",
    "26-30",
    "31-35",
    "36-40"
]

FAUTES_COMMISES = [
    "ABSENCE IRREGULIERE PROLONGEE",
    "FAUTE CONTRE L'HONNEUR",
    "NON-RESPECT DES CONSIGNES",
    "ABSENCE IRREGULIERE",
    "ABANDON DE POSTE",
    "FAUTE DE COMPORTEMENT",
    "EVASION GARDE A VUE",
    "FAUTE PROFESSIONNELLE",
    "EXTORSION DE FONDS",
    "TENTATIVE D'EXTORSION DE FONDS",
    "INDISCIPLINE",
    "NEGLIGENCE PROFESSIONNELLE",
    "IMPRUDENCE",
    "PERTE D'ARME"
]

# Thèmes d'analyse statistique
#TODO- ADD LEGION, REGION AND TYPE OF SANCTION
ANALYSIS_THEMES = {
    "Année": {
        "field": "annee_enr",
        "subfields": ["Fautes commises", "Statut","Région","Légion", "Subdivision",
                      "Catégorie de Fautes", "Dossiers disciplinaires complet",
                      "Situation matrimoniale", "Tranches années service", "Grades", "Types de sanction"]
    },
    "Fautes commises": {
        "field": "lib_faute",
        "subfields": ["Statut","Région","Légion", "Subdivision", "Catégorie de Fautes",
                      "Dossiers disciplinaires complet", "Situation matrimoniale",
                      "Tranches années service", "Grades","Types de sanction", "Année"]
    },
    "Statut": {
        "field": "lib_statut",
        "subfields": ["Région","Légion","Subdivision", "Catégorie de Fautes",
                      "Dossiers disciplinaires complet", "Situation matrimoniale",
                      "Tranches années service", "Grades","Types de sanction", "Année", "Fautes commises"]
    },
    "Région": {
        "field": "lib_rg",
        "subfields": ["Légion", "Subdivision", "Catégorie de Fautes",
                      "Dossiers disciplinaires complet", "Situation matrimoniale",
                      "Tranches années service", "Grades","Types de sanction", "Année", "Fautes commises", "Type de sanction"]
    },
    "Légion": {
        "field": "lib_legion",
        "subfields": ["Région", "Subdivision", "Catégorie de Fautes",
                      "Dossiers disciplinaires complet", "Situation matrimoniale",
                      "Tranches années service", "Grades","Types de sanction", "Année", "Fautes commises", "Type de sanction"]
    },
    "Type de sanction": {
        "field": "lib_type_sanction",
        "subfields": ["Région","Légion", "Subdivision", "Catégorie de Fautes",
                      "Dossiers disciplinaires complet", "Situation matrimoniale",
                      "Tranches années service", "Grades", "Année", "Fautes commises"]
    },
    "Subdivision": {
        "field": "lib_subdiv",
        "subfields": ["Région","Légion","Catégorie de Fautes", "Dossiers disciplinaires complet",
                      "Situation matrimoniale", "Tranches années service", "Grades","Types de sanction",
                      "Année", "Fautes commises", "Statut"]
    },
    "Catégorie de Fautes": {
        "field": "id_categorie",
        "subfields": ["Dossiers disciplinaires complet", "Situation matrimoniale",
                      "Tranches années service", "Grades","Types de sanction", "Année", "Fautes commises",
                      "Statut", "Région","Légion", "Subdivision"]
    },
    "Situation matrimoniale": {
        "field": "lib_sit_mat",
        "subfields": ["Tranches années service", "Grades","Types de sanction", "Année", "Fautes commises",
                      "Statut","Région","Légion", "Subdivision", "Catégorie de Fautes",
                      "Dossiers disciplinaires complet"]
    },
    "Tranches années service": {
        "field": "annee_service",
        "subfields": ["Grades","Types de sanction", "Année", "Fautes commises", "Statut","Région","Légion", "Subdivision",
                      "Catégorie de Fautes", "Dossiers disciplinaires complet",
                      "Situation matrimoniale"]
    },
    "Grades": {
        "field": "lib_grade",
        "subfields": ["Types de sanction","Tranches années service", "Année", "Fautes commises", "Statut","Région","Légion", "Subdivision",
                      "Catégorie de Fautes", "Dossiers disciplinaires complet",
                      "Situation matrimoniale"]
    }
}

STRUCTURE_UNITE = {
    "REGIONS": {
        "1°RG": {
            "GT": {
                "EM": ["EM GT"],
                "1° LGT": [
                    "EM-CIE ABJ-OUEST",
                    "BDE YOP-TOITS-ROUGES",
                    "BDE YOP NORD",
                    "BDE AUTOROUTE",
                    "BDE SONGON",
                    "EM-CIE ABJ-EST",
                    "BDE COCODY",
                    "BDE ANGRE",
                    "BDE ABJ ROUTE",
                    "BDE BINGERVILLE",
                    "EM-CIE ABJ-NORD",
                    "BDE ANYAMA",
                    "BDE ABOBO-GARE",
                    "BDE ABOBO-NORD",
                    "BDE ATTECOUBE",
                    "BDE ADJAME",
                    "EM-CIE ABJ-SUD",
                    "BDE KOUMASSI",
                    "BDE MARCORY",
                    "BDE TREICHVILLE",
                    "BDE PORT-BOUET",
                    "EM-CIE GRD-BASSAM",
                    "BDE GRD-BASSAM",
                    "BDE BONOUA",
                    "BDE BONGO",
                    "EM-CIE ABOISSO",
                    "BDE ABOISSO",
                    "BDE ADIAKE",
                    "BDE AYAME",
                    "BDE EHANIA",
                    "BDE MAFERE",
                    "BDE ASSINI",
                    "BDE BIANOUAN",
                    "BDE TIAPOUM"
                ],
                "7° LGT": [
                    "EM-CIE ABENGOUROU",
                    "BDE VILLE ABENGOUROU",
                    "BDE ROUTE ABENGOUROU",
                    "BDE RECHERCHE ABENGOUROU",
                    "BDE AGNIBILEKRO",
                    "BDE EBILASSOKRO",
                    "BDE AMELEKIA",
                    "BDE ANIASSUE",
                    "BDE BETTIE",
                    "BDE NIABLE",
                    "EM-CIE ADZOPE",
                    "BDE ADZOPE",
                    "BDE AGOU",
                    "BDE AKOUPE",
                    "BDE YAKASSE-ATTOBROU",
                    "BDE ALEPE"
                ],
                "10° LGT": [
                    "EM-CIE DIVO",
                    "BDE DIVO",
                    "BDE GUITRY",
                    "BDE LAKOTA",
                    "BDE HIRE",
                    "EM-CIE TIASSALE",
                    "BDE TIASSALE",
                    "BDE N'DOUCI ROUTE",
                    "BDE TAABO",
                    "BDE SIKENSI",
                    "EM-CIE AGBOVILLE",
                    "BDE AGBOVILLE",
                    "BDE RUBINO",
                    "BDE AZAGUIE",
                    "BDE CECHI",
                    "BDE LOVIGUIE",
                    "EM-CIE DABOU",
                    "BDE DABOU",
                    "BDE DABOU-RECHERCHE",
                    "BDE GRD-LAHOU",
                    "BDE JACQUEVILLE",
                    "BDE AHOUANOU"
                ]
            },
            "GM": {
                "EM": ["EM GM"],
                "1° LGM": [
                    "EM-1°LGM",
                    "ESC AGBAN",
                    "ESC YOPOUGON",
                    "ESC ABOBO",
                    "ESC KOUMASSI",
                    "ESC ABOISSO",
                    "ESC BINGERVILLE"
                ],
                "7° LGM": [
                    "EM-7°LGM",
                    "ESC ABENGOUROU",
                    "ESC ADZOPE",
                    "ESC BONGOUANOU"
                ],
                "10° LGM": [
                    "EM-10°LGM",
                    "ESC AGBOVILLE",
                    "ESC DABOU",
                    "ESC DIVO"
                ]
            },
            "CSG": {
                "CAB": ["CAB"],
                "IGN": ["IGN"],
                "IGGN": ["IGGN"],
                "OG-OPS": ["OG-OPS"],
                "DOE": [
                    "ORGANISATION",
                    "EMPLOI",
                    "SPORT",
                    "STATISTIQUE"
                ],
                "DRF": [
                    "REGIE DES AVANCES",
                    "SOLDE",
                    "DEPLACEMENT TRANSPORT",
                    "ETUDE PROJET",
                    "PLAN BUDGET"
                ],
                "DRH": [
                    "PERSONNEL OFFICIER ET CIVIL",
                    "PERSONNEL SOUS-OFFICIER",
                    "RECRUTEMENT-CHANCELLERIE",
                    "ACTION SOCIALE",
                    "EFFECTIFS"
                ],
                "DTI": [
                    "INFORMATIQUE",
                    "TELECOMMUNICATION"
                ],
                "D.SANTE": ["D.SANTE"],
                "DLOG": [
                    "MATERIELS-INTENDANCE",
                    "CARBURANT",
                    "PLANIFICATION DOMAINE ET INFRASTRUCTURE",
                    "CASERNEMENT",
                    "PARC AUTOMOBILE"
                ],
                "DCOD": ["COMMUNICATION"]
            },
            "GRURGN": {
                "GRURGN": [
                    "EM-GRURGN",
                    "URGN",
                    "GCS",
                    "GSR",
                    "GSPR",
                    "GS-LOI",
                    "GS-LEIPA",
                    "BIRGN",
                    "ESH /P.ESCORTE",
                    "ESH /P.HONNEUR",
                    "ESH /P.MUSIQUE",
                    "ULCIR",
                    "GDR",
                    "BRRO"
                ],
                "CENTRE DE RENSEIGNEMENT OPERATIONNEL": [
                    "SECTION RENSEIGNEMENT",
                    "SECTION ANALYSES TRACES TECHNOLOGIQUES"
                ],
                "DROGUES-FICHIER-CYNOPHILE": [
                    "SECTION ANTI-DROGUE",
                    "SECTION FICHIER",
                    "SECTION CYNOPHILE"
                ]
            },
            "US": {
                "US": [
                    "EM US",
                    "GSP ABIDJAN",
                    "GSP SAN-PEDRO",
                    "GEB-GN",
                    "UIGN",
                    "EPHP",
                    "GSA",
                    "PSA BOUAKE",
                    "PSA KORHOGO",
                    "PSA SAN-PEDRO",
                    "PSA YAKRO",
                    "PSA MAN",
                    "PSA ODIENNE"
                ]
            },
            "CECF": {
                "CECF": [
                    "EM-CECF",
                    "EGA",
                    "EGT",
                    "GIP-GN",
                    "CFEC"
                ]

            },
            "RG": {
                "RG": [
                    "EM-1°RG",
                    "EM-2°RG",
                    "EM-3°RG",
                    "EM-4°RG"
                ]
            }
        },
        "2°RG": {
            "GT": {
                "2° LGT": [
                    "EM-CIE DALOA",
                    "BDE VILLE DALOA",
                    "BDE ROUTE DALOA",
                    "BDE VAVOUA",
                    "BDE ZOUKOUGBEU",
                    "EM-CIE BOUAFLE",
                    "BDE BOUAFLE",
                    "BDE BONON",
                    "BDE ZUENOULA",
                    "BDE GOHITAFLA",
                    "EM-CIE GAGNOA",
                    "BDE GAGNOA",
                    "BDE OUME",
                    "BDE GUIBEROUA",
                    "BDE DIEGONEFLA",
                    "BDE BAYOTA",
                    "BDE OURAGAHIO",
                    "EM-CIE ISSIA",
                    "BDE ISSIA",
                    "BDE SINFRA",
                    "BDE SAIOUA",
                    "BDE KONONFLA"
                ],
                "5° LGT": [
                    "EM-CIE SAN-PEDRO",
                    "BDE VILLE SAN-PEDRO",
                    "BDE ROUTE SAN-PEDRO",
                    "BDE TABOU",
                    "BDE SASSANDRA",
                    "BDE GRD-BEREBY",
                    "BDE FRESCO",
                    "BDE GRABO",
                    "BDE DJOUROUTOU",
                    "BDE RECHERCHE SAN-PEDRO",
                    "EM-CIE SOUBRE",
                    "BDE SOUBRE",
                    "BDE BUYO",
                    "BDE GUEYO",
                    "BDE MEAGUI",
                    "BDE OKROUYO",
                    "BDE GRD-ZATRY"
                ],
                "8° LGT": [
                    "EM-CIE MAN",
                    "BDE MAN",
                    "BDE BIANKOUMAN",
                    "BDE LOGOUALE",
                    "BDE SANGOUINE",
                    "EM-CIE GUIGLO",
                    "BDE GUIGLO",
                    "BDE TAI",
                    "BDE BLOLEQUIN",
                    "BDE TOULEPLEU"
                    "EM-CIE DANANE",
                    "BDE DANANE",
                    "BDE SIPILOU",
                    "BDE ZOUAN-HOUNIEN"
                    "EM-CIE DUEKOUE",
                    "BDE BONGOUANOU",
                    "BDE KOUIBLY",
                    "BDE FACOBLY",
                    "BDE ZOU"
                ]
            },
            "GM": {
                "2° LGM": [
                    "EM-2°LGM",
                    "ESC DALOA",
                    "ESC GAGNOA",
                    "ESC ZUENOULA",
                ],
                "5° LGM": [
                    "EM-5°LGM",
                    "ESC SAN-PEDRO",
                    "ESC SOUBRE",
                    "ESC TABOU",
                    "ESC FRESCO"
                ],
                "8° LGM": [
                    "EM-8°LGM",
                    "ESC MAN",
                    "ESC TOULEPLEU",
                    "ESC DANANE"
                ]
            }
        },
        "3°RG": {
            "GT": {
                "3° LGT": [
                    "EM-CIE BOUAKE",
                    "BDE VILLE BOUAKE",
                    "BDE ROUTE BOUAKE",
                    "BDE DJEBONOUA",
                    "BDE BROBO",
                    "EM-CIE KATIOLA",
                    "BDE KATIOLA",
                    "BDE DABAKALA",
                    "BDE NIAKARA",
                    "BDE BONIERE",
                    "BDE TAFIRE",
                    "BDE TORTIYA",
                    "BDE SATAMA-SOKOURA",
                    "EM-CIE SAKASSOU",
                    "BDE SAKASSOU",
                    "BDE BEOUMI",
                    "BDE BOTRO",
                    "BDE BODOKRO"
                ],
                "6° LGT": [
                    "EM-CIE YAKRO",
                    "BDE VILLE YAKRO",
                    "BDE ROUTE YAKRO",
                    "BDE RECHERCHE YAKRO",
                    "BDE KOSSOU",
                    "BDE TOUMODI",
                    "BDE TIEBISSOU",
                    "BDE DJEKANOU",
                    "BDE DIDIEVI",
                    "BDE TIE N'DIEKRO",
                    "EM-CIE DIMBOKRO",
                    "BDE DIMBOKRO",
                    "BDE BOCANDA",
                    "BDE BONGOUANOU",
                    "BDE M'BATTO",
                    "EM-CIE DAOUKRO",
                    "BDE DAOUKRO",
                    "BDE ARRAH",
                    "BDE M'BAHIAKRO",
                    "BDE PRIKRO",
                    "BDE OUELLE",
                    "BDE KOKUMBO"
                ],
                "11° LGT": [
                    "EM-CIE BONDOUKOU",
                    "BDE BONDOUKOU",
                    "BDE TRANSUA",
                    "BDE ASSUEFRY",
                    "BDE TABAGNE",
                    "BDE GOUMERE",
                    "EM-CIE BOUNA",
                    "BDE BOUNA",
                    "BDE NASSIAN",
                    "BDE TEHINI",
                    "BDE DOROPO",
                    "EM-CIE TANDA",
                    "BDE TANDA",
                    "BDE KOUN-FAO",
                    "BDE SANDEGUE"
                ]
            },
            "GM": {
                "3° LGM": [
                    "EM-3°LGM",
                    "ESC BOUAKE",
                    "ESC MARABADIASSA",
                    "ESC NIAKARA",
                    "ESC DABAKALA"
                ],
                "6° LGM": [
                    "EM-6°LGM",
                    "ESC YAKRO",
                    "ESC DAOUKRO",
                    "ESC DIMBOKRO"
                ],
                "11° LGM": [
                    "EM-11°LGM",
                    "ESC BONDOUKOU",
                    "ESC KOUN-FAO",
                    "ESC BOUNA"
                ]
            }
        },
        "4°RG": {
            "GT": {
                "4° LGT": [
                    "EM-CIE KORHOGO-OUEST",
                    "BDE M'BENGUE",
                    "BDE DIKODOUGOU",
                    "BDE SIRASSO",
                    "BDE NIOFOUIN",
                    "BDE KONI",
                    "EM-CIE KORHOGO-EST",
                    "BDE VILLE KORHOGO",
                    "BDE ROUTE KORHOGO",
                    "BDE SINEMATIALI",
                    "BDE NAPIE",
                    "EM-CIE BOUNDIALI",
                    "BDE BOUNDIALI",
                    "BDE TENGRELA",
                    "BDE GBON",
                    "BDE TAFIRE"
                    "EM-CIE FERKE",
                    "BDE FERKE",
                    "BDE OUANGOLO",
                    "BDE KONG",
                    "BDE NIELLE",
                    "BDE DIAWALA"
                ],
                "9° LGT": [
                    "EM-CIE ODIENNE-OUEST",
                    "BDE ODIENNE VILLE",
                    "BDE MINIGNAN",
                    "BDE BAKO",
                    "BDE SAMATIGUILA",
                    "BDE GBELEBAN",
                    "EM-CIE ODIENNE-EST",
                    "BDE ODIENNE ROUTE",
                    "BDE ODIENNE RECHERCHE",
                    "BDE ODIENNE MADINANI",
                    "BDE TIEME",
                    "BDE FENGOLO",
                    "BDE SEGUELON",
                    "EM-CIE SEGUELA",
                    "BDE SEGUELA",
                    "BDE KANI",
                    "BDE MANKONO",
                    "BDE DIANRA",
                    "BDE TIENINGBOUE",
                    "BDE KOUNAHIRI",
                    "EM-CIE TOUBA",
                    "BDE TOUBA",
                    "BDE BOROTOU-KORO",
                    "BDE GUINTEGUELA"
                ]
            },
            "GM": {
                "4° LGM": [
                    "EM-4°LGM",
                    "ESC KORHOGO",
                    "ESC FERKE",
                    "ESC KONG",
                    "ESC TENGRELA"
                ],
                "9° LGM": [
                    "EM-9°LGM",
                    "ESC ODIENNE",
                    "ESC SEGUELA",
                    "ESC TOUBA"
                ]
            }

        }
    }
}

STRUCTURE_CSG = {
    "CSG": {
        "CAB": ["CAB"],
        "IGN": ["IGN"],
        "IGGN": ["IGGN"],
        "OG-OPS": ["OG-OPS"],
        "DOE": [
            "ORGANISATION",
            "EMPLOI",
            "SPORT",
            "STATISTIQUE"
        ],
        "DRF": [
            "REGIE DES AVANCES",
            "SOLDE",
            "DEPLACEMENT TRANSPORT",
            "ETUDE PROJET",
            "PLAN BUDGET"
        ],
        "DRH": [
            "PERSONNEL OFFICIER ET CIVIL",
            "PERSONNEL SOUS-OFFICIER",
            "RECRUTEMENT-CHANCELLERIE",
            "ACTION SOCIALE",
            "EFFECTIFS"
        ],
        "DTI": [
            "INFORMATIQUE",
            "TELECOMMUNICATION"
        ],
        "D.SANTE": ["D.SANTE"],
        "DLOG": [
            "MATERIELS-INTENDANCE",
            "CARBURANT",
            "PLANIFICATION DOMAINE ET INFRASTRUCTURE",
            "CASERNEMENT",
            "PARC AUTOMOBILE"
        ],
        "DCOD": ["COMMUNICATION"]
    },
    "GRURGN": {
        "GRURGN": [
            "EM-GRURGN",
            "URGN",
            "GCS",
            "GSR",
            "GS-LOI",
            "GS-LEIPA",
            "BIRGN",
            "ESH",
            "ULCIR",
            "BSR1",
            "BSR2",
            "BSR3",
            "GDR",
            "BRRO"
        ],
        "CENTRE DE RENSEIGNEMENT OPERATIONNEL": [
            "SECTION RENSEIGNEMENT",
            "SECTION ANALYSES TRACES TECHNOLOGIQUES"
        ],
        "DROGUES-FICHIER-CYNOPHILE": [
            "SECTION ANTI-DROGUE",
            "SECTION FICHIER",
            "SECTION CYNOPHILE"
        ]
    },
    "US": {
        "US": [
            "EM US",
            "GSP ABIDJAN",
            "GSP SAN-PEDRO",
            "GEB-GN",
            "UIGN",
            "EPHP",
            "GSA",
            "PSA BOUAKE",
            "PSA KORHOGO",
            "PSA SAN-PEDRO",
            "PSA YAKRO",
            "PSA MAN",
            "PSA ODIENNE"
        ]
    },
    "CECF": {
        "CECF": [
            "EM-CECF",
            "EGA",
            "EGT",
            "GIP-GN",
            "CFEC"
        ]

    },
    "RG": {
        "RG": [
            "EM-1°RG",
            "EM-2°RG",
            "EM-3°RG",
            "EM-4°RG",
        ]
    }
}


class Unit:
    def __init__(self, name, region, subdivision, legion):
        self.name = name
        self.region = region
        self.subdivision = subdivision
        self.legion = legion

    def __str__(self):
        return self.name


def get_all_unit_names(structure):
    unit_names = []
    for region, region_data in structure["REGIONS"].items():
        for subdivision, subdivision_data in region_data.items():
            for legion, legion_data in subdivision_data.items():
                if isinstance(legion_data, list):
                    unit_names.extend(legion_data)
                else:
                    for cie, cie_units in legion_data.items():
                        unit_names.extend(cie_units)
    return unit_names


def get_all_regions(structure):
    return list(structure["REGIONS"].keys())


def get_all_subdivisions(structure, region):
    if region in structure["REGIONS"]:
        return list(structure["REGIONS"][region].keys())
    return []


def get_all_legions(structure, region, subdivision):
    if region in structure["REGIONS"] and subdivision in structure["REGIONS"][region]:
        legion_data = structure["REGIONS"][region][subdivision]
        if isinstance(legion_data, dict):
            return list(legion_data.keys())
        else:
            return legion_data
    return []

def get_unit_by_name(structure, unit_name):
    for region, region_data in structure["REGIONS"].items():
        for subdivision, subdivision_data in region_data.items():
            for legion, legion_data in subdivision_data.items():
                if isinstance(legion_data, list):
                    if unit_name in legion_data:
                        return Unit(unit_name, region, subdivision, legion)
                else:
                    for cie, cie_units in legion_data.items():
                        if unit_name in cie_units:
                            return Unit(unit_name, region, subdivision, legion, cie)
    return None

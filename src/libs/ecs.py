from libs.utils import safe_divide
from pydantic import BaseModel
import os
from typing import Optional

# Rs_ecs
# Abaque(tv049bis_rendement_stockage_ecs.csv)
# Keys: ['type_stockage', 'category_stockage', 'volume_stockage']
# Values: ['Cr']

# Rd_ecs
# Abaque(tv040_rendement_distribution_ecs.csv)
# Keys: ['type_installation', 'type_generateur', 'production_volume_habitable', 'pieces_alimentees_contigues']
# Values: ['rd']

# Rg_ecs
# Abaque(tv047bis_rendement_generation_ecs.csv)
# Keys: ['annee_generateur', 'puissance_nominale']
# Values: ['Rpn', 'Qp0', 'Pveilleuse']

# Rg_ecs_pac
# Abaque(tv047bis_rendement_generation_ecs_pac.csv)
# Keys: ['annee_generateur', 'zone_hiver', 'type_pac']
# Values: ['COP']


class EcsInput(BaseModel):
    identifiant: str
    type_generateur: str = (
        None  # "Electrique", "A combustion ECS seule par chaudière gaz, fioul ou chauffe-eau gaz", "A combustion Mixte chaudière gaz, fioul ou bois", "A combustion Accumulateur gaz", "A combustion Chauffe-bain au gaz à production instantannée", "Thermodynamique à accumulation avec appoint", "Thermodynamique à accumulation sans appoint", "Réseau de chaleur isolé", "Réseau de chaleur non isolé"
    )

    ## Rendement distribution
    type_generateur_distribution: Optional[str] = (
        None  # "Electrique classique", "Electrique thermodinamyque", "Autres types de chauffe-eau", "Réseau collectif non isolé", "Réseau collectif isolé", "Générateur à combustion en l'absence"
    )
    type_installation: Optional[str] = None  # "Individuelle", "Collectif"
    production_en_volume_habitable: Optional[bool] = (
        None  # True, False or None, if the generator is inside the habitable volume
    )
    pieces_alimentees_contigues: Optional[bool] = (
        None  # True, False or None, if the generator is next to the rooms where the ecs is used
    )

    ## Rendement stockage
    type_stockage: Optional[str] = None  # Chauffe-eau vertical, Chauffe-eau horizontal
    category_stockage: Optional[str] = None  # Catégorie B ou 2 étoiles, Catégorie C ou 3 étoiles, Other
    volume_ballon: Optional[float] = None  # Volume du ballon en litre

    ## Rendement_générateur
    Pnom: Optional[float] = None  # Puissance nominale du générateur en kW
    annee_generateur: Optional[int] = None  # Année de mise en service du générateur
    type_pac: Optional[str] = (
        None  # "CET sur air extérieur ou ambiant (sur local non chauffé)", "CET sur air extrait", "PAC double service
    )


class ECS:
    def __init__(self, abaques):
        self.abaques = abaques

    def forward(self, dpe, kwargs: EcsInput):
        ecs = kwargs.dict()

        ## Rendement distribution
        ecs["Rd"] = self.abaques["Rd_ecs"](
            {
                "type_installation": ecs["type_installation"],
                "type_generateur": ecs["type_generateur_distribution"],
                "production_volume_habitable": ecs["production_en_volume_habitable"],
                "pieces_alimentees_contigues": ecs["pieces_alimentees_contigues"],
            },
            "rd",
        )

        ## Rendement stockage
        if ecs["type_stockage"] is None:
            ecs["Rs"] = 1
            ecs["Qgw"] = 0
        else:
            ecs["Cr"] = self.abaques["Rs_ecs"](
                {
                    "type_stockage": ecs["type_stockage"],
                    "category_stockage": ecs["category_stockage"],
                    "volume_stockage": ecs["volume_ballon"],
                },
                "Cr",
            )
            ecs["Qgw"] = 8592 * (45 / 24) * ecs["Cr"] * ecs["volume_ballon"]
            ecs["Rs"] = safe_divide(1, 1 + (ecs["Qgw"] * ecs["Rd"] / dpe["Becs"]))

        ## Rendement générateur

        if ecs["type_generateur"] == "A combustion Chauffe-bain au gaz à production instantannée":
            ecs["type_generateur"] = "A combustion ECS seule par chaudière gaz, fioul ou chauffe-eau gaz"
        if (
            ecs["type_generateur"] == "Electrique"
            or ecs["type_generateur"] == "Electrique classique"
            or ecs["type_generateur"] == "Electrique thermodinamyque"
        ):
            ecs["Rg"] = 1
        elif ecs["type_generateur"] == "Réseau de chaleur isolé":
            ecs["Rg"] = 0.9
            ecs["Rs"] = 1
        elif ecs["type_generateur"] == "Réseau de chaleur non isolé":
            ecs["Rg"] = 0.75
            ecs["Rs"] = 1
        elif ecs["type_generateur"] == "A combustion ECS seule par chaudière gaz, fioul ou chauffe-eau gaz":
            ecs["Pnom"] = 10 if ecs["Pnom"] < 10 else 1000
            ecs["Rpn"] = self.abaques["Rg_ecs"](
                {
                    "annee_generateur": dpe["annee_generateur"],
                    "puissance_nominale": dpe["Pnom"],
                },
                "Rpn",
            )
            ecs["Qp0"] = self.abaques["Rg_ecs"](
                {
                    "annee_generateur": dpe["annee_generateur"],
                    "puissance_nominale": dpe["Pnom"],
                },
                "Qp0",
            )
            ecs["Pveilleuse"] = self.abaques["Rg_ecs"](
                {
                    "annee_generateur": dpe["annee_generateur"],
                    "puissance_nominale": dpe["Pnom"],
                },
                "Pveilleuse",
            )
            ecs["Rg"] = safe_divide(
                1,
                (1 / ecs["Rpn"]) + (1790 * ecs["Qp0"] / dpe["Becs"]) + (6970 * ecs["Pveilleuse"] / dpe["Becs"]),
            )
        elif ecs["type_generateur"] == "A combustion Mixte chaudière gaz, fioul ou bois":
            ecs["Pnom"] = 10 if ecs["Pnom"] < 10 else 1000
            ecs["Rpn"] = self.abaques["Rg_ecs"](
                {
                    "annee_generateur": dpe["annee_generateur"],
                    "puissance_nominale": dpe["Pnom"],
                },
                "Rpn",
            )
            ecs["Qp0"] = self.abaques["Rg_ecs"](
                {
                    "annee_generateur": dpe["annee_generateur"],
                    "puissance_nominale": dpe["Pnom"],
                },
                "Qp0",
            )
            ecs["Pveilleuse"] = self.abaques["Rg_ecs"](
                {
                    "annee_generateur": dpe["annee_generateur"],
                    "puissance_nominale": dpe["Pnom"],
                },
                "Pveilleuse",
            )
            ecs["Rg"] = safe_divide(
                1,
                (1 / ecs["Rpn"])
                + ((1790 * ecs["Qp0"] + ecs["Qgw"]) / dpe["Becs"])
                + (6970 * 0.5 * ecs["Pveilleuse"] / dpe["Becs"]),
            )
        elif ecs["type_generateur"] == "A combustion Accumulateur gaz":
            ecs["Qp0"] = 1.5 * ecs["Pnom"] / 100
            ecs["Rpn"] = self.abaques["Rg_ecs"](
                {
                    "annee_generateur": dpe["annee_generateur"],
                    "puissance_nominale": "Accumulateur",
                },
                "Rpn",
            )
            ecs["Pveilleuse"] = self.abaques["Rg_ecs"](
                {
                    "annee_generateur": dpe["annee_generateur"],
                    "puissance_nominale": "Accumulateur",
                },
                "Pveilleuse",
            )
            ecs["Rg"] = safe_divide(
                1,
                (1 / ecs["Rpn"])
                + ((8592 * ecs["Qp0"] + ecs["Qgw"]) / dpe["Becs"])
                + (6970 * ecs["Pveilleuse"] / dpe["Becs"]),
            )

        elif (
            ecs["type_generateur"] == "Thermodynamique à accumulation avec appoint"
            or ecs["type_generateur"] == "Thermodynamique à accumulation sans appoint"
        ):
            ecs["Rg"] = self.abaques["Rg_ecs_pac"](
                {
                    "annee_generateur": dpe["annee_generateur"],
                    "zone_hiver": dpe["zone_hiver"],
                    "type_pac": ecs["type_pac"],
                },
                "COP",
            )
            ecs["Rs"] = 1
        else:
            raise ValueError(f"Type de générateur {ecs['type_generateur']} non reconnu")

        ecs["Recs"] = ecs["Rg"] * ecs["Rs"] * ecs["Rd"]
        ecs["Iecs"] = safe_divide(1, ecs["Recs"])
        return ecs

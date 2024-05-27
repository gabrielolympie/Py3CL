from libs.utils import safe_divide
from pydantic import BaseModel
import os

# kpth
# Abaque(tv013_valeur_pont_thermique.csv)
# Keys: ['type_liaison', 'isolation_mur', 'isolation_plancher_bas', 'type_pose', 'retour_isolation', 'largeur_dormant']
# Values: ['k']


class PontThermiqueInput(BaseModel):
    """A class to represent the input for a thermal bridge.

    Attributes:
        identifiant (str): The identifier of the thermal bridge.
        longueur_pont (float): The length of the bridge.
        type_liaison (str): The type of connection. Options include 'Menuiserie / Mur', 'Plancher bas / Mur',
            'Plancher haut lourd / Mur', 'Plancher intermédiaire lourd / Mur', 'Refend / Mur', 'Menuiserie / Plancher haut'.
        isolation_mur (str): The type of wall insulation. Options include 'ITE', 'ITE+ITR', 'ITI', 'ITI+ITE',
            'ITI+ITR', 'ITR', 'Non isolé', 'MOB', 'Inconnu'.
        isolation_plancher_bas (str): The type of floor insulation. Options include 'ITE', 'ITE+ITI', 'ITI',
            'Non isolé', 'Inconnu'.
        type_pose (str): The type of pose. Options include 'Nu extérieur', 'Nu intérieur', 'Tunnel'.
        retour_isolation (str): The return of insulation. Options include 'Avec', 'Sans'.
        largeur_dormant (float): The width of the dormant.
    """

    identifiant: str
    longueur_pont: float
    type_liaison: str = (
        None  # Menuiserie / Mur, Plancher bas / Mur, Plancher haut lourd / Mur, Plancher intermédiaire lourd / Mur, Refend / Mur, Menuiserie / Plancher haut
    )
    isolation_mur: str = None  # ITE, ITE+ITR, ITI, ITI+ITE, ITI+ITR, ITR, Non isolé, MOB, Inconnu
    isolation_plancher_bas: str = None  # ITE, ITE+ITI, ITI, Non isolé, Inconnu
    type_pose: str = None  # Nu extérieur, Nu intérieur, Tunnel
    retour_isolation: str = None  # Avec, Sans
    largeur_dormant: float = None


class PontThermique:
    def __init__(self, abaques):
        self.abaques = abaques

    def forward(self, dpe, kwargs: PontThermiqueInput):
        pont_thermique = kwargs.dict()

        # Get the abaque
        # dpe['zone_climatique'] = self.abaques['department']({'id': dpe['department']}, 'zone_climatique')

        pont_thermique["k"] = self.abaques["kpth"](
            {
                "type_liaison": pont_thermique["type_liaison"],
                "isolation_mur": pont_thermique["isolation_mur"],
                "isolation_plancher_bas": pont_thermique["isolation_plancher_bas"],
                "type_pose": pont_thermique["type_pose"],
                "retour_isolation": pont_thermique["retour_isolation"],
                "largeur_dormant": pont_thermique["largeur_dormant"],
            },
        )

        pont_thermique["d_pont"] = pont_thermique["k"] * pont_thermique["longueur_pont"]
        return pont_thermique

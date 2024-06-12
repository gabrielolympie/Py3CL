from py3cl.libs.utils import safe_divide, vectorized_safe_divide
from py3cl.libs.base import BaseProcessor
from pydantic import BaseModel

import numpy as np
from typing import Optional


class ClimatisationInput(BaseModel):
    """
    Data model for input parameters for the Climatisation system.

    Attributes:
        identifiant (str): Unique identifier for the climatisation record.
        annee_installation (Optional[float]): Year of installation of the climatisation system. Default is None.
        surface_refroidie (Optional[float]): Cooled surface area in square meters. Default is None.
        type_energie (Optional[str]): Type of energy used (e.g., 'Electricité', 'Gaz', 'Fioul'). Default is None.
    """

    identifiant: str
    type_energie: Optional[str] = None  # Electricité, Gaz, Fioul...
    annee_installation: Optional[float] = None
    surface_refroidie: Optional[float] = None


class Climatisation(BaseProcessor):
    """
    Represents a climatisation system with methods to calculate various climatic metrics.

    Attributes:
        abaques (dict): Data structure containing abaque functions for energy efficiency calculations.
    """

    LIGHT_INERTIA = "Légère"
    MEDIUM_INERTIA = "Moyenne"
    HIGH_INERTIA = "Forte"

    def __init__(self, abaques):
        """
        Initializes a new Climatisation instance.

        Args:
            abaques (dict): Abaques for calculating EER and other coefficients.
        """
        super().__init__(abaques, ClimatisationInput)

    def define_categorical(self):
        """
        Define the fields that are considered categorical within the input data model.
        """
        self.categorical_fields = [
            "type_energie",  # 'Electricité', 'Gaz', 'Fioul'...
        ]

    def define_numerical(self):
        """
        Define the fields that are considered numerical within the input data model.
        """
        self.numerical_fields = [
            "annee_installation",
            "surface_refroidie",
        ]

    def define_abaques(self):
        """
        Define and map the abaque configurations to specific fields used in climatisation calculations.
        """
        self.used_abaques = {
            "seer_clim": {
                "zone_hiver": "zone_hiver",  # This might come from dpe, not ClimatisationInput
                "annee_climatisation": "annee_installation",
            },
            "emission_froid": {
                "type_energie": "type_energie",
            },
        }

    def calculate_rbth_j(self, dpe):
        """
        Calculates the Rbth_j values.

        Args:
            dpe (dict): Contains building and environmental data necessary for calculations.

        Returns:
            np.ndarray: Array of Rbth_j values.
        """
        Rbth_j_num = dpe["Ai_frj"] + dpe["Asj"] * (dpe["Ai_frj"] > 0)
        Rbth_j_den = dpe["GV"] * (dpe["Textmoy_clim_j"] - dpe["Tint_froids"]) * dpe["Nref_froids_j"]
        Rbth_j = vectorized_safe_divide(Rbth_j_num, Rbth_j_den)
        Rbth_j[Rbth_j < 0.5] = 0
        return Rbth_j

    def calculate_inertia(self, dpe, surface_habitable):
        """
        Calculates the inertia coefficient C_in.

        Args:
            dpe (dict): Contains building and environmental data necessary for calculations.
            surface_habitable (float): The habitable surface area.

        Returns:
            float: Calculated inertia coefficient.
        """
        if dpe["inertie_batiment"] == self.LIGHT_INERTIA:
            return 110000 * surface_habitable
        elif dpe["inertie_batiment"] == self.MEDIUM_INERTIA:
            return 165000 * surface_habitable
        else:
            return 260000 * surface_habitable

    def calculate_futj(self, rbth_j, c_in, dpe):
        """
        Calculates the futj values.

        Args:
            rbth_j (np.ndarray): Array of Rbth_j values.
            c_in (float): Inertia coefficient.
            dpe (dict): Contains building and environmental data necessary for calculations.

        Returns:
            np.ndarray: Array of futj values.
        """
        a = 1 + c_in / (dpe["GV"] * 3600 * 15)
        futj = np.array(
            [
                (safe_divide(a, 1 + a) if elt == 1 else safe_divide(1 - elt ** (-a), 1 - elt ** (-a - 1)))
                for elt in rbth_j
            ]
        )
        futj[rbth_j == 0] = 0
        return futj

    def forward(self, dpe, kwargs: ClimatisationInput):
        """
        Calculates and updates climatisation-related metrics based on DPE (Diagnostic de Performance Énergétique) data and input parameters.

        Args:
            dpe (dict): Contains building and environmental data necessary for calculations.
            kwargs (ClimatisationInput): Input data for the specific climatisation setup.

        Returns:
            dict: Updated climatisation parameters after calculations.
        """
        clim = kwargs.dict()

        rbth_j = self.calculate_rbth_j(dpe)
        clim["Rbth_j"] = rbth_j

        c_in = self.calculate_inertia(dpe, dpe["surface_habitable"])
        clim["C_in"] = c_in

        futj = self.calculate_futj(rbth_j, c_in, dpe)
        clim["futj"] = futj

        bfroids_term1 = (dpe["Ai_frj"] + dpe["Asj"] * (dpe["Ai_frj"] > 0)) / 1000
        bfroids_term2 = (futj * dpe["GV"] * (dpe["Tint_froids"] - dpe["Textmoy_clim_j"]) * dpe["Nref_froids_j"]) / 1000
        clim["Bfrj"] = bfroids_term1 - bfroids_term2

        clim["EER"] = self.abaques["seer_clim"](
            {
                "zone_hiver": dpe["zone_hiver"],
                "annee_climatisation": clim["annee_installation"],
            },
            "SEER",
        )

        clim["SEER"] = 0.95 * clim["EER"]

        clim["Cfr"] = 0.9 * clim["Bfrj"] / clim["SEER"]
        clim["Cfr"] = clim["Cfr"] * safe_divide(clim["surface_refroidie"], dpe["surface_habitable"])

        if "Electricité" in clim["type_energie"]:
            clim["ratio_primaire_finale"] = 2.3
            clim["coef_emission"] = 0.079
        else:
            clim["ratio_primaire_finale"] = 1
            clim["coef_emission"] = self.abaques["emission_froid"](
                {
                    "type_energie": clim["type_energie"],
                },
                "taux_conversion",
            )

        clim["Cfr_primaire"] = clim["Cfr"] * clim["ratio_primaire_finale"]
        clim["emission_fr"] = clim["Cfr"] * clim["coef_emission"]
        return clim

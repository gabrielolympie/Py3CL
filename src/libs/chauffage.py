from libs.utils import safe_divide, vectorized_safe_divide, set_community, iterative_merge
from libs.base import BaseProcessor
from pydantic import BaseModel
import os
from typing import Optional
import numpy as np

class ChauffageInput(BaseModel):
    """
    A class to represent the input parameters for a heating system configuration.

    Attributes:
        identifiant (str): Unique identifier for the heating input.
        surface_chauffee (float, optional): Heated area in square meters. Defaults to None.
        type_installation (str, optional): Type of heating installation, e.g., "Chauffage individuel", "Chauffage collectif".
        annee_installation (int, optional): Year of installation of the heating system.
        type_pac (str, optional): Type of heat pump, e.g., 'PAC Air/Eau', 'PAC Eau/Eau'.
        type_generateur (str, optional): Type of heating generator, such as "Générateur à effet joule direct".
        type_emetteur (str, optional): Type of emitter, like "Convecteur électrique NFC".
        type_distribution (str, optional): Type of distribution system used in the heating system.
        isolation_distribution (bool, optional): Indicates if the distribution system is insulated.
        type_regulation (str, optional): Type of regulation, e.g., "Régulation pièce par pièce".
        equipement_intermittence (str, optional): Type of intermittent heating equipment used.
        comptage_individuel (str, optional): Indicates if there is individual metering.
        type_regulation_intermittence (str, optional): Type of intermittent regulation.
        type_chauffage (str, optional): General type of heating, e.g., 'Central', 'Divisé'.
    """
    identifiant: str
    surface_chauffee: Optional[float] = None
    type_installation: Optional[str] = None
    annee_installation: Optional[int] = None
    type_pac: Optional[str] = None
    type_generateur: Optional[str] = None
    type_emetteur: Optional[str] = None
    type_distribution: Optional[str] = None
    isolation_distribution: Optional[bool] = None
    type_regulation: Optional[str] = None
    equipement_intermittence: Optional[str] = None
    comptage_individuel: Optional[str] = None
    type_regulation_intermittence: Optional[str] = None
    type_chauffage: Optional[str] = None


class Chauffage(BaseProcessor):
    """
    A class to handle heating system calculations based on various input parameters and predefined efficiency tables.

    Attributes:
        abaque (dict): A dictionary containing abaque configurations.
        input (Any): An input object expected to have type annotations defining its structure.
        input_scheme (dict): Extracted type annotations from the input object.
        categorical_fields (list): List of fields categorized as categorical.
        numerical_fields (list): List of fields categorized as numerical.
        used_abaques (dict): Mapping of field usage to abaque specifications.
        field_usage (dict): Tracks the usage of fields across different abaques.
    """

    def __init__(self, abaques):
        super().__init__(abaques, ChauffageInput)

    
    def define_categorical(self):
        self.categorical_fields = [
            "type_installation",
            "type_pac",
            "type_generateur",
            "type_emetteur",
            "type_distribution",
            "isolation_distribution",
            "type_regulation",
            "equipement_intermittence",
            "comptage_individuel",
            "type_regulation_intermittence",
            "type_chauffage",
        ]

    def define_numerical(self):
        self.numerical_fields = [
            "surface_chauffee",
            "annee_installation",
        ]

    def define_abaques(self):
        self.used_abaques = {
            "Rd_systeme_chauffage": {
                "type_distribution": "type_distribution",
                "isole": "isolation_distribution",
            },
            "Rr_systeme_chauffage": {
                "type_installation": "type_regulation",
            },
            "Re_systeme_chauffage": {
                "type_emetteur": "type_emetteur",
            },
            "scop_pac": {
                "type_pac": "type_pac",
                "zone_hiver": "zone_hiver",  # This comes from dpe, not ChauffageInput
                "annee_installation": "annee_installation",
                "type_emetteur": "calc_type_emetteur",  # Adjusted based on logic in the class
            },
            "Rg": {
                "type_generateur": "type_generateur",
            },
            "I0_intermittence": {
                "type_batiment": "type_batiment",  # This comes from dpe, not ChauffageInput
                "type_installation": "type_installation",
                "type_chauffage": "type_chauffage",
                "type_regulation": "type_regulation_intermittence",
                "type_emetteur": "calc_type_emetteur",  # Adjusted based on logic in the class
                "inertie": "inertie_globale",  # This comes from dpe, not ChauffageInput
                "equipement_intermittence": "equipement_intermittence",
                "comptage_individuel": "comptage_individuel",
            },
        }


    def forward(self, dpe, kwargs: ChauffageInput):
        """
        Processes the heating data using the DPE and ChauffageInput to calculate various heating characteristics.

        Args:
            dpe (dict): Dictionary containing information about the dwelling's performance evaluation (DPE).
            kwargs (ChauffageInput): Input parameters for the heating system configuration.

        Returns:
            dict: A dictionary containing calculated values such as surface percentage, various rendements (efficiencies), and intermittence metrics.
        """
        heat = kwargs.dict()

        heat["%_surface"] = self._calculate_surface_percentage(heat, dpe)
        heat["Rd"] = self._calculate_rendement_distribution(heat)
        heat["Rr"] = self._calculate_rendement_regulation(heat)
        heat["Re"] = self._calculate_rendement_emission(heat)

        type_emission_1 = self._determine_type_emission(heat)

        heat["Rg"] = self._calculate_rendement_generation(heat, dpe, type_emission_1)
        heat["G"] = self._calculate_G(dpe)
        heat["INT"] = self._calculate_intermittence(heat, dpe, type_emission_1)

        heat["Ich"] = self._calculate_ich(heat)

        return heat

    def _calculate_surface_percentage(self, heat, dpe):
        """
        Calculate the percentage of the surface that is heated.

        Args:
            heat (dict): Heating input parameters.
            dpe (dict): Dwelling's performance evaluation data.

        Returns:
            float: Percentage of the surface that is heated.
        """
        return safe_divide(heat["surface_chauffee"], dpe["surface_habitable"])

    def _calculate_rendement_distribution(self, heat):
        """
        Calculate the distribution efficiency.

        Args:
            heat (dict): Heating input parameters.

        Returns:
            float: Distribution efficiency.
        """
        return self.abaques["Rd_systeme_chauffage"](
            {
                "type_distribution": heat["type_distribution"],
                "isole": heat["isolation_distribution"],
            },
            "rd",
        )

    def _calculate_rendement_regulation(self, heat):
        """
        Calculate the regulation efficiency.

        Args:
            heat (dict): Heating input parameters.

        Returns:
            float: Regulation efficiency.
        """
        return self.abaques["Rr_systeme_chauffage"](
            {
                "type_installation": heat["type_regulation"],
            },
            "rr",
        )

    def _calculate_rendement_emission(self, heat):
        """
        Calculate the emission efficiency.

        Args:
            heat (dict): Heating input parameters.

        Returns:
            float: Emission efficiency.
        """
        return self.abaques["Re_systeme_chauffage"](
            {
                "type_emetteur": heat["type_emetteur"],
            },
            "re",
        )

    def _determine_type_emission(self, heat):
        """
        Determine the type of emission system based on the emitter type.

        Args:
            heat (dict): Heating input parameters.

        Returns:
            str: Type of emission system.
        """
        if heat["type_emetteur"] is not None:
            if "NFC" in heat["type_emetteur"].lower():
                return "Radiateurs"
            elif "soufflage" in heat["type_emetteur"].lower():
                return "Air soufflé"
            elif "plancher" in heat["type_emetteur"].lower():
                return "Planchers chauffant"
            elif "plafond" in heat["type_emetteur"].lower():
                return "Planchers chauffant"
            else:
                return "Autres systèmes"
        return None

    def _calculate_rendement_generation(self, heat, dpe, type_emission_1):
        """
        Calculate the generation efficiency.

        Args:
            heat (dict): Heating input parameters.
            dpe (dict): Dwelling's performance evaluation data.
            type_emission_1 (str): Type of emission system.

        Returns:
            float: Generation efficiency.
        """
        if "pac" in heat["identifiant"].lower():
            if type_emission_1 == "Planchers chauffant":
                return self.abaques["scop_pac"](
                    {
                        "type_pac": heat["type_pac"],
                        "zone_hiver": dpe["zone_hiver"],
                        "annee_installation": heat["annee_installation"],
                        "type_emetteur": "Planchers/Plafonds",
                    },
                    "SCOP",
                )
            else:
                return self.abaques["scop_pac"](
                    {
                        "type_pac": heat["type_pac"],
                        "zone_hiver": dpe["zone_hiver"],
                        "annee_installation": heat["annee_installation"],
                        "type_emetteur": "Autres",
                    },
                    "SCOP",
                )
        else:
            return self.abaques["Rg"](
                {
                    "type_generateur": heat["type_generateur"],
                },
                "rg",
            )

    def _calculate_G(self, dpe):
        """
        Calculate the G coefficient.

        Args:
            dpe (dict): Dwelling's performance evaluation data.

        Returns:
            float: G coefficient.
        """
        return safe_divide(dpe["GV"], (dpe["surface_habitable"] * dpe["hauteur_sous_plafond"]))

    def _calculate_intermittence(self, heat, dpe, type_emission_1):
        """
        Calculate the intermittence coefficient.

        Args:
            heat (dict): Heating input parameters.
            dpe (dict): Dwelling's performance evaluation data.
            type_emission_1 (str): Type of emission system.

        Returns:
            float: Intermittence coefficient.
        """
        return self.abaques["I0_intermittence"](
            {
                "type_batiment": dpe["type_batiment"],
                "type_installation": heat["type_installation"],
                "type_chauffage": heat["type_chauffage"],
                "type_regulation": heat["type_regulation_intermittence"],
                "type_emetteur": type_emission_1,
                "inertie": dpe["inertie_globale"],
                "equipement_intermittence": heat["equipement_intermittence"],
                "comptage_individuel": heat["comptage_individuel"],
            },
            "I0",
        )

    def _calculate_ich(self, heat):
        """
        Calculate the Ich coefficient.

        Args:
            heat (dict): Heating input parameters.

        Returns:
            float: Ich coefficient.
        """
        return safe_divide(1, heat["Rd"] * heat["Rr"] * heat["Re"] * heat["Rg"])

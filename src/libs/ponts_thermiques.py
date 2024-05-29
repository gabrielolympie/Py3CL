from libs.utils import safe_divide
from pydantic import BaseModel, Field
import os
from typing import Optional, Dict, Any
import logging

# kpth
# Abaque(tv013_valeur_pont_thermique.csv)
# Keys: ['type_liaison', 'isolation_mur', 'isolation_plancher_bas', 'type_pose', 'retour_isolation', 'largeur_dormant']
# Values: ['k']
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PontThermiqueInput(BaseModel):
    """Represents the input for a thermal bridge calculation.

    Attributes:
        identifiant (str): Identifier of the thermal bridge.
        longueur_pont (float): Length of the bridge in meters.
        type_liaison (str): Type of connection between structural elements. Options include various interfaces such as 'Menuiserie / Mur' (joinery to wall), etc.
        isolation_mur (str): Type of wall insulation. Options include 'ITE' (External Thermal Insulation), 'ITI' (Internal Thermal Insulation), etc.
        isolation_plancher_bas (str): Type of lower floor insulation, similar options as wall insulation.
        type_pose (str): Installation type of the window frame or similar structure, options are 'Nu extérieur' (external bare), 'Nu intérieur' (internal bare), and 'Tunnel'.
        retour_isolation (str): Specifies if there is a return on the insulation, options are 'Avec' (with) and 'Sans' (without).
        largeur_dormant (float): Width of the frame in meters.
    """

    identifiant: str
    longueur_pont: float = Field(..., gt=0, description="Length of the bridge in meters.")
    type_liaison: Optional[str] = Field(None, description="Type of connection between structural elements.")
    isolation_mur: Optional[str] = Field(None, description="Type of wall insulation.")
    isolation_plancher_bas: Optional[str] = Field(None, description="Type of lower floor insulation.")
    type_pose: Optional[str] = Field(None, description="Installation type of the window frame or similar structure.")
    retour_isolation: Optional[str] = Field(None, description="Specifies if there is a return on the insulation.")
    largeur_dormant: Optional[float] = Field(None, gt=0, description="Width of the frame in meters.")


class PontThermique:
    """Manages the calculations for thermal bridges using input parameters and abaque tables.

    Attributes:
        abaques (dict): A dictionary of abaque tables used for looking up thermal bridge coefficients.
    """

    def __init__(self, abaques: Dict[str, Any]):
        """Initialize the PontThermique with abaque tables.

        Args:
            abaques (dict): A dictionary containing abaque tables needed for the calculations.
        """
        self.abaques = abaques

    def lookup_k_value(self, pont_thermique: Dict[str, Any]) -> float:
        """Look up the k value from the abaque tables based on the input parameters.

        Args:
            pont_thermique (dict): Dictionary of input parameters for the thermal bridge calculation.

        Returns:
            float: The k value from the abaque tables.

        Raises:
            KeyError: If required keys are missing in the abaque lookup.
            ValueError: If the k value is not found.
        """
        try:
            k_value = self.abaques["kpth"](
                {
                    "type_liaison": pont_thermique["type_liaison"],
                    "isolation_mur": pont_thermique["isolation_mur"],
                    "isolation_plancher_bas": pont_thermique["isolation_plancher_bas"],
                    "type_pose": pont_thermique["type_pose"],
                    "retour_isolation": pont_thermique["retour_isolation"],
                    "largeur_dormant": pont_thermique["largeur_dormant"],
                },
            )
            if k_value is None:
                raise ValueError("K value not found in abaque.")
            return k_value
        except KeyError as e:
            logger.error(f"Key error during k value lookup: {e}")
            raise
        except ValueError as e:
            logger.error(e)
            raise

    def forward(self, dpe: Dict[str, Any], kwargs: PontThermiqueInput) -> Dict[str, Any]:
        """Calculates the thermal bridge based on input parameters and climatic zone.

        Args:
            dpe (dict): Dictionary containing DPE (Diagnostic de Performance Énergétique) information including department and climatic zone.
            kwargs (PontThermiqueInput): Input parameters for the thermal bridge calculation.

        Returns:
            dict: Updated dictionary of pont_thermique with calculated thermal bridge values.
        """
        pont_thermique = kwargs.dict()

        # Retrieve and log the climatic zone if needed
        # zone_climatique = self.abaques['department'].get(dpe['department'], {}).get('zone_climatique')
        # logger.info(f"Climatic zone for department {dpe['department']}: {zone_climatique}")

        try:
            pont_thermique["k"] = self.lookup_k_value(pont_thermique)
        except Exception as e:
            logger.error(f"Failed to calculate k value: {e}")
            pont_thermique["k"] = None

        pont_thermique["d_pont"] = safe_divide(
            pont_thermique["k"] * pont_thermique["longueur_pont"], 1
        )  # Use safe_divide to handle any potential division issues
        return pont_thermique

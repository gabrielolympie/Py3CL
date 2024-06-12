from py3cl.libs.utils import safe_divide
from py3cl.libs.base import BaseProcessor
from pydantic import BaseModel
import os
from typing import Optional, Dict, Any, Union

generator_types = [
    "A combustion Chauffe-bain au gaz à production instantannée",
    "Electrique",
    "Electrique classique",
    "Electrique thermodinamyque",
    "Réseau de chaleur isolé",
    "Réseau de chaleur non isolé",
    "A combustion ECS seule par chaudière gaz, fioul ou chauffe-eau gaz",
    "A combustion Mixte chaudière gaz, fioul ou bois",
    "A combustion Accumulateur gaz",
    "Thermodynamique à accumulation avec appoint",
    "Thermodynamique à accumulation sans appoint",
]


class EcsInput(BaseModel):
    """
    Data model for the input parameters needed to calculate the efficiency of a hot water system.

    Args:
        identifiant (str): Unique identifier for the hot water system.
        type_energie (str, optional): Type of energy used by the hot water system, like electric, gas, etc.
        type_generateur (str, optional): Type of the hot water generation system, with various options like electric, combustion, etc.
        type_generateur_distribution (str, optional): Distribution type for the hot water system, which includes electric and other types.
        type_installation (str, optional): Installation type, whether individual or collective.
        production_en_volume_habitable (bool, optional): Specifies if the generator is within the habitable volume.
        pieces_alimentees_contigues (bool, optional): Specifies if the generator is adjacent to the rooms where hot water is used.
        type_stockage (str, optional): Storage type of the water heater, either vertical or horizontal.
        category_stockage (str, optional): Efficiency category of the storage system.
        volume_ballon (float, optional): Volume of the storage tank in liters.
        Pnom (float, optional): Nominal power of the generator in kW.
        annee_generateur (int, optional): Year the generator was put into service.
        type_pac (str, optional): Type of heat pump used, if any.
    """

    identifiant: str
    type_energie: Optional[str] = None
    type_generateur: Optional[str] = None
    type_generateur_distribution: Optional[str] = None
    type_installation: Optional[str] = None
    production_en_volume_habitable: Optional[bool] = None
    pieces_alimentees_contigues: Optional[bool] = None
    type_stockage: Optional[str] = None
    category_stockage: Optional[str] = None
    volume_ballon: Optional[float] = None
    Pnom: Optional[Union[float, None]] = None
    # is_accumulateur: Optional[bool] = None
    annee_generateur: Optional[int] = None
    type_pac: Optional[str] = None


class ECS(BaseProcessor):
    """
    Class to compute various efficiency metrics for a hot water system based on provided parameters and lookup tables (abaques).

    Attributes:
        abaque (dict): A dictionary containing abaque configurations.
        input (Any): An input object expected to have type annotations defining its structure.
        input_scheme (dict): Extracted type annotations from the input object.
        categorical_fields (list): List of fields categorized as categorical.
        numerical_fields (list): List of fields categorized as numerical.
        used_abaques (dict): Mapping of field usage to abaque specifications.
        field_usage (dict): Tracks the usage of fields across different abaques.
    """

    DEFAULT_POWER_LIMIT_LOW = 10
    DEFAULT_POWER_LIMIT_HIGH = 1000

    def __init__(self, abaques: Dict[str, Any]):
        """
        Initialize the ECS object with necessary lookup tables.

        Args:
            abaques (dict): Dictionary containing the lookup tables for efficiency calculations.
        """
        self.characteristics_corrections = {
            "type_generateur": generator_types,
            "pieces_alimentees_contigues": [True, False],
        }

        super().__init__(
            abaques,
            EcsInput,
            characteristics_corrections=self.characteristics_corrections,
        )

    def define_categorical(self):
        """
        Defines the list of input fields that are categorized as categorical for processing ECS efficiency.
        """
        self.categorical_fields = [
            "type_energie",
            "type_generateur",
            "type_generateur_distribution",
            "type_installation",
            "production_en_volume_habitable",
            "type_stockage",
            "category_stockage",
            "type_pac",
            "Pnom",
        ]

    def define_numerical(self):
        """
        Defines the list of input fields that are categorized as numerical for computing efficiencies in the ECS system.
        """
        self.numerical_fields = [
            "volume_ballon",
            "annee_generateur",
        ]

    def define_abaques(self):
        """
        Sets up the mapping of field usage to abaque configurations necessary for ECS efficiency calculations.
        """
        self.used_abaques = {
            "Rd_ecs": {
                "type_installation": "type_installation",
                "type_generateur": "type_generateur_distribution",
                "production_volume_habitable": "production_en_volume_habitable",
                "pieces_alimentees_contigues": "pieces_alimentees_contigues",
            },
            "Rs_ecs": {
                "type_stockage": "type_stockage",
                "category_stockage": "category_stockage",
                "volume_stockage": "volume_ballon",
            },
            "Rg_ecs": {
                # "type_generateur": "type_generateur",
                "annee_generateur": "annee_generateur",
                "puissance_nominale": "Pnom",
            },
            "Rg_ecs_pac": {
                "annee_generateur": "annee_generateur",
                "zone_hiver": "zone_hiver",  # From DPE data
                "type_pac": "type_pac",
            },
            "emission_ecs": {
                "type_energie": "type_energie",
            },
        }

    def forward(self, dpe: Dict[str, Any], kwargs: EcsInput) -> Dict[str, Any]:
        """
        Compute the efficiency of the hot water system using the provided DPE data and user inputs.

        Args:
            dpe (dict): Dictionary containing DPE related data such as annual energy consumption.
            kwargs (EcsInput): User input data model containing parameters of the hot water system.

        Returns:
            dict: A dictionary containing calculated efficiency metrics like Rg (generator efficiency),
                  Rs (storage efficiency), and Rd (distribution efficiency).
        """
        # Create a copy of the input dictionary to avoid mutating the original input
        ecs = kwargs.dict().copy()

        # Calculate efficiency metrics
        ecs["Rd"] = self.calculate_distribution_efficiency(ecs)
        ecs["Rs"], ecs["Qgw"] = self.calculate_storage_efficiency(ecs, dpe)
        ecs["Rg"] = self.calculate_generator_efficiency(ecs, dpe)

        ecs["Recs"] = ecs["Rg"] * ecs["Rs"] * ecs["Rd"]
        ecs["Iecs"] = safe_divide(1, ecs["Recs"])

        if "Electricité" in ecs["type_energie"]:
            ecs["ratio_primaire_finale"] = 2.3
            ecs["coef_emission"] = 0.079
        else:
            ecs["ratio_primaire_finale"] = 1
            ecs["coef_emission"] = self.abaques["emission_ecs"](
                {
                    "type_energie": ecs["type_energie"],
                },
                "taux_conversion",
            )

        ecs["Cecs"] = dpe["Becs"] * ecs["Iecs"] * (1 - dpe["fecs"]) / 1000
        ecs["Cecs_primaire"] = ecs["Cecs"] * ecs["ratio_primaire_finale"]
        ecs["emission_ecs"] = ecs["Cecs"] * ecs["coef_emission"]
        return ecs

    def calculate_distribution_efficiency(self, ecs: Dict[str, Any]) -> float:
        """
        Calculate the distribution efficiency (Rd) for the ECS system.

        Args:
            ecs (dict): Dictionary containing the ECS input parameters.

        Returns:
            float: The distribution efficiency (Rd).
        """
        return self.abaques["Rd_ecs"](
            {
                "type_installation": ecs["type_installation"],
                "type_generateur": ecs["type_generateur_distribution"],
                "production_volume_habitable": ecs["production_en_volume_habitable"],
                "pieces_alimentees_contigues": ecs["pieces_alimentees_contigues"],
            },
            "rd",
        )

    def calculate_storage_efficiency(self, ecs: Dict[str, Any], dpe: Dict[str, Any]) -> (float, float):
        """
        Calculate the storage efficiency (Rs) and storage heat loss (Qgw).

        Args:
            ecs (dict): Dictionary containing the ECS input parameters.
            dpe (dict): Dictionary containing DPE related data such as annual energy consumption.

        Returns:
            tuple: A tuple containing the storage efficiency (Rs) and storage heat loss (Qgw).
        """
        if ecs["type_stockage"] is None:
            return 1, 0

        Cr = self.abaques["Rs_ecs"](
            {
                "type_stockage": ecs["type_stockage"],
                "category_stockage": ecs["category_stockage"],
                "volume_stockage": ecs["volume_ballon"],
            },
            "Cr",
        )
        Qgw = 8592 * (45 / 24) * Cr * ecs["volume_ballon"]
        Rs = safe_divide(1, 1 + (Qgw * ecs["Rd"] / dpe["Becs"]))

        return Rs, Qgw

    def calculate_generator_efficiency(self, ecs: Dict[str, Any], dpe: Dict[str, Any]) -> float:
        """
        Calculate the generator efficiency (Rg) for the ECS system.

        Args:
            ecs (dict): Dictionary containing the ECS input parameters.
            dpe (dict): Dictionary containing DPE related data such as annual energy consumption.

        Returns:
            float: The generator efficiency (Rg).
        """
        type_generateur = ecs["type_generateur"]

        if type_generateur == "A combustion Chauffe-bain au gaz à production instantannée":
            type_generateur = "A combustion ECS seule par chaudière gaz, fioul ou chauffe-eau gaz"

        if type_generateur in [
            "Electrique",
            "Electrique classique",
            "Electrique thermodinamyque",
        ]:
            return 1

        if type_generateur == "Réseau de chaleur isolé":
            ecs["Rs"] = 1
            return 0.9

        if type_generateur == "Réseau de chaleur non isolé":
            ecs["Rs"] = 1
            return 0.75

        if type_generateur in [
            "A combustion ECS seule par chaudière gaz, fioul ou chauffe-eau gaz",
            "A combustion Mixte chaudière gaz, fioul ou bois",
        ]:
            return self._calculate_combustion_generator_efficiency(ecs, dpe, type_generateur)

        if type_generateur == "A combustion Accumulateur gaz":
            Qp0 = 1.5 * ecs["Pnom"] / 100
            Rpn = self.abaques["Rg_ecs"](
                {
                    "annee_generateur": ecs["annee_generateur"],
                    "puissance_nominale": "Accumulateur",
                },
                "Rpn",
            )
            Pveilleuse = self.abaques["Rg_ecs"](
                {
                    "annee_generateur": ecs["annee_generateur"],
                    "puissance_nominale": "Accumulateur",
                },
                "Pveilleuse",
            )
            return safe_divide(
                1,
                (1 / Rpn) + ((8592 * Qp0 + ecs["Qgw"]) / dpe["Becs"]) + (6970 * Pveilleuse / dpe["Becs"]),
            )

        if type_generateur in [
            "Thermodynamique à accumulation avec appoint",
            "Thermodynamique à accumulation sans appoint",
        ]:
            ecs["Rs"] = 1
            return self.abaques["Rg_ecs_pac"](
                {
                    "annee_generateur": ecs["annee_generateur"],
                    "zone_hiver": dpe["zone_hiver"],
                    "type_pac": ecs["type_pac"],
                },
                "COP",
            )

        raise ValueError(f"Type de générateur {type_generateur} non reconnu")

    def _calculate_combustion_generator_efficiency(
        self, ecs: Dict[str, Any], dpe: Dict[str, Any], type_generateur: str
    ) -> float:
        """
        Calculate the efficiency for combustion generators.

        Args:
            ecs (dict): Dictionary containing the ECS input parameters.
            dpe (dict): Dictionary containing DPE related data such as annual energy consumption.
            type_generateur (str): Type of combustion generator.

        Returns:
            float: The generator efficiency (Rg).
        """
        ecs["Pnom"] = (
            self.DEFAULT_POWER_LIMIT_LOW
            if ecs["Pnom"] < self.DEFAULT_POWER_LIMIT_LOW
            else self.DEFAULT_POWER_LIMIT_HIGH
        )
        Rpn = self.abaques["Rg_ecs"](
            {
                "annee_generateur": ecs["annee_generateur"],
                "puissance_nominale": ecs["Pnom"],
            },
            "Rpn",
        )
        Qp0 = self.abaques["Rg_ecs"](
            {
                "annee_generateur": ecs["annee_generateur"],
                "puissance_nominale": ecs["Pnom"],
            },
            "Qp0",
        )
        Pveilleuse = self.abaques["Rg_ecs"](
            {
                "annee_generateur": ecs["annee_generateur"],
                "puissance_nominale": ecs["Pnom"],
            },
            "Pveilleuse",
        )

        if type_generateur == "A combustion ECS seule par chaudière gaz, fioul ou chauffe-eau gaz":
            return safe_divide(
                1,
                (1 / Rpn) + (1790 * Qp0 / dpe["Becs"]) + (6970 * Pveilleuse / dpe["Becs"]),
            )

        return safe_divide(
            1,
            (1 / Rpn) + ((1790 * Qp0 + ecs["Qgw"]) / dpe["Becs"]) + (6970 * 0.5 * Pveilleuse / dpe["Becs"]),
        )

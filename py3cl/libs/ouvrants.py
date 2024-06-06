from py3cl.libs.utils import safe_divide
from py3cl.libs.base import BaseProcessor
from pydantic import BaseModel
import os
import numpy as np
from typing import Optional, Dict, List, Tuple, Any

# Constants for fixed strings
ORIENTATION_HORIZONTAL = "Horizontal"
ORIENTATION_VERTICAL = "Verticale"
VALID_SUB_TYPE_FENETRES = [
    "Portes-fenêtres coulissantes",
    "Fenêtres battantes",
    "Portes-fenêtres battantes",
    "Fenêtres coulissantes",
    "Fenêtres battante ou coulissantes",
    "Portes-fenêtres battantes ou coulissantes sans soubassement",
    "Portes-fenêtres battantes avec soubassement",
    "Portes-fenêtres battantes sans soubassement",
]


class VitrageInput(BaseModel):
    """
    This class is used to store the input parameters for a window or glazing system.

    Args:
        identifiant (str): The unique identifier for the window.
        surface_vitrage (float): The surface area of the window (m²).
        hauteur_vitrage (float): The height of the window (m).
        largeur_vitrage (float): The width of the window (m).
        type_vitrage (str): The type of glazing (e.g., single, double, triple). Must be one of the valid glazing types defined in the dataset.
        orientation (str, optional): The orientation of the wall. Must be one of the valid orientations defined in the dataset. Defaults to None.
        inclinaison (str, optional): The inclination of the wall. Must be one of the valid inclinations defined in the dataset. Defaults to None.
        remplissage (str, optional): The type of filling material in the glazing (e.g., air, argon). Defaults to None.
        traitement_vitrage (str, optional): The type of treatment applied to the glazing (e.g., low-e coating). Defaults to None.
        epaisseur_lame (float, optional): The thickness of the glazing layer (mm). Defaults to None.
        type_pose (str, optional): The type of installation (e.g., interior or exterior). Must be one of the valid installation types defined in the dataset. Defaults to None.
        type_materiaux (str, optional): The material of the window frame (e.g., PVC, aluminium, wood). Defaults to None.
        type_menuiserie (str, optional): The type of window (e.g., casement, awning, fixed). Defaults to None.
        type_baie (str, optional): The overall type of window system (e.g., window, door-window, french window). Defaults to None.
        fermetures (str, optional): The type of closure device for the window (e.g., shutters, blinds). Defaults to None.
        masque_proche_type_masque (str, optional): The type of nearby shading element (e.g., awning, overhang). Defaults to None.
        masque_proche_avance (str, optional): The distance between the window and the nearby shading element (meters). Defaults to None.
        masque_proche_orientation (str, optional): The orientation of the nearby shading element. Defaults to None.
        masque_proche_rapport_l1_l2 (str, optional): The ratio of the width to the height of the nearby shading element. Defaults to None.
        masque_proche_beta_gama (str, optional): The beta-gamma angle of the nearby shading element. Defaults to None.
        masque_proche_angle_superieur_30 (str, optional): The angle of the nearby shading element relative to the horizontal plane (degrees). Defaults to None.
        masque_lointain_hauteur_alpha (str, optional): The height-alpha angle of the distant shading element (degrees). Defaults to None.
        masque_lointain_orientation (str, optional): The orientation of the distant shading element. Defaults to None.
        ombrage_lointain_hauteur (str, optional): The height of the distant obstacle (degrees). Defaults to None.
        ombrage_lointain_orientation (str, optional): The orientation of the distant obstacle. Defaults to None.
        ombrage_lointain_secteur (str, optional): The sector of the distant obstacle. Defaults to None.
    """

    identifiant: str
    surface_vitrage: float
    hauteur_vitrage: float
    largeur_vitrage: float
    type_vitrage: str
    orientation: Optional[str] = None
    inclinaison: Optional[str] = None
    remplissage: Optional[str] = None
    traitement_vitrage: Optional[str] = None
    epaisseur_lame: Optional[float] = None
    type_pose: Optional[str] = None
    type_materiaux: Optional[str] = None
    type_menuiserie: Optional[str] = None
    type_baie: Optional[str] = None
    fermetures: Optional[str] = None
    masque_proche_type_masque: Optional[str] = None
    masque_proche_avance: Optional[str] = None
    masque_proche_orientation: Optional[str] = None
    masque_proche_rapport_l1_l2: Optional[str] = None
    masque_proche_beta_gama: Optional[str] = None
    masque_proche_angle_superieur_30: Optional[str] = None
    masque_lointain_hauteur_alpha: Optional[str] = None
    masque_lointain_orientation: Optional[str] = None
    ombrage_lointain_hauteur: Optional[str] = None
    ombrage_lointain_orientation: Optional[str] = None
    ombrage_lointain_secteur: Optional[str] = None
    exterior_type_or_local_non_chauffe: Optional[str] = None
    surface_paroi_contact: Optional[float] = None
    surface_paroi_local_non_chauffe: Optional[float] = None
    local_non_chauffe_isole: Optional[bool] = None


class Vitrage(BaseProcessor):
    """
    A class that encapsulates the logic to process vitrage data using provided input parameters and external datasets.

    Attributes:
        abaque (dict): A dictionary containing abaque configurations.
        input (Any): An input object expected to have type annotations defining its structure.
        input_scheme (dict): Extracted type annotations from the input object.
        categorical_fields (list): List of fields categorized as categorical.
        numerical_fields (list): List of fields categorized as numerical.
        used_abaques (dict): Mapping of field usage to abaque specifications.
        field_usage (dict): Tracks the usage of fields across different abaques.

    Methods:
        forward(dpe: dict, kwargs: VitrageInput) -> dict:
            Calculates the thermal properties of a glazing system based on the input parameters and given performance datasets.
    """

    def __init__(self, abaques: Dict[str, Any]) -> None:
        """
        Initializes the Vitrage object with the given datasets.

        Args:
            abaques (dict): A dictionary containing the datasets used for calculation.
        """
        super().__init__(abaques, VitrageInput)
        self.months = [
            "Janvier",
            "Février",
            "Mars",
            "Avril",
            "Mai",
            "Juin",
            "Juillet",
            "Août",
            "Septembre",
            "Octobre",
            "Novembre",
            "Décembre",
        ]

        self.valid_sub_type_fenetres = [
            "Portes-fenêtres coulissantes",
            "Fenêtres battantes",
            "Portes-fenêtres battantes",
            "Fenêtres coulissantes",
            "Fenêtres battante ou coulissantes",
            "Portes-fenêtres battantes  ou coulissantes sans soubassement",
            "Portes-fenêtres battantes  avec soubassement",
            "Portes-fenêtres battantes  sans soubassement",
        ]

    def define_categorical(self):
        self.categorical_fields = [
            "type_vitrage",
            "orientation",
            "inclinaison",
            "remplissage",
            "traitement_vitrage",
            "type_pose",
            "type_materiaux",
            "type_menuiserie",
            "type_baie",
            "fermetures",
            "masque_proche_type_masque",
            "masque_proche_orientation",
            "masque_lointain_orientation",
            "ombrage_lointain_orientation",
            "ombrage_lointain_secteur",
            "exterior_type_or_local_non_chauffe",
            "masque_proche_avance",
            "masque_proche_rapport_l1_l2",
            "masque_proche_beta_gama",
            "masque_proche_angle_superieur_30",
            "masque_lointain_hauteur_alpha",
            "ombrage_lointain_hauteur",
        ]

    def define_numerical(self):
        self.numerical_fields = [
            "surface_vitrage",
            "hauteur_vitrage",
            "largeur_vitrage",
            "epaisseur_lame",            
            "surface_paroi_contact",
            "surface_paroi_local_non_chauffe"
        ]

    def define_abaques(self):
        self.used_abaques = {
            "coef_reduction_deperdition_exterieur": {
                "aiu_aue": "exterior_type_or_local_non_chauffe",
            },
            "coef_reduction_veranda": {
                "zone_hiver": "zone_hiver",
                "orientation_veranda": "orientation",
                "isolation_paroi": "local_non_chauffe_isole"
            },
            "coef_reduction_deperdition_local": {
                "aiu_aue_max": "aiu_aue",
                "aue_isole": "local_non_chauffe_isole",
                "aiu_isole": "isolation",
                "uv_ue": "uvue"
            },
            "ug_vitrage": {
                "type_vitrage": "type_vitrage",
                "orientation": "orientation",
                "remplissage": "remplissage",
                "traitement_vitrage": "traitement_vitrage",
                "epaisseur_lame": "epaisseur_lame"
            },
            "uw_vitrage": {
                "type_materiaux": "type_materiaux",
                "type_menuiserie": "type_menuiserie",
                "type_baie": "type_baie",
                "ug": "Ug"
            },
            "resistance_additionnelle_vitrage": {
                "fermetures": "fermetures"
            },
            "transmission_thermique_baie": {
                "uw": "Uw",
                "deltar": "DeltaR"
            },
            "facteur_solaire": {
                "type_pose": "type_pose",
                "materiaux": "type_materiaux",
                "type_baie": "type_baie",
                "type_vitrage": "calc_type_vitrage_fs"
            },
            "coefficient_orientation": {
                "zone_climatique": "zone_climatique",
                "month": "month",
                "orientation": "orientation",
                "inclination": "inclinaison"
            },
            "coef_masques_proches": {
                "type_masque": "masque_proche_type_masque",
                "avance": "masque_proche_avance",
                "orientation": "masque_proche_orientation",
                "rapport_l1_l2": "masque_proche_rapport_l1_l2",
                "beta_gama": "masque_proche_beta_gama",
                "angle_superieur_30": "masque_proche_angle_superieur_30"
            },
            "coef_masques_lointain_homogene": {
                "hauteur_alpha": "masque_lointain_hauteur_alpha",
                "orientation": "masque_lointain_orientation"
            },
            "coef_ombrage_lointain": {
                "hauteur": "ombrage_lointain_hauteur",
                "orientation": "ombrage_lointain_orientation",
                "secteur": "ombrage_lointain_secteur"
            }
        }


    def forward(self, dpe: Dict[str, Any], kwargs: VitrageInput) -> Dict[str, Any]:
        """
        Processes the vitrage input data to calculate various thermal properties such as U-values and solar factors,
        integrating with given abaque datasets that provide necessary coefficients and values for computations.

        Args:
            dpe (dict): Dictionary containing building-specific energy performance data.
                        Keys should include 'zone_climatique' and 'zone_hiver', which are used for regional thermal property calculations.
            kwargs (VitrageInput): Object containing detailed specifications of a glazing unit, including dimensions,
                                materials, and environmental context.

        Returns:
            dict: A dictionary containing updated input data with additional calculated thermal properties such as 'Ug', 'Uw', and solar gain factors.

        Raises:
            KeyError: If required keys in the 'dpe' dictionary are missing.
            ValueError: If any input values in 'kwargs' are outside of expected ranges or incompatible with the dataset constraints.
        """
        vitrage = kwargs.dict()
        vitrage["zone_climatique"] = dpe["zone_climatique"]
        vitrage["zone_hiver"] = dpe["zone_hiver"]

        vitrage["b"] = self.calculate_b(vitrage, dpe)
        vitrage["Ug"] = self.calculate_ug(vitrage)
        vitrage["Uw"] = self.calculate_uw(vitrage)
        vitrage["U"] = self.calculate_u(vitrage)

        if vitrage["type_baie"] != "Portes":
            vitrage["facteur_solaire"] = self.calculate_facteur_solaire(vitrage)
            vitrage["c1j"] = self.calculate_c1j(vitrage)
            vitrage["Fe"], vitrage["Fe1"], vitrage["Fe2"] = self.calculate_fe(vitrage)
            vitrage["ssej"] = self.calculate_ssej(vitrage)

        return vitrage

    def calculate_b(self, vitrage: Dict[str, Any], dpe: Dict[str, Any]) -> float:
        """
        Calculates the coefficient of reduction of loss (b) for the vitrage.

        Args:
            vitrage (dict): Dictionary containing vitrage-specific data.
            dpe (dict): Dictionary containing building-specific energy performance data.

        Returns:
            float: The coefficient of reduction of loss (b).
        """
        exterior_type = vitrage["exterior_type_or_local_non_chauffe"]
        if exterior_type in self.abaques["coef_reduction_deperdition_exterieur"].key_characteristics["aiu_aue"]:
            return self.abaques["coef_reduction_deperdition_exterieur"]({"aiu_aue": exterior_type}, "valeur")
        elif exterior_type == "Véranda":
            return self.abaques["coef_reduction_veranda"](
                {
                    "zone_hiver": vitrage["zone_hiver"],
                    "orientation_veranda": vitrage["orientation"],
                    "isolation_paroi": vitrage["isolation"],
                },
                "bver",
            )
        else:
            vitrage["aiu_aue"] = safe_divide(
                vitrage["surface_paroi_contact"], vitrage["surface_paroi_local_non_chauffe"]
            )
            vitrage["uvue"] = self.abaques["local_non_chauffe"](
                {"type_batiment": dpe["type_batiment"], "local_non_chauffe": exterior_type}, "uvue"
            )
            return self.abaques["coef_reduction_deperdition_local"](
                {
                    "aiu_aue_max": vitrage["aiu_aue"],
                    "aue_isole": vitrage["isolation"],
                    "aiu_isole": vitrage["local_non_chauffe_isole"],
                    "uv_ue": vitrage["uvue"],
                },
                "valeur",
            )

    def calculate_ug(self, vitrage: Dict[str, Any]) -> float:
        """
        Calculates the U-value (Ug) for the vitrage based on its type and characteristics.

        Args:
            vitrage (dict): Dictionary containing vitrage-specific data.

        Returns:
            float: The U-value (Ug) of the vitrage.
        """
        if vitrage["type_vitrage"] == "Simple Vitrage":
            return 5.8
        orientation = "Horizontale" if vitrage["orientation"] == "Horizontal" else "Verticale"
        return self.abaques["ug_vitrage"](
            {
                "type_vitrage": vitrage["type_vitrage"],
                "orientation": orientation,
                "remplissage": vitrage["remplissage"],
                "traitement_vitrage": vitrage["traitement_vitrage"],
                "epaisseur_lame": vitrage["epaisseur_lame"],
            },
            "ug",
        )

    def calculate_uw(self, vitrage: Dict[str, Any]) -> float:
        """
        Calculates the U-value (Uw) for the vitrage based on its type and characteristics.

        Args:
            vitrage (dict): Dictionary containing vitrage-specific data.

        Returns:
            float: The U-value (Uw) of the vitrage.
        """
        type_baie = (
            "Fenêtres / Porte-fenêtres"
            if vitrage["type_baie"] in self.valid_sub_type_fenetres
            else vitrage["type_baie"]
        )
        return self.abaques["uw_vitrage"](
            {
                "type_materiaux": vitrage["type_materiaux"],
                "type_menuiserie": vitrage["type_menuiserie"],
                "type_baie": type_baie,
                "ug": vitrage["Ug"],
            },
            "uw",
        )

    def calculate_u(self, vitrage: Dict[str, Any]) -> float:
        """
        Calculates the overall U-value (U) for the vitrage, taking into account additional resistance if there are closures.

        Args:
            vitrage (dict): Dictionary containing vitrage-specific data.

        Returns:
            float: The overall U-value (U) of the vitrage.
        """
        if vitrage["fermetures"]:
            vitrage["DeltaR"] = self.abaques["resistance_additionnelle_vitrage"](
                {"fermetures": vitrage["fermetures"]}, "resistance_additionnelle"
            )
            vitrage["Ujn"] = self.abaques["transmission_thermique_baie"](
                {"uw": vitrage["Uw"], "deltar": vitrage["DeltaR"]}, "ujn"
            )
            return vitrage["Ujn"]
        return vitrage["Uw"]

    def calculate_facteur_solaire(self, vitrage: Dict[str, Any]) -> float:
        """
        Calculates the solar factor (facteur solaire) for the vitrage.

        Args:
            vitrage (dict): Dictionary containing vitrage-specific data.

        Returns:
            float: The solar factor (facteur solaire) of the vitrage.
        """
        vitrage["type_vitrage_fs"] = vitrage["type_vitrage"]
        if vitrage["traitement_vitrage"] != "Non Traités":
            if "Double" in vitrage["type_vitrage"] or "Triple" in vitrage["type_vitrage"]:
                vitrage["type_vitrage_fs"] = vitrage["type_vitrage"] + " V.I.R"
        
        return self.abaques["facteur_solaire"](
            {
                "type_pose": vitrage["type_pose"],
                "materiaux": vitrage["type_materiaux"],
                "type_baie": vitrage["type_baie"],
                "type_vitrage": vitrage["type_vitrage_fs"],
            },
            "fts",
        )

    def calculate_c1j(self, vitrage: Dict[str, Any]) -> np.ndarray:
        """
        Calculates the orientation factor (c1j) for each month of the year.

        Args:
            vitrage (dict): Dictionary containing vitrage-specific data.

        Returns:
            np.ndarray: An array of orientation factors for each month.
        """
        orientation = "Horizontal" if vitrage["orientation"] == "Horizontal" else vitrage["orientation"]
        inclinaison = "NULL" if vitrage["orientation"] == "Horizontal" else vitrage["inclinaison"]
        return np.array(
            [
                self.abaques["coefficient_orientation"](
                    {
                        "zone_climatique": vitrage["zone_climatique"],
                        "month": month,
                        "orientation": orientation,
                        "inclination": inclinaison,
                    },
                    "c1",
                )
                for month in self.months
            ]
        )

    def calculate_fe(self, vitrage: Dict[str, Any]) -> tuple:
        """
        Calculates the shading coefficients (Fe, Fe1, Fe2) for the vitrage.

        Args:
            vitrage (dict): Dictionary containing vitrage-specific data.

        Returns:
            tuple: A tuple containing the overall shading coefficient (Fe) and its components (Fe1, Fe2).
        """
        Fe1 = 1.0
        if vitrage["masque_proche_type_masque"] and vitrage["masque_proche_type_masque"] != "Absence de masque proche":
            Fe1 = self.abaques["coef_masques_proches"](
                {
                    "type_masque": vitrage["masque_proche_type_masque"],
                    "avance": vitrage["masque_proche_avance"],
                    "orientation": vitrage["masque_proche_orientation"],
                    "rapport_l1_l2": vitrage["masque_proche_rapport_l1_l2"],
                    "beta_gama": vitrage["masque_proche_beta_gama"],
                    "angle_superieur_30": vitrage["masque_proche_angle_superieur_30"],
                },
                "fe1",
            )

        Fe2_1 = 1.0
        if vitrage["masque_lointain_hauteur_alpha"] and vitrage["masque_lointain_orientation"]:
            Fe2_1 = self.abaques["coef_masques_lointain_homogene"](
                {
                    "hauteur_alpha": vitrage["masque_lointain_hauteur_alpha"],
                    "orientation": vitrage["masque_lointain_orientation"],
                },
                "fe2",
            )

        Fe2_2 = 1.0
        if (
            vitrage["ombrage_lointain_hauteur"]
            and vitrage["ombrage_lointain_orientation"]
            and vitrage["ombrage_lointain_secteur"]
        ):
            Fe2_2 = 1 - 0.01 * self.abaques["coef_ombrage_lointain"](
                {
                    "hauteur": vitrage["ombrage_lointain_hauteur"],
                    "orientation": vitrage["ombrage_lointain_orientation"],
                    "secteur": vitrage["ombrage_lointain_secteur"],
                },
                "omb",
            )

        Fe2 = min(Fe2_1, Fe2_2)
        Fe = Fe1 * Fe2
        return Fe, Fe1, Fe2

    def calculate_ssej(self, vitrage: Dict[str, Any]) -> np.ndarray:
        """
        Calculates the solar heat gain (ssej) for each month of the year.

        Args:
            vitrage (dict): Dictionary containing vitrage-specific data.

        Returns:
            np.ndarray: An array of solar heat gains for each month.
        """
        return vitrage["surface_vitrage"] * vitrage["facteur_solaire"] * vitrage["Fe"] * vitrage["c1j"]

from py3cl.libs.utils import safe_divide
from py3cl.libs.base import BaseProcessor
from pydantic import BaseModel
import os
from typing import Optional, List, Dict, Any, Union


class ParoiInput(BaseModel):
    """
    Represents the input data for a Paroi object.

    Attributes:
        identifiant: The identifier of the wall.
        identifiant_adjacents: The identifiers of the adjacent items, only for walls (used to compute pths). For plancher it can only reference an ouvrant.

        surface_paroi: The surface area of the wall in square meters.
        hauteur: The height/plancher of the wall in meters. None for planchers
        largeur: The width/plancher of the wall in meters. None for planchers
        inertie: The inertia of the wall, which can be one of 'Léger' ou 'Lourd'

        uparoi: The non-insulated thermal transmittance of the wall in W/(m²·K).
        materiaux: The materials used to construct the wall.
        epaisseur: The thickness of the wall in centimeters.
        isolation: Whether or not the wall is insulated.
        annee_isolation: The year the wall was insulated.
        r_isolant: The thermal resistance of the insulation in m²·K/W.
        epaisseur_isolant: The thickness of the insulation in centimeters.
        effet_joule: Whether or not the wall is affected by the Joule effect.

        # Specifique aux murs
        enduit: Whether or not the wall has a plaster.
        doublage_with_lame_below_15mm: Whether or not the wall has a lining with a thickness below 15mm.
        doublage_with_lame_above_15mm: Whether or not the wall has a lining with a thickness above 15mm.

        # Specifique aux planchers bas
        is_vide_sanitaire: Whether or not the floor has a crawl space.
        is_unheated_underground: Whether or not the floor is under an unheated underground space.
        is_terre_plain: Whether or not the floor is on bare ground.
        surface_immeuble: The surface area of the building in square meters.
        perimeter_immeuble: The perimeter of the building in meters.

        # Specifique aux planchers hauts
        # None

        # Coefficient d'attenuation
        exterior_type_or_local_non_chauffe: The type of exterior wall or non-heated local, which can be one of 'Mur', 'Plancher bas', 'Plancher haut', 'Véranda', or 'Local non chauffé'.
        surface_paroi_contact: The surface area of the wall in contact with the exterior or non-heated local in square meters.
        surface_paroi_local_non_chauffe: The surface area of the wall facing the non-heated local in square meters.
        local_non_chauffe_isole: Whether or not the non-heated local is insulated.

        # Specifique aux verandas
        orientation: The orientation of the veranda, which can be one of 'Nord', 'Sud', 'Est', or 'Ouest'.
    """

    identifiant: str
    identifiant_adjacents: Optional[List[str]] = None

    # dimensions
    surface_paroi: float
    largeur: Optional[float] = None
    hauteur: Optional[float] = None
    inertie: Optional[str] = None  # Leger / Lourd

    # Coefficient de transmission surfacique
    exterior_type_or_local_non_chauffe: Optional[str] = None
    # type_paroi: str  # ['Mur', 'Plancher bas', 'Plancher haut']
    uparoi: Optional[float] = None
    materiaux: Optional[str] = None
    epaisseur: Optional[float] = None
    isolation: Optional[bool] = None
    annee_isolation: Optional[Union[int, str]] = None
    r_isolant: Optional[float] = None
    epaisseur_isolant: Optional[float] = None
    effet_joule: Optional[bool] = None

    # Coefficient d'attenuation
    surface_paroi_contact: Optional[Union[float, str]] = None
    surface_paroi_local_non_chauffe: Optional[Union[float, str]] = None
    local_non_chauffe_isole: Optional[Union[bool, str]] = None

    # Specifique aux murs
    enduit: Optional[bool] = None
    doublage_with_lame_below_15mm: Optional[bool] = None
    doublage_with_lame_above_15mm: Optional[bool] = None

    # Specifique aux planchers bas
    is_vide_sanitaire: Optional[bool] = None
    is_unheated_underground: Optional[bool] = None
    is_terre_plain: Optional[bool] = None
    surface_immeuble: Optional[float] = None
    perimeter_immeuble: Optional[float] = None

    # Specifique aux verandas
    orientation: Optional[str] = None  # ['Nord', 'Sud', 'Est', 'Ouest']


class Paroi(BaseProcessor):
    """
    A processor class that handles the initialization and configuration of processing parameters based on input schemes,

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
        """
        Initializes a new instance of the Paroi class.


        Args:
            abaques (dict): A dictionary containing reference data and coefficients necessary for calculations.
        """
        self.characteristics_corrections = {
            "inertie": ["Léger", "Lourd"],
            "effet_joule": [True, False],
        }
        super().__init__(
            abaques,
            ParoiInput,
            characteristics_corrections=self.characteristics_corrections,
        )

    def define_categorical(self):
        self.categorical_fields = [
            # 'identifiant_adjacents',
            # 'type_paroi',
            "materiaux",
            "isolation",
            "effet_joule",
            "enduit",
            "doublage_with_lame_below_15mm",
            "doublage_with_lame_above_15mm",
            "is_vide_sanitaire",
            "is_unheated_underground",
            "is_terre_plain",
            "exterior_type_or_local_non_chauffe",
            "local_non_chauffe_isole",
            "orientation",
        ]

    def define_numerical(self):
        self.numerical_fields = [
            "surface_paroi",
            "largeur",
            "hauteur",
            "uparoi",
            "epaisseur",
            "annee_isolation",
            "r_isolant",
            "epaisseur_isolant",
            "surface_immeuble",
            "perimeter_immeuble",
            "surface_paroi_contact",
            "surface_paroi_local_non_chauffe",
        ]

    def define_abaques(self):
        self.used_abaques = {
            "coef_reduction_deperdition_exterieur": {
                # Mapping the exterior type to calculate reduction coefficients
                "aiu_aue": "exterior_type_or_local_non_chauffe"
            },
            "coef_reduction_veranda": {
                # Specific handling for verandas based on orientation and isolation
                "orientation_veranda": "orientation",
                "isolation_paroi": "isolation",
            },
            "local_non_chauffe": {
                # Handling non-heated local conditions based on building type
                "type_batiment": "type_batiment",  # Assuming 'type_batiment' is available in the dpe context
                "local_non_chauffe": "exterior_type_or_local_non_chauffe",
            },
            "coef_reduction_deperdition_local": {
                # Handling local non-heated coefficients based on surface contact and isolation
                "aiu_aue_max": "surface_paroi_contact",
                "aue_isole": "local_non_chauffe_isole",
                "aiu_isole": "isolation",
                "uv_ue": "calc_uvue",
            },
            "uph0": {
                # Basic thermal transmittance for upper floors based on materials
                "materiaux": "materiaux"
            },
            "upb0": {
                # Basic thermal transmittance for lower floors based on materials
                "materiaux": "materiaux"
            },
            "umur0": {
                # Basic thermal transmittance for walls based on materials and thickness
                "umur0_materiaux": "materiaux",
                "epaisseur": "epaisseur",
            },
        }

    def forward(self, dpe, kwargs: ParoiInput):
        """
        Processes input data for a wall using provided models and reference coefficients.

        Args:
            dpe (dict): A dictionary containing information about the overall energy performance of the building.
            kwargs (ParoiInput): An instance of ParoiInput containing detailed wall-specific parameters.

        Returns:
            dict: A dictionary containing processed data and calculated values for the wall.
        """
        paroi = kwargs.dict()
        if paroi['annee_isolation']=="Unknown or Empty":
            paroi["annee_isolation"]=None
        paroi["annee_construction_ou_isolation"] = (
            paroi["annee_isolation"]
            if paroi["annee_isolation"] is not None
            else dpe["annee_construction"]
        )
        paroi["zone_hiver"] = dpe["zone_hiver"]

        # Calc b : coefficient de reduction de deperdition
        if (
            paroi["exterior_type_or_local_non_chauffe"]
            in self.abaques["coef_reduction_deperdition_exterieur"].key_characteristics[
                "aiu_aue"
            ]
        ):
            paroi["b"] = self.abaques["coef_reduction_deperdition_exterieur"](
                {"aiu_aue": paroi["exterior_type_or_local_non_chauffe"]}, "valeur"
            )
        elif paroi["exterior_type_or_local_non_chauffe"] == "Véranda":
            paroi["b"] = self.abaques["coef_reduction_veranda"](
                {
                    "zone_hiver": paroi["zone_hiver"],
                    "orientation_veranda": paroi["orientation"],
                    "isolation_paroi": paroi["isolation"],
                },
                "bver",
            )
        else:
            paroi["aiu_aue"] = safe_divide(
                paroi["surface_paroi_contact"], paroi["surface_paroi_local_non_chauffe"]
            )
            paroi["uvue"] = self.abaques["local_non_chauffe"](
                {
                    "type_batiment": dpe["type_batiment"],
                    "local_non_chauffe": paroi["exterior_type_or_local_non_chauffe"],
                },
                "uvue",
            )
            paroi["b"] = self.abaques["coef_reduction_deperdition_local"](
                {
                    "aiu_aue_max": paroi["aiu_aue"],
                    "aue_isole": paroi["local_non_chauffe_isole"],
                    "aiu_isole": paroi["isolation"],
                    "uv_ue": paroi["uvue"],
                },
                "valeur",
            )

        # Calc U
        if paroi["uparoi"] is not None:
            paroi["U"] = paroi["uparoi"]
        else:
            if "mur" in paroi["identifiant"]:
                paroi = self._forward_mur(paroi)
            elif "plancher_bas" in paroi["identifiant"]:
                paroi = self._forward_plancher_bas(paroi)
            elif "plancher_haut" in paroi["identifiant"]:
                paroi = self._forward_plancher_haut(paroi)

        return paroi

    def _forward_plancher_haut(self, paroi):
        """
        Processes and calculates thermal transmittance values specifically for upper floors.

        Args:
            paroi (dict): A dictionary containing specific parameters for an upper floor.

        Returns:
            dict: The updated dictionary with calculated U values for the floor.
        """
        if paroi["materiaux"]:
            uparoi_0 = self.abaques["uph0"]({"materiaux": paroi["materiaux"]}, "uph0")
            uparoi_nu = min(uparoi_0, 2.5)
        else:
            uparoi_nu = 2.5
        paroi["U_nu"] = uparoi_nu
        if paroi["isolation"] == False:
            paroi["U"] = uparoi_nu
        elif paroi["isolation"] is None:
            uparoi_tab = self.abaques["uph"](
                {
                    "type_toit": paroi["annee_construction_ou_isolation"],
                    "zone_hiver": paroi["zone_hiver"],
                    "effet_joule": paroi["effet_joule"],
                },
                "uph",
            )
            paroi["U"] = min(uparoi_0, uparoi_tab)
        else:
            if paroi["r_isolant"]:
                paroi["U"] = safe_divide(
                    1, safe_divide(1, uparoi_0) + paroi["r_isolant"]
                )
            elif paroi["epaisseur_isolant"]:
                paroi["U"] = safe_divide(
                    1,
                    safe_divide(1, uparoi_0)
                    + safe_divide(paroi["epaisseur_isolant"], 40),
                )
            else:
                uparoi_tab = self.abaques["uph"](
                    {
                        "type_toit": paroi["annee_construction_ou_isolation"],
                        "zone_hiver": paroi["zone_hiver"],
                        "effet_joule": paroi["effet_joule"],
                    },
                    "uph",
                )
                paroi["U"] = min(uparoi_0, uparoi_tab)
        return paroi

    def _forward_plancher_bas(self, paroi):
        """
        Processes and calculates thermal transmittance values specifically for lower floors.

        Args:
            paroi (dict): A dictionary containing specific parameters for a lower floor.

        Returns:
            dict: The updated dictionary with calculated U values for the floor.
        """
        if paroi["materiaux"]:
            uparoi_0 = self.abaques["upb0"]({"materiaux": paroi["materiaux"]}, "upb0")
            uparoi_nu = min(uparoi_0, 2.0)
        else:
            uparoi_nu = 2.0
        paroi["U_nu"] = uparoi_nu
        if paroi["isolation"] == False:
            paroi["U"] = uparoi_nu
        elif paroi["isolation"] is None:
            uparoi_tab = self.abaques["upb"](
                {
                    "annee_construction_max": paroi["annee_construction_ou_isolation"],
                    "zone_hiver": paroi["zone_hiver"],
                    "effet_joule": paroi["effet_joule"],
                },
                "upb",
            )
            paroi["U"] = min(uparoi_0, uparoi_tab)
        else:
            if paroi["r_isolant"]:
                paroi["U"] = safe_divide(
                    1, safe_divide(1, uparoi_0) + paroi["r_isolant"]
                )
            elif paroi["epaisseur_isolant"]:
                paroi["U"] = safe_divide(
                    1,
                    safe_divide(1, uparoi_0)
                    + safe_divide(paroi["epaisseur_isolant"], 42),
                )
            else:
                uparoi_tab = self.abaques["upb"](
                    {
                        "annee_construction_max": paroi[
                            "annee_construction_ou_isolation"
                        ],
                        "zone_hiver": paroi["zone_hiver"],
                        "effet_joule": paroi["effet_joule"],
                    },
                    "upb",
                )
                paroi["U"] = min(uparoi_0, uparoi_tab)

        if (
            paroi["is_vide_sanitaire"]
            or paroi["is_unheated_underground"]
            or paroi["is_terre_plain"]
        ):
            try:
                ssp = 2 * paroi["surface_immeuble"] / paroi["perimeter_immeuble"]
            except:
                ssp = 2 * paroi["surface_paroi"] / paroi["perimeter_immeuble"]

            if paroi["is_vide_sanitaire"] or paroi["is_unheated_underground"]:
                type_tp = "other"
            else:
                if paroi["annee_construction"] < 2001:
                    type_tp = "tp_pre_2001"
                else:
                    type_tp = "tp_post_2001 plein"
            paroi["Upb_sans_tp"] = paroi["U"]
            paroi["U"] = self.abaques["upb_tp"](
                {"type_tp": type_tp, "2S/P": ssp, "Upb": paroi["Upb_sans_tp"]}, "Value"
            )
        return paroi

    def _forward_mur(self, paroi):
        """
        Processes and calculates thermal transmittance values specifically for walls.

        Args:
            paroi (dict): A dictionary containing specific parameters for a wall.

        Returns:
            dict: The updated dictionary with calculated U values for the wall.
        """
        if paroi["materiaux"] and paroi["epaisseur"]:
            uparoi_0 = self.abaques["umur0"](
                {
                    "umur0_materiaux": paroi["materiaux"],
                    "epaisseur": paroi["epaisseur"],
                },
                "umur",
            )
            uparoi_nu = min(uparoi_0, 2.5)
        else:
            uparoi_nu = 2.5
        paroi["U_nu"] = uparoi_nu
        if paroi["isolation"] == False:
            r_isolant = 0
            if paroi["enduit"]:
                r_isolant = 0.7
            elif paroi["doublage_with_lame_below_15mm"]:
                r_isolant = 0.1
            elif paroi["doublage_with_lame_above_15mm"]:
                r_isolant = 0.21
            paroi["U"] = safe_divide(1, safe_divide(1, uparoi_nu) + r_isolant)
        elif paroi["isolation"] is None:
            uparoi_tab = self.abaques["umur"](
                {
                    "annee_construction_max": paroi["annee_construction_ou_isolation"],
                    "zone_hiver": paroi["zone_hiver"],
                    "effet_joule": paroi["effet_joule"],
                },
                "umur",
            )
            paroi["U"] = min(uparoi_0, uparoi_tab)
        else:
            if paroi["r_isolant"]:
                paroi["U"] = safe_divide(
                    1, safe_divide(1, uparoi_0) + paroi["r_isolant"]
                )
            elif paroi["epaisseur_isolant"]:
                paroi["U"] = safe_divide(
                    1,
                    safe_divide(1, uparoi_0)
                    + safe_divide(paroi["epaisseur_isolant"], 40),
                )
            else:
                uparoi_tab = self.abaques["umur"](
                    {
                        "annee_construction_max": paroi[
                            "annee_construction_ou_isolation"
                        ],
                        "zone_hiver": paroi["zone_hiver"],
                        "effet_joule": paroi["effet_joule"],
                    },
                    "umur",
                )
                paroi["U"] = min(uparoi_0, uparoi_tab)
        return paroi

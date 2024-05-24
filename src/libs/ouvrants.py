from libs.utils import safe_divide
from pydantic import BaseModel
import os
import numpy as np


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
        masque_proche_avance (float, optional): The distance between the window and the nearby shading element (meters). Defaults to None.
        masque_proche_orientation (str, optional): The orientation of the nearby shading element. Defaults to None.
        masque_proche_rapport_l1_l2 (float, optional): The ratio of the width to the height of the nearby shading element. Defaults to None.
        masque_proche_beta_gama (float, optional): The beta-gamma angle of the nearby shading element. Defaults to None.
        masque_proche_angle_superieur_30 (float, optional): The angle of the nearby shading element relative to the horizontal plane (degrees). Defaults to None.
        masque_lointain_hauteur_alpha (float, optional): The height-alpha angle of the distant shading element (degrees). Defaults to None.
        masque_lointain_orientation (str, optional): The orientation of the distant shading element. Defaults to None.
        ombrage_lointain_hauteur (float, optional): The height of the distant obstacle (degrees). Defaults to None.
        ombrage_lointain_orientation (str, optional): The orientation of the distant obstacle. Defaults to None.
        ombrage_lointain_secteur (str, optional): The sector of the distant obstacle. Defaults to None.
    """

    ## Parois en contact
    identifiant: str

    ## Dimensions
    surface_vitrage: float
    hauteur_vitrage: float
    largeur_vitrage: float

    type_vitrage: str
    orientation: str = None  # Sud, Nord, Est, Ouest, Horizontal
    inclinaison: str = None  # >= 75, 75° >  >= 25°, < 25°, Paroi Horizontale, >= 75 = vertical
    remplissage: str = None
    traitement_vitrage: str = None
    epaisseur_lame: float = None
    type_pose: str = None
    type_materiaux: str = None
    type_menuiserie: str = None
    type_baie: str = None
    fermetures: str = None
    masque_proche_type_masque: str = None
    masque_proche_avance: float = None
    masque_proche_orientation: str = None
    masque_proche_rapport_l1_l2: float = None
    masque_proche_beta_gama: float = None
    masque_proche_angle_superieur_30: float = None
    masque_lointain_hauteur_alpha: str = None
    masque_lointain_orientation: str = None
    ombrage_lointain_hauteur: float = None
    ombrage_lointain_orientation: str = None
    ombrage_lointain_secteur: str = None

    exterior_type_or_local_non_chauffe: str = None
    surface_paroi_contact: float = None
    surface_paroi_local_non_chauffe: float = None
    local_non_chauffe_isole: bool = None


class Vitrage:
    def __init__(self, abaques):
        self.abaques = abaques
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

    def forward(self, dpe, kwargs: VitrageInput):
        vitrage = kwargs.dict()
        vitrage["zone_climatique"] = dpe["zone_climatique"]
        vitrage["zone_hiver"] = dpe["zone_hiver"]

        # Calc b : coefficient de reduction de deperdition
        if (
            vitrage["exterior_type_or_local_non_chauffe"]
            in self.abaques["coef_reduction_deperdition_exterieur"].key_characteristics["aiu_aue"]
        ):
            vitrage["b"] = self.abaques["coef_reduction_deperdition_exterieur"](
                {"aiu_aue": vitrage["exterior_type_or_local_non_chauffe"]}, "valeur"
            )
        elif vitrage["exterior_type_or_local_non_chauffe"] == "Véranda":
            vitrage["b"] = self.abaques["coef_reduction_veranda"](
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
                {
                    "type_batiment": dpe["type_batiment"],
                    "local_non_chauffe": vitrage["exterior_type_or_local_non_chauffe"],
                },
                "uvue",
            )
            vitrage["b"] = self.abaques["coef_reduction_deperdition_local"](
                {
                    "aiu_aue_max": vitrage["aiu_aue"],
                    "aue_isole": vitrage["isolation"],
                    "aiu_isole": vitrage["local_non_chauffe_isole"],
                    "uv_ue": vitrage["uvue"],
                },
                "valeur",
            )

        # Calc Ug
        if vitrage["type_vitrage"] == "Simple Vitrage":
            vitrage["Ug"] = 5.8
        else:
            if vitrage["orientation"] == "Horizontal":
                orientation = "Horizontale"
                vitrage["orientation"] = vitrage["orientation"]
            else:
                orientation = "Verticale"
            vitrage["Ug"] = self.abaques["ug_vitrage"](
                {
                    "type_vitrage": vitrage["type_vitrage"],
                    "orientation": orientation,
                    "remplissage": vitrage["remplissage"],
                    "traitement_vitrage": vitrage["traitement_vitrage"],
                    "epaisseur_lame": vitrage["epaisseur_lame"],
                },
                "ug",
            )

        # Calc Uw
        if vitrage["type_baie"] in self.valid_sub_type_fenetres:
            type_baie = "Fenêtres / Porte-fenêtres"
        else:
            type_baie = vitrage["type_baie"]
        vitrage["Uw"] = self.abaques["uw_vitrage"](
            {
                "type_materiaux": vitrage["type_materiaux"],
                "type_menuiserie": vitrage["type_menuiserie"],
                "type_baie": type_baie,
                "ug": vitrage["Ug"],
            },
            "uw",
        )

        if vitrage["fermetures"]:
            # Calc DeltaR
            vitrage["DeltaR"] = self.abaques["resistance_additionnelle_vitrage"](
                {"fermetures": vitrage["fermetures"]}, "resistance_additionnelle"
            )
            vitrage["Ujn"] = self.abaques["transmission_thermique_baie"](
                {"uw": vitrage["Uw"], "deltar": vitrage["DeltaR"]}, "ujn"
            )
            vitrage["U"] = vitrage["Ujn"]
        else:
            vitrage["U"] = vitrage["Uw"]

        ## Calcul facteur solaire

        if vitrage["type_baie"] != "Portes":
            if vitrage["traitement_vitrage"] != "Non Traités":
                if "Double" in vitrage["type_vitrage"] or "Triple" in vitrage["type_vitrage"]:
                    vitrage["type_vitrage"] = vitrage["type_vitrage"] + " V.I.R"

            vitrage["facteur_solaire"] = self.abaques["facteur_solaire"](
                {
                    "type_pose": vitrage["type_pose"],
                    "materiaux": vitrage["type_materiaux"],
                    "type_baie": vitrage["type_baie"],
                    "type_vitrage": vitrage["type_vitrage"],
                },
                "fts",
            )

            ## Calcul facteur d'orientation
            if vitrage["orientation"] == "Horizontal":
                orientation = "Horizontal"
                inclinaison = "NULL"
            else:
                inclinaison = vitrage["inclinaison"]
                orientation = vitrage["orientation"]

            vitrage["c1j"] = np.array(
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

            ## Calcul coefficient de masques proches
            Fe1 = 1.0
            if (
                vitrage["masque_proche_type_masque"]
                and vitrage["masque_proche_type_masque"] != "Absence de masque proche"
            ):
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
            vitrage["Fe"] = Fe
            vitrage["Fe1"] = Fe1
            vitrage["Fe2"] = Fe2

            vitrage["ssej"] = vitrage["surface_vitrage"] * vitrage["facteur_solaire"] * vitrage["Fe"] * vitrage["c1j"]
        return vitrage

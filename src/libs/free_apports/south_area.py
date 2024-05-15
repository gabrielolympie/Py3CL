import pandas as pd
import numpy as np
import os

from libs.utils import safe_divide
from libs.base import BaseProcessor


class SouthAreaProcessor(BaseProcessor):
    def __init__(
        self,
        data_path="../data/raw",
    ):
        """
        Processor to compute the south area equivalent of a single facade for a given month.
        """
        super().__init__(data_path)

    @property
    def calc_input(self):
        """Valid input for calc method for categorical variables"""
        return {
            "zone": self.valid_zone,
            "mois": self.valid_mois,
            "orientation_paroi": self.valid_coefficient_orientation_orientation_paroi,
            "inclinaison_paroi": self.valid_coefficient_orientation_inclinaison_paroi,
            "materiaux": self.valid_facteur_solaire_materiaux,
            "type_baie": self.valid_facteur_solaire_type_baie,
            "type_pose": self.valid_facteur_solaire_type_pose,
            "type_vitrage": self.valid_facteur_solaire_type_vitrage,
            "masque_proche_types": self.valid_coefficient_masques_proches_type_masque,
            "masque_proche_avances": self.valid_coefficient_masques_proches_avance,
            "masque_proche_rapports_l1_l2": self.valid_rapport_l1_l2,
            "masque_proche_beta_gamas": self.valid_beta_gama,
            "masque_lointain_orientation": self.valid_orientation,
            "masque_lointain_alpha": self.valid_coefficient_masques_lointains_homogenes_hauteur_alpha,
            "ombrage_obstacle_lointain_hauteurs": self.valid_ombrage_obstacle_lointain_hauteur,
            "ombrage_obstacle_lointain_secteurs": self.valid_ombrage_obstacle_lointain_secteur,
        }

    def calc(
        self,
        zone: str = None,
        mois: str = None,
        surface_baie: float = None,
        orientation_paroi: str = None,
        inclinaison_paroi: str = None,
        materiaux: str = None,
        type_baie: str = None,
        type_pose: str = None,
        type_vitrage: str = None,
        masque_proche_types: str = None,
        masque_proche_avances: str = None,
        masque_proche_rapports_l1_l2: str = None,
        masque_proche_beta_gamas: str = None,
        masque_lointain_homogene_orientation: str = None,
        masque_lointain_homogene_alpha: str = None,
        ombrage_obstacle_lointain_hauteurs: list = None,
        ombrage_obstacle_lointain_secteurs: list = None,
        ombrage_obstacle_lointain_orientations: list = None,
    ) -> float:
        """
        Calculate the south area equivalent (Sse) for a given month.

        The calculation of Sse is based on the formula:
        Sse_j = sum(A_i * Sw_i * Fe_i * C1_i,j)
        where:
        - A_i: Surface of the window i (m²)
        - Sw_i: Proportion of incident solar energy that penetrates the building through the window i
        - Fe_i: Sun exposure factor, which reflects the reduction of solar energy received by a window due to shading
        - C1_i,j: Orientation and inclination coefficient for window i for month j

        Valid values for categorical parameters can be found using the calc_input property.

        Args:
            zone (str): The geographical zone of the building. Must be one of the valid zones defined in the dataset.
            mois (str): The month for which the calculation is performed. Must be one of the valid months defined in the dataset.
            surface_baie (float): Surface area of the window (m²).
            orientation_paroi (str): Orientation of the wall. Must be one of the valid orientations defined in the dataset.
            inclinaison_paroi (str): Inclination of the wall. Must be one of the valid inclinations defined in the dataset.
            materiaux (str): Material of the window. Must be one of the valid materials defined in the dataset.
            type_baie (str): Type of window. Must be one of the valid window types defined in the dataset.
            type_pose (str): Type of installation (e.g., interior or exterior). Must be one of the valid installation types defined in the dataset.
            type_vitrage (str): Type of glazing (e.g., single, double, triple). Must be one of the valid glazing types defined in the dataset.
            masque_proche_types (list of str): List of types of nearby shading. Each entry must be one of the valid shading types defined in the dataset.
            masque_proche_avances (list of float): List of advances of nearby shading (in meters). Refer to the table in section 6.2.2.1.1 of the documentation.
            masque_proche_rapports_l1_l2 (list of float): List of ratios related to nearby shading. Refer to the table in section 6.2.2.1.2 of the documentation.
            masque_proche_beta_gamas (list of float): List of beta-gamma angles for nearby shading.
            masque_lointain_homogene_orientation (str): Orientation for distant shading. Must be one of the valid orientations defined in the dataset.
            masque_lointain_homogene_alpha (float): Alpha angle for distant shading (in degrees). Refer to the table in section 6.2.2.2.1 of the documentation.
            ombrage_obstacle_lointain_hauteurs (list of float): List of heights of distant obstacles (in degrees). Must be in same order as ombrage_obstacle_lointain_secteurs.
            ombrage_obstacle_lointain_secteurs (list of float): List of sectors of distant obstacles (in degrees). Must be in same order as ombrage_obstacle_lointain_hauteurs.
            ombrage_obstacle_lointain_orientations (list of str): List of orientations of distant obstacles. Must be in same order as ombrage_obstacle_lointain_hauteurs.

        Returns:
            float: The calculated south area equivalent (Sse) for the given parameters.
        """
        self.validate(
            zone=zone,
            mois=mois,
            orientation_paroi=orientation_paroi,
            inclinaison_paroi=inclinaison_paroi,
            materiaux=materiaux,
            type_baie=type_baie,
            type_pose=type_pose,
            type_vitrage=type_vitrage,
            masque_proche_types=masque_proche_types,
            masque_proche_avances=masque_proche_avances,
            masque_proche_rapports_l1_l2=masque_proche_rapports_l1_l2,
            masque_proche_beta_gamas=masque_proche_beta_gamas,
            masque_lointain_homogene_orientation=masque_lointain_homogene_orientation,
            masque_lointain_homogene_alpha=masque_lointain_homogene_alpha,
            ombrage_obstacle_lointain_hauteurs=ombrage_obstacle_lointain_hauteurs,
            ombrage_obstacle_lointain_secteurs=ombrage_obstacle_lointain_secteurs,
            ombrage_obstacle_lointain_orientations=ombrage_obstacle_lointain_orientations,
        )

        facteur_solaire = self._calc_facteur_solaire(
            materiaux=materiaux,
            type_baie=type_baie,
            type_pose=type_pose,
            type_vitrage=type_vitrage,
        )

        coefficient_orientation = self._calc_coefficient_orientation(
            zone=zone,
            mois=mois,
            orientation_paroi=orientation_paroi,
            inclinaison_paroi=inclinaison_paroi,
        )

        Fe1 = 1
        if masque_proche_types:
            for i, elt in enumerate(masque_proche_types):
                f = self._calc_coefficient_masques_proches(
                    type_masque=masque_proche_types[i],
                    avancee=masque_proche_avances[i],
                    orientation=orientation_paroi,
                    rapport_l1_l2=masque_proche_rapports_l1_l2[i],
                    beta_gama=masque_proche_beta_gamas[i],
                )
                if f < Fe1:
                    Fe1 = f

        Fe2_1 = 1
        if masque_lointain_homogene_alpha:
            Fe2_1 = self._calc_coefficient_masques_lointains_homogenes(
                hauteur_alpha=masque_lointain_homogene_alpha,
                orientation=masque_lointain_homogene_orientation,
            )

        Fe2_2 = 1
        if ombrage_obstacle_lointain_hauteurs:
            Fe2_2 = self._calc_ombrage_obstacles_lointains(
                hauteurs=ombrage_obstacle_lointain_hauteurs,
                secteurs=ombrage_obstacle_lointain_secteurs,
                orientations=ombrage_obstacle_lointain_orientations,
            )
        Fe2 = min(Fe2_1, Fe2_2)
        Fe = Fe1 * Fe2

        return surface_baie * facteur_solaire * coefficient_orientation * Fe

    def _calc_coefficient_orientation(
        self,
        zone: str = None,
        mois: str = None,
        orientation_paroi: str = None,
        inclinaison_paroi: str = None,
    ):
        assert zone in self.valid_zone, f"zone must be in {self.valid_zone}"
        assert mois in self.valid_mois, f"mois must be in {self.valid_mois}"
        assert (
            orientation_paroi in self.valid_coefficient_orientation_orientation_paroi
        ), f"orientation_paroi must be in {self.valid_coefficient_orientation_orientation_paroi}, got {orientation_paroi}"
        assert (
            inclinaison_paroi in self.valid_coefficient_orientation_inclinaison_paroi
        ), f"inclinaison_paroi must be in {self.valid_coefficient_orientation_inclinaison_paroi}, got {inclinaison_paroi}"
        if inclinaison_paroi == "Paroi Horizontale":
            orientation_paroi = "Paroi Horizontale"

        return self.coefficient_orientation[
            (zone, mois, orientation_paroi, inclinaison_paroi)
        ]

    def _calc_facteur_solaire(
        self,
        materiaux: str = None,
        type_baie: str = None,
        type_pose: str = None,
        type_vitrage: str = None,
    ):
        assert (
            materiaux in self.valid_facteur_solaire_materiaux
        ), f"materiaux must be in {self.valid_facteur_solaire_materiaux}, got {materiaux}"
        assert (
            type_baie in self.valid_facteur_solaire_type_baie
        ), f"type_baie must be in {self.valid_facteur_solaire_type_baie}, got {type_baie}"
        assert (
            type_pose in self.valid_facteur_solaire_type_pose
        ), f"type_pose must be in {self.valid_facteur_solaire_type_pose}, got {type_pose}"
        assert (
            type_vitrage in self.valid_facteur_solaire_type_vitrage
        ), f"type_vitrage must be in {self.valid_facteur_solaire_type_vitrage}"
        if materiaux is None:
            materiaux = np.nan
        if type_baie is None:
            type_baie = np.nan
        if type_pose is None:
            type_pose = np.nan
        if type_vitrage is None:
            type_vitrage = np.nan
        return self.facteur_solaire[(materiaux, type_baie, type_pose, type_vitrage)]

    def _calc_coefficient_masques_proches(
        self,
        type_masque: str = None,
        avancee: str = None,
        orientation: str = None,
        rapport_l1_l2: str = None,
        beta_gama: str = None,
    ):
        if orientation == "Nord" or orientation == "Sud":
            orientation = "Sud ou Nord"
        elif orientation == "Est" or orientation == "Ouest":
            orientation = "Est ou Ouest"

        assert (
            type_masque in self.valid_coefficient_masques_proches_type_masque
        ), f"type_masque must be in {self.valid_coefficient_masques_proches_type_masque}, got {type_masque}"
        if type_masque == "Absence de masque proche":
            return 1.0
        if type_masque == "Fond de balcon ou fond et flanc de loggias":
            return self._calc_coefficient_masques_proches_3(
                type_masque=type_masque,
                avancee=avancee,
                orientation=orientation,
            )
        elif type_masque == "Baie sous un balcon ou auvent":
            return self._calc_coefficient_masques_proches_4(
                type_masque=type_masque,
                avancee=avancee,
                rapport_l1_l2=rapport_l1_l2,
            )
        elif type_masque == "Baie masquée par une paroi latérale":
            return self._calc_coefficient_masques_proches_5(
                type_masque=type_masque,
                beta_gama=beta_gama,
            )
        elif type_masque == "Baie donnant sur un local non chauffé":
            return 0
        else:
            raise ValueError(f"Unknown type_masque: {type_masque}")

    def _calc_coefficient_masques_proches_3(
        self,
        type_masque: str = None,
        avancee: str = None,
        orientation: str = None,
    ):
        assert (
            type_masque in self.valid_coefficient_masques_proches_type_masque
        ), f"type_masque must be in {self.valid_coefficient_masques_proches_type_masque}, got {type_masque}"
        assert (
            avancee in self.valid_coefficient_masques_proches_avance
        ), f"avancee must be in {self.valid_coefficient_masques_proches_avance} when type_masque is {type_masque}, got {avancee}"
        assert (
            orientation in self.valid_orientation
        ), f"orientation must be in {self.valid_orientation} when type_masque is {type_masque}, got {orientation}"
        return self.coefficient_masques_proches[
            (type_masque, avancee, orientation, "Null", "Null")
        ]

    def _calc_coefficient_masques_proches_4(
        self,
        type_masque: str = None,
        avancee: str = None,
        rapport_l1_l2: str = None,
    ):
        assert (
            type_masque in self.valid_coefficient_masques_proches_type_masque
        ), f"type_masque must be in {self.valid_coefficient_masques_proches_type_masque}, got {type_masque}"
        assert (
            avancee in self.valid_coefficient_masques_proches_avance
        ), f"avancee must be in {self.valid_coefficient_masques_proches_avance} when type_masque is {type_masque}, got {avancee}"
        assert (
            rapport_l1_l2 in self.valid_rapport_l1_l2
        ), f"rapport_l1_l2 must be in {self.valid_rapport_l1_l2} when type_masque is {type_masque}, got {rapport_l1_l2}"

        return self.coefficient_masques_proches[
            (type_masque, avancee, "Null", rapport_l1_l2, "Null")
        ]

    def _calc_coefficient_masques_proches_5(
        self,
        type_masque: str = None,
        beta_gama: str = None,
    ):
        assert (
            type_masque in self.valid_coefficient_masques_proches_type_masque
        ), f"type_masque must be in {self.valid_coefficient_masques_proches_type_masque}, got {type_masque}"
        assert (
            beta_gama in self.valid_beta_gama
        ), f"beta_gama must be in {self.valid_beta_gama} when type_masque is {type_masque}, got {beta_gama}"
        return self.coefficient_masques_proches[
            (type_masque, "Null", "Null", "Null", beta_gama)
        ]

    def _calc_coefficient_masques_lointains_homogenes(
        self,
        hauteur_alpha: str = None,
        orientation: str = None,
    ):
        assert (
            hauteur_alpha
            in self.valid_coefficient_masques_lointains_homogenes_hauteur_alpha
        ), f"hauteur_alpha must be in {self.valid_coefficient_masques_lointains_homogenes_hauteur_alpha}, got {hauteur_alpha}"
        assert (
            orientation in self.valid_orientation
        ), f"orientation must be in {self.valid_orientation}"

        if hauteur_alpha == "< 15" or hauteur_alpha == "Absence de masque":
            return 0.1

        return self.coefficient_masques_lointains_homogenes[
            (hauteur_alpha, orientation)
        ]

    def _calc_ombrage_obstacle_lointain(
        self,
        hauteur: str = None,
        secteur: str = None,
        orientation: str = None,
    ):
        assert (
            hauteur in self.valid_ombrage_obstacle_lointain_hauteur
        ), f"hauteur must be in {self.valid_ombrage_obstacle_lointain_hauteur}, got {hauteur}"
        assert (
            secteur in self.valid_ombrage_obstacle_lointain_secteur
        ), f"secteur must be in {self.valid_ombrage_obstacle_lointain_secteur}, got {secteur}"

        if hauteur == "< 15" or hauteur == "Absence de masque":
            return 0

        if orientation == "Nord" or orientation == "Sud":
            orientation = "Sud ou Nord"
        elif orientation == "Est" or orientation == "Ouest":
            orientation = "Est ou Ouest"

        if orientation == "Sud ou Nord":
            assert secteur in [
                "Facade Sud/Nord secteurs latéraux",
                "Facade Sud/Nord secteurs centraux",
                "Facade Est/Ouest secteur latéral vers le sud",
            ], f"when orientation is nord or sud, secteur must be in ['Facade Sud/Nord secteurs latéraux', 'Facade Sud/Nord secteurs centraux', 'Facade Est/Ouest secteur latéral vers le sud'], got {secteur}"
        elif orientation == "Est ou Ouest":
            assert secteur in [
                "Est/Ouest secteur central vers le sud",
                "Est/Ouest 2 autres secteurs",
            ], f"when orientation is est or west, secteur must be in ['Est/Ouest secteur central vers le sud', 'Est/Ouest 2 autres secteurs'], got {secteur}"

        return self.ombrage_obstacle_lointain[(hauteur, orientation, secteur)]

    def _calc_ombrage_obstacles_lointains(
        self,
        hauteurs: str = None,
        secteurs: str = None,
        orientations: str = None,
    ):
        return 1 - 0.01 * sum(
            [
                self._calc_ombrage_obstacle_lointain(
                    hauteur=hauteur, secteur=secteur, orientation=orientation
                )
                for hauteur, secteur, orientation in zip(
                    hauteurs, secteurs, orientations
                )
            ]
        )

    def load(
        self,
        data_path,
        coefficient_orientation_inclinaison_paroi="tv020_coefficient_orientation_inclinaison_paroi.csv",
        coefficient_orientation_orientation_paroi="tv020_coefficient_orientation_orientation_paroi.csv",
        coefficient_orientation="tv020_bis_coefficient_orientation.csv",
        facteur_solaire_materiaux="tv021_facteur_solaire_materiaux.csv",
        facteur_solaire_type_baie="tv021_facteur_solaire_type_baie.csv",
        facteur_solaire_type_pose="tv021_facteur_solaire_type_pose.csv",
        facteur_solaire_type_vitrage="tv021_facteur_solaire_type_vitrage.csv",
        facteur_solaire="tv021_facteur_solaire.csv",
        coefficient_masques_proches_avance="tv022_coefficient_masques_proches_avance.csv",
        coefficient_masques_proches_type_masque="tv022_coefficient_masques_proches_type_masque.csv",
        orientation="tv0xx_orientation.csv",
        coefficient_masques_proches="tv022_coefficient_masques_proches.csv",
        coefficient_masques_lointains_homogenes_hauteur_alpha="tv023_coefficient_masques_lointains_homogenes_hauteur_alpha.csv",
        coefficient_masques_lointains_homogenes="tv023_coefficient_masques_lointains_homogenes.csv",
        ombrage_obstacle_lointain_hauteur="tv024_ombrage_obstacle_lointain_hauteur.csv",
        ombrage_obstacle_lointain_secteur="tv024_ombrage_obstacle_lointain_secteur.csv",
        ombrage_obstacle_lointain="tv024_ombrage_obstacle_lointain.csv",
    ):
        """
        Load data from data_path
        """
        self.coefficient_orientation_inclinaison_paroi = pd.read_csv(
            os.path.join(data_path, coefficient_orientation_inclinaison_paroi)
        )
        self.coefficient_orientation_orientation_paroi = pd.read_csv(
            os.path.join(data_path, coefficient_orientation_orientation_paroi)
        )
        self.coefficient_orientation = pd.read_csv(
            os.path.join(data_path, coefficient_orientation)
        )
        self.facteur_solaire_materiaux = pd.read_csv(
            os.path.join(data_path, facteur_solaire_materiaux)
        )
        self.facteur_solaire_type_baie = pd.read_csv(
            os.path.join(data_path, facteur_solaire_type_baie)
        )
        self.facteur_solaire_type_pose = pd.read_csv(
            os.path.join(data_path, facteur_solaire_type_pose)
        )
        self.facteur_solaire_type_vitrage = pd.read_csv(
            os.path.join(data_path, facteur_solaire_type_vitrage)
        )
        self.facteur_solaire = pd.read_csv(os.path.join(data_path, facteur_solaire))
        self.coefficient_masques_proches_avance = pd.read_csv(
            os.path.join(data_path, coefficient_masques_proches_avance)
        )
        self.coefficient_masques_proches_type_masque = pd.read_csv(
            os.path.join(data_path, coefficient_masques_proches_type_masque)
        )
        self.orientation = pd.read_csv(os.path.join(data_path, orientation))
        self.coefficient_masques_proches = pd.read_csv(
            os.path.join(data_path, coefficient_masques_proches)
        )
        self.coefficient_masques_lointains_homogenes_hauteur_alpha = pd.read_csv(
            os.path.join(
                data_path, coefficient_masques_lointains_homogenes_hauteur_alpha
            )
        )
        self.coefficient_masques_lointains_homogenes = pd.read_csv(
            os.path.join(data_path, coefficient_masques_lointains_homogenes)
        )
        self.ombrage_obstacle_lointain_hauteur = pd.read_csv(
            os.path.join(data_path, ombrage_obstacle_lointain_hauteur)
        )
        self.ombrage_obstacle_lointain_secteur = pd.read_csv(
            os.path.join(data_path, ombrage_obstacle_lointain_secteur)
        )
        self.ombrage_obstacle_lointain = pd.read_csv(
            os.path.join(data_path, ombrage_obstacle_lointain)
        )

    def preprocess(
        self,
    ):
        """
        Preprocess data for further computation
        """
        self._preprocess_coefficient_orientation_inclinaison_paroi()
        self._preprocess_coefficient_orientation_orientation_paroi()
        self._preprocess_coefficient_orientation()
        self._preprocess_facteur_solaire_materiaux()
        self._preprocess_facteur_solaire_type_baie()
        self._preprocess_facteur_solaire_type_pose()
        self._preprocess_facteur_solaire_type_vitrage()
        self._preprocess_facteur_solaire()
        self._preprocess_coefficient_masques_proches_avance()
        self._preprocess_coefficient_masques_proches_type_masque()
        self._preprocess_orientation()
        self._preprocess_coefficient_masques_proches()
        self._preprocess_coefficient_masques_lointains_homogenes_hauteur_alpha()
        self._preprocess_coefficient_masques_lointains_homogenes()
        self._preprocess_ombrage_obstacle_lointain_hauteur()
        self._preprocess_ombrage_obstacle_lointain_secteur()
        self._preprocess_ombrage_obstacle_lointain()

    def _preprocess_coefficient_orientation_inclinaison_paroi(self):
        self.coefficient_orientation_inclinaison_paroi["inclination_paroi"] = (
            self.coefficient_orientation_inclinaison_paroi["inclinaison_paroi"].replace(
                {">= 75°": ">=75°", "75° >  >= 25°": "75°> ≥25°", "< 25°": "<25°"}
            )
        )
        self.coefficient_orientation_inclinaison_paroi = (
            self.coefficient_orientation_inclinaison_paroi.set_index(
                "inclinaison_paroi"
            )["id"].to_dict()
        )
        self.valid_coefficient_orientation_inclinaison_paroi = list(
            self.coefficient_orientation_inclinaison_paroi.keys()
        ) + [None]

    def _preprocess_coefficient_orientation_orientation_paroi(self):
        self.coefficient_orientation_orientation_paroi = (
            self.coefficient_orientation_orientation_paroi.set_index(
                "orientation_paroi"
            )["id"].to_dict()
        )
        self.valid_coefficient_orientation_orientation_paroi = list(
            self.coefficient_orientation_orientation_paroi.keys()
        ) + [None]

    def _preprocess_coefficient_orientation(self):
        self.valid_zone = list(self.coefficient_orientation["area"].unique())
        self.valid_mois = list(self.coefficient_orientation["month"].unique())
        self.coefficient_orientation["orientation"] = self.coefficient_orientation[
            "orientation"
        ].replace({"Horizontal": "Paroi Horizontale"})
        self.coefficient_orientation["inclination"] = self.coefficient_orientation[
            "inclination"
        ].fillna("Paroi Horizontale")
        self.valid_coefficient_orientation_inclinaison_paroi = list(
            self.coefficient_orientation["inclination"].unique()
        ) + [None]
        self.coefficient_orientation = self.coefficient_orientation.set_index(
            ["area", "month", "orientation", "inclination"]
        )["c1"].to_dict()

    def _preprocess_facteur_solaire_materiaux(self):
        self.facteur_solaire_materiaux = self.facteur_solaire_materiaux.set_index("id")[
            "materiaux"
        ].to_dict()
        self.valid_facteur_solaire_materiaux = list(
            self.facteur_solaire_materiaux.values()
        ) + [None]

    def _preprocess_facteur_solaire_type_baie(self):
        self.facteur_solaire_type_baie = self.facteur_solaire_type_baie.set_index("id")[
            "type_baie"
        ].to_dict()
        self.valid_facteur_solaire_type_baie = list(
            self.facteur_solaire_type_baie.values()
        ) + [None]

    def _preprocess_facteur_solaire_type_pose(self):
        self.facteur_solaire_type_pose = self.facteur_solaire_type_pose.set_index("id")[
            "type_pose"
        ].to_dict()
        self.valid_facteur_solaire_type_pose = list(
            self.facteur_solaire_type_pose.values()
        ) + [None]

    def _preprocess_facteur_solaire_type_vitrage(self):
        self.facteur_solaire_type_vitrage = self.facteur_solaire_type_vitrage.set_index(
            "id"
        )["type_vitrage"].to_dict()
        self.valid_facteur_solaire_type_vitrage = list(
            self.facteur_solaire_type_vitrage.values()
        ) + [None]

    def _preprocess_facteur_solaire(self):
        self.facteur_solaire["facteur_solaire_materiaux"] = self.facteur_solaire[
            "tv021_facteur_solaire_materiaux_id"
        ].replace(self.facteur_solaire_materiaux)
        self.facteur_solaire["facteur_solaire_type_baie"] = self.facteur_solaire[
            "tv021_facteur_solaire_type_baie_id"
        ].replace(self.facteur_solaire_type_baie)
        self.facteur_solaire["facteur_solaire_type_pose"] = self.facteur_solaire[
            "tv021_facteur_solaire_type_pose_id"
        ].replace(self.facteur_solaire_type_pose)
        self.facteur_solaire["facteur_solaire_type_vitrage"] = self.facteur_solaire[
            "tv021_facteur_solaire_type_vitrage_id"
        ].replace(self.facteur_solaire_type_vitrage)
        self.facteur_solaire = self.facteur_solaire.set_index(
            [
                "facteur_solaire_materiaux",
                "facteur_solaire_type_baie",
                "facteur_solaire_type_pose",
                "facteur_solaire_type_vitrage",
            ]
        )["id"].to_dict()

    def _preprocess_coefficient_masques_proches_avance(self):
        self.coefficient_masques_proches_avance = (
            self.coefficient_masques_proches_avance.set_index("id")["avance"].to_dict()
        )
        self.valid_coefficient_masques_proches_avance = list(
            self.coefficient_masques_proches_avance.values()
        ) + [None]

    def _preprocess_coefficient_masques_proches_type_masque(self):
        self.coefficient_masques_proches_type_masque = (
            self.coefficient_masques_proches_type_masque.set_index("id")[
                "type_masque"
            ].to_dict()
        )
        self.valid_coefficient_masques_proches_type_masque = list(
            self.coefficient_masques_proches_type_masque.values()
        ) + [None]

    def _preprocess_orientation(self):
        self.orientation = self.orientation.set_index("id")["orientation"].to_dict()
        self.valid_orientation = list(self.orientation.values()) + [None]

    def _preprocess_coefficient_masques_proches(self):
        self.coefficient_masques_proches["coefficient_masques_proches_avance"] = (
            self.coefficient_masques_proches[
                "tv022_coefficient_masques_proches_avance_id"
            ].replace(self.coefficient_masques_proches_avance)
        )
        self.coefficient_masques_proches["coefficient_masques_proches_type_masque"] = (
            self.coefficient_masques_proches[
                "tv022_coefficient_masques_proches_type_masque_id"
            ].replace(self.coefficient_masques_proches_type_masque)
        )
        self.coefficient_masques_proches["orientation"] = (
            self.coefficient_masques_proches["tv0xx_orientation_id"].replace(
                self.orientation
            )
        )
        self.valid_rapport_l1_l2 = list(
            self.coefficient_masques_proches["rapport_l1_l2"].unique()
        )
        self.valid_largeur_baie_superieure = list(
            self.coefficient_masques_proches["largeur_baie_superieure"].unique()
        )
        self.valid_beta_gama = list(
            self.coefficient_masques_proches["beta_gama"].unique()
        ) + [None]

        self.coefficient_masques_proches = (
            self.coefficient_masques_proches.fillna("Null")
            .set_index(
                [
                    "coefficient_masques_proches_type_masque",
                    "coefficient_masques_proches_avance",
                    "orientation",
                    "rapport_l1_l2",
                    "beta_gama",
                ]
            )["id"]
            .to_dict()
        )

    def _preprocess_coefficient_masques_lointains_homogenes_hauteur_alpha(self):
        self.coefficient_masques_lointains_homogenes_hauteur_alpha = (
            self.coefficient_masques_lointains_homogenes_hauteur_alpha.set_index(
                ["id"]
            )["hauteur_alpha"].to_dict()
        )
        self.valid_coefficient_masques_lointains_homogenes_hauteur_alpha = list(
            self.coefficient_masques_lointains_homogenes_hauteur_alpha.values()
        ) + [None]

    def _preprocess_coefficient_masques_lointains_homogenes(self):
        self.coefficient_masques_lointains_homogenes[
            "coefficient_masques_lointains_homogenes_hauteur_alpha"
        ] = self.coefficient_masques_lointains_homogenes[
            "tv023_coefficient_masques_lointains_homogenes_hauteur_alpha_id"
        ].replace(
            self.coefficient_masques_lointains_homogenes_hauteur_alpha
        )
        self.coefficient_masques_lointains_homogenes["orientation"] = (
            self.coefficient_masques_lointains_homogenes[
                "tv0xx_orientation_id"
            ].replace(self.orientation)
        )
        self.coefficient_masques_lointains_homogenes = (
            self.coefficient_masques_lointains_homogenes.set_index(
                ["coefficient_masques_lointains_homogenes_hauteur_alpha", "orientation"]
            )["id"].to_dict()
        )

    def _preprocess_ombrage_obstacle_lointain_hauteur(self):
        self.ombrage_obstacle_lointain_hauteur = (
            self.ombrage_obstacle_lointain_hauteur.set_index("id")["hauteur"].to_dict()
        )
        self.valid_ombrage_obstacle_lointain_hauteur = list(
            self.ombrage_obstacle_lointain_hauteur.values()
        ) + [None]

    def _preprocess_ombrage_obstacle_lointain_secteur(self):
        self.ombrage_obstacle_lointain_secteur = (
            self.ombrage_obstacle_lointain_secteur.set_index("id")["secteur"].to_dict()
        )
        self.valid_ombrage_obstacle_lointain_secteur = list(
            self.ombrage_obstacle_lointain_secteur.values()
        ) + [None]

    def _preprocess_ombrage_obstacle_lointain(self):
        self.ombrage_obstacle_lointain["ombrage_obstacle_lointain_hauteur"] = (
            self.ombrage_obstacle_lointain[
                "tv024_ombrage_obstacle_lointain_hauteur_id"
            ].replace(self.ombrage_obstacle_lointain_hauteur)
        )
        self.ombrage_obstacle_lointain["ombrage_obstacle_lointain_secteur"] = (
            self.ombrage_obstacle_lointain[
                "tv024_ombrage_obstacle_lointain_secteur_id"
            ].replace(self.ombrage_obstacle_lointain_secteur)
        )
        self.ombrage_obstacle_lointain["orientation"] = self.ombrage_obstacle_lointain[
            "tv0xx_orientation_id"
        ].replace(self.orientation)
        self.ombrage_obstacle_lointain = self.ombrage_obstacle_lointain.set_index(
            [
                "ombrage_obstacle_lointain_hauteur",
                "orientation",
                "ombrage_obstacle_lointain_secteur",
            ]
        )["id"].to_dict()

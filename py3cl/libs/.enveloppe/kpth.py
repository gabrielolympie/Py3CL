import pandas as pd
import numpy as np
import os

from libs.utils import safe_divide
from libs.base import BaseProcessor


class KProcessorPth(BaseProcessor):
    def __init__(
        self,
        data_path="../data/raw",
    ):
        super().__init__(data_path)

    @property
    def calc_input(self):
        return {
            "type_liaison": self.valid_type_liaison,
            "isolation_mur": self.valid_isolation_mur,
            "isolation_plancher": self.valid_isolation_plancher,
            "type_pose": self.valid_type_pose,
            "retour_isolation": self.valid_retour_isolation,
        }

    def calc(
        self,
        type_liaison: str = None,
        isolation_mur: str = None,
        isolation_plancher: str = None,
        largeur_dormant: float = None,
        type_pose: str = None,
        retour_isolation: str = None,
        *args,
        **kwargs,
    ) -> float:
        """Calcule le coefficient de déperdition thermique pour un pont thermique, en W/(m.K)

        !Warning! : For plancher bas, intermediaire and refend, only heavy material are counted in thermal bridge

        Check the valid argument values with self.calc_input

        Args:
            - type_liaison (str): Type de liaison
            - isolation_mur (str): Isolation du mur
            - isolation_plancher (str): Isolation du plancher
            - largeur_dormant (float): Largeur du dormant (only for menuiserie)
            - type_pose (str): Type de pose (only for menuiserie)
            - retour_isolation (str): Retour d'isolation (only for menuiserie)
        """
        self.validate(
            type_liaison=type_liaison,
            isolation_mur=isolation_mur,
            isolation_plancher=isolation_plancher,
            type_pose=type_pose,
            retour_isolation=retour_isolation,
        )

        if type_liaison == "Menuiserie / Mur":
            assert largeur_dormant is not None, "largeur_dormant must be provided"
            assert type_pose is not None, "type_pose must be provided"
            assert retour_isolation is not None, "retour_isolation must be provided"
            return self._calc_k_menuiserie(
                type_liaison,
                isolation_mur,
                largeur_dormant,
                type_pose,
                retour_isolation,
            )
        elif type_liaison == "Menuiserie / Plancher haut":
            return 0
        elif type_liaison == "Plancher intermédiaire lourd / Mur":
            return self._calc_k_plancher_intermediaire(type_liaison, isolation_mur)
        else:
            assert isolation_plancher is not None, "isolation_plancher must be provided"
            return self._calc_k(type_liaison, isolation_mur, isolation_plancher)

    def _calc_k(
        self,
        type_liaison: str,
        isolation_mur: str,
        isolation_plancher: str,
    ):
        """
        Calcule le coefficient de transmission thermique pour une paroi
        """
        return self.valeur_pth[(type_liaison, isolation_mur, isolation_plancher)]

    def _calc_k_plancher_intermediaire(
        self,
        type_liaison: str,
        isolation_mur: str,
    ):
        """Calcule le coefficient de transmission thermique pour un plancher intermediaire

        Args:
            - type_liaison (str): Type de liaison
            - isolation_plancher (str): Isolation du plancher
        """
        return self._calc_k(type_liaison, isolation_mur, "NULL")

    def _calc_k_menuiserie(
        self,
        type_liaison: str,
        isolation_mur: str,
        largeur_dormant: float,
        type_pose: str,
        retour_isolation: str,
    ):
        """
        Calcule le coefficient de transmission thermique pour une menuiserie
        """
        ## Check if largeur is closer to 5 or 10
        largeur_dormant = 5 if abs(largeur_dormant - 5) < abs(largeur_dormant - 10) else 10
        return self.valeur_pth_menuiserie[(type_liaison, isolation_mur, largeur_dormant, type_pose, retour_isolation)]

    def load(
        self,
        data_path,
        valeur_pont_thermique_isolation_mur="tv013_valeur_pont_thermique_isolation_mur.csv",
        valeur_pont_thermique_isolation_plancher="tv013_valeur_pont_thermique_isolation_plancher_bas.csv",
        valeur_pont_thermique_retour_isolation="tv013_valeur_pont_thermique_retour_isolation.csv",
        valeur_pont_thermique_type_liaison="tv013_valeur_pont_thermique_type_liaison.csv",
        valeur_pont_thermique_type_pose="tv013_valeur_pont_thermique_type_pose.csv",
        valeur_pont_thermique="tv013_valeur_pont_thermique.csv",
    ):
        """
        Load data from data_path
        """
        self.valeur_pont_thermique_isolation_mur = pd.read_csv(
            os.path.join(data_path, valeur_pont_thermique_isolation_mur)
        )
        self.valeur_pont_thermique_isolation_plancher = pd.read_csv(
            os.path.join(data_path, valeur_pont_thermique_isolation_plancher)
        )
        self.valeur_pont_thermique_retour_isolation = pd.read_csv(
            os.path.join(data_path, valeur_pont_thermique_retour_isolation)
        )
        self.valeur_pont_thermique_type_liaison = pd.read_csv(
            os.path.join(data_path, valeur_pont_thermique_type_liaison)
        )
        self.valeur_pont_thermique_type_pose = pd.read_csv(os.path.join(data_path, valeur_pont_thermique_type_pose))
        self.valeur_pont_thermique = pd.read_csv(os.path.join(data_path, valeur_pont_thermique))

    def preprocess(
        self,
    ):
        """
        Preprocess data for further computation
        """
        self._preprocess_valeur_pont_thermique_isolation_mur()
        self._preprocess_valeur_pont_thermique_isolation_plancher()
        self._preprocess_valeur_pont_thermique_retour_isolation()
        self._preprocess_valeur_pont_thermique_type_liaison()
        self._preprocess_valeur_pont_thermique_type_pose()
        self._preprocess_valeur_pont_thermique()

    def _preprocess_valeur_pont_thermique_isolation_mur(self):
        self.valeur_pont_thermique_isolation_mur = self.valeur_pont_thermique_isolation_mur.set_index("id")[
            "isolation_mur"
        ].to_dict()
        self.valid_isolation_mur = list(self.valeur_pont_thermique_isolation_mur.values())

    def _preprocess_valeur_pont_thermique_isolation_plancher(self):
        self.valeur_pont_thermique_isolation_plancher = self.valeur_pont_thermique_isolation_plancher.set_index("id")[
            "plancher_bas"
        ].to_dict()
        self.valid_isolation_plancher = list(self.valeur_pont_thermique_isolation_plancher.values())

    def _preprocess_valeur_pont_thermique_retour_isolation(self):
        self.valeur_pont_thermique_retour_isolation = self.valeur_pont_thermique_retour_isolation.set_index("id")[
            "retour_isolation"
        ].to_dict()
        self.valid_retour_isolation = list(self.valeur_pont_thermique_retour_isolation.values())

    def _preprocess_valeur_pont_thermique_type_liaison(self):
        self.valeur_pont_thermique_type_liaison = self.valeur_pont_thermique_type_liaison.set_index("id")[
            "type_liaison"
        ].to_dict()
        self.valid_type_liaison = list(self.valeur_pont_thermique_type_liaison.values())

    def _preprocess_valeur_pont_thermique_type_pose(self):
        self.valeur_pont_thermique_type_pose = self.valeur_pont_thermique_type_pose.set_index("id")[
            "type_pose"
        ].to_dict()
        self.valid_type_pose = list(self.valeur_pont_thermique_type_pose.values())

    def _preprocess_valeur_pont_thermique(self):
        self.valeur_pont_thermique["type_liaison"] = self.valeur_pont_thermique[
            "tv013_valeur_pont_thermique_type_liaison_id"
        ].replace(self.valeur_pont_thermique_type_liaison)
        self.valeur_pont_thermique["largeur_dormant"] = self.valeur_pont_thermique["largeur_dormant"].replace(
            {"NULL": np.nan}
        )

        self.valeur_pont_thermique["isolation_mur"] = self.valeur_pont_thermique[
            "tv013_valeur_pont_thermique_isolation_mur_id"
        ].replace(self.valeur_pont_thermique_isolation_mur)
        self.valeur_pont_thermique["plancher"] = self.valeur_pont_thermique[
            "tv013_valeur_pont_thermique_isolation_plancher_bas_id"
        ].replace(self.valeur_pont_thermique_isolation_plancher)

        ## Drop value different from nan
        self.valeur_pth_menuiserie = self.valeur_pont_thermique[
            self.valeur_pont_thermique["largeur_dormant"].notna()
        ].copy()
        self.valeur_pth = self.valeur_pont_thermique[self.valeur_pont_thermique["largeur_dormant"].isna()].copy()

        ## Prepare general case:
        self.valeur_pth = self.valeur_pth.set_index(["type_liaison", "isolation_mur", "plancher"], drop=True)[
            "k"
        ].to_dict()

        ## Prepare menuiserie case:
        print(self.valeur_pth_menuiserie["tv013_valeur_pont_thermique_type_pose_id"].unique())
        self.valeur_pth_menuiserie["type_pose"] = (
            self.valeur_pth_menuiserie["tv013_valeur_pont_thermique_type_pose_id"]
            .astype(int)
            .replace(self.valeur_pont_thermique_type_pose)
        )
        self.valeur_pth_menuiserie["retour_isolation"] = self.valeur_pth_menuiserie[
            "tv013_valeur_pont_thermique_retour_isolation_id"
        ].replace(self.valeur_pont_thermique_retour_isolation)
        self.valeur_pth_menuiserie = self.valeur_pth_menuiserie.set_index(
            [
                "type_liaison",
                "isolation_mur",
                "largeur_dormant",
                "type_pose",
                "retour_isolation",
            ],
            drop=True,
        )["k"].to_dict()

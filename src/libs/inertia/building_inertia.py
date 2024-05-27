import pandas as pd
import numpy as np
import os

from libs.utils import safe_divide
from libs.base import BaseProcessor


class InertiaProcessor(BaseProcessor):
    def __init__(
        self,
        data_path="../data/raw",
    ):
        super().__init__(data_path)

    @property
    def calc_input(self):
        return {
            "classe_inertie_plancher_bas": self.valid_classe_inertie_plancher_bas,
            "classe_inertie_paroi_verticale": self.valid_classe_inertie_paroi_verticale,
            "classe_inertie_plancher_haut": self.valid_classe_inertie_plancher_haut,
        }

    def calc(
        self,
        classe_inertie_plancher_bas: str = None,
        classe_inertie_paroi_verticale: str = None,
        classe_inertie_plancher_haut: str = None,
        *args,
        **kwargs,
    ) -> float:
        """
        Based on the classe_inertie_plancher_bas, classe_inertie_paroi_verticale, classe_inertie_plancher_haut,
        computes the whole building inertia class

        Args:
        - classe_inertie_plancher_bas: str
        - classe_inertie_paroi_verticale: str
        - classe_inertie_plancher_haut: str
        """
        self.validate(
            classe_inertie_plancher_bas=classe_inertie_plancher_bas,
            classe_inertie_paroi_verticale=classe_inertie_paroi_verticale,
            classe_inertie_plancher_haut=classe_inertie_plancher_haut,
        )
        return self.classe_inerties[
            (
                classe_inertie_plancher_bas,
                classe_inertie_paroi_verticale,
                classe_inertie_plancher_haut,
            )
        ]

    def load(
        self,
        data_path,
        classe_inertie_type="tv026_classe_inertie_type.csv",
        classe_inerties="tv026_classe_inertie.csv",
    ):
        """
        Load data from data_path
        """
        self.classe_inertie_type = pd.read_csv(
            os.path.join(data_path, classe_inertie_type)
        )
        self.classe_inerties = pd.read_csv(os.path.join(data_path, classe_inerties))

    def preprocess(
        self,
    ):
        """
        Preprocess data for further computation
        """
        self._preprocess_classe_inertie_type()
        self._preprocess_classe_inerties()

    def _preprocess_classe_inertie_type(self):
        """
        Preprocess classe_inertie_type
        """
        self.classe_inertie_type = self.classe_inertie_type.set_index("id")[
            "type"
        ].to_dict()

    def _preprocess_classe_inerties(self):
        """
        Preprocess classe_inerties
        """
        self.classe_inerties["classe_inertie_plancher_bas"] = self.classe_inerties[
            "tv026_classe_inertie_plancher_bas_id"
        ].replace(self.classe_inertie_type)
        self.classe_inerties["classe_inertie_paroi_verticale"] = self.classe_inerties[
            "tv026_classe_inertie_paroi_verticale_id"
        ].replace(self.classe_inertie_type)
        self.classe_inerties["classe_inertie_plancher_haut"] = self.classe_inerties[
            "tv026_classe_inertie_plancher_haut_id"
        ].replace(self.classe_inertie_type)
        self.classe_inerties["classe_inertie_classe_inertie"] = self.classe_inerties[
            "tv026_classe_inertie_classe_inertie_id"
        ].replace(self.classe_inertie_type)

        self.valid_classe_inertie_plancher_bas = self.classe_inerties[
            "classe_inertie_plancher_bas"
        ].unique()
        self.valid_classe_inertie_paroi_verticale = self.classe_inerties[
            "classe_inertie_paroi_verticale"
        ].unique()
        self.valid_classe_inertie_plancher_haut = self.classe_inerties[
            "classe_inertie_plancher_haut"
        ].unique()

        self.classe_inerties = self.classe_inerties.set_index(
            [
                "classe_inertie_plancher_bas",
                "classe_inertie_paroi_verticale",
                "classe_inertie_plancher_haut",
            ]
        )["classe_inertie_classe_inertie"].to_dict()

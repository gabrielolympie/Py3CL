import pandas as pd
import numpy as np
import os

from libs.utils import safe_divide
from libs.base import BaseProcessor


class UParoiProcessorPh(BaseProcessor):
    def __init__(
        self,
        data_path="../data/raw",
        uparoi_table="tv007_uph.csv",
        uparoi0="tv008_uph0.csv",
        uparoi_materiaux="tv007_uph_type_toit.csv",
    ):
        super().__init__(data_path)

    @property
    def calc_input(self):
        return {
            "materiaux": list(self.valid_ph_materiaux),
            "type_toit": list(self.valid_ph_type),
            "zone_climatique": ["H1", "H2", "H3"],
            "effet_joule": [0, 1],
        }

    def calc(
        self,
        uparoi=None,
        materiaux=None,
        type_toit=None,
        annee_construction=None,
        isolation=None,
        r_isolant=None,
        epaisseur_isolant=None,
        annee_isolation=None,
        zone_climatique=None,
        effet_joule=None,
        *args,
        **kwargs,
    ) -> float:
        """Calcule l'uparoi en fonction des paramètres

        Args:
            - uparoi (float): uparoi, if known, it will be the value used
            - materiaux (str): Materiaux de la paroi, canbe listed with the property valid_ph_materiaux
            - type_toit (str): Type de toit, see valid_ph_type
            - annee_construction (float): Année de construction
            - isolation (bool): Isolation, if known
            - r_isolant (float): R de l'isolant
            - epaisseur_isolant (float): Epaisseur de l'isolant
            - annee_isolation (float): Année d'isolation
            - zone_climatique (str): Zone climatique, in ['H1', 'H2', 'H3']
            - effet_joule (float): Effet joule, in [0, 1], is computation is for isolation, put zero. Is computation is for construction and heating is done with electricity, then put 1
        """
        self.validate(
            materiaux=materiaux,
            type_toit=type_toit,
            zone_climatique=zone_climatique,
            effet_joule=effet_joule,
        )
        if materiaux == "Inconnu":
            materiaux = None

        if uparoi:
            return uparoi

        if materiaux:
            uparoi_0 = self._calc_uparoi_0(materiaux)
            uparoi_nu = min(uparoi_0, 2.5)
        else:
            uparoi_nu = 2.5

        if isolation is None:
            uparoi_table = self._calc_uparoi_table(type_toit, annee_construction, zone_climatique, effet_joule)
            return min(uparoi_nu, uparoi_table)
        elif isolation is False:
            return uparoi_nu
        else:
            if r_isolant is not None:
                return self._calc_harmonic_mean(uparoi_nu, r_isolant)
            elif epaisseur_isolant is not None:
                ## Todo : verifier que le calcul est correct (0.04 dans le doc est-il en mètre ou cm ?)
                r_isolant = epaisseur_isolant / 40
                return self._calc_harmonic_mean(uparoi_nu, r_isolant)
            else:
                assert (
                    zone_climatique is not None
                ), "zone_climatique is required in uparoi calculation if isolation is not known"
                if annee_isolation is None:
                    if annee_construction is None:
                        annee_isolation = 70
                    if annee_construction <= 74:
                        annee_isolation = 76
                    else:
                        annee_isolation = annee_construction
                uparoi_table = self._calc_uparoi_table(annee_isolation, zone_climatique, 1)
                return min(uparoi_nu, uparoi_table)

    def _calc_uparoi_table(
        self,
        type_toit: str = None,
        annee_construction_isolation: float = None,
        zone_climatique: str = None,
        effet_joule: float = None,
    ) -> float:
        """Calcule l'uparoi en fonction de l'année de construction, de la zone climatique et de l'effet joule

        Args:
            - type_toit (str): Type de toit, see valid_ph_type
            - annee_construction_isolation (float): Année de construction ou d'isolation
            - zone_climatique (str): Zone climatique, in ['H1', 'H2', 'H3']
            - effet_joule (float): Effet joule, in [0, 1], is computation is for isolation, put zero. Is computation is for construction and heating is done with electricity, then put 1
        """
        assert type_toit is not None, "type_toit is required in uparoi table calculation"
        assert type_toit in self.valid_ph_type, f"type_toit should be in {self.valid_ph_type}"
        assert (
            annee_construction_isolation is not None
        ), "anne_construction_isolation is required in uparoi table calculation"
        assert zone_climatique in [
            "H1",
            "H2",
            "H3",
        ], "zone_climatique is required in uparoi table calculation and with a value in ['H1', 'H2', 'H3']"
        assert effet_joule is not None, "effet_joule is required in uparoi table calculation"

        idx_year = np.where(annee_construction_isolation <= self.uparoi_table_max_years)[0][0]
        year = self.uparoi_table_max_years[idx_year]
        uparoi_0 = self.uparoi_table.loc[(type_toit, year, zone_climatique, effet_joule)]
        return uparoi_0

    def _calc_harmonic_mean(self, uparoi_nu: float = None, r_isolant: float = None) -> float:
        """Calcule la moyenne harmonique entre l'uparoi nu et l'uparoi de l'isolant

        Args:
            - uparoi_nu (float): uparoi nu
            - r_isolant (float): R de l'isolant
        """
        assert uparoi_nu is not None, "uparoi_nu is required in harmonic mean calculation"
        assert r_isolant is not None, "r_isolant is required in harmonic mean calculation"
        return 1 / (1 / uparoi_nu + r_isolant)

    def _calc_uparoi_0(
        self,
        materiaux: str = None,
    ) -> float:
        """Calcule l'uparoi0 en fonction du materiaux et de l'épaisseur

        Args:
            - materiaux (str): Materiaux de la paroi
        """
        assert materiaux is not None, "materiaux is required in uparoi0 calculation"
        assert materiaux in self.valid_ph_materiaux, f"materiaux should be in {self.valid_ph_materiaux}"

        return self.uparoi0.loc[materiaux]

    def load(
        self,
        data_path,
        uparoi_table="tv007_uph.csv",
        uparoi0="tv008_uph0.csv",
        uparoi_materiaux="tv007_uph_type_toit.csv",
    ):
        """
        Load data from data_path
        """
        self.uparoi_table = pd.read_csv(os.path.join(data_path, uparoi_table))
        self.uparoi0 = pd.read_csv(os.path.join(data_path, uparoi0))
        self.uparoi_materiaux = pd.read_csv(os.path.join(data_path, uparoi_materiaux))

    def preprocess(
        self,
    ):
        """
        Preprocess data for further computation
        """
        self._preprocess_uparoi_materiaux()
        self._preprocess_uparoi_table()
        self._preprocess_uparoi0()

    def _preprocess_uparoi_materiaux(self):
        self.valid_ph_type = self.uparoi_materiaux["type_toit"].unique()
        self.type_toit_id = self.uparoi_materiaux.set_index("id", drop=True)["type_toit"].to_dict()

    def _preprocess_uparoi0(self):
        self.valid_ph_materiaux = self.uparoi0["materiaux"].unique()
        # self.uparoi0['materiaux']=self.uparoi0['tv004_umur0_materiaux_id'].replace(self.materiaux_id)
        self.uparoi0 = self.uparoi0.set_index(["materiaux"], drop=True)["uph0"]

    def _preprocess_uparoi_table(self):
        self.uparoi_table = self.uparoi_table.dropna(subset="annee_construction")
        self.uparoi_table["zone_climatique"] = self.uparoi_table["tv017_zone_hiver_id"].replace(
            {1: "H1", 2: "H2", 3: "H3"}
        )
        self.uparoi_table["type_toit"] = self.uparoi_table["tv007_uph_type_toit_id"].replace(self.type_toit_id)
        self.uparoi_table_max_years = self.uparoi_table["annee_construction_max"].sort_values().unique()
        self.uparoi_table = self.uparoi_table.set_index(
            ["type_toit", "annee_construction_max", "zone_climatique", "effet_joule"],
            drop=True,
        )["uph"]

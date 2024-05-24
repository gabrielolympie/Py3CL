import pandas as pd
import numpy as np
import os

from scipy.interpolate import RegularGridInterpolator
from libs.utils import safe_divide
from libs.base import BaseProcessor


class UParoiProcessorPb(BaseProcessor):
    def __init__(
        self,
        data_path="../data/raw",
        uparoi_table="tv005_upb.csv",
        uparoi0="tv006_upb0.csv",
        uparoi_materiaux="tv006_upb0.csv",  ## Keeping it for consistency
        abaque_file="vide_sanitaire.xlsx",
        abaque_names=["other", "tp_pre_2001", "tp_post_2001"],
    ):
        super().__init__(data_path)

    @property
    def calc_input(self):
        return {
            "materiaux": list(self.valid_pb_materials),
            "isolation": [True, False],
            "zone_climatique": ["H1", "H2", "H3"],
            "effet_joule": [0, 1],
            "is_vide_sanitaire": [True, False],
            "is_unheated_underground": [True, False],
            "is_terre_plain": [True, False],
        }

    def calc(
        self,
        uparoi=None,
        materiaux=None,
        epaisseur=None,
        annee_construction=None,
        isolation=None,
        r_isolant=None,
        epaisseur_isolant=None,
        annee_isolation=None,
        zone_climatique=None,
        effet_joule=None,
        is_vide_sanitaire=False,
        is_unheated_underground=False,
        is_terre_plain=False,
        surface_immeuble=None,
        perimeter_immeuble=None,
        *args,
        **kwargs,
    ) -> float:
        """Calcule l'uparoi en fonction des paramètres

        Args:
            - uparoi (float): uparoi, if known, it will be the value used
            - materiaux (str): Materiaux de la paroi, canbe listed with the property valid_pb_materials
            - epaisseur (float): Epaisseur de la paroi in centimeters
            - annee_construction (float): Année de construction
            - isolation (bool): Isolation, if known
            - r_isolant (float): R de l'isolant
            - epaisseur_isolant (float): Epaisseur de l'isolant
            - annee_isolation (float): Année d'isolation
            - zone_climatique (str): Zone climatique, in ['H1', 'H2', 'H3']
            - effet_joule (float): Effet joule, in [0, 1], is computation is for isolation, put zero. Is computation is for construction and heating is done with electricity, then put 1
            - is_vide_sanitaire (bool): if the underground is a vide sanitaire
            - is_unheated_underground (bool): if the underground is unheated
            - is_terre_plain (bool): if the underground is terre plain
            - surface_immeuble (float): Surface de l'immeuble (should englobe the whole building sharing the terre plain / vide sanitaire / underground)
            - perimeter_immeuble (float): Perimeter de l'immeuble (should englobe the whole building sharing the terre plain / vide sanitaire / underground)

        """
        self.validate(
            materiaux=materiaux,
            zone_climatique=zone_climatique,
            effet_joule=effet_joule,
            is_vide_sanitaire=is_vide_sanitaire,
            is_unheated_underground=is_unheated_underground,
            is_terre_plain=is_terre_plain,
        )
        upb = self._calc(
            uparoi=uparoi,
            materiaux=materiaux,
            epaisseur=epaisseur,
            annee_construction=annee_construction,
            isolation=isolation,
            r_isolant=r_isolant,
            epaisseur_isolant=epaisseur_isolant,
            annee_isolation=annee_isolation,
            zone_climatique=zone_climatique,
            effet_joule=effet_joule,
        )

        upb = self._calc_underground(
            uparoi=upb,
            annee_construction=annee_construction,
            is_vide_sanitaire=is_vide_sanitaire,
            is_unheated_underground=is_unheated_underground,
            is_terre_plain=is_terre_plain,
            surface_immeuble=surface_immeuble,
            perimeter_immeuble=perimeter_immeuble,
        )
        return upb

    def _calc_underground(
        self,
        uparoi: float = None,
        annee_construction: float = None,
        is_vide_sanitaire: bool = False,
        is_unheated_underground: bool = False,
        is_terre_plain: bool = False,
        surface_immeuble: bool = None,
        perimeter_immeuble: bool = None,
    ):

        if is_vide_sanitaire or is_unheated_underground or is_terre_plain:
            assert (
                surface_immeuble is not None
            ), "surface_immeuble is required for underground, vide sanitaire and terre plain"
            assert (
                perimeter_immeuble is not None
            ), "perimeter_immeuble is required for underground, vide sanitaire and terre plain"
            ssp = 2 * surface_immeuble / perimeter_immeuble

            if is_vide_sanitaire or is_unheated_underground:
                return self.abaque["other"]([ssp, uparoi])[0]
            elif is_terre_plain:
                assert annee_construction is not None, "annee_construction is required for terre plain"
                if annee_construction < 2001:
                    return self.abaque["tp_pre_2001"]([ssp, uparoi])[0]
                else:
                    return self.abaque["tp_post_2001"]([ssp, uparoi])[0]
        return uparoi

    @property
    def calc_input(self):
        return {
            "materiaux": self.valid_pb_materials,
            "isolation": [True, False],
            "zone_climatique": ["H1", "H2", "H3"],
            "effet_joule": [0, 1],
            "is_vide_sanitaire": [True, False],
            "is_unheated_underground": [True, False],
            "is_terre_plain": [True, False],
        }

    def _calc(
        self,
        uparoi=None,
        materiaux=None,
        epaisseur=None,
        annee_construction=None,
        isolation=None,
        r_isolant=None,
        epaisseur_isolant=None,
        annee_isolation=None,
        zone_climatique=None,
        effet_joule=None,
    ) -> float:
        """Calcule l'uparoi en fonction des paramètres

        Args:
            - uparoi (float): uparoi, if known, it will be the value used
            - materiaux (str): Materiaux de la paroi, canbe listed with the property valid_pb_materials
            - epaisseur (float): Epaisseur de la paroi in centimeters, unused anyways
            - annee_construction (float): Année de construction
            - isolation (bool): Isolation, if known
            - r_isolant (float): R de l'isolant
            - epaisseur_isolant (float): Epaisseur de l'isolant
            - annee_isolation (float): Année d'isolation
            - zone_climatique (str): Zone climatique, in ['H1', 'H2', 'H3']
            - effet_joule (float): Effet joule, in [0, 1], is computation is for isolation, put zero. Is computation is for construction and heating is done with electricity, then put 1
        """
        epaisseur = 1
        if materiaux == "Inconnu":
            materiaux = None

        if uparoi:
            return uparoi

        if materiaux and epaisseur:
            uparoi_0 = self._calc_uparoi_0(materiaux, epaisseur)
            uparoi_nu = min(uparoi_0, 2.0)
        else:
            uparoi_nu = 2.0

        if isolation is None:
            assert (
                annee_construction is not None
            ), "annee_construction is required in uparoi calculation if isolation is not known"
            assert (
                zone_climatique is not None
            ), "zone_climatique is required in uparoi calculation if isolation is not known"
            assert effet_joule is not None, "effet_joule is required in uparoi calculation if isolation is not known"
            uparoi_table = self._calc_uparoi_table(annee_construction, zone_climatique, effet_joule)
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
        annee_construction_isolation: float = None,
        zone_climatique: str = None,
        effet_joule: float = None,
        enduit: bool = False,
        doublage_with_lame_below_15mm: bool = False,
        doublage_with_lame_above_15mm: bool = False,
    ) -> float:
        """Calcule l'uparoi en fonction de l'année de construction, de la zone climatique et de l'effet joule

        Args:
            - annee_construction_isolation (float): Année de construction ou d'isolation
            - zone_climatique (str): Zone climatique, in ['H1', 'H2', 'H3']
            - effet_joule (float): Effet joule, in [0, 1], is computation is for isolation, put zero. Is computation is for construction and heating is done with electricity, then put 1
            - enduit (bool): Enduit, if True, then the value will be used
            - doublage_with_lame_below_15mm (bool): Doublage with lame below 15mm, if True, then the value will be used
            - doublage_with_lame_above_15mm (bool): Doublage with lame above 15mm, if True, then the value will be used
        """

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
        uparoi_0 = self.uparoi_table.loc[(year, zone_climatique, effet_joule)]
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

    def _calc_uparoi_0(self, materiaux: str = None, epaisseur: float = None) -> float:
        """Calcule l'uparoi0 en fonction du materiaux et de l'épaisseur

        Args:
            - materiaux (str): Materiaux de la paroi
            - epaisseur (float): Epaisseur de la paroi in centimeters
        """
        assert materiaux is not None, "materiaux is required in uparoi0 calculation"
        assert epaisseur is not None, "epaisseur is required in uparoi0 calculation"
        assert materiaux in self.valid_pb_materials, f"materiaux should be in {self.valid_pb_materials}"

        tresholds = self.uparoi_tresholds[materiaux]
        idx = np.where(min(epaisseur, tresholds[-1]) <= tresholds)[0][0]
        return self.uparoi0.loc[(materiaux, tresholds[idx])]

    def load(
        self,
        data_path,
        uparoi_table="tv005_upb.csv",
        uparoi0="tv006_upb0.csv",
        uparoi_materiaux="tv006_upb0.csv",  ## Keeping it for consistency
        abaque_file="vide_sanitaire.xlsx",
        abaque_names=["other", "tp_pre_2001", "tp_post_2001"],
    ):
        """
        Load data from data_path
        """
        self.uparoi_table = pd.read_csv(os.path.join(data_path, uparoi_table))
        self.uparoi0 = pd.read_csv(os.path.join(data_path, uparoi0))
        self.abaque = {
            elt: pd.read_excel(os.path.join(data_path, abaque_file), sheet_name=elt, index_col=0)
            for elt in abaque_names
        }

    def preprocess(
        self,
    ):
        """
        Preprocess data for further computation
        """
        self._preprocess_uparoi_table()
        self._preprocess_uparoi0()

        self.abaque = {k: self._preprocess_abaque(v) for k, v in self.abaque.items()}

    def _preprocess_abaque(self, abaque):
        row_headers = abaque.index
        column_headers = abaque.columns
        table_data = abaque.values
        interpolator = RegularGridInterpolator(
            (row_headers, column_headers),
            table_data,
            bounds_error=False,
            fill_value=None,
        )
        return interpolator

    def _preprocess_uparoi0(self):
        # self.uparoi0['materiaux']=self.uparoi0['tv004_uparoi0_materiaux_id'].replace(self.materiaux_id)
        self.valid_pb_materials = self.uparoi0["materiaux"].unique()
        self.uparoi0["epaisseur"] = 1
        self.uparoi_tresholds = (
            self.uparoi0[["materiaux", "epaisseur"]].groupby("materiaux").agg(lambda x: list(x))["epaisseur"].to_dict()
        )
        self.uparoi_tresholds = {k: np.array(sorted(v)) for k, v in self.uparoi_tresholds.items()}
        self.uparoi0 = self.uparoi0.set_index(["materiaux", "epaisseur"], drop=True)["upb0"]

    def _preprocess_uparoi_table(self):
        self.uparoi_table = self.uparoi_table.dropna(subset="annee_construction")
        self.uparoi_table["zone_climatique"] = self.uparoi_table["tv017_zone_hiver_id"].replace(
            {1: "H1", 2: "H2", 3: "H3"}
        )
        self.uparoi_table_max_years = self.uparoi_table["annee_construction_max"].sort_values().unique()
        self.uparoi_table = self.uparoi_table.set_index(
            ["annee_construction_max", "zone_climatique", "effet_joule"], drop=True
        )["upb"]

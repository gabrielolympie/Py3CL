import pandas as pd
import numpy as np
import os

from libs.utils import safe_divide
from libs.base import BaseProcessor


class DRProcessor(BaseProcessor):
    def __init__(
        self,
        data_path="../data/raw",
    ):
        super().__init__(data_path)

    @property
    def calc_input(self):
        return {
            "type_ventilation": self.valid_type_ventilation,
            "type_batiment": self.valid_type_batiment,
        }

    def calc(
        self,
        type_ventilation: str,
        surface_habitable: float,
        q4paconv: float = None,
        type_batiment: str = None,
        annee_construction: int = None,
        surface_paroir_deperditive_hors_ps: float = None,
        ratio_isolated_surface: float = None,
        menuiserie_has_join: bool = None,
        hauteur_sous_plafond: float = None,
        nb_facade_exposee: int = None,
        *args,
        **kwargs,
    ) -> float:
        """Calcule le débit de renouvellement d'air pour une habitation, W/K

        Args:
            - type_ventilation (str): Type de ventilation, look for input validation for available options
            - surface_habitable (float): Surface habitable in square meters
            - q4paconv (float): Débit de renouvellement d'air conventionnel, optional, if known, will override computed values
            - type_batiment (str): Type de bâtiment, look for input validation for available options
            - annee_construction (int): Année de construction of the building
            - surface_paroir_deperditive_hors_ps (float): Surface de paroi déperditive hors plancher bas, in square meters
            - ratio_isolated_surface (float): Ratio de surface isolée ratio between isolated area and total deperditive area
            - menuiserie_has_join (bool): Présence of joint pour les menuiseries
            - hauteur_sous_plafond (float): Hauteur sous plafond, in meters
            - nb_facade_exposee (int): Nombre de façades exposées
        """
        self.validate(
            type_ventilation=type_ventilation,
            type_batiment=type_batiment,
        )

        h_vent = self._calc_h_vent(type_ventilation, surface_habitable)
        h_perm = self._calc_h_perm(
            q4paconv=q4paconv,
            type_ventilation=type_ventilation,
            type_batiment=type_batiment,
            annee_construction=annee_construction,
            surface_paroir_deperditive_hors_ps=surface_paroir_deperditive_hors_ps,
            ratio_isolated_surface=ratio_isolated_surface,
            menuiserie_has_join=menuiserie_has_join,
            hauteur_sous_plafond=hauteur_sous_plafond,
            surface_habitable=surface_habitable,
            nb_facade_exposee=nb_facade_exposee,
        )
        return h_vent + h_perm

    def _calc_h_vent(self, type_ventilation, surface_habitable):
        assert (
            type_ventilation in self.valid_type_ventilation
        ), f"type_ventilation must be in {self.valid_type_ventilation}"
        return 0.34 * self.qvarepconv[type_ventilation] * surface_habitable

    def _calc_h_perm(
        self,
        q4paconv: float = None,
        type_ventilation: str = None,
        type_batiment: str = None,
        annee_construction: int = None,
        surface_paroir_deperditive_hors_ps: float = None,
        ratio_isolated_surface: float = None,
        menuiserie_has_join: bool = None,
        hauteur_sous_plafond: float = None,
        surface_habitable: float = None,
        nb_facade_exposee: int = None,
    ):
        nu_50 = self._calc_nu_50(
            q4paconv=q4paconv,
            type_ventilation=type_ventilation,
            type_batiment=type_batiment,
            annee_construction=annee_construction,
            surface_paroir_deperditive_hors_ps=surface_paroir_deperditive_hors_ps,
            ratio_isolated_surface=ratio_isolated_surface,
            menuiserie_has_join=menuiserie_has_join,
            hauteur_sous_plafond=hauteur_sous_plafond,
            surface_habitable=surface_habitable,
        )
        e, f = self._calc_e_f(nb_facade_exposee)
        qvasoufconv = self.qvasoufconv[type_ventilation]
        qvarepconv = self.qvarepconv[type_ventilation]

        qvinf_num = hauteur_sous_plafond * surface_habitable * nu_50 * e
        qvinf_den = (
            1
            + (f / e)
            * (qvasoufconv - qvarepconv) ** 2
            / (hauteur_sous_plafond * nu_50) ** 2
        )
        qvinf = qvinf_num / qvinf_den
        return 0.34 * qvinf

    def _calc_nu_50(
        self,
        q4paconv: float = None,
        type_ventilation: str = None,
        type_batiment: str = None,
        annee_construction: int = None,
        surface_paroir_deperditive_hors_ps: float = None,
        ratio_isolated_surface: float = None,
        menuiserie_has_join: bool = None,
        hauteur_sous_plafond: float = None,
        surface_habitable: float = None,
    ):
        q4pa = self._calc_q4pa(
            q4paconv=q4paconv,
            type_ventilation=type_ventilation,
            type_batiment=type_batiment,
            annee_construction=annee_construction,
            surface_paroir_deperditive_hors_ps=surface_paroir_deperditive_hors_ps,
            ratio_isolated_surface=ratio_isolated_surface,
            menuiserie_has_join=menuiserie_has_join,
        )

        nu_50 = q4pa / ((4 / 50) ** (2 / 3) * hauteur_sous_plafond * surface_habitable)
        return nu_50

    def _calc_q4pa(
        self,
        q4paconv: float = None,
        type_ventilation: str = None,
        type_batiment: str = None,
        annee_construction: int = None,
        surface_paroir_deperditive_hors_ps: float = None,
        ratio_isolated_surface: float = None,
        menuiserie_has_join: bool = None,
    ):
        if q4paconv is None:
            if annee_construction < 1948 and ratio_isolated_surface > 0.5:
                q4paconv = 2
            elif (
                annee_construction >= 1948
                and annee_construction < 1974
                and ratio_isolated_surface <= 0.5
            ):
                q4paconv = 1.9
            elif annee_construction <= 1948 and menuiserie_has_join:
                q4paconv = 2.5
            else:
                q4paconv = self._calc_q4paconv(type_batiment, annee_construction)
        smeaconv = self.smeaconv[type_ventilation]
        return q4paconv + 0.45 * smeaconv * surface_paroir_deperditive_hors_ps

    def _calc_q4paconv(self, type_batiment, annee_construction):
        assert (
            type_batiment in self.valid_type_batiment
        ), f"type_batiment must be in {self.valid_type_batiment}"
        idx = np.where(annee_construction <= self.year_tresholds)[0][0]
        return self.permeabililte[(type_batiment, self.year_tresholds[idx])]

    def _calc_e_f(self, nb_facade_exposee):
        if nb_facade_exposee == 1:
            return 0.02, 20
        else:
            return 0.07, 15

    def load(
        self,
        data_path,
        permeabililte="tv014_bis_permeabilite.csv",
        valeur_conventionnelle_renouvellement_air="tv015_bis_valeur_conventionnelle_renouvellement_air.csv",
        # valeur_pont_thermique_isolation_mur="tv013_valeur_pont_thermique_isolation_mur.csv",
    ):
        """
        Load data from data_path
        """
        self.permeabililte = pd.read_csv(os.path.join(data_path, permeabililte))
        self.valeur_conventionnelle_renouvellement_air = pd.read_csv(
            os.path.join(data_path, valeur_conventionnelle_renouvellement_air)
        )

    def preprocess(
        self,
    ):
        """
        Preprocess data for further computation
        """
        pass
        self._preprocess_permeabililte()
        self._preprocess_valeur_conventionnelle_renouvellement_air()

    def _preprocess_permeabililte(self):
        self.valid_type_batiment = list(self.permeabililte["type_batiment"].unique())
        self.year_tresholds = self.permeabililte["annee_construction_max"].unique()
        self.permeabililte = self.permeabililte.set_index(
            ["type_batiment", "annee_construction_max"]
        )["q4paconv"].to_dict()

    def _preprocess_valeur_conventionnelle_renouvellement_air(self):
        self.valid_type_ventilation = list(
            self.valeur_conventionnelle_renouvellement_air["type_ventilation"].unique()
        )
        self.qvarepconv = self.valeur_conventionnelle_renouvellement_air.set_index(
            "type_ventilation"
        )["Qvarepconv"].to_dict()
        self.qvasoufconv = self.valeur_conventionnelle_renouvellement_air.set_index(
            "type_ventilation"
        )["Qvasoufconv"].to_dict()
        self.smeaconv = self.valeur_conventionnelle_renouvellement_air.set_index(
            "type_ventilation"
        )["Smeaconv"].to_dict()

import pandas as pd
import numpy as np
import os

from libs.utils import safe_divide
from libs.base import BaseProcessor


class UgProcessorVitrage(BaseProcessor):
    def __init__(
        self,
        data_path="../data/raw",
    ):
        super().__init__(data_path)

    @property
    def calc_input(self):
        return {
            "type_vitrage": self.valid_type_vitrages,
            "remplissage": self.valid_remplissages,
            "orientation": self.valid_orientations,
            "traitement_vitrage": self.valid_traitement_vitrages,
        }

    def calc(
        self,
        type_vitrage: str,
        remplissage: str,
        orientation: str,
        traitement_vitrage: str,
        epaisseur_lame: float,
        *args,
        **kwargs,
    ) -> float:
        """
        Get the coefficient for the given parameters

        Args
            type_vitrage (str): the type of vitrage, see self.valid_type_vitrages
            remplissage (str): the remplissage, see self.valid_remplissages
            orientation (str): the orientation of the vitrage, see self.valid_orientations
            traitement_vitrage (str): the traitement_vitrage, see self.valid_traitement_vitrages
            epaisseur_lame (float): the how wide is the epaisseur between lames in a vitrage (in mm)
        """
        self.validate(
            type_vitrage=type_vitrage,
            remplissage=remplissage,
            orientation=orientation,
            traitement_vitrage=traitement_vitrage,
        )

        if type_vitrage == "Simple Vitrage":
            return 5.8

        epaisseur_lame = self._get_epaisseur_lame(epaisseur_lame)
        return self.ug_coefficient_transmission_thermique_vitrage.loc[
            (type_vitrage, remplissage, orientation, traitement_vitrage, epaisseur_lame)
        ]

    def _get_epaisseur_lame(self, epaisseur_lame):
        try:
            idx = np.where(epaisseur_lame <= self.tresholds)[0][0]
        except:
            idx = -1
        return self.tresholds[idx]

    def load(
        self,
        data_path,
        ug_coefficient_transmission_thermique_vitrage="tv009_coefficient_transmission_thermique_vitrage.csv",
        ug_orientation="tv009_ug_orientation.csv",
        ug_remplissage="tv009_ug_remplissage.csv",
        ug_type_vitrage="tv009_ug_type_vitrage.csv",
        ug_traitement_vitrage="tv009_ug_traitement_vitrage.csv",
    ):
        """
        Load data from data_path
        """
        self.ug_coefficient_transmission_thermique_vitrage = pd.read_csv(
            os.path.join(data_path, ug_coefficient_transmission_thermique_vitrage)
        )
        self.ug_orientation = pd.read_csv(os.path.join(data_path, ug_orientation))
        self.ug_remplissage = pd.read_csv(os.path.join(data_path, ug_remplissage))
        self.ug_type_vitrage = pd.read_csv(os.path.join(data_path, ug_type_vitrage))
        self.ug_traitement_vitrage = pd.read_csv(
            os.path.join(data_path, ug_traitement_vitrage)
        )

    def preprocess(
        self,
    ):
        """
        Preprocess data for further computation
        """
        self._preprocess_orientation()
        self._preprocess_remplissage()
        self._preprocess_type_vitrage()
        self._preprocess_traitement_vitrage()
        self._preprocess_coefficient_transmission_thermique_vitrage()

    def _preprocess_orientation(self):
        """
        Preprocess ug_orientation
        """
        self.ug_orientation = self.ug_orientation.set_index("id")[
            "orientation"
        ].to_dict()
        self.valid_orientations = self.ug_orientation.values()

    def _preprocess_remplissage(self):
        """
        Preprocess ug_remplissage
        """
        self.ug_remplissage = self.ug_remplissage.set_index("id")[
            "remplissage"
        ].to_dict()
        self.valid_remplissages = self.ug_remplissage.values()

    def _preprocess_type_vitrage(self):
        """
        Preprocess ug_type_vitrage
        """
        self.ug_type_vitrage = self.ug_type_vitrage.set_index("id")[
            "type_vitrage"
        ].to_dict()
        self.valid_type_vitrages = self.ug_type_vitrage.values()

    def _preprocess_traitement_vitrage(self):
        """
        Preprocess ug_traitement_vitrage
        """
        self.ug_traitement_vitrage = self.ug_traitement_vitrage.set_index("id")[
            "traitement_vitrage"
        ].to_dict()
        self.valid_traitement_vitrages = self.ug_traitement_vitrage.values()

    def _preprocess_coefficient_transmission_thermique_vitrage(self):
        """
        Preprocess ug_coefficient_transmission_thermique_vitrage
        """
        self.ug_coefficient_transmission_thermique_vitrage["type_vitrage"] = (
            self.ug_coefficient_transmission_thermique_vitrage[
                "tv009_ug_type_vitrage_id"
            ].replace(self.ug_type_vitrage)
        )
        self.ug_coefficient_transmission_thermique_vitrage["remplissage"] = (
            self.ug_coefficient_transmission_thermique_vitrage[
                "tv009_ug_remplissage_id"
            ].replace(self.ug_remplissage)
        )
        self.ug_coefficient_transmission_thermique_vitrage["orientation"] = (
            self.ug_coefficient_transmission_thermique_vitrage[
                "tv009_ug_orientation_id"
            ].replace(self.ug_orientation)
        )
        self.ug_coefficient_transmission_thermique_vitrage["traitement_vitrage"] = (
            self.ug_coefficient_transmission_thermique_vitrage[
                "tv009_ug_traitement_vitrage_id"
            ].replace(self.ug_traitement_vitrage)
        )
        self.tresholds = (
            self.ug_coefficient_transmission_thermique_vitrage["epaisseur_lame"]
            .sort_values()
            .unique()
        )
        self.ug_coefficient_transmission_thermique_vitrage = (
            self.ug_coefficient_transmission_thermique_vitrage.set_index(
                [
                    "type_vitrage",
                    "remplissage",
                    "orientation",
                    "traitement_vitrage",
                    "epaisseur_lame",
                ],
                drop=True,
            )["ug"]
        )


class UwProcessorVitrage(BaseProcessor):
    ## todo : voir intégration des doubles fenetres page 29
    def __init__(
        self,
        data_path="../data/raw",
    ):
        super().__init__(data_path)

    @property
    def calc_input(self):
        return {
            "type_baie": list(self.valid_type_baies),
            "type_materiaux": list(self.valid_type_materiaux),
            "type_menuiserie": list(self.valid_type_menuiseries),
        }

    def calc(
        self,
        ug: float,
        type_baie: str,
        type_materiaux: str,
        type_menuiserie: str,
    ) -> float:
        """
        Get the coefficient for the given parameters

        Args:
            ug (float): the ug of the vitrage
            type_baie (str): the type of baie, see self.valid_type_baies
            type_materiaux (str): the type of materiaux, see self.valid_type_materiaux
            type_menuiserie (str): the type of menuiserie, see self.valid_type_menuiseries
        """
        self.validate(
            type_baie=type_baie,
            type_materiaux=type_materiaux,
            type_menuiserie=type_menuiserie,
        )
        ug = self._get_ug(ug, type_baie, type_materiaux, type_menuiserie)
        return self.coefficient_transmission_thermique_baie.loc[
            (type_baie, type_materiaux, type_menuiserie, ug)
        ]

    def _get_ug(self, ug, type_baie, type_materiaux, type_menuiserie):
        ## get the tresholds based on the type of baie, materiaux and menuiserie
        tresholds = self.tresholds[(type_baie, type_materiaux, type_menuiserie)]
        try:
            idx = np.where(ug <= tresholds)[0][0]
        except:
            idx = -1
        return tresholds[idx]

    def load(
        self,
        data_path,
        coefficient_transmission_thermique_baie="tv010_coefficient_transmission_thermique_baie.csv",
        uw_type_baie="tv010_uw_type_baie.csv",
        uw_type_materiaux="tv010_uw_type_materiaux.csv",
        uw_type_menuiserie="tv010_uw_type_menuiserie.csv",
    ):
        """
        Load data from data_path
        """
        self.coefficient_transmission_thermique_baie = pd.read_csv(
            os.path.join(data_path, coefficient_transmission_thermique_baie)
        )
        self.uw_type_baie = pd.read_csv(os.path.join(data_path, uw_type_baie))
        self.uw_type_materiaux = pd.read_csv(os.path.join(data_path, uw_type_materiaux))
        self.uw_type_menuiserie = pd.read_csv(
            os.path.join(data_path, uw_type_menuiserie)
        )

    def preprocess(
        self,
    ):
        """
        Preprocess data for further computation
        """
        self._preprocess_type_baie()
        self._preprocess_type_materiaux()
        self._preprocess_type_menuiserie()
        self._preprocess_coefficient_transmission_thermique_baie()

    def _preprocess_type_baie(self):
        """
        Preprocess uw_type_baie
        """
        self.uw_type_baie = self.uw_type_baie.set_index("id")["type_baie"].to_dict()
        self.valid_type_baies = self.uw_type_baie.values()

    def _preprocess_type_materiaux(self):
        """
        Preprocess uw_type_materiaux
        """
        self.uw_type_materiaux = self.uw_type_materiaux.set_index("id")[
            "type_materiaux"
        ].to_dict()
        self.valid_type_materiaux = self.uw_type_materiaux.values()

    def _preprocess_type_menuiserie(self):
        """
        Preprocess uw_type_menuiserie
        """
        self.uw_type_menuiserie = self.uw_type_menuiserie.set_index("id")[
            "type_menuiserie"
        ].to_dict()
        self.valid_type_menuiseries = self.uw_type_menuiserie.values()

    def _preprocess_coefficient_transmission_thermique_baie(self):
        """
        Preprocess coefficient_transmission_thermique_baie
        """
        self.coefficient_transmission_thermique_baie["type_baie"] = (
            self.coefficient_transmission_thermique_baie[
                "tv010_uw_type_baie_id"
            ].replace(self.uw_type_baie)
        )
        self.coefficient_transmission_thermique_baie["type_materiaux"] = (
            self.coefficient_transmission_thermique_baie[
                "tv010_uw_type_materiaux_id"
            ].replace(self.uw_type_materiaux)
        )
        self.coefficient_transmission_thermique_baie["type_menuiserie"] = (
            self.coefficient_transmission_thermique_baie[
                "tv010_uw_type_menuiserie_id"
            ].replace(self.uw_type_menuiserie)
        )
        self.coefficient_transmission_thermique_baie["ug"] = (
            self.coefficient_transmission_thermique_baie["ug"].apply(
                self._nulify_non_numerical
            )
        )
        self.coefficient_transmission_thermique_baie = (
            self.coefficient_transmission_thermique_baie.dropna(subset=["ug"])
        )
        # self.tresholds=self.coefficient_transmission_thermique_baie['ug'].sort_values().unique()
        # tresholds are adapted based on materiaux, menuiserie and baie
        self.tresholds = (
            self.coefficient_transmission_thermique_baie.groupby(
                ["type_baie", "type_materiaux", "type_menuiserie"]
            )["ug"]
            .apply(lambda x: x.sort_values().unique())
            .to_dict()
        )
        self.coefficient_transmission_thermique_baie = (
            self.coefficient_transmission_thermique_baie.set_index(
                ["type_baie", "type_materiaux", "type_menuiserie", "ug"], drop=True
            )["uw"]
        )

    def _nulify_non_numerical(self, x):
        try:
            return float(x)
        except:
            if x == "NULL":
                return 1000.0
            return np.nan


class UjnProcessorVitrage(BaseProcessor):
    def __init__(
        self,
        data_path="../data/raw",
    ):
        super().__init__(data_path)

    @property
    def calc_input(self):
        return {
            "type_fermeture": list(self.valid_type_fermetures),
        }

    def calc(
        self,
        uw: float,
        type_fermeture: str,
    ):
        """
        Get the coefficient for the given parameters

        Args:
            uw (float): the uw of the vitrage
            type_fermeture (str): the type of fermeture
        """
        self.validate(type_fermeture=type_fermeture)
        uw = self._get_uw(uw)
        deltar = self._get_deltar(type_fermeture)
        return self.coefficient_transmission_thermique_baie_protection_solaire.loc[
            (uw, deltar)
        ]

    def _get_uw(self, uw):
        try:
            idx = np.where(uw <= self.uw_tresholds)[0][0]
        except:
            idx = -1
        return self.uw_tresholds[idx]

    def _get_deltar(self, type_fermeture):
        return self.resistance_additionnelle[type_fermeture]

    def load(
        self,
        data_path,
        resistance_additionnelle="tv011_resistance_additionnelle.csv",
        coefficient_transmission_thermique_baie_protection_solaire="tv012_coefficient_transmission_thermique_baie_protection_solaire.csv",
    ):
        """
        Load data from data_path
        """
        self.resistance_additionnelle = pd.read_csv(
            os.path.join(data_path, resistance_additionnelle)
        )
        self.coefficient_transmission_thermique_baie_protection_solaire = pd.read_csv(
            os.path.join(
                data_path, coefficient_transmission_thermique_baie_protection_solaire
            )
        )

    def preprocess(
        self,
    ):
        """
        Preprocess data for further computation
        """
        self._preprocess_resistance_additionnelle()
        self._preprocess_coefficient_transmission_thermique_baie_protection_solaire()

    def _preprocess_resistance_additionnelle(self):
        """
        Preprocess resistance_additionnelle
        """
        self.resistance_additionnelle = self.resistance_additionnelle.set_index(
            "fermetures"
        )["resistance_additionnelle"].to_dict()
        self.valid_type_fermetures = self.resistance_additionnelle.keys()

    def _preprocess_coefficient_transmission_thermique_baie_protection_solaire(self):
        """
        Preprocess coefficient_transmission_thermique_baie_protection_solaire
        """
        self.uw_tresholds = (
            self.coefficient_transmission_thermique_baie_protection_solaire["uw"]
            .sort_values()
            .unique()
        )
        self.coefficient_transmission_thermique_baie_protection_solaire = (
            self.coefficient_transmission_thermique_baie_protection_solaire.set_index(
                ["uw", "deltar"], drop=True
            )["ujn"]
        )


class UBaieProcessorVitrage(BaseProcessor):
    def __init__(
        self,
        data_path="../data/raw",
    ):
        super().__init__(data_path)

    @property
    def calc_input(self):
        # combine all the valid inputs from the sub processors
        return {
            **self.ug_processor.calc_input,
            **self.uw_processor.calc_input,
            **self.ujn_processor.calc_input,
        }

    # Calc combine all inputs of the calc of sub processors. All value default to none
    def calc(
        self,
        u: str = None,
        type_vitrage: str = None,
        remplissage: str = None,
        orientation: str = None,
        traitement_vitrage: str = None,
        epaisseur_lame: float = None,
        type_baie: str = None,
        type_materiaux: str = None,
        type_menuiserie: str = None,
        type_fermeture: str = None,
    ):
        """Compute the coefficient for the given parameters

        Args:
            u (str): If it is known, you can directly pass the value of u
            type_vitrage (str): the type of vitrage
            remplissage (str): the remplissage
            orientation (str): the orientation of the vitrage
            traitement_vitrage (str): the traitement_vitrage
            epaisseur_lame (float): the how wide is the epaisseur between lames in a vitrage (in mm)
            type_baie (str): the type of baie
            type_materiaux (str): the type of materiaux
            type_menuiserie (str): the type of menuiserie
            type_fermeture (str): si des volets soont présent, les ajouter dans le calcul
        """
        ## Compute Ug, then Uw and finally Ujn if needed

        if u:
            return u

        self.validate(
            type_vitrage=type_vitrage,
            remplissage=remplissage,
            orientation=orientation,
            traitement_vitrage=traitement_vitrage,
            epaisseur_lame=epaisseur_lame,
            type_baie=type_baie,
            type_materiaux=type_materiaux,
            type_menuiserie=type_menuiserie,
            type_fermeture=type_fermeture,
        )
        ug = self.ug_processor.calc(
            type_vitrage, remplissage, orientation, traitement_vitrage, epaisseur_lame
        )
        uw = self.uw_processor.calc(ug, type_baie, type_materiaux, type_menuiserie)

        if type_fermeture:
            ubaie = self.ujn_processor.calc(uw, type_fermeture)
        else:
            ubaie = uw
        return ubaie

    def load(self, data_path, *args, **kwargs):
        ## Load each sub type of vitrage processor
        self.ug_processor = UgProcessorVitrage(data_path=data_path)
        self.uw_processor = UwProcessorVitrage(data_path=data_path)
        self.ujn_processor = UjnProcessorVitrage(data_path=data_path)

    def preprocess(self):
        pass

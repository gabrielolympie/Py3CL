import pandas as pd
import numpy as np
import os

from libs.utils import safe_divide
from libs.base import BaseProcessor


class CauxProcessor(BaseProcessor):
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
        type_ventilation: str = None,
        type_batiment: str = None,
        annee_construction: int = None,
        is_collective: bool = None,
        surface_habitable: float = None,
        *args,
        **kwargs,
    ) -> float:
        self.validate(
            type_ventilation=type_ventilation,
            type_batiment=type_batiment,
        )

        if " df " in type_ventilation.lower():
            type_vmc = "Double Flux"
        elif (
            " hybride " in type_ventilation.lower()
            or " mécanique " in type_ventilation.lower()
        ):
            type_vmc = "hybride"
        elif " hygro " in type_ventilation.lower():
            type_vmc = "Simple Flux hygro"
        else:
            type_vmc = "Simple Flux Auto"

        if type_batiment == "Maison individuelle":
            if annee_construction < 2012:
                if type_vmc == "Double Flux":
                    pvent_moy = 80
                elif type_vmc == "Simple flux hygro":
                    pvent_moy = 50
                elif type_vmc == "Simple Flux Auto":
                    pvent_moy = 65
                elif type_vmc == "hybride":
                    pvent_moy = 65 * 0.083
                else:
                    raise ValueError(f"Type de VMC inconnu: {type_vmc}")
            else:
                if type_vmc == "Double Flux":
                    pvent_moy = 35
                elif type_vmc == "Simple flux hygro":
                    pvent_moy = 15
                elif type_vmc == "Simple Flux Auto":
                    pvent_moy = 35
                elif type_vmc == "hybride":
                    pvent_moy = 35 * 0.083
                else:
                    raise ValueError(f"Type de VMC inconnu: {type_vmc}")
        else:
            assert (
                surface_habitable is not None
            ), "surface_habitable must be provided for collective building"
            if annee_construction < 2012:
                if type_vmc == "Double Flux":
                    pvent = 1.1
                elif type_vmc == "Simple flux hygro":
                    pvent = 0.46
                elif type_vmc == "Simple Flux Auto":
                    pvent = 0.46
                elif type_vmc == "hybride":
                    assert (
                        is_collective is not None
                    ), "is_collective must be provided for hybride VMC in collective building"
                    if is_collective:
                        pvent = 0.46 * 0.167
                    else:
                        pvent = 0.46 * 0.083
                else:
                    raise ValueError(f"Type de VMC inconnu: {type_vmc}")
            else:
                if type_vmc == "Double Flux":
                    pvent = 0.6
                elif type_vmc == "Simple flux hygro":
                    pvent = 0.25
                elif type_vmc == "Simple Flux Auto":
                    pvent = 0.25
                elif type_vmc == "hybride":
                    assert (
                        is_collective is not None
                    ), "is_collective must be provided for hybride VMC in collective building"
                    if is_collective:
                        pvent = 0.25 * 0.167
                    else:
                        pvent = 0.25 * 0.083
                else:
                    raise ValueError(f"Type de VMC inconnu: {type_vmc}")
            qvarepconv = self.qvarepconv[type_ventilation]
            pvent_moy = pvent * qvarepconv * surface_habitable
        caux = 8760 * pvent_moy / 1000
        return caux

    def load(
        self,
        data_path,
        valeur_conventionnelle_renouvellement_air="tv015_bis_valeur_conventionnelle_renouvellement_air.csv",
    ):
        self.valeur_conventionnelle_renouvellement_air = pd.read_csv(
            os.path.join(data_path, valeur_conventionnelle_renouvellement_air)
        )

    def preprocess(
        self,
    ):
        self._preprocess_valeur_conventionnelle_renouvellement_air()
        self.valid_type_vmc = [
            "Simple Flux Auto",
            "Simple Flux hygro",
            "Double Flux",
            "hybride",
        ]

        self.valid_type_batiment = [
            "Maison individuelle",
            "Logement collectif",
        ]

    def _preprocess_valeur_conventionnelle_renouvellement_air(self):
        self.valid_type_ventilation = list(
            self.valeur_conventionnelle_renouvellement_air["type_ventilation"].unique()
        )
        self.qvarepconv = self.valeur_conventionnelle_renouvellement_air.set_index(
            "type_ventilation"
        )["Qvarepconv"].to_dict()

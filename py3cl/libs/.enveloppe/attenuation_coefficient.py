import pandas as pd
import numpy as np
import os

from libs.utils import safe_divide
from libs.base import BaseProcessor


class AttenuationCoefficient(BaseProcessor):
    def __init__(self, data_path, *args, **kwargs):
        super().__init__(data_path, *args, **kwargs)
        # self.load(data_path, *args, **kwargs)
        # self.preprocess(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        return self.calc(*args, **kwargs)

    @property
    def calc_input(self):
        return {
            "exterior_type": list(self.valid_exterior_types),
            "aiu_isole": [0, 1],
            "aue_isole": [0, 1],
            "zone_climatique": ["H1", "H2", "H3"],
            "orientation": ["Nord", "Est / Ouest", "Sud"],
        }

    def calc(
        self,
        exterior_type: str,
        aiu: float = None,
        aue: float = None,
        aiu_isole: float = None,
        aue_isole: float = None,
        zone_climatique: str = None,
        orientation: str = None,
        *args,
        **kwargs,
    ):
        """
        Get the coefficient for the given parameters

        Args
            exterior_type (str): the type of exterior, see self.valid_exterior_types
            aiu (float): the surface of the wall between the habitation and the non heated area (optional)
            aue (float): the surface of the wall between the non heated area and the exterior (optional)
            aiu_isole (float): whether the interior area is isolated or not (1 or 0) (optional)
            aue_isole (float): whether the exterior area is isolated or not (1 or 0) (optional)
            zone_climatique (str): the climatic zone in ['H1', 'H2', 'H3'] (optional)
            orientation (str): the orientation of the véranda in ['Nord', 'Est / Ouest', 'Sud'] (optional)
        """
        self.validate(
            exterior_type=exterior_type,
            aiu_isole=aiu_isole,
            aue_isole=aue_isole,
            zone_climatique=zone_climatique,
            orientation=orientation,
        )
        if exterior_type in self.exterior_types:
            return self._calc_exterior(exterior_type)
        elif exterior_type == "Véranda":
            return self._calc_veranda(zone_climatique, orientation, aiu_isole)
        elif exterior_type in self.local_non_chauffe_types:
            return self._calc_local_non_chauffe(exterior_type, aiu, aue, aiu_isole, aue_isole)
        else:
            raise ValueError(f"exterior_type must be in {self.valid_exterior_types}")

    def _calc_exterior(
        self,
        exterior_type: str,
    ):
        """
        Get the coefficient for the given exterior type

        Args:
            exterior_type (str): the type of exterior, see self.exterior_types
        """
        assert exterior_type in self.exterior_types, f"exterior_type must be in {self.exterior_types }"
        return self.coefficient_reduction_exterior[exterior_type]

    def _calc_local_non_chauffe(
        self,
        exterior_type: str,
        aiu: float,
        aue: float,
        aiu_isole: float,
        aue_isole: float,
    ):
        """
        Get the coefficient for the given parameters for a non heated area

        Args:
            exterior_type (str): the type of exterior, see self.local_non_chauffe_types
            aiu (float): the surface of the wall between the habitation and the non heated area
            aue (float): the surface of the wall between the non heated area and the exterior
            aiu_isole (float): whether the interior area is isolated or not (1 or 0)
            aue_isole (float): whether the exterior area is isolated or not (1 or 0)
        """
        assert exterior_type in self.local_non_chauffe_types, f"exterior_type must be in {self.local_non_chauffe_types}"
        assert aiu is not None, "aiu should be provided for non heated areas"
        assert aue is not None, "aue should be provided for non heated areas"
        assert aue_isole is not None, "aue_isole should be provided for non heated areas"
        assert aiu_isole is not None, "aiu_isole should be provided for non heated areas"

        uv_ue = self.local_non_chauffe[exterior_type]
        aiu_aue = safe_divide(aiu, aue)
        idx = np.where(aiu_aue <= self.tresholds)[0][0]
        return self.coefficient_reduction_interior.loc[self.tresholds[idx], uv_ue, aue_isole, aiu_isole]

    def _calc_veranda(
        self,
        zone_climatique: str,
        orientation: str,
        aiu_isole: float,
    ):
        """
        Get the coefficient for the given parameters for a veranda

        Args:
            zone_climatique (str): the climatic zone in ['H1', 'H2', 'H3']
            orientation (str): the orientation of the véranda in ['Nord', 'Est / Ouest', 'Sud']
            aiu_isole (float): whether the interior area is isolated or not (1 or 0)
        """
        assert zone_climatique in [
            "H1",
            "H2",
            "H3",
        ], "zone_climatique must be in ['H1', 'H2', 'H3']"
        assert orientation in [
            "Nord",
            "Est / Ouest",
            "Sud",
        ], "orientation must be in ['Nord', 'Est / Ouest', 'Sud']"
        assert aiu_isole in [0, 1], "aiu_isole must be 0 or 1"
        return self.coefficient_reduction_veranda.loc[zone_climatique, orientation, aiu_isole]

    def load(
        self,
        data_path,
        coefficient_reduction_deperditions_path="tv001_coefficient_reduction_deperditions.csv",
        local_non_chauffe_path="tv002_local_non_chauffe.csv",
        veranda_path="tv002_veranda.csv",
    ):
        """
        Loads the necessary data files for the model.

        Args:
            data_path (str): The path to the directory containing the data files.
            coefficient_reduction_deperditions_path (str, optional): The filename of the coefficient reduction deperditions data file. Defaults to "tv001_coefficient_reduction_deperditions.csv".
            local_non_chauffe_path (str, optional): The filename of the local non chauffe data file. Defaults to "tv002_local_non_chauffe.csv".
            veranda_path (str, optional): The filename of the veranda data file. Defaults to "tv002_veranda.csv".
        """
        self.coefficient_reduction_deperditions = pd.read_csv(
            os.path.join(data_path, coefficient_reduction_deperditions_path)
        )
        self.local_non_chauffe = pd.read_csv(os.path.join(data_path, local_non_chauffe_path))
        self.coefficient_reduction_veranda = pd.read_csv(os.path.join(data_path, veranda_path))

    def preprocess(self, *args, **kwargs):
        self._preprocess_coefficient_reduction_deperditions(*args, **kwargs)
        self._preprocess_local_non_chauffe(*args, **kwargs)
        self._preprocess_veranda(*args, **kwargs)

        self.exterior_types = list(self.coefficient_reduction_exterior.keys())
        self.local_non_chauffe_types = list(self.local_non_chauffe.keys())
        self.valid_exterior_types = self.exterior_types + self.local_non_chauffe_types

    def _preprocess_coefficient_reduction_deperditions(self, *args, **kwargs):
        self.coefficient_reduction_exterior = (
            self.coefficient_reduction_deperditions[self.coefficient_reduction_deperditions["aue_isole"].isna()][
                ["aiu_aue", "valeur"]
            ]
            .set_index("aiu_aue", drop=True)["valeur"]
            .to_dict()
        )
        self.coefficient_reduction_exterior["Local Chauffé"] = 0.0

        self.coefficient_reduction_interior = self.coefficient_reduction_deperditions[
            self.coefficient_reduction_deperditions["aue_isole"].notna()
        ][["aiu_aue_max", "uv_ue", "aue_isole", "aiu_isole", "valeur"]]
        self.coefficient_reduction_interior["aiu_aue_max"] = self.coefficient_reduction_interior["aiu_aue_max"].fillna(
            10000
        )
        self.tresholds = self.coefficient_reduction_interior["aiu_aue_max"].sort_values().unique()

    def _preprocess_local_non_chauffe(self, *args, **kwargs):
        self.local_non_chauffe = self.local_non_chauffe.set_index("local_non_chauffe")["uvue"].to_dict()

    def _preprocess_veranda(self, *args, **kwargs):
        self.coefficient_reduction_veranda["Paroi donnant sur la véranda"] = self.coefficient_reduction_veranda[
            "Paroi donnant sur la véranda"
        ].replace({"Isolé": 1, "Non isolé": 0})
        self.coefficient_reduction_veranda = self.coefficient_reduction_veranda.set_index(
            [
                "Zone climatique",
                "Orientation de la véranda",
                "Paroi donnant sur la véranda",
            ],
            drop=True,
        )["bver"]

import pandas as pd
import numpy as np
import os

from libs.utils import safe_divide
from libs.base import BaseProcessor


class FapportProcessor(BaseProcessor):
    def __init__(
        self,
        data_path="../data/raw",
    ):
        super().__init__(data_path)

    @property
    def calc_input(self):
        return {}

    def calc(
        self,
    ) -> float:
        pass

    def load(
        self,
        data_path,
        departement="tv016_departement.csv",
    ):
        """
        Load data from data_path
        """
        self.departement = pd.read_csv(os.path.join(data_path, departement))

    def preprocess(
        self,
    ):
        """
        Preprocess data for further computation
        """
        pass

    # def _preprocess_permeabililte(self):
    #     pass

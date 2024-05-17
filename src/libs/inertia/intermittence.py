import pandas as pd
import numpy as np
import os

from libs.utils import safe_divide
from libs.base import BaseProcessor


class I0Processor(BaseProcessor):
    def __init__(self, data_path, *args, **kwargs):
        super().__init__(data_path, *args, **kwargs)

    @property
    def calc_input(self):
        return {
            "comptage_individuel": list(self.valid_intermittence_comptage_individuel),
            "equipement_intermittence": list(self.valid_intermittence_equipement_intermittence),
            "inertie": list(self.valid_intermittence_inertie),
            "type_batiment": list(self.valid_intermittence_type_batiment),
            "type_chauffage": list(self.valid_intermittence_type_chauffage),
            "type_emetteur": list(self.valid_intermittence_type_emetteur),
            "type_installation": list(self.valid_intermittence_type_installation),
            "type_regulation": list(self.valid_intermittence_type_regulation),
        }
    
    @property
    def valid_input_combinations(self):
        return self.valid_input_combination

    def calc(
        self,
        comptage_individuel: str = None,
        equipement_intermittence: str = None,
        inertie: str = None,
        type_batiment: str = None,
        type_chauffage: str = None,
        type_emetteur: str = None,
        type_installation: str = None,
        type_regulation: str = None,
        *args,
        **kwargs,
    ):
        self.validate(
            comptage_individuel=comptage_individuel,
            equipement_intermittence=equipement_intermittence,
            inertie=inertie,
            type_batiment=type_batiment,
            type_chauffage=type_chauffage,
            type_emetteur=type_emetteur,
            type_installation=type_installation,
            type_regulation=type_regulation,
        )
        if type_batiment != "Immeuble Collectif":
            comptage_individuel=np.nan

        return self.intermittence[(
            comptage_individuel,
            equipement_intermittence,
            inertie,
            type_batiment,
            type_chauffage,
            type_emetteur,
            type_installation,
            type_regulation,
        )]

    def load(
        self,
        data_path,
        intermittence_comptage_individuel="tv025_intermittence_comptage_individuel.csv",
        intermittence_equipement_intermittence="tv025_intermittence_equipement_intermittence.csv",
        intermittence_inertie="tv025_intermittence_inertie.csv",
        intermittence_type_batiment="tv025_intermittence_type_batiment.csv",
        intermittence_type_chauffage="tv025_intermittence_type_chauffage.csv",
        intermittence_type_emetteur="tv025_intermittence_type_emetteur.csv",
        intermittence_type_installation="tv025_intermittence_type_installation.csv",
        intermittence_type_regulation="tv025_intermittence_type_regulation.csv",
        intermittence="tv025_intermittence.csv",
    ):
        self.intermittence_comptage_individuel = pd.read_csv(os.path.join(data_path, intermittence_comptage_individuel))
        self.intermittence_equipement_intermittence = pd.read_csv(os.path.join(data_path, intermittence_equipement_intermittence))
        self.intermittence_inertie = pd.read_csv(os.path.join(data_path, intermittence_inertie))
        self.intermittence_type_batiment = pd.read_csv(os.path.join(data_path, intermittence_type_batiment))
        self.intermittence_type_chauffage = pd.read_csv(os.path.join(data_path, intermittence_type_chauffage))
        self.intermittence_type_emetteur = pd.read_csv(os.path.join(data_path, intermittence_type_emetteur))
        self.intermittence_type_installation = pd.read_csv(os.path.join(data_path, intermittence_type_installation))
        self.intermittence_type_regulation = pd.read_csv(os.path.join(data_path, intermittence_type_regulation))
        self.intermittence = pd.read_csv(os.path.join(data_path, intermittence))

    def preprocess(self, *args, **kwargs):
        self._preprocess_intermittence_comptage_individuel(*args, **kwargs)
        self._preprocess_intermittence_equipement_intermittence(*args, **kwargs)
        self._preprocess_intermittence_inertie(*args, **kwargs)
        self._preprocess_intermittence_type_batiment(*args, **kwargs)
        self._preprocess_intermittence_type_chauffage(*args, **kwargs)
        self._preprocess_intermittence_type_emetteur(*args, **kwargs)
        self._preprocess_intermittence_type_installation(*args, **kwargs)
        self._preprocess_intermittence_type_regulation(*args, **kwargs)
        self._preprocess_intermittence(*args, **kwargs)

    def _preprocess_intermittence_comptage_individuel(self, *args, **kwargs):
        self.valid_intermittence_comptage_individuel = self.intermittence_comptage_individuel["comptage_individuel"].unique()
        self.intermittence_comptage_individuel = self.intermittence_comptage_individuel.set_index("id")["comptage_individuel"].to_dict()

    def _preprocess_intermittence_equipement_intermittence(self, *args, **kwargs):
        self.valid_intermittence_equipement_intermittence = self.intermittence_equipement_intermittence["equipement_intermittence"].unique()
        self.intermittence_equipement_intermittence = self.intermittence_equipement_intermittence.set_index("id")["equipement_intermittence"].to_dict()

    def _preprocess_intermittence_inertie(self, *args, **kwargs):
        self.valid_intermittence_inertie = self.intermittence_inertie["inertie"].unique()
        self.intermittence_inertie = self.intermittence_inertie.set_index("id")["inertie"].to_dict()

    def _preprocess_intermittence_type_batiment(self, *args, **kwargs):
        self.valid_intermittence_type_batiment = self.intermittence_type_batiment["type_batiment"].unique()
        self.intermittence_type_batiment = self.intermittence_type_batiment.set_index("id")["type_batiment"].to_dict()

    def _preprocess_intermittence_type_chauffage(self, *args, **kwargs):
        self.valid_intermittence_type_chauffage = self.intermittence_type_chauffage["type_chauffage"].unique()
        self.intermittence_type_chauffage = self.intermittence_type_chauffage.set_index("id")["type_chauffage"].to_dict()

    def _preprocess_intermittence_type_emetteur(self, *args, **kwargs):
        self.valid_intermittence_type_emetteur = self.intermittence_type_emetteur["type_emetteur"].unique()
        self.intermittence_type_emetteur = self.intermittence_type_emetteur.set_index("id")["type_emetteur"].to_dict()

    def _preprocess_intermittence_type_installation(self, *args, **kwargs):
        self.valid_intermittence_type_installation = self.intermittence_type_installation["type_installation"].unique()
        self.intermittence_type_installation = self.intermittence_type_installation.set_index("id")["type_installation"].to_dict()

    def _preprocess_intermittence_type_regulation(self, *args, **kwargs):
        self.valid_intermittence_type_regulation = self.intermittence_type_regulation["type_regulation"].unique()
        self.intermittence_type_regulation = self.intermittence_type_regulation.set_index("id")["type_regulation"].to_dict()

    # "id","code","tv025_type_batiment_id","tv025_intermittence_type_installation_id","tv025_intermittence_type_chauffage_id","tv025_intermittence_type_regulation_id","tv025_type_emetteur_id","tv025_intermittence_inertie_id","tv025_equipement_intermittence_id","tv025_intermittence_comptage_individuel_id","I0","est_efface"
    def _preprocess_intermittence(self, *args, **kwargs):
        self.intermittence['comptage_individuel']=self.intermittence['tv025_intermittence_comptage_individuel_id'].replace(self.intermittence_comptage_individuel)
        self.intermittence['equipement_intermittence']=self.intermittence['tv025_equipement_intermittence_id'].replace(self.intermittence_equipement_intermittence)
        self.intermittence['inertie']=self.intermittence['tv025_intermittence_inertie_id'].replace(self.intermittence_inertie)
        self.intermittence['type_batiment']=self.intermittence['tv025_type_batiment_id'].replace(self.intermittence_type_batiment)
        self.intermittence['type_chauffage']=self.intermittence['tv025_intermittence_type_chauffage_id'].replace(self.intermittence_type_chauffage)
        self.intermittence['type_emetteur']=self.intermittence['tv025_type_emetteur_id'].replace(self.intermittence_type_emetteur)
        self.intermittence['type_installation']=self.intermittence['tv025_intermittence_type_installation_id'].replace(self.intermittence_type_installation)
        self.intermittence['type_regulation']=self.intermittence['tv025_intermittence_type_regulation_id'].replace(self.intermittence_type_regulation)

        self.valid_input_combination=self.intermittence[['comptage_individuel', 'equipement_intermittence', 'inertie', 'type_batiment', 'type_chauffage', 'type_emetteur', 'type_installation', 'type_regulation']].drop_duplicates().to_dict(orient='records')
        self.intermittence = self.intermittence.set_index(['comptage_individuel', 'equipement_intermittence', 'inertie', 'type_batiment', 'type_chauffage', 'type_emetteur', 'type_installation', 'type_regulation'])['I0'].to_dict()
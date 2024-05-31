from libs.utils import safe_divide, vectorized_safe_divide, set_community, iterative_merge
from pydantic import BaseModel
import os
from typing import Optional
import numpy as np
import pandas as pd


class BaseProcessor:
    """
    A processor class that handles the initialization and configuration of processing parameters based on input schemes,
    defines categorical and numerical fields, manages abaque configurations, and establishes inverse mappings.
    
    Attributes:
        abaque (dict): A dictionary containing abaque configurations.
        input (Any): An input object expected to have type annotations defining its structure.
        input_scheme (dict): Extracted type annotations from the input object.
        categorical_fields (list): List of fields categorized as categorical.
        numerical_fields (list): List of fields categorized as numerical.
        used_abaques (dict): Mapping of field usage to abaque specifications.
        field_usage (dict): Tracks the usage of fields across different abaques.
    """
    def __init__(self, abaques, input, characteristics_corrections=None):
        self.abaques = abaques
        self.input=input
        self.input_scheme = input.__annotations__
        self.characteristics_corrections = characteristics_corrections
        self.define_categorical()
        self.define_numerical()
        self.define_abaques()
        self.inverse_abaques()
        self.field_usage = self.list_fields_usages

    
    def define_categorical(self):
        self.categorical_fields = [
            ## Fill with the categorical fields
        ]

    def define_numerical(self):
        self.numerical_fields = [
            ## Fill with the numerical fields
        ]

    def define_abaques(self):
        self.used_abaques = {
            # "Rd_systeme_chauffage": {
            #     "type_distribution": "type_distribution",
            #     "isole": "isolation_distribution",
            # },
        }

    def inverse_abaques(self):
        self.used_abaques_inv = self.used_abaques.copy()
        for k, v in self.used_abaques_inv.items():
            v = {v: k for k, v in v.items()}
            self.used_abaques[k] = v

    def get_renamed_cat_combination(self, name_abaque):
        cat_combinations=pd.DataFrame(self.abaques[name_abaque].valid_cat_combinations)
        correspondance_dict=self.used_abaques_inv[name_abaque]
        cat_combinations.columns = [correspondance_dict[elt] if elt in correspondance_dict else elt for elt in cat_combinations.columns]
        return cat_combinations.to_dict(orient='records')

    @property
    def valid_cat_combinations(self):
        valid_cat_combinations = {}
        # Iterate over each abaque to gather combinations of fields that are used together
        standalone_abaques = []
        entangled_abaques = []
        for field, abaques in self.field_usage.items():
            if field in self.categorical_fields:
                if len(abaques) > 1:
                    entangled_abaques.append(set(abaques))
        standalone_abaques = [abaques for abaques in self.used_abaques if abaques not in list(set().union(*entangled_abaques))]
        entangled_abaques = [list(elt) for elt in set_community(entangled_abaques)]

        n=0
        for elt in standalone_abaques:
            # temp = pd.DataFrame(self.abaques[elt].valid_cat_combinations)
            # temp.columns = []

            valid_cat_combinations[f"group_{n}"] = {
                'keys': list(self.used_abaques[elt].keys()),
                'combinations':self.get_renamed_cat_combination(elt)
            }
            n+=1

        for elt in entangled_abaques:
            combinations = [self.get_renamed_cat_combination(a) for a in elt]
            combinations = iterative_merge(combinations)
            valid_cat_combinations[f"group_{n}"] = {
                'keys': list(set().union(*[list(c.keys()) for c in combinations])),
                'combinations': combinations
            }
            n+=1

        return valid_cat_combinations

    @property
    def key_characteristics(self):
        key_characteristics={}
        for field in self.input_scheme:
            if field in self.field_usage:
                candidates=[self.abaques[a].key_characteristics[self.used_abaques[a][field]] for a in self.field_usage[field]]
                if field in self.categorical_fields:
                    if len(candidates)>1:
                        candidates=np.concatenate(candidates)
                    else:
                        candidates=candidates[0]
                    
                    candidates=np.unique([str(elt) for elt in candidates])
                    key_characteristics[field]=candidates
                elif field in self.numerical_fields:
                    m = min([candidate['min'] for candidate in candidates])
                    M = max([candidate['max'] for candidate in candidates])
                    key_characteristics[field]={'min':m, 'max':M}
                else:
                    key_characteristics[field]="any"
            elif field in self.numerical_fields:
                key_characteristics[field]="float"
            else:
                key_characteristics[field]="any"
        if self.characteristics_corrections is not None:
            for field, value in self.characteristics_corrections.items():
                key_characteristics[field]=value
        return key_characteristics
                
    @property
    def list_fields_usages(self):
        dico={}
        for elt in self.input_scheme:
            for abaque in self.used_abaques:
                if elt in self.used_abaques[abaque].keys():
                    try:
                        dico[elt].append(abaque)
                    except:
                        dico[elt]=[abaque]
        return dico
    

    def forward(self, dpe, kwargs):
        pass
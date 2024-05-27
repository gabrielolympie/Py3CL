import numpy as np
import pandas as pd
import os
from utils import save_config, load_config
import json
from itertools import product


class Abaque:
    """
    A class to represent an Abaque object, which is a specialized data handling and transformation tool.

    Attributes:
    -----------
    abaque : pd.DataFrame
        DataFrame that stores the main data.
    upper_thresholds : dict
        Dictionary to store upper threshold values for numeric keys.
    key_characteristics : dict
        Dictionary to store characteristics (min, max, unique values) of keys.
    valid_cat_combinations : dict
        Dictionary to store valid combinations of categorical keys.
    config : dict
        Configuration dictionary loaded from a file.

    Methods:
    --------
    __dict__():
        Prints the configuration in a JSON formatted string.
    __str__():
        Returns a string representation of the Abaque object.
    __call__(keys, value):
        Allows the object to be called as a function to retrieve specific values.
    forward(keys):
        Processes input keys and retrieves corresponding values from the abaque.
    load_abaques(data_path, file, refs=None, keys=list[dict], values=list, mapping=None, reduce=None):
        Loads the abaque from a CSV file and applies various transformations.
    get_key_characteristics(keys):
        Extracts and stores characteristics of the specified keys.
    process_references(refs, data_path):
        Processes reference files to replace column values based on external data.
    apply_mapping(mapping):
        Applies transformation functions to specified columns.
    apply_reduction(reduce):
        Reduces multiple columns into a new column based on a specified function.
    initialize_valid_cat_combinations():
        Initializes valid categorical combinations by filtering and deduplicating values.
    """

    def __init__(self, config, **kwargs):
        """
        Constructs all the necessary attributes for the Abaque object.

        Parameters:
        -----------
        config : str
            Path to the configuration file.
        kwargs : dict
            Additional keyword arguments to be passed to the load_abaques method.
        """
        self.abaque = None
        self.upper_thresholds = {}
        self.key_characteristics = {}

        self.valid_cat_combinations = {}
        self.config = load_config(config)
        self.load_abaques(**self.config)
        print(self.__str__())

    def __dict__(self):
        """Prints the configuration of the Abaque object in a JSON formatted string."""
        print(json.dumps(self.config, indent=2))

    def __str__(self):
        """Returns a string representation of the Abaque object."""
        return f"""Abaque({self.config['file']})
Keys: {self.keys()}
Values: {self.values()}
        """

    def __repr__(self):
        return self.__str__()

    def keys(self):
        return self.abaque.index.names

    def values(self):
        return self.config["values"]

    def __call__(self, keys, value=None):
        """
        Allows the Abaque object to be called as a function to retrieve specific values.

        Parameters:
        -----------
        keys : dict
            Dictionary of keys to be used for lookup.
        value : str
            The value to be retrieved from the abaque.
            WARNING: If value is None, the first value in the 'values' list will be returned.

        Returns:
        --------
        The retrieved value from the abaque.
        """
        if value is None:
            return self.forward(keys)[self.config["values"][0]]
        out = self.forward(keys)
        return out[value]

    def forward(self, keys):
        processed_input = {}

        for key, val in keys.items():
            if val is None:
                processed_input[key] = "NULL"
            elif key in self.upper_thresholds:
                thresholds = self.upper_thresholds[key]
                idx = np.searchsorted(thresholds, val, side="right") - 1
                processed_input[key] = thresholds[max(0, idx)]
            else:
                processed_input[key] = val
        try:
            inputs = tuple(processed_input[k] for k in self.abaque.index.names)
            if len(inputs) == 1:
                inputs = inputs[0]
            result = self.abaque_dict[inputs]
        except KeyError:
            if len(self.cat_columns) > 0:
                cat_inputs = tuple(processed_input[k] for k in self.cat_columns)
                if len(cat_inputs) == 1:
                    cat_inputs = cat_inputs[0]
                num_candidates = self.num_abaque[cat_inputs]
            else:
                num_candidates = self.index.values

            num_values = np.array([processed_input[k] for k in self.num_columns])
            idx = np.where(num_candidates >= num_values)[0]
            for i, k in enumerate(self.num_columns):
                if len(idx) == 0:
                    processed_input[k] = self.key_characteristics[k]["max"]
                else:
                    processed_input[k] = num_candidates[idx[0], i]
            inputs = tuple(processed_input[k] for k in self.abaque.index.names)
            result = self.abaque_dict[inputs]
        return result

    def load_abaques(
        self,
        data_path,
        file,
        refs=None,
        keys=list[dict],
        values=list,
        rename: dict = None,
        mapping=None,
        filters: list[dict] = None,
        reduce=None,
    ):
        """
        Loads the abaque from a CSV file and applies various transformations.

        Parameters:
        -----------
        data_path : str
            The path to the directory containing the data files.
        file : str
            The name of the CSV file to be loaded.
        refs : list[dict], optional
            List of references for processing column replacements.
        keys : list[dict], optional
            List of dictionaries specifying the keys and their characteristics.
        values : list, optional
            List of column names to be retained in the abaque.
        rename : dict, optional
            Dictionary to rename columns in the abaque.
        mapping : list[dict], optional
            List of mappings to be applied to the columns.
        filters : list[dict], optional
            List of filters to be applied to the columns.
        reduce : list[dict], optional
            List of reduction operations to create new columns.
        """
        try:
            self.abaque = pd.read_csv(os.path.join(data_path, file))
            if rename:
                self.apply_rename(rename)
            if filters:
                self.apply_filters(filters)
            if refs:
                self.process_references(refs, data_path)
            if mapping:
                self.apply_mapping(mapping)
            if reduce:
                self.apply_reduction(reduce)
            if keys:
                self.abaque = self.abaque.fillna("NULL")
                self.get_key_characteristics(keys)
                self.initialize_valid_cat_combinations()
                self.initialize_upper_tresholds()
                self.cat_columns = [k["key_name"] for k in keys if k["key_type"] == "cat"]
                self.num_columns = [k["key_name"] for k in keys if k["key_type"] == "num"]
                if len(self.num_columns) > 0 and len(self.cat_columns) > 0:
                    ## Get list of possible num values for each cat combination
                    self.num_abaque = (
                        self.abaque[self.cat_columns + self.num_columns]
                        .groupby(self.cat_columns)
                        .agg(lambda x: list(x))
                        .to_dict(orient="index")
                    )

                    ## for each cat combination, create a numpy array of possible values, with n column, n being the number of num columns
                    for cat_comb, num_values in self.num_abaque.items():
                        self.num_abaque[cat_comb] = np.array([np.array(v) for k, v in num_values.items()]).T

                self.abaque = self.abaque.set_index([k["key_name"] for k in keys])
                self.abaque = self.abaque[values].copy()
            # if not self.abaque.index.is_lexsorted():

            self.abaque.sort_index(inplace=True)
            self.abaque = self.abaque.groupby(self.abaque.index).head(1)
            self.abaque_dict = self.abaque.to_dict(orient="index")

        except Exception as e:
            print(f"An error occurred: {str(e)}")

    def get_key_characteristics(self, keys):
        """
        Extracts and stores characteristics of the specified keys.

        Parameters:
        -----------
        keys : list[dict]
            List of dictionaries specifying the keys and their characteristics.
        """
        for key in keys:
            if key["key_type"] == "num":
                self.key_characteristics[key["key_name"]] = {
                    "min": self.abaque[key["key_name"]].min(),
                    "max": self.abaque[key["key_name"]].max(),
                }
            elif key["key_type"] == "cat":
                self.key_characteristics[key["key_name"]] = self.abaque[key["key_name"]].unique()

    def process_references(self, refs, data_path):
        """
        Processes reference files to replace column values based on external data.

        Parameters:
        -----------
        refs : list[dict]
            List of references for processing column replacements.
        data_path : str
            The path to the directory containing the reference files.
        """
        for ref in refs:
            try:
                replacement_dict = (
                    pd.read_csv(os.path.join(data_path, ref["file"])).set_index(ref["key"])[ref["value"]].to_dict()
                )
                self.abaque[ref["new_col"]] = self.abaque[ref["col"]].replace(replacement_dict)
            except Exception as e:
                print(f"Error processing references: {str(e)}")

    def apply_rename(self, rename):
        """
        Renames columns in the abaque based on the specified dictionary.
        """
        for elt in rename:
            self.abaque[rename[elt]] = self.abaque[elt]

    def apply_mapping(self, mapping):
        """
        Applies transformation functions to specified columns.

        Parameters:
        -----------
        mapping : list[dict]
            List of mappings to be applied to the columns.
        """
        for m in mapping:
            try:
                self.abaque[m["col"]] = self.abaque[m["col"]].apply(eval(m["function"]))
            except Exception as e:
                print(f"Error applying mapping: {str(e)}")

    def apply_filters(self, filters):
        """
        Applies filters to the specified columns.

        Parameters:
        -----------
        filters : list[dict]
            List of filters to be applied to the columns.
        """
        for f in filters:
            try:
                self.abaque = self.abaque[self.abaque[f["col"]].apply(eval(f["function"]))]
            except Exception as e:
                print(f"Error applying filter: {str(e)}")

    def apply_reduction(self, reduce):
        """
        Reduces multiple columns into a new column based on a specified function.

        Parameters:
        -----------
        reduce : list[dict]
            List of reduction operations to create new columns.
        """
        for r in reduce:
            try:
                self.abaque[r["new_col"]] = self.abaque.apply(
                    lambda row: eval(r["function"])([row[col] for col in r["cols"]]),
                    axis=1,
                )
            except Exception as e:
                print(f"Error applying reduction: {str(e)}")

    def initialize_valid_cat_combinations(self):
        """
        Initializes valid categorical combinations by filtering and deduplicating values.
        """
        if self.abaque is not None:
            cat_keys = [k["key_name"] for k in self.config.get("keys", []) if k["key_type"] == "cat"]
            unique_combinations = self.abaque[cat_keys].drop_duplicates()
            self.valid_cat_combinations = unique_combinations.to_dict(orient="records")

    def initialize_upper_tresholds(self):
        """
        Initializes upper threshold values for numeric keys.
        """
        if self.abaque is not None:
            num_keys = [k["key_name"] for k in self.config.get("keys", []) if k["key_type"] == "num"]
            for key in num_keys:
                self.upper_thresholds[key] = np.array(sorted(self.abaque[key].unique().astype(float)))

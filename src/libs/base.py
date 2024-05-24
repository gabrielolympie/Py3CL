import numpy as np
import pandas as pd
import os


class BaseProcessor:
    def __init__(self, data_path, *args, **kwargs):
        """Define the base class for the processor"""
        self.load(data_path, *args, **kwargs)
        self.preprocess(*args, **kwargs)

    def __str__(self):
        return f"{self.__class__.__name__}({self.__dict})"

    def __dict__(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    def __call__(self, *args, **kwargs):
        """Call the calc function"""
        return self.calc(*args, **kwargs)

    def load(self, *args, **kwargs):
        pass

    def preprocess(self, *args, **kwargs):
        pass

    def calc(self, *args, **kwargs):
        """Based on variable, compute the value of the variable"""
        pass

    @property
    def calc_input(self):
        """Return the valid inputs of the calc function when input is categorical"""
        return {}

    def validate(self, *args, **kwargs):
        """Validate the input of the calc function"""
        for arg, arg_value in kwargs.items():
            if arg_value is not None and not (str(arg_value).lower() == "nan"):
                if arg in self.calc_input:
                    if type(arg_value) == list:
                        for value in arg_value:
                            if value is not None and not (str(value).lower() == "nan"):
                                assert (
                                    value in self.calc_input[arg]
                                ), f"{arg} must be in {self.calc_input[arg]}, got {value}"
                    else:
                        assert (
                            arg_value in self.calc_input[arg]
                        ), f"{arg} must be in {self.calc_input[arg]}, got {arg_value}"


class AggregatedProcessor:
    def __init__(self, data_path, *args, **kwargs):
        """Define the base class for the processor"""
        self.load(data_path, *args, **kwargs)

    def __str__(self):
        return f"{self.__class__.__name__}({self.__dict})"

    def __dict__(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    def __call__(self, *args, **kwargs):
        """Call the calc function"""
        return self.calc(*args, **kwargs)

    @property
    def calc_input(self):
        """Return a dict of inputs for the detailed_calc function.

        For categorical inputs, the value is a list of valid inputs.
        For numerical inputs, the value is "num"

        """
        return {}

    def load(self, data_path):
        """This time, directly loads leaf processor to perform computations"""
        pass

    def calc(self, args, kwargs):
        """Based on variable, compute the value of the variable"""
        pass

    def detailed_calc(self, args, kwargs):
        """Based on variable, compute the value of the variable and output the final value as well as the intermediate values into a dictionary"""
        pass

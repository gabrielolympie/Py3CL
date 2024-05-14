class BaseProcessor:
    def __init__(self, data_path, *args, **kwargs):
        """Define the base class for the processor"""
        self.load(data_path, *args, **kwargs)
        self.preprocess(*args, **kwargs)

    def __str__(self):
        return f"{self.__class__.__name__}({self.__dict})"

    def __dict(self):
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
            if arg_value is not None:
                if arg in self.calc_input:
                    assert (
                        arg_value in self.calc_input[arg]
                    ), f"{arg} must be in {self.calc_input[arg]}"

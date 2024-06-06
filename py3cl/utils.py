import yaml
import dill
import base64


def serialize_function(func):
    """Serialize a function to a base64 encoded string."""
    dumped = dill.dumps(func)
    b64_encoded = base64.b64encode(dumped).decode("utf-8")
    return b64_encoded


def deserialize_function(encoded_func):
    """Deserialize a function from a base64 encoded string."""
    decoded = base64.b64decode(encoded_func.encode("utf-8"))
    func = dill.loads(decoded)
    return func


def save_config(config, filename):
    """Save a configuration dictionary containing lambda functions to a YAML file."""
    serialized_funcs = {k: serialize_function(v) for k, v in config.items()}
    with open(filename, "w") as file:
        yaml.dump(config, file)


def load_config(filename):
    """Load a configuration dictionary containing lambda functions from a YAML file."""
    with open(filename, "r") as file:
        loaded_funcs_yaml = yaml.safe_load(file)
    # loaded_funcs = {k: deserialize_function(v) for k, v in loaded_funcs_yaml.items()}
    return loaded_funcs_yaml



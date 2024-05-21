from libs.abaques import Abaque
from pydantic import BaseModel

class DPEInput(BaseModel):
    postal_code: str
    adress: str = None
    city: str = None
    country: str = None
    type_logement: str = None
    surface_habitable: float = None

# class ParoiInput(BaseModel):


class DPE:
    def __init__(self, configs):
        self.configs = configs
        self.load_abaques(self.configs)
    
    def forward(self, kwargs: DPEInput):
        dpe = kwargs.dict()  # Convert Pydantic model to dictionary

        ## Compute the climatic zone
        dpe['department'] = int(dpe['postal_code'][:2])
        dpe['zone_climatique'] = self.abaques['department']({'id': dpe['department']}, 'zone_climatique')
        dpe['zone_hiver'] = dpe['zone_climatique'][:2]
        ## Calcul d'enveloppe
        return dpe

    def load_abaques(self, configs):
        self.abaques = {}
        for key, value in configs.items():
            print(key)
            self.abaques[key] = Abaque(value)
    
    def get_input_scheme(self):
        # Implementation for returning the input scheme
        pass

    def get_valid_inputs(self):
        # Implementation for returning valid inputs
        pass

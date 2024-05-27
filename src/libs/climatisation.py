from libs.utils import safe_divide
from pydantic import BaseModel
import os
from typing import Optional
from libs.utils import safe_divide, vectorized_safe_divide
import numpy as np

# Rs_ecs
# Abaque(tv049bis_rendement_stockage_ecs.csv)
# Keys: ['type_stockage', 'category_stockage', 'volume_stockage']
# Values: ['Cr']

# Rd_ecs
# Abaque(tv040_rendement_distribution_ecs.csv)
# Keys: ['type_installation', 'type_generateur', 'production_volume_habitable', 'pieces_alimentees_contigues']
# Values: ['rd']

# Rg_ecs
# Abaque(tv047bis_rendement_generation_ecs.csv)
# Keys: ['annee_generateur', 'puissance_nominale']
# Values: ['Rpn', 'Qp0', 'Pveilleuse']

# Rg_ecs_pac
# Abaque(tv047bis_rendement_generation_ecs_pac.csv)
# Keys: ['annee_generateur', 'zone_hiver', 'type_pac']
# Values: ['COP']

# seer_climatisation
# Abaque(tv0xx_seer_clim.csv)
# Keys: ['zone_hiver', 'annee_climatisation']
# Values: ['SEER']


class ClimatisationInput(BaseModel):
    identifiant: str
    annee_installation: float = None
    surface_refroidie: float = None
    type_energie: Optional[str] = None # Electricité, Gaz, Fioul...


class Climatisation:
    def __init__(self, abaques):
        self.abaques = abaques

    def forward(self, dpe, kwargs: ClimatisationInput):
        clim = kwargs.dict()

        Rbth_j_num = dpe['Ai_frj'] + dpe['Asj'] * (dpe['Ai_frj'] > 0 ) # in theory, as Ai fr is zero sur les mois de refroidissement, pas de pb
        Rbth_j_den = dpe['GV'] * (dpe['Textmoy_clim_j'] - dpe['Tint_froids']) * dpe['Nref_froids_j']

        Rbth_j = vectorized_safe_divide(Rbth_j_num, Rbth_j_den)
        Rbth_j[Rbth_j < 0.5] = 0
        clim['Rbth_j']=Rbth_j

        inertie=dpe["inertie_batiment"]
        if inertie == "Légère":
            clim['C_in']=110000 * dpe["surface_habitable"]
        elif inertie == "Moyenne":
            clim['C_in']=165000 * dpe["surface_habitable"]
        else:
            clim['C_in']=260000 * dpe["surface_habitable"]

        a = 1 +  clim['C_in'] / ( dpe['GV'] * 3600 * 15 )

        futj = np.array([safe_divide(a, 1+a) if elt==1 else safe_divide(1 - elt**(-a), 1-elt**(-a-1)) for elt in clim['Rbth_j']])
        futj[clim['Rbth_j'] ==0] = 0
        clim['futj'] = futj


        bfroids_term1 = (dpe['Ai_frj'] + dpe['Asj'] * (dpe['Ai_frj'] > 0 ))/1000
        bfroids_term2 = clim['futj'] * dpe['GV'] * (dpe['Tint_froids'] - dpe['Textmoy_clim_j']) * dpe['Nref_froids_j'] / 1000
        clim['Bfrj'] = bfroids_term1 - bfroids_term2

        clim['EER'] = self.abaques["seer_clim"]({"zone_hiver": dpe["zone_hiver"], "annee_climatisation": clim["annee_installation"]}, "SEER")

        clim['SEER'] = 0.95 * clim['EER']

        clim['Cfr'] = 0.9 * clim['Bfrj'] / clim['SEER']

        clim['Cfr'] = clim['Cfr'] * clim['surface_refroidie'] / dpe['surface_habitable']
        return clim



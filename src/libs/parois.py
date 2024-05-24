from libs.utils import safe_divide
from pydantic import BaseModel
import os

class ParoiInput(BaseModel):
    """
    Represents the input data for a Paroi object.

    Attributes:
        identifiant: The identifier of the wall.
        identifiant_adjacents: The identifiers of the adjacent items, only for walls (used to compute pths). For plancher it can only reference an ouvrant.

        surface_paroi: The surface area of the wall in square meters.
        hauteur: The height/plancher of the wall in meters. None for planchers
        largeur: The width/plancher of the wall in meters. None for planchers

        type_paroi: The type of wall, which can be one of 'Mur', 'Plancher bas', or 'Plancher haut'.
        uparoi: The non-insulated thermal transmittance of the wall in W/(m²·K).
        materiaux: The materials used to construct the wall.
        epaisseur: The thickness of the wall in centimeters.
        isolation: Whether or not the wall is insulated.
        annee_isolation: The year the wall was insulated.
        r_isolant: The thermal resistance of the insulation in m²·K/W.
        epaisseur_isolant: The thickness of the insulation in centimeters.
        effet_joule: Whether or not the wall is affected by the Joule effect.

        # Specifique aux murs
        enduit: Whether or not the wall has a plaster.
        doublage_with_lame_below_15mm: Whether or not the wall has a lining with a thickness below 15mm.
        doublage_with_lame_above_15mm: Whether or not the wall has a lining with a thickness above 15mm.

        # Specifique aux planchers bas
        is_vide_sanitaire: Whether or not the floor has a crawl space.
        is_unheated_underground: Whether or not the floor is under an unheated underground space.
        is_terre_plain: Whether or not the floor is on bare ground.
        surface_immeuble: The surface area of the building in square meters.
        perimeter_immeuble: The perimeter of the building in meters.

        # Specifique aux planchers hauts
        # None

        # Coefficient d'attenuation
        exterior_type_or_local_non_chauffe: The type of exterior wall or non-heated local, which can be one of 'Mur', 'Plancher bas', 'Plancher haut', 'Véranda', or 'Local non chauffé'.
        surface_paroi_contact: The surface area of the wall in contact with the exterior or non-heated local in square meters.
        surface_paroi_local_non_chauffe: The surface area of the wall facing the non-heated local in square meters.
        local_non_chauffe_isole: Whether or not the non-heated local is insulated.

        # Specifique aux verandas
        orientation: The orientation of the veranda, which can be one of 'Nord', 'Sud', 'Est', or 'Ouest'.
    """
    identifiant: str
    identifiant_adjacents: list = None

    # dimensions
    surface_paroi: float
    largeur: float = None
    hauteur: float = None
    inertie: str = None # Leger / Lourd

    # Coefficient de transmission surfacique
    type_paroi: str # ['Mur', 'Plancher bas', 'Plancher haut']
    uparoi: float=None
    materiaux: str=None
    epaisseur: float=None
    isolation: bool=None
    annee_isolation: int=None
    r_isolant: float=None
    epaisseur_isolant: float=None
    effet_joule: bool=None

    # Specifique aux murs
    enduit: bool=None
    doublage_with_lame_below_15mm: bool=None
    doublage_with_lame_above_15mm: bool=None

    # Specifique aux planchers bas
    is_vide_sanitaire: bool=None
    is_unheated_underground: bool=None
    is_terre_plain: bool=None
    surface_immeuble: float=None
    perimeter_immeuble: float=None

    # Specifique aux planchers hauts
    ## None

    # Coefficient d'attenuation
    exterior_type_or_local_non_chauffe: str=None
    surface_paroi_contact: float=None
    surface_paroi_local_non_chauffe: float=None
    local_non_chauffe_isole: bool=None

    # Specifique aux verandas
    orientation: str=None # ['Nord', 'Sud', 'Est', 'Ouest']


class Paroi:
    def __init__(self, abaques):
        self.abaques = abaques

    def forward(self, dpe, kwargs: ParoiInput):
        paroi = kwargs.dict()
        paroi['annee_construction_ou_isolation'] = paroi['annee_isolation'] if paroi['annee_isolation'] is not None else dpe['annee_construction']
        paroi['zone_hiver'] = dpe['zone_hiver']

        # Calc b : coefficient de reduction de deperdition
        if paroi['exterior_type_or_local_non_chauffe'] in self.abaques['coef_reduction_deperdition_exterieur'].key_characteristics['aiu_aue']:
            paroi['b'] = self.abaques['coef_reduction_deperdition_exterieur']({'aiu_aue': paroi['exterior_type_or_local_non_chauffe']}, 'valeur')
        elif paroi['exterior_type_or_local_non_chauffe'] == 'Véranda':
            paroi['b'] = self.abaques['coef_reduction_veranda']({'zone_hiver': paroi['zone_hiver'], 'orientation_veranda': paroi['orientation'], 'isolation_paroi': paroi['isolation']}, 'bver')
        else:
            paroi['aiu_aue'] = safe_divide(paroi['surface_paroi_contact'], paroi['surface_paroi_local_non_chauffe'])
            paroi['uvue'] = self.abaques['local_non_chauffe']({'type_batiment': dpe['type_batiment'], 'local_non_chauffe': paroi['exterior_type_or_local_non_chauffe']}, 'uvue')
            paroi['b'] = self.abaques['coef_reduction_deperdition_local']({'aiu_aue_max': paroi['aiu_aue'], 'aue_isole': paroi['isolation'], 'aiu_isole': paroi['local_non_chauffe_isole'], 'uv_ue': paroi['uvue']}, 'valeur')
        
        # Calc U
        if paroi['uparoi'] is not None:
            paroi['U'] = paroi['uparoi']
        else:
            if paroi['type_paroi'] == 'Mur':
                paroi = self._forward_mur(paroi)
            elif paroi['type_paroi'] == 'Plancher bas':
                paroi = self._forward_plancher_bas(paroi)
            elif paroi['type_paroi'] == 'Plancher haut':
                paroi = self._forward_plancher_haut(paroi)

        return paroi
    
    def _forward_plancher_haut(self, paroi):
        if paroi['materiaux']:
            uparoi_0=self.abaques['uph0']({'materiaux': paroi['materiaux']}, 'uph0')
            uparoi_nu=min(uparoi_0, 2.5)
        else:
            uparoi_nu=2.5
        paroi['U_nu']=uparoi_nu
        if paroi['isolation']==False:
            paroi['U']=uparoi_nu
        elif paroi['isolation'] is None:
            uparoi_tab=self.abaques['uph']({'type_toit': paroi['annee_construction_ou_isolation'], 'zone_hiver': paroi['zone_hiver'], 'effet_joule': paroi['effet_joule']}, 'uph')
            paroi['U']=min(uparoi_0, uparoi_tab)
        else:
            if paroi['r_isolant']:
                paroi['U']=safe_divide(1, safe_divide(1, uparoi_0) + paroi['r_isolant'])
            elif paroi['epaisseur_isolant']:
                paroi['U']=safe_divide(1, safe_divide(1, uparoi_0) + safe_divide(paroi['epaisseur_isolant'], 40))
            else:
                uparoi_tab=self.abaques['uph']({'type_toit': paroi['annee_construction_ou_isolation'], 'zone_hiver': paroi['zone_hiver'], 'effet_joule': paroi['effet_joule']}, 'uph')
                paroi['U']=min(uparoi_0, uparoi_tab)
        return paroi

    def _forward_plancher_bas(self, paroi):
        if paroi['materiaux']:
            uparoi_0=self.abaques['upb0']({'materiaux': paroi['materiaux']}, 'upb0')
            uparoi_nu=min(uparoi_0, 2.0)
        else:
            uparoi_nu=2.0
        paroi['U_nu']=uparoi_nu
        if paroi['isolation']==False:
            paroi['U']=uparoi_nu
        elif paroi['isolation'] is None:
            uparoi_tab=self.abaques['upb']({'annee_construction_max': paroi['annee_construction_ou_isolation'], 'zone_hiver': paroi['zone_hiver'], 'effet_joule': paroi['effet_joule']}, 'upb')
            paroi['U']=min(uparoi_0, uparoi_tab)
        else:
            if paroi['r_isolant']:
                paroi['U']=safe_divide(1, safe_divide(1, uparoi_0) + paroi['r_isolant'])
            elif paroi['epaisseur_isolant']:
                paroi['U']=safe_divide(1, safe_divide(1, uparoi_0) + safe_divide(paroi['epaisseur_isolant'], 42))
            else:
                uparoi_tab=self.abaques['upb']({'annee_construction_max': paroi['annee_construction_ou_isolation'], 'zone_hiver': paroi['zone_hiver'], 'effet_joule': paroi['effet_joule']}, 'upb')
                paroi['U']=min(uparoi_0, uparoi_tab)

        if paroi['is_vide_sanitaire'] or paroi['is_unheated_underground'] or paroi['is_terre_plain']:
            try:
                ssp= 2 * paroi['surface_immeuble'] / paroi['perimeter_immeuble']
            except:
                ssp= 2 * paroi['surface_paroi'] / paroi['perimeter_immeuble']

            if paroi['is_vide_sanitaire'] or paroi['is_unheated_underground']:
                type_tp="other"
            else:
                if paroi["annee_construction"] < 2001:
                    type_tp="tp_pre_2001"
                else:
                    type_tp="tp_post_2001 plein"
            paroi["Upb_sans_tp"]=paroi["U"]
            paroi["U"]=self.abaques['upb_tp']({'type_tp': type_tp, '2S/P': ssp, "Upb":paroi["Upb_sans_tp"]}, 'Value')
        return paroi
    
    def _forward_mur(self, paroi):
        if paroi['materiaux'] and paroi['epaisseur']:
            uparoi_0=self.abaques['umur0']({'umur0_materiaux': paroi['materiaux'], 'epaisseur':paroi['epaisseur']}, 'umur')
            uparoi_nu=min(uparoi_0, 2.5)
        else:
            uparoi_nu=2.5
        paroi['U_nu']=uparoi_nu
        if paroi['isolation']==False:
            r_isolant=0
            if paroi['enduit']:
                r_isolant=0.7
            elif paroi['doublage_with_lame_below_15mm']:
                r_isolant=0.1
            elif paroi['doublage_with_lame_above_15mm']:
                r_isolant=0.21
            paroi['U']=safe_divide(1, safe_divide(1, uparoi_nu) + r_isolant)
        elif paroi['isolation'] is None:
            uparoi_tab=self.abaques['umur']({'annee_construction_max': paroi['annee_construction_ou_isolation'], 'zone_hiver': paroi['zone_hiver'], 'effet_joule': paroi['effet_joule']}, 'umur')
            paroi['U']=min(uparoi_0, uparoi_tab)
        else:
            if paroi['r_isolant']:
                paroi['U']=safe_divide(1, safe_divide(1, uparoi_0) + paroi['r_isolant'])
            elif paroi['epaisseur_isolant']:
                paroi['U']=safe_divide(1, safe_divide(1, uparoi_0) + safe_divide(paroi['epaisseur_isolant'], 40))
            else:
                uparoi_tab=self.abaques['umur']({'annee_construction_max': paroi['annee_construction_ou_isolation'], 'zone_hiver': paroi['zone_hiver'], 'effet_joule': paroi['effet_joule']}, 'umur')
                paroi['U']=min(uparoi_0, uparoi_tab)
        return paroi
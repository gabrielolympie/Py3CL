from libs.utils import safe_divide
from pydantic import BaseModel
import os

class ParoiInput(BaseModel):
    # Surface
    surface_paroi: float

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
    def __init__(self, abaques, dpe):
        self.abaques = abaques
        self.dpe = dpe

    def forward(self, kwargs: ParoiInput):
        paroi = kwargs.dict()
        paroi['annee_construction_ou_isolation'] = paroi['annee_isolation'] if paroi['annee_isolation'] is not None else self.dpe['annee_construction']
        paroi['zone_hiver'] = self.dpe['zone_hiver']

        # Calc b : coefficient de reduction de deperdition
        if paroi['exterior_type_or_local_non_chauffe'] in self.abaques['coef_reduction_deperdition_exterieur'].key_characteristics['aiu_aue']:
            paroi['b'] = self.abaques['coef_reduction_deperdition_exterieur']({'aiu_aue': paroi['exterior_type_or_local_non_chauffe']}, 'valeur')
        elif paroi['exterior_type_or_local_non_chauffe'] == 'Véranda':
            paroi['b'] = self.abaques['coef_reduction_veranda']({'zone_hiver': paroi['zone_hiver'], 'orientation_veranda': paroi['orientation'], 'isolation_paroi': paroi['isolation']}, 'bver')
        else:
            paroi['aiu_aue'] = safe_divide(paroi['surface_paroi_contact'], paroi['surface_paroi_local_non_chauffe'])
            paroi['uvue'] = self.abaques['local_non_chauffe']({'type_batiment': self.dpe['type_batiment'], 'local_non_chauffe': paroi['exterior_type_or_local_non_chauffe']}, 'uvue')
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
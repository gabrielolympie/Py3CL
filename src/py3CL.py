from libs.abaques import Abaque
from libs.parois import ParoiInput, Paroi
from libs.utils import safe_divide
from pydantic import BaseModel
import os

configs_path='../src/configs/'

abaques_configs={
    "department":os.path.join(configs_path,'departments.yaml'),
    "local_non_chauffe":os.path.join(configs_path,'local_non_chauffe.yaml'),
    "coef_reduction_deperdition_local": os.path.join(configs_path,'coef_reduction_deperdition_local.yaml'),
    "coef_reduction_deperdition_exterieur": os.path.join(configs_path,'coef_reduction_deperdition_exterieur.yaml'),
    "coef_reduction_veranda": os.path.join(configs_path,'coef_reduction_veranda.yaml'),
    "umur0":os.path.join(configs_path,'umur0.yaml'),
    "umur":os.path.join(configs_path,'umur.yaml'),
    "upb0":os.path.join(configs_path,'upb0.yaml'),
    "upb":os.path.join(configs_path,'upb.yaml'),
    'upb_tp':os.path.join(configs_path,'upb_tp.yaml'),
    "uph":os.path.join(configs_path,'uph.yaml'),
    "uph0":os.path.join(configs_path,'uph0.yaml'),
    "ug_vitrage":os.path.join(configs_path,'ug_vitrage.yaml'),
    "uw_vitrage":os.path.join(configs_path,'uw_vitrage.yaml'),
    "resistance_additionnelle_vitrage":os.path.join(configs_path,'resistance_additionnelle_vitrage.yaml'),
    "transmission_thermique_baie":os.path.join(configs_path,'transmission_thermique_baie.yaml'),
    "kpth":os.path.join(configs_path,'kpth.yaml'),
    "permeabilite_fenetre":os.path.join(configs_path,'permeabilite_fenetre.yaml'),
    "permeabilite_batiment":os.path.join(configs_path,'permeabilite_batiment.yaml'),
    "renouvellement_air":os.path.join(configs_path,'renouvellement_air.yaml'),
    "coefficient_orientation":os.path.join(configs_path,'coefficient_orientation.yaml'),
    "facteur_solaire":os.path.join(configs_path,'facteur_solaire.yaml'),
    "coef_masques_proches":os.path.join(configs_path,'coef_masques_proches.yaml'),
    "coef_masques_lointain_µhomogene":os.path.join(configs_path,'coef_masques_lointain_homogene.yaml'),
    "coef_ombrage_lointain":os.path.join(configs_path,'coef_ombrage_lointain.yaml'),
    "I0_intermittence":os.path.join(configs_path,'I0_intermittence.yaml'),
    "inertie_batiment":os.path.join(configs_path,'inertie_batiment.yaml'),
    "recovered_ecs_loss":os.path.join(configs_path,'recovered_ecs_loss.yaml'),
    "Re_systeme_chauffage":os.path.join(configs_path,'Re_systeme_chauffage.yaml'),
    "Rd_systeme_chauffage":os.path.join(configs_path,'Rd_systeme_chauffage.yaml'),
    "Rr_systeme_chauffage":os.path.join(configs_path,'Rr_systeme_chauffage.yaml'),
    "Rg":os.path.join(configs_path,'Rg.yaml'),
    "coef_correction_regulation":os.path.join(configs_path,'coef_correction_regulation.yaml'),
    "Rd_ecs":os.path.join(configs_path,'Rd_ecs.yaml'),
    "coef_emplacement_fonctionnement":os.path.join(configs_path,'coef_emplacement_fonctionnement.yaml'),
    "conversion_kwh_co2":os.path.join(configs_path,'conversion_kwh_co2.yaml'),
    "convertion_energie_phi":os.path.join(configs_path,'convertion_energie_phi.yaml'),
}

# department
# Abaque(tv016_departement.csv)
# Keys: ['id']
# Values: ['altmin', 'altmax', 'nref', 'dhref', 'pref', 'c2', 'c3', 'c4', 't_ext_basse', 'e', 'fch', 'fecs_ancienne_m_i', 'fecs_recente_m_i', 'fecs_solaire_m_i', 'fecs_ancienne_i_c', 'fecs_recente_i_c', 'zone_climatique']
        
# local_non_chauffe
# Abaque(tv002_local_non_chauffe.csv)
# Keys: ['type_batiment', 'local_non_chauffe']
# Values: ['uvue']
        
# coef_reduction_deperdition_local
# Abaque(tv001_coefficient_reduction_deperditions.csv)
# Keys: ['aiu_aue_max', 'aue_isole', 'aiu_isole', 'uv_ue']
# Values: ['valeur']
        
# coef_reduction_deperdition_exterieur
# Abaque(tv001_coefficient_reduction_deperditions.csv)
# Keys: ['aiu_aue']
# Values: ['valeur']
        
# coef_reduction_veranda
# Abaque(tv002_veranda.csv)
# Keys: ['zone_hiver', 'orientation_veranda', 'isolation_paroi']
# Values: ['bver']
        
# umur0
# Abaque(tv004_umur0.csv)
# Keys: ['umur0_materiaux', 'epaisseur']
# Values: ['umur']
        
# umur
# Abaque(tv003_umur.csv)
# Keys: ['annee_construction_max', 'zone_hiver', 'effet_joule']
# Values: ['umur']
        
# upb0
# Abaque(tv006_upb0.csv)
# Keys: ['materiaux']
# Values: ['upb0']
        
# upb
# Abaque(tv005_upb.csv)
# Keys: ['annee_construction_max', 'zone_hiver', 'effet_joule']
# Values: ['upb']
        
# upb_tp
# Abaque(tv005bis_upb_terre_plein.csv)
# Keys: ['type_tp', '2S/P', 'Upb']
# Values: ['Value']
        
# uph
# Abaque(tv007_uph.csv)
# Keys: ['type_toit', 'annee_construction_max', 'zone_hiver', 'effet_joule']
# Values: ['uph']
        
# uph0
# Abaque(tv008_uph0.csv)
# Keys: ['materiaux']
# Values: ['uph0']
        
# ug_vitrage
# Abaque(tv009_coefficient_transmission_thermique_vitrage.csv)
# Keys: ['type_vitrage', 'orientation', 'remplissage', 'traitement_vitrage', 'epaisseur_lame']
# Values: ['ug']
        
# uw_vitrage
# Abaque(tv010_coefficient_transmission_thermique_baie.csv)
# Keys: ['type_materiaux', 'type_menuiserie', 'type_baie', 'ug']
# Values: ['uw']
        
# resistance_additionnelle_vitrage
# Abaque(tv011_resistance_additionnelle.csv)
# Keys: ['fermetures']
# Values: ['resistance_additionnelle']
        
# transmission_thermique_baie
# Abaque(tv012_coefficient_transmission_thermique_baie_protection_solaire.csv)
# Keys: ['uw', 'deltar']
# Values: ['ujn']
        
# kpth
# Abaque(tv013_valeur_pont_thermique.csv)
# Keys: ['type_liaison', 'isolation_mur', 'isolation_plancher_bas', 'type_pose', 'retour_isolation', 'largeur_dormant']
# Values: ['k']
        
# permeabilite_fenetre
# Abaque(tv014_permeabilite.csv)
# Keys: ['type_prise_air']
# Values: ['q4paconv']
        
# permeabilite_batiment
# Abaque(tv014_bis_permeabilite.csv)
# Keys: ['type_batiment', 'annee_construction_max']
# Values: ['q4paconv']
        
# renouvellement_air
# Abaque(tv015_bis_valeur_conventionnelle_renouvellement_air.csv)
# Keys: ['type_ventilation']
# Values: ['Qvarepconv', 'Qvasoufconv', 'Smeaconv']
        
# coefficient_orientation
# Abaque(tv020_bis_coefficient_orientation.csv)
# Keys: ['zone_climatique', 'orientation', 'inclination']
# Values: ['c1']
        
# facteur_solaire
# Abaque(tv021_facteur_solaire.csv)
# Keys: ['type_pose', 'materiaux', 'type_baie', 'type_vitrage']
# Values: ['fts']
        
# coef_masques_proches
# Abaque(tv022_coefficient_masques_proches.csv)
# Keys: ['type_masque', 'avance', 'orientation', 'rapport_l1_l2', 'beta_gama', 'angle_superieur_30']
# Values: ['fe1']
        
# coef_masques_lointain_µhomogene
# Abaque(tv023_coefficient_masques_lointains_homogenes.csv)
# Keys: ['hauteur_alpha', 'orientation']
# Values: ['fe2']
        
# coef_ombrage_lointain
# Abaque(tv024_ombrage_obstacle_lointain.csv)
# Keys: ['hauteur', 'orientation', 'secteur']
# Values: ['omb']
        
# I0_intermittence
# Abaque(tv025_intermittence.csv)
# Keys: ['type_batiment', 'type_installation', 'type_chauffage', 'type_regulation', 'type_emetteur', 'inertie', 'equipement_intermittence', 'comptage_individuel']
# Values: ['I0']
        
# inertie_batiment
# Abaque(tv026_classe_inertie.csv)
# Keys: ['inertie_plancher_bas', 'inertie_plancher_haut', 'inertie_mur']
# Values: ['classe_inertie_batiment']
        
# recovered_ecs_loss
# Abaque(tv027_pertes_recuperees_ecs.csv)
# Keys: ['type_installation', 'type_production', 'type_systeme', 'zone_hiver']
# Values: ['prs2']
        
# Re_systeme_chauffage
# Abaque(tv028_rendement_emission_systeme_chauffage.csv)
# Keys: ['type_emetteur']
# Values: ['re']
        
# Rd_systeme_chauffage
# Abaque(tv029_rendement_distribution_systeme_chauffage.csv)
# Keys: ['type_distribution', 'isole']
# Values: ['rd']
        
# Rr_systeme_chauffage
# Abaque(tv030_rendement_regulation_systeme_chauffage.csv)
# Keys: ['type_installation']
# Values: ['rr']
        
# Rg
# Abaque(tv031_rendement_generation.csv)
# Keys: ['type_generateur', 'methode_generation']
# Values: ['rg']
        
# coef_correction_regulation
# Abaque(tv033_coefficient_correction_regulation.csv)
# Keys: ['emetteur']
# Values: ['c_regul']
        
# Rd_ecs
# Abaque(tv040_rendement_distribution_ecs.csv)
# Keys: ['type_installation', 'type_generateur', 'production_volume_habitable', 'pieces_alimentees_contigues']
# Values: ['rd']
        
# coef_emplacement_fonctionnement
# Abaque(tv041_coefficient_emplacement_fonctionnement.csv)
# Keys: ['alimentation']
# Values: ['cef']
        
# conversion_kwh_co2
# Abaque(tv045_conversion_kwh_co2.csv)
# Keys: ['energie', 'type_production']
# Values: ['ratio_co2_kwh', 'conversion_pci_pcs']
        
# convertion_energie_phi
# Abaque(tv044_conversion_kwh_energies_relevees.csv)
# Keys: ['type_energie', 'forme_physique', 'unite']
# Values: ['taux_conversion']


class DPEInput(BaseModel):
    postal_code: str # 5 digits
    adress: str = None
    city: str = None
    country: str = None
    type_batiment: str = None # ['Maison individuelle', 'Logement collectif', 'Tous bâtiments']
    altitude: float = None
    surface_habitable: float = None
    annee_construction: int = None
    parois: list = None


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



class DPE:
    def __init__(self, configs=abaques_configs):
        self.configs = configs
        self.load_abaques(self.configs)
    
    def forward(self, kwargs: DPEInput):
        dpe = kwargs.dict()  # Convert Pydantic model to dictionary

        ## Compute the climatic zone and altitude
        dpe['department'] = int(dpe['postal_code'][:2])
        dpe['zone_climatique'] = self.abaques['department']({'id': dpe['department']}, 'zone_climatique')
        dpe['zone_hiver'] = dpe['zone_climatique'][:2]
        
        if dpe['altitude'] is None:
            dpe['altitude'] = (self.abaques['department']({'id': dpe['department']}, 'altmin') + self.abaques['department']({'id': dpe['department']}, 'altmax') ) / 2
        dpe['t_ext_basse'] = self.abaques['department']({'id': dpe['department']}, 't_ext_basse')

        ## Calcul d'enveloppe
        parois = []
        for paroi in dpe['parois']:
            paroi_input=ParoiInput(**paroi)
            parois.append(Paroi(self.abaques, dpe).forward(paroi_input))
        dpe['parois'] = parois
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

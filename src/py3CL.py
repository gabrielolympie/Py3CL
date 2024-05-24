from libs.abaques import Abaque
from libs.parois import ParoiInput, Paroi
from libs.ouvrants import VitrageInput, Vitrage
from libs.ponts_thermiques import PontThermiqueInput, PontThermique
from libs.utils import safe_divide, vectorized_safe_divide
from pydantic import BaseModel
import os
import numpy as np

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
    "coef_masques_lointain_homogene":os.path.join(configs_path,'coef_masques_lointain_homogene.yaml'),
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
    "zone_info":os.path.join(configs_path,'zone_info.yaml'),
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

# zone_info
# Abaque(tv016bis_departement.csv)
# Keys: ['altitude', 'month', 'zone_climatique']
# Values: ['E(kWh/m²)', 'Text(°C)', 'Nref(19°C)', 'Nref(21°C)', 'DH14(°Ch)', 'DH19(°Ch)', 'DH21(°Ch)']
        

class DPEInput(BaseModel):
    postal_code: str # 5 digits
    adress: str = None
    city: str = None
    country: str = None
    type_batiment: str = None # ['Maison individuelle', 'Logement collectif', 'Tous bâtiments']
    usage: str = "Conventionnel" # ['Conventionnel', 'Dépensier']
    altitude: float = None
    surface_habitable: float = None
    nb_logements: int = 1
    hauteur_sous_plafond: float = None
    annee_construction: int = None

    ## Enveloppe
    parois: dict = None
    vitrages: dict = None
    ponts_thermiques: dict = None

    type_ventilation: str = None
    q4paconv: float = None # permeabilite de l'enveloppe, si isolation faite récemment

    ## Installations
    type_installation:str =None #'Chauffage Individuel', 'Chauffage Collectif'
    type_chauffage:str = None # 'Central', 'Divisé'
    type_regulation:str=None #'Avec régulation pièce par pièce', 'Sans régulation pièce par pièce'
    type_emetteur:str=None #'Planchers chauffant', 'Autres systèmes', 'Air soufflé','Radiateurs'
    equipement_intermittence:str=None #'Absent', 'Central sans minimum de température', 'Central avec minimum de température', 'Par pièce avec minimum de température', 'NULL', 'Central Collectif'
    comptage_individuel:str=None # 'NULL', 'Absent', 'Présent'

class DPE:
    def __init__(self, configs=abaques_configs):
        self.configs = configs
        self.load_abaques(self.configs)

        self.parois_processor = Paroi(self.abaques)
        self.vitrage_processor = Vitrage(self.abaques)
        self.pont_thermique_processor = PontThermique(self.abaques)
        
        self.months = [
            "Janvier",
            "Février",
            "Mars",
            "Avril",
            "Mai",
            "Juin",
            "Juillet",
            "Août",
            "Septembre",
            "Octobre",
            "Novembre",
            "Décembre",
        ]
    
    def forward(self, kwargs: DPEInput):
        dpe = kwargs.dict()  # Convert Pydantic model to dictionary
        ## Compute the climatic zone and altitude
        dpe = self._calc_geographics(dpe)

        # Compute the number of inhabitants
        dpe = self._calc_n_adeq(dpe)

        ## Compute the envelope
        dpe = self.__calc_enveloppe(dpe)

        ## Calcul des deperditions par flux d'airs
        dpe = self._calc_deperdition_flux_air(dpe)

        ## Calcul Inertie
        dpe = self._calc_inertie(dpe)

        ## Calcul deperdition enveloppe
        dpe = self._calc_deperdition_enveloppe(dpe)

        ## Calcul apports solaires
        dpe = self._calc_apports_solaire(dpe)

        ## Besoin de chauffage mois i
        dpe['BVj'] = dpe['GV'] * (1 - dpe['Fj'])

        ## Calcul Coefficient d'intermittence
        dpe['G'] = dpe['GV'] / (dpe['surface_habitable'] * dpe['hauteur_sous_plafond'])
        if dpe['inertie_batiment'] in ['Légère', 'Moyenne']:
            inertie = 'Légère ou Moyenne'
        else:
            inertie = 'Lourde ou Très lourde'
        dpe['INT'] = self.abaques['I0_intermittence']({'type_batiment': dpe['type_batiment'], 'type_installation': dpe['type_installation'], 'type_chauffage': dpe['type_chauffage'], 'type_regulation': dpe['type_regulation'], 'type_emetteur': dpe['type_emetteur'], 'inertie': inertie, 'equipement_intermittence': dpe['equipement_intermittence'], 'comptage_individuel': dpe['comptage_individuel']}, 'I0')




        ## Calcul de la consommation d'éclairage
        # dpe['Nhj'] = np.array([self.abaques['zone_info']({'altitude': dpe['altitude_1'], 'month': elt, 'zone_climatique': dpe['zone_climatique']}, 'Nref(19°C)') for elt in self.months])
        # dpe['Ceclj'] = dpe['surface_habitable'] * 0.9 * 1.4 

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
    
    def _calc_apports_solaire(self, dpe):
        dpe['ssej'] = np.array([vitre['ssej'] for id, vitre in dpe['vitrages'].items()]).sum(axis=0)
        dpe['Asj'] = dpe['ssej'] * dpe['Ej'] * 1000 ## todo : add veranda
        dpe['Aij'] = ((3.18 + 0.34) * dpe['surface_habitable']  + 90 * (132 / 168) * dpe['Nadeq']) * dpe['Nrefj']
        dpe['Xj'] = vectorized_safe_divide(dpe['Asj'] + dpe['Aij'], dpe['GV'] * dpe['Dhj'])
        dpe['Fj'] = vectorized_safe_divide(dpe['Xj'] - dpe['Xj'] ** dpe['coef_inertie'], 1 - dpe['Xj'] ** dpe['coef_inertie'])
        return dpe

    def _calc_n_adeq(self, dpe):
        dpe['surface_habitable_moyenne'] = dpe['surface_habitable'] / dpe['nb_logements']
        if dpe['type_batiment'] == "Maison individuelle":
            t1, t2, c = 30, 70, 0.025
        else:
            t1, t2, c = 10, 50, 0.035
        
        if dpe['surface_habitable_moyenne'] < t1:
            dpe['Nmax'] = 1
        elif dpe['surface_habitable_moyenne'] < t2:
            dpe['Nmax'] = 1.75 - 0.01875 * (t2 - dpe['surface_habitable_moyenne'])
        else:
            dpe['Nmax'] = c * dpe['surface_habitable_moyenne']

        if dpe['Nmax'] < 1.75:
            dpe['Nadeq'] = dpe['Nmax'] * dpe['nb_logements']
        else:
            dpe['Nadeq'] = dpe['nb_logements'] * (1.75 + 0.3 * (dpe['Nmax'] - 1.75))
        return dpe
        


    def _calc_deperdition_enveloppe(self, dpe):
        parois=[paroi for id, paroi in dpe['parois'].items()]
        vitrages=[vitrage for id, vitrage in dpe['vitrages'].items()]
        ponts_thermiques=[pont_thermique for id, pont_thermique in dpe['ponts_thermiques'].items()]
        dpe['DP_mur']=sum([paroi['U'] * paroi['surface_paroi'] * paroi['b'] for paroi in parois if paroi['type_paroi']=='Mur'])
        dpe['DP_pb']=sum([paroi['U'] * paroi['surface_paroi'] * paroi['b'] for paroi in parois if paroi['type_paroi']=='Plancher bas'])
        dpe['DP_ph']=sum([paroi['U'] * paroi['surface_paroi'] * paroi['b'] for paroi in parois if paroi['type_paroi']=='Plancher haut'])
        dpe['DP_vitrage']=sum([vitrage['U'] * vitrage['surface_vitrage'] * vitrage['b'] for vitrage in vitrages])
        dpe['PT'] = sum([pont_thermique['d_pont'] for pont_thermique in ponts_thermiques])
        dpe['DR'] = dpe['Hvent'] + dpe['Hperm']
        dpe['GV'] = dpe['DP_mur'] + dpe['DP_pb'] + dpe['DP_ph'] + dpe['DP_vitrage'] + dpe['PT'] + dpe['DR']
        return dpe


    def _calc_inertie(self, dpe):
        parois = [paroi for id, paroi in dpe['parois'].items()]
        inerties_mur = [(paroi['inertie'], paroi['surface_paroi']) for paroi in parois if paroi['type_paroi']=='Mur']
        inerties_mur = sorted(inerties_mur, key=lambda x: x[1], reverse=True)[0][0] + "e"

        inerties_plancher_bas = [(paroi['inertie'], paroi['surface_paroi']) for paroi in parois if paroi['type_paroi']=='Plancher bas']
        if len(inerties_plancher_bas) > 0:
            inerties_plancher_bas = sorted(inerties_plancher_bas, key=lambda x: x[1], reverse=True)[0][0]
        else:
            inerties_plancher_bas = "Léger"

        inerties_plancher_haut = [(paroi['inertie'], paroi['surface_paroi']) for paroi in parois if paroi['type_paroi']=='Plancher haut']
        if len(inerties_plancher_haut) > 0:
            inerties_plancher_haut = sorted(inerties_plancher_haut, key=lambda x: x[1], reverse=True)[0][0]
        else:
            inerties_plancher_haut = "Léger"

        dpe['inertie_batiment'] = self.abaques['inertie_batiment']({'inertie_plancher_bas': inerties_plancher_bas, 'inertie_plancher_haut': inerties_plancher_haut, 'inertie_mur': inerties_mur}, 'classe_inertie_batiment')
        
        if dpe['inertie_batiment'] == 'Légère':
            dpe['coef_inertie'] = 2.5
        elif dpe['inertie_batiment'] == 'Moyenne':
            dpe['coef_inertie'] = 2.9
        else:
            dpe['coef_inertie'] = 3.6
        return dpe

    def __calc_enveloppe(self, dpe):
        for id, paroi in dpe['parois'].items():
            paroi_input=ParoiInput(**paroi)
            dpe['parois'][id] = self.parois_processor.forward(dpe, paroi_input)

        ## Todo : add veranda

        ## Calcul de vitrages / ouvrants
        for id, vitrage in dpe['vitrages'].items():
            vitrage_input=VitrageInput(**vitrage)
            dpe['vitrages'][id] = self.vitrage_processor.forward(dpe, vitrage_input)
        
        # Todo
        ## Calcul des deperditions par ponts thermiques
        ### Determination des ponts thermiques liés aux parois
        # auto_pths={}
        # for id, paroi in dpe['parois'].items():
        #     if len(paroi['identifiant_adjacents']) > 0:
        #         for identifiant in paroi['identifiant_adjacents']:
        #             if "mur" in id:
        #                 if "mur" in identifiant:
        #                     new_pth_id=f'auto_{id}_{identifiant}'
        #                     auto_pths[new_pth_id] = {'identifiant': new_pth_id, 'longueur_pont': 1, 'type_liaison': 'Menuiserie / Mur', 'isolation_mur': paroi['isolation'], 'isolation_plancher_bas': None, 'type_pose': 'Nu extérieur', 'retour_isolation': 'Avec', 'largeur_dormant': 0.15}


        ponts_thermiques = []
        for id, pont_thermique in dpe['ponts_thermiques'].items():
            pont_thermique_input=PontThermiqueInput(**pont_thermique)
            dpe['ponts_thermiques'][id] = self.pont_thermique_processor.forward(dpe, pont_thermique_input)
        return dpe
    
    def _calc_geographics(self, dpe):
        if dpe['usage'] == "Conventionnel":
            dpe['DH'] = "DH19(°Ch)"
            dpe['Nref'] = "Nref(19°C)"
        else:
            dpe['DH'] = "DH21(°Ch)"
            dpe['Nref'] = "Nref(21°C)"


        dpe['department'] = int(dpe['postal_code'][:2])
        dpe['zone_climatique'] = self.abaques['department']({'id': dpe['department']}, 'zone_climatique')
        if dpe['zone_climatique'][:2] == 'H3':
            dpe['zone_climatique'] = 'H3'
        dpe['zone_hiver'] = dpe['zone_climatique'][:2]
        
        if dpe['altitude'] is None:
            dpe['altitude'] = (self.abaques['department']({'id': dpe['department']}, 'altmin') + self.abaques['department']({'id': dpe['department']}, 'altmax') ) / 2
        
        
        if dpe['altitude'] < 400:
            dpe['altitude_1'] = 400
        elif dpe['altitude'] < 800:
            dpe['altitude_1'] = 800
        else:
            dpe['altitude_1'] = 8000
        
        dpe['t_ext_basse'] = self.abaques['department']({'id': dpe['department']}, 't_ext_basse')

        dpe['Dhj'] = np.array([self.abaques['zone_info']({'altitude': dpe['altitude_1'], 'month': elt, 'zone_climatique': dpe['zone_climatique']}, dpe['DH']) for elt in self.months])
        dpe['Nrefj'] = np.array([self.abaques['zone_info']({'altitude': dpe['altitude_1'], 'month': elt, 'zone_climatique': dpe['zone_climatique']}, dpe['Nref']) for elt in self.months])
        dpe['Ej'] = np.array([self.abaques['zone_info']({'altitude': dpe['altitude_1'], 'month': elt, 'zone_climatique': dpe['zone_climatique']}, 'E(kWh/m²)') for elt in self.months])
        dpe['Textj'] = np.array([self.abaques['zone_info']({'altitude': dpe['altitude_1'], 'month': elt, 'zone_climatique': dpe['zone_climatique']}, 'Text(°C)') for elt in self.months])

        return dpe

    def _calc_deperdition_flux_air(self, dpe):
        
        if dpe['q4paconv'] is None:
            q4paconv = self.abaques['permeabilite_batiment']({'type_batiment': dpe['type_batiment'], 'annee_construction_max': dpe['annee_construction']}, 'q4paconv')
        else:
            q4paconv = dpe['q4paconv']


        sh = dpe['surface_habitable']
        hsp = dpe['hauteur_sous_plafond']

        nb_facade_exposee = len([paroi for id, paroi in dpe['parois'].items() if paroi['type_paroi']=='Mur'])
        if nb_facade_exposee > 1:
            e, f = 0.07, 15
        else:
            e, f = 0.02, 20

        type_ventilation=dpe['type_ventilation']
        qvarepconv = self.abaques['renouvellement_air']({'type_ventilation': type_ventilation}, 'Qvarepconv')
        qvasoufconv = self.abaques['renouvellement_air']({'type_ventilation': type_ventilation}, 'Qvasoufconv')
        smeaconv = self.abaques['renouvellement_air']({'type_ventilation': type_ventilation}, 'Smeaconv')

        ## Somme des surfaces hors plancher bas
        sdep = sum([paroi['surface_paroi'] for id, paroi in dpe['parois'].items() if paroi['type_paroi']!='Plancher bas'])

        q4paenv = q4paconv * sh
        q4pa = q4paenv + 0.45 * smeaconv * sh

        nu_50_num = q4pa
        nu_50_den = (4/50)**(2/3) * sh * hsp
        nu_50 = safe_divide(nu_50_num, nu_50_den)

        Hperm_num = 0.34 * hsp * sh * nu_50 * e
        Hperm_den = 1 + (f / e) * ((qvasoufconv - qvarepconv) / (hsp * nu_50)) ** 2

        dpe['nu_50'] = nu_50
        dpe['nb_facade_exposee'] = nb_facade_exposee
        dpe['surface_parois_exposees'] = sdep
        dpe['q4paconv'] = q4paconv
        dpe['q4paenv'] = q4paenv
        dpe['q4pa'] = q4pa


        dpe['Hvent'] = 0.34 * q4paconv * dpe['surface_habitable']
        dpe['Hperm'] = safe_divide(Hperm_num, Hperm_den)
        return dpe


            

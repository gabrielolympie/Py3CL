from py3cl.libs import (
    BaseProcessor,
    Abaque,
    ParoiInput,
    Paroi,
    VitrageInput,
    Vitrage,
    PontThermiqueInput,
    PontThermique,
    EcsInput,
    ECS,
    ClimatisationInput,
    Climatisation,
    ChauffageInput,
    Chauffage,
    safe_divide,
    vectorized_safe_divide,
)

from pydantic import BaseModel
from typing import Optional
import os
import numpy as np
import logging

# Get the current working directory
dir_path = os.path.dirname(os.path.realpath(__file__))
configs_path = os.path.join(dir_path, "configs")
data_path = os.path.join(dir_path, "data")
# configs_path = "../py3cl/configs/"

abaques_configs = {
    "department": os.path.join(configs_path, "departments.yaml"),
    "local_non_chauffe": os.path.join(configs_path, "local_non_chauffe.yaml"),
    "coef_reduction_deperdition_local": os.path.join(
        configs_path, "coef_reduction_deperdition_local.yaml"
    ),
    "coef_reduction_deperdition_exterieur": os.path.join(
        configs_path, "coef_reduction_deperdition_exterieur.yaml"
    ),
    "coef_reduction_veranda": os.path.join(configs_path, "coef_reduction_veranda.yaml"),
    "umur0": os.path.join(configs_path, "umur0.yaml"),
    "umur": os.path.join(configs_path, "umur.yaml"),
    "upb0": os.path.join(configs_path, "upb0.yaml"),
    "upb": os.path.join(configs_path, "upb.yaml"),
    "upb_tp": os.path.join(configs_path, "upb_tp.yaml"),
    "uph": os.path.join(configs_path, "uph.yaml"),
    "uph0": os.path.join(configs_path, "uph0.yaml"),
    "ug_vitrage": os.path.join(configs_path, "ug_vitrage.yaml"),
    "uw_vitrage": os.path.join(configs_path, "uw_vitrage.yaml"),
    "resistance_additionnelle_vitrage": os.path.join(
        configs_path, "resistance_additionnelle_vitrage.yaml"
    ),
    "transmission_thermique_baie": os.path.join(
        configs_path, "transmission_thermique_baie.yaml"
    ),
    "kpth": os.path.join(configs_path, "kpth.yaml"),
    "permeabilite_fenetre": os.path.join(configs_path, "permeabilite_fenetre.yaml"),
    "permeabilite_batiment": os.path.join(configs_path, "permeabilite_batiment.yaml"),
    "renouvellement_air": os.path.join(configs_path, "renouvellement_air.yaml"),
    "coefficient_orientation": os.path.join(
        configs_path, "coefficient_orientation.yaml"
    ),
    "facteur_solaire": os.path.join(configs_path, "facteur_solaire.yaml"),
    "coef_masques_proches": os.path.join(configs_path, "coef_masques_proches.yaml"),
    "coef_masques_lointain_homogene": os.path.join(
        configs_path, "coef_masques_lointain_homogene.yaml"
    ),
    "coef_ombrage_lointain": os.path.join(configs_path, "coef_ombrage_lointain.yaml"),
    "I0_intermittence": os.path.join(configs_path, "I0_intermittence.yaml"),
    "inertie_batiment": os.path.join(configs_path, "inertie_batiment.yaml"),
    "recovered_ecs_loss": os.path.join(configs_path, "recovered_ecs_loss.yaml"),
    "Re_systeme_chauffage": os.path.join(configs_path, "Re_systeme_chauffage.yaml"),
    "Rd_systeme_chauffage": os.path.join(configs_path, "Rd_systeme_chauffage.yaml"),
    "Rr_systeme_chauffage": os.path.join(configs_path, "Rr_systeme_chauffage.yaml"),
    "Rg": os.path.join(configs_path, "Rg.yaml"),
    "coef_correction_regulation": os.path.join(
        configs_path, "coef_correction_regulation.yaml"
    ),
    "Rd_ecs": os.path.join(configs_path, "Rd_ecs.yaml"),
    "coef_emplacement_fonctionnement": os.path.join(
        configs_path, "coef_emplacement_fonctionnement.yaml"
    ),
    "conversion_kwh_co2": os.path.join(configs_path, "conversion_kwh_co2.yaml"),
    "convertion_energie_phi": os.path.join(configs_path, "convertion_energie_phi.yaml"),
    "zone_info": os.path.join(configs_path, "zone_info.yaml"),
    "fecs": os.path.join(configs_path, "fecs.yaml"),
    "Rs_ecs": os.path.join(configs_path, "Rs_ecs.yaml"),
    "Rg_ecs": os.path.join(configs_path, "Rg_ecs.yaml"),
    "Rg_ecs_pac": os.path.join(configs_path, "Rg_ecs_pac.yaml"),
    "seer_clim": os.path.join(configs_path, "seer_clim.yaml"),
    "heure_eclairage": os.path.join(configs_path, "heure_eclairage.yaml"),
    "scop_pac": os.path.join(configs_path, "scop_pac.yaml"),
    "emission_chauffage": os.path.join(configs_path, "emission_chauffage.yaml"),
    "emission_ecs": os.path.join(configs_path, "emission_ecs.yaml"),
    "emission_froid": os.path.join(configs_path, "emission_froid.yaml"),
    "emission_autre": os.path.join(configs_path, "emission_autre.yaml"),
    "kwh_to_co2": os.path.join(configs_path, "kwh_to_co2.yaml"),
    "dpe": os.path.join(configs_path, "dpe.yaml"),
    "ges": os.path.join(configs_path, "ges.yaml"),
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
# Keys: ['altitude', 'month', 'zone_climatique', 'inertie']
# Values: ['E-pv(kWh/m²)', 'Text(°C)', 'E(kWh/m²)', 'Nref(19°C)', 'DH19(°Ch)', 'DH14(°Ch)', 'Tefs(°C)', 'Nref(21°C)', 'DH21(°Ch)', 'Textmoy_clim(°C)Tcons=26°C', 'Textmoy_clim(°C)Tcons=28°C', 'E_fr(kWh/m²)Tcons=26°C', 'E_fr(kWh/m²)Tcons=28°C', 'Nref(26°C)', 'Nref(28°C)', 'DH26(°Ch)', 'DH28(°Ch)']

# fecs
# Abaque(tv019bis_fecs.csv)
# Keys: ['type_batiment', 'type_installation', 'zone_climatique']
# Values: ['fecs']

# Rs_ecs
# Abaque(tv049bis_rendement_stockage_ecs.csv)
# Keys: ['type_stockage', 'category_stockage', 'volume_stockage']
# Values: ['Cr']

# Rg_ecs
# Abaque(tv047bis_rendement_generation_ecs.csv)
# Keys: ['annee_generateur', 'puissance_nominale']
# Values: ['Rpn', 'Qp0', 'Pveilleuse']

# Rg_ecs_pac
# Abaque(tv047bis_rendement_generation_ecs_pac.csv)
# Keys: ['annee_generateur', 'zone_hiver', 'type_pac']
# Values: ['COP']


# heure_eclairage
# Abaque(tv0xx_heure_ecl.csv)
# Keys: ['month', 'zone_climatique']
# Values: ['Nh']

# scop_pac
# Abaque(tv0xx_scop_pac.csv)
# Keys: ['type_pac', 'zone_hiver', 'annee_installation']
# Values: ['SCOP']

# emission_chauffage
# Abaque(tv045_conversion_kwh_co2.csv)
# Keys: ['type_energie']
# Values: ['taux_conversion', 'conversion_pci_pcs']

# emission_ecs
# Abaque(tv045_conversion_kwh_co2.csv)
# Keys: ['type_energie']
# Values: ['taux_conversion', 'conversion_pci_pcs']

# emission_froid
# Abaque(tv045_conversion_kwh_co2.csv)
# Keys: ['type_energie']
# Values: ['taux_conversion', 'conversion_pci_pcs']

# emission_autre
# Abaque(tv045_conversion_kwh_co2.csv)
# Keys: ['type_energie']
# Values: ['taux_conversion', 'conversion_pci_pcs']

# kwh_to_co2
# Abaque(tv046bis_evaluation_contenu_co2_reseaux.csv)
# Keys: ['departement']
# Values: ['co2']

# dpe
# An error occurred: "None of [Index(['dpe'], dtype='object')] are in the [columns]"
# Abaque(tv0xx_dpe.csv)
# Keys: ['conso_per_square_meter']
# Values: ['dpe']

# ges
# An error occurred: "None of [Index(['ges'], dtype='object')] are in the [columns]"
# Abaque(tv0xx_ges.csv)
# Keys: ['conso_per_square_meter']
# Values: ['ges']


class DPEInput(BaseModel):
    """
    This class represents the input for the DPE (Diagnostic de Performance Énergétique) model.

    Attributes:
        postal_code (str): The postal code of the building. Must be 5 digits.
        address (str, optional): The address of the building.
        city (str, optional): The city where the building is located.
        country (str, optional): The country where the building is located.
        type_batiment (str, optional): The type of the building. Can be 'Maison individuelle', 'Logement collectif', or 'Tous bâtiments'.
        usage (str): The usage of the building. Can be 'Conventionnel' or 'Dépensier'.
        altitude (float, optional): The altitude of the building.
        surface_habitable (float, optional): The habitable surface of the building.
        nb_logements (int): The number of housing units in the building.
        hauteur_sous_plafond (float, optional): The height under the ceiling of the building.
        annee_construction (int, optional): The year the building was constructed.
        parois (dict, optional): The walls of the building.
        vitrages (dict, optional): The glazing of the building.
        ponts_thermiques (dict, optional): The thermal bridges of the building.
        type_ventilation (str, optional): The type of ventilation of the building.
        q4paconv (float, optional): The permeability of the envelope, if insulation was done recently.
        type_installation_fecs (str, optional): The type of solar heating installation. Can be 'Chauffage solaire (seul ou combiné)', 'ECS solaire seule > 5 ans', 'ECS solaire seule ≤ 5 ans', or 'Chauffage + ECS solaire'.
        installations (dict, optional): The installations in the building. Can be ECS, Heating, PAC, etc.
    """

    postal_code: str  # 5 digits
    adress: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    type_batiment: Optional[str] = (
        None  # ['Maison individuelle', 'Logement collectif', 'Tous bâtiments']
    )
    usage: str = "Conventionnel"  # ['Conventionnel', 'Dépensier']
    altitude: Optional[float] = None
    surface_habitable: Optional[float] = None
    nb_logements: int = 1
    hauteur_sous_plafond: Optional[float] = None
    annee_construction: Optional[int] = None

    ## Enveloppe
    parois: Optional[dict] = None
    vitrages: Optional[dict] = None
    ponts_thermiques: Optional[dict] = None

    type_ventilation: Optional[str] = None
    # type_energie_ventilation: Optional[str] = None
    q4paconv: Optional[float] = (
        None  # permeabilite de l'enveloppe, si isolation faite récemment
    )

    ## Installations

    type_installation_fecs: Optional[str] = (
        None  # 'Chauffage solaire (seul ou combiné)', 'ECS solaire seule > 5 ans', 'ECS solaire seule ≤ 5 ans', 'Chauffage + ECS solaire'
    )
    installations: Optional[dict] = None  # ECS, Chauffage, PAC ...


months_days = {
    "Janvier": 31,
    "Février": 28,
    "Mars": 31,
    "Avril": 30,
    "Mai": 31,
    "Juin": 30,
    "Juillet": 31,
    "Août": 31,
    "Septembre": 30,
    "Octobre": 31,
    "Novembre": 30,
    "Décembre": 24,
}


class DPE(BaseProcessor):
    """
    Represents a DPE model with methods to calculate various energy efficiency metrics.

    Attributes:
        configs (dict): A dictionary containing the paths to the configuration files for the DPE model.
        abaques (dict): A dictionary containing the lookup tables for the DPE model.
        parois_processor (Paroi): A Paroi object to process the walls of the building.
        vitrage_processor (Vitrage): A Vitrage object to process the glazing of the building.
        pont_thermique_processor (PontThermique): A PontThermique object to process the thermal bridges of the building.
        ecs_processor (ECS): An ECS object to process the hot water system of the building.
        clim_processor (Climatisation): A Climatisation object to process the air conditioning system of the building.
        chauffage_processor (Chauffage): A Chauffage object to process the heating system of the building.
        months (list): A list of months in French.

    """

    def __init__(self, configs=abaques_configs):
        """
        Initializes a new DPE instance with the given configuration files.

        Args:
            configs (dict): A dictionary containing the paths to the configuration files for the DPE model.
        """
        self.configs = configs
        self.load_abaques(self.configs)
        self.characteristics_corrections = {
            "usage": ["Conventionnel", "Dépensier"],
            "nb_logements": "float",
            "type_batiment": ["Maison individuelle", "Logement collectif"],
        }

        super().__init__(
            self.abaques,
            DPEInput,
            characteristics_corrections=self.characteristics_corrections,
        )

        self.parois_processor = Paroi(self.abaques)
        self.vitrage_processor = Vitrage(self.abaques)
        self.pont_thermique_processor = PontThermique(self.abaques)
        self.ecs_processor = ECS(self.abaques)
        self.clim_processor = Climatisation(self.abaques)
        self.chauffage_processor = Chauffage(self.abaques)

        self.months = list(months_days.keys())

    def define_categorical(self):
        self.categorical_fields = [
            "type_batiment",
            "usage",
            "type_ventilation",
            "type_energie_ventilation",
            "type_installation_fecs",
        ]

    def define_numerical(self):
        self.numerical_fields = [
            "altitude",
            "surface_habitable",
            "hauteur_sous_plafond",
            "annee_construction",
            "q4paconv",
        ]

    def define_abaques(self):
        self.used_abaques = {
            # 'coef_reduction_deperdition_exterieur': {
            #     # Mapping the exterior type to calculate reduction coefficients
            #     'aiu_aue': 'exterior_type_or_local_non_chauffe'
            # },
            "zone_info": {
                "altitude": "altitude",
                "month": "calc_month",
                "zone_climatique": "calc_zone_climatique",
            },
            "fecs": {
                # "type_batiment": "type_batiment",
                "type_installation": "type_installation_fecs",
                "zone_climatique": "calc_zone_climatique",
            },
            "department": {"id": "calc_department"},
            "renouvellement_air": {"type_ventilation": "type_ventilation"},
            # "emission_autre": {
            #     "type_energie": "type_energie_ventilation"
            # },
        }

    def forward(self, kwargs: DPEInput):
        """
        Processes the DPE data using the input parameters to calculate various energy efficiency metrics.

        Args:
            kwargs (DPEInput): Input parameters for the DPE model.

        Returns:
            dict: A dictionary containing the calculated energy efficiency metrics.
        """

        ## Warning you who read this code, each function is used in a given order, changing this order will likelly break the code

        dpe = kwargs.dict()  # Convert Pydantic model to dictionary
        ## Compute the climatic zone and altitude
        dpe = self._calc_geographics(dpe)

        # Compute the number of inhabitants
        dpe = self._calc_n_adeq(dpe)

        ## Compute the envelope
        dpe = self._calc_enveloppe(dpe)

        ## Calcul des deperditions par flux d'airs
        dpe = self._calc_deperdition_flux_air(dpe)

        ## Calcul Inertie
        dpe = self._calc_inertie(dpe)

        ## Get info based on inertie, altitude etc.
        dpe = self._calc_geographics_bis(dpe)

        ## Calcul deperdition enveloppe
        dpe = self._calc_deperdition_enveloppe(dpe)

        ## Calcul apports solaires
        dpe = self._calc_apports_solaire(dpe)

        ## Besoin de chauffage mois i
        dpe["BVj"] = dpe["GV"] * (1 - dpe["Fj"])

        ## Consommation ECS
        dpe = self._calc_consommation_ecs(dpe)

        ## Consommation Froids
        dpe = self._calc_consommation_froids(dpe)

        ## Calcul des besoins d'éclairage
        dpe = self._calc_consommation_eclairage(dpe)

        ## Caclcul consommation auxilliaires

        # Auxiliaire de chauffage
        Q_dw_col_vc_j = np.zeros(12)
        Q_dw_ind_vc_j = np.zeros(12)

        ## Calcul consommation chauffage
        dpe["Bch_hp_j"] = dpe["BVj"] * dpe["Dh_chauffe_j"] / 1000
        ### Pertes recuperes
        #### Distribution Ecs
        Qrec_chauffe_j = (
            0.48 * dpe["Nref_chauffe_j"] * (Q_dw_col_vc_j + Q_dw_ind_vc_j) / 8760
        )
        #### Stockage Ecs
        Qgw_rec_j = 0.48 * dpe["Nref_chauffe_j"] * dpe["Qgw"] / 8760
        ### Generation Chauffage + Ecs
        Qgen_rec_j = 0  # ToDo

        dpe["Bch_j"] = (
            dpe["Bch_hp_j"] - (Qrec_chauffe_j + Qgw_rec_j + Qgen_rec_j) / 1000
        )

        dpe = self._calc_consommation_chauffage(dpe)

        ## Emission primaire
        dpe["C_finale"] = dpe["Cch"] + dpe["Cfr"] + dpe["Cecl"] + dpe["Cecs"]
        dpe["C_primaire"] = (
            dpe["Cch_primaire"]
            + dpe["Cfr_primaire"]
            + dpe["Cecl_primaire"]
            + dpe["Cecs_primaire"]
        )
        dpe["emission_totale"] = (
            dpe["emission_ch"]
            + dpe["emission_fr"]
            + dpe["emission_ecl"]
            + dpe["emission_ecs"]
        )

        ## Per square meter
        dpe["C_finale_m2"] = safe_divide(dpe["C_finale"], dpe["surface_habitable"])
        dpe["C_primaire_m2"] = safe_divide(dpe["C_primaire"], dpe["surface_habitable"])
        dpe["emission_totale_m2"] = safe_divide(
            dpe["emission_totale"], dpe["surface_habitable"]
        )

        ## Compute DPE and GES
        dpe["dpe"] = self.abaques["dpe"](
            {"conso_per_square_meter": dpe["C_primaire_m2"]}, "dpe"
        )
        dpe["ges"] = self.abaques["ges"](
            {"conso_per_square_meter": dpe["emission_totale_m2"]}, "ges"
        )
        return dpe

    def __call__(self, kwargs: DPEInput):
        dpe = self.forward(kwargs)

    def load_abaques(self, configs):
        """
        Loads the lookup tables for the DPE model.

        Args:
            configs (dict): A dictionary containing the paths to the configuration files for the DPE model.
        """
        self.abaques = {}
        for key, value in configs.items():
            print(key)
            self.abaques[key] = Abaque(value, name=key, data_path=data_path)

    def get_input_scheme(self):
        # Implementation for returning the input scheme
        pass

    def get_valid_inputs(self):
        # Implementation for returning valid inputs
        pass

    def _calc_consommation_chauffage(self, dpe):
        """
        Compute the heating consumption of the building.

        Args:
            dpe (dict): Dictionary containing DPE related data.
        """
        chauffages = []
        # total_power=0
        for installation in dpe["installations"]:
            if "chauffage" in installation or "pac" in installation:
                chauffage_input = ChauffageInput(**dpe["installations"][installation])
                dpe["installations"][installation] = self.chauffage_processor.forward(
                    dpe, chauffage_input
                )
                # total_power+=dpe["installations"][installation]["power"]
                chauffages.append(dpe["installations"][installation])

        dpe["Cch"] = np.sum(
            [
                installation["Cch"]
                for id, installation in dpe["installations"].items()
                if (("chauffage" in id) or ("pac" in id))
            ]
        )
        dpe["Cch_primaire"] = np.sum(
            [
                installation["Cch_primaire"]
                for id, installation in dpe["installations"].items()
                if (("chauffage" in id) or ("pac" in id))
            ]
        )
        dpe["emission_ch"] = np.sum(
            [
                installation["emission_ch"]
                for id, installation in dpe["installations"].items()
                if (("chauffage" in id) or ("pac" in id))
            ]
        )
        return dpe

    def _calc_consommation_froids(self, dpe):
        """
        Compute the cold consumption of the building.

        Args:
            dpe (dict): Dictionary containing DPE related data.
        """

        n_clim = 0
        for installation in dpe["installations"]:
            if "clim" in installation:
                clim_input = ClimatisationInput(**dpe["installations"][installation])
                dpe["installations"][installation] = self.clim_processor.forward(
                    dpe, clim_input
                )
                n_clim += 1

        dpe["Cfr"] = np.sum(
            [
                installation["Cfr"]
                for id, installation in dpe["installations"].items()
                if "clim" in id
            ]
        )
        dpe["Cfr_primaire"] = np.sum(
            [
                installation["Cfr_primaire"]
                for id, installation in dpe["installations"].items()
                if "clim" in id
            ]
        )
        dpe["emission_fr"] = np.sum(
            [
                installation["emission_fr"]
                for id, installation in dpe["installations"].items()
                if "clim" in id
            ]
        )
        return dpe

    def _calc_consommation_eclairage(self, dpe):
        """
        Compute the lighting consumption of the building.

        Args:
            dpe (dict): Dictionary containing DPE related data.
        """
        Pecl = 1.4
        C = 0.9
        dpe["Cecl_j"] = Pecl * 0.9 * dpe["Nhj"] * dpe["surface_habitable"]
        dpe["Cecl"] = dpe["Cecl_j"].sum() / 1000
        dpe["coef_emission_ecl"] = 0.079

        dpe["Cecl_primaire"] = dpe["Cecl"] * 2.3
        dpe["emission_ecl"] = dpe["Cecl"] * dpe["coef_emission_ecl"]
        return dpe

    def _calc_consommation_ecs(self, dpe):
        """
        Compute the hot water consumption of the building.

        Args:
            dpe (dict): Dictionary containing DPE related data.
        """
        dpe["Tefsj"] = np.array(
            [
                self.abaques["zone_info"](
                    {
                        "inertie": dpe["inertie_globale"],
                        "altitude": dpe["altitude_1"],
                        "month": elt,
                        "zone_climatique": dpe["zone_climatique"],
                    },
                    "Tefs(°C)",
                )
                for elt in self.months
            ]
        )

        if dpe["usage"] == "Conventionnel":
            dpe["Nlmoy"] = 56
        else:
            dpe["Nlmoy"] = 79

        dpe["nj"] = np.array(list(map(lambda x: months_days[x], self.months)))
        dpe["Becsj"] = (
            1.163 * dpe["Nadeq"] * dpe["Nlmoy"] * (40 - dpe["Tefsj"]) * dpe["nj"]
        )
        dpe["Becs"] = dpe["Becsj"].sum()

        calc_type_batiment = dpe["type_batiment"]
        if dpe["type_installation_fecs"] and dpe['type_installation_fecs'] != 'Unknown or Empty':
            dpe["fecs"] = self.abaques["fecs"](
                {
                    "type_batiment": calc_type_batiment,
                    "type_installation": dpe["type_installation_fecs"],
                    "zone_climatique": dpe["zone_climatique"],
                },
                "fecs",
            )
        else:
            dpe["fecs"] = 0

        for installation in dpe["installations"]:
            if "ecs" in installation:
                ecs_input = EcsInput(**dpe["installations"][installation])
                dpe["installations"][installation] = self.ecs_processor.forward(
                    dpe, ecs_input
                )

        dpe["Iecs"] = np.mean(
            [
                installation["Iecs"]
                for id, installation in dpe["installations"].items()
                if "ecs" in id
            ]
        )
        dpe["Qgw"] = np.mean(
            [
                installation["Qgw"]
                for id, installation in dpe["installations"].items()
                if "ecs" in id
            ]
        )
        dpe["Cecs"] = np.mean(
            [
                installation["Cecs"]
                for id, installation in dpe["installations"].items()
                if "ecs" in id
            ]
        )
        dpe["Cecs_primaire"] = np.mean(
            [
                installation["Cecs_primaire"]
                for id, installation in dpe["installations"].items()
                if "ecs" in id
            ]
        )
        dpe["emission_ecs"] = np.mean(
            [
                installation["emission_ecs"]
                for id, installation in dpe["installations"].items()
                if "ecs" in id
            ]
        )
        return dpe

    def _calc_apports_solaire(self, dpe):
        """
        Compute the solar gains of the building.

        Args:
            dpe (dict): Dictionary containing DPE related data.
        """

        dpe["ssej"] = np.array(
            [vitre["ssej"] for id, vitre in dpe["vitrages"].items()]
        ).sum(axis=0)
        dpe["Asj"] = dpe["ssej"] * dpe["Ej"] * 1000  ## todo : add veranda

        dpe["Ai_chj"] = (
            (3.18 + 0.34) * dpe["surface_habitable"] + 90 * (132 / 168) * dpe["Nadeq"]
        ) * dpe["Nref_chauffe_j"]
        dpe["Ai_frj"] = (
            (3.18 + 0.34) * dpe["surface_habitable"] + 90 * (132 / 168) * dpe["Nadeq"]
        ) * dpe["Nref_froids_j"]
        dpe["Aij"] = dpe["Ai_chj"] + dpe["Ai_frj"]
        dpe["Xj"] = vectorized_safe_divide(
            dpe["Asj"] + dpe["Aij"], dpe["GV"] * dpe["DHj"]
        )
        dpe["Fj"] = vectorized_safe_divide(
            dpe["Xj"] - dpe["Xj"] ** dpe["coef_inertie"],
            1 - dpe["Xj"] ** dpe["coef_inertie"],
        )
        return dpe

    def _calc_n_adeq(self, dpe):
        """
        Compute the number of inhabitants.

        Args:
            dpe (dict): Dictionary containing DPE related data.
        """
        dpe["surface_habitable_moyenne"] = (
            dpe["surface_habitable"] / dpe["nb_logements"]
        )
        if dpe["type_batiment"] == "Maison individuelle":
            t1, t2, c = 30, 70, 0.025
        else:
            t1, t2, c = 10, 50, 0.035

        if dpe["surface_habitable_moyenne"] < t1:
            dpe["Nmax"] = 1
        elif dpe["surface_habitable_moyenne"] < t2:
            dpe["Nmax"] = 1.75 - 0.01875 * (t2 - dpe["surface_habitable_moyenne"])
        else:
            dpe["Nmax"] = c * dpe["surface_habitable_moyenne"]

        if dpe["Nmax"] < 1.75:
            dpe["Nadeq"] = dpe["Nmax"] * dpe["nb_logements"]
        else:
            dpe["Nadeq"] = dpe["nb_logements"] * (1.75 + 0.3 * (dpe["Nmax"] - 1.75))
        return dpe

    def _calc_deperdition_enveloppe(self, dpe):
        """
        Compute the envelope heat loss of the building.

        Args:
            dpe (dict): Dictionary containing DPE related data.
        """
        parois = [paroi for id, paroi in dpe["parois"].items()]
        vitrages = [vitrage for id, vitrage in dpe["vitrages"].items()]
        ponts_thermiques = [
            pont_thermique for id, pont_thermique in dpe["ponts_thermiques"].items()
        ]
        dpe["DP_mur"] = sum(
            [
                paroi["U"] * paroi["surface_paroi"] * paroi["b"]
                for paroi in parois
                if "mur" in paroi["identifiant"]
            ]
        )
        dpe["DP_pb"] = sum(
            [
                paroi["U"] * paroi["surface_paroi"] * paroi["b"]
                for paroi in parois
                if "plancher_bas" in paroi["identifiant"]
            ]
        )
        dpe["DP_ph"] = sum(
            [
                paroi["U"] * paroi["surface_paroi"] * paroi["b"]
                for paroi in parois
                if "planche_haut" in paroi["identifiant"]
            ]
        )
        dpe["DP_vitrage"] = sum(
            [
                vitrage["U"] * vitrage["surface_vitrage"] * vitrage["b"]
                for vitrage in vitrages
            ]
        )
        dpe["PT"] = sum(
            [pont_thermique["d_pont"] for pont_thermique in ponts_thermiques]
        )
        dpe["DR"] = dpe["Hvent"] + dpe["Hperm"]
        dpe["GV"] = (
            dpe["DP_mur"]
            + dpe["DP_pb"]
            + dpe["DP_ph"]
            + dpe["DP_vitrage"]
            + dpe["PT"]
            + dpe["DR"]
        )
        return dpe

    def _calc_inertie(self, dpe):
        """
        Compute the inertia of the building.

        Args:
            dpe (dict): Dictionary containing DPE related data.
        """
        parois = [paroi for id, paroi in dpe["parois"].items()]
        inerties_mur = [
            (paroi["inertie"], paroi["surface_paroi"])
            for paroi in parois
            if "mur" in paroi["identifiant"]
        ]
        inerties_mur = sorted(inerties_mur, key=lambda x: x[1], reverse=True)[0][0]
        if inerties_mur == "Léger":
            inerties_mur = "Légère"
        else:
            inerties_mur = "Lourde"

        inerties_plancher_bas = [
            (paroi["inertie"], paroi["surface_paroi"])
            for paroi in parois
            if "plancher_bas" in paroi["identifiant"]
        ]
        if len(inerties_plancher_bas) > 0:
            inerties_plancher_bas = sorted(
                inerties_plancher_bas, key=lambda x: x[1], reverse=True
            )[0][0]
        else:
            inerties_plancher_bas = "Léger"

        inerties_plancher_haut = [
            (paroi["inertie"], paroi["surface_paroi"])
            for paroi in parois
            if "plancher_haut" in paroi["identifiant"]
        ]
        if len(inerties_plancher_haut) > 0:
            inerties_plancher_haut = sorted(
                inerties_plancher_haut, key=lambda x: x[1], reverse=True
            )[0][0]
        else:
            inerties_plancher_haut = "Léger"

        dpe["inertie_batiment"] = self.abaques["inertie_batiment"](
            {
                "inertie_plancher_bas": inerties_plancher_bas,
                "inertie_plancher_haut": inerties_plancher_haut,
                "inertie_mur": inerties_mur,
            },
            "classe_inertie_batiment",
        )

        if dpe["inertie_batiment"] == "Légère":
            dpe["coef_inertie"] = 2.5
        elif dpe["inertie_batiment"] == "Moyenne":
            dpe["coef_inertie"] = 2.9
        else:
            dpe["coef_inertie"] = 3.6

        if dpe["inertie_batiment"] in ["Légère", "Moyenne"]:
            dpe["inertie_globale"] = "Légère ou Moyenne"
        else:
            dpe["inertie_globale"] = "Lourde ou Très lourde"
        return dpe

    def _calc_enveloppe(self, dpe):
        """
        Compute the envelope of the building.

        Args:
            dpe (dict): Dictionary containing DPE related data.
        """
        for id, paroi in dpe["parois"].items():
            paroi_input = ParoiInput(**paroi)
            dpe["parois"][id] = self.parois_processor.forward(dpe, paroi_input)

        ## Todo : add veranda

        ## Calcul de vitrages / ouvrants
        for id, vitrage in dpe["vitrages"].items():
            vitrage_input = VitrageInput(**vitrage)
            dpe["vitrages"][id] = self.vitrage_processor.forward(dpe, vitrage_input)

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
        for id, pont_thermique in dpe["ponts_thermiques"].items():
            
            pont_thermique_input = PontThermiqueInput(**pont_thermique)
            
            
            dpe["ponts_thermiques"][id] = self.pont_thermique_processor.forward(
                dpe, pont_thermique_input
            )
        return dpe

    def _calc_geographics(self, dpe):
        """
        Compute the geographic data of the building.

        Args:
            dpe (dict): Dictionary containing DPE related data.
        """
        if dpe["usage"] == "Conventionnel":
            dpe["DH_chauffe"] = "DH19(°Ch)"
            dpe["DH_froids"] = "DH28(°Ch)"
            dpe["Nref_chauffe"] = "Nref(19°C)"
            dpe["Nref_froids"] = "Nref(28°C)"
            dpe["Textmoy_clim"] = "Textmoy_clim(°C)Tcons=26°C"
            dpe["Tint_froids"] = 28
            dpe["Tint_chauffe"] = 19
            dpe["E_fr"] = "E_fr(kWh/m²)Tcons=28°C"
        else:
            dpe["DH_chauffe"] = "DH21(°Ch)"
            dpe["Nref_chauffe"] = "Nref(21°C)"
            dpe["DH_froids"] = "DH26(°Ch)"
            dpe["Nref_froids"] = "Nref(26°C)"
            dpe["Textmoy_clim"] = "Textmoy_clim(°C)Tcons=28°C"
            dpe["Tint_froids"] = 26
            dpe["Tint_chauffe"] = 21
            dpe["E_fr"] = "E_fr(kWh/m²)Tcons=26°C"

        dpe["department"] = int(dpe["postal_code"][:2])
        dpe["coef_co2_elec_dpt"] = self.abaques["kwh_to_co2"](
            {"departement": dpe["department"]}, "co2"
        )
        dpe["zone_climatique"] = self.abaques["department"](
            {"id": dpe["department"]}, "zone_climatique"
        )
        if dpe["zone_climatique"][:2] == "H3":
            dpe["zone_climatique"] = "H3"
        dpe["zone_hiver"] = dpe["zone_climatique"][:2]

        if dpe["altitude"] is None:
            dpe["altitude"] = (
                self.abaques["department"]({"id": dpe["department"]}, "altmin")
                + self.abaques["department"]({"id": dpe["department"]}, "altmax")
            ) / 2

        return dpe

    def _calc_geographics_bis(self, dpe):
        """
        Compute the geographic data of the building.

        Args:
            dpe (dict): Dictionary containing DPE related data.
        """
        if dpe["altitude"] < 400:
            dpe["altitude_1"] = 400
        elif dpe["altitude"] < 800:
            dpe["altitude_1"] = 800
        else:
            dpe["altitude_1"] = 8000

        dpe["t_ext_basse"] = self.abaques["department"](
            {"id": dpe["department"]}, "t_ext_basse"
        )

        dpe["Dh_chauffe_j"] = np.array(
            [
                self.abaques["zone_info"](
                    {
                        "inertie": dpe["inertie_globale"],
                        "altitude": dpe["altitude_1"],
                        "month": elt,
                        "zone_climatique": dpe["zone_climatique"],
                    },
                    dpe["DH_chauffe"],
                )
                for elt in self.months
            ]
        )

        dpe["Dh_froids_j"] = np.array(
            [
                self.abaques["zone_info"](
                    {
                        "inertie": dpe["inertie_globale"],
                        "altitude": dpe["altitude_1"],
                        "month": elt,
                        "zone_climatique": dpe["zone_climatique"],
                    },
                    dpe["DH_froids"],
                )
                for elt in self.months
            ]
        )

        dpe["Textmoy_clim_j"] = np.array(
            [
                self.abaques["zone_info"](
                    {
                        "inertie": dpe["inertie_globale"],
                        "altitude": dpe["altitude_1"],
                        "month": elt,
                        "zone_climatique": dpe["zone_climatique"],
                    },
                    dpe["Textmoy_clim"],
                )
                for elt in self.months
            ]
        )

        dpe["Nref_chauffe_j"] = np.array(
            [
                self.abaques["zone_info"](
                    {
                        "inertie": dpe["inertie_globale"],
                        "altitude": dpe["altitude_1"],
                        "month": elt,
                        "zone_climatique": dpe["zone_climatique"],
                    },
                    dpe["Nref_chauffe"],
                )
                for elt in self.months
            ]
        )

        dpe["Nref_froids_j"] = np.array(
            [
                self.abaques["zone_info"](
                    {
                        "inertie": dpe["inertie_globale"],
                        "altitude": dpe["altitude_1"],
                        "month": elt,
                        "zone_climatique": dpe["zone_climatique"],
                    },
                    dpe["Nref_froids"],
                )
                for elt in self.months
            ]
        )

        dpe["DHj"] = dpe["Dh_chauffe_j"] + dpe["Dh_froids_j"]
        dpe["Nrefj"] = dpe["Nref_chauffe_j"] + dpe["Nref_froids_j"]

        dpe["E_chauffe_j"] = np.array(
            [
                self.abaques["zone_info"](
                    {
                        "inertie": dpe["inertie_globale"],
                        "altitude": dpe["altitude_1"],
                        "month": elt,
                        "zone_climatique": dpe["zone_climatique"],
                    },
                    "E(kWh/m²)",
                )
                for elt in self.months
            ]
        )

        dpe["Nhj"] = np.array(
            [
                self.abaques["heure_eclairage"](
                    {"month": elt, "zone_climatique": dpe["zone_climatique"]}, "Nh"
                )
                for elt in self.months
            ]
        )

        dpe["E_froids_j"] = np.array(
            [
                self.abaques["zone_info"](
                    {
                        "inertie": dpe["inertie_globale"],
                        "altitude": dpe["altitude_1"],
                        "month": elt,
                        "zone_climatique": dpe["zone_climatique"],
                    },
                    dpe["E_fr"],
                )
                for elt in self.months
            ]
        )
        dpe["Ej"] = dpe["E_chauffe_j"] + dpe["E_froids_j"]

        dpe["Textj"] = np.array(
            [
                self.abaques["zone_info"](
                    {
                        "inertie": dpe["inertie_globale"],
                        "altitude": dpe["altitude_1"],
                        "month": elt,
                        "zone_climatique": dpe["zone_climatique"],
                    },
                    "Text(°C)",
                )
                for elt in self.months
            ]
        )
        return dpe

    def _calc_deperdition_flux_air(self, dpe):
        """
        Compute the air flow heat loss of the building.

        Args:
            dpe (dict): Dictionary containing DPE related data.
        """

        if dpe["q4paconv"] is None or dpe["q4paconv"] == "Unknown or Empty":
            q4paconv = self.abaques["permeabilite_batiment"](
                {
                    "type_batiment": dpe["type_batiment"],
                    "annee_construction_max": dpe["annee_construction"],
                },
                "q4paconv",
            )
        else:
            q4paconv = dpe["q4paconv"]

        sh = dpe["surface_habitable"]
        hsp = dpe["hauteur_sous_plafond"]

        nb_facade_exposee = len(
            [
                paroi
                for id, paroi in dpe["parois"].items()
                if "mur" in paroi["identifiant"]
            ]
        )
        if nb_facade_exposee > 1:
            e, f = 0.07, 15
        else:
            e, f = 0.02, 20

        type_ventilation = dpe["type_ventilation"]
        qvarepconv = self.abaques["renouvellement_air"](
            {"type_ventilation": type_ventilation}, "Qvarepconv"
        )
        qvasoufconv = self.abaques["renouvellement_air"](
            {"type_ventilation": type_ventilation}, "Qvasoufconv"
        )
        smeaconv = self.abaques["renouvellement_air"](
            {"type_ventilation": type_ventilation}, "Smeaconv"
        )

        ## Somme des surfaces hors plancher bas
        sdep = sum(
            [
                paroi["surface_paroi"]
                for id, paroi in dpe["parois"].items()
                if "plancher_bas" not in paroi["identifiant"]
            ]
        )

        q4paenv = q4paconv * sh
        q4pa = q4paenv + 0.45 * smeaconv * sh

        nu_50_num = q4pa
        nu_50_den = (4 / 50) ** (2 / 3) * sh * hsp
        nu_50 = safe_divide(nu_50_num, nu_50_den)

        Hperm_num = 0.34 * hsp * sh * nu_50 * e
        Hperm_den = (
            1 + (f / e) * safe_divide(qvasoufconv - qvarepconv, hsp * nu_50) ** 2
        )

        dpe["nu_50"] = nu_50
        dpe["nb_facade_exposee"] = nb_facade_exposee
        dpe["surface_parois_exposees"] = sdep
        dpe["q4paconv"] = q4paconv
        dpe["q4paenv"] = q4paenv
        dpe["q4pa"] = q4pa

        dpe["Hvent"] = 0.34 * q4paconv * dpe["surface_habitable"]
        dpe["Hperm"] = safe_divide(Hperm_num, Hperm_den)
        return dpe

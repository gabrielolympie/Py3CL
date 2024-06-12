import pandas as pd
import os
import numpy as np
import sys
from tqdm.auto import tqdm
import gradio as gr
import pretty_errors

sys.path.append(".")
from py3cl import DPE, DPEInput, abaques_configs

pd.set_option("display.max_columns", 500)


murs = [f"mur_{i}" for i in range(6)]
ph = [f"plancher_haut_{i}" for i in range(2)]
pb = [f"plancher_bas_{i}" for i in range(2)]
parois = murs + ph + pb

ouvrants = [f"vitrage_{i}" for i in range(10)]
id_adjacents = parois + ouvrants
# verandas=[f"veranda{i}" for i in range(2)]
ponts_thermiques = [f"pont_thermique_saisie_{i}" for i in range(20)]
ecs = [f"ecs_{i}" for i in range(3)]
clims = [f"clim_{i}" for i in range(1)]
chauffages = [f"chauffage_{i}" for i in range(3)]


input_descriptors = {
    "hauteur": {"name": "Hauteur", "description": "La hauteur du mur en mètres."},
    "fermetures": {
        "name": "Fermetures",
        "description": "Le type de dispositif de fermeture pour la fenêtre (par exemple, volets, stores).",
    },
    "exterior_type_or_local_non_chauffe": {
        "name": 'Type de d"extérieur ou Local Non Chauffé',
        "description": 'Le type de zone à l"extérieur du mur ou de la paroi déperditive',
    },
    "Pnom": {
        "name": "Puissance Nominale",
        "description": "Puissance nominale du générateur en kW.",
    },
    "largeur": {"name": "Largeur", "description": "La largeur du mur en mètres."},
    "surface_refroidie": {
        "name": "Surface Refroidie",
        "description": "Surface refroidie par le système de climatisation en mètres carrés.",
    },
    "q4paconv": {
        "name": "Perméabilité de l'Enveloppe (Q4Paconv)",
        "description": "Perméabilité de l'enveloppe, si l'isolation a été récemment réalisée. Laisser vide si inconnu",
    },
    "type_pac": {
        "name": "Type de Pompe à Chaleur",
        "description": "Type de pompe à chaleur utilisée, le cas échéant.",
    },
    "type_pose": {
        "name": "Type de Pose",
        "description": "Type de pose du cadre de la fenêtre ou d'une structure similaire.",
    },
    "is_terre_plain": {
        "name": "Est en Terre-plein",
        "description": "Indique si le sol sous le plancher bas est en terre-plein.",
    },
    "adress": {"name": "Adresse", "description": "L'adresse du bâtiment."},
    "altitude": {"name": "Altitude", "description": "L'altitude du bâtiment."},
    "masque_proche_avance": {
        "name": "Distance de l'Élément d'Ombrage Proche",
        "description": "La distance entre la fenêtre et l'élément d'ombrage proche (mètres).",
    },
    "surface_paroi_contact": {
        "name": "Surface de Contact avec l'Extérieur",
        "description": "La surface du mur en contact avec l'extérieur ou un local non chauffé en mètres carrés.",
    },
    "type_regulation_intermittence": {
        "name": "Type de Régulation Intermittence",
        "description": "Type de régulation pour l'intermittence.",
    },
    "largeur_dormant": {
        "name": "Largeur du Dormant",
        "description": "Largeur du dormant en mètres",
    },
    "local_non_chauffe_isole": {
        "name": "Local Non Chauffé Isolé",
        "description": "Indique si le local non chauffé à l'extérieur de la paroi déperditive est isolé.",
    },
    "production_en_volume_habitable": {
        "name": "Générateur dans le Volume Habitable",
        "description": "Indique si le générateur est dans le volume habitable ou non.",
    },
    "identifiant_adjacents": {
        "name": "Identifiants Adjoints",
        "description": "Les identifiants des éléments adjacents, uniquement pour les murs, vitres et planchers.",
    },
    "usage": {
        "name": "Usage",
        "description": 'L\'usage du bâtiment. Peut être "Conventionnel" ou "Dépensier".',
    },
    "orientation": {
        "name": "Orientation",
        "description": "L'orientation du mur (pour l'exposition solaire).",
    },
    "isolation": {"name": "Isolation", "description": "Indique si le mur est isolé."},
    "type_regulation": {
        "name": "Type de Régulation",
        "description": "Type de régulation.",
    },
    "type_chauffage": {
        "name": "Type de Chauffage",
        "description": 'Type général de chauffage, par exemple "Central", "Divisé".',
    },
    "type_menuiserie": {
        "name": "Type de Menuiserie",
        "description": "Le type de fenêtre ou de porte (par exemple, battante, à auvent, fixe).",
    },
    "perimeter_immeuble": {
        "name": "Périmètre de l'Immeuble",
        "description": "Le périmètre du bâtiment en mètres (utilisé uniquement en cas de plancher bas donnant sur un local non chauffé, laisser vide sinon).",
    },
    "masque_proche_angle_superieur_30": {
        "name": "Angle de l'Élément d'Ombrage Proche",
        "description": "Prendre l\angle entre l'horizontale et la droite allant du milieu de la fenetre au sommet de l'element d'ombrage proche.",
    },
    "is_unheated_underground": {
        "name": "Est en Sous-Sol Non Chauffé",
        "description": "Indique si le plancher bas donne sur un sous-sol non chauffé.",
    },
    "nb_logements": {
        "name": "Nombre de Logements",
        "description": "Le nombre de logements dans le bâtiment (pour une maison ou un appartement simple, mettre 1).",
    },
    "epaisseur": {
        "name": "Épaisseur",
        "description": "L'épaisseur du mur en centimètres.",
    },
    "ponts_thermiques": {
        "name": "Ponts Thermiques",
        "description": "Les ponts thermiques du bâtiment.",
    },
    "isolation_plancher_bas": {
        "name": "Isolation du Plancher Bas",
        "description": "Type d'isolation du plancher bas.",
    },
    "postal_code": {
        "name": "Code Postal",
        "description": "Le code postal du bâtiment. Doit comporter 5 chiffres.",
    },
    "type_energie": {
        "name": "Type d'Énergie",
        "description": 'Type d\'énergie utilisée pour le chauffage, par exemple "Électricité", "Gaz".',
    },
    "epaisseur_isolant": {
        "name": "Épaisseur de l'Isolant",
        "description": "L'épaisseur de l'isolant en centimètres.",
    },
    "ombrage_lointain_orientation": {
        "name": "Orientation de l'Élément d'Ombrage Lointain",
        "description": "L'orientation de la facade étant occultée par des masques lointains",
    },
    "type_distribution": {
        "name": "Type de Distribution",
        "description": "Type de système de distribution utilisé dans le système de chauffage.",
    },
    "largeur_vitrage": {
        "name": "Largeur du Vitrage",
        "description": "La largeur de la fenêtre en mètres.",
    },
    "annee_installation": {
        "name": "Année d'Installation",
        "description": "Année d'installation du système de chauffage.",
    },
    "type_emetteur": {
        "name": "Type d'Émetteur",
        "description": 'Type d\'émetteur, comme "Convecteur électrique NFC".',
    },
    "uparoi": {
        "name": "Transmission Thermique",
        "description": "La transmission thermique non isolée du mur en W/(m²·K). Si inconnue, laisser vide",
    },
    "effet_joule": {
        "name": "Effet Joule",
        "description": "Indique si le mur est affecté par l'effet Joule. Essentiellement vrai pour les chauffages par radiateurs électriques.",
    },
    "surface_chauffee": {
        "name": "Surface Chauffée",
        "description": "Surface chauffée en mètres carrés.",
    },
    "ombrage_lointain_secteur": {
        "name": "Secteur de l'Élément d'Ombrage Lointain",
        "description": "Le secteur de l'obstacle distant. (Considérer qu'on se met dos à la façade et qu'on regarde vers l'obstacle distant).",
    },
    "inertie": {
        "name": "Inertie",
        "description": 'L\'inertie du mur, qui peut être "Léger" ou "Lourd".',
    },
    "type_materiaux": {
        "name": "Type de Matériaux",
        "description": "Le matériau du cadre de la fenêtre (par exemple, PVC, aluminium, bois).",
    },
    "category_stockage": {
        "name": "Catégorie de Stockage",
        "description": "Catégorie d'efficacité du système de stockage.",
    },
    "comptage_individuel": {
        "name": "Comptage Individuel",
        "description": "Indique s'il y a un comptage individuel.",
    },
    "parois": {"name": "Parois", "description": "Les parois du bâtiment."},
    "type_generateur_distribution": {
        "name": "Type de Générateur de Distribution",
        "description": "Type de distribution pour le système d'eau chaude.",
    },
    "vitrages": {"name": "Vitrages", "description": "Les vitrages du bâtiment."},
    "masque_lointain_orientation": {
        "name": "Orientation de l'Ombrage Lointain",
        "description": "L'orientation de la facade occultée par le masque lointain",
    },
    "longueur_pont": {
        "name": "Longueur du Pont",
        "description": "Longueur du pont thermique en mètres.",
    },
    "type_liaison": {
        "name": "Type de Liaison",
        "description": "Type de liaison entre les éléments structurels.",
    },
    "is_vide_sanitaire": {
        "name": "Présence de Vide Sanitaire",
        "description": "Indique si le plancher bas donne sur un vide sanitaire. (inutilisé pour un mur ou un plancher haut, peut être laissé vide).",
    },
    "ombrage_lointain_hauteur": {
        "name": "Hauteur de l'Élément d'Ombrage Lointain",
        "description": "La hauteur de l'obstacle distant (degrés). Prendre l'angle entre l'horizontale et la droite allant du sommet de l'obstacle distant au milieu de la fenêtre.",
    },
    "type_generateur": {
        "name": "Type de Générateur",
        "description": 'Type de générateur de chauffage, tel que "Générateur à effet Joule direct".',
    },
    "isolation_distribution": {
        "name": "Isolation de la Distribution",
        "description": "Indique si le système de distribution est isolé.",
    },
    "annee_generateur": {
        "name": "Année du Générateur",
        "description": "Année de mise en service du générateur.",
    },
    "type_vitrage": {
        "name": "Type de Vitrage",
        "description": "Le type de vitrage (par exemple, simple, double, triple).",
    },
    "type_batiment": {
        "name": "Type d'habitation",
        "description": "Le type d'habitation.",
    },
    "remplissage": {
        "name": "Remplissage du Vitrage",
        "description": "Le type de matériau de remplissage du vitrage (par exemple, air, argon).",
    },
    "annee_isolation": {
        "name": "Année d'Isolation",
        "description": "L'année où le mur/paroi a été isolé.",
    },
    "country": {"name": "Pays", "description": "Le pays où le bâtiment est situé."},
    "isolation_mur": {
        "name": "Isolation du Mur",
        "description": "Type d'isolation du mur.",
    },
    "surface_paroi": {
        "name": "Surface du Mur",
        "description": "La surface du mur en mètres carrés.",
    },
    "r_isolant": {
        "name": "Résistance Thermique de l'Isolant",
        "description": "La résistance thermique de l'isolant en m²·K/W, si connue (si inconnue, elle est déduite de l'épaisseur, avec un gros malus).",
    },
    "masque_proche_orientation": {
        "name": "Orientation de l'Élément d'Ombrage Proche",
        "description": "L'orientation de l'élément d'ombrage proche.",
    },
    "doublage_with_lame_above_15mm": {
        "name": "Doublage avec Épaisseur Supérieure à 15mm",
        "description": "Indique si le mur a un doublage avec une épaisseur supérieure à 15mm. (utilisé uniquement pour les murs, ignorer pour les plancher bas et plancher haut).",
    },
    "inclinaison": {
        "name": "Inclinaison",
        "description": "L'inclinaison de la paroi en degré,  0° = Horizontal, 90° = Vertical.",
    },
    "enduit": {
        "name": "Enduit",
        "description": "Indique si le mur a un enduit. (utilisé uniquement pour les murs, ignorer pour les plancher bas et plancher haut).",
    },
    "type_stockage": {
        "name": "Type de Stockage",
        "description": "Type de stockage du chauffe-eau, soit vertical ou horizontal.",
    },
    "epaisseur_lame": {
        "name": "Épaisseur de la Lame",
        "description": "L'épaisseur de la lame de vitrage (mm).",
    },
    "masque_proche_beta_gama": {
        "name": "Beta-Gamma de l'Élément d'Ombrage Proche",
        "description": "L'angle beta-gamma de l'élément d'ombrage proche. beta est l'angle entre le vitrage et le sommet de l'élément d'ombrage proche, et gamma est l'angle entre le vitrage et l'extrémité de l'élément d'ombrage proche.",
    },
    "annee_construction": {
        "name": "Année de Construction",
        "description": "L'année de construction du bâtiment.",
    },
    "hauteur_sous_plafond": {
        "name": "Hauteur sous Plafond",
        "description": "La hauteur sous plafond moyenne du bâtiment.",
    },
    "type_installation": {
        "name": "Type d'Installation",
        "description": "Type d'installation de chauffage.",
    },
    "hauteur_vitrage": {
        "name": "Hauteur du Vitrage",
        "description": "La hauteur de la fenêtre en mètres.",
    },
    "pieces_alimentees_contigues": {
        "name": "Pièces Alimentées Contiguës",
        "description": "Indique si le générateur est adjacent aux pièces où l'eau chaude est utilisée.",
    },
    "installations": {
        "name": "Installations",
        "description": "Les installations dans le bâtiment (par exemple, ECS, Chauffage, PAC).",
    },
    "masque_lointain_hauteur_alpha": {
        "name": "Hauteur-Alpha de l'Élément d'Ombrage Lointain",
        "description": "L'angle hauteur-alpha de l'élément d'ombrage lointain (degrés). Prendre l'angle entre l'horizontale et la droite allant du sommet de l'obstacle distant au sommet de la fenêtre.",
    },
    "orientation_veranda": {
        "name": "Orientation de la Véranda",
        "description": "L'orientation de la véranda.",
    },
    "surface_habitable": {
        "name": "Surface Habitable",
        "description": "La surface habitable du logement.",
    },
    "masque_proche_type_masque": {
        "name": "Type de l'Élément d'Ombrage Proche",
        "description": "Le type de l'élément d'ombrage proche. (mettre pas de masque si pas de masque)",
    },
    "equipement_intermittence": {
        "name": "Équipement Intermittent",
        "description": "Type d'équipement de chauffage intermittent utilisé.",
    },
    "type_installation_fecs": {
        "name": "Type d'Installation de Chauffage Solaire",
        "description": "Le type d'installation de chauffage solaire, si présent, laisser vide sinon",
    },
    "doublage_with_lame_below_15mm": {
        "name": "Doublage avec Épaisseur Inférieure à 15mm",
        "description": "Indique si le mur a un doublage avec une épaisseur inférieure à 15mm. (utilisé uniquement pour les murs, ignorer pour les plancher bas et plancher haut).",
    },
    "identifiant": {
        "name": "Identifiant",
        "description": "Identifiant unique pour l'entrée.",
    },
    "retour_isolation": {
        "name": "Retour d'Isolation",
        "description": "Indique s'il y a un retour sur l'isolation pour le pont thermique.",
    },
    "volume_ballon": {
        "name": "Volume du Ballon",
        "description": "Volume du ballon de stockage en litres.",
    },
    "type_ventilation": {
        "name": "Type de Ventilation",
        "description": "Le type de ventilation du logement.",
    },
    "traitement_vitrage": {
        "name": "Traitement du Vitrage",
        "description": "Le type de traitement appliqué au vitrage.",
    },
    "masque_proche_rapport_l1_l2": {
        "name": "Rapport L1/L2 de l'Élément d'Ombrage Proche",
        "description": "Le rapport de la largeur à la hauteur de l'élément d'ombrage proche. L1 étant la largeur du masque, L2 étant la largeur de la surface masquée",
    },
    "city": {"name": "Ville", "description": "La ville où se trouve le bâtiment."},
    "materiaux": {
        "name": "Matériaux",
        "description": "Les matériaux utilisés pour construire le mur.",
    },
    "surface_immeuble": {
        "name": "Surface de l'Immeuble",
        "description": "La surface au sol de l'immeuble en mètres carrés (utilisée pour le calcul des déperdition si terre plein ou sous sol non chauffé, laisser vide si pas de terre plein ou si mur ou plancher haut. Si seul logement de l'immeuble, mettre surface au sol).",
    },
    "surface_vitrage": {
        "name": "Surface du Vitrage",
        "description": "La surface du vitrage en mètres carrés.",
    },
    "type_baie": {
        "name": "Type de Baie",
        "description": "Le type global de système de fenêtre (par exemple, fenêtre, porte-fenêtre, baie vitrée).",
    },
    "surface_paroi_local_non_chauffe": {
        "name": "Surface extérieur local non chauffé",
        "description": "La surface du mur extérieur du local non chauffé en mètres carrés.",
    },
}


def entangled_dropdown(valid_combinations, input_scheme, prefix=""):
    keys = [elt for elt in valid_combinations[0].keys() if elt in input_scheme]

    def reset_dropdown():
        out = [
            gr.update(
                choices=list(set([elt[key] for elt in valid_combinations])), value=None
            )
            for key in keys
        ]
        return out

    def update_dropdown(*args):
        valid = valid_combinations.copy()
        for key, arg in zip(keys, args):
            if arg:
                valid = [elt for elt in valid if elt[key] == arg]
        out = [
            gr.update(choices=list(set([elt[key] for elt in valid]))) for key in keys
        ]
        return out

    with gr.Group():
        dropdowns = {
            prefix
            + k: gr.Dropdown(
                choices=list(set([elt[k] for elt in valid_combinations])),
                key=prefix + k,
                label=input_descriptors[k]["name"],
                info=input_descriptors[k]["description"],
                elem_id=prefix + k,
            )
            for k in keys
        }

        for dropdown in dropdowns.values():
            dropdown.input(
                update_dropdown,
                inputs=[dropdowns[prefix + k] for k in keys],
                outputs=[dropdowns[prefix + k] for k in keys],
            )

        reset_button = gr.Button("Reset Group Selection", update_dropdown)
        reset_button.click(
            reset_dropdown, outputs=[dropdowns[prefix + k] for k in keys]
        )

    return dropdowns


def create_processor(
    processor, identifiants=None, identifiants_adjacents=None, prefix=""
):
    valid_combinations = processor.valid_cat_combinations
    key_characteristics = processor.key_characteristics
    input_scheme = processor.input_scheme

    inputs = {}

    entangled_fields = []
    for g, group in valid_combinations.items():
        if len(group["keys"]) > 1:
            entangled_fields.extend(group["keys"])

    implemented_groups = []
    for key in input_scheme:
        if key in entangled_fields:
            for name, value in valid_combinations.items():
                if key in value["keys"]:
                    if not (name in implemented_groups):
                        inputs.update(
                            entangled_dropdown(
                                value["combinations"],
                                input_scheme=input_scheme,
                                prefix=prefix,
                            )
                        )
                        implemented_groups.append(name)
        else:
            characteristic = key_characteristics[key]
            key_id = prefix + key

            if type(characteristic) == str and characteristic == "any":
                if not (
                    key in ["parois", "vitrages", "ponts_thermiques", "installations"]
                ):
                    if key == "identifiant":
                        input_field = gr.Dropdown(
                            choices=identifiants,
                            label=input_descriptors[key]["name"],
                            info=input_descriptors[key]["description"],
                            key=key_id,
                        )
                    elif key == "identifiant_adjacents":
                        input_field = gr.Dropdown(
                            choices=identifiants_adjacents,
                            label=input_descriptors[key]["name"],
                            info=input_descriptors[key]["description"],
                            multiselect=True,
                            key=key_id,
                            value=[],
                        )
                    elif "is_" in key or "doublage" in key or "enduit" in key:
                        input_field = gr.Dropdown(
                            choices=[False, True],
                            label=input_descriptors[key]["name"],
                            info=input_descriptors[key]["description"],
                            value=False,
                            key=key_id,
                        )
                    else:
                        input_field = gr.Textbox(
                            label=input_descriptors[key]["name"],
                            info=input_descriptors[key]["description"],
                            placeholder="Enter text",
                            key=key_id,
                        )
            elif type(characteristic) == str and characteristic == "float":
                input_field = gr.Number(
                    label=input_descriptors[key]["name"],
                    info=input_descriptors[key]["description"],
                    key=key_id,
                    value=" ",
                )
            elif (
                isinstance(characteristic, dict)
                and "min" in characteristic
                and "max" in characteristic
            ):
                input_field = gr.Slider(
                    minimum=0,
                    maximum=characteristic["max"],
                    value=0,
                    label=input_descriptors[key]["name"],
                    info=input_descriptors[key]["description"],
                    key=key_id,
                )
            elif isinstance(characteristic, list) or isinstance(
                characteristic, np.ndarray
            ):
                char = [
                    elt
                    for elt in characteristic
                    if ((elt is not None) and (elt != "NULL") and (str(elt) != "nan"))
                ] + ["Unknown or Empty"]
                input_field = gr.Dropdown(
                    choices=char,
                    label=input_descriptors[key]["name"],
                    info=input_descriptors[key]["description"],
                    value=None,
                    key=key_id,
                )
            else:
                input_field = gr.Text(
                    label="Unsupported type for " + input_descriptors[key]["name"],
                    key=key_id,
                )
            inputs[key_id] = input_field
    return inputs


def get_demo(dpe):
    with gr.Blocks(theme="freddyaboulton/dracula_revamped", title="Py3CL by Renovly") as demo:
        with gr.Tab(label="General Informations"):
            base_inputs = create_processor(dpe)

        with gr.Tab(label="Parois"):
            for i in range(10):
                with gr.Accordion(label=f"Paroi {i}", open=False):
                    base_inputs.update(
                        create_processor(
                            dpe.parois_processor,
                            identifiants=parois,
                            identifiants_adjacents=id_adjacents,
                            prefix=f"paroi_{i}-",
                        )
                    )

        with gr.Tab(label="Ouvrants"):
            for i in range(10):
                with gr.Accordion(label=f"Ouvrant {i}", open=False):
                    base_inputs.update(
                        create_processor(
                            dpe.vitrage_processor,
                            identifiants=ouvrants,
                            prefix=f"vitrage_{i}-",
                        )
                    )

        with gr.Tab(label="Ponts Thermiques"):
            for i in range(10):
                with gr.Accordion(label=f"Pont Thermique {i}", open=False):
                    base_inputs.update(
                        create_processor(
                            dpe.pont_thermique_processor,
                            identifiants=ponts_thermiques,
                            prefix=f"pont_thermique_{i}-",
                        )
                    )

        with gr.Tab(label="ECS"):
            for i in range(3):
                with gr.Accordion(label=f"ECS {i}", open=False):
                    base_inputs.update(
                        create_processor(
                            dpe.ecs_processor, identifiants=ecs, prefix=f"ecs_{i}-"
                        )
                    )

        with gr.Tab(label="Climatisation"):
            for i in range(1):
                with gr.Accordion(label=f"Climatisation {i}", open=False):
                    base_inputs.update(
                        create_processor(
                            dpe.clim_processor, identifiants=clims, prefix=f"clim_{i}-"
                        )
                    )

        with gr.Tab(label="Chauffage"):
            for i in range(3):
                with gr.Accordion(label=f"Chauffage {i}", open=False):
                    base_inputs.update(
                        create_processor(
                            dpe.chauffage_processor,
                            identifiants=chauffages,
                            prefix=f"chauffage_{i}-",
                        )
                    )

        def get_json(*inputs):
            dico = dict(zip(list(base_inputs.keys()), inputs))

            for k, val in dico.items():
                if val in ["NULL", "", None]:
                    dico[k] = "Unknown or Empty"
                elif val == " ":
                    dico[k] = None

            list_parois = list(
                set([elt.split("-")[0] for elt in dico.keys() if "paroi_" in elt])
            )
            list_vitrages = list(
                set([elt.split("-")[0] for elt in dico.keys() if "vitrage_" in elt])
            )
            list_ponts_thermiques = list(
                set(
                    [
                        elt.split("-")[0]
                        for elt in dico.keys()
                        if "pont_thermique_" in elt
                    ]
                )
            )
            list_ecs = list(
                set([elt.split("-")[0] for elt in dico.keys() if "ecs_" in elt])
            )
            list_clims = list(
                set([elt.split("-")[0] for elt in dico.keys() if "clim_" in elt])
            )
            list_chauffages = list(
                set([elt.split("-")[0] for elt in dico.keys() if "chauffage_" in elt])
            )
            list_installations = list_ecs + list_clims + list_chauffages

            special = (
                list_parois + list_vitrages + list_ponts_thermiques + list_installations
            )
            for elt in special:
                print(elt, dico[elt + "-identifiant"])
            used_special = [
                elt
                for elt in special
                if dico[elt + "-identifiant"] != "Unknown or Empty"
            ]
            base = {
                k: v for k, v in dico.items() if not any([elt in k for elt in special])
            }

            (
                base["parois"],
                base["vitrages"],
                base["ponts_thermiques"],
                base["installations"],
            ) = ({}, {}, {}, {})

            for s in used_special:
                special_dico = {k.split("-")[-1]: v for k, v in dico.items() if s in k}
                if "paroi" in s:
                    base["parois"].update({dico[s + "-identifiant"]: special_dico})
                elif "vitrage" in s:
                    base["vitrages"].update({dico[s + "-identifiant"]: special_dico})
                elif "pont_thermique" in s:
                    base["ponts_thermiques"].update(
                        {dico[s + "-identifiant"]: special_dico}
                    )
                else:
                    base["installations"].update(
                        {dico[s + "-identifiant"]: special_dico}
                    )
            try:
                dpe_input = DPEInput(**base)
                result = dpe.forward(dpe_input)

                return result
            except Exception as e:
                base["error"] = str(e)
                return base

        with gr.Tab(label="Results"):
            button = gr.Button("Compute")
            output = gr.JSON()
            button.click(
                get_json,
                inputs=[base_inputs[key] for key in base_inputs.keys()],
                outputs=[output],
            )
    return demo


if __name__ == "__main__":
    dpe = DPE(configs=abaques_configs)
    demo = get_demo(dpe)

    ## Queue 20, debug=Fals, share = false, port=8080
    demo.queue(20).launch(
        debug=False,
        share=False,
        server_port=8080,
        max_threads=40,
        favicon_path="demo/icon_green.ico"
    )

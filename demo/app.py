import streamlit as st
import numpy as np
import pandas as pd
import os
import numpy as np
import sys
from tqdm.auto import tqdm

sys.path.append('.')
from py3cl import DPE, DPEInput, abaques_configs
pd.set_option('display.max_columns', 500)

## St layout wide



# st.set_option('theme.primaryColor', '#519351')
# st.set_option('theme.backgroundColor', '#519351')
# st.set_option('theme.secondaryBackgroundColor', '#519351')
# st.set_option('theme.textColor', '#262730')
# st.set_option('theme.font', 'sans serif')
st.set_page_config(layout="wide")



def recursive_selectbox(valid, keys, select={}, prefix="", cols=None, col_count=0, container=None):
    if not keys:
        # st.write(f"Selected: {select}")
        # col_count+=1
        return select, col_count
    k = keys[0]
    init = list(set([i[k] for i in valid]))
    with cols[col_count % len(cols)]:
        with container:
            select[k] = st.selectbox(f"{k}", options=init + [None], index=None, key=f"{prefix}_dropdown_{k}")

    if select[k]:
        col_count += 1
        new_valid = [i for i in valid if i[k] == select[k]]
        return recursive_selectbox(new_valid, keys[1:], select, prefix=prefix, cols=cols, col_count=col_count, container=container)
    
    return select, col_count

def nested_selectbox(valid_cat_combinations, prefix="", cols=None, col_count=0, container=None):
    keys = valid_cat_combinations['keys']
    return recursive_selectbox(valid_cat_combinations['combinations'], keys, prefix=prefix, cols=cols, col_count=col_count, container=container)


def build_processor(processor, identifiants=None, identifiants_adjacents=None, prefix="", col=4):
    input_scheme = processor.input_scheme
    key_characteristics = processor.key_characteristics
    valid_cat_combinations = processor.valid_cat_combinations

    combinations_keys = []
    for group, cat_combinations in valid_cat_combinations.items():
        combinations_keys.extend(cat_combinations['keys'])
    combinations_keys = list(set(combinations_keys))

    inputs = {}

    cols = st.columns(col)
    col_count = 0
    with st.container():
        for key, characteristic in key_characteristics.items():
            if not(key in combinations_keys):
                key_id=prefix+key
                
                if type(characteristic) == str and characteristic == "any":
                    if not(key in ['parois', 'vitrages', 'ponts_thermiques', 'installations']):
                        if key == "identifiant":
                            with cols[col_count % col]:
                                input_field = st.selectbox(label=key, options=identifiants,index=None, key=key_id)
                        elif key == "identifiant_adjacents":
                            with cols[col_count % col]:
                                input_field = st.multiselect(label=key, options=identifiants_adjacents, key=key_id)
                        elif "is_" in key:
                            with cols[col_count % col]:
                                input_field = st.selectbox(label=key, options=[True, False], index=1, key=key_id)
                        else:
                            with cols[col_count % col]:
                                input_field = st.text_input(label=key, value="", key=key_id)
                elif type(characteristic) == str and characteristic == "float":
                    with cols[col_count % col]:
                        input_field = st.number_input(label=key, key=key_id, value=None)
                elif isinstance(characteristic, dict) and 'min' in characteristic and 'max' in characteristic:
                    # input_field = st.slider(label=key, min_value=0, max_value=int(characteristic['max']), value=-100, key=key_id)
                    with cols[col_count % col]:
                        input_field = st.number_input(label=key + f" ({0}, {int(characteristic['max'])})", key=key_id, value=None)
                elif isinstance(characteristic, list) or isinstance(characteristic, np.ndarray):
                    char = [elt for elt in characteristic if ((elt is not None) and (elt != "NULL"))] + [None]
                    with cols[col_count % col]:
                        input_field = st.selectbox(label=key, options=char, key=key_id)
                else:   
                    with cols[col_count % col]:
                        input_field = st.text(label="Unsupported type for " + key, key=key_id)
                inputs[key] = input_field
                col_count += 1
    
    for group, cat_combinations in valid_cat_combinations.items():
        container= st.container()
        select, col_count = nested_selectbox(cat_combinations, prefix=prefix, cols=cols, col_count=0, container=container)
        inputs.update(select)
    return inputs
        
murs=[f"mur_{i}" for i in range(6)]
ph=[f"plancher_haut_{i}" for i in range(2)]
pb=[f"plancher_bas_{i}" for i in range(2)]
ouvrants=[f"vitrage_{i}" for i in range(10)]

parois = murs + ph + pb
parois_adjacents = murs + ph + pb + ouvrants
# verandas=[f"veranda{i}" for i in range(2)]
ponts_thermiques=[f"pont_thermique_saisie_{i}" for i in range(20)]

ecs=[f"ecs_{i}" for i in range(3)]
clims=[f"clim_{i}" for i in range(1)]
chauffages=[f"chauffage_{i}" for i in range(3)]

def build_json(
        inputs_general,
        inputs_parois,
        inputs_vitrages,
        inputs_ponts_thermiques,
        inputs_ecs,
        inputs_clims,
        inputs_chauffages
    ):
    inputs = {}
    inputs.update(inputs_general)

    inputs['parois'] = {elt['identifiant']:elt for elt in inputs_parois if elt['identifiant'] is not None}
    inputs['vitrages'] = {elt['identifiant']:elt for elt in inputs_vitrages if elt['identifiant'] is not None}
    inputs['ponts_thermiques'] = {elt['identifiant']:elt for elt in inputs_ponts_thermiques if elt['identifiant'] is not None}
    
    installations = {elt['identifiant']:elt for elt in inputs_ecs if elt['identifiant'] is not None}
    installations.update({elt['identifiant']:elt for elt in inputs_clims if elt['identifiant'] is not None})
    installations.update({elt['identifiant']:elt for elt in inputs_chauffages if elt['identifiant'] is not None})
    inputs['installations'] = installations
    return inputs

if __name__ == "__main__":
    if not('processor' in st.session_state):
        st.session_state.processor = DPE(configs=abaques_configs)

    tab_general, tab_parois, tab_vitrages, tab_ponts_thermiques, tab_ecs, tab_clims, tab_chauffages, tab_result = st.tabs(["Général", "Parois", "Vitrages", "Ponts thermiques", "ECS", "Climatisations", "Chauffages", "Résultat"])

    with tab_general:
        inputs_general=build_processor(st.session_state.processor)


    inputs_parois = []
    with tab_parois:
        for i in range(8):
            with st.expander(f"Paroi {i}", expanded=False):
                inputs_parois.append(build_processor(st.session_state.processor.parois_processor, identifiants=parois, identifiants_adjacents=parois_adjacents, prefix=f"paroi_{i}_"))

    inputs_vitrages = []
    with tab_vitrages:
        for i in range(10):
            with st.expander(f"Vitrage {i}", expanded=False):
                inputs_vitrages.append(build_processor(st.session_state.processor.vitrage_processor, identifiants=ouvrants, prefix=f"vitrage_{i}_"))

    inputs_ponts_thermiques = []
    with tab_ponts_thermiques:
        for i in range(10):
            with st.expander(f"Pont thermique {i}", expanded=False):
                inputs_ponts_thermiques.append(build_processor(st.session_state.processor.pont_thermique_processor, identifiants=ponts_thermiques, prefix=f"pont_thermique_{i}_"))

    inputs_ecs = []
    with tab_ecs:
        for i in range(3):
            with st.expander(f"ECS {i}", expanded=False):
                inputs_ecs.append(build_processor(st.session_state.processor.ecs_processor, identifiants=ecs, prefix=f"ecs_{i}_"))

    inputs_clims = []
    with tab_clims:
        for i in range(1):
            with st.expander(f"Climatisation {i}", expanded=False):
                inputs_clims.append(build_processor(st.session_state.processor.clim_processor, identifiants=clims, prefix=f"clim_{i}_"))

    inputs_chauffages = []
    with tab_chauffages:
        for i in range(3):
            with st.expander(f"Chauffage {i}", expanded=False):
                inputs_chauffages.append(build_processor(st.session_state.processor.chauffage_processor, identifiants=chauffages, prefix=f"chauffage_{i}_"))


    with tab_result:
        if st.button("Calculer"):
            json = build_json(
                inputs_general,
                inputs_parois,
                inputs_vitrages,
                inputs_ponts_thermiques,
                inputs_ecs,
                inputs_clims,
                inputs_chauffages
            )
            try:
                input = DPEInput(**json)
                result = st.session_state.processor.forward(input)
                st.json(result)
            except Exception as e:
                json['error'] = str(e)
                st.json(json)
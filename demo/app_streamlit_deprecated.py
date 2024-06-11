import streamlit as st
import numpy as np
import pandas as pd
import os
import numpy as np
import sys
from tqdm.auto import tqdm
import cProfile
import pstats
from io import StringIO

sys.path.append(".")
from py3cl import DPE, DPEInput, abaques_configs

pd.set_option("display.max_columns", 500)

st.set_page_config(layout="wide")

murs = [f"mur_{i}" for i in range(6)]
ph = [f"plancher_haut_{i}" for i in range(2)]
pb = [f"plancher_bas_{i}" for i in range(2)]
ouvrants = [f"vitrage_{i}" for i in range(10)]

parois = murs + ph + pb
parois_adjacents = murs + ph + pb + ouvrants
# verandas=[f"veranda{i}" for i in range(2)]
ponts_thermiques = [f"pont_thermique_saisie_{i}" for i in range(20)]

ecs = [f"ecs_{i}" for i in range(3)]
clims = [f"clim_{i}" for i in range(1)]
chauffages = [f"chauffage_{i}" for i in range(3)]


def recursive_selectbox(
    valid, keys, select={}, prefix="", cols=None, col_count=0, container=None
):
    if not keys:
        return select, col_count
    k = keys[0]
    init = list(set([i[k] for i in valid]))
    if len(init) > 1:
        with cols[col_count % len(cols)]:
            with container:
                select[k] = st.selectbox(
                    f"{k}",
                    options=np.unique(init + ["Unknown or Empty"]),
                    index=None,
                    key=f"{prefix}_dropdown_{k}",
                )
    else:
        select[k] = init[0]
    if select[k]:
        col_count += 1
        new_valid = [i for i in valid if i[k] == select[k]]
        return recursive_selectbox(
            new_valid,
            keys[1:],
            select,
            prefix=prefix,
            cols=cols,
            col_count=col_count,
            container=container,
        )

    return select, col_count


def nested_selectbox(
    valid_cat_combinations, prefix="", cols=None, col_count=0, container=None
):
    keys = valid_cat_combinations["keys"]
    return recursive_selectbox(
        valid_cat_combinations["combinations"],
        keys,
        prefix=prefix,
        cols=cols,
        col_count=col_count,
        container=container,
    )


def build_processor(
    processor, identifiants=None, identifiants_adjacents=None, prefix="", col=4
):
    input_scheme = processor.input_scheme
    key_characteristics = processor.key_characteristics
    valid_cat_combinations = processor.valid_cat_combinations

    combinations_keys = {
        k for cat_comb in valid_cat_combinations.values() for k in cat_comb["keys"]
    }
    inputs = {}

    cols = st.columns(col)
    col_count = 0
    with st.container():
        for key, characteristic in key_characteristics.items():
            if key not in combinations_keys:
                key_id = prefix + key

                with cols[col_count % col]:
                    if characteristic == "any":
                        if key == "identifiant":
                            input_field = st.selectbox(
                                label=key, options=identifiants, index=None, key=key_id
                            )
                        elif key == "identifiant_adjacents":
                            input_field = st.multiselect(
                                label=key, options=identifiants_adjacents, key=key_id
                            )
                        elif "is_" in key:
                            input_field = st.selectbox(
                                label=key, options=[True, False], index=1, key=key_id
                            )
                        else:
                            input_field = st.text_input(label=key, value="", key=key_id)
                    elif characteristic == "float":
                        input_field = st.number_input(label=key, key=key_id, value=None)
                    elif (
                        isinstance(characteristic, dict)
                        and "min" in characteristic
                        and "max" in characteristic
                    ):
                        input_field = st.number_input(
                            label=key + f" ({0}, {int(characteristic['max'])})",
                            key=key_id,
                            value=None,
                        )
                    elif isinstance(characteristic, (list, np.ndarray)):
                        char = [
                            elt
                            for elt in characteristic
                            if elt and elt != "Unknown or Empty"
                        ] + ["Unknown or Empty"]
                        input_field = st.selectbox(label=key, options=char, key=key_id)
                    else:
                        input_field = st.text(
                            label="Unsupported type for " + key, key=key_id
                        )
                    inputs[key] = input_field
                    col_count += 1

    for group, cat_combinations in valid_cat_combinations.items():
        container = st.container()
        select, col_count = nested_selectbox(
            cat_combinations, prefix=prefix, cols=cols, col_count=0, container=container
        )
        inputs.update(select)
    return inputs


def build_json(
    inputs_general,
    inputs_parois,
    inputs_vitrages,
    inputs_ponts_thermiques,
    inputs_ecs,
    inputs_clims,
    inputs_chauffages,
):
    inputs = {}
    inputs.update(inputs_general)

    inputs["parois"] = {
        elt["identifiant"]: elt for elt in inputs_parois if elt["identifiant"]
    }
    inputs["vitrages"] = {
        elt["identifiant"]: elt for elt in inputs_vitrages if elt["identifiant"]
    }
    inputs["ponts_thermiques"] = {
        elt["identifiant"]: elt for elt in inputs_ponts_thermiques if elt["identifiant"]
    }

    installations = {
        elt["identifiant"]: elt for elt in inputs_ecs if elt["identifiant"]
    }
    installations.update(
        {elt["identifiant"]: elt for elt in inputs_clims if elt["identifiant"]}
    )
    installations.update(
        {elt["identifiant"]: elt for elt in inputs_chauffages if elt["identifiant"]}
    )
    inputs["installations"] = installations
    return inputs


if __name__ == "__main__":
    if "processor" not in st.session_state:
        st.session_state.processor = DPE(configs=abaques_configs)

    tab_names = [
        "Général",
        "Parois",
        "Vitrages",
        "Ponts thermiques",
        "ECS",
        "Climatisations",
        "Chauffages",
        "Résultat",
    ]
    tabs = st.tabs(tab_names)

    inputs_general = (
        build_processor(st.session_state.processor) if "Général" in tab_names else {}
    )

    inputs_parois = []
    with tabs[1]:
        for i in range(8):
            with st.expander(f"Paroi {i}", expanded=False):
                inputs_parois.append(
                    build_processor(
                        st.session_state.processor.parois_processor,
                        identifiants=parois,
                        identifiants_adjacents=parois_adjacents,
                        prefix=f"paroi_{i}_",
                    )
                )

    inputs_vitrages = []
    with tabs[2]:
        for i in range(10):
            with st.expander(f"Vitrage {i}", expanded=False):
                inputs_vitrages.append(
                    build_processor(
                        st.session_state.processor.vitrage_processor,
                        identifiants=ouvrants,
                        prefix=f"vitrage_{i}_",
                    )
                )

    inputs_ponts_thermiques = []
    with tabs[3]:
        for i in range(10):
            with st.expander(f"Pont thermique {i}", expanded=False):
                inputs_ponts_thermiques.append(
                    build_processor(
                        st.session_state.processor.pont_thermique_processor,
                        identifiants=ponts_thermiques,
                        prefix=f"pont_thermique_{i}_",
                    )
                )

    inputs_ecs = []
    with tabs[4]:
        for i in range(3):
            with st.expander(f"ECS {i}", expanded=False):
                inputs_ecs.append(
                    build_processor(
                        st.session_state.processor.ecs_processor,
                        identifiants=ecs,
                        prefix=f"ecs_{i}_",
                    )
                )

    inputs_clims = []
    with tabs[5]:
        for i in range(1):
            with st.expander(f"Climatisation {i}", expanded=False):
                inputs_clims.append(
                    build_processor(
                        st.session_state.processor.clim_processor,
                        identifiants=clims,
                        prefix=f"clim_{i}_",
                    )
                )

    inputs_chauffages = []
    with tabs[6]:
        for i in range(3):
            with st.expander(f"Chauffage {i}", expanded=False):
                inputs_chauffages.append(
                    build_processor(
                        st.session_state.processor.chauffage_processor,
                        identifiants=chauffages,
                        prefix=f"chauffage_{i}_",
                    )
                )

    with tabs[7]:
        if st.button("Calculer"):
            json = build_json(
                inputs_general,
                inputs_parois,
                inputs_vitrages,
                inputs_ponts_thermiques,
                inputs_ecs,
                inputs_clims,
                inputs_chauffages,
            )
            try:
                input = DPEInput(**json)
                result = st.session_state.processor.forward(input)
                st.json(result)
            except Exception as e:
                json["error"] = str(e)
                st.json(json)

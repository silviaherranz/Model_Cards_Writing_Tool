import streamlit as st
import json
from collections import OrderedDict
from main import extract_learning_architectures_from_state
from template_base import LEARNING_ARCHITECTURE, TRAINING_DATA_INPUT_OUTPUT_TS
from copy import deepcopy




""" def parse_into_json():
    model_card_schema = utils.get_model_card_schema()
    serializable_state = {}

    for key in ["model_basic_information"]:
        serializable_state[key] = {}
        for variable in model_card_schema.get(key, []):
            session_key = f"{key}_{variable}"
            if session_key in st.session_state:
                serializable_state[key][variable] = st.session_state[session_key]
            else:
                serializable_state[key][variable] = None  # Or omit with .setdefault(), depending on needs

    json_string = json.dumps(serializable_state)
    return json_string
 """
"""
def parse_into_json():
    serializable_state = {key: st.session_state[key] for key in st.session_state if isinstance(st.session_state[key], (str, int, float, bool, list, dict, type(None)))}
    json_string = json.dumps(serializable_state)
    return json_string 
"""


def parse_into_json(schema):
    raw_data = {}

    # 1. Procesar SCHEMA por secciones
    for section, keys in schema.items():
        raw_data[section] = {}
        for full_key in keys:
            prefix = section + "_"
            subkey = full_key[len(prefix):] if full_key.startswith(prefix) else full_key
            raw_data[section][subkey] = st.session_state.get(full_key, "")

    # 2. Añadir learning_architectures como sección independiente
    forms = st.session_state.get("learning_architecture_forms", {})
    learning_architectures = []

    for i in range(len(forms)):
        prefix = f"learning_architecture_{i}_"
        arch = deepcopy(LEARNING_ARCHITECTURE)
        for field in arch.keys():
            session_key = f"{prefix}{field}"
            arch[field] = st.session_state.get(session_key, arch[field])
        arch["id"] = i
        learning_architectures.append(arch)

    # 3. Reordenar secciones como quieras
    structured_data = OrderedDict()

    for section in ["card_metadata", "model_basic_information", "technical_specifications", "training_data"]:
        if section in raw_data:
            structured_data[section] = raw_data[section]

    # Insertar learning_architectures aquí
    structured_data["learning_architectures"] = learning_architectures

    # Luego el resto (hw_and_sw)
    if "hw_and_sw" in raw_data:
        structured_data["hw_and_sw"] = raw_data["hw_and_sw"]

    # Recolectar entradas model_inputs y model_outputs
    modality_entries = []
    for key, value in st.session_state.items():
        if key.endswith("model_inputs") and isinstance(value, list):
            for item in value:
                modality_entries.append({"modality": item, "source": "model_inputs"})
        elif key.endswith("model_outputs") and isinstance(value, list):
            for item in value:
                modality_entries.append({"modality": item, "source": "model_outputs"})

    inputs = []
    for entry in modality_entries:
        clean_modality = entry["modality"].strip().replace(" ", "_").lower()
        source = entry["source"]
        modality_obj = {
            "input_content": entry["modality"],
            "source": source
        }
        for field in TRAINING_DATA_INPUT_OUTPUT_TS:
            key = f"training_data_{clean_modality}_{source}_{field}"
            modality_obj[field] = st.session_state.get(key, "")
        inputs.append(modality_obj)

    if "training_data" not in raw_data:
        raw_data["training_data"] = {}

    raw_data["training_data"]["inputs"] = inputs

    structured_data["training_data"]["inputs"] = inputs

    return json.dumps(structured_data, indent=2)




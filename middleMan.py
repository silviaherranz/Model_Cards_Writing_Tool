import streamlit as st
import json
from main import extract_learning_architectures_from_state
from template_base import LEARNING_ARCHITECTURE
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
    structured_data = {}

    # 1. Procesar SCHEMA por secciones
    for section, keys in schema.items():
        structured_data[section] = {}
        for full_key in keys:
            # extraer la clave interna: "card_metadata_doi" → "doi"
            prefix = section + "_"
            subkey = full_key[len(prefix):] if full_key.startswith(prefix) else full_key
            structured_data[section][subkey] = st.session_state.get(full_key, "")

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

    structured_data["learning_architectures"] = learning_architectures

    return json.dumps(structured_data, indent=2)




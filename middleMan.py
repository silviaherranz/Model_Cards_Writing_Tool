import streamlit as st
import json
from main import extract_learning_architectures_from_state




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

    for section, keys in schema.items():
        structured_data[section] = {}
        for key in keys:
            value = st.session_state.get(key)
            if value is not None:
                structured_data[section][key] = value

    # 👇 Añadir learning_architectures SIN sobrescribir lo que ya haya
    learning_architectures = extract_learning_architectures_from_state()

    if learning_architectures:
        if "technical_specifications" not in structured_data:
            structured_data["technical_specifications"] = {}

        structured_data["technical_specifications"]["learning_architectures"] = learning_architectures

    return json.dumps(structured_data, indent=2)



    return json.dumps(structured_data, indent=2)



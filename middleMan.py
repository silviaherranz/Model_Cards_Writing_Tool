import streamlit as st
import json
from collections import OrderedDict
from main import extract_evaluations_from_state
from template_base import LEARNING_ARCHITECTURE, DATA_INPUT_OUTPUT_TS, TASK_METRIC_MAP, EVALUATION_METRIC_FIELDS
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
VOLCADO DEL SESSIO STATE A UN JSON UTIL PARA VER CON QUÉ NOMBRE SE GUARDA CADA CAMPO
def parse_into_json():
    serializable_state = {key: st.session_state[key] for key in st.session_state if isinstance(st.session_state[key], (str, int, float, bool, list, dict, type(None)))}
    json_string = json.dumps(serializable_state)
    return json_string 
"""


def parse_into_json(schema):
    raw_data = {}
    current_task = st.session_state.get("task")

    for section, fields in schema.items():
        raw_data[section] = {}

        # Soporta formato antiguo: lista de claves
        if isinstance(fields, list):
            for full_key in fields:
                prefix = section + "_"
                subkey = full_key[len(prefix):] if full_key.startswith(prefix) else full_key
                raw_data[section][subkey] = st.session_state.get(full_key, "")

        # Soporta formato nuevo: diccionario de propiedades
        elif isinstance(fields, dict):
            for key, props in fields.items():
                allowed_tasks = props.get("model_types")
                if allowed_tasks is not None and current_task not in allowed_tasks:
                    continue
                full_key = f"{section}_{key}"
                raw_data[section][key] = st.session_state.get(full_key, "")


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
    task = st.session_state.get("task")
    if task:
        structured_data["task"] = task

    for section in ["card_metadata", "model_basic_information", "technical_specifications"]:
        if section in raw_data:
            structured_data[section] = raw_data[section]

    # Insertar learning_architectures aquí
    structured_data["learning_architectures"] = learning_architectures

    # Luego el resto (hw_and_sw)
    if "hw_and_sw" in raw_data:
        structured_data["hw_and_sw"] = raw_data["hw_and_sw"]

    if "training_data" in raw_data:
        structured_data["training_data"] = raw_data["training_data"]

    # Recolectar entradas model_inputs y model_outputs
    modality_entries = []
    for key, value in st.session_state.items():
        if key.endswith("model_inputs") and isinstance(value, list):
            for item in value:
                modality_entries.append({"modality": item, "source": "model_inputs"})
        elif key.endswith("model_outputs") and isinstance(value, list):
            for item in value:
                modality_entries.append({"modality": item, "source": "model_outputs"})

    model_inputs_outputs_ts = []
    for entry in modality_entries:
        clean_modality = entry["modality"].strip().replace(" ", "_").lower()
        source = entry["source"]
        modality_obj = {
            "input_content": entry["modality"],
            "source": source
        }
        for field in DATA_INPUT_OUTPUT_TS:
            key = f"training_data_{clean_modality}_{source}_{field}"

            value = st.session_state.get(key)
            if value is None:
                value = st.session_state.get(f"_{key}")
            if value is None:
                value = st.session_state.get(f"__{key}")
            modality_obj[field] = value if value is not None else ""

        model_inputs_outputs_ts.append(modality_obj)

    if "training_data" not in raw_data:
        raw_data["training_data"] = {}

    raw_data["training_data"]["inputs_outputs_technical_specifications"] = model_inputs_outputs_ts

    structured_data["training_data"]["inputs_outputs_technical_specifications"] = model_inputs_outputs_ts
    
    structured_data["evaluations"] = extract_evaluations_from_state()
    task = st.session_state.get("task", "").strip().lower()
    metric_types = TASK_METRIC_MAP.get(task, [])

    for eval_form in structured_data.get("evaluations", []):
        for metric_type in metric_types:
            metric_list_key = f"{metric_type}_list"
            metric_entries = st.session_state.get(f"evaluation_{eval_form.get('name', '')}_{metric_list_key}", [])

            export_list = []
            for metric_name in metric_entries:
                sub_prefix = f"evaluation_{eval_form.get('name', '')}.{metric_name}"
                metric_obj = {"name": metric_name}
                for field in EVALUATION_METRIC_FIELDS[metric_type]:
                    key = f"{sub_prefix}_{field}"
                    value = st.session_state.get(key)
                    if value is None:
                        value = st.session_state.get(f"_{key}")
                    metric_obj[field] = value if value is not None else ""
                export_list.append(metric_obj)

            if export_list:
                eval_form[metric_type] = export_list

    if "qualitative_evaluation" in raw_data:
        structured_data["qualitative_evaluation"] = raw_data["qualitative_evaluation"]

    if "other_considerations" in raw_data:
        structured_data["other_considerations"] = raw_data["other_considerations"]

    return json.dumps(structured_data, indent=2)




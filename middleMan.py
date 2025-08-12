import streamlit as st
import json
from collections import OrderedDict
from main import extract_evaluations_from_state
from template_base import (
    LEARNING_ARCHITECTURE,
    DATA_INPUT_OUTPUT_TS,
    TASK_METRIC_MAP,
    EVALUATION_METRIC_FIELDS,
)
from copy import deepcopy


def parse_into_json(schema):
    raw_data = {}
    current_task = st.session_state.get("task")

    for section, fields in schema.items():
        raw_data[section] = {}

        if isinstance(fields, list):
            for full_key in fields:
                prefix = section + "_"
                subkey = (
                    full_key[len(prefix) :] if full_key.startswith(prefix) else full_key
                )
                raw_data[section][subkey] = st.session_state.get(full_key, "")

        elif isinstance(fields, dict):
            for key, props in fields.items():
                allowed_tasks = props.get("model_types")
                if allowed_tasks is None or current_task in allowed_tasks:
                    full_key = f"{section}_{key}"
                    raw_data[section][key] = st.session_state.get(full_key, "")

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

    structured_data = OrderedDict()
    task = st.session_state.get("task")
    if task:
        structured_data["task"] = task

    for section in [
        "card_metadata",
        "model_basic_information",
        "technical_specifications",
    ]:
        if section in raw_data:
            structured_data[section] = raw_data[section]

    structured_data["learning_architectures"] = learning_architectures

    if "hw_and_sw" in raw_data:
        structured_data["hw_and_sw"] = raw_data["hw_and_sw"]

    if "training_data" in raw_data:
        structured_data["training_data"] = raw_data["training_data"]

    modality_entries = []
    for key, value in st.session_state.items():
        if key.endswith("model_inputs") and isinstance(value, list):
            for item in value:
                modality_entries.append({"modality": item, "source": "model_inputs"})
        elif key.endswith("model_outputs") and isinstance(value, list):
            for item in value:
                modality_entries.append({"modality": item, "source": "model_outputs"})

    io_details = []
    for entry in modality_entries:
        clean = entry["modality"].strip().replace(" ", "_").lower()
        source = entry["source"]
        detail = {"input_content": entry["modality"], "source": source}
        for field in DATA_INPUT_OUTPUT_TS:
            key = f"training_data_{clean}_{source}_{field}"
            val = (
                st.session_state.get(key)
                or st.session_state.get(f"_{key}")
                or st.session_state.get(f"__{key}")
                or ""
            )
            detail[field] = val
        io_details.append(detail)

    if "training_data" not in raw_data:
        raw_data["training_data"] = {}
    raw_data["training_data"]["inputs_outputs_technical_specifications"] = io_details

    if "training_data" not in structured_data:
        structured_data["training_data"] = {}
    structured_data["training_data"]["inputs_outputs_technical_specifications"] = (
        io_details
    )

    structured_data["evaluations"] = extract_evaluations_from_state()
    task = st.session_state.get("task", "").strip().lower()
    metric_types = TASK_METRIC_MAP.get(task, [])

    for eval_form in structured_data.get("evaluations", []):
        for metric_type in metric_types:
            metric_list_key = f"{metric_type}_list"
            metric_entries = st.session_state.get(
                f"evaluation_{eval_form.get('name', '')}_{metric_list_key}", []
            )

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

    if "other_considerations" in raw_data:
        structured_data["other_considerations"] = raw_data["other_considerations"]

    # Appendix
    appendix = []
    for name, data in st.session_state.get("appendix_uploads", {}).items():
        appendix.append({"name": name, "label": data.get("custom_label",""), "relpath": data.get("path","")})
    if appendix:
        structured_data["appendix"] = appendix

    # Images
    images = {}
    for field_key, recs in st.session_state.get("image_fields", {}).items():
        items = [{"name": r.get("name",""), "label": r.get("label",""), "relpath": r.get("relpath","")} for r in recs]
        if items:
            images[field_key] = items
    if images:
        structured_data.setdefault("assets", {})
        structured_data["assets"]["images"] = images


    return json.dumps(structured_data, indent=2)

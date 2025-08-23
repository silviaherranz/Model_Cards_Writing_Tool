import os
from json_template import (
    DATA_INPUT_OUTPUT_TS,
    EVALUATION_METRIC_FIELDS,
    LEARNING_ARCHITECTURE,
    TASK_METRIC_MAP,
)

import streamlit as st

def is_empty(value):
        return value in ("", None, [], {})


def _has_required_image(full_key: str) -> bool:
    """Return True iff the uploader for `full_key` has a saved file."""
    rec = st.session_state.get("render_uploads", {}).get(full_key)
    if not rec:
        return False
    # If you want to be strict and ensure the file still exists on disk:
    try:
        return os.path.exists(rec.get("path", ""))
    except Exception:
        return False

def validate_static_fields(schema, current_task):
    from json_template import DATA_INPUT_OUTPUT_TS

    missing = []

    
    skip_fields = set(DATA_INPUT_OUTPUT_TS.keys())
    skip_keys = {
        "input_content_rtstruct_subtype",
        "output_content_rtstruct_subtype",
    }
    skip_sections = {
        "evaluation_data_methodology_results_commisioning",
        "learning_architecture",
        "qualitative_evaluation",
    }

    for section, fields in schema.items():

        if section in skip_sections or not isinstance(fields, dict):
            continue
        for key, props in fields.items():

            if key in skip_keys or (key in skip_fields and section in [
                "training_data",
                "evaluation_data_methodology_results_commisioning",
            ]):
                continue
            
            full_key = f"{section}_{key}"
            if props.get("required", False):
                model_types = props.get("model_types")
                if model_types is None or (
                    current_task and current_task in model_types
                ):
                    field_type = (props.get("type") or "").lower()
                    if field_type == "image":
                        if not _has_required_image(full_key):
                            label = props.get("label", key) or key.replace("_", " ").title()
                            missing.append((section, label))
                        continue
                    
                    value = st.session_state.get(full_key)
                    if is_empty(value):
                        label = props.get("label", key) or key.replace("_", " ").title()
                        missing.append((section, label))
    return missing


def validate_learning_architectures(schema):
    missing = []

    def is_empty(value):
        return value in ("", None, [], {})

    forms = st.session_state.get("learning_architecture_forms", {})
    schema_fields = schema.get("learning_architecture", {})

    for i in range(len(forms)):
        prefix = f"learning_architecture_{i}_"

        for field in LEARNING_ARCHITECTURE:
            props = schema_fields.get(field)
            if not props:
                continue

            if props.get("required", False):
                full_key = f"{prefix}{field}"
                value = st.session_state.get(full_key)

                if is_empty(value):
                    label = props.get("label", field.replace("_", " ").title())
                    missing.append(
                        (
                            "learning_architecture",
                            f"{label} (Learning Architecture {i + 1})",
                        )
                    )
    return missing


def validate_modalities_fields(schema, current_task):
    missing = []

    def is_empty(value):
        return value in ("", None, [], {})

    modalities = []
    for key, value in st.session_state.items():
        if key.endswith("model_inputs") and isinstance(value, list):
            for item in value:
                modalities.append((item, "model_inputs"))
        elif key.endswith("model_outputs") and isinstance(value, list):
            for item in value:
                modalities.append((item, "model_outputs"))

    for modality, source in modalities:
        clean = modality.strip().replace(" ", "_").lower()

        prefix_train = f"training_data_{clean}_{source}_"
        for field, label in DATA_INPUT_OUTPUT_TS.items():
            full_key = f"{prefix_train}{field}"
            value = st.session_state.get(full_key)
            if is_empty(value):
                missing.append(
                    (
                        "training_data",
                        f"{label} ({modality} - {source})",
                    )
                )
        eval_forms = st.session_state.get("evaluation_forms", [])
        for name in eval_forms:
            slug = name.replace(" ", "_")
            prefix = f"evaluation_{slug}_"

            prefix_eval = f"{prefix}{clean}_"
            for field, label in DATA_INPUT_OUTPUT_TS.items():
                full_key = f"{prefix_eval}{source}_{field}"
                #print(f"Checking {full_key}")
                value = st.session_state.get(full_key)
                if is_empty(value):
                    missing.append(
                        (
                            "evaluation_data_methodology_results_commisioning",
                            f"{label} ({modality} - {source})(Eval: {name})",
                        )
                    )

    return missing


def validate_evaluation_forms(schema, current_task):
    from json_template import DATA_INPUT_OUTPUT_TS
    missing = []

    skip_fields = set(DATA_INPUT_OUTPUT_TS.keys())

    def is_empty(value):
        return value in ("", None, [], {})

    eval_forms = st.session_state.get("evaluation_forms", [])
    eval_section = schema.get("evaluation_data_methodology_results_commisioning", {})
    qual_eval_section = schema.get("qualitative_evaluation", {})
    metric_fields = TASK_METRIC_MAP.get(current_task, [])

    metric_field_keys = set()
    for type_field in metric_fields:
        metric_field_keys.update(EVALUATION_METRIC_FIELDS.get(type_field, []))

    for name in eval_forms:
        slug = name.replace(" ", "_")
        prefix = f"evaluation_{slug}_"
        approved_same_key = f"{prefix}evaluated_same_as_approved"
        approved_same = st.session_state.get(approved_same_key, False)

        for key, props in eval_section.items():

            if key in metric_field_keys or key in skip_fields:
                continue

            if approved_same and key in [
                "evaluated_by_name",
                "evaluated_by_institution",
                "evaluated_by_contact_email",
            ]:
                continue

            if props.get("required", False):
                model_types = props.get("model_types")
                if model_types is None or (
                    current_task and current_task in model_types
                ):
                    value = st.session_state.get(f"{prefix}{key}")
                    if is_empty(value):
                        label = props.get("label", key) or key.replace("_", " ").title()
                        missing.append(
                            (
                                "evaluation_data_methodology_results_commisioning",
                                f"{label} (Eval: {name})",
                            )
                        )

        for type_field in metric_fields:
            entry_list = st.session_state.get(f"{prefix}{type_field}_list", [])
            for metric_name in entry_list:
                metric_short = metric_name.split(" (")[0]
                metric_prefix = f"evaluation_{slug}.{metric_name}"

                for field_key in EVALUATION_METRIC_FIELDS.get(type_field, []):
                    props = eval_section.get(field_key)
                    if not props or not props.get("required", False):
                        continue

                    full_key = f"{metric_prefix}_{field_key}"
                    value = st.session_state.get(full_key)
                    if is_empty(value):
                        label = props.get("label", field_key.replace("_", " ").title())
                        missing.append(
                            (
                                "evaluation_data_methodology_results_commisioning",
                                f"{label} (Metric: {metric_short}, Eval: {name})",
                            )
                        )

        qprefix = f"{prefix}qualitative_evaluation_"
        for key, props in qual_eval_section.items():
            if props.get("required", False):
                full_key = f"{qprefix}{key}"
                value = st.session_state.get(full_key)
                if is_empty(value):
                    label = props.get("label", key) or key.replace("_", " ").title()
                    missing.append(
                        (
                            "evaluation_data_methodology_results_commisioning",
                            f"{label} (Eval: {name})",
                        )
                    )


    return missing


def validate_required_fields(schema, current_task=None):
    res1 = validate_static_fields(schema, current_task)
    res2 = validate_learning_architectures(schema)
    res3 = validate_modalities_fields(schema, current_task)
    res4 = validate_evaluation_forms(schema, current_task)
    return res1 + res2 + res3 + res4
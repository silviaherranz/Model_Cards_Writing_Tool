from template_base import DATA_INPUT_OUTPUT_TS, EVALUATION_METRIC_FIELDS, LEARNING_ARCHITECTURE, TASK_METRIC_MAP


def validate_static_fields(schema, session_state, current_task):
    from template_base import DATA_INPUT_OUTPUT_TS

    missing = []

    def is_empty(value):
        return value in ("", None, [], {})

    skip_fields = set(DATA_INPUT_OUTPUT_TS.keys())
    skip_keys = {
        "input_content_rtstruct_subtype",
        "output_content_rtstruct_subtype",
    }  # puedes agregar más claves aquí
    skip_sections = {
        "evaluation_data_methodology_results_commisioning",
        "learning_architecture",
    }

    for section, fields in schema.items():
        if section in skip_sections:
            continue
        if not isinstance(fields, dict):
            continue
        for key, props in fields.items():
            if key in skip_fields and section in [
                "training_data_methodology_results_commisioning",
                "evaluation_data_methodology_results_commisioning",
            ]:
                continue
        for key, props in fields.items():
            if key in skip_keys:
                continue

            full_key = f"{section}_{key}"
            if props.get("required", False):
                model_types = props.get("model_types")
                if model_types is None or (
                    current_task and current_task in model_types
                ):
                    value = session_state.get(full_key)
                    if is_empty(value):
                        label = props.get("label", key) or key.replace("_", " ").title()
                        missing.append((section, label))
    return missing


def validate_learning_architectures(schema, session_state):
    missing = []

    def is_empty(value):
        return value in ("", None, [], {})

    forms = session_state.get("learning_architecture_forms", {})
    schema_fields = schema.get("learning_architecture", {})

    for i in range(len(forms)):
        prefix = f"learning_architecture_{i}_"

        for field in LEARNING_ARCHITECTURE:
            props = schema_fields.get(field)
            if not props:
                continue

            if props.get("required", False):
                full_key = f"{prefix}{field}"
                value = session_state.get(full_key)

                if is_empty(value):
                    label = props.get("label", field.replace("_", " ").title())
                    missing.append(
                        (
                            "learning_architecture",
                            f"{label} (Learning Architecture {i + 1})",
                        )
                    )

    return missing


def validate_modalities_fields(schema, session_state, current_task):
    missing = []

    def is_empty(value):
        return value in ("", None, [], {})

    modalities = []
    for key, value in session_state.items():
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
            value = session_state.get(full_key)
            if is_empty(value):
                missing.append(
                    (
                        "training_data_methodology_results_commisioning",
                        f"{label} ({modality} - {source})",
                    )
                )

        # --- EVALUATION ---
        prefix_eval = f"evaluation_data_{clean}_{source}_"
        for field, label in DATA_INPUT_OUTPUT_TS.items():
            full_key = f"{prefix_eval}{field}"
            value = session_state.get(full_key)
            if is_empty(value):
                missing.append(
                    (
                        "evaluation_data_methodology_results_commisioning",
                        f"{label} ({modality} - {source})",
                    )
                )

    return missing


def validate_evaluation_forms(schema, session_state, current_task):
    missing = []

    def is_empty(value):
        return value in ("", None, [], {})

    eval_forms = session_state.get("evaluation_forms", [])
    eval_section = schema.get("evaluation_data_methodology_results_commisioning", {})
    metric_fields = TASK_METRIC_MAP.get(current_task, [])

    # Recolectar todas las keys métricas válidas para la tarea actual
    metric_field_keys = set()
    for type_field in metric_fields:
        metric_field_keys.update(EVALUATION_METRIC_FIELDS.get(type_field, []))

    for name in eval_forms:
        slug = name.replace(" ", "_")
        prefix = f"evaluation_{slug}_"
        approved_same_key = f"{prefix}evaluated_same_as_approved"
        approved_same = session_state.get(approved_same_key, False)

        # 🔹 Validación general (no métricas)
        for key, props in eval_section.items():
            if key in metric_field_keys:
                continue

            if approved_same and key in [
                "evaluated_by_institution",
                "evaluated_by_contact_email",
            ]:
                continue

            if props.get("required", False):
                model_types = props.get("model_types")
                if model_types is None or (
                    current_task and current_task in model_types
                ):
                    value = session_state.get(f"{prefix}{key}")
                    if is_empty(value):
                        label = props.get("label", key) or key.replace("_", " ").title()
                        missing.append(
                            (
                                "evaluation_data_methodology_results_commisioning",
                                f"{label} (Eval: {name})",
                            )
                        )

        # 🔹 Validación específica de métricas
        for type_field in metric_fields:
            entry_list = session_state.get(f"{prefix}{type_field}_list", [])
            for metric_name in entry_list:
                metric_short = metric_name.split(" (")[0]
                metric_prefix = f"evaluation_{slug}.{metric_name}"

                for field_key in EVALUATION_METRIC_FIELDS.get(type_field, []):
                    props = eval_section.get(field_key)
                    if not props or not props.get("required", False):
                        continue

                    full_key = f"{metric_prefix}_{field_key}"
                    value = session_state.get(full_key)
                    if is_empty(value):
                        label = props.get("label", field_key.replace("_", " ").title())
                        missing.append(
                            (
                                "evaluation_data_methodology_results_commisioning",
                                f"{label} (Metric: {metric_short}, Eval: {name})",
                            )
                        )
    return missing


def validate_required_fields(schema, session_state, current_task=None):
    missing_fields = []

    missing_fields += validate_static_fields(schema, session_state, current_task)
    missing_fields += validate_learning_architectures(schema, session_state)
    missing_fields += validate_modalities_fields(schema, session_state, current_task)
    missing_fields += validate_evaluation_forms(schema, session_state, current_task)

    return missing_fields
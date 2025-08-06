import json
import streamlit as st
import re
from datetime import datetime, date, timedelta
import base64


def get_base64_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def generate_date_options(start_year=1970, end_year=None):
    if end_year is None:
        end_year = datetime.today().year
    start = date(start_year, 1, 1)
    end = datetime.today().date()
    delta = (end - start).days
    return [start + timedelta(days=i) for i in range(delta + 1)]


def require_task():
    if "task" not in st.session_state:
        from main import task_selector_page

        st.session_state.runpage = task_selector_page
        st.rerun()


@st.cache_data  # This avoids reloading on every rerun
def get_model_card_schema():
    with open("model_card_schema.json", "r") as f:
        return json.load(f)


def store_value(key):
    st.session_state[key] = st.session_state["_" + key]


def load_value(key, default=None):
    if key not in st.session_state:
        st.session_state[key] = default
    st.session_state["_" + key] = st.session_state[key]

def validate_static_fields(schema, session_state, current_task):
    from template_base import DATA_INPUT_OUTPUT_TS
    missing = []

    def is_empty(value):
        return value in ("", None, [], {})

    # Evitar validar estos campos como parte del bloque general
    skip_fields = set(DATA_INPUT_OUTPUT_TS.keys())

    for section, fields in schema.items():
        if not isinstance(fields, dict):
            continue
        for key, props in fields.items():
            if key in skip_fields and section in ["training_data_methodology_results_commisioning", "evaluation_data_methodology_results_commisioning"]:
                continue

            full_key = f"{section}_{key}"
            if props.get("required", False):
                model_types = props.get("model_types")
                if model_types is None or (current_task and current_task in model_types):
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
    for i in range(len(forms)):
        prefix = f"learning_architecture_{i}_"
        for field, props in schema.get("learning_architectures", {}).items():
            if props.get("required", False):
                full_key = f"{prefix}{field}"
                value = session_state.get(full_key)
                if is_empty(value):
                    label = props.get("label", field)
                    missing.append(("learning_architectures", f"{label} (entry {i+1})"))
    return missing

def validate_modalities_fields(schema, session_state, current_task):
    from template_base import DATA_INPUT_OUTPUT_TS
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
                missing.append((
                    "training_data_methodology_results_commisioning",
                    f"{label} ({modality} - {source})"
                ))

        # --- EVALUATION ---
        prefix_eval = f"evaluation_data_{clean}_{source}_"
        for field, label in DATA_INPUT_OUTPUT_TS.items():
            full_key = f"{prefix_eval}{field}"
            value = session_state.get(full_key)
            if is_empty(value):
                missing.append((
                    "evaluation_data_methodology_results_commisioning",
                    f"{label} ({modality} - {source})"
                ))


    return missing
def validate_evaluation_forms(schema, session_state, current_task):
    print("✅ validate_evaluation_forms() ejecutada")

    from template_base import EVALUATION_METRIC_FIELDS, TASK_METRIC_MAP
    missing = []

    def is_empty(value):
        return value in ("", None, [], {})

    eval_forms = session_state.get("evaluation_forms", [])
    for name in eval_forms:
        slug = name.replace(" ", "_")
        prefix = f"evaluation_{slug}_"

        approved_same_key = f"{prefix}evaluated_same_as_approved"
        approved_same = session_state.get(approved_same_key, False)

        eval_section = schema.get("evaluation_data_methodology_results_commisioning", {})
        for key, props in eval_section.items():
            full_key = f"{prefix}{key}"

            # ✅ Inyectar campos "aprobados" temporalmente si el checkbox está activo
            if approved_same and key in [
                "evaluated_by_name",
                "evaluated_by_institution",
                "evaluated_by_contact_email",
            ]:
                value = (
                    session_state.get(f"model_basic_information_clearance_approved_by_{key.split('_')[-1]}", "")
                )
            else:
                value = session_state.get(full_key)

            print(f"🔍 Campo: {key}, Clave: {full_key}, Valor: {value!r}")

            if props.get("required", False):
                model_types = props.get("model_types")
                if model_types is None or (current_task and current_task in model_types):
                    if is_empty(value):
                        label = props.get("label", key)
                        missing.append(("evaluation_data", f"{label} (Evaluation: {name})"))
                    else:
                        print(f"Campo válido: {key} = {value!r}")

        # Métricas
        metric_fields = TASK_METRIC_MAP.get(current_task, [])
        for type_field in metric_fields:
            entry_list = session_state.get(f"{prefix}{type_field}_list", [])
            for metric_name in entry_list:
                metric_prefix = f"evaluation_{slug}.{metric_name}"
                for field in EVALUATION_METRIC_FIELDS.get(type_field, []):
                    full_key = f"{metric_prefix}_{field}"
                    value = session_state.get(full_key)
                    if is_empty(value):
                        label = field.replace("_", " ").title()
                        missing.append((
                            "evaluation_data",
                            f"{label} (Metric: {metric_name}, Eval: {name})"
                        ))

    return missing


# def validate_required_fields(schema, session_state, current_task=None):
#     print("validate_required_fields() ejecutada")

#     missing_fields = []

#     missing_fields += validate_static_fields(schema, session_state, current_task)
#     missing_fields += validate_learning_architectures(schema, session_state)
#     missing_fields += validate_modalities_fields(schema, session_state, current_task)
#     missing_fields += validate_evaluation_forms(schema, session_state, current_task)

#     return missing_fields

def validate_required_fields(eval_key, required_fields):
    missing_fields = []

    for field, label in required_fields:
        full_key = f"evaluation_{eval_key}_{field}"
        value = st.session_state.get(full_key, "[NO EXISTE]")

        print(f"🔍 Campo en evaluación: {field}")
        print(f"    Clave completa buscada: {full_key}")
        print(f"    Valor encontrado en session_state: {repr(value)}")

        # Consideramos como MISSING si es vacío, None o una lista vacía
        if value in ("", None, []) or (isinstance(value, str) and value.strip() == ""):
            print(f"    ❌ MISSING: {field} - {label}")
            missing_fields.append(f"{label}")
        else:
            print(f"    ✅ Campo válido: {field} con valor {repr(value)}")

    return missing_fields


def is_yyyymmdd(s):
    return isinstance(s, str) and len(s) == 8 and s.isdigit()

def to_date(s):
    try:
        return datetime.strptime(s, "%Y%m%d").date()
    except:
        return None

def set_safe_date_field(base_key: str, yyyymmdd_string: str | None):
    """
    Guarda de forma segura un campo de fecha en st.session_state:
    - Acepta string YYYYMMDD válida.
    - Guarda .date() en las claves de widget.
    - Deja None si el valor no es válido.
    """
    widget_key = f"{base_key}_widget"
    raw_key = f"_{widget_key}"

    if is_yyyymmdd(yyyymmdd_string):
        parsed_date = to_date(yyyymmdd_string)
    else:
        parsed_date = None

    # Guardar para el widget
    st.session_state[base_key] = yyyymmdd_string if parsed_date else None
    st.session_state[widget_key] = parsed_date
    st.session_state[raw_key] = parsed_date


def populate_session_state_from_json(data):
    if "task" in data:
        st.session_state["task"] = data["task"]

    for section, content in data.items():
        if section == "learning_architectures":
            st.session_state["learning_architecture_forms"] = {
                f"Learning Architecture {i + 1}": {} for i in range(len(content))
            }
            for i, arch in enumerate(content):
                prefix = f"learning_architecture_{i}_"
                for key, value in arch.items():
                    full_key = f"{prefix}{key}"
                    st.session_state[full_key] = value

        elif section == "training_data":
            # Guarda los campos planos y listas
            for k, v in content.items():
                full_key = f"{section}_{k}"
                if not isinstance(v, list):
                    st.session_state[full_key] = v
                else:
                    st.session_state[full_key] = v
                    st.session_state[full_key + "_list"] = v

            # Maneja los campos técnicos de inputs/outputs
            ios = content.get("inputs_outputs_technical_specifications", [])
            for io in ios:
                clean = io["input_content"].strip().replace(" ", "_").lower()
                src = io["source"]
                for io_key, io_val in io.items():
                    if io_key not in ["input_content", "source"]:
                        io_full_key = f"training_data_{clean}_{src}_{io_key}"
                        st.session_state[io_full_key] = io_val
                        st.session_state["_" + io_full_key] = io_val  # <- Esto es CLAVE


        elif section == "evaluations":
            eval_names = [entry["name"] for entry in content]
            st.session_state["evaluation_forms"] = eval_names

            for entry in content:
                name = entry["name"].replace(" ", "_")
                prefix = f"evaluation_{name}_"

                for key, value in entry.items():
                    if key == "inputs_outputs_technical_specifications":
                        for io in value:
                            clean = io["input_content"].strip().replace(" ", "_").lower()
                            src = io["source"]
                            for io_key, io_val in io.items():
                                if io_key not in ["input_content", "source"]:
                                    io_full_key = f"{prefix}{clean}_{src}_{io_key}"
                                    st.session_state[io_full_key] = io_val
                                    st.session_state["_" + io_full_key] = io_val


                    elif isinstance(value, list) and key.startswith("type_"):
                        metric_names = [m["name"] for m in value]
                        st.session_state[f"{prefix}{key}_list"] = metric_names
                        st.session_state[f"{prefix}{key}"] = metric_names

                        for metric in value:
                            metric_prefix = f"evaluation_{name}.{metric['name']}"
                            for m_field, m_val in metric.items():
                                if m_field != "name":
                                    st.session_state[f"{metric_prefix}_{m_field}"] = m_val

                    elif is_yyyymmdd(value):
                        date_obj = to_date(value)
                        if date_obj:
                            widget_key = f"{prefix}{key}_widget"
                            st.session_state[widget_key] = date_obj
                            st.session_state[f"_{widget_key}"] = date_obj
                            st.session_state[f"{prefix}{key}"] = value
                        else:
                            st.session_state[f"{prefix}{key}"] = value
                    else:
                        st.session_state[f"{prefix}{key}"] = value

        elif isinstance(content, dict):
            for k, v in content.items():
                full_key = f"{section}_{k}"
                st.session_state[full_key] = v

                if k.endswith("creation_date"):
                    set_safe_date_field(full_key, v)

                if isinstance(v, list):
                    st.session_state[full_key + "_list"] = v



def light_header(text, size="16px", bottom_margin="1em"):
    st.markdown(
        f"""
        <div style='font-size: {size}; font-weight: normal; color: #444; margin-bottom: {bottom_margin};'>
            {text}
        </div>
    """,
        unsafe_allow_html=True,
    )


def light_header_italics(text, size="16px", bottom_margin="1em"):
    st.markdown(
        f"""
        <div style='font-size: {size}; font-style: italic; font-weight: normal; color: #444; margin-bottom: {bottom_margin};'>
            {text}
        </div>
    """,
        unsafe_allow_html=True,
    )


def title_header(text, size="1.2rem", bottom_margin="1em", top_margin="0.5em"):
    st.markdown(
        f"""
        <div style='
            font-size: {size};
            font-weight: 600;
            color: #333;
            margin-top: {top_margin};
            margin-bottom: {bottom_margin};
        '>{text}</div>
        """,
        unsafe_allow_html=True,
    )


def title_header_grey(text, size="1.3rem", bottom_margin="0.2em", top_margin="0.5em"):
    st.markdown(
        f"""
        <div style='
            font-size: {size};
            font-weight: 600;
            color: #6c757d;
            margin-top: {top_margin};
            margin-bottom: {bottom_margin};
        '>{text}</div>
        """,
        unsafe_allow_html=True,
    )


def title(text, size="2rem", bottom_margin="0.1em", top_margin="0.4em"):
    st.markdown(
        f"""
        <div style='
            font-size: {size};
            font-weight: 650;
            color: #222;
            margin-top: {top_margin};
            margin-bottom: {bottom_margin};
            text-align: justify;
        '>{text}</div>
        """,
        unsafe_allow_html=True,
    )


def subtitle(text, size="1.05rem", bottom_margin="0.8em", top_margin="0.2em"):
    st.markdown(
        f"""
        <div style='
            font-size: {size};
            font-weight: 400;
            color: #444;
            margin-top: {top_margin};
            margin-bottom: {bottom_margin};
            text-align: justify;
        '>{text}</div>
        """,
        unsafe_allow_html=True,
    )


def section_divider():
    st.markdown(
        "<hr style='margin: 1.5em 0; border: none; border-top: 1px solid #ccc;'>",
        unsafe_allow_html=True,
    )


def strip_brackets(text):
    return re.sub(r"\s*\(.*?\)", "", text).strip()

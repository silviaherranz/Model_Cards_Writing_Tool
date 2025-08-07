import json
import streamlit as st
import re
from datetime import datetime, date, timedelta
import base64
from fpdf import FPDF

from middleMan import parse_into_json
from template_base import DATA_INPUT_OUTPUT_TS, EVALUATION_METRIC_FIELDS, LEARNING_ARCHITECTURE, TASK_METRIC_MAP


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

    skip_fields = set(DATA_INPUT_OUTPUT_TS.keys())
    skip_keys = {"input_content_rtstruct_subtype", "output_content_rtstruct_subtype"}  # puedes agregar más claves aquí
    skip_sections = {"evaluation_data_methodology_results_commisioning", "learning_architecture"}

    for section, fields in schema.items():
        if section in skip_sections:
            continue
        if not isinstance(fields, dict):
            continue
        for key, props in fields.items():
            if key in skip_fields and section in ["training_data_methodology_results_commisioning", "evaluation_data_methodology_results_commisioning"]:
                continue
        for key, props in fields.items():
            if key in skip_keys:
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
                    missing.append((
                        "learning_architecture",
                        f"{label} (Learning Architecture {i+1})"
                    ))

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

            if approved_same and key in ["evaluated_by_institution", "evaluated_by_contact_email"]:
                continue

            if props.get("required", False):
                model_types = props.get("model_types")
                if model_types is None or (current_task and current_task in model_types):
                    value = session_state.get(f"{prefix}{key}")
                    if is_empty(value):
                        label = props.get("label", key) or key.replace("_", " ").title()
                        missing.append(("evaluation_data_methodology_results_commisioning", f"{label} (Eval: {name})"))

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
                        missing.append((
                            "evaluation_data_methodology_results_commisioning",
                            f"{label} (Metric: {metric_short}, Eval: {name})"
                        ))
    return missing


def validate_required_fields(schema, session_state, current_task=None):
    missing_fields = []

    missing_fields += validate_static_fields(schema, session_state, current_task)
    missing_fields += validate_learning_architectures(schema, session_state)
    missing_fields += validate_modalities_fields(schema, session_state, current_task)
    missing_fields += validate_evaluation_forms(schema, session_state, current_task)

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


def export_json_pretty_to_pdf(schema_path, filename="output.pdf"):
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    structured_data = json.loads(parse_into_json(schema))

    pretty = json.dumps(structured_data, indent=2, ensure_ascii=False)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=10)

    for line in pretty.split("\n"):
        pdf.multi_cell(0, 5, line)

    pdf.output(filename)



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

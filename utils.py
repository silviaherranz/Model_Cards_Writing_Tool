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


def validate_required_fields(schema, session_state, current_task=None):
    missing_fields = []
    for section, fields in schema.items():
        for key, props in fields.items():
            full_key = f"{section}_{key}"
            if props.get("required", False):
                model_types = props.get("model_types")
                if model_types is None or (
                    current_task and current_task in model_types
                ):
                    value = session_state.get(full_key)
                    if value in ("", None, [], {}):
                        label = props.get("label", key)
                        missing_fields.append(label)
    return missing_fields

def populate_session_state_from_json(data):
    if "task" in data:
        st.session_state["task"] = data["task"]

    for section, content in data.items():
        if section == "learning_architectures":
            st.session_state["learning_architecture_forms"] = {
                f"Learning Architecture {i+1}": {} for i in range(len(content))
            }
            for i, arch in enumerate(content):
                prefix = f"learning_architecture_{i}_"
                for key, value in arch.items():
                    st.session_state[f"{prefix}{key}"] = value

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
                                    st.session_state[f"{prefix}{clean}_{src}_{io_key}"] = io_val

                    elif isinstance(value, list) and key.startswith("type_"):
                        st.session_state[f"{prefix}{key}_list"] = [m["name"] for m in value]
                        st.session_state[f"{prefix}{key}"] = [m["name"] for m in value]

                        for metric in value:
                            metric_prefix = f"evaluation_{name}.{metric['name']}"
                            for m_field, m_val in metric.items():
                                if m_field != "name":
                                    st.session_state[f"{metric_prefix}_{m_field}"] = m_val

                    # Soporte especial para fechas de evaluación (evaluation_date, creation_date)
                    if isinstance(value, str) and len(value) == 8 and value.isdigit():
                        try:
                            date_obj = datetime.strptime(value, "%Y%m%d")
                            widget_key = f"{prefix}{key}_widget"
                            st.session_state[widget_key] = date_obj           # para el valor del widget (value=)
                            st.session_state[f"_{widget_key}"] = date_obj     # para la clave key= del widget
                            st.session_state[f"{prefix}{key}"] = value        # guarda el valor original (YYYYMMDD)
                            continue  # evita duplicar seteo abajo
                        except:
                            pass  
                    else:
                        st.session_state[f"{prefix}{key}"] = value

        elif isinstance(content, dict):
            for k, v in content.items():
                full_key = f"{section}_{k}"
                st.session_state[full_key] = v

                if isinstance(v, str) and len(v) == 8 and v.isdigit():
                    try:
                        dt = datetime.strptime(v, "%Y%m%d")
                        widget_key = f"{full_key}_widget"
                        st.session_state[widget_key] = dt
                        st.session_state[f"_{widget_key}"] = dt  

                        if full_key == "card_metadata_creation_date":
                            st.session_state["_card_metadata_creation_date_widget"] = dt
                    except:
                        pass

                    # 🟢 Si es lista para campos tipo select + botón ➕
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

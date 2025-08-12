import io
import json
import zipfile
import streamlit as st
import re
from datetime import datetime, date, timedelta
import base64
from fpdf import FPDF
from middleMan import parse_into_json


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
            for k, v in content.items():
                full_key = f"{section}_{k}"
                if not isinstance(v, list):
                    st.session_state[full_key] = v
                else:
                    st.session_state[full_key] = v
                    st.session_state[full_key + "_list"] = v

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
                            clean = (
                                io["input_content"].strip().replace(" ", "_").lower()
                            )
                            src = io["source"]
                            for io_key, io_val in io.items():
                                if io_key not in ["input_content", "source"]:
                                    io_full_key = f"{prefix}{clean}_{src}_{io_key}"
                                    st.session_state[io_full_key] = io_val
                                    st.session_state["_" + io_full_key] = io_val

                    elif key == "qualitative_evaluation" and isinstance(value, dict):
                        qprefix = f"evaluation_{name}_qualitative_evaluation_"

                        for simple_field in [
                            "evaluators_information",
                            "explainability",
                            "citation_details",
                        ]:
                            qkey = f"{qprefix}{simple_field}"
                            qval = value.get(simple_field, "")
                            st.session_state[qkey] = qval
                            st.session_state["_" + qkey] = qval

                        for block in [
                            "likert_scoring",
                            "turing_test",
                            "time_saving",
                            "other",
                        ]:
                            b = value.get(block, {})
                            if isinstance(b, dict):
                                mkey = f"{qprefix}{block}_method"
                                rkey = f"{qprefix}{block}_results"
                                mval = b.get("method", "")
                                rval = b.get("results", "")
                                st.session_state[mkey] = mval
                                st.session_state[rkey] = rval
                                st.session_state["_" + mkey] = mval
                                st.session_state["_" + rkey] = rval

                    elif isinstance(value, list) and key.startswith("type_"):
                        metric_names = [m["name"] for m in value]
                        st.session_state[f"{prefix}{key}_list"] = metric_names
                        st.session_state[f"{prefix}{key}"] = metric_names

                        for metric in value:
                            metric_prefix = f"evaluation_{name}_{metric['name']}"
                            for m_field, m_val in metric.items():
                                if m_field != "name":
                                    st.session_state[f"{metric_prefix}_{m_field}"] = (
                                        m_val
                                    )

                    elif isinstance(value, str) and is_yyyymmdd(value):
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
    

def export_model_card_zip(schema):
    import streamlit as st
    from pathlib import Path

    json_str = parse_into_json(schema)
    data = json.loads(json_str)

    def _maybe_add(zf, relpath: str, arcname: str | None = None):
        if not relpath:
            return
        p = Path(relpath)
        if p.exists() and p.is_file():
            zf.write(p, arcname=arcname or relpath)

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        # the model card JSON
        zf.writestr("model_card.json", json_str)

        # appendix
        for item in data.get("appendix", []):
            rel = item.get("relpath")
            if rel:
                p = Path(rel)
                arc = f"assets/appendix/{p.name}"
                _maybe_add(zf, rel, arc)

        # images by field
        for field_key, items in data.get("assets", {}).get("images", {}).items():
            for item in items:
                rel = item.get("relpath")
                if rel:
                    p = Path(rel)
                    arc = f"assets/images/{field_key}/{p.name}"
                    _maybe_add(zf, rel, arc)

    buf.seek(0)
    st.download_button(
        "Download model card + assets (.zip)",
        data=buf.getvalue(),
        file_name="model_card_with_assets.zip",
        mime="application/zip",
    )



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


def enlarge_tab_titles(font_px: int, underline_px: int = 4, pad_y: int = 6):
    st.markdown(
        f"""
    <style>
      /* Streamlit 1.4x+: los tabs son botones con role=tab */
      [data-testid="stTabs"] button[role="tab"] {{
        font-size: {font_px}px !important;
        padding-top: {pad_y}px !important;
        padding-bottom: {pad_y}px !important;
        line-height: 1.2 !important;
      }}
      /* Algunas builds envuelven el texto en <p> */
      [data-testid="stTabs"] button[role="tab"] p {{
        font-size: {font_px}px !important;
      }}
      /* Subrayado de la pestaña activa (opcional) */
      [data-testid="stTabs"] [data-baseweb="tab-highlight"] {{
        height: {underline_px}px !important;
      }}
      /* Fallback para implementaciones antiguas basadas en baseweb */
      [data-testid="stTabs"] [data-baseweb="tab"] {{
        font-size: {font_px}px !important;
        padding-top: {pad_y}px !important;
        padding-bottom: {pad_y}px !important;
      }}
    </style>
    """,
        unsafe_allow_html=True,
    )

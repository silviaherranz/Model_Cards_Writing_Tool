import json
import streamlit as st
import re


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


def title_header(text, size="1.1rem", bottom_margin="1em", top_margin="0.5em"):
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


def subtitle(text, size="1rem", bottom_margin="0.8em", top_margin="0.2em"):
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

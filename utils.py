import json
import streamlit as st

@st.cache_data  # This avoids reloading on every rerun
def get_model_card_schema():
    with open("model_card_schema.json", "r") as f:
        return json.load(f)
    

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
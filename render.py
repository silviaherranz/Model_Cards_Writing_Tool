# render.py
import streamlit as st
from persist import persist


def render_schema_section(schema_section, section_prefix=""):
    """Render a section of the schema, grouping some fields into expanders."""
    EXPANDERS = {
        "model_basic_information": {
            "Versioning": ["version_number", "version_changes"],
            "Model Scope": ["model_scope_summary", "model_scope_anatomical_site"]
        },
        "card_metadata": {
            "Card Metadata": ["creation_date", "version_number", "version_changes", "doi"]
        }
    }

    used_keys = set()

    # Render grouped fields in expanders
    for expander, keys in EXPANDERS.get(section_prefix, {}).items():
        with st.expander(expander):
            for key in keys:
                if key in schema_section:
                    render_field(key, schema_section[key], section_prefix)
                    used_keys.add(key)

    # Render all remaining fields
    for key, props in schema_section.items():
        if key not in used_keys:
            render_field(key, props, section_prefix)


def render_field(key, props, section_prefix):
    """Render a single field based on type and schema properties."""
    full_key = f"{section_prefix}_{key}"
    label = props.get("label", key)
    description = props.get("description", "")
    example = props.get("example", "")
    field_type = props.get("type", "string")
    required = props.get("required", False)
    options = props.get("options", [])

    create_helpicon(label, description, field_type, example, required)

    if field_type == "select":
        st.selectbox(label, options=options, key=persist(full_key), help=description)
    else:
        st.text_input(label, key=persist(full_key), label_visibility="hidden")


def create_helpicon(label, description, field_format, example, required=False):
    """Render a tooltip-style help icon next to field labels."""
    required_tag = "<span style='color: black; font-size: 1.2em; cursor: help;' title='Required field'>*</span>" if required else ""
    st.markdown("""
    <style>
    .tooltip-inline {
        display: inline-block;
        position: relative;
        margin-left: 4px;
        cursor: pointer;
        font-size: 0.8em;
        color: #999;
    }

    .tooltip-inline .tooltiptext {
        visibility: hidden;
        width: 260px;
        background-color: #f9f9f9;
        color: #333;
        text-align: left;
        border-radius: 6px;
        border: 1px solid #ccc;
        padding: 10px;
        position: absolute;
        bottom: 150%;
        left: 0;
        z-index: 10;
        box-shadow: 0px 0px 10px rgba(0,0,0,0.1);
        font-weight: normal;
        font-size: 0.9em;
        line-height: 1.4;
    }

    .tooltip-inline:hover .tooltiptext {
        visibility: visible;
    }

    div[data-testid="stTextInput"] {
        margin-top: -10px;
    }
    </style>
    """, unsafe_allow_html=True)

    tooltip_html = f"""
    <div style='margin-bottom: -8px; font-weight: 500; font-size: 0.9em;'>
        {label} {required_tag}
        <span class="tooltip-inline">ⓘ
            <span class="tooltiptext">
                <span style="font-weight: bold;">Description:</span> {description}<br><br>
                <span style="font-weight: bold;">Format:</span> {field_format}<br><br>
                <span style="font-weight: bold;">Example(s):</span> {example}
            </span>
        </span>
    </div>
    """
    st.markdown(tooltip_html, unsafe_allow_html=True)

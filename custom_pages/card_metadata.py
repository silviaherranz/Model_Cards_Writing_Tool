from datetime import datetime
import streamlit as st
import utils
from render import create_helpicon, render_field


def card_metadata_render():
    st.markdown("""
    <style>
    /* hide Streamlit Cloud’s top-right toolbar (includes the GitHub icon) */
    div[data-testid="stToolbar"] { visibility: hidden; height: 0; }

    /* optional: also hide the 'Manage app' badge and footer */
    a[data-testid="viewerBadge_link"] { display: none !important; }
    div[data-testid="stStatusWidget"] { display: none !important; }
    footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)
            
    from side_bar import sidebar_render

    sidebar_render()
    model_card_schema = utils.get_model_card_schema()
    section = model_card_schema["card_metadata"]
    utils.title("Card Metadata")
    utils.subtitle("with relevant information about the model card itself")

    if "card_creation_date" in section:
        props = section["card_creation_date"]
        label = props.get("label", "Creation Date")
        description = props.get("description", "")
        example = props.get("example", "")
        required = props.get("required", False)
        field_type = props.get("type", "date")

        create_helpicon(label, description, field_type, example, required)

        # Only load if a real stored value exists, not default today
        if "card_metadata_card_creation_date" not in st.session_state:
            st.session_state["card_metadata_card_creation_date"] = None

        st.date_input(
            "Click and select a date",
            value=st.session_state["card_metadata_card_creation_date"],
            min_value=datetime(1900, 1, 1),
            max_value=datetime.today(),
            key="_card_metadata_card_creation_date",
        )

        user_date = st.session_state.get("_card_metadata_card_creation_date")

        if user_date:
            formatted = user_date.strftime("%Y%m%d")
            st.session_state["card_metadata_card_creation_date"] = formatted
        elif required and user_date is not None:
            st.session_state["card_metadata_card_creation_date"] = None
            st.error("Creation date is required. Please select a valid date.")
        else:
            st.session_state["card_metadata_card_creation_date"] = None

    utils.section_divider()
    utils.title_header("Versioning")
    st.info(
        "Version number of the model card is set to 0.0 by default, change it to reflect the current version of the model card. You can introduce manually the number or use the up and down arrows to change it."
    )

    if all(k in section for k in ["version_number", "version_changes"]):
        col1, col2 = st.columns([1, 3])
        with col1:
            props = section["version_number"]
            create_helpicon(
                props.get("label", "Version Number"),
                props.get("description", ""),
                props.get("type", ""),
                props.get("example", ""),
                props.get("required", False),
            )
            utils.load_value("card_metadata_version_number", 0)
            k = "_card_metadata_version_number"
            v = st.session_state.get(k, 0)

            try:
                if isinstance(v, str):
                    v = v.strip()
                    if v == "":
                        flt = float(0.0)
                flt = float(v)
            except (TypeError, ValueError):
                flt = float(0.0)

            st.session_state[k] = flt
            st.number_input(
                label=".",
                min_value=0.0,
                max_value=10000000000.0,
                step=0.10,
                format="%.2f",
                key="_card_metadata_version_number",
                on_change=utils.store_value,
                args=["card_metadata_version_number"],
                label_visibility="hidden",
            )

        with col2:
            props = section["version_changes"]
            create_helpicon(
                props.get("label", "Version Changes"),
                props.get("description", ""),
                props.get("type", ""),
                props.get("example", ""),
                props.get("required", False),
            )
            utils.load_value("card_metadata_version_changes")
            st.text_input(
                label=".",
                key="_card_metadata_version_changes",
                on_change=utils.store_value,
                args=["card_metadata_version_changes"],
                label_visibility="hidden",
            )
    utils.section_divider()

    for key in section:
        if key not in ["card_creation_date", "version_number", "version_changes"]:
            render_field(key, section[key], "card_metadata")

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([9.4, 1])
    with col2:
        if st.button("Next"):
            from custom_pages.model_basic_information import (
                model_basic_information_render,
            )

            st.session_state.runpage = model_basic_information_render
            st.rerun()
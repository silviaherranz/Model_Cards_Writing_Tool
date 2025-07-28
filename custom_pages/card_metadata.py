from datetime import datetime

import streamlit as st
import utils
from render import create_helpicon, render_field


def card_metadata_render():
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

        # Ensure value is initialized once
        if "card_creation_date_widget" not in st.session_state:
            utils.load_value("card_creation_date_widget")

        st.date_input(
            "Click and select a date",
            min_value=datetime(1900, 1, 1),
            max_value=datetime.today(),
            key="_card_creation_date_widget",
            on_change=utils.store_value,
            args=["card_creation_date_widget"],
        )

        # Check if user actually interacted with the input
        user_date = st.session_state.get("_card_creation_date_widget")

        if user_date:
            formatted = user_date.strftime("%Y%m%d")
            st.session_state["card_metadata_creation_date"] = formatted
        elif required and user_date is not None:
            # Only show error if field exists but is empty (not on initial load)
            st.session_state["card_metadata_creation_date"] = None
            st.error("Creation date is required. Please select a valid date.")
        else:
            st.session_state["card_metadata_creation_date"] = None

    utils.title_header("Versioning")

    # Render version_number + version_changes in the same row using create_helpicon for labels
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
    # Render all other metadata fields except the three already handled
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

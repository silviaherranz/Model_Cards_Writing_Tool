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

    if "creation_date" in section:
        props = section["creation_date"]
        label = props.get("label", "Creation Date")
        description = props.get("description", "")
        example = props.get("example", "")
        required = props.get("required", False)
        type = props.get("type", "date")

        create_helpicon(label, description, type, example, required)
        utils.load_value("creation_date_widget", datetime.today())
        # Calendar input from 1900 to today
        date_value = st.date_input(
            "Select a date",
            min_value=datetime(1900, 1, 1),
            max_value=datetime.today(),
            key="_creation_date_widget",
            on_change=utils.store_value,
            args=["creation_date_widget"],
        )

        # Format date as YYYYMMDD (e.g., 20240102)
        formatted = date_value.strftime("%Y%m%d")

        # Store in session using your persistent key logic
        st.session_state["card_metadata_creation_date"] = formatted
    utils.section_divider()

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
        if key not in ["creation_date", "version_number", "version_changes"]:
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

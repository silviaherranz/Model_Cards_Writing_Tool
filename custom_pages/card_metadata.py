from datetime import datetime

import streamlit as st
import utils
from persist import persist
from render import (
    create_helpicon,
    render_field,
    title_header,
)

model_card_schema = utils.get_model_card_schema()


def card_metadata_render():
    from side_bar import sidebar_render
    sidebar_render()

    section = model_card_schema["card_metadata"]
    # Render creation_date
    # if "creation_date" in section:
    # render_field("creation_date", section["creation_date"], "card_metadata")
    if "creation_date" in section:
        props = section["creation_date"]
        label = props.get("label", "Creation Date")
        description = props.get("description", "")
        example = props.get("example", "")
        required = props.get("required", False)
        type = props.get("type", "date")

        create_helpicon(label, description, type, example, required)

        # Calendar input from 1900 to today
        date_value = st.date_input(
            "Select a date",
            min_value=datetime(1900, 1, 1),
            max_value=datetime.today(),
            key="creation_date_widget",
        )

        # Format date as YYYYMMDD (e.g., 20240102)
        formatted = date_value.strftime("%Y%m%d")

        # Store in session using your persistent key logic
        st.session_state[persist("card_metadata_creation_date")] = formatted

    title_header(
        "Versioning", size="1rem", bottom_margin="0.01em", top_margin="0.5em"
    )

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
            st.number_input(
                label=".",
                min_value=0.0,
                max_value=10000000000.0,
                step=0.10,
                format="%.2f",
                key=persist("card_metadata_version_number"),
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
            st.text_input(
                label=".",
                key=persist("card_metadata_version_changes"),
                label_visibility="hidden",
            )
    # Render all other metadata fields except the three already handled
    for key in section:
        if key not in ["creation_date", "version_number", "version_changes"]:
            render_field(key, section[key], "card_metadata")

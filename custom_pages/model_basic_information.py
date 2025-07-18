from datetime import datetime

import streamlit as st
import utils
from persist import persist
from render import (
    create_helpicon,
    render_field,
    title_header,
    section_divider,
)

model_card_schema = utils.get_model_card_schema()


def model_basic_information_render():
    from side_bar import sidebar_render
    sidebar_render()

    # filtered_fields = filter_fields_by_task(model_card_schema["model_basic_information"], task)
    # render_schema_section(filtered_fields, section_prefix="model_basic_information", current_task=task)
    section = model_card_schema["model_basic_information"]
    # Line 1: name + creation_date
    if "name" in section and "creation_date" in section:
        col1, col2 = st.columns(2)
        with col1:
            render_field("name", section["name"], "model_basic_information")
        with col2:
            props = section["creation_date"]
            label = props.get("label", "Creation Date")
            description = props.get("description", "")
            example = props.get("example", "")
            required = props.get("required", False)
            field_type = props.get("type", "date")

            create_helpicon(label, description, field_type, example, required)

            date_value = st.date_input(
                "Select a date",
                min_value=datetime(1900, 1, 1),
                max_value=datetime.today(),
                key="model_basic_information_creation_date_widget",
            )

            formatted = date_value.strftime("%Y%m%d")
            st.session_state[persist("model_basic_information_creation_date")] = (
                formatted
            )

    section_divider()
    title_header(
        "Versioning", size="1rem", bottom_margin="0.01em", top_margin="0.5em"
    )
    # Line 2: version_number + version_changes
    if "version_number" in section and "version_changes" in section:
        col1, col2 = st.columns([1, 3])
        with col1:
            section["version_number"]["placeholder"] = "MM.mm.bbbb"
            render_field(
                "version_number",
                section["version_number"],
                "model_basic_information",
            )
        with col2:
            render_field(
                "version_changes",
                section["version_changes"],
                "model_basic_information",
            )
    section_divider()
    # Line 3: doi
    if "doi" in section:
        render_field("doi", section["doi"], "model_basic_information")
    section_divider()
    title_header(
        "Model scope", size="1rem", bottom_margin="0.01em", top_margin="0.5em"
    )
    # Line 4: summary + anatomical_site
    if (
        "model_scope_summary" in section
        and "model_scope_anatomical_site" in section
    ):
        col1, col2 = st.columns([2, 1])
        with col1:
            render_field(
                "model_scope_summary",
                section["model_scope_summary"],
                "model_basic_information",
            )
        with col2:
            render_field(
                "model_scope_anatomical_site",
                section["model_scope_anatomical_site"],
                "model_basic_information",
            )
    section_divider()
    # Line 5: Clearance
    title_header(
        "Clearance", size="1rem", bottom_margin="0.01em", top_margin="0.5em"
    )
    # Render clearance_type
    if "clearance_type" in section:
        render_field(
            "clearance_type", section["clearance_type"], "model_basic_information"
        )
    # Grouped "Approved by"
    if all(
        k in section
        for k in [
            "clearance_approved_by_name",
            "clearance_approved_by_institution",
            "clearance_approved_by_contact_email",
        ]
    ):
        title_header("Approved by", size="1rem", bottom_margin="0.5em")
        col1, col2, col3 = st.columns([1, 1.5, 1.5])
        with col1:
            render_field(
                "clearance_approved_by_name",
                section["clearance_approved_by_name"],
                "model_basic_information",
            )
        with col2:
            render_field(
                "clearance_approved_by_institution",
                section["clearance_approved_by_institution"],
                "model_basic_information",
            )
        with col3:
            render_field(
                "clearance_approved_by_contact_email",
                section["clearance_approved_by_contact_email"],
                "model_basic_information",
            )

    # Render additional information
    if "clearance_additional_information" in section:
        render_field(
            "clearance_additional_information",
            section["clearance_additional_information"],
            "model_basic_information",
        )

    section_divider()

    render_field(
        "intended_users", section["intended_users"], "model_basic_information"
    )
    render_field(
        "observed_limitations",
        section["observed_limitations"],
        "model_basic_information",
    )
    render_field(
        "potential_limitations",
        section["potential_limitations"],
        "model_basic_information",
    )
    render_field(
        "type_of_learning_architecture",
        section["type_of_learning_architecture"],
        "model_basic_information",
    )

    section_divider()

    # Developer Information
    title_header("Developed by", size="1rem", bottom_margin="0.5em")
    col1, col2, col3 = st.columns([1, 1.5, 1.5])
    with col1:
        render_field(
            "developed_by_name",
            section["developed_by_name"],
            "model_basic_information",
        )
    with col2:
        render_field(
            "developed_by_institution",
            section["developed_by_institution"],
            "model_basic_information",
        )
    with col3:
        render_field(
            "developed_by_email",
            section["developed_by_email"],
            "model_basic_information",
        )

    section_divider()

    render_field(
        "conflict_of_interest",
        section["conflict_of_interest"],
        "model_basic_information",
    )

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        render_field(
            "software_license",
            section["software_license"],
            "model_basic_information",
        )
    with col2:
        render_field(
            "code_source", section["code_source"], "model_basic_information"
        )
    with col3:
        render_field(
            "model_source", section["model_source"], "model_basic_information"
        )

    col1, col2 = st.columns([1, 1])
    with col1:
        render_field(
            "citation_details",
            section["citation_details"],
            "model_basic_information",
        )
    with col2:
        render_field("url_info", section["url_info"], "model_basic_information")

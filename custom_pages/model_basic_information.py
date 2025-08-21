from datetime import datetime
import streamlit as st
import utils
from render import create_helpicon, render_field


def model_basic_information_render():
    utils.hide_streamlit_chrome()
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
    section = model_card_schema["model_basic_information"]
    utils.title("Model Basic Information")
    utils.subtitle("with the main information to use the model")

    if "name" in section and "creation_date" in section:
        col1, col2 = st.columns(2)
        with col1:
            render_field("name", section["name"], "model_basic_information")
        with col2:
            if "creation_date" in section:
                props = section["creation_date"]
                label = props.get("label", "Creation Date")
                description = props.get("description", "")
                example = props.get("example", "")
                required = props.get("required", False)
                field_type = props.get("type", "date")

                create_helpicon(label, description, field_type, example, required)

                if "model_basic_information_creation_date" not in st.session_state:
                    st.session_state["model_basic_information_creation_date"] = None

                st.date_input(
                    "Click and select a date",
                    value=st.session_state["model_basic_information_creation_date"],
                    min_value=datetime(1900, 1, 1),
                    max_value=datetime.today(),
                    key="_model_basic_information_creation_date",
                    on_change=utils.store_value,
                    args=["model_basic_information_creation_date"],
                )

                user_date = st.session_state.get(
                    "_model_basic_information_creation_date"
                )

                if user_date:
                    formatted = user_date.strftime("%Y%m%d")
                    st.session_state["model_basic_information_creation_date"] = (
                        formatted
                    )
                elif required and user_date is not None:
                    st.session_state["model_basic_information_creation_date"] = None
                    st.error("Creation date is required. Please select a valid date.")
                else:
                    st.session_state["model_basic_information_creation_date"] = None

    utils.section_divider()
    utils.title_header("Versioning")
    utils.light_header_italics(
        "Note that any change in an existing model is considered as a new version and thus a new model card associated with it should be filled in."
    )
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
    utils.section_divider()

    if "doi" in section:
        render_field("doi", section["doi"], "model_basic_information")
    utils.section_divider()
    utils.title_header("Model scope")

    if "model_scope_summary" in section and "model_scope_anatomical_site" in section:
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
    utils.section_divider()

    utils.title_header("Clearance")

    if "clearance_type" in section:
        render_field(
            "clearance_type", section["clearance_type"], "model_basic_information"
        )

    if all(
        k in section
        for k in [
            "clearance_approved_by_name",
            "clearance_approved_by_institution",
            "clearance_approved_by_contact_email",
        ]
    ):
        utils.title_header("Approved by", "1rem")
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

    if "clearance_additional_information" in section:
        render_field(
            "clearance_additional_information",
            section["clearance_additional_information"],
            "model_basic_information",
        )

    utils.section_divider()

    render_field("intended_users", section["intended_users"], "model_basic_information")
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

    utils.section_divider()

    utils.title_header("Developed by")
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

    utils.section_divider()

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
        render_field("code_source", section["code_source"], "model_basic_information")
    with col3:
        render_field("model_source", section["model_source"], "model_basic_information")

    col1, col2 = st.columns([1, 1])
    with col1:
        render_field(
            "citation_details",
            section["citation_details"],
            "model_basic_information",
        )
    with col2:
        render_field("url_info", section["url_info"], "model_basic_information")

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns([1.5, 2, 4.3, 2, 1.1])

    with col1:
        if st.button("Previous"):
            from custom_pages.card_metadata import card_metadata_render

            st.session_state.runpage = card_metadata_render
            st.rerun()

    with col5:
        if st.button("Next"):
            from custom_pages.technical_specifications import (
                technical_specifications_render,
            )

            st.session_state.runpage = technical_specifications_render
            st.rerun()

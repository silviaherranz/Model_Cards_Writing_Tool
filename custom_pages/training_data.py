import streamlit as st
import utils
from render import (
    render_field,
    title_header,
    titulo,
    subtitulo,
    section_divider,
)
import uuid


def training_data_render():
    from side_bar import sidebar_render

    sidebar_render()
    model_card_schema = utils.get_model_card_schema()
    section = model_card_schema["training_data_methodology_results_commisioning"]
    titulo("Training data, methodology, and information")
    subtitulo("containing all information about training and validation data (in case of a fine-tuned model, this section contains information about the tuning dataset)")
    title_header("Fine tuned form")
    col1, col2, col3 = st.columns([1, 1.5, 1.5])
    with col1:
        render_field(
            "model_name",
            section["model_name"],
            "model_basic_information",
        )
    with col2:
        render_field(
            "url_doi_to_model_card",
            section["url_doi_to_model_card"],
            "model_basic_information",
        )
    with col3:
        render_field(
            "tuning_technique",
            section["tuning_technique"],
            "model_basic_information",
        )

    section_divider()

    title_header("Training Dataset", size="1.2rem")
    title_header("1. General information")

    col1, col2, col3 = st.columns([0.8, 0.6, 1])
    with col1:
        render_field(
            "total_size",
            section["total_size"],
            "training_data",
        )
    with col2:
        render_field(
            "number_of_patients",
            section["number_of_patients"],
            "training_data",
        )
    with col3:
        render_field(
            "source",
            section["source"],
            "training_data",
        )

    col1, col2 = st.columns([1, 1])
    with col1:
        render_field(
            "acquisition_period",
            section["acquisition_period"],
            "training_data",
        )
    with col2:
        render_field(
            "inclusion_exclusion_criteria",
            section["inclusion_exclusion_criteria"],
            "training_data",
        )
    for field in [
        "type_of_data_argumentation",
        "strategy_for_data_argumentation",
        "url_info",
    ]:
        render_field(
            field,
            section[field],
            "training_data",
        )
    section_divider()
    title_header("2. Technical characteristics")
    utils.light_header_italics(
        "(i.e. image acquisition protocol, treatment details, …)"
    )

    import re

    tech_section_prefix = "training_data"
    section = model_card_schema["training_data_methodology_results_commisioning"]  # ✅ this was missing

    model_inputs = []
    model_outputs = []

    # ✅ Collect from all learning_architecture_X_input_content/output_content keys
    for key, value in st.session_state.items():
        if re.match(r"^learning_architecture_\d+_input_content$", key) and isinstance(value, list):
            model_inputs.extend(value)
        if re.match(r"^learning_architecture_\d+_output_content$", key) and isinstance(value, list):
            model_outputs.extend(value)

    # ✅ Deduplicate
    model_inputs = list(set(model_inputs))
    model_outputs = list(set(model_outputs))

    st.write("✅ Aggregated Inputs:", model_inputs)
    st.write("✅ Aggregated Outputs:", model_outputs)

    all_modalities = list(set(model_inputs + model_outputs))

    modality_fields = [
        "image_resolution",
        "patient_positioning",
        "scanner_model",
        "scan_acquisition_parameters",
        "scan_reconstruction_parameters",
        "fov",
    ]

    for modality in all_modalities:
        if not modality.strip():
            continue

        clean_modality = modality.strip().replace(" ", "_").lower()
        title_header(f"{modality} Details", size="1rem")

        for field in modality_fields:
            if field not in section:
                st.warning(f"Missing schema for field: {field}")
                continue

            unique_key = f"{tech_section_prefix}_{clean_modality}_{field}"
            field_schema = section[field].copy()

            utils.load_value(unique_key)
            st.text_input(
                label=field_schema.get("label", field),
                value=st.session_state.get("_" + unique_key, ""),
                key="_" + unique_key,
                on_change=utils.store_value,
                args=[unique_key],
                placeholder=field_schema.get("placeholder", ""),
                help=field_schema.get("description", ""),
            )

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns([1.5, 2, 4.3, 2, 1.1])
    with col1:
        if st.button("Previous"):
            from custom_pages.technical_specifications import (
                technical_specifications_render,
            )

            st.session_state.runpage = technical_specifications_render
            st.rerun()
    with col5:
        if st.button("Next"):
            from custom_pages.evaluation_data_mrc import evaluation_data_mrc_render

            st.session_state.runpage = evaluation_data_mrc_render
            st.rerun()

    # st.markdown("---")
    # st.subheader("🔍 Debug: Session State")
    # st.json(st.session_state)
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = str(uuid.uuid4())
    # st.write("🔁 Session ID:", st.session_state["session_id"])

    model_inputs = st.session_state.get("technical_specifications_input_content") or []
    model_outputs = st.session_state.get("technical_specifications_output_content") or []

    st.write("✅ Inputs:", model_inputs)
    st.write("✅ Outputs:", model_outputs)
    for modality in all_modalities:
        st.write("🔄 Rendering fields for:", modality)


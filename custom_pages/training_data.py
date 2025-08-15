import streamlit as st
import utils
from render import render_field, render_image_field, should_render


def training_data_render():
    utils.require_task()

    from side_bar import sidebar_render

    sidebar_render()
    model_card_schema = utils.get_model_card_schema()
    section = model_card_schema["training_data_methodology_results_commisioning"]
    utils.title("Training data, methodology, and information")
    utils.subtitle(
        "containing all information about training and validation data (in case of a fine-tuned model, this section contains information about the tuning dataset)"
    )
    utils.title_header("Fine tuned from")
    utils.light_header_italics(
        "These fields are only relevant for fine-tuned models. For tuned models, the training data will contain the tuning data information. Indicate NA if not applicable."
    )
    col1, col2, col3 = st.columns([1, 1.5, 1.5])
    with col1:
        render_field(
            "model_name",
            section["model_name"],
            "training_data",
        )
    with col2:
        render_field(
            "url_doi_to_model_card",
            section["url_doi_to_model_card"],
            "training_data",
        )
    with col3:
        render_field(
            "tuning_technique",
            section["tuning_technique"],
            "training_data",
        )

    utils.section_divider()

    utils.title_header("Training Dataset", size="1.2rem")
    utils.light_header_italics(
        "Note that all fields refer to the raw training data used in 'Model inputs' (i.e. before pre-processing steps)."
    )
    utils.title_header("1. General information")

    col1, col2 = st.columns([1, 1])
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
        "type_of_data_augmentation",
        "strategy_for_data_augmentation",
        "url_info",
    ]:
        render_field(
            field,
            section[field],
            "training_data",
        )
    utils.section_divider()
    utils.title_header("2. Technical characteristics")
    utils.light_header_italics(
        "(i.e. image acquisition protocol, treatment details, …)"
    )

    tech_section_prefix = "training_data"
    section = model_card_schema["training_data_methodology_results_commisioning"]

    modality_entries = []

    for key, value in st.session_state.items():
        if key.endswith("model_inputs") and isinstance(value, list):
            for item in value:
                modality_entries.append({"modality": item, "source": "model_inputs"})

        elif key.endswith("model_outputs") and isinstance(value, list):
            for item in value:
                modality_entries.append({"modality": item, "source": "model_outputs"})

    if not modality_entries:
        st.warning(
            "Start by adding model inputs and outputs in the previous section to enable technical details."
        )
    else:
        tabs = st.tabs([utils.strip_brackets(m["modality"]) for m in modality_entries])

        for idx, entry in enumerate(modality_entries):
            modality = entry["modality"]
            source = entry["source"]

            with tabs[idx]:
                clean_modality = modality.strip().replace(" ", "_").lower()
                utils.title_header(
                    f"{utils.strip_brackets(modality)} — {source.replace('_', ' ').capitalize()}",
                    size="1rem",
                )

                field_keys = {
                    "image_resolution": section["image_resolution"],
                    "patient_positioning": section["patient_positioning"],
                    "scanner_model": section["scanner_model"],
                    "scan_acquisition_parameters": section[
                        "scan_acquisition_parameters"
                    ],
                    "scan_reconstruction_parameters": section[
                        "scan_reconstruction_parameters"
                    ],
                    "fov": section["fov"],
                }

                for f in field_keys.values():
                    f["placeholder"] = f.get("placeholder", "NA if Not Applicable")

                # Render form fields
                col1, col2 = st.columns([1, 1])
                with col1:
                    render_field(
                        f"{tech_section_prefix}_{clean_modality}_{source}_image_resolution",
                        field_keys["image_resolution"],
                        "",
                    )
                with col2:
                    render_field(
                        f"{tech_section_prefix}_{clean_modality}_{source}_patient_positioning",
                        field_keys["patient_positioning"],
                        "",
                    )

                render_field(
                    f"{tech_section_prefix}_{clean_modality}_{source}_scanner_model",
                    field_keys["scanner_model"],
                    "",
                )

                col1, col2 = st.columns([1, 1])
                with col1:
                    render_field(
                        f"{tech_section_prefix}_{clean_modality}_{source}_scan_acquisition_parameters",
                        field_keys["scan_acquisition_parameters"],
                        "",
                    )
                with col2:
                    render_field(
                        f"{tech_section_prefix}_{clean_modality}_{source}_scan_reconstruction_parameters",
                        field_keys["scan_reconstruction_parameters"],
                        "",
                    )

                render_field(
                    f"{tech_section_prefix}_{clean_modality}_{source}_fov",
                    field_keys["fov"],
                    "",
                )

    model_card_schema = utils.get_model_card_schema()
    section = model_card_schema["training_data_methodology_results_commisioning"]
    task = st.session_state.get("task").strip().lower()

    if should_render(section["treatment_modality_train"], task):
        render_field(
            "treatment_modality_train",
            section["treatment_modality_train"],
            "training_data",
        )

    col1, col2 = st.columns([2, 1.1])
    with col1:
        if should_render(section["beam_configuration_energy"], task):
            render_field(
                "beam_configuration_energy",
                section["beam_configuration_energy"],
                "training_data",
            )
    with col2:
        if should_render(section["dose_engine"], task):
            render_field("dose_engine", section["dose_engine"], "training_data")
    col1, col2 = st.columns([2, 1.1])
    with col1:
        if should_render(section["target_volumes_and_prescription"], task):
            render_field(
                "target_volumes_and_prescription",
                section["target_volumes_and_prescription"],
                "training_data",
            )
    with col2:
        if should_render(section["number_of_fractions"], task):
            render_field(
                "number_of_fractions", section["number_of_fractions"], "training_data"
            )

    utils.section_divider()
    for field in [
        "reference_standard",
        "reference_standard_qa",
        "reference_standard_qa_additional_information",
    ]:
        render_field(
            field,
            section[field],
            "training_data",
        )

    utils.section_divider()
    utils.title_header("3. Patient demographics and clinical characteristics")
    col1, col2 = st.columns([1, 1])
    with col1:
        render_field("icd10_11", section["icd10_11"], "training_data")
    with col2:
        render_field("tnm_staging", section["tnm_staging"], "training_data")

    col1, col2 = st.columns([1, 1])
    with col1:
        render_field("age", section["age"], "training_data")
    with col2:
        render_field("sex", section["sex"], "training_data")
    col1, col2 = st.columns([2.5, 1])
    with col1:
        render_field("target_volume_cm3", section["target_volume_cm3"], "training_data")
    with col2:
        render_field("bmi", section["bmi"], "training_data")
    render_field(
        "additional_patient_info",
        section["additional_patient_info"],
        "training_data",
    )
    col1, col2, col3 = st.columns([1.7, 1.2, 1])
    with col1:
        render_field(
            "validation_strategy", section["validation_strategy"], "training_data"
        )
    with col2:
        render_field(
            "validation_data_partition",
            section["validation_data_partition"],
            "training_data",
        )
    with col3:
        render_field(
            "weights_initialization", section["weights_initialization"], "training_data"
        )
    col1, col2, col3 = st.columns([2, 1.1, 1])
    with col1:
        render_field("epochs", section["epochs"], "training_data")
    with col2:
        render_field("optimiser", section["optimiser"], "training_data")
    with col3:
        render_field("learning_rate", section["learning_rate"], "training_data")

    render_image_field("train_and_validation_loss_curves", section["train_and_validation_loss_curves"], "training_data")

    for field in [
        "model_choice_criteria",
        "inference_method",
    ]:
        render_field(
            field,
            section[field],
            "training_data",
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

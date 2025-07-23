import streamlit as st
from datetime import datetime
import utils
from render import (
    create_helpicon,
    render_field,
    render_fields,
    has_renderable_fields,
)


def render_evaluation_section(schema_section, section_prefix, current_task):
    utils.require_task()

    if "evaluation_date" in schema_section:
        props = schema_section["evaluation_date"]
        label = props.get("label", "Evaluation Date")
        description = props.get("description", "")
        example = props.get("example", "")
        required = props.get("required", False)
        field_type = props.get("type", "date")

        create_helpicon(label, description, field_type, example, required)

        date_key = f"{section_prefix}_evaluation_date_widget"
        value = st.date_input(
            label="Select a date",
            min_value=datetime(1900, 1, 1),
            max_value=datetime.today(),
            key=date_key,
        )

        formatted = value.strftime("%Y%m%d")
        st.session_state[f"{section_prefix}_evaluation_date"] = formatted

    utils.section_divider()

    utils.title_header("Evaluated by")
    same_key = f"{section_prefix}_evaluated_same_as_approved"
    same = st.checkbox("Same as 'Approved by'", key=same_key)

    if not same:
        if all(
            k in schema_section
            for k in [
                "evaluated_by_name",
                "evaluated_by_institution",
                "evaluated_by_contact_email",
            ]
        ):
            col1, col2, col3 = st.columns([1, 1.5, 1.5])  # puedes ajustar proporciones
            with col1:
                render_field(
                    "evaluated_by_name",
                    schema_section["evaluated_by_name"],
                    section_prefix,
                )
            with col2:
                render_field(
                    "evaluated_by_institution",
                    schema_section["evaluated_by_institution"],
                    section_prefix,
                )
            with col3:
                render_field(
                    "evaluated_by_contact_email",
                    schema_section["evaluated_by_contact_email"],
                    section_prefix,
                )

    else:
        st.info("Evaluation team is the same as the approval team. Fields auto-filled.")
    utils.section_divider()

    render_fields(
        ["evaluation_frame", "sanity_check"],
        schema_section,
        section_prefix,
        current_task,
    )
    utils.section_divider()

    utils.title_header("Evaluation Dataset")

    utils.title_header("1. General Information", size="1rem")
    render_fields(
        [
            "total_size",
            "number_of_patients",
            "source",
            "acquisition_period",
            "inclusion_exclusion_criteria",
            "url_info",
        ],
        schema_section,
        section_prefix,
        current_task,
    )
    utils.section_divider()
    utils.title_header("Technical Characteristics", size="1rem")
    render_fields(
        [
            "image_resolution",
            "patient_positioning",
            "scanner_model",
            "scan_acquisition_parameters",
            "scan_reconstruction_parameters",
            "fov",
            "treatment_modality",
            "beam_configuration_energy",
            "dose_engine",
            "target_volumes_and_prescription",
            "number_of_fractions",
            "reference_standard",
            "reference_standard_qa",
            "reference_standard_qa_additional_information",
        ],
        schema_section,
        section_prefix,
        current_task,
    )
    utils.section_divider()

    utils.title_header("Patient Demographics and Clinical Characteristics", size="1rem")
    render_fields(
        [
            "icd10_11",
            "tnm_staging",
            "age_ev",
            "sex_ev",
            "target_volume_cm3",
            "bmi",
            "additional_patient_info",
        ],
        schema_section,
        section_prefix,
        current_task,
    )
    utils.section_divider()
    utils.title_header("Quantitative Evaluation")

    # Image similarity metrics
    ism_fields = [
        "type_ism",
        "on_volume_ism",
        "registration_ism",
        "sample_data_ism",
        "mean_data_ism",
        "figure_ism",
    ]
    if has_renderable_fields(ism_fields, schema_section, current_task):
        utils.title_header("Image similarity metrics", size="1rem")
        render_fields(ism_fields, schema_section, section_prefix, current_task)

    # Dose metrics - Image-to-Image
    dose_dm_fields = [
        "type_dose_dm",
        "metric_specifications_dm",
        "on_volume_dm",
        "registration_dm",
        "treatment_modality_dm",
        "dose_engine_dm",
        "dose_grid_resolution_dm",
        "tps_vendor_dm",
        "sample_data_dm",
        "mean_data_dm",
        "figure_dm",
    ]
    if has_renderable_fields(dose_dm_fields, schema_section, current_task):
        utils.title_header("Dose metrics", size="1rem")
        render_fields(dose_dm_fields, schema_section, section_prefix, current_task)

    # Dose metrics - Segmentation
    dose_seg_fields = [
        "type_dose_seg",
        "metric_specifications_seg",
        "on_volume_seg",
        "treatment_modality_seg",
        "dose_engine_seg",
        "dose_grid_resolution_seg",
        "tps_vendor_seg",
        "sample_data_seg",
        "mean_data_seg",
        "figure_seg",
    ]
    if has_renderable_fields(dose_seg_fields, schema_section, current_task):
        utils.title_header("Geometric metrics", size="1rem")
        utils.title_header("Dose metrics", size="1rem")
        render_fields(dose_seg_fields, schema_section, section_prefix, current_task)
    utils.title_header("Other", size="1rem")

    utils.title_header("Qualitative Evaluation")


def evaluation_data_mrc_render():
    from side_bar import sidebar_render

    sidebar_render()
    model_card_schema = utils.get_model_card_schema()
    utils.title("Evaluation data, methodology, and results / commissioning")
    utils.subtitle(
        "containing all info about the evaluation data and procedure. Because it is common to evaluate your model on a different dataset, this section can be repeated as many times as needed. We refer to evaluation results for models that are evaluated but not necessarily with a clinical implementation in mind, and commissioning for models that are specifically evaluated within a clinical environment with clinic-specific data."
    )

    task = st.session_state.get("task", "Image-to-Image translation")

    if "evaluation_forms" not in st.session_state:
        existing_keys = [
            k for k in st.session_state.keys() if k.startswith("evaluation_")
        ]
        if existing_keys:
            indices = set(
                k.split("_")[1] for k in existing_keys if k.split("_")[1].isdigit()
            )
            st.session_state.evaluation_forms = [{} for _ in indices]
        else:
            st.session_state.evaluation_forms = [{}]

    # utils.light_header("Evaluation Data Methodology, Results & Commissioning")
    # utils.light_header_italics(
    #     "To be repeated as many times as evaluations sets used", bottom_margin="1em"
    # )

    to_delete = None
    for i, eval_data in enumerate(st.session_state.evaluation_forms):
        with st.expander(f"Evaluation {i + 1}", expanded=False):
            render_evaluation_section(
                model_card_schema["evaluation_data_methodology_results_commisioning"],
                section_prefix=f"evaluation_{i}",
                current_task=task,
            )
            col1, col2 = st.columns([0.2, 0.8])
            with col1:
                if st.button("🗑️ Delete", key=f"delete_eval_{i}"):
                    to_delete = i

    if to_delete is not None:
        del st.session_state.evaluation_forms[to_delete]
        for key in list(st.session_state.keys()):
            if key.startswith(f"evaluation_{to_delete}_"):
                del st.session_state[key]
        st.rerun()

    if st.button("➕ Add Another Evaluation"):
        st.session_state.evaluation_forms.append({})
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns([1.5, 2, 4.3, 2, 1.1])

    with col1:
        if st.button("Previous"):
            from custom_pages.training_data import training_data_render

            st.session_state.runpage = training_data_render
            st.rerun()

    with col5:
        if st.button("Next"):
            from custom_pages.other_considerations import other_considerations_render

            st.session_state.runpage = other_considerations_render
            st.rerun()

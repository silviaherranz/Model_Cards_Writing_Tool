import streamlit as st
from datetime import datetime
import utils
import html
from render import (
    create_helpicon,
    render_field,
    render_fields,
    has_renderable_fields,
    should_render,
)


def render_evaluation_section(schema_section, section_prefix, current_task):
    utils.require_task()
    # model_card_schema = utils.get_model_card_schema()
    # section = model_card_schema["evaluation_data_methodology_results_commisioning"]

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
    utils.load_value(same_key, 0)
    same = st.checkbox(
        "Same as 'Approved by'",
        key="_" + same_key,
        on_change=utils.store_value,
        args=[same_key],
    )

    if not same:
        if all(
            k in schema_section
            for k in [
                "evaluated_by_name",
                "evaluated_by_institution",
                "evaluated_by_contact_email",
            ]
        ):
            col1, col2, col3 = st.columns([1, 1.5, 1.5])
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

    utils.title_header("Evaluation Dataset", size="1.2rem")
    utils.title_header("1. General information")

    col1, col2 = st.columns([1, 1])
    with col1:
        render_field(
            "total_size",
            schema_section["total_size"],
            section_prefix,
        )
    with col2:
        render_field(
            "number_of_patients", schema_section["number_of_patients"], section_prefix
        )
    render_field("source", schema_section["source"], section_prefix)

    col1, col2 = st.columns([1, 1])
    with col1:
        render_field(
            "acquisition_period", schema_section["acquisition_period"], section_prefix
        )
    with col2:
        render_field(
            "inclusion_exclusion_criteria",
            schema_section["inclusion_exclusion_criteria"],
            section_prefix,
        )
    render_field("url_info", schema_section["url_info"], section_prefix)
    utils.section_divider()
    utils.title_header("2. Technical characteristics")
    utils.light_header_italics(
        "(i.e. image acquisition protocol, treatment details, …)"
    )
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

    # # Image similarity metrics
    # ism_fields = [
    #     "type_ism",
    #     "on_volume_ism",
    #     "registration_ism",
    #     "sample_data_ism",
    #     "mean_data_ism",
    #     "figure_ism",
    # ]
    # if has_renderable_fields(ism_fields, schema_section, current_task):
    #     utils.title_header("Image similarity metrics", size="1rem")
    #     render_fields(ism_fields, schema_section, section_prefix, current_task)

    # Main ISM field list
    ism_fields = [
        "on_volume_ism",
        "registration_ism",
        "sample_data_ism",
        "mean_data_ism",
        "figure_ism",
    ]

    # --- STEP 1: TYPE_ISM multi-select logic ---
    type_ism_key = f"{section_prefix}_type_ism"
    type_ism_list_key = f"{type_ism_key}_list"
    type_ism_select_key = f"{type_ism_key}_selected"

    # Session state setup
    utils.load_value(type_ism_list_key, default=[])
    utils.load_value(type_ism_select_key)

    type_options = schema_section.get("type_ism", {}).get("options", [])

    utils.title_header("Image Similarity Types", size="1rem")
    col1, col2 = st.columns([4, 0.5])

    with col1:
        st.selectbox(
            "Select image similarity type",
            options=type_options,
            key="_" + type_ism_select_key,
            on_change=utils.store_value,
            args=[type_ism_select_key],
            placeholder="-Select an option-",
        )

    with col2:
        st.markdown("<div style='margin-top: 26px;'>", unsafe_allow_html=True)
        if st.button("➕", key=f"{type_ism_key}_add_button"):
            entry = st.session_state.get(type_ism_select_key, "")
            if entry and entry not in st.session_state[type_ism_list_key]:
                st.session_state[type_ism_list_key].append(entry)
                st.session_state[type_ism_key] = st.session_state[type_ism_list_key]
        st.markdown("</div>", unsafe_allow_html=True)

    # Show selections
    entries = st.session_state[type_ism_list_key]
    if entries:
        col1, col2 = st.columns([5, 1])
        with col1:
            tooltip_items = [
                f"<span title='{html.escape(item)}' style='margin-right: 6px; font-weight: 500; color: #333;'>{html.escape(item)}</span>"
                for item in entries
            ]
            st.markdown(
                f"**Selected Types:** {', '.join(tooltip_items)}",
                unsafe_allow_html=True,
            )
        with col2:
            if st.button("🧹 Clear", key=f"{type_ism_key}_clear_all"):
                st.session_state[type_ism_list_key] = []
                st.session_state[type_ism_key] = []
                st.rerun()

    # --- STEP 2: Per-Type Tabs with Remaining Fields ---
    if entries and has_renderable_fields(ism_fields, schema_section, current_task):
        utils.title_header("Image Similarity Metrics Details", size="1rem")
        tabs = st.tabs(entries)

        for tab, type_name in zip(tabs, entries):
            with tab:
                sub_prefix = f"{section_prefix}.{type_name}"
                task = st.session_state.get("task").strip().lower()
                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    if should_render(schema_section["on_volume_ism"], task):
                        render_field(
                            "on_volume_ism",
                            schema_section["on_volume_ism"],
                            sub_prefix,
                        )
                with col2:
                    if should_render(schema_section["registration_ism"], task):
                        render_field(
                            "registration_ism",
                            schema_section["registration_ism"],
                            sub_prefix,
                        )
                with col3:
                    if should_render(schema_section["sample_data_ism"], task):
                        render_field(
                            "sample_data_ism",
                            schema_section["sample_data_ism"],
                            sub_prefix,
                        )

                if should_render(schema_section["mean_data_ism"], task):
                    render_field(
                        "mean_data_ism",
                        schema_section["mean_data_ism"],
                        sub_prefix,
                    )

                if should_render(schema_section["figure_ism"], task):
                    render_field(
                        "figure_ism", schema_section["figure_ism"], sub_prefix
                    )
                utils.section_divider()

    # # Dose metrics - Image-to-Image
    # dose_dm_fields = [
    #     "type_dose_dm",
    #     "metric_specifications_dm",
    #     "on_volume_dm",
    #     "registration_dm",
    #     "treatment_modality_dm",
    #     "dose_engine_dm",
    #     "dose_grid_resolution_dm",
    #     "tps_vendor_dm",
    #     "sample_data_dm",
    #     "mean_data_dm",
    #     "figure_dm",
    # ]
    # if has_renderable_fields(dose_dm_fields, schema_section, current_task):
    #     utils.title_header("Dose metrics", size="1rem")
    #     render_fields(dose_dm_fields, schema_section, section_prefix, current_task)
    dm_base_fields = [
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

    # --- STEP 1: DM Type Selection Interface ---

    dm_key = f"{section_prefix}_dose_metrics"
    dm_list_key = f"{dm_key}_list"
    dm_select_key = f"{dm_key}_selected"
    dm_dynamic_prefix_key = f"{dm_key}_dyn"

    # Initialize state
    utils.load_value(dm_list_key, default=[])
    utils.load_value(dm_select_key, default="GPR")
    utils.load_value(dm_dynamic_prefix_key, default={"prefix": "D", "value": 95})

    static_dm_options = ["GPR", "MAE", "MSE"]
    parametric_dm_prefixes = ["D", "V"]

    utils.title_header("Dose Metrics", size="1rem")
    col1, col2, col3, col4 = st.columns([2, 1.5, 2, 1])

    with col1:
        st.selectbox(
            "Metric type",
            static_dm_options + parametric_dm_prefixes,
            key="_" + dm_select_key,
            on_change=utils.store_value,
            args=[dm_select_key],
        )
        dm_type = st.session_state.get(dm_select_key)

    with col2:
        if dm_type in parametric_dm_prefixes:
            value_key = f"{dm_dynamic_prefix_key}_{dm_type}_value"

            # Initialize if missing
            if value_key not in st.session_state:
                st.session_state[value_key] = st.session_state[dm_dynamic_prefix_key].get("value", 95)

            val = st.number_input(
                f"{dm_type} value (0–100)",
                min_value=0,
                max_value=100,
                value=st.session_state[value_key],
                key=value_key,
            )

            st.session_state[dm_dynamic_prefix_key]["value"] = val
            st.session_state[dm_dynamic_prefix_key]["prefix"] = dm_type
        else:
            val = None


    with col3:
        if st.button("➕ Add Metric", key=f"{dm_key}_add_button"):
            if dm_type in static_dm_options:
                metric = dm_type
            else:
                num = st.session_state[dm_dynamic_prefix_key]["value"]
                prefix = st.session_state[dm_dynamic_prefix_key]["prefix"]
                metric = f"{prefix}{num}"

            if metric not in st.session_state[dm_list_key]:
                st.session_state[dm_list_key].append(metric)
                st.session_state[dm_key] = st.session_state[dm_list_key]

    with col4:
        if st.button("🧹 Clear All", key=f"{dm_key}_clear_all"):
            st.session_state[dm_list_key] = []
            st.session_state[dm_key] = []
            st.rerun()

    # --- STEP 2: Tabbed Rendering per Dose Metric ---

    dm_entries = st.session_state.get(dm_list_key, [])

    if dm_entries and has_renderable_fields(
        dm_base_fields, schema_section, current_task
    ):
        utils.title_header("Dose Metric Specifications", size="1rem")
        tabs = st.tabs(dm_entries)

        for tab, dm_name in zip(tabs, dm_entries):
            with tab:
                sub_prefix = f"{section_prefix}.{dm_name}"
                render_fields(dm_base_fields, schema_section, sub_prefix, current_task)

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

import streamlit as st
from datetime import datetime
import utils
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

        # Ensure value is initialized once
        if "evaluation_date_widget" not in st.session_state:
            utils.load_value("evaluation_date_widget")

        st.date_input(
            "Select a date",
            min_value=datetime(1900, 1, 1),
            max_value=datetime.today(),
            key="_evaluation_date_widget",
            on_change=utils.store_value,
            args=["evaluation_date_widget"],
        )

        # Check if user actually interacted with the input
        user_date = st.session_state.get("_evaluation_date_widget")

        if user_date:
            formatted = user_date.strftime("%Y%m%d")
            st.session_state["evaluation_creation_date"] = formatted
        elif required and user_date is not None:
            # Only show error if field exists but is empty (not on initial load)
            st.session_state["evaluation_creation_date"] = None
            st.error("Date of evaluation is required. Please select a valid date.")
        else:
            st.session_state["evaluation_creation_date"] = None

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

    col1, col2 = st.columns([1, 1])
    with col1:
        render_field(
            "image_resolution", schema_section["image_resolution"], section_prefix
        )
    with col2:
        render_field(
            "patient_positioning", schema_section["patient_positioning"], section_prefix
        )
    render_fields(
        [
            "scanner_model",
            "scan_acquisition_parameters",
            "scan_reconstruction_parameters",
            "fov",
        ],
        schema_section,
        section_prefix,
        current_task,
    )
    ####################################
    # EXCLUSIVE TO DOSE PREDICTION TASK
    ####################################
    task = st.session_state.get("task").strip().lower()
    if should_render(schema_section["treatment_modality"], task):
        render_field(
            "treatment_modality", schema_section["treatment_modality"], section_prefix
        )
    col1, col2 = st.columns([1, 1])
    with col1:
        if should_render(schema_section["beam_configuration_energy"], task):
            render_field(
                "beam_configuration_energy",
                schema_section["beam_configuration_energy"],
                section_prefix,
            )
    with col2:
        if should_render(schema_section["dose_engine"], task):
            render_field(
                "dose_engine",
                schema_section["dose_engine"],
                section_prefix,
            )
    col1, col2 = st.columns([1, 1])
    with col1:
        if should_render(schema_section["target_volumes_and_prescription"], task):
            render_field(
                "target_volumes_and_prescription",
                schema_section["target_volumes_and_prescription"],
                section_prefix,
            )
    with col2:
        if should_render(schema_section["number_of_fractions"], task):
            render_field(
                "number_of_fractions",
                schema_section["number_of_fractions"],
                section_prefix,
            )
    ########################################
    # END EXCLUSIVE TO DOSE PREDICTION TASK
    ########################################
    render_fields(
        [
            "reference_standard",
            "reference_standard_qa",
            "reference_standard_qa_additional_information",
        ],
        schema_section,
        section_prefix,
        current_task,
    )

    utils.section_divider()

    utils.title_header("3. Patient Demographics and Clinical Characteristics")
    col1, col2 = st.columns([1, 1])
    with col1:
        render_field(
            "icd10_11_ev",
            schema_section["icd10_11_ev"],
            section_prefix,
        )
    with col2:
        render_field(
            "tnm_staging_ev",
            schema_section["tnm_staging_ev"],
            section_prefix,
        )
    col1, col2 = st.columns([1, 1])
    with col1:
        render_field(
            "age_ev",
            schema_section["age_ev"],
            section_prefix,
        )
    with col2:
        render_field(
            "sex_ev",
            schema_section["sex_ev"],
            section_prefix,
        )
    col1, col2 = st.columns([1, 1])
    with col1:
        render_field(
            "target_volume_cm3_ev",
            schema_section["target_volume_cm3_ev"],
            section_prefix,
        )
    with col2:
        render_field(
            "bmi_ev",
            schema_section["bmi_ev"],
            section_prefix,
        )
    render_field(
        "additional_patient_info_ev",
        schema_section["additional_patient_info_ev"],
        section_prefix,
    )
    # utils.section_divider()
    # utils.title_header("Quantitative Evaluation")
    quant_qual_tabs = st.tabs(["Quantitative Evaluation", "Qualitative Evaluation"])

    with quant_qual_tabs[0]:
        utils.section_divider()
        utils.title_header("Quantitative Evaluation")

        ism_fields = [
            "on_volume_ism",
            "registration_ism",
            "sample_data_ism",
            "mean_data_ism",
            "figure_ism",
        ]

        task = st.session_state.get("task").strip().lower()
        if should_render(schema_section["type_ism"], task):
            utils.title_header("Image Similarity Metrics")
            render_field(
                "type_ism",
                schema_section["type_ism"],
                section_prefix,
            )

        ism_entries = st.session_state.get(f"{section_prefix}_type_ism_list", [])
        if ism_entries and has_renderable_fields(
            ism_fields, schema_section, current_task
        ):
            tabs = st.tabs(ism_entries)

            for tab, type_name in zip(tabs, ism_entries):
                with tab:
                    sub_prefix = f"{section_prefix}.{type_name}"
                    task = st.session_state.get("task").strip().lower()
                    col1, col2 = st.columns([1, 1])
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

        task = st.session_state.get("task").strip().lower()
        if should_render(schema_section["type_dose_dm"], task):
            utils.title_header("Dose Metrics")
            render_field(
                "type_dose_dm",
                schema_section["type_dose_dm"],
                section_prefix,
            )

        dm_entries = st.session_state.get(f"{section_prefix}_type_dose_dm_list", [])

        if dm_entries and has_renderable_fields(
            dm_base_fields, schema_section, current_task
        ):
            utils.title_header("Dose Metric Specifications", size="1rem")
            tabs = st.tabs([str(entry) for entry in dm_entries if entry])
            for tab, dm_name in zip(tabs, dm_entries):
                with tab:
                    sub_prefix = f"{section_prefix}.{dm_name}"
                    task = st.session_state.get("task").strip().lower()
                    if should_render(schema_section["metric_specifications_dm"], task):
                        render_field(
                            "metric_specifications_dm",
                            schema_section["metric_specifications_dm"],
                            sub_prefix,
                        )
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if should_render(schema_section["on_volume_dm"], task):
                            render_field(
                                "on_volume_dm",
                                schema_section["on_volume_dm"],
                                sub_prefix,
                            )
                    with col2:
                        if should_render(schema_section["registration_dm"], task):
                            render_field(
                                "registration_dm",
                                schema_section["registration_dm"],
                                sub_prefix,
                            )
                    if should_render(schema_section["treatment_modality_dm"], task):
                        render_field(
                            "treatment_modality_dm",
                            schema_section["treatment_modality_dm"],
                            sub_prefix,
                        )
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col1:
                        if should_render(schema_section["dose_engine_dm"], task):
                            render_field(
                                "dose_engine_dm",
                                schema_section["dose_engine_dm"],
                                sub_prefix,
                            )
                    with col2:
                        if should_render(
                            schema_section["dose_grid_resolution_dm"], task
                        ):
                            render_field(
                                "dose_grid_resolution_dm",
                                schema_section["dose_grid_resolution_dm"],
                                sub_prefix,
                            )
                    with col3:
                        if should_render(schema_section["tps_vendor_dm"], task):
                            render_field(
                                "tps_vendor_dm",
                                schema_section["tps_vendor_dm"],
                                sub_prefix,
                            )

                    if should_render(schema_section["sample_data_dm"], task):
                        render_field(
                            "sample_data_dm",
                            schema_section["sample_data_dm"],
                            sub_prefix,
                        )

                    if should_render(schema_section["mean_data_dm"], task):
                        render_field(
                            "mean_data_dm",
                            schema_section["mean_data_dm"],
                            sub_prefix,
                        )

                    if should_render(schema_section["figure_dm"], task):
                        render_field(
                            "figure_dm", schema_section["figure_dm"], sub_prefix
                        )

                    utils.section_divider()

        ##################################################
        # END EXCLUSIVE TO IMAGE-TO-IMAGE TRANSLATION TASK
        ##################################################

        #################################
        # EXCLUSIVE TO SEGMENTATION TASK
        #################################
        task = st.session_state.get("task").strip().lower()

        if should_render(schema_section["type_gm_seg"], task):
            utils.title_header("Geometric Metrics")
            render_field(
                "type_gm_seg",
                schema_section["type_gm_seg"],
                section_prefix,
            )

        dose_seg_fields = [
            "metric_specifications_gm_seg",
            "on_volume_gm_seg",
            "sample_data_gm_seg",
            "mean_data_gm_seg",
            "figure_gm_seg",
        ]

        seg_entries = st.session_state.get(f"{section_prefix}_type_gm_seg_list", [])

        if seg_entries and has_renderable_fields(dose_seg_fields, schema_section, task):
            utils.title_header("Geometric Metric Specifications")
            tabs = st.tabs([str(entry) for entry in seg_entries if entry])

            for tab, seg_name in zip(tabs, seg_entries):
                with tab:
                    sub_prefix = f"{section_prefix}.{seg_name}"

                    # First row: two fields side by side
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        render_field(
                            "metric_specifications_gm_seg",
                            schema_section["metric_specifications_gm_seg"],
                            sub_prefix,
                        )
                    with col2:
                        render_field(
                            "on_volume_gm_seg",
                            schema_section["on_volume_gm_seg"],
                            sub_prefix,
                        )

                    # Other fields on separate lines
                    render_field(
                        "sample_data_gm_seg",
                        schema_section["sample_data_gm_seg"],
                        sub_prefix,
                    )
                    render_field(
                        "mean_data_gm_seg",
                        schema_section["mean_data_gm_seg"],
                        sub_prefix,
                    )
                    render_field(
                        "figure_gm_seg", schema_section["figure_gm_seg"], sub_prefix
                    )

        utils.section_divider()

        dose_dm_seg_fields = [
            "metric_specifications_dm_seg",
            "on_volume_dm_seg",
            "treatment_modality_dm_seg",
            "dose_engine_dm_seg",
            "dose_grid_resolution_dm_seg",
            "tps_vendor_dm_seg",
            "sample_data_dm_seg",
            "mean_data_dm_seg",
            "figure_dm_seg",
        ]

        task = st.session_state.get("task").strip().lower()

        if should_render(schema_section["type_dose_dm_seg"], task):
            utils.title_header("Dose Metrics for Segmentation")
            render_field(
                "type_dose_dm_seg",
                schema_section["type_dose_dm_seg"],
                section_prefix,
            )

        dm_seg_entries = st.session_state.get(
            f"{section_prefix}_type_dose_dm_seg_list", []
        )

        if dm_seg_entries and has_renderable_fields(
            dose_dm_seg_fields, schema_section, task
        ):
            utils.title_header("Dose Metric Specifications (Segmentation)", size="1rem")
            tabs = st.tabs([str(entry) for entry in dm_seg_entries if entry])
            for tab, seg_name in zip(tabs, dm_seg_entries):
                with tab:
                    sub_prefix = f"{section_prefix}.{seg_name}"
                    if should_render(
                        schema_section["metric_specifications_dm_seg"], task
                    ):
                        render_field(
                            "metric_specifications_dm_seg",
                            schema_section["metric_specifications_dm_seg"],
                            sub_prefix,
                        )

                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if should_render(schema_section["on_volume_dm_seg"], task):
                            render_field(
                                "on_volume_dm_seg",
                                schema_section["on_volume_dm_seg"],
                                sub_prefix,
                            )
                    with col2:
                        if should_render(
                            schema_section["treatment_modality_dm_seg"], task
                        ):
                            render_field(
                                "treatment_modality_dm_seg",
                                schema_section["treatment_modality_dm_seg"],
                                sub_prefix,
                            )

                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col1:
                        if should_render(schema_section["dose_engine_dm_seg"], task):
                            render_field(
                                "dose_engine_dm_seg",
                                schema_section["dose_engine_dm_seg"],
                                sub_prefix,
                            )
                    with col2:
                        if should_render(
                            schema_section["dose_grid_resolution_dm_seg"], task
                        ):
                            render_field(
                                "dose_grid_resolution_dm_seg",
                                schema_section["dose_grid_resolution_dm_seg"],
                                sub_prefix,
                            )
                    with col3:
                        if should_render(schema_section["tps_vendor_dm_seg"], task):
                            render_field(
                                "tps_vendor_dm_seg",
                                schema_section["tps_vendor_dm_seg"],
                                sub_prefix,
                            )

                    if should_render(schema_section["sample_data_dm_seg"], task):
                        render_field(
                            "sample_data_dm_seg",
                            schema_section["sample_data_dm_seg"],
                            sub_prefix,
                        )

                    if should_render(schema_section["mean_data_dm_seg"], task):
                        render_field(
                            "mean_data_dm_seg",
                            schema_section["mean_data_dm_seg"],
                            sub_prefix,
                        )

                    if should_render(schema_section["figure_dm_seg"], task):
                        render_field(
                            "figure_dm_seg", schema_section["figure_dm_seg"], sub_prefix
                        )

        task = st.session_state.get("task").strip().lower()
        utils.section_divider()
        if should_render(schema_section["iov_method_seg"], task) or should_render(
            schema_section["iov_results_seg"], task
        ):
            utils.title_header("IOV (Inter-Observer Variability)")

        col1, col2 = st.columns([1, 1])
        with col1:
            if should_render(schema_section["iov_method_seg"], task):
                render_field(
                    "iov_method_seg", schema_section["iov_method_seg"], section_prefix
                )
        with col2:
            if should_render(schema_section["iov_results_seg"], task):
                render_field(
                    "iov_results_seg", schema_section["iov_results_seg"], section_prefix
                )
        ####################################
        # END EXCLUSIVE TO SEGMENTATION TASK
        ####################################

        ####################################
        # EXCLUSIVE TO DOSE PREDICTION TASK
        ####################################
        dose_seg_fields = [
            "metric_specifications_dm_dp",
            "on_volume_dm_dp",
            "sample_data_dm_dp",
            "mean_data_dm_dp",
            "figure_dm_dp",
        ]

        task = st.session_state.get("task").strip().lower()

        if should_render(schema_section["type_dose_dm_dp"], task):
            utils.title_header("Dose Metrics for Dose Prediction")
            render_field(
                "type_dose_dm_dp",
                schema_section["type_dose_dm_dp"],
                section_prefix,
            )

        dm_dp_entries = st.session_state.get(
            f"{section_prefix}_type_dose_dm_dp_list", []
        )

        if dm_dp_entries and has_renderable_fields(
            dose_seg_fields, schema_section, task
        ):
            utils.title_header(
                "Dose Metric Specifications (Dose Prediction)", size="1rem"
            )
            tabs = st.tabs([str(entry) for entry in dm_dp_entries if entry])

            for tab, dp_name in zip(tabs, dm_dp_entries):
                with tab:
                    sub_prefix = f"{section_prefix}.{dp_name}"

                    if should_render(
                        schema_section["metric_specifications_dm_dp"], task
                    ):
                        render_field(
                            "metric_specifications_dm_dp",
                            schema_section["metric_specifications_dm_dp"],
                            sub_prefix,
                        )

                    if should_render(schema_section["on_volume_dm_dp"], task):
                        render_field(
                            "on_volume_dm_dp",
                            schema_section["on_volume_dm_dp"],
                            sub_prefix,
                        )

                    if should_render(schema_section["sample_data_dm_dp"], task):
                        render_field(
                            "sample_data_dm_dp",
                            schema_section["sample_data_dm_dp"],
                            sub_prefix,
                        )

                    if should_render(schema_section["mean_data_dm_dp"], task):
                        render_field(
                            "mean_data_dm_dp",
                            schema_section["mean_data_dm_dp"],
                            sub_prefix,
                        )

                    if should_render(schema_section["figure_dm_dp"], task):
                        render_field(
                            "figure_dm_dp", schema_section["figure_dm_dp"], sub_prefix
                        )

                    utils.section_divider()

        #######################################
        # END EXCLUSIVE TO DOSE PREDICTION TASK
        #######################################

        ##########################
        # EXCLUSIVE TO OTHER TASK
        ##########################

        task = st.session_state.get("task").strip().lower()
        if should_render(schema_section["type_metrics_other"], task):
            utils.title_header("Other Metrics")
            render_field(
                "type_metrics_other",
                schema_section["type_metrics_other"],
                section_prefix,
            )
        other_keys = st.session_state.get(
            f"{section_prefix}_type_metrics_other_list", []
        )
        if other_keys:
            tabs = st.tabs(other_keys)
            for tab, name in zip(tabs, other_keys):
                with tab:
                    sub_prefix = f"{section_prefix}.{name}"
                    render_field(
                        "additional_info_other",
                        schema_section["additional_info_other"],
                        sub_prefix,
                    )
                    render_field(
                        "sample_data_other",
                        schema_section["sample_data_other"],
                        sub_prefix,
                    )
                    render_field(
                        "mean_data_other", schema_section["mean_data_other"], sub_prefix
                    )
                    render_field(
                        "figure_other", schema_section["figure_other"], sub_prefix
                    )

        #############################
        # END EXCLUSIVE TO OTHER TASK
        #############################

        # Uncertainty Metrics Section
        utils.title_header("Uncertainty Metrics")
        col1, col2 = st.columns([1, 1])
        with col1:
            render_field(
                "uncertainty_metrics_method",
                schema_section["uncertainty_metrics_method"],
                section_prefix,
            )
        with col2:
            render_field(
                "uncertainty_metrics_results",
                schema_section["uncertainty_metrics_results"],
                section_prefix,
            )

        utils.section_divider()
        # Other Evaluation Section
        utils.title_header("Other Evaluation")
        col1, col2 = st.columns([1, 1])
        with col1:
            render_field("other_method", schema_section["other_method"], section_prefix)
        with col2:
            render_field(
                "other_results", schema_section["other_results"], section_prefix
            )

    with quant_qual_tabs[1]:
        model_card_schema = utils.get_model_card_schema()
        if "qualitative_evaluation" in model_card_schema:
            qeval = model_card_schema["qualitative_evaluation"]
            section_prefix = "qualitative_evaluation"

            utils.section_divider()
            utils.title_header("Qualitative Evaluation")

            render_field(
                "evaluators_informations",
                qeval["evaluators_informations"],
                section_prefix,
            )
            utils.section_divider()

            def render_method_result_row(method_key, result_key, label: str):
                utils.title_header(label)
                col1, col2 = st.columns([1, 1])
                with col1:
                    render_field(method_key, qeval[method_key], section_prefix)
                with col2:
                    render_field(result_key, qeval[result_key], section_prefix)

            tabs = st.tabs(["Likert Scoring", "Turing Test", "Time Saving", "Other"])

            with tabs[0]:  # Likert
                utils.title_header("Likert Scoring")
                col1, col2 = st.columns([1, 1])
                with col1:
                    render_field(
                        "likert_scoring_method",
                        qeval["likert_scoring_method"],
                        section_prefix,
                    )
                with col2:
                    render_field(
                        "likert_scoring_results",
                        qeval["likert_scoring_results"],
                        section_prefix,
                    )

            with tabs[1]:  # Turing Test
                utils.title_header("Turing Test")
                col1, col2 = st.columns([1, 1])
                with col1:
                    render_field(
                        "turing_test_method",
                        qeval["turing_test_method"],
                        section_prefix,
                    )
                with col2:
                    render_field(
                        "turing_test_results",
                        qeval["turing_test_results"],
                        section_prefix,
                    )

            with tabs[2]:  # Time Saving
                utils.title_header("Time Saving")
                col1, col2 = st.columns([1, 1])
                with col1:
                    render_field(
                        "time_saving_method",
                        qeval["time_saving_method"],
                        section_prefix,
                    )
                with col2:
                    render_field(
                        "time_saving_results",
                        qeval["time_saving_results"],
                        section_prefix,
                    )

            with tabs[3]:  # Other
                utils.title_header("Other Evaluation")
                col1, col2 = st.columns([1, 1])
                with col1:
                    render_field("other_method", qeval["other_method"], section_prefix)
                with col2:
                    render_field(
                        "other_results", qeval["other_results"], section_prefix
                    )

            utils.section_divider()

            render_field("explainability", qeval["explainability"], section_prefix)
            render_field("citation_details", qeval["citation_details"], section_prefix)


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
                if st.button("Delete", key=f"delete_eval_{i}"):
                    to_delete = i

    if to_delete is not None:
        del st.session_state.evaluation_forms[to_delete]
        for key in list(st.session_state.keys()):
            if key.startswith(f"evaluation_{to_delete}_"):
                del st.session_state[key]
        st.rerun()

    if st.button("Add Another Evaluation"):
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

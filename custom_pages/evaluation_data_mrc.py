"""Evaluation data, methodology, and results / commissioning page."""

from __future__ import annotations

from typing import Any, TypedDict, cast

import streamlit as st

import utils
from render import (
    has_renderable_fields,
    render_field,
    render_fields,
    render_image_field,
    should_render,
)

TITLE = "Evaluation data, methodology, and results / commissioning"
SUBTITLE = (
    "containing all info about the evaluation data and procedure. "
    "Because it is common to evaluate your model on a different dataset, "
    "this section can be repeated as many times as needed. We refer to "
    "evaluation results for models that are evaluated but not necessarily "
    "with a clinical implementation in mind, and commissioning for models "
    "that are specifically evaluated within a clinical environment with "
    "clinic-specific data."
)

# This page renders dynamic forms with prefixes like "evaluation_<name>", so no
# single SECTION_PREFIX.


class EvaluationSection(TypedDict, total=False):
    # header/date
    evaluation_date: dict[str, Any]

    # evaluated by
    evaluated_by_name: dict[str, Any]
    evaluated_by_institution: dict[str, Any]
    evaluated_by_contact_email: dict[str, Any]

    # general info
    total_size: dict[str, Any]
    number_of_patients: dict[str, Any]
    source: dict[str, Any]
    acquisition_period: dict[str, Any]
    inclusion_exclusion_criteria: dict[str, Any]
    url_info: dict[str, Any]

    # generic frames/checks
    evaluation_frame: dict[str, Any]
    sanity_check: dict[str, Any]

    # technical characteristics (per-modality rendering)
    image_resolution: dict[str, Any]
    patient_positioning: dict[str, Any]
    scanner_model: dict[str, Any]
    scan_acquisition_parameters: dict[str, Any]
    scan_reconstruction_parameters: dict[str, Any]
    fov: dict[str, Any]

    # dose prediction (eval) specifics
    treatment_modality_eval: dict[str, Any]
    beam_configuration_energy: dict[str, Any]
    dose_engine: dict[str, Any]
    target_volumes_and_prescription: dict[str, Any]
    number_of_fractions: dict[str, Any]

    # reference standard
    reference_standard: dict[str, Any]
    reference_standard_qa: dict[str, Any]
    reference_standard_qa_additional_information: dict[str, Any]

    # patient demographics (evaluation suffix _ev)
    icd10_11_ev: dict[str, Any]
    tnm_staging_ev: dict[str, Any]
    age_ev: dict[str, Any]
    sex_ev: dict[str, Any]
    target_volume_cm3_ev: dict[str, Any]
    bmi_ev: dict[str, Any]
    additional_patient_info_ev: dict[str, Any]

    # quantitative metrics – ISM
    type_ism: dict[str, Any]
    on_volume_ism: dict[str, Any]
    registration_ism: dict[str, Any]
    sample_data_ism: dict[str, Any]
    mean_data_ism: dict[str, Any]
    figure_ism: dict[str, Any]

    # quantitative metrics – Dose Metrics (DM)
    type_dose_dm: dict[str, Any]
    metric_specifications_dm: dict[str, Any]
    on_volume_dm: dict[str, Any]
    treatment_modality_dm: dict[str, Any]
    dose_engine_dm: dict[str, Any]
    dose_grid_resolution_dm: dict[str, Any]
    tps_vendor_dm: dict[str, Any]
    sample_data_dm: dict[str, Any]
    mean_data_dm: dict[str, Any]
    figure_dm: dict[str, Any]

    # segmentation – Geometric Metrics (gm_seg)
    type_gm_seg: dict[str, Any]
    metric_specifications_gm_seg: dict[str, Any]
    on_volume_gm_seg: dict[str, Any]
    sample_data_gm_seg: dict[str, Any]
    mean_data_gm_seg: dict[str, Any]
    figure_gm_seg: dict[str, Any]

    # segmentation – Dose Metrics (dm_seg)
    type_dose_dm_seg: dict[str, Any]
    metric_specifications_dm_seg: dict[str, Any]
    on_volume_dm_seg: dict[str, Any]
    treatment_modality_dm_seg: dict[str, Any]
    dose_engine_dm_seg: dict[str, Any]
    dose_grid_resolution_dm_seg: dict[str, Any]
    tps_vendor_dm_seg: dict[str, Any]
    sample_data_dm_seg: dict[str, Any]
    mean_data_dm_seg: dict[str, Any]
    figure_dm_seg: dict[str, Any]

    # dose prediction – Dose Metrics (dm_dp)
    type_dose_dm_dp: dict[str, Any]
    metric_specifications_dm_dp: dict[str, Any]
    on_volume_dm_dp: dict[str, Any]
    sample_data_dm_dp: dict[str, Any]
    mean_data_dm_dp: dict[str, Any]
    figure_dm_dp: dict[str, Any]

    # other task metrics
    type_metrics_other: dict[str, Any]
    additional_info_other: dict[str, Any]
    sample_data_other: dict[str, Any]
    mean_data_other: dict[str, Any]
    figure_other: dict[str, Any]

    # uncertainty & other
    uncertainty_metrics_method: dict[str, Any]
    uncertainty_metrics_results: dict[str, Any]
    other_method: dict[str, Any]
    other_results: dict[str, Any]

    # qualitative evaluation
    evaluators_information: dict[str, Any]
    likert_scoring_method: dict[str, Any]
    likert_scoring_results: dict[str, Any]
    turing_test_method: dict[str, Any]
    turing_test_results: dict[str, Any]
    time_saving_method: dict[str, Any]
    time_saving_results: dict[str, Any]
    other_method: dict[str, Any]
    other_results: dict[str, Any]
    explainability: dict[str, Any]
    citation_details: dict[str, Any]


# ---- Section render helpers -------------------------------------------------
def _render_header_and_evaluated_by(section: EvaluationSection, section_prefix: str) -> None:
    utils.require_task()

    if "evaluation_date" in section:
        render_field("evaluation_date", section["evaluation_date"], section_prefix)

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
            k in section
            for k in (
                "evaluated_by_name",
                "evaluated_by_institution",
                "evaluated_by_contact_email",
            )
        ):
            col1, col2, col3 = st.columns([1, 1.5, 1.5])
            with col1:
                render_field("evaluated_by_name", section["evaluated_by_name"], section_prefix)
            with col2:
                render_field("evaluated_by_institution", section["evaluated_by_institution"], section_prefix)
            with col3:
                render_field("evaluated_by_contact_email", section["evaluated_by_contact_email"], section_prefix)
    else:
        st.info("Evaluation team is the same as the approval team. Fields auto-filled.")

    utils.section_divider()
    render_fields(["evaluation_frame", "sanity_check"], section, section_prefix, st.session_state.get("task", ""))


def _render_general_info(section: EvaluationSection, section_prefix: str) -> None:
    utils.section_divider()
    utils.title_header("Evaluation Dataset", size="1.2rem")
    utils.light_header_italics(
        "Note that all fields refer to the raw evaluation data used in 'Model inputs' (i.e. "
        "before  pre-processing steps) and raw 'Model outputs' for supervised models (i.e. after post-processing)."
    )
    utils.title_header("1. General information")

    col1, col2 = st.columns([1, 1])
    with col1:
        render_field("total_size", section["total_size"], section_prefix)
    with col2:
        render_field("number_of_patients", section["number_of_patients"], section_prefix)
    render_field("source", section["source"], section_prefix)

    col1, col2 = st.columns([1, 1])
    with col1:
        render_field("acquisition_period", section["acquisition_period"], section_prefix)
    with col2:
        render_field(
            "inclusion_exclusion_criteria", section["inclusion_exclusion_criteria"], section_prefix
        )
    render_field("url_info", section["url_info"], section_prefix)


def _render_technical_characteristics(section: EvaluationSection, section_prefix: str) -> None:
    utils.section_divider()
    utils.title_header("2. Technical characteristics")
    utils.light_header_italics("(i.e. image acquisition protocol, treatment details, …)")

    modality_entries: list[dict[str, str]] = []
    for key, value in st.session_state.items():
        if key.endswith("model_inputs") and isinstance(value, list):
            modality_entries.extend({"modality": item, "source": "model_inputs"} for item in value)
        elif key.endswith("model_outputs") and isinstance(value, list):
            modality_entries.extend({"modality": item, "source": "model_outputs"} for item in value)

    if not modality_entries:
        st.warning(
            "Start by adding model inputs and outputs in the Technical Specifications section to enable technical details."
        )
        return

    tabs = st.tabs([utils.strip_brackets(m["modality"]) for m in modality_entries])

    for idx, entry in enumerate(modality_entries):
        modality, source = entry["modality"], entry["source"]
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
                "scan_acquisition_parameters": section["scan_acquisition_parameters"],
                "scan_reconstruction_parameters": section["scan_reconstruction_parameters"],
                "fov": section["fov"],
            }
            for f in field_keys.values():
                f["placeholder"] = f.get("placeholder", "N/A or NA if Not Applicable")

            col1, col2 = st.columns([1, 1])
            with col1:
                render_field(f"{clean_modality}_{source}_image_resolution", field_keys["image_resolution"], section_prefix)
            with col2:
                render_field(f"{clean_modality}_{source}_patient_positioning", field_keys["patient_positioning"], section_prefix)

            render_field(f"{clean_modality}_{source}_scanner_model", field_keys["scanner_model"], section_prefix)

            col1, col2 = st.columns([1, 1])
            with col1:
                render_field(f"{clean_modality}_{source}_scan_acquisition_parameters", field_keys["scan_acquisition_parameters"], section_prefix)
            with col2:
                render_field(f"{clean_modality}_{source}_scan_reconstruction_parameters", field_keys["scan_reconstruction_parameters"], section_prefix)

            render_field(f"{clean_modality}_{source}_fov", field_keys["fov"], section_prefix)


def _render_dose_prediction_eval(section: EvaluationSection, section_prefix: str) -> None:
    # Exclusive to dose prediction task (eval)
    task = st.session_state.get("task", "").strip().lower()
    if should_render(section["treatment_modality_eval"], task):
        render_field("treatment_modality_eval", section["treatment_modality_eval"], section_prefix)

    col1, col2 = st.columns([1, 1])
    with col1:
        if should_render(section["beam_configuration_energy"], task):
            render_field("beam_configuration_energy", section["beam_configuration_energy"], section_prefix)
    with col2:
        if should_render(section["dose_engine"], task):
            render_field("dose_engine", section["dose_engine"], section_prefix)

    col1, col2 = st.columns([1, 1])
    with col1:
        if should_render(section["target_volumes_and_prescription"], task):
            render_field("target_volumes_and_prescription", section["target_volumes_and_prescription"], section_prefix)
    with col2:
        if should_render(section["number_of_fractions"], task):
            render_field("number_of_fractions", section["number_of_fractions"], section_prefix)


def _render_reference_and_demographics(section: EvaluationSection, section_prefix: str, current_task: str) -> None:
    utils.section_divider()
    render_fields(
        ["reference_standard", "reference_standard_qa", "reference_standard_qa_additional_information"],
        section,
        section_prefix,
        current_task,
    )

    utils.title_header("3. Patient Demographics and Clinical Characteristics")
    col1, col2 = st.columns([1, 1])
    with col1:
        render_field("icd10_11_ev", section["icd10_11_ev"], section_prefix)
    with col2:
        render_field("tnm_staging_ev", section["tnm_staging_ev"], section_prefix)

    col1, col2 = st.columns([1, 1])
    with col1:
        render_field("age_ev", section["age_ev"], section_prefix)
    with col2:
        render_field("sex_ev", section["sex_ev"], section_prefix)

    col1, col2 = st.columns([1, 1])
    with col1:
        render_field("target_volume_cm3_ev", section["target_volume_cm3_ev"], section_prefix)
    with col2:
        render_field("bmi_ev", section["bmi_ev"], section_prefix)

    render_field("additional_patient_info_ev", section["additional_patient_info_ev"], section_prefix)


def _render_quantitative_tabs(section: EvaluationSection, section_prefix: str, current_task: str) -> None:
    quant_qual_tabs = st.tabs(["Quantitative Evaluation", "Qualitative Evaluation"])

    # ----------------------- Quantitative Evaluation -------------------------
    with quant_qual_tabs[0]:
        utils.title_header_grey("Quantitative Evaluation")

        # ISM block
        ism_fields = ["on_volume_ism", "registration_ism", "sample_data_ism", "mean_data_ism", "figure_ism"]
        task = st.session_state.get("task", "").strip().lower()
        if should_render(section["type_ism"], task):
            utils.title_header("Image Similarity Metrics")
            render_field("type_ism", section["type_ism"], section_prefix)

        ism_entries = st.session_state.get(f"{section_prefix}_type_ism_list", [])
        if ism_entries and has_renderable_fields(ism_fields, section, current_task):
            tabs = st.tabs(ism_entries)
            for tab, type_name in zip(tabs, ism_entries):
                with tab:
                    sub_prefix = f"{section_prefix}.{type_name}"
                    task = st.session_state.get("task", "").strip().lower()
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if should_render(section["on_volume_ism"], task):
                            render_field("on_volume_ism", section["on_volume_ism"], sub_prefix)
                    with col2:
                        if should_render(section["registration_ism"], task):
                            render_field("registration_ism", section["registration_ism"], sub_prefix)
                    if should_render(section["sample_data_ism"], task):
                        render_field("sample_data_ism", section["sample_data_ism"], sub_prefix)
                    if should_render(section["mean_data_ism"], task):
                        render_field("mean_data_ism", section["mean_data_ism"], sub_prefix)
                    if should_render(section["figure_ism"], task):
                        render_image_field("figure_ism", section["figure_ism"], sub_prefix)

        # DM block
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
        task = st.session_state.get("task", "").strip().lower()
        if should_render(section["type_dose_dm"], task):
            utils.section_divider()
            utils.title_header("Dose Metrics")
            render_field("type_dose_dm", section["type_dose_dm"], section_prefix)

        dm_entries = st.session_state.get(f"{section_prefix}_type_dose_dm_list", [])
        if dm_entries and has_renderable_fields(dm_base_fields, section, current_task):
            tabs = st.tabs([str(entry) for entry in dm_entries if entry])
            for tab, dm_name in zip(tabs, dm_entries):
                with tab:
                    sub_prefix = f"{section_prefix}.{dm_name}"
                    task = st.session_state.get("task", "").strip().lower()
                    if should_render(section["metric_specifications_dm"], task):
                        render_field("metric_specifications_dm", section["metric_specifications_dm"], sub_prefix)
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if should_render(section["on_volume_dm"], task):
                            render_field("on_volume_dm", section["on_volume_dm"], sub_prefix)
                    with col2:
                        if should_render(section["registration_dm"], task):
                            render_field("registration_dm", section["registration_dm"], sub_prefix)
                    if should_render(section["treatment_modality_dm"], task):
                        render_field("treatment_modality_dm", section["treatment_modality_dm"], sub_prefix)
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col1:
                        if should_render(section["dose_engine_dm"], task):
                            render_field("dose_engine_dm", section["dose_engine_dm"], sub_prefix)
                    with col2:
                        if should_render(section["dose_grid_resolution_dm"], task):
                            render_field("dose_grid_resolution_dm", section["dose_grid_resolution_dm"], sub_prefix)
                    with col3:
                        if should_render(section["tps_vendor_dm"], task):
                            render_field("tps_vendor_dm", section["tps_vendor_dm"], sub_prefix)
                    if should_render(section["sample_data_dm"], task):
                        render_field("sample_data_dm", section["sample_data_dm"], sub_prefix)
                    if should_render(section["mean_data_dm"], task):
                        render_field("mean_data_dm", section["mean_data_dm"], sub_prefix)
                    if should_render(section["figure_dm"], task):
                        render_image_field("figure_dm", section["figure_dm"], sub_prefix)

        # Segmentation – geometric metrics
        task = st.session_state.get("task", "").strip().lower()
        if should_render(section["type_gm_seg"], task):
            utils.title_header("Geometric Metrics")
            render_field("type_gm_seg", section["type_gm_seg"], section_prefix)

        dose_seg_fields = ["metric_specifications_gm_seg", "on_volume_gm_seg", "sample_data_gm_seg", "mean_data_gm_seg", "figure_gm_seg"]
        seg_entries = st.session_state.get(f"{section_prefix}_type_gm_seg_list", [])
        if seg_entries and has_renderable_fields(dose_seg_fields, section, task):
            tabs = st.tabs([str(entry) for entry in seg_entries if entry])
            for tab, seg_name in zip(tabs, seg_entries):
                with tab:
                    sub_prefix = f"{section_prefix}.{seg_name}"
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        render_field("metric_specifications_gm_seg", section["metric_specifications_gm_seg"], sub_prefix)
                    with col2:
                        render_field("on_volume_gm_seg", section["on_volume_gm_seg"], sub_prefix)
                    render_field("sample_data_gm_seg", section["sample_data_gm_seg"], sub_prefix)
                    render_field("mean_data_gm_seg", section["mean_data_gm_seg"], sub_prefix)
                    render_image_field("figure_gm_seg", section["figure_gm_seg"], sub_prefix)

        # Segmentation – dose metrics
        task = st.session_state.get("task", "").strip().lower()
        if should_render(section["type_dose_dm_seg"], task):
            utils.section_divider()
            utils.title_header("Dose Metrics")
            render_field("type_dose_dm_seg", section["type_dose_dm_seg"], section_prefix)

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
        dm_seg_entries = st.session_state.get(f"{section_prefix}_type_dose_dm_seg_list", [])
        if dm_seg_entries and has_renderable_fields(dose_dm_seg_fields, section, task):
            tabs = st.tabs([str(entry) for entry in dm_seg_entries if entry])
            for tab, seg_name in zip(tabs, dm_seg_entries):
                with tab:
                    sub_prefix = f"{section_prefix}.{seg_name}"
                    if should_render(section["metric_specifications_dm_seg"], task):
                        render_field("metric_specifications_dm_seg", section["metric_specifications_dm_seg"], sub_prefix)
                    if should_render(section["on_volume_dm_seg"], task):
                        render_field("on_volume_dm_seg", section["on_volume_dm_seg"], sub_prefix)
                    if should_render(section["treatment_modality_dm_seg"], task):
                        render_field("treatment_modality_dm_seg", section["treatment_modality_dm_seg"], sub_prefix)
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col1:
                        if should_render(section["dose_engine_dm_seg"], task):
                            render_field("dose_engine_dm_seg", section["dose_engine_dm_seg"], sub_prefix)
                    with col2:
                        if should_render(section["dose_grid_resolution_dm_seg"], task):
                            render_field("dose_grid_resolution_dm_seg", section["dose_grid_resolution_dm_seg"], sub_prefix)
                    with col3:
                        if should_render(section["tps_vendor_dm_seg"], task):
                            render_field("tps_vendor_dm_seg", section["tps_vendor_dm_seg"], sub_prefix)
                    if should_render(section["sample_data_dm_seg"], task):
                        render_field("sample_data_dm_seg", section["sample_data_dm_seg"], sub_prefix)
                    if should_render(section["mean_data_dm_seg"], task):
                        render_field("mean_data_dm_seg", section["mean_data_dm_seg"], sub_prefix)
                    if should_render(section["figure_dm_seg"], task):
                        render_image_field("figure_dm_seg", section["figure_dm_seg"], sub_prefix)

        # IOV (segmentation)
        task = st.session_state.get("task", "").strip().lower()
        if should_render(section["iov_method_seg"], task) or should_render(section["iov_results_seg"], task):
            utils.section_divider()
            utils.title_header("IOV (Inter-Observer Variability)")

        col1, col2 = st.columns([1, 1])
        with col1:
            if should_render(section["iov_method_seg"], task):
                render_field("iov_method_seg", section["iov_method_seg"], section_prefix)
        with col2:
            if should_render(section["iov_results_seg"], task):
                render_field("iov_results_seg", section["iov_results_seg"], section_prefix)

        # Dose prediction – DM (dp)
        dose_seg_fields = ["metric_specifications_dm_dp", "on_volume_dm_dp", "sample_data_dm_dp", "mean_data_dm_dp", "figure_dm_dp"]
        task = st.session_state.get("task", "").strip().lower()
        if should_render(section["type_dose_dm_dp"], task):
            utils.title_header("Dose Metrics")
            render_field("type_dose_dm_dp", section["type_dose_dm_dp"], section_prefix)

        dm_dp_entries = st.session_state.get(f"{section_prefix}_type_dose_dm_dp_list", [])
        if dm_dp_entries and has_renderable_fields(dose_seg_fields, section, task):
            tabs = st.tabs([str(entry) for entry in dm_dp_entries if entry])
            for tab, dp_name in zip(tabs, dm_dp_entries):
                with tab:
                    sub_prefix = f"{section_prefix}.{dp_name}"
                    if should_render(section["metric_specifications_dm_dp"], task):
                        render_field("metric_specifications_dm_dp", section["metric_specifications_dm_dp"], sub_prefix)
                    if should_render(section["on_volume_dm_dp"], task):
                        render_field("on_volume_dm_dp", section["on_volume_dm_dp"], sub_prefix)
                    if should_render(section["sample_data_dm_dp"], task):
                        render_field("sample_data_dm_dp", section["sample_data_dm_dp"], sub_prefix)
                    if should_render(section["mean_data_dm_dp"], task):
                        render_field("mean_data_dm_dp", section["mean_data_dm_dp"], sub_prefix)
                    if should_render(section["figure_dm_dp"], task):
                        render_image_field("figure_dm_dp", section["figure_dm_dp"], sub_prefix)

        # Other task metrics
        task = st.session_state.get("task", "").strip().lower()
        if should_render(section["type_metrics_other"], task):
            utils.title_header("Other Metrics")
            render_field("type_metrics_other", section["type_metrics_other"], section_prefix)

        other_keys = st.session_state.get(f"{section_prefix}_type_metrics_other_list", [])
        if other_keys:
            tabs = st.tabs(other_keys)
            for tab, name in zip(tabs, other_keys):
                with tab:
                    sub_prefix = f"{section_prefix}.{name}"
                    render_field("additional_info_other", section["additional_info_other"], sub_prefix)
                    render_field("sample_data_other", section["sample_data_other"], sub_prefix)
                    render_field("mean_data_other", section["mean_data_other"], sub_prefix)
                    render_image_field("figure_other", section["figure_other"], sub_prefix)

        utils.section_divider()
        utils.title_header("Uncertainty Metrics")
        col1, col2 = st.columns([1, 1])
        with col1:
            render_field("uncertainty_metrics_method", section["uncertainty_metrics_method"], section_prefix)
        with col2:
            render_field("uncertainty_metrics_results", section["uncertainty_metrics_results"], section_prefix)

        utils.section_divider()
        utils.title_header("Other")
        col1, col2 = st.columns([1, 1])
        with col1:
            render_field("other_method", section["other_method"], section_prefix)
        with col2:
            render_field("other_results", section["other_results"], section_prefix)

    # ----------------------- Qualitative Evaluation --------------------------
    with quant_qual_tabs[1]:
        # model_card_schema = utils.get_model_card_schema()
        # if "qualitative_evaluation" in model_card_schema:
        #     qeval = cast(QualitativeEvaluationSection, model_card_schema["qualitative_evaluation"])
        #     q_prefix = f"{section_prefix}_qualitative_evaluation"

            utils.title_header_grey("Qualitative Evaluation")
            render_field("evaluators_information", section["evaluators_information"], section_prefix)

            tabs = st.tabs(["Likert Scoring", "Turing Test", "Time Saving", "Other"])
            with tabs[0]:
                utils.title_header("Likert Scoring")
                col1, col2 = st.columns([1, 1])
                with col1:
                    render_field("likert_scoring_method", section["likert_scoring_method"], section_prefix)
                with col2:
                    render_field("likert_scoring_results", section["likert_scoring_results"], section_prefix)

            with tabs[1]:
                utils.title_header("Turing Test")
                col1, col2 = st.columns([1, 1])
                with col1:
                    render_field("turing_test_method", section["turing_test_method"], section_prefix)
                with col2:
                    render_field("turing_test_results", section["turing_test_results"], section_prefix)

            with tabs[2]:
                utils.title_header("Time Saving")
                col1, col2 = st.columns([1, 1])
                with col1:
                    render_field("time_saving_method", section["time_saving_method"], section_prefix)
                with col2:
                    render_field("time_saving_results", section["time_saving_results"], section_prefix)

            with tabs[3]:
                utils.title_header("Other Evaluation")
                col1, col2 = st.columns([1, 1])
                with col1:
                    render_field("qualitative_other_method", section["qualitative_other_method"], section_prefix)
                with col2:
                    render_field("qualitative_other_results", section["qualitative_other_results"], section_prefix)

            utils.section_divider()
            render_field("explainability", section["explainability"], section_prefix)
            render_field("citation_details", section["citation_details"], section_prefix)


def _render_one_evaluation_form(form_name: str, eval_schema: EvaluationSection, task: str) -> None:
    """Render one evaluation form inside an expander, with delete button."""
    section_prefix = f"evaluation_{form_name.replace(' ', '_')}"
    with st.expander(f"{form_name}", expanded=False):
        _render_header_and_evaluated_by(eval_schema, section_prefix)
        _render_general_info(eval_schema, section_prefix)
        _render_technical_characteristics(eval_schema, section_prefix)
        _render_dose_prediction_eval(eval_schema, section_prefix)
        _render_reference_and_demographics(eval_schema, section_prefix, task)
        _render_quantitative_tabs(eval_schema, section_prefix, task)

        col1, col2 = st.columns([0.2, 0.8])
        with col1:
            if st.button("Delete", key=f"delete_eval_{form_name}"):
                st.session_state["_to_delete_eval_form"] = form_name


def evaluation_data_mrc_render() -> None:
    """Public entrypoint: page scaffold + dynamic form management."""
    from side_bar import sidebar_render  # noqa: PLC0415
    sidebar_render()

    schema_any: dict[str, Any] = utils.get_model_card_schema()
    eval_schema = cast(EvaluationSection, schema_any["evaluation_data_methodology_results_commisioning"])

    utils.title(TITLE)
    utils.subtitle(SUBTITLE)

    task = st.session_state.get("task", "Image-to-Image translation")

    if "evaluation_forms" not in st.session_state:
        st.session_state.evaluation_forms = []

    with st.expander("Add New Evaluation Form"):
        new_form_name = st.text_input("Evaluation name", key="new_eval_name")
        if st.button("Add Evaluation Form"):
            if new_form_name:
                if new_form_name not in st.session_state.evaluation_forms:
                    st.session_state.evaluation_forms.append(new_form_name)
                    st.success(f"Added evaluation form: {new_form_name}")
                    st.rerun()
                else:
                    st.warning("An evaluation form with this name already exists.")
            else:
                st.warning("Please enter a name for the evaluation form.")

    # Render forms
    for form_name in list(st.session_state.evaluation_forms):
        _render_one_evaluation_form(form_name, eval_schema, task)

    # Handle deletion if requested
    form_to_delete = st.session_state.pop("_to_delete_eval_form", None)
    if form_to_delete:
        st.session_state.evaluation_forms.remove(form_to_delete)
        prefix = f"evaluation_{form_to_delete.replace(' ', '_')}_"
        for key in list(st.session_state.keys()):
            if key.startswith(prefix):
                del st.session_state[key]
        st.rerun()

    # Navigation (unchanged behavior)
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

# render.py
import streamlit as st
from persist import persist

def title_header(text, size="1.1rem", bottom_margin="1em", top_margin="0.5em"):
    st.markdown(
        f"""
        <div style='
            font-size: {size};
            font-weight: 600;
            color: #333;
            margin-top: {top_margin};
            margin-bottom: {bottom_margin};
        '>{text}</div>
        """,
        unsafe_allow_html=True
    )

def section_divider():
    st.markdown(
        "<hr style='margin: 1.5em 0; border: none; border-top: 1px solid #ccc;'>",
        unsafe_allow_html=True
    )

def render_schema_section(schema_section, section_prefix="", current_task=None):
    for key, props in schema_section.items():
        if should_render(props, current_task):
            render_field(key, props, section_prefix)

def has_renderable_fields(field_keys, schema_section, current_task):
    return any(
        key in schema_section and should_render(schema_section[key], current_task)
        for key in field_keys
    )

def render_evaluation_section(schema_section, section_prefix, current_task):
    render_fields(["evaluation_date"], schema_section, section_prefix, current_task)
    section_divider()

    title_header("Evaluated by")
    same_key = f"{section_prefix}_evaluated_same_as_approved"
    same = st.checkbox("Same as 'Approved by'", key=persist(same_key))

    if not same:
        if all(k in schema_section for k in ["evaluated_by_name", "evaluated_by_institution", "evaluated_by_contact_email"]):
            col1, col2, col3 = st.columns([1, 1.5, 1.5])  # puedes ajustar proporciones
            with col1:
                render_field("evaluated_by_name", schema_section["evaluated_by_name"], section_prefix)
            with col2:
                render_field("evaluated_by_institution", schema_section["evaluated_by_institution"], section_prefix)
            with col3:
                render_field("evaluated_by_contact_email", schema_section["evaluated_by_contact_email"], section_prefix)

    else:
        st.info("Evaluation team is the same as the approval team. Fields auto-filled.")
    section_divider()

    render_fields(["evaluation_frame", "sanity_check"], schema_section, section_prefix, current_task)
    section_divider()

    title_header("Evaluation Dataset")

    title_header("General Information", size="1rem")
    render_fields([
        "total_size", "number_of_patients", "source", "acquisition_period",
        "inclusion_exclusion_criteria", "url_info"
    ], schema_section, section_prefix, current_task)
    section_divider()
    title_header("Technical Characteristics", size="1rem")
    render_fields([
        "image_resolution", "patient_positioning", "scanner_model", "scan_acquisition_parameters",
        "scan_reconstruction_parameters", "fov", "treatment_modality", "beam_configuration_energy",
        "dose_engine", "target_volumes_and_prescription", "number_of_fractions",
        "reference_standard", "reference_standard_qa", "reference_standard_qa_additional_information"
    ], schema_section, section_prefix, current_task)
    section_divider()

    title_header("Patient Demographics and Clinical Characteristics", size="1rem")
    render_fields([
        "icd10_11", "tnm_staging", "age_ev", "sex_ev", "target_volume_cm3", "bmi", "additional_patient_info"
    ], schema_section, section_prefix, current_task)
    section_divider()
    title_header("Quantitative Evaluation")

    # Image similarity metrics
    ism_fields = ["type_ism", "on_volume_ism", "registration_ism", "sample_data_ism", "mean_data_ism", "figure_ism"]
    if has_renderable_fields(ism_fields, schema_section, current_task):
        title_header("Image similarity metrics", size="1rem")
        render_fields(ism_fields, schema_section, section_prefix, current_task)

    # Dose metrics - Image-to-Image
    dose_dm_fields = ["type_dose_dm", "metric_specifications_dm", "on_volume_dm", "registration_dm", "treatment_modality_dm", "dose_engine_dm", "dose_grid_resolution_dm", "tps_vendor_dm", "sample_data_dm", "mean_data_dm", "figure_dm"]
    if has_renderable_fields(dose_dm_fields, schema_section, current_task):
        title_header("Dose metrics", size="1rem")
        render_fields(dose_dm_fields, schema_section, section_prefix, current_task)

    # Dose metrics - Segmentation
    dose_seg_fields = ["type_dose_seg", "metric_specifications_seg", "on_volume_seg", "treatment_modality_seg", "dose_engine_seg", "dose_grid_resolution_seg", "tps_vendor_seg", "sample_data_seg", "mean_data_seg", "figure_seg"]
    if has_renderable_fields(dose_seg_fields, schema_section, current_task):
        title_header("Geometric metrics", size="1rem")
        title_header("Dose metrics", size="1rem")
        render_fields(dose_seg_fields, schema_section, section_prefix, current_task)
    title_header("Other", size="1rem")

    title_header("Qualitative Evaluation")


def render_fields(field_keys, schema_section, section_prefix, current_task):
    for key in field_keys:
        if key in schema_section and should_render(schema_section[key], current_task):
            render_field(key, schema_section[key], section_prefix)

def should_render(props, current_task):
    model_types = props.get("model_types")
    if not model_types:
        return True
    if current_task:
        return current_task.strip().lower() in map(str.lower, model_types)
    return False


def render_field(key, props, section_prefix):
    full_key = f"{section_prefix}_{key}"
    #label = props.get("label", key)
    label = props.get("label") or key or "Field"
    description = props.get("description", "")
    example = props.get("example", "")
    field_type = props.get("type", "string")
    required = props.get("required", False)
    options = props.get("options", [])


    create_helpicon(label, description, field_type, example, required)

    try:
        safe_label = label if label.strip() else "Field"
        if field_type == "select":
            if not options:
                st.warning(f"Field '{label}' is missing options for select dropdown.")
            else:
                st.selectbox(safe_label, options=options, key=persist(full_key), help=description, label_visibility="hidden")
        else:
            st.text_input(safe_label, key=persist(full_key), label_visibility="hidden")
    except Exception as e:
        st.error(f"Error rendering field '{label}': {str(e)}")

def create_helpicon(label, description, field_format, example, required=False):
    required_tag = "<span style='color: black; font-size: 1.2em; cursor: help;' title='Required field'>*</span>" if required else ""
    
    st.markdown("""
    <style>
    .tooltip-inline {
        display: inline-block;
        position: relative;
        margin-left: 4px;
        cursor: pointer;
        font-size: 0.8em;
        color: #999;
    }
    .tooltip-inline .tooltiptext {
        visibility: hidden;
        width: 260px;
        background-color: #f9f9f9;
        color: #333;
        text-align: left;
        border-radius: 6px;
        border: 1px solid #ccc;
        padding: 10px;
        position: absolute;
        bottom: 150%;
        left: 0;
        z-index: 10;
        box-shadow: 0px 0px 10px rgba(0,0,0,0.1);
        font-weight: normal;
        font-size: 0.9em;
        line-height: 1.4;
    }
    .tooltip-inline:hover .tooltiptext {
        visibility: visible;
    }
    <style>
    /* Align number_input and text_input visually */
    div[data-testid="stNumberInput"] {
        margin-top: -6px !important;
    }
    div[data-testid="stTextInput"] {
        margin-top: 0px !important;
    }
    </style>

    </style>
    """, unsafe_allow_html=True)
    tooltip_html = f"""
    <div style='margin-bottom: 0px; font-weight: 500; font-size: 0.98em;'>
        {label} {required_tag}
        <span class="tooltip-inline">ⓘ
            <span class="tooltiptext">
                <span style="font-weight: bold;">Description:</span> {description}<br><br>
                <span style="font-weight: bold;">Format:</span> {field_format}<br><br>
                <span style="font-weight: bold;">Example(s):</span> {example}
            </span>
        </span>
    </div>
    """
    st.markdown(tooltip_html, unsafe_allow_html=True)
    

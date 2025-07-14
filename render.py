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

def render_schema_section(schema_section, section_prefix="", current_task=None):
    """Render fields from a flat schema section with optional task filtering."""
    for key, props in schema_section.items():
        model_types = props.get("model_types")
        if model_types is None or (current_task and current_task.lower() in map(str.lower, model_types)):
            render_field(key, props, section_prefix)


def render_evaluation_section(schema_section, section_prefix, current_task):

    def section_divider():
        st.markdown("<hr style='margin: 1.5em 0; border: none; border-top: 1px solid #ccc;'>", unsafe_allow_html=True)

    def render_fields(field_keys, schema_section, section_prefix, current_task):
        for key in field_keys:
            if key in schema_section:
                props = schema_section[key]
                model_types = props.get("model_types")
                if model_types is None or (current_task and current_task.lower() in map(str.lower, model_types)):
                    render_field(key, props, section_prefix)



    # 1. Evaluation Date
    title_header("1. Evaluation Date", size="1.1rem")
    render_fields(["evaluation_date"], schema_section, section_prefix, current_task)
    section_divider()

    # 2. Evaluated by
    title_header("2. Evaluated by", size="1.1rem")
    same_key = f"{section_prefix}_evaluated_same_as_approved"
    same = st.checkbox("Same as 'Approved by'", key=persist(same_key))
    if not same:
        render_fields(["evaluated_by_name", "evaluated_by_institution", "evaluated_by_contact_email"],
    schema_section, section_prefix, current_task
)

    else:
        st.info("Evaluation team is the same as the approval team. Fields auto-filled.")
    section_divider()

    render_fields(["evaluation_frame", "sanity_check"], schema_section, section_prefix, current_task)
    section_divider()

    title_header("3. Evaluation Dataset", size="1.1rem")
    dataset = schema_section.get("evaluation_dataset", {})  

    # 3.1 General Information
    title_header("3.1 General Information", size="1rem")
    render_fields([
        "evaluation_dataset_total_size",
        "evaluation_dataset_number_of_patients",
        "evaluation_dataset_source",
        "evaluation_dataset_acquisition_period",
        "evaluation_dataset_inclusion_exclusion_criteria",
        "evaluation_dataset_url_info"
    ], schema_section, section_prefix, current_task)



    # 3.2 Technical Characteristics
    title_header("3.2 Technical Characteristics", size="1rem")
    render_fields([
        "image_resolution", "patient_positioning", "scanner_model", "scan_acquisition_parameters",
        "scan_reconstruction_parameters", "fov", "treatment_modality", "beam_configuration_energy",
        "dose_engine", "target_volumes_and_prescription", "number_of_fractions", "reference_standard",
        "reference_standard_qa", "reference_standard_qa_additional_information"
    ], dataset, f"{section_prefix}_evaluation_dataset", current_task)
    section_divider()

    # 3.3 Patient Demographics and Clinical Characteristics
    title_header("3.3 Patient Demographics and Clinical Characteristics", size="1rem")
    render_fields([
        "icd10_11", "tnm_staging", "age", "sex", "target_volume_cm3", "bmi", "additional_patient_info"
    ], dataset, f"{section_prefix}_evaluation_dataset", current_task)
    section_divider()



def render_field(key, props, section_prefix):
    """Render a single field based on type and schema properties."""
    full_key = f"{section_prefix}_{key}"
    label = props.get("label", key)
    description = props.get("description", "")
    example = props.get("example", "")
    field_type = props.get("type", "string")
    required = props.get("required", False)
    options = props.get("options", []) 

    create_helpicon(label, description, field_type, example, required)

    if field_type == "select":
        st.selectbox(label, options=options, key=persist(full_key), help=description, label_visibility="hidden")
    else:
        st.text_input(label, key=persist(full_key), label_visibility="hidden")


def create_helpicon(label, description, field_format, example, required=False):
    """Render a tooltip-style help icon next to field labels."""
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

    div[data-testid="stTextInput"] {
        margin-top: -10px;
    }
    </style>
    """, unsafe_allow_html=True)

    tooltip_html = f"""
    <div style='margin-bottom: -8px; font-weight: 500; font-size: 0.98em;'>
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

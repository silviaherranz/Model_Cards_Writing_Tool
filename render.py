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
    """Render grouped fields using headers and vertical layout with spacing."""

    def render_fields(field_keys):
        for key in field_keys:
            if key in schema_section:
                props = schema_section[key]
                model_types = props.get("model_types")
                if model_types is None or (current_task and current_task in model_types):
                    render_field(key, props, section_prefix)
                    st.markdown("")

    if section_prefix.startswith("evaluation_"):

        #title_header("Evaluation Date", size="h3")
        render_fields(["evaluation_date"])
        st.markdown("<hr style='margin: 1.5em 0; border: none; border-top: 1px solid #ccc;'>", unsafe_allow_html=True)

        title_header("Evaluated by", size="h3")
        same_key = f"{section_prefix}_evaluated_same_as_approved"
        same = st.checkbox("Same as 'Approved by'", key=persist(same_key))
        if not same:
            render_fields([
                "evaluated_by_name", "evaluated_by_institution", "evaluated_by_contact_email"
            ])
        else:
            st.info("Evaluation team is the same as the approval team. Fields auto-filled.")
        st.markdown("<hr style='margin: 1.5em 0; border: none; border-top: 1px solid #ccc;'>", unsafe_allow_html=True)

        render_fields(["evaluation_frame", "sanity_check"])

        title_header("Evaluation Dataset", size="h3")

        st.markdown("#### 3.1 General Information")
        render_fields([
            "evaluation_dataset_total_size", "evaluation_dataset_number_of_patients",
            "evaluation_dataset_source", "evaluation_dataset_acquisition_period",
            "evaluation_dataset_inclusion_exclusion_criteria", "evaluation_dataset_url_info"
        ])

        st.markdown("#### 3.2 Technical Characteristics")
        render_fields([
            "evaluation_dataset_image_resolution", "evaluation_dataset_patient_positioning",
            "evaluation_dataset_scanner_model", "evaluation_dataset_scan_acquisition_parameters",
            "evaluation_dataset_scan_reconstruction_parameters", "evaluation_dataset_fov",
            "evaluation_dataset_treatment_modality", "evaluation_dataset_beam_configuration_energy",
            "evaluation_dataset_dose_engine", "evaluation_dataset_target_volumes_and_prescription",
            "evaluation_dataset_number_of_fractions", "evaluation_dataset_reference_standard",
            "evaluation_dataset_reference_standard_qa", "evaluation_dataset_reference_standard_qa_additional_information"
        ])

        st.markdown("#### 3.3 Patient Demographics and Clinical Characteristics")
        render_fields([
            "evaluation_dataset_icd10_11", "evaluation_dataset_tnm_staging", "evaluation_dataset_age",
            "evaluation_dataset_sex", "evaluation_dataset_target_volume_cm3",
            "evaluation_dataset_bmi", "evaluation_dataset_additional_patient_info"
        ])

        st.markdown("---")
        st.markdown("### 4. Quantitative Evaluation")
        render_fields(["quantitative_evaluation", "dose_metrics", "dose_metrics_segmentation"])

        st.markdown("### 5. Qualitative Evaluation")

    else:
        for key, props in schema_section.items():
            model_types = props.get("model_types")
            if model_types is None or (current_task and current_task in model_types):
                render_field(key, props, section_prefix)


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

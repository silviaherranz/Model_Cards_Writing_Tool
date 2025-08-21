import streamlit as st
import utils
import validation_utils

model_card_schema = utils.get_model_card_schema()

SECTION_NAMES = {
    "Card Metadata": ["card_metadata"],
    "Model Basic Information": ["model_basic_information"],
    "Technical Specifications": ["technical_specifications", "learning_architecture"],
    "Training data, methodology, and information": [
        "training_data"
    ],
    "Evaluation data, methodology, and results / commissioning": [
        "evaluation_data_methodology_results_commisioning",
        "qualitative_evaluation",
    ],
}


def warnings_render():
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

    task = st.session_state.get("task", "Image-to-Image translation")

    missing_required = validation_utils.validate_required_fields(
        model_card_schema, current_task=task
    )

    grouped_missing = {}
    for section, label in missing_required:
        if section not in grouped_missing:
            grouped_missing[section] = []
        grouped_missing[section].append(label)

    if not grouped_missing:
        return

    SECTION_LABEL_MAP = {}
    for display_name, internal_keys in SECTION_NAMES.items():
        for key in internal_keys:
            SECTION_LABEL_MAP[key] = display_name

    display_grouped = {}
    for section_key, labels in grouped_missing.items():
        section_title = SECTION_LABEL_MAP.get(section_key)
        if section_title:
            display_grouped.setdefault(section_title, []).extend(labels)

    for section_title, labels in display_grouped.items():
        st.info(f"Section: {section_title}")
        st.warning(f"Missing required fields: {', '.join(labels)}")
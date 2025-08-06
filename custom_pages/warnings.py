# import streamlit as st
# import utils

# model_card_schema = utils.get_model_card_schema()


# def warnings_render():
#     from side_bar import sidebar_render

#     sidebar_render()

#     task = st.session_state.get("task", "Image-to-Image translation")

#     missing_required = utils.validate_required_fields(
#         model_card_schema, st.session_state, current_task=task
#     )
#     st.warning(
#         "Warning: The following required fields are missing:\n\n"
#         + "\n".join([f"- {field}" for field in missing_required])
#     )
import streamlit as st
import utils

model_card_schema = utils.get_model_card_schema()

SECTION_NAMES = {
    "Card Metadata": ["card_metadata"],
    "Model Basic Information": ["model_basic_information"],
    "Technical Specifications": ["technical_specifications", "learning_architecture"],
    "Training data, methodology, and information": ["training_data_methodology_results_commisioning"],
    "Evaluation data, methodology, and results / commissioning": ["evaluation_data_methodology_results_commisioning", "qualitative_evaluation"],
}

def warnings_render():
    from side_bar import sidebar_render
    sidebar_render()

    task = st.session_state.get("task", "Image-to-Image translation")

    # Validar campos requeridos
    missing_required = utils.validate_required_fields(
        model_card_schema, st.session_state, current_task=task
    )

    # Agrupar los campos faltantes por su clave de sección
    grouped_missing = {}
    for section, label in missing_required:
        if section not in grouped_missing:
            grouped_missing[section] = []
        grouped_missing[section].append(label)

    if not grouped_missing:
        return  # Todo está completo

    # Invertimos SECTION_NAMES para obtener un mapeo sección -> nombre visible
    SECTION_LABEL_MAP = {}
    for display_name, internal_keys in SECTION_NAMES.items():
        for key in internal_keys:
            SECTION_LABEL_MAP[key] = display_name

    # Agrupamos los campos faltantes usando solo los nombres definidos en SECTION_NAMES
    display_grouped = {}
    for section_key, labels in grouped_missing.items():
        section_title = SECTION_LABEL_MAP.get(section_key)
        if section_title:  # Solo usamos secciones explícitamente definidas
            display_grouped.setdefault(section_title, []).extend(labels)

    # Mostrar advertencias agrupadas por sección visible
    for section_title, labels in display_grouped.items():
        st.info(f"Section: {section_title}")
        st.warning(f"Missing required fields: {', '.join(labels)}")



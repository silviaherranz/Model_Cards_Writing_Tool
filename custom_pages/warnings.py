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

# Nombres legibles para secciones
SECTION_NAMES = {
    "card_metadata": "Card Metadata",
    "model_basic_information": "Model Basic Information",
    "technical_specifications": "Technical Specifications",
    "training_data": "Training data, methodology, and information",
    "evaluation_data": "Evaluation data, methodology, and results / commissioning"
}

def warnings_render():
    from side_bar import sidebar_render
    sidebar_render()

    task = st.session_state.get("task", "Image-to-Image translation")

    # Campos requeridos vacíos
    missing_required = utils.validate_required_fields(
        model_card_schema, st.session_state, current_task=task
    )

    # Agrupar por sección
    grouped_missing = {}
    for full_key in missing_required:
        if "_" in full_key:
            section, field = full_key.split("_", 1)
        else:
            section, field = "general", full_key

        if section not in grouped_missing:
            grouped_missing[section] = []
        grouped_missing[section].append(field)

    if not grouped_missing:
        return  # Todo completo

    # Mostrar por sección
    for section, fields in grouped_missing.items():
        section_title = SECTION_NAMES.get(section, section.replace("_", " ").title())
        st.info(f"📂 Section: {section_title}")

        schema_section = model_card_schema.get(section, {})

        for field in fields:
            # Buscar el title desde el schema
            title = schema_section.get(field, {}).get("title", field.replace("_", " ").capitalize())
            st.warning(f"⚠️ Missing required field: **{title}**")

import streamlit as st
import utils
from persist import persist
from render import (
    create_helpicon,
    render_evaluation_section,
    render_field,
    title_header,
)

model_card_schema = utils.get_model_card_schema()


def warnings_render():
    from side_bar import sidebar_render
    sidebar_render()
    
    task = st.session_state.get("task", "Image-to-Image translation")

    missing_required = utils.validate_required_fields(
            model_card_schema, st.session_state, current_task=task
    )
    st.warning(
        "Warning: The following required fields are missing:\n\n"
        + "\n".join([f"- {field}" for field in missing_required])
    )
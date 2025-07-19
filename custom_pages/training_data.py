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


def training_data_render():
    from side_bar import sidebar_render
    sidebar_render()
    task = st.session_state.get("task", "Image-to-Image translation")

    
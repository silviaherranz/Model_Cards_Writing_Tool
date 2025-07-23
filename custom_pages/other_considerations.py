import streamlit as st
import utils
from render import render_field


def other_considerations_render():
    from side_bar import sidebar_render

    sidebar_render()
    model_card_schema = utils.get_model_card_schema()
    section = model_card_schema["other_considerations"]
    utils.title("Other considerations")
    render_field(
        "responsible_use_and_ethical_considerations",
        section["responsible_use_and_ethical_considerations"],
        "other_considerations",
    )
    render_field("risk_analysis", section["risk_analysis"], "other_considerations")
    render_field(
        "post_market_surveillance_live_monitoring",
        section["post_market_surveillance_live_monitoring"],
        "other_considerations",
    )
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([2, 12])
    with col1:
        if st.button("Previous"):
            from custom_pages.evaluation_data_mrc import evaluation_data_mrc_render

            st.session_state.runpage = evaluation_data_mrc_render
            st.rerun()

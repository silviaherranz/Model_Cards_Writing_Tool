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


def other_considerations_render():
    from side_bar import sidebar_render
    sidebar_render()
    section = model_card_schema["other_considerations"]
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
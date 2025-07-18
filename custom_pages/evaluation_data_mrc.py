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


def evaluation_data_mrc_render():
    from side_bar import sidebar_render
    sidebar_render()
    task = st.session_state.get("task", "Image-to-Image translation")

    if "evaluation_forms" not in st.session_state:
        existing_keys = [
            k for k in st.session_state.keys() if k.startswith("evaluation_")
        ]
        if existing_keys:
            indices = set(
                k.split("_")[1] for k in existing_keys if k.split("_")[1].isdigit()
            )
            st.session_state.evaluation_forms = [{} for _ in indices]
        else:
            st.session_state.evaluation_forms = [{}]
            
    utils.light_header("Evaluation Data Methodology, Results & Commissioning")
    utils.light_header_italics(
        "To be repeated as many times as evaluations sets used", bottom_margin="1em"
    )

    to_delete = None
    for i, eval_data in enumerate(st.session_state.evaluation_forms):
        with st.expander(f"Evaluation {i + 1}", expanded=False):
            render_evaluation_section(
                model_card_schema["evaluation_data_methodology_results_commisioning"],
                section_prefix=f"evaluation_{i}",
                current_task=task,
            )
            col1, col2 = st.columns([0.2, 0.8])
            with col1:
                if st.button("🗑️ Delete", key=f"delete_eval_{i}"):
                    to_delete = i

    if to_delete is not None:
        del st.session_state.evaluation_forms[to_delete]
        for key in list(st.session_state.keys()):
            if key.startswith(f"evaluation_{to_delete}_"):
                del st.session_state[key]
        st.rerun()

    if st.button("➕ Add Another Evaluation"):
        st.session_state.evaluation_forms.append({})
        st.rerun()

    with st.expander("Other considerations", expanded=False):
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
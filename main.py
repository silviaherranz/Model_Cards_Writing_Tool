from pathlib import Path

import pandas as pd
import streamlit as st
import utils
from persist import persist
from side_bar import sidebar_render
from custom_pages.card_metadata import card_metadata_render


model_card_schema = utils.get_model_card_schema()


def get_state(key, default=None):
    return st.session_state.get(key, default)


@st.cache_data(ttl=3600)
def get_cached_data():
    license_df = pd.read_html("https://huggingface.co/docs/hub/repositories-licenses")[
        0
    ]
    return pd.Series(
        license_df["License identifier (to use in repo card)"].values,
        index=license_df.Fullname,
    ).to_dict()


def task_selector_page():
    st.header("Select Model Task")
    st.radio(
        "Choose the model type:",
        ["Image-to-Image translation", "Segmentation", "Dose prediction"],
        key=persist("task"),
        index=0,
    )
    if st.button("Continue"):
        page_switcher(card_metadata_render)
        st.rerun()


def extract_evaluations_from_state():
    evaluations = []
    for i in range(len(st.session_state.evaluation_forms)):
        prefix = f"evaluation_{i}_"
        entry = {}
        for key, value in st.session_state.items():
            if key.startswith(prefix):
                field = key[len(prefix) :]
                entry[field] = value
        evaluations.append(entry)
    return evaluations


def main_page():
    sidebar_render()

    get_cached_data()

    """ missing_required = utils.validate_required_fields(
        model_card_schema, st.session_state, current_task=task
    )

    if missing_required:
        st.warning(
            "Warning: The following required fields are missing:\n\n"
            + "\n".join([f"- {field}" for field in missing_required])
        ) """


def page_switcher(page):
    st.session_state.runpage = page


def main():
    st.header("About Model Cards")
    about_path = Path("about.md")
    if about_path.exists():
        st.markdown(about_path.read_text(), unsafe_allow_html=True)
    else:
        st.error(
            "The file 'about.md' is missing. Please ensure it exists in the current working directory."
        )

    if st.button("Create a Model Card 📝"):
        page_switcher(task_selector_page)
        st.rerun()


if __name__ == "__main__":
    if "runpage" not in st.session_state:
        st.session_state.runpage = main
    st.session_state.runpage()

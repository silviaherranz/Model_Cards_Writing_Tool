from pathlib import Path
import pandas as pd
import streamlit as st
from template_base import SCHEMA, DATA_INPUT_OUTPUT_TS, TASK_METRIC_MAP, EVALUATION_METRIC_FIELDS
import utils
import json


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

    if "task" not in st.session_state:
        selected_task = st.radio(
            "Select the task for your model card",
            ["Image-to-Image translation", "Segmentation", "Dose prediction", "Other"],
            key="task_temp",
        )

        if st.button("Continue"):
            st.session_state["task"] = selected_task
            from custom_pages.card_metadata import card_metadata_render

            st.session_state.runpage = card_metadata_render
            st.rerun()
    else:
        st.success(f"Task already selected: **{st.session_state['task']}**")

def load_model_card_page():
    st.header("Load a Model Card")
    st.markdown(
    "<p style='font-size:18px; font-weight:450;'>Upload a <code>.json</code> model card</p>",
    unsafe_allow_html=True
    )
    uploaded_file = st.file_uploader(".", type=["json"], label_visibility="hidden")
    #uploaded_file = st.file_uploader("Upload a `.json` model card", type=["json"])
    st.info("Only `.json` files are supported. Please ensure your file is in the correct format.")
    if uploaded_file:
        try:
            json_data = json.load(uploaded_file)
            utils.populate_session_state_from_json(json_data)
            st.success("Model card loaded successfully!")
            # Redirigir a la primera sección
            from custom_pages.card_metadata import card_metadata_render
            st.session_state.runpage = card_metadata_render
            st.rerun()
        except Exception as e:
            st.error(f"Error loading file: {e}")

#IDEA: max_archs = len(st.session_state.get("learning_architecture_forms", {})) guardar dinámicamente el número de Learning architectures que hay

def extract_learning_architectures_from_state(max_archs=100):
    learning_architectures = []

    for i in range(max_archs):
        prefix = f"learning_architecture_{i}_"
        entry = {}
        for key, value in st.session_state.items():
            if key.startswith(prefix):
                field = key[len(prefix):]
                entry[field] = value
        if entry:
            entry["id"] = i
            learning_architectures.append(entry)

    return learning_architectures

def extract_evaluations_from_state():
    evaluations = []
    eval_forms = st.session_state.get("evaluation_forms", [])
    task = st.session_state.get("task", "Other")

    for name in eval_forms:
        slug = name.replace(" ", "_")
        prefix = f"evaluation_{slug}_"
        nested_prefix = f"evaluation_{slug}."
        evaluation = {"name": name}

        # General evaluation fields
        for field in SCHEMA.get("evaluation_data", []):
            key = prefix + field
            evaluation[field] = st.session_state.get(key, "")

        # Inputs/outputs technical characteristics
        modality_entries = []
        for key, value in st.session_state.items():
            if key.endswith("model_inputs") and isinstance(value, list):
                for item in value:
                    modality_entries.append({"modality": item, "source": "model_inputs"})
            elif key.endswith("model_outputs") and isinstance(value, list):
                for item in value:
                    modality_entries.append({"modality": item, "source": "model_outputs"})

        io_details = []
        for entry in modality_entries:
            clean = entry["modality"].strip().replace(" ", "_").lower()
            source = entry["source"]
            detail = {
                "input_content": entry["modality"],
                "source": source
            }
            for field in DATA_INPUT_OUTPUT_TS:
                key = f"{prefix}{clean}_{source}_{field}"
                val = (
                    st.session_state.get(key)
                    or st.session_state.get(f"_{key}")
                    or st.session_state.get(f"__{key}")
                    or ""
                )
                detail[field] = val
            io_details.append(detail)

        evaluation["inputs_outputs_technical_specifications"] = io_details

        # Metrics per task
        for metric_key in TASK_METRIC_MAP.get(task, []):
            type_list_key = f"{prefix}{metric_key}_list"
            metric_entries = st.session_state.get(type_list_key, [])
            evaluation[metric_key] = []

            for metric_name in metric_entries:
                entry = {"name": metric_name}
                for field in EVALUATION_METRIC_FIELDS[metric_key]:
                    full_key = f"{nested_prefix}{metric_name}_{field}"
                    entry[field] = st.session_state.get(full_key, "")
                evaluation[metric_key].append(entry)

        evaluations.append(evaluation)

    return evaluations



def main_page():
    from side_bar import sidebar_render
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
    st.markdown("""
    <div style='text-align: justify; font-size: 16px;'>
    This is a tool to generate Model Cards. It aims to provide a simple interface to build from scratch a new model card or to edit an existing one. The generated model card can be downloaded or directly pushed to your model hosted on the Hub. 
    Please use <a href='https://huggingface.co/spaces/huggingface/Model_Cards_Writing_Tool/discussions' target='_blank'>the Community tab</a> to give us some feedback.
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    # about_path = Path("about.md")
    # if about_path.exists():
    #     st.markdown(about_path.read_text(), unsafe_allow_html=True)
    # else:
    #     st.error(
    #         "The file 'about.md' is missing. Please ensure it exists in the current working directory."
    #     )
    col1, col2 = st.columns([3.4, 1])
    with col1:
        if st.button("Create a Model Card"):
            page_switcher(task_selector_page)
            st.rerun()
    with col2:
        if st.button("Load a Model Card"):
            page_switcher(load_model_card_page)
            st.rerun()


if __name__ == "__main__":
    if "runpage" not in st.session_state:
        st.session_state.runpage = main
    st.session_state.runpage()

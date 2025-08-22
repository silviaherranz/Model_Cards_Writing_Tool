import pandas as pd
import streamlit as st
from json_template import (
    SCHEMA,
    DATA_INPUT_OUTPUT_TS,
    TASK_METRIC_MAP,
    EVALUATION_METRIC_FIELDS,
)
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
    if "task" not in st.session_state:
        st.markdown("""
            <style>
            /* Contenedor central de todo el bloque */
            .radio-center {
                display: flex;
                flex-direction: column;
                align-items: center;
                width: 100%;
            }
            /* Caja de opciones centrada */
            div[role="radiogroup"] {
                background-color: #f9f9f9;
                padding: 1rem 2rem;
                border-radius: 10px;
                border: 1px solid #ddd;
                display: inline-block;
                text-align: left;
                margin: auto; /* Centra horizontalmente */
            }
            /* Texto de las opciones */
            label[data-baseweb="radio"] > div:first-child {
                font-size: 16px !important;
                padding: 4px 0;
            }
            /* Opción seleccionada */
            div[role="radiogroup"] input:checked + div {
                color: #1E88E5 !important;
                font-weight: bold;
            }
            /* Espaciado entre opciones */
            label[data-baseweb="radio"] {
                margin-bottom: 6px;
            }
            </style>
        """, unsafe_allow_html=True)

        # Contenedor central
        st.markdown("<div class='radio-center'>", unsafe_allow_html=True)

        # Título centrado
        st.markdown(
            "<h2 style='text-align: center;'>Select the task for your Model Card</h2>",
            unsafe_allow_html=True
        )


        left, center, right = st.columns([1, 2, 1])

        with center:
        # Radio centrado
            selected_task = st.radio(
                ".",
                ["Image-to-Image translation", "Segmentation", "Dose prediction", "Other"],
                key="task_temp",
                label_visibility="hidden"
            )

        st.markdown("</div>", unsafe_allow_html=True)


        if st.button("Continue", use_container_width=True):
            st.session_state["task"] = selected_task
            from custom_pages.model_card_info import model_card_info_render

            st.session_state.runpage = model_card_info_render
            st.rerun()
        if st.button("Return to Main Page", use_container_width=True):
            st.session_state.runpage = main
            st.rerun()
    else:
        st.success(f"Task already selected: **{st.session_state['task']}**")


def load_model_card_page():
    st.header("Load a Model Card")

    st.markdown(
        "<p style='font-size:18px; font-weight:450;'>Upload a <code>.json</code> model card</p>",
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Upload your model card (.json)", type=["json"], label_visibility="collapsed"
    )

    st.info(
        "Only `.json` files are supported. Please ensure your file is in the correct format."
    )

    if uploaded_file:
        st.success("File uploaded. Click the button below to load it.")

        if st.button("Load Model Card", use_container_width=True):
            with st.spinner("Parsing and loading model card..."):
                content = uploaded_file.read().decode("utf-8")
                json_data = json.loads(content)
                utils.populate_session_state_from_json(json_data)
                from custom_pages.card_metadata import card_metadata_render

                st.session_state.runpage = card_metadata_render
                st.success("Model card loaded successfully!")
                st.rerun()

    if st.button("Return to Main Page", use_container_width=True):
        st.session_state.runpage = main
        st.rerun()


def extract_learning_architectures_from_state(max_archs=100):
    learning_architectures = []

    for i in range(max_archs):
        prefix = f"learning_architecture_{i}_"
        entry = {}
        for key, value in st.session_state.items():
            if key.startswith(prefix):
                field = key[len(prefix) :]
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

        eval_section = SCHEMA.get("evaluation_data", {})

        if isinstance(eval_section, dict):
            iter_fields = []
            for field, props in eval_section.items():
                allowed_tasks = props.get("model_types")
                if allowed_tasks is None or task in allowed_tasks:
                    iter_fields.append(field)
        else:
            # fallback por si viniera como lista
            iter_fields = list(eval_section or [])

        for field in iter_fields:
            key = prefix + field
            if field.startswith("evaluated_by_") and field in evaluation:
                continue
            evaluation[field] = st.session_state.get(key, "")
            if evaluation.get("evaluated_same_as_approved", False):
                evaluation["evaluated_by_name"] = st.session_state.get(
                    "model_basic_information_clearance_approved_by_name", ""
                )
                evaluation["evaluated_by_institution"] = st.session_state.get(
                    "model_basic_information_clearance_approved_by_institution", ""
                )
                evaluation["evaluated_by_contact_email"] = st.session_state.get(
                    "model_basic_information_clearance_approved_by_contact_email", ""
                )
        q_prefix = f"{prefix}qualitative_evaluation_"

        def qget(suffix, default=""):
            return (
                st.session_state.get(q_prefix + suffix, None)
                or st.session_state.get("_" + q_prefix + suffix, None)
                or st.session_state.get("__" + q_prefix + suffix, None)
                or default
            )

        qualitative = {
            "evaluators_information": qget("evaluators_information", ""),
            "likert_scoring": {
                "method": qget("likert_scoring_method", ""),
                "results": qget("likert_scoring_results", ""),
            },
            "turing_test": {
                "method": qget("turing_test_method", ""),
                "results": qget("turing_test_results", ""),
            },
            "time_saving": {
                "method": qget("time_saving_method", ""),
                "results": qget("time_saving_results", ""),
            },
            "other": {
                "method": qget("other_method", ""),
                "results": qget("other_results", ""),
            },
            "explainability": qget("explainability", ""),
            "citation_details": qget("citation_details", ""),
        }

        evaluation["qualitative_evaluation"] = qualitative
        modality_entries = []
        for key, value in st.session_state.items():
            if key.endswith("model_inputs") and isinstance(value, list):
                for item in value:
                    modality_entries.append(
                        {"modality": item, "source": "model_inputs"}
                    )
            elif key.endswith("model_outputs") and isinstance(value, list):
                for item in value:
                    modality_entries.append(
                        {"modality": item, "source": "model_outputs"}
                    )

        io_details = []
        for entry in modality_entries:
            clean = entry["modality"].strip().replace(" ", "_").lower()
            source = entry["source"]
            detail = {"entry": entry["modality"], "source": source}
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

        evaluation = utils.insert_after(
            evaluation,
            "inputs_outputs_technical_specifications",
            io_details,
            "url_info",
        )

        metric_dic = {}
        for metric_key in TASK_METRIC_MAP.get(task, []):
            type_list_key = f"{prefix}{metric_key}_list"
            metric_entries = st.session_state.get(type_list_key, [])
            metric_dic[metric_key] = []

            for metric_name in metric_entries:
                entry = {"name": metric_name}
                for field in EVALUATION_METRIC_FIELDS[metric_key]:
                    full_key = f"{nested_prefix}{metric_name}_{field}"
                    entry[field] = st.session_state.get(full_key, "")
                metric_dic[metric_key].append(entry)
        
        evaluation = utils.insert_dict_after(
            evaluation,
            metric_dic,
            "additional_patient_info_ev",
        )

        evaluations.append(evaluation)

    return evaluations


def main_page():
    from side_bar import sidebar_render

    sidebar_render()

    get_cached_data()


def page_switcher(page):
    st.session_state.runpage = page


def main():
    st.markdown("""
        <style>
        .block-container p, .block-container li {
            text-align: justify;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("## About Model Cards")

    st.markdown("""
    This model card aims to **enhance transparency and standardize the reporting of artificial intelligence (AI)-based applications** in the field of **Radiation Therapy**. It is designed for use by professionals in both research and clinical settings to support these objectives. Although it includes items useful for current regulatory requirements, **it does not replace or fulfill regulatory requirements such as the EU Medical Device Regulation or equivalent standards**.
    """)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Create a Model Card", use_container_width=True):
        page_switcher(task_selector_page)
        st.rerun()

    if st.button("Load a Model Card", use_container_width=True):
        page_switcher(load_model_card_page)
        st.rerun()


if __name__ == "__main__":
    if "runpage" not in st.session_state:
        st.session_state.runpage = main
    st.session_state.runpage()
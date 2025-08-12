import streamlit as st
from huggingface_hub import upload_file
from io_utils import save_uploadedfile, upload_json_card, upload_readme_card
import tempfile
from pathlib import Path
import json
from custom_pages.other_considerations import other_considerations_render
from readme_builder import build_readme_from_card
from template_base import SCHEMA
import utils
from middleMan import parse_into_json
from custom_pages.card_metadata import card_metadata_render
from custom_pages.model_basic_information import model_basic_information_render
from custom_pages.technical_specifications import technical_specifications_render
from custom_pages.training_data import training_data_render
from custom_pages.evaluation_data_mrc import evaluation_data_mrc_render
from custom_pages.warnings import warnings_render
from custom_pages.appendix import appendix_render
import time

import validation_utils

model_card_schema = utils.get_model_card_schema()

def sidebar_render():
    with st.sidebar:
        # Apply CSS for all buttons inside the sidebar container
        st.markdown("""
        <style>
        /* Style Streamlit buttons inside sidebar */
        section[data-testid="stSidebar"] button {
            width: 100% !important;
            text-align: left !important;
            padding: 0.5rem 1rem !important;
            border: 1px solid #ccc !important;
            border-radius: 6px !important;
            background-color: #ffffff !important;
            color: #000 !important;
            margin-bottom: 10px;
            font-size: 14px;
            font-weight: 500;
        }

        section[data-testid="stSidebar"] button:hover {
            background-color: #e0f0ff !important;
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown("## Menu")

        if st.button("Card Metadata"):
            st.session_state.runpage = card_metadata_render
            st.rerun()
        
        if st.button("Model Basic Information"):
            st.session_state.runpage = model_basic_information_render
            st.rerun()
        
        if st.button("Technical Specifications"):
            st.session_state.runpage = technical_specifications_render
            st.rerun()

        if st.button("Training Data Methodology and Information"):
            st.session_state.runpage = training_data_render
            st.rerun()

        if st.button("Evaluation Data Methodology, Results and Commissioning"):
            st.session_state.runpage = evaluation_data_mrc_render
            st.rerun()
        
        if st.button("Other Considerations"):
            st.session_state.runpage = other_considerations_render
            st.rerun()

        if st.button("Appendix"):
            st.session_state.runpage = appendix_render
            st.rerun()

        task = st.session_state.get("task", "Image-to-Image translation")
        if validation_utils.validate_required_fields(model_card_schema, st.session_state, current_task=task):
            if st.button("Warnings"):
                st.session_state.runpage = warnings_render
                st.rerun()

        st.markdown("## Model Card Builder")
        st.markdown("""
        <style>
        /* Make tab headers flat with white background */
        .stTabs [role="tablist"] {
        background: #fff;
        border-bottom: 1px solid #e5e7eb; /* light gray line under tabs */
        padding: 4px 0;
        gap: 0.75rem;
        }

        /* Each tab "button" -> flat link style */
        .stTabs [role="tab"] {
        background: #fff !important;
        border: none !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        padding: 6px 8px;
        margin: 0;
        color: #374151; /* neutral text */
        }

        /* Hover state: keep it flat */
        .stTabs [role="tab"]:hover {
        background: #fff !important;
        color: #111827;
        }

        /* Active tab: underline only */
        .stTabs [role="tab"][aria-selected="true"] {
        background: #fff !important;
        color: #111827;
        border-bottom: 2px solid #ef4444; /* change to your brand color */
        }

        /* Optional: remove the little focus ring outline if you don't want it */
        .stTabs [role="tab"]:focus { outline: none; box-shadow: none; }
        </style>
        """, unsafe_allow_html=True)

        tab_local, tab_readme, tab_export = st.tabs(
            ["Local downloads", "README tools", "Export to Hub"]
        )

        # ------------------------------
        # TAB 1 — README tools
        # ------------------------------
        with tab_readme:

            # Generate README
            task = st.session_state.get("task")
            _ = validation_utils.validate_required_fields(SCHEMA, st.session_state, current_task=task)

            if "last_readme_text" not in st.session_state:
                st.session_state.last_readme_text = None

            with st.form("form_generate_readme"):
                gen_readme = st.form_submit_button("Generate README.md")
                if gen_readme:
                    try:
                        card_content = parse_into_json(SCHEMA)
                        card_obj = json.loads(card_content) if isinstance(card_content, str) else card_content
                        st.session_state.last_readme_text = build_readme_from_card(card_obj)
                        st.success("README built successfully. Use the download button below.")
                    except Exception as e:
                        st.session_state.last_readme_text = None
                        st.error(f"Could not build README: {e}")

            if st.session_state.last_readme_text:
                st.download_button(
                    "Download README.md",
                    data=st.session_state.last_readme_text.encode("utf-8"),
                    file_name="README.md",
                    mime="text/markdown",
                    use_container_width=True,
                    key="btn_download_readme",
                )
                with st.expander("Preview README.md", expanded=False):
                    st.text_area("README.md", value=st.session_state.last_readme_text, height=300, key="ta_readme_preview")

            st.markdown("## Export README.md to Hub")

            with st.form("form_upload_readme_hub"):
                st.markdown("Use a token with write access from [here](https://hf.co/settings/tokens)")
                token_rm = st.text_input("Token", type="password", key="token_rm_hub")
                repo_id_rm = st.text_input("Repo ID (e.g. user/repo)", key="repo_id_rm_hub")
                push_rm = st.form_submit_button("Upload README.md to Hub")

            if push_rm:
                if len(repo_id_rm.split("/")) == 2:
                    try:
                        card_content = parse_into_json(SCHEMA)
                        card_obj = json.loads(card_content) if isinstance(card_content, str) else card_content
                        readme_text = build_readme_from_card(card_obj)
                        new_url = upload_readme_card(readme_text, repo_id_rm, token_rm)
                        st.success(f"Pushed the README to the repo [here]({new_url})!")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                else:
                    st.error("Repo ID invalid. It should be username/repo-name. For example: nateraw/food")

        # ------------------------------
        # TAB 2 — Local downloads (JSON / PDF)
        # ------------------------------
        with tab_local:
            st.markdown("## Download Model Card")

            with st.expander("Download Options", expanded=True):
                # JSON
                with st.form("form_download_json"):
                    download_submit = st.form_submit_button("Download Model Card as `.json`")
                    if download_submit:
                        if st.session_state.get("format_error"):
                            st.error("Cannot download — there are fields with invalid format.")
                        else:
                            missing_required = validation_utils.validate_required_fields(
                                model_card_schema, st.session_state, current_task=st.session_state.get("task")
                            )
                            st.session_state.download_ready = True  # allow download even if missing_required
                            if missing_required:
                                st.error("Some required fields are missing. Check the Warnings section on the sidebar for details.")

                if st.session_state.get("download_ready"):
                    card_content = parse_into_json(SCHEMA)
                    st.download_button(
                        "Your download is ready — click here (JSON)",
                        data=card_content,
                        file_name="model_card.json",
                        mime="application/json",
                        key="btn_download_json",
                    )
                    st.session_state.download_ready = False

                # PDF
                with st.form("form_download_pdf"):
                    pdf_submit = st.form_submit_button("Download Model Card as `.pdf`")
                    if pdf_submit:
                        if st.session_state.get("format_error"):
                            st.error("Cannot download — there are fields with invalid format.")
                        else:
                            missing_required = validation_utils.validate_required_fields(
                                model_card_schema, st.session_state, current_task=st.session_state.get("task")
                            )
                            card_data = parse_into_json(SCHEMA)
                            if isinstance(card_data, str):
                                card_data = json.loads(card_data)
                            utils.export_json_pretty_to_pdf("model_card_schema.json")
                            st.session_state.download_ready_pdf = True
                            if missing_required:
                                st.error("Some required fields are missing. Check the Warnings section on the sidebar for details.")

                if st.session_state.get("download_ready_pdf"):
                    with open("output.pdf", "rb") as f:
                        st.download_button(
                            "Your download is ready — click here (PDF)",
                            f,
                            file_name="model_card.pdf",
                            use_container_width=True,
                            key="btn_download_pdf",
                        )
                    st.session_state.download_ready_pdf = False

        # ------------------------------
        # TAB 3 — Export to Hub
        # ------------------------------
        with tab_export:
            # (If you want the JSON uploader here, keep it; otherwise remove)
            uploaded_file = st.file_uploader(
                "Choose a JSON file", type=[".json"],
                help="Choose a JSON (.json) file to upload",
                key="uploader_json_tab1",
            )
            if uploaded_file is not None:
                name_of_uploaded_file = save_uploadedfile(uploaded_file)
                st.session_state.markdown_upload = name_of_uploaded_file
                st.success(f"File {uploaded_file.name} saved successfully.")

            st.markdown("## Export Loaded Model Card to Hub (.json)")
            with st.form("form_upload_json_hub"):
                st.markdown("Use a token with write access from [here](https://hf.co/settings/tokens)")
                token_json = st.text_input("Token", type="password", key="token_json_hub")
                repo_id_json = st.text_input("Repo ID (e.g. user/repo)", key="repo_id_json_hub")
                submit_json = st.form_submit_button("Upload .json to Hub")

            if submit_json:
                if len(repo_id_json.split("/")) == 2:
                    try:
                        json_path = st.session_state.get("markdown_upload")
                        if not json_path:
                            st.error("Please upload a .json file in the README tools tab first.")
                        else:
                            with open(json_path, "r") as json_file:
                                model_card = json.load(json_file)
                            new_url = upload_json_card(model_card, repo_id_json, token_json)
                            st.success(f"Pushed the card to the repo [here]({new_url})!")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                else:
                    st.error("Repo ID invalid. It should be username/repo-name. For example: nateraw/food")


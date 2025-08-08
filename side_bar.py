import streamlit as st
from huggingface_hub import upload_file, create_repo
import tempfile
from pathlib import Path
import json
from custom_pages.other_considerations import other_considerations_render
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

model_card_schema = utils.get_model_card_schema()

def card_upload(card_info, repo_id, token):
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir) / "README.md"
        tmp_path.write_text(
            json.dumps(card_info) if isinstance(card_info, dict) else str(card_info)
        )
        url = upload_file(
            path_or_fileobj=str(tmp_path),
            path_in_repo="README.md",
            repo_id=repo_id,
            token=token,
            repo_type="model",
        )
    return url

def save_uploadedfile(uploadedfile):
    import time

    unique_name = f"{int(time.time())}_{uploadedfile.name}"
    with open(unique_name, "wb") as f:
        f.write(uploadedfile.getbuffer())
    st.success(f"Saved File: {unique_name} to temp dir")
    return unique_name

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

        st.markdown("##  Menu")

        if st.button("Card Metadata"):
            st.session_state.runpage = card_metadata_render
            st.rerun()
        
        if st.button("Model Basic Information"):
            st.session_state.runpage = model_basic_information_render
            st.rerun()
        
        if st.button("Technical Specifications"):
            st.session_state.runpage = technical_specifications_render
            st.rerun()

        if st.button("Training Data Methodology, Results & Commissioning"):
            st.session_state.runpage = training_data_render
            st.rerun()
        
        if st.button("Evaluation Data Methodology, Results & Commissioning"):
            st.session_state.runpage = evaluation_data_mrc_render
            st.rerun()
        
        if st.button("Other Considerations"):
            st.session_state.runpage = other_considerations_render
            st.rerun()

        if st.button("Appendix"):
            st.session_state.runpage = appendix_render
            st.rerun()

        task = st.session_state.get("task", "Image-to-Image translation")
        if utils.validate_required_fields(model_card_schema, st.session_state, current_task=task):
            if st.button("Warnings"):
                st.session_state.runpage = warnings_render
                st.rerun()

        ######################################################
        ### Uploading a model card from local drive
        ######################################################

     
        # Código Streamlit para interactuar con el usuario

        st.markdown("## Upload Model Card")

        # Subir un archivo JSON
        uploaded_file = st.file_uploader("Choose a file", type=['.json'], help='Choose a JSON (.json) file to upload')

        if uploaded_file is not None:
            # Guardamos el archivo subido en el directorio local
            name_of_uploaded_file = save_uploadedfile(uploaded_file)
            st.session_state.markdown_upload = name_of_uploaded_file

            st.success(f"Archivo {uploaded_file.name} guardado correctamente.")

            # Exportar la tarjeta de modelo cargada al Hub
            st.markdown("## Export Loaded Model Card to Hub")
            with st.form("Upload to 🤗 Hub"):
                st.markdown("Use a token with write access from [here](https://hf.co/settings/tokens)")
                token = st.text_input("Token", type='password')
                repo_id = st.text_input("Repo ID")
                submit = st.form_submit_button('Upload to 🤗 Hub', help='The current model card will be uploaded to a branch in the supplied repo')

            if submit:
                # Validación de Repo ID
                if len(repo_id.split('/')) == 2:
                    try:
                        # Cargar la tarjeta de modelo
                        with open(name_of_uploaded_file, "r") as json_file:
                            model_card = json.load(json_file)

                        # Subir el archivo .json al Hugging Face Hub
                        new_url = card_upload(model_card, repo_id, token)

                        st.success(f"Pushed the card to the repo [here]({new_url})!")  # Éxito, mostrar URL

                    except Exception as e:
                        st.error(f"Error: {str(e)}")  # Mostrar error si algo sale mal
                else:
                    st.error("Repo ID invalid. It should be username/repo-name. For example: nateraw/food")


        with st.expander("Download Options", expanded=True):
            task = st.session_state.get("task")

            missing_required = utils.validate_required_fields(SCHEMA, st.session_state, current_task=task)

            with st.form("Download model card as json"):
                download_submit = st.form_submit_button("Download Model Card as `.json`")
                if download_submit:
                    task = st.session_state.get("task")
                    missing_required = utils.validate_required_fields(
                        model_card_schema, st.session_state, current_task=task
                    )
                    if missing_required:
                        st.session_state.download_ready = True
                    st.error(
                        "There are some fields missing, check the Warnings section on the sidebar for more information."
                    )
            if st.session_state.get("download_ready"):
                card_content = parse_into_json(SCHEMA)
                st.download_button(
                    "Your download is ready — click here (JSON)",
                    data=card_content,
                    file_name="model_card.json",
                    mime="application/json",
                )
                st.session_state.download_ready = False

            with st.form("Download model card as pdf"):
                pdf_submit = st.form_submit_button("Download Model Card as `.pdf`")
                if pdf_submit:
                    task = st.session_state.get("task")
                    missing_required = utils.validate_required_fields(
                        model_card_schema, st.session_state, current_task=task
                    )

                    card_data = parse_into_json(SCHEMA)
                    if isinstance(card_data, str):
                        card_data = json.loads(card_data)

                    utils.export_json_pretty_to_pdf("model_card_schema.json")
                    st.session_state.download_ready_pdf = True

                    if missing_required:
                        st.error(
                            "There are some fields missing, check the Warnings section on the sidebar for more information."
                        )

            if st.session_state.get("download_ready_pdf"):
                with open("output.pdf", "rb") as f:
                    st.download_button(
                        "Your download is ready — click here (PDF)",
                        f,
                        file_name="model_card.pdf",
                        use_container_width=True,
                    )
                st.session_state.download_ready_pdf = False
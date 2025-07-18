import streamlit as st
from huggingface_hub import upload_file, create_repo
import tempfile
from pathlib import Path
import json
import utils
from middleMan import parse_into_jinja_markdown as pj
from custom_pages.card_metadata import card_metadata_render
from custom_pages.model_basic_information import model_basic_information_render
from custom_pages.technical_specifications import technical_specifications_render
from custom_pages.evaluation_data_mrc import evaluation_data_mrc_render
from custom_pages.warnings import warnings_render

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
        task = st.session_state.get("task", "Image-to-Image translation")

        st.markdown("## 🔀 Navigate")

        if st.button("📝 Card Metadata"):
            st.session_state.runpage = card_metadata_render
            st.rerun()
        
        if st.button("🧠 Model Basic Information"):
            st.session_state.runpage = model_basic_information_render
            st.rerun()
        
        if st.button("🔎 Technical Specifications"):
            st.session_state.runpage = technical_specifications_render
            st.rerun()
        
        if st.button("🔬 Evaluation Data Methodology, Results & Commissioning"):
            st.session_state.runpage = evaluation_data_mrc_render
            st.rerun()


        missing_required = utils.validate_required_fields(
            model_card_schema, st.session_state, current_task=task
        )

        if missing_required:
            if st.button("⚠️ Warnings"):
                st.session_state.runpage = warnings_render
                st.rerun()
            

        st.markdown("## Upload Model Card")
        uploaded_file = st.file_uploader(
            "Choose a file", type=["md"], help="Upload a markdown (.md) file"
        )
        if uploaded_file:
            st.session_state.markdown_upload = save_uploadedfile(uploaded_file)
        else:
            st.session_state.markdown_upload = "current_card.md"

        try:
            out_markdown = Path(st.session_state.markdown_upload).read_text()
        except FileNotFoundError:
            st.error(
                f"File {st.session_state.markdown_upload} not found. Please upload a valid file."
            )
            out_markdown = ""

        st.markdown("## Export Loaded Model Card to Hub")
        with st.form("Upload to 🤗 Hub"):
            token = st.text_input("Token", type="password")
            repo_id = st.text_input("Repo ID")
            submit = st.form_submit_button("Upload to 🤗 Hub")

        if submit:
            task = st.session_state.get("task")
            missing_required = utils.validate_required_fields(
                model_card_schema, st.session_state, current_task=task
            )
            if missing_required:
                st.error(
                    "Please complete the required fields:\n\n"
                    + "\n".join([f"- {field}" for field in missing_required])
                )
            elif len(repo_id.split("/")) == 2:
                create_repo(repo_id, exist_ok=True, token=token)
                card_content = pj(st.session_state)
                new_url = card_upload(card_content, repo_id, token=token)
                st.success(f"Pushed the card to the repo [here]({new_url})!")
            else:
                st.error("Repo ID invalid. It should be username/repo-name.")

        if "show_download" not in st.session_state:
            st.session_state.show_download = False

        st.markdown("## Download Model Card `.md`")
        with st.form("Download model card form"):
            download_submit = st.form_submit_button("📥 Download Model Card")
            if download_submit:
                task = st.session_state.get("task")
                missing_required = utils.validate_required_fields(
                    model_card_schema, st.session_state, current_task=task
                )
                if missing_required:
                    st.session_state.show_download = False
                    st.error(
                        "The following required fields are missing:\n\n"
                        + "\n".join([f"- {field}" for field in missing_required])
                    )
                else:
                    st.session_state.show_download = True

        if st.session_state.get("show_download"):
            card_content = pj(st.session_state)
            st.download_button(
                "📥 Click here to download",
                data=card_content,
                file_name="model_card.md",
                mime="text/markdown",
            )
        
        for key, value in {
            "model_name": "",
            "license": "",
            "markdown_upload": "current_card.md",
        }.items():
            st.session_state.setdefault(key, value)

        st.markdown("## Download Model Card `.json`")
        with st.form("Download model card json"):
            download_submit = st.form_submit_button("📥 Download Model Card")
            if download_submit:
                task = st.session_state.get("task")
                missing_required = utils.validate_required_fields(
                    model_card_schema, st.session_state, current_task=task
                )
                if missing_required:
                    st.session_state.show_download = False
                    st.error(
                        "The following required fields are missing:\n\n"
                        + "\n".join([f"- {field}" for field in missing_required])
                    )
                else:
                    st.session_state.show_download = True
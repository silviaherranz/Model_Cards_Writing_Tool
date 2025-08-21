import io
import os
from pathlib import Path
import zipfile
import streamlit as st
from custom_pages.model_card_info import model_card_info_render
from io_utils import save_uploadedfile, upload_json_card, upload_readme_card
import json
from custom_pages.other_considerations import other_considerations_render
from md_renderer import render_full_model_card_md
from readme_builder import render_hf_readme, upload_readme_to_hub
from json_template import SCHEMA
import utils
import validation_utils
from middleMan import parse_into_json
from custom_pages.card_metadata import card_metadata_render
from custom_pages.model_basic_information import model_basic_information_render
from custom_pages.technical_specifications import technical_specifications_render
from custom_pages.training_data import training_data_render
from custom_pages.evaluation_data_mrc import evaluation_data_mrc_render
from custom_pages.warnings import warnings_render
from custom_pages.appendix import appendix_render

model_card_schema = utils.get_model_card_schema()

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

SIDEBAR_WIDTH_PX = 500


def sidebar_render():
    with st.sidebar:
        st.markdown(
            """
            <style>
            /* Sidebar responsive que respeta el estado expandido/colapsado */
            [data-testid="stSidebar"][aria-expanded="true"] {
            width: clamp(260px, 26vw, 500px) !important;  /* entre 260 y 500 */
            min-width: 260px !important;
            }
            [data-testid="stSidebar"][aria-expanded="false"] {
            width: 0 !important;
            min-width: 0 !important;
            }

            /* Botones: ocupan todo el ancho disponible del sidebar */
            [data-testid="stSidebar"] .stButton > button,
            [data-testid="stSidebar"] [data-testid="baseButton-primary"],
            [data-testid="stSidebar"] [data-testid="baseButton-secondary"] {
            width: 100% !important;
            text-align: left !important;
            padding: 0.6rem 1rem !important;
            border: 1px solid #d1d5db !important;
            border-radius: 8px !important;
            background: #ffffff !important;
            color: #111827 !important;
            margin-bottom: 10px !important;
            box-shadow: none !important;
            }
            [data-testid="stSidebar"] .stButton > button:hover,
            [data-testid="stSidebar"] [data-testid="baseButton-primary"]:hover,
            [data-testid="stSidebar"] [data-testid="baseButton-secondary"]:hover {
            background: #e0f0ff !important;
            }

            /* En pantallas pequeñas, limita aún más el ancho */
            @media (max-width: 1024px) {
            [data-testid="stSidebar"][aria-expanded="true"] {
                width: 260px !important;
            }
            }
            </style>
            """,
            unsafe_allow_html=True,
        )


        if st.button("About Model Cards", use_container_width=True):
            st.session_state.runpage = model_card_info_render
            st.rerun()

        st.markdown("## Menu")

        if st.button("Card Metadata", use_container_width=True):
            st.session_state.runpage = card_metadata_render
            st.rerun()

        if st.button("Model Basic Information", use_container_width=True):
            st.session_state.runpage = model_basic_information_render
            st.rerun()

        if st.button("Technical Specifications", use_container_width=True):
            st.session_state.runpage = technical_specifications_render
            st.rerun()

        if st.button("Training Data Methodology and Information", use_container_width=True):
            st.session_state.runpage = training_data_render
            st.rerun()

        if st.button("Evaluation Data Methodology, Results and Commissioning", use_container_width=True):
            st.session_state.runpage = evaluation_data_mrc_render
            st.rerun()

        if st.button("Other Considerations", use_container_width=True):
            st.session_state.runpage = other_considerations_render
            st.rerun()

        if st.button("Appendix", use_container_width=True):
            st.session_state.runpage = appendix_render
            st.rerun()

        task = st.session_state.get("task", "Image-to-Image translation")
        if validation_utils.validate_required_fields(
            model_card_schema, current_task=task
        ):
            if st.button("Warnings"):
                st.session_state.runpage = warnings_render
                st.rerun()

        st.markdown("## Model Card Builder")
        st.markdown(
            """
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
        """,
            unsafe_allow_html=True,
        )

        utils.enlarge_tab_titles(16)
        tab_local, tab_readme, tab_export = st.tabs(
            ["Local downloads", "README tools", "Export to Hub"]
        )

        # ------------------------------
        # TAB 1 — README tools
        # ------------------------------
        with tab_readme:
            task = st.session_state.get("task")
            _ = validation_utils.validate_required_fields(
                SCHEMA, current_task=task
            )

            if "last_readme_text" not in st.session_state:
                st.session_state.last_readme_text = None

            # -------------------------
            # Generate README.md (text)
            # -------------------------
            with st.form("form_generate_readme"):
                gen_readme = st.form_submit_button("Generate README.md")
                if gen_readme:
                    try:
                        # You can still parse/validate your card; not strictly required for README rendering
                        _ = parse_into_json(SCHEMA)

                        # Use our new renderer (auto-fills from session_state as discussed)
                        st.session_state.last_readme_text = render_hf_readme()
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
                    st.text_area(
                        "README.md",
                        value=st.session_state.last_readme_text,
                        height=300,
                        key="ta_readme_preview",
                    )

            # -------------------------
            # Push README.md to the Hub
            # -------------------------
            st.markdown("## Export README.md to Hub")

            with st.form("form_upload_readme_hub"):
                st.markdown("Use a token with write access from [here](https://hf.co/settings/tokens)")
                token_rm = st.text_input("Token", type="password", key="token_rm_hub")
                repo_id_rm = st.text_input("Repo ID (e.g. user/repo)", key="repo_id_rm_hub")
                push_rm = st.form_submit_button("Upload README.md to Hub")

            if push_rm:
                if len(repo_id_rm.split("/")) == 2:
                    try:
                        # Ensure we have fresh README text if user skipped the Generate step
                        if not st.session_state.last_readme_text:
                            st.session_state.last_readme_text = render_hf_readme()

                        # Write a temp file (upload_file API expects a path or fileobj)
                        tmp_path = "README.md"
                        with open(tmp_path, "w", encoding="utf-8") as f:
                            f.write(st.session_state.last_readme_text)

                        # Upload to Hub (creates repo if missing)
                        upload_readme_to_hub(
                            repo_id=repo_id_rm,
                            token=token_rm or None,
                            readme_path=tmp_path,
                            create_if_missing=True,
                        )

                        new_url = f"https://huggingface.co/{repo_id_rm}"
                        st.success(f"Pushed the README to the repo [here]({new_url})!")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                else:
                    st.error(
                        "Repo ID invalid. It should be username/repo-name. For example: nateraw/food"
                    )

        # ------------------------------
        # TAB 2 — Local downloads (JSON / PDF)
        # ------------------------------
        with tab_local:
            st.markdown("## Download Model Card")

            with st.expander("Download Options", expanded=True):
                # JSON
                with st.form("form_download_json"):
                    download_submit = st.form_submit_button(
                        "Download Model Card as `.json`"
                    )
                    if download_submit:
                        if st.session_state.get("format_error"):
                            st.error(
                                "Cannot download — there are fields with invalid format."
                            )
                        else:
                            missing_required = (
                                validation_utils.validate_required_fields(
                                    model_card_schema,
                                    current_task=st.session_state.get("task"),
                                )
                            )
                            st.session_state.download_ready = True
                            if missing_required:
                                st.error(
                                    "Some required fields are missing. Check the Warnings section on the sidebar for details."
                                )

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

                with st.form("form_download_pdf"):
                    pdf_submit = st.form_submit_button("Download Model Card as `.pdf`")
                    if pdf_submit:
                        if st.session_state.get("format_error"):
                            st.error("Cannot download — there are fields with invalid format.")
                        else:
                            try:
                                from md_renderer import save_model_card_pdf
                                pdf_path = save_model_card_pdf("model_card.pdf", base_url=os.getcwd())
                                st.session_state.download_ready_pdf = True
                                st.session_state.generated_pdf_path = pdf_path  # <- guarda la ruta
                            except Exception as e:
                                st.error(f"Failed to generate PDF: {e}")
                                st.session_state.download_ready_pdf = False

                if st.session_state.get("download_ready_pdf"):
                    pdf_path = st.session_state.get("generated_pdf_path", "model_card.pdf")
                    with open(pdf_path, "rb") as f:  # <- usa la misma ruta
                        st.download_button(
                            "Your download is ready — click here (PDF)",
                            f,
                            file_name="model_card.pdf",
                            use_container_width=True,
                            key="btn_download_pdf",
                        )
                    st.session_state.download_ready_pdf = False



                def parse_into_markdown(schema) -> str:
                    """Return the complete Model Card as Markdown via your renderer."""
                    return render_full_model_card_md()

                # --- MD download form (mirrors your JSON structure) ---
                with st.form("form_download_md"):
                    download_submit_md = st.form_submit_button("Download Model Card as `.md`")
                    if download_submit_md:
                        if st.session_state.get("format_error"):
                            st.error("Cannot download — there are fields with invalid format.")
                        else:
                            missing_required = validation_utils.validate_required_fields(
                                model_card_schema,                   # or SCHEMA if that’s your variable
                                current_task=st.session_state.get("task"),
                            )
                            st.session_state.download_ready_md = True
                            if missing_required:
                                st.error(
                                    "Some required fields are missing. Check the Warnings section on the sidebar for details."
                                )

                if st.session_state.get("download_ready_md"):
                    try:
                        md_text = parse_into_markdown(model_card_schema)  # or SCHEMA
                        # Optional: quick preview
                        with st.expander("Preview (.md)", expanded=False):
                            st.code(md_text, language="markdown")

                        st.download_button(
                            "Your download is ready — click here (Markdown)",
                            data=md_text.encode("utf-8"),
                            file_name="model_card.md",
                            mime="text/markdown",
                            key="btn_download_md",
                        )
                    except Exception as e:
                        st.error(f"Error while generating Markdown: {e}")
                    finally:
                        st.session_state.download_ready_md = False

                
            
                def _get_uploaded_paths():
                    paths = st.session_state.get("all_uploaded_paths", set())
                    return [p for p in list(paths) if isinstance(p, str) and os.path.exists(p)]

                # ========== FORM: Download files (.zip only) ==========
                with st.form("form_download_files"):
                    submit_files = st.form_submit_button("Download files (`.zip`)")
                    if submit_files:
                        files = _get_uploaded_paths()
                        if not files:
                            st.warning("No uploaded files to download.")
                        else:
                            st.session_state.download_files_ready = True

                if st.session_state.get("download_files_ready"):
                    files = _get_uploaded_paths()
                    if not files:
                        st.warning("No uploaded files to download.")
                    else:
                        buffer = io.BytesIO()
                        with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                            for fpath in files:
                                try:
                                    arcname = Path(fpath).name
                                    zf.write(fpath, arcname=arcname)
                                except Exception:
                                    st.warning(f"Could not add: {fpath}")
                        buffer.seek(0)

                        st.download_button(
                            label="Download all files (ZIP)",
                            data=buffer,
                            file_name="uploaded_files.zip",
                            mime="application/zip",
                            key="btn_download_files_zip",
                            use_container_width=True,
                        )

                    st.session_state.download_files_ready = False

                # ========== FORM: Download .zip (json + files) ==========
                with st.form("form_download_zip_all"):
                    zip_submit = st.form_submit_button("Download `.zip` (Model Card `.json` + files)")
                    if zip_submit:
                        files = _get_uploaded_paths()
                        if not files:
                            st.warning("No uploaded files to include in the ZIP.")
                        else:
                            if st.session_state.get("format_error"):
                                st.error("Cannot download — there are fields with invalid format.")
                            else:
                                missing_required = validation_utils.validate_required_fields(
                                    model_card_schema,
                                    current_task=st.session_state.get("task"),
                                )
                                st.session_state.download_zip_ready = True
                                if missing_required:
                                    st.error(
                                        "Some required fields are missing. Check the Warnings section on the sidebar for details."
                                    )

                if st.session_state.get("download_zip_ready"):
                    files = _get_uploaded_paths()
                    if not files:
                        st.warning("No uploaded files to include in the ZIP.")
                    else:
                        # 1) Generar JSON como en tu flujo actual
                        card_content = parse_into_json(SCHEMA)  # usa los imports ya presentes

                        # 2) Crear ZIP en memoria con JSON + files
                        buffer = io.BytesIO()
                        try:
                            with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                                # Añade el JSON
                                zf.writestr("model_card.json", card_content)

                                # Añade los ficheros subidos
                                for fpath in files:
                                    try:
                                        arcname = f"files/{Path(fpath).name}"
                                        zf.write(fpath, arcname=arcname)
                                    except Exception:
                                        st.warning(f"Could not add: {fpath}")
                            buffer.seek(0)

                            st.download_button(
                                "Your download is ready — click here (ZIP)",
                                data=buffer,
                                file_name="model_card_with_files.zip",
                                mime="application/zip",
                                key="btn_download_zip_all",
                                use_container_width=True,
                            )
                        finally:
                            # Limpia el buffer si quieres evitar mantenerlo en sesión
                            pass

                    st.session_state.download_zip_ready = False


        # ------------------------------
        # TAB 3 — Export to Hub
        # ------------------------------
        with tab_export:
            uploaded_file = st.file_uploader(
                "Choose a `.json` file",
                type=[".json"],
                help="Only `.json` files are supported.",
                key="uploader_json_tab1",
            )
            if uploaded_file is not None:
                name_of_uploaded_file = save_uploadedfile(uploaded_file)
                st.session_state.markdown_upload = name_of_uploaded_file
                st.success(f"File {uploaded_file.name} saved successfully.")

            st.markdown("## Export Loaded Model Card to Hub (`.json`)")
            with st.form("form_upload_json_hub"):
                st.markdown(
                    "Use a token with write access from [here](https://hf.co/settings/tokens)"
                )
                token_json = st.text_input(
                    "Token", type="password", key="token_json_hub"
                )
                repo_id_json = st.text_input(
                    "Repo ID (e.g. user/repo)", key="repo_id_json_hub"
                )
                submit_json = st.form_submit_button("Upload .json to Hub")

            if submit_json:
                if len(repo_id_json.split("/")) == 2:
                    try:
                        json_path = st.session_state.get("markdown_upload")
                        if not json_path:
                            st.error(
                                "Please upload a .json file in the README tools tab first."
                            )
                        else:
                            with open(json_path, "r") as json_file:
                                model_card = json.load(json_file)
                            new_url = upload_json_card(
                                model_card, repo_id_json, token_json
                            )
                            st.success(
                                f"Pushed the card to the repo [here]({new_url})!"
                            )
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                else:
                    st.error(
                        "Repo ID invalid. It should be username/repo-name. For example: nateraw/food"
                    )
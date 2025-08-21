import streamlit as st
import utils
import base64
import uuid
from pathlib import Path

model_card_schema = utils.get_model_card_schema()

UPLOAD_DIR = Path("uploads/appendix")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def _safe_remove(path_str: str):
    try:
        Path(path_str).unlink(missing_ok=True)
    except Exception:
        pass

def appendix_render():
    st.markdown("""
    <style>
    /* hide Streamlit Cloud’s top-right toolbar (includes the GitHub icon) */
    div[data-testid="stToolbar"] { visibility: hidden; height: 0; }

    /* optional: also hide the 'Manage app' badge and footer */
    a[data-testid="viewerBadge_link"] { display: none !important; }
    div[data-testid="stStatusWidget"] { display: none !important; }
    footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)
    from side_bar import sidebar_render
    sidebar_render()

    utils.title("Appendix")
    st.info(
        "Files uploaded in the **Appendix** as well as files added in other sections will **not** appear when you load an incomplete model card.\n\n"
        "They are included only when you download:\n"
        "- the **ZIP with files**\n"
        "- the **ZIP with Model Card (`.json`) + files**\n"
        "- the **Model Card as `.pdf`**",
        icon="ℹ",
    )

    utils.subtitle("Attach any additional files you want to include in your model card.")
    st.info("You can upload any supporting files such as PDFs, figures, CSVs, ZIPs, or notes.")

    # --- Persistent registries in session_state ---
    if "appendix_uploads" not in st.session_state:
        # { original_name: { "custom_label": str, "path": str, "stored_name": str } }
        st.session_state.appendix_uploads = {}
    if "all_uploaded_paths" not in st.session_state:
        st.session_state.all_uploaded_paths = set()
    if "render_uploads" not in st.session_state:
        st.session_state.render_uploads = {}
    # Nonce to force a fresh uploader (prevents the "×" from appearing after upload)
    if "appendix_uploader_nonce" not in st.session_state:
        st.session_state.appendix_uploader_nonce = 0

    # --- Uploader is ADD-ONLY; we never infer deletions from its value ---
    uploaded_files = st.file_uploader(
        "Upload files here",
        type=None,
        accept_multiple_files=True,
        help="Any file type is allowed.",
        key=f"appendix_uploader_{st.session_state.appendix_uploader_nonce}",  # fresh key hides the "×"
    )

    # Save any newly uploaded files (add-only), then reset uploader so no "×" is shown
    if uploaded_files:
        for file in uploaded_files:
            if file.name not in st.session_state.appendix_uploads:
                unique_id = uuid.uuid4().hex[:8]
                stored_name = f"appendix_{unique_id}_{file.name}"
                save_path = UPLOAD_DIR / stored_name
                with open(save_path, "wb") as f:
                    f.write(file.getbuffer())

                st.session_state.appendix_uploads[file.name] = {
                    "custom_label": "",
                    "path": str(save_path),
                    "stored_name": stored_name,
                }

                # Register for markdown renderer normalization
                st.session_state.render_uploads[stored_name] = {
                    "path": str(save_path),
                    "name": file.name,
                }
                st.session_state.all_uploaded_paths.add(str(save_path))

        # Bump nonce and rerun so the uploader re-mounts with a fresh key (no selected files, no "×")
        st.session_state.appendix_uploader_nonce += 1
        st.rerun()

    # --- Display uploaded files (from our registry only) ---
    if st.session_state.appendix_uploads:
        utils.title("Files Uploaded")
        utils.section_divider()

        # Iterate over a snapshot to allow mutation during loop
        for original_name, file_data in list(st.session_state.appendix_uploads.items()):
            file_path = file_data["path"]
            file_ext = Path(file_path).suffix.lower()

            col1, col2, col3 = st.columns([3, 5, 1])
            with col1:
                st.markdown(f"**{original_name}**")
                st.caption(Path(file_path).name)
            with col2:
                label_key = f"label_{original_name}"
                label_val = st.text_input(
                    label="Label",
                    value=file_data.get("custom_label", ""),
                    key=label_key,
                    placeholder="Indicate here the Figure/ File number e.g., Fig 1",
                    label_visibility="collapsed",
                )
                st.session_state.appendix_uploads[original_name]["custom_label"] = label_val
            with col3:
                # Explicit delete (doesn't rely on uploader)
                if st.button("Delete", key=f"del_{file_data['stored_name']}"):
                    _safe_remove(file_path)
                    st.session_state.all_uploaded_paths.discard(file_path)
                    st.session_state.render_uploads.pop(file_data["stored_name"], None)
                    st.session_state.appendix_uploads.pop(original_name, None)
                    # No need to rerun manually; button click already triggers a rerun

            # Preview
            try:
                preview_supported = file_ext in [
                    ".png", ".jpg", ".jpeg", ".gif", ".pdf",
                    ".txt", ".csv", ".json", ".md",
                    ".py", ".c", ".cpp", ".h",
                ]

                if preview_supported:
                    with st.expander("Preview", expanded=False):
                        if file_ext in [".png", ".jpg", ".jpeg", ".gif"]:
                            st.image(file_path, use_container_width=True)
                        elif file_ext == ".pdf":
                            with open(file_path, "rb") as f:
                                base64_pdf = base64.b64encode(f.read()).decode("utf-8")
                                pdf_display = (
                                    f'<iframe src="data:application/pdf;base64,{base64_pdf}" '
                                    'width="100%" height="500px"></iframe>'
                                )
                                st.markdown(pdf_display, unsafe_allow_html=True)
                        else:
                            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                                st.code(f.read(), language="text")
                else:
                    utils.light_header_italics("Preview not supported for this file type.")
            except Exception:
                utils.light_header_italics("Could not preview this file.")

            utils.section_divider()

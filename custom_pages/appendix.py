import base64  # still used by preview helper (import left for compatibility if needed)
from pathlib import Path
import streamlit as st
import utils

from uploads_manager import (
    ensure_upload_state,
    save_appendix_files,
    delete_appendix_item,
    preview_file
)

model_card_schema = utils.get_model_card_schema()

UPLOAD_DIR = Path("uploads/appendix")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def appendix_render():
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

    ensure_upload_state()

    uploaded_files = st.file_uploader(
        "Upload files here",
        type=None,
        accept_multiple_files=True,
        help="Any file type is allowed.",
        key=f"appendix_uploader_{st.session_state.appendix_uploader_nonce}",  
    )

    if save_appendix_files(uploaded_files, UPLOAD_DIR):
        st.session_state.appendix_uploader_nonce += 1
        st.rerun()

    if st.session_state.appendix_uploads:
        utils.title("Files Uploaded")
        utils.section_divider()

        # Iterate over a snapshot to allow mutation during loop
        for original_name, file_data in list(st.session_state.appendix_uploads.items()):
            file_path = file_data["path"]

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
                if st.button("Delete", key=f"del_{file_data['stored_name']}"):
                    delete_appendix_item(original_name)
                    st.rerun()

            with st.expander("Preview", expanded=False):
                prev = preview_file(file_path)
                if prev is False:
                    utils.light_header_italics("Preview not supported for this file type.")
                elif prev is None:
                    utils.light_header_italics("Could not preview this file.")

            utils.section_divider()

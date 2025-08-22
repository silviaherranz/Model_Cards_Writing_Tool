from __future__ import annotations

from pathlib import Path
from typing import Dict

import streamlit as st
import utils

from uploads_manager import (
    ensure_upload_state,
    save_appendix_files,
    delete_appendix_item,
    preview_file,
)

__all__ = ["appendix_render"]

APPENDIX_TITLE = "Appendix"
APPENDIX_HELP = (
    "Files uploaded in the **Appendix** as well as files added in other sections will "
    "**not** appear when you load an incomplete model card.\n\n"
    "They are included only when you download:\n"
    "- the **ZIP with files**\n"
    "- the **ZIP with Model Card (`.json`) + files**\n"
    "- the **Model Card as `.pdf`**"
)
APPENDIX_SUBTITLE = (
    "Attach any additional files you want to include in your model card."
)
APPENDIX_HINT = (
    "You can upload any supporting files such as PDFs, figures, CSVs, ZIPs, or notes."
)

UPLOAD_DIR = Path("uploads/appendix")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def _appendix_uploader_key() -> str:
    """Stable key that changes only when the global appendix nonce changes."""
    return f"appendix_uploader_{st.session_state.appendix_uploader_nonce}"


def _bump_appendix_uploader() -> None:
    """Force remount of the appendix uploader to clear selection after save."""
    st.session_state.appendix_uploader_nonce += 1


def _render_uploaded_row(original_name: str, file_data: Dict[str, str]) -> None:
    """
    Render a single uploaded file row with label editing, delete button, and preview.
    """
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
        # Persist label alongside the stored entry
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


def appendix_render() -> None:
    """Render the Appendix page (UI only)."""
    from side_bar import sidebar_render

    sidebar_render()

    utils.title(APPENDIX_TITLE)
    st.info(APPENDIX_HELP, icon="ℹ")
    utils.subtitle(APPENDIX_SUBTITLE)
    st.info(APPENDIX_HINT)

    ensure_upload_state()

    uploaded_files = st.file_uploader(
        "Upload files here",
        type=None,  # Allow any file type in Appendix
        accept_multiple_files=True,
        help="Any file type is allowed.",
        key=_appendix_uploader_key(),
    )

    if save_appendix_files(uploaded_files, UPLOAD_DIR):
        _bump_appendix_uploader()
        st.rerun()

    if st.session_state.appendix_uploads:
        utils.title("Files Uploaded")
        utils.section_divider()

        # Iterate over a snapshot to allow deletion during iteration
        for original_name, file_data in list(st.session_state.appendix_uploads.items()):
            _render_uploaded_row(original_name, file_data)

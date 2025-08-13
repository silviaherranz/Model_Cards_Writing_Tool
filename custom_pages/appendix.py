import streamlit as st
from pack_io import APPENDIX_DIR
import utils
import os
import base64
from pathlib import Path

model_card_schema = utils.get_model_card_schema()

def appendix_render():
    from side_bar import sidebar_render
    sidebar_render()

    utils.title("Appendix")
    utils.subtitle("Attach any additional files you want to include in your model card.")
    st.info("You can upload any supporting files such as PDFs, figures, CSVs, ZIPs, or notes.")

    if "appendix_uploads" not in st.session_state:
        st.session_state.appendix_uploads = {}

    # 1) Generic uploader (free uploads not tied to a section label)
    uploaded_files = st.file_uploader(
        "Upload files here",
        type=None,
        accept_multiple_files=True,
        help="Any file type is allowed.",
        key="appendix_free_uploader",
    )
    if uploaded_files:
        for file in uploaded_files:
            if file.name not in st.session_state.appendix_uploads:
                save_path = APPENDIX_DIR / file.name
                with open(save_path, "wb") as f:
                    f.write(file.getbuffer())
                st.session_state.appendix_uploads[file.name] = {
                    "custom_label": "",
                    "path": str(save_path),
                }

    # 2) Labeled placeholders created from sections (fixed label, empty path)
    pending = [(name, meta) for name, meta in st.session_state.appendix_uploads.items() if not meta.get("path")]
    if pending:
        utils.title("Labeled uploads (from sections)")
        utils.section_divider()
        for fixed_label, meta in pending:
            st.markdown(f"**{fixed_label}** *(fixed label from a section)*")
            up = st.file_uploader(
                label=f"Drop file for label: {fixed_label}",
                type=["png","jpg","jpeg","gif","bmp","tiff","webp","svg",
                      "dcm","dicom","nii","nifti","pdf","docx","doc",
                      "pptx","ppt","txt","xlsx","xls"],
                key=f"uploader_for_label_{fixed_label}",
                accept_multiple_files=False,
            )
            if up:
                save_path = APPENDIX_DIR / up.name
                with open(save_path, "wb") as f:
                    f.write(up.getbuffer())
                st.session_state.appendix_uploads[fixed_label]["path"] = str(save_path)
                st.success("File saved for this label.")

    # 3) Normal list (files that have a path)
    files_with_path = [(n, m) for n, m in st.session_state.appendix_uploads.items() if m.get("path")]
    if files_with_path:
        utils.title("Files Uploaded")
        utils.section_divider()
        for original_name, file_data in list(files_with_path):
            col1, col2, col3 = st.columns([3, 5, 1])
            with col1:
                st.markdown(f"**{original_name}**")
            with col2:
                # Label is editable for free uploads; but if this entry is owned by a section (appendix_links),
                # keep it read-only to honor the “fixed label” behavior.
                owner = st.session_state.get("appendix_links", {}).get(original_name)
                if owner:
                    st.caption("Label is fixed (linked from a section).")
                    st.text_input("Label", value=file_data.get("custom_label", original_name),
                                  key=f"ro_{original_name}", disabled=True, label_visibility="collapsed")
                else:
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
                if st.button("Remove", key=f"rm_{original_name}"):
                    try:
                        if file_data.get("path"):
                            os.remove(file_data["path"])
                    except Exception:
                        pass
                    st.session_state.appendix_uploads.pop(original_name, None)
                    # Also clear link ownership if it exists
                    if st.session_state.get("appendix_links", {}).get(original_name):
                        st.session_state.appendix_links.pop(original_name, None)
                    st.rerun()

            # Preview
            file_path = file_data.get("path")
            if not file_path:
                continue
            file_ext = Path(file_path).suffix.lower()
            try:
                preview_supported = file_ext in [
                    ".png",".jpg",".jpeg",".gif",".pdf",".txt",".csv",".json",".md",".py",".c",".cpp",".h"
                ]
                if preview_supported:
                    with st.expander("Preview", expanded=False):
                        if file_ext in [".png",".jpg",".jpeg",".gif"]:
                            st.image(file_path, use_container_width=True)
                        elif file_ext == ".pdf":
                            with open(file_path, "rb") as f:
                                base64_pdf = base64.b64encode(f.read()).decode("utf-8")
                                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="500px"></iframe>'
                                st.markdown(pdf_display, unsafe_allow_html=True)
                        else:
                            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                                st.code(f.read(), language="text")
                else:
                    utils.light_header_italics("Preview not supported for this file type.")
            except Exception:
                utils.light_header_italics("Could not preview this file.")

            utils.section_divider()



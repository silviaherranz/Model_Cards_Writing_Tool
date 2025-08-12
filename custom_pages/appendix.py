import base64
from helpers import _init_registry, register_file, remove_registered_by_relpath


def appendix_render():
    import streamlit as st
    from pathlib import Path
    import utils
    
    _init_registry()

    from side_bar import sidebar_render
    sidebar_render()

    utils.title("Appendix")
    utils.subtitle("Attach any additional files you want to include in your model card.")
    st.info("You can upload any supporting files such as PDFs, figures, CSVs, ZIPs, or notes.")

    # Upload
    uploaded_files = st.file_uploader(
        "Upload files here",
        type=None,
        accept_multiple_files=True,
        help="Any file type is allowed.",
        key="appendix_uploader",
    )

    # Add newly uploaded files to session + disk
    if uploaded_files:
        for file in uploaded_files:
            if file.name not in st.session_state.appendix_uploads:
                rec = register_file(file, source="appendix")
                # keep your original structure for UI, but store relpath + record id
                st.session_state.appendix_uploads[file.name] = {
                    "custom_label": "",
                    "path": rec["relpath"],
                    "id": rec["id"],
                }

    # Detect deletions (if user removes from file_uploader list)
    current_file_names = [f.name for f in uploaded_files] if uploaded_files else []
    for stored_name in list(st.session_state.appendix_uploads.keys()):
        if stored_name not in current_file_names:
            relpath = st.session_state.appendix_uploads[stored_name]["path"]
            remove_registered_by_relpath(relpath)
            del st.session_state.appendix_uploads[stored_name]

    # Display + label + preview
    if st.session_state.appendix_uploads:
        utils.title("Files Uploaded")
        utils.section_divider()

        for original_name, file_data in st.session_state.appendix_uploads.items():
            col1, col2 = st.columns([3, 5])
            with col1:
                st.markdown(f"**{original_name}**")
            with col2:
                label_key = f"label_{original_name}"
                label_val = st.text_input(
                    label="Label",
                    value=file_data.get("custom_label", ""),
                    key=label_key,
                    placeholder="Indicate here the Figure/ File number e.g., Fig 1",
                    label_visibility="collapsed",
                )
                # update both appendix dict + registry
                st.session_state.appendix_uploads[original_name]["custom_label"] = label_val
                rid = file_data.get("id")
                if rid and rid in st.session_state.file_registry:
                    st.session_state.file_registry[rid]["label"] = label_val

            file_path = file_data["path"]
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
                            st.markdown(
                                f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="500px"></iframe>',
                                unsafe_allow_html=True,
                            )
                        else:
                            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                                st.code(f.read(), language="text")
                else:
                    utils.light_header_italics("Preview not supported for this file type.")
            except Exception:
                utils.light_header_italics("Could not preview this file.")

            utils.section_divider()

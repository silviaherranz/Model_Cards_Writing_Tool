import streamlit as st
import utils
import os
import base64
from pathlib import Path

model_card_schema = utils.get_model_card_schema()


def appendix_render():
    from side_bar import sidebar_render

    sidebar_render()

    utils.title("Appendix")
    utils.subtitle(
        "Attach any additional files you want to include in your model card."
    )
    st.info(
        "You can upload any supporting files such as PDFs, figures, CSVs, ZIPs, or notes."
    )

    if "appendix_uploads" not in st.session_state:
        st.session_state.appendix_uploads = {}

    uploaded_files = st.file_uploader(
        "Upload files here",
        type=None,
        accept_multiple_files=True,
        help="Any file type is allowed.",
    )

    if uploaded_files:
        for file in uploaded_files:
            if file.name not in st.session_state.appendix_uploads:
                save_path = f"appendix_{file.name}"
                with open(save_path, "wb") as f:
                    f.write(file.getbuffer())

                st.session_state.appendix_uploads[file.name] = {
                    "custom_label": "",
                    "path": save_path,
                }

    deleted_files = []
    current_file_names = [f.name for f in uploaded_files] if uploaded_files else []

    for stored_file in list(st.session_state.appendix_uploads):
        if stored_file not in current_file_names:
            deleted_files.append(stored_file)

    for file_to_delete in deleted_files:
        try:
            os.remove(st.session_state.appendix_uploads[file_to_delete]["path"])
        except Exception:
            pass
        del st.session_state.appendix_uploads[file_to_delete]

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
                st.session_state.appendix_uploads[original_name]["custom_label"] = (
                    label_val
                )

            file_path = st.session_state.appendix_uploads[original_name]["path"]
            file_ext = Path(file_path).suffix.lower()

            try:
                preview_supported = False
                if file_ext in [
                    ".png",
                    ".jpg",
                    ".jpeg",
                    ".gif",
                    ".pdf",
                    ".txt",
                    ".csv",
                    ".json",
                    ".md",
                    ".py",
                    ".c",
                    ".cpp",
                    ".h",
                ]:
                    preview_supported = True

                if preview_supported:
                    with st.expander("Preview", expanded=False):
                        if file_ext in [".png", ".jpg", ".jpeg", ".gif"]:
                            st.image(file_path, use_container_width=True)
                        elif file_ext == ".pdf":
                            with open(file_path, "rb") as f:
                                base64_pdf = base64.b64encode(f.read()).decode("utf-8")
                                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="500px"></iframe>'
                                st.markdown(pdf_display, unsafe_allow_html=True)
                        else:
                            with open(
                                file_path, "r", encoding="utf-8", errors="ignore"
                            ) as f:
                                st.code(f.read(), language="text")
                else:
                    utils.light_header_italics(
                        "Preview not supported for this file type."
                    )
            except Exception:
                utils.light_header_italics("Could not preview this file.")

            utils.section_divider()

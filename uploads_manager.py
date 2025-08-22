from __future__ import annotations
from pathlib import Path
import base64
import os
import uuid
import streamlit as st


REG_APPENDIX_UPLOADS = "appendix_uploads"
REG_ALL_PATHS = "all_uploaded_paths"
REG_RENDER_UPLOADS = "render_uploads"
REG_APPENDIX_NONCE = "appendix_uploader_nonce"


def ensure_upload_state():
    """
    Ensure the upload state is initialized in the session.
    """
    
    if REG_APPENDIX_UPLOADS not in st.session_state:
        st.session_state[REG_APPENDIX_UPLOADS] = {}
    if REG_ALL_PATHS not in st.session_state:
        st.session_state[REG_ALL_PATHS] = set()
    if REG_RENDER_UPLOADS not in st.session_state:
        st.session_state[REG_RENDER_UPLOADS] = {}
    if REG_APPENDIX_NONCE not in st.session_state:
        st.session_state[REG_APPENDIX_NONCE] = 0


def safe_remove(path_str: str):
    """
    Safely remove a file or directory.

    :param path_str: The path to the file or directory to remove.
    :type path_str: str
    """
    try:
        Path(path_str).unlink(missing_ok=True)
    except Exception:
        pass


def register_path(path_str: str):
    st.session_state[REG_ALL_PATHS].add(path_str)


def unregister_path(path_str: str):
    st.session_state[REG_ALL_PATHS].discard(path_str)


def save_appendix_files(uploaded_files, dest_dir: Path):
    """
    Add-only save for Appendix. Returns True if anything was saved.
    Expects ensure_upload_state() to have been called.
    """
    if not uploaded_files:
        return False

    saved_any = False
    dest_dir.mkdir(parents=True, exist_ok=True)

    for file in uploaded_files:
        original_name = file.name
        if original_name in st.session_state[REG_APPENDIX_UPLOADS]:
            continue  # add-only: ignore duplicates by original name

        unique_id = uuid.uuid4().hex[:8]
        stored_name = f"appendix_{unique_id}_{original_name}"
        save_path = dest_dir / stored_name
        with open(save_path, "wb") as f:
            f.write(file.getbuffer())

        st.session_state[REG_APPENDIX_UPLOADS][original_name] = {
            "custom_label": "",
            "path": str(save_path),
            "stored_name": stored_name,
        }
        # For markdown renderer normalization
        st.session_state[REG_RENDER_UPLOADS][stored_name] = {
            "path": str(save_path),
            "name": original_name,
        }
        register_path(str(save_path))
        saved_any = True

    return saved_any


def delete_appendix_item(original_name: str):
    entry = st.session_state[REG_APPENDIX_UPLOADS].pop(original_name, None)
    if not entry:
        return
    file_path = entry["path"]
    stored_name = entry["stored_name"]
    safe_remove(file_path)
    unregister_path(file_path)
    st.session_state[REG_RENDER_UPLOADS].pop(stored_name, None)


def field_current(full_key: str):
    return st.session_state[REG_RENDER_UPLOADS].get(full_key)


def field_overwrite(full_key: str, uploaded_file, folder: str = "uploads"):
    """
    Save/overwrite a single file for a given field key.
    Returns metadata dict with {path, name}.
    """
    os.makedirs(folder, exist_ok=True)
    safe_name = uploaded_file.name
    save_path = os.path.join(folder, f"{full_key}_{safe_name}")

    field_delete(full_key)

    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    register_path(save_path)
    meta = {"path": save_path, "name": safe_name}
    st.session_state[REG_RENDER_UPLOADS][full_key] = meta
    return meta


def field_delete(full_key: str):
    prev = st.session_state[REG_RENDER_UPLOADS].pop(full_key, None)
    if not prev:
        return
    try:
        if os.path.exists(prev["path"]):
            os.remove(prev["path"])
    except Exception:
        pass
    unregister_path(prev["path"])
    # Backcompat with your code that stashes the raw upload
    st.session_state.pop(f"{full_key}_image", None)


PREVIEW_EXTS = {
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
}


def preview_file(file_path: str):
    """
    Mirrors your original preview behavior.
    """
    try:
        suffix = Path(file_path).suffix.lower()
        if suffix not in PREVIEW_EXTS:
            return False  # not previewed

        if suffix in {".png", ".jpg", ".jpeg", ".gif"}:
            st.image(file_path, use_container_width=True)
        elif suffix == ".pdf":
            with open(file_path, "rb") as f:
                base64_pdf = base64.b64encode(f.read()).decode("utf-8")
            st.markdown(
                f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="500px"></iframe>',
                unsafe_allow_html=True,
            )
        else:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                st.code(f.read(), language="text")
        return True
    except Exception:
        return None  


def uploader_key_for(field_key: str) -> str:
    """Return a stable uploader key that remounts when its per-field nonce changes."""
    nk = f"{field_key}__uploader_nonce"
    if nk not in st.session_state:
        st.session_state[nk] = 0
    return f"{field_key}__uploader_{st.session_state[nk]}"


def bump_uploader(field_key: str) -> None:
    """Increment the per-field nonce so the uploader remounts on next rerun."""
    nk = f"{field_key}__uploader_nonce"
    st.session_state[nk] = st.session_state.get(nk, 0) + 1

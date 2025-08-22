from __future__ import annotations

import base64
import re
import uuid
from pathlib import Path
from typing import Dict, Iterable, Optional, Set, TypedDict, cast

import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile

# ---- Session-state keys ------------------------------------------------------

REG_APPENDIX_UPLOADS = (
    "appendix_uploads"  # original_name -> {"custom_label","path","stored_name"}
)
REG_ALL_PATHS = "all_uploaded_paths"  # set[str] for cleanup
REG_RENDER_UPLOADS = "render_uploads"  # key|stored_name -> {"path","name"}
REG_APPENDIX_NONCE = "appendix_uploader_nonce"  # kept for compatibility

# ---- Shared UI constants (imported by UI modules to avoid duplication) -------

ALLOWED_UPLOAD_EXTS: list[str] = [
    "png",
    "jpg",
    "jpeg",
    "gif",
    "bmp",
    "tiff",
    "webp",
    "svg",
    "dcm",
    "dicom",
    "nii",
    "nifti",
    "pdf",
    "docx",
    "doc",
    "pptx",
    "ppt",
    "txt",
    "xlsx",
    "xls",
    "DICOM",
]

# ---- Types -------------------------------------------------------------------


class UploadMeta(TypedDict):
    """Metadata for a stored upload."""

    path: str
    name: str


class AppendixMeta(TypedDict, total=False):
    """Metadata stored per original filename in appendix uploads."""

    custom_label: str
    path: str
    stored_name: str


# ---- Filename sanitization ---------------------------------------------------

_SAFE_CHARS = re.compile(r"[^A-Za-z0-9._-]")


def sanitize_filename(name: str, max_len: int = 120) -> str:
    """
    Return a filesystem-safe filename.

    :param name: Original filename (may include directories).
    :type name: str
    :param max_len: Maximum length for the sanitized name.
    :type max_len: int
    :returns: Sanitized filename without directory components.
    :rtype: str
    """
    base = Path(name).name
    base = _SAFE_CHARS.sub("_", base)
    return base[:max_len] if max_len > 0 else base


# ---- Session-state lifecycle -------------------------------------------------


def ensure_upload_state() -> None:
    """
    Ensure all required Streamlit session-state registries exist.

    Creates keys:

    - ``appendix_uploads``: ``dict[str, AppendixMeta]``
    - ``all_uploaded_paths``: ``set[str]``
    - ``render_uploads``: ``dict[str, UploadMeta]``
    - ``appendix_uploader_nonce``: ``int``
    """
    if REG_APPENDIX_UPLOADS not in st.session_state:
        st.session_state[REG_APPENDIX_UPLOADS] = cast(Dict[str, AppendixMeta], {})
    if REG_ALL_PATHS not in st.session_state:
        st.session_state[REG_ALL_PATHS] = cast(Set[str], set())
    if REG_RENDER_UPLOADS not in st.session_state:
        st.session_state[REG_RENDER_UPLOADS] = cast(Dict[str, UploadMeta], {})
    if REG_APPENDIX_NONCE not in st.session_state:
        st.session_state[REG_APPENDIX_NONCE] = 0


def register_path(path_str: str) -> None:
    """Register a path for later cleanup."""
    st.session_state[REG_ALL_PATHS].add(path_str)


def unregister_path(path_str: str) -> None:
    """Unregister a path from the cleanup registry."""
    st.session_state[REG_ALL_PATHS].discard(path_str)


def safe_remove(path_str: str) -> None:
    """
    Safely remove a **file** (ignore if missing).

    :param path_str: Path to the file to remove.
    :type path_str: str
    """
    try:
        Path(path_str).unlink(missing_ok=True)
    except Exception:
        # Intentionally ignore failures so UI flows don't crash on cleanup.
        pass


def clear_all_uploads() -> None:
    """
    Remove all stored uploads and clear registries.

    Useful for a global "Reset uploads" button.
    """
    ensure_upload_state()
    for p in list(st.session_state[REG_ALL_PATHS]):
        safe_remove(p)
        unregister_path(p)
    st.session_state[REG_APPENDIX_UPLOADS].clear()
    st.session_state[REG_RENDER_UPLOADS].clear()


# ---- Appendix uploads (add-only) --------------------------------------------


def save_appendix_files(
    uploaded_files: Optional[Iterable[UploadedFile]], dest_dir: Path
) -> bool:
    """
    Save appendix files in an *add-only* manner.

    Duplicated files (by **original filename**) are ignored. Each saved file gets
    a unique prefix to avoid collisions on disk.

    :param uploaded_files: Iterable of Streamlit ``UploadedFile`` objects.
    :type uploaded_files: Iterable[UploadedFile] | None
    :param dest_dir: Destination directory for saved files.
    :type dest_dir: pathlib.Path
    :returns: ``True`` if at least one file was saved, else ``False``.
    :rtype: bool
    :raises OSError: If writing a file fails.
    :note: Call :func:`ensure_upload_state` before using this function.
    """
    if not uploaded_files:
        return False

    ensure_upload_state()
    saved_any = False
    dest_dir.mkdir(parents=True, exist_ok=True)

    for uploaded in uploaded_files:
        original_name = sanitize_filename(uploaded.name)
        if original_name in st.session_state[REG_APPENDIX_UPLOADS]:
            continue  # skip duplicates by original name

        unique_id = uuid.uuid4().hex[:8]
        stored_name = f"appendix_{unique_id}_{original_name}"
        save_path = dest_dir / stored_name

        with save_path.open("wb") as f:
            f.write(uploaded.getbuffer())

        st.session_state[REG_APPENDIX_UPLOADS][original_name] = AppendixMeta(
            custom_label="",
            path=str(save_path),
            stored_name=stored_name,
        )
        st.session_state[REG_RENDER_UPLOADS][stored_name] = UploadMeta(
            path=str(save_path),
            name=original_name,
        )
        register_path(str(save_path))
        saved_any = True

    return saved_any


def delete_appendix_item(original_name: str) -> None:
    """
    Delete an appendix item by its original filename.

    :param original_name: Original filename used as key in the appendix registry.
    :type original_name: str
    """
    ensure_upload_state()
    entry = st.session_state[REG_APPENDIX_UPLOADS].pop(original_name, None)
    if not entry:
        return
    file_path = entry.get("path", "")
    stored_name = entry.get("stored_name", "")
    if file_path:
        safe_remove(file_path)
        unregister_path(file_path)
    if stored_name:
        st.session_state[REG_RENDER_UPLOADS].pop(stored_name, None)


# ---- Per-field uploads (single file per key) --------------------------------


def field_current(full_key: str) -> Optional[UploadMeta]:
    """
    Get current stored metadata for a given field key.

    :param full_key: Unique field key used to store the uploaded file.
    :type full_key: str
    :returns: Dict with ``path`` and ``name`` or ``None`` if not set.
    :rtype: dict[str, str] | None
    """
    ensure_upload_state()
    return st.session_state[REG_RENDER_UPLOADS].get(full_key)


def field_delete(full_key: str) -> None:
    """
    Delete the stored file (if any) for a given field key and clear state.

    :param full_key: Unique field key.
    :type full_key: str
    """
    ensure_upload_state()
    prev = st.session_state[REG_RENDER_UPLOADS].pop(full_key, None)
    if not prev:
        return
    try:
        p = Path(prev["path"])
        if p.exists():
            p.unlink()
    except Exception:
        pass
    unregister_path(prev["path"])
    # Back-compat: some code stores the raw upload under "<key>_image"
    st.session_state.pop(f"{full_key}_image", None)


def field_overwrite(
    full_key: str, uploaded_file: UploadedFile, folder: str = "uploads"
) -> UploadMeta:
    """
    Save (overwriting any previous) a single uploaded file for a field.

    :param full_key: Unique field key.
    :type full_key: str
    :param uploaded_file: Streamlit uploaded file object.
    :type uploaded_file: UploadedFile
    :param folder: Destination folder (created if missing).
    :type folder: str
    :returns: Metadata with ``path`` and ``name``.
    :rtype: UploadMeta
    """
    ensure_upload_state()
    folder_path = Path(folder)
    folder_path.mkdir(parents=True, exist_ok=True)

    safe_name = sanitize_filename(uploaded_file.name)
    save_path = folder_path / f"{full_key}_{safe_name}"

    # Remove previous file (if any) before writing the new one
    field_delete(full_key)

    with save_path.open("wb") as f:
        f.write(uploaded_file.getbuffer())

    register_path(str(save_path))
    meta: UploadMeta = {"path": str(save_path), "name": safe_name}
    st.session_state[REG_RENDER_UPLOADS][full_key] = meta
    return meta


# ---- Preview utilities -------------------------------------------------------

_PREVIEW_LANG_BY_EXT: Dict[str, str] = {
    ".txt": "text",
    ".csv": "csv",
    ".json": "json",
    ".md": "markdown",
    ".py": "python",
    ".c": "c",
    ".cpp": "cpp",
    ".h": "c",
}
_PREVIEW_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif"}
_PREVIEW_OTHER_EXTS = set(_PREVIEW_LANG_BY_EXT) | {".pdf"}


def preview_file(file_path: str) -> Optional[bool]:
    """
    Render a file preview in Streamlit based on file extension.

    Supported formats:

    - Images: ``.png``, ``.jpg``, ``.jpeg``, ``.gif``
    - PDF: rendered inline with ``<iframe>``
    - Text/code: ``.txt``, ``.csv``, ``.json``, ``.md``, ``.py``, ``.c``, ``.cpp``, ``.h``

    :param file_path: Filesystem path to the file.
    :type file_path: str
    :returns:
        ``True`` if file was previewed, ``False`` if extension not supported,
        ``None`` if an error occurred.
    :rtype: bool | None
    """
    try:
        path = Path(file_path)
        suffix = path.suffix.lower()
        if suffix in _PREVIEW_IMAGE_EXTS:
            st.image(str(path), use_container_width=True)
            return True
        if suffix == ".pdf":
            with path.open("rb") as f:
                base64_pdf = base64.b64encode(f.read()).decode("utf-8")
            st.markdown(
                f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="500px"></iframe>',
                unsafe_allow_html=True,
            )
            return True
        if suffix in _PREVIEW_OTHER_EXTS:
            lang = _PREVIEW_LANG_BY_EXT.get(suffix, "text")
            with path.open("r", encoding="utf-8", errors="ignore") as f:
                st.code(f.read(), language=lang)
            return True
        return False
    except Exception:
        return None


# ---- (Legacy) uploader remount helpers --------------------------------------
# These are perfect for remount-on-delete: we only bump when the user clicks Delete.


def uploader_key_for(field_key: str) -> str:
    """Return an uploader key coupled to a per-field nonce."""
    ensure_upload_state()
    nk = f"{field_key}__uploader_nonce"
    if nk not in st.session_state:
        st.session_state[nk] = 0
    return f"{field_key}__uploader_{st.session_state[nk]}"


def bump_uploader(field_key: str) -> None:
    """Increment the per-field nonce (forces the uploader to remount)."""
    ensure_upload_state()
    nk = f"{field_key}__uploader_nonce"
    st.session_state[nk] = st.session_state.get(nk, 0) + 1

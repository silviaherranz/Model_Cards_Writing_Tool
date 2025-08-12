import streamlit as st
import os
import re
import uuid
import json
import io
import zipfile
import base64
from pathlib import Path

ASSETS_ROOT = Path("assets") 
ASSETS_ROOT.mkdir(exist_ok=True)

def _slugify_filename(name: str) -> str:
    p = Path(name)
    base = re.sub(r"[^\w\-.]+", "_", p.stem).strip("_") or "file"
    return f"{base}{p.suffix.lower()}"

def _ensure_unique_path(dirpath: Path, filename: str) -> Path:
    dirpath.mkdir(parents=True, exist_ok=True)
    candidate = dirpath / _slugify_filename(filename)
    i = 1
    while candidate.exists():
        p = candidate
        candidate = dirpath / f"{p.stem}-{i}{p.suffix}"
        i += 1
    return candidate

def _init_registry():
    import streamlit as st
    st.session_state.setdefault("file_registry", {})          # id -> {name,label,relpath,source,field_key?}
    st.session_state.setdefault("appendix_uploads", {})       # backwards-compat for your UI
    st.session_state.setdefault("image_fields", {})           # field_key -> list[ {id,name,label,relpath} ]

def register_file(file, *, source: str, label: str = "", field_key: str | None = None) -> dict:
    """
    source: "appendix" or "image_field"
    field_key: only for image_field, a stable key like "card_metadata_cover_image"
    """
    _init_registry()
    subdir = "appendix" if source == "appendix" else f"images/{field_key or 'misc'}"
    save_dir = ASSETS_ROOT / subdir
    save_path = _ensure_unique_path(save_dir, file.name)
    with open(save_path, "wb") as f:
        f.write(file.getbuffer())
    rid = str(uuid.uuid4())
    rec = {
        "id": rid,
        "name": file.name,
        "label": label or "",
        "relpath": str(save_path.as_posix()),  
        "source": source,
        "field_key": field_key,
    }
    st.session_state.file_registry[rid] = rec
    return rec

def remove_registered_by_relpath(relpath: str):
    import streamlit as st
    try:
        Path(relpath).unlink(missing_ok=True)
    except Exception:
        pass
    for rid, rec in list(st.session_state.get("file_registry", {}).items()):
        if rec.get("relpath") == relpath:
            del st.session_state.file_registry[rid]

def image_field_uploader(
    field_key: str,
    ui_label: str,
    allow_multiple: bool = False,
    allowed_types=None,
    uploader_key: str | None = None,
    default_label: str = "",
    set_legacy_key: bool = True,
):
    import streamlit as st
    _init_registry()

    if allowed_types is None:
        allowed_types = ["png", "jpg", "jpeg", "gif", "svg", "webp"]

    st.markdown(f"**{ui_label}**")
    files = st.file_uploader(
        " ",
        type=allowed_types,
        accept_multiple_files=allow_multiple,
        key=(uploader_key or f"{field_key}__uploader"),
        label_visibility="collapsed",
    )

    # SIEMPRE trabajar con lista
    if allow_multiple:
        files_list = files or []
    else:
        files_list = [files] if files is not None else []

    st.session_state.image_fields.setdefault(field_key, [])
    recs = st.session_state.image_fields[field_key]

    # Añadir / Reemplazar
    if allow_multiple:
        for f in files_list:
            if f and not any(r["name"] == f.name for r in recs):
                rec = register_file(f, source="image_field", field_key=field_key)
                rec["label"] = default_label or rec.get("label", "")
                if rec["id"] in st.session_state.file_registry:
                    st.session_state.file_registry[rec["id"]]["label"] = rec["label"]
                recs.append(rec)
    else:
        if files_list:
            f = files_list[0]
            if f:
                # reemplaza si el nombre cambia
                if recs and recs[0]["name"] != f.name:
                    remove_registered_by_relpath(recs[0]["relpath"])
                    recs.clear()
                if not recs:
                    rec = register_file(f, source="image_field", field_key=field_key)
                    rec["label"] = default_label or rec.get("label", "")
                    if rec["id"] in st.session_state.file_registry:
                        st.session_state.file_registry[rec["id"]]["label"] = rec["label"]
                    recs.append(rec)

    # UI: etiqueta + botón Remove (NO borrar por ausencia)
    for i, rec in enumerate(list(recs)):
        c1, c2, c3 = st.columns([3, 5, 1])
        with c1:
            st.markdown(f"- {rec['name']}")
        with c2:
            lbl = st.text_input(
                "Label",
                value=rec.get("label", ""),
                key=f"{field_key}__label__{i}",
                placeholder="p. ej., Fig. 2: Diagrama del modelo",
                label_visibility="collapsed",
            )
            rec["label"] = lbl
            rid = rec.get("id")
            if rid and rid in st.session_state.file_registry:
                st.session_state.file_registry[rid]["label"] = lbl
        with c3:
            if st.button("Remove", key=f"{field_key}__rm__{i}"):
                remove_registered_by_relpath(rec["relpath"])
                recs.remove(rec)
                st.rerun()

    if allow_multiple:
        st.session_state[field_key] = [r["relpath"] for r in recs]
    else:
        st.session_state[field_key] = (recs[0]["relpath"] if recs else "")

    # compatibilidad legacy
    if set_legacy_key:
        if allow_multiple:
            st.session_state[f"{field_key}_image"] = [r["relpath"] for r in recs]
        else:
            st.session_state[f"{field_key}_image"] = (recs[0]["relpath"] if recs else "")

    st.divider()

    # helpers.py
def build_model_card_zip(schema) -> bytes:
    import streamlit as st
    from pathlib import Path
    from middleMan import parse_into_json

    json_str = parse_into_json(schema)
    data = json.loads(json_str) if isinstance(json_str, str) else json_str

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("model_card.json", json.dumps(data, indent=2))

        # appendix
        for item in data.get("appendix", []):
            rel = item.get("relpath")
            if rel and Path(rel).is_file():
                zf.write(rel, arcname=f"assets/appendix/{Path(rel).name}")

        # images por campo
        for field_key, items in data.get("assets", {}).get("images", {}).items():
            for it in items:
                rel = it.get("relpath")
                if rel and Path(rel).is_file():
                    zf.write(rel, arcname=f"assets/images/{field_key}/{Path(rel).name}")

    buf.seek(0)
    return buf.getvalue()


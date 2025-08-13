import io
import os
import json
import zipfile
from pathlib import Path
from uuid import uuid4

# Carpeta temporal local para guardar ficheros persistentes
BASE_DIR = Path(".")
IMPORTS_DIR = BASE_DIR / ".imports"
SECTIONS_DIR = BASE_DIR / "sections_files"
APPENDIX_DIR = BASE_DIR / "appendix_files"

for d in (IMPORTS_DIR, SECTIONS_DIR, APPENDIX_DIR):
    d.mkdir(parents=True, exist_ok=True)


def _safe_name(name: str) -> str:
    return (
        "".join(c for c in name if c.isalnum() or c in (" ", ".", "_", "-", "/"))
        .strip()
        .replace(" ", "_")
    )


def save_uploaded_to(path: Path, uploaded_file) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return path


def build_zip_from_state(json_data: dict, st):
    """
    Crea un ZIP (BytesIO) con:
      - model_card.json (json_data modificado con __files__)
      - archivos del appendix y de campos tipo Image guardados en rutas relativas
    """
    from pathlib import Path

    files_manifest = {}  # { logical_key_en_estado : ruta_relativa_en_zip }
    files_to_pack = []  # [(ruta_local, ruta_en_zip)]

    # 1) Appendix
    appendix = st.session_state.get("appendix_uploads", {}) or {}
    for original_name, meta in appendix.items():
        local_path = Path(meta["path"])
        if local_path.exists():
            arcname = f"appendix/{_safe_name(original_name)}"
            files_to_pack.append((local_path, arcname))
            files_manifest[f"appendix:{original_name}"] = arcname

    # 2) Campos tipo Image (guardamos en disco si aún no existe)
    for key, val in list(st.session_state.items()):
        # patrón acordado: <full_key>_image_path
        if key.endswith("_image_path"):
            local_path = Path(val)
            if local_path.exists():
                arcname = f"sections/{_safe_name(local_path.name)}"
                files_to_pack.append((local_path, arcname))
                logical = key  # usaremos la clave del estado para restaurar
                files_manifest[logical] = arcname

    # Añadimos el manifest al JSON
    json_data = dict(json_data)  # copia
    json_data["__files__"] = files_manifest

    # 3) Empaquetar
    bio = io.BytesIO()
    with zipfile.ZipFile(bio, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr(
            "model_card.json", json.dumps(json_data, ensure_ascii=False, indent=2)
        )
        for src, arc in files_to_pack:
            z.write(src, arcname=arc)
    bio.seek(0)
    return bio


def restore_from_json_or_zip(uploaded, st):
    """
    Acepta un .json o .zip. Rellena st.session_state con:
      - datos del JSON (devuelve el dict para que tú lo uses)
      - ficheros, grabando paths en *_image_path y appendix_uploads
    """
    import json
    import zipfile

    if uploaded.name.lower().endswith(".json"):
        data = json.loads(uploaded.read().decode("utf-8"))
        _restore_files_from_manifest(
            None, data, st
        )  # no hay archivos, pero deja limpio el estado
        return data

    # ZIP
    with zipfile.ZipFile(uploaded) as z:
        tmp_root = IMPORTS_DIR / f"import_{uuid4().hex}"
        z.extractall(tmp_root)

        json_path = tmp_root / "model_card.json"
        if not json_path.exists():
            # fallback: algún nombre alternativo
            for cand in tmp_root.glob("*.json"):
                json_path = cand
                break
        data = json.loads(json_path.read_text(encoding="utf-8"))

        _restore_files_from_manifest(tmp_root, data, st)
        return data


def _restore_files_from_manifest(root: Path | None, data: dict, st):
    """
    Reconstruye appendix_uploads y *_image_path desde data["__files__"].
    Si root es None (carga de JSON plano), solo prepara estructuras vacías.
    """
    files_map = data.get("__files__", {}) or {}

    # Asegura estructuras mínimas
    if "appendix_uploads" not in st.session_state:
        st.session_state.appendix_uploads = {}

    # Appendix
    for logical, rel in files_map.items():
        if logical.startswith("appendix:"):
            original_name = logical.split("appendix:", 1)[1]
            if root is None:
                # JSON sin archivos -> no podemos restaurar contenidos
                continue
            src = (root / rel).resolve()
            if src.exists():
                # Copiamos el archivo a una zona conocida
                dst = APPENDIX_DIR / _safe_name(src.name)
                dst.write_bytes(src.read_bytes())
                st.session_state.appendix_uploads[original_name] = {
                    "custom_label": "",  # si lo guardas en tu JSON, úsalo aquí
                    "path": str(dst),
                }

    # Campos tipo Image
    for logical, rel in files_map.items():
        if logical.endswith("_image_path"):
            if root is None:
                # no hay archivo que restaurar
                continue
            src = (root / rel).resolve()
            if src.exists():
                dst = SECTIONS_DIR / _safe_name(src.name)
                dst.write_bytes(src.read_bytes())
                st.session_state[logical] = str(dst)

# helpers_appendix_link.py
from pathlib import Path
from pack_io import APPENDIX_DIR

def ensure_appendix_entry(st, src_path: Path, original_name: str, label: str = "") -> str:
    """
    Copy src_path to the Appendix folder (if needed), register in st.session_state.appendix_uploads,
    set label, and return the 'appendix original name' used as the key.
    """
    APPENDIX_DIR.mkdir(parents=True, exist_ok=True)
    if "appendix_uploads" not in st.session_state:
        st.session_state.appendix_uploads = {}

    # Use the original name as the dictionary key (what the UI shows)
    key_name = original_name

    # If the same key exists, just update path/label; else copy file first
    dst = APPENDIX_DIR / src_path.name
    if not dst.exists():
        dst.write_bytes(src_path.read_bytes())

    st.session_state.appendix_uploads[key_name] = {
        "custom_label": label or "",
        "path": str(dst),
    }
    return key_name

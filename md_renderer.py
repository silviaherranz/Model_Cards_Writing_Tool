import os
import re
import base64
import mimetypes
import streamlit as st
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape, TemplateNotFound
from json_template import DATA_INPUT_OUTPUT_TS
from templates.sections import SECTION_REGISTRY, TEMPLATES_DIR
from main import extract_evaluations_from_state  


def _format_date(raw, in_fmt="%Y%m%d", out_fmt="%Y/%m/%d"):
    if not raw:
        return None
    try:
        return datetime.strptime(raw, in_fmt).strftime(out_fmt)
    except Exception:
        return raw


def _to_data_uri(mime, data):
    """Return data: URI for small images."""
    try:
        b64 = base64.b64encode(data).decode("ascii")
        return f"data:{mime or 'application/octet-stream'};base64,{b64}"
    except Exception:
        return None


def _file_to_data_uri(path, fallback_mime=None):
    """Open a local file and return a data: URI if it's an image."""
    try:
        mime, _ = mimetypes.guess_type(path)
        mime = mime or fallback_mime
        if not mime or not mime.lower().startswith("image/"):
            return None
        with open(path, "rb") as f:
            data = f.read()
        return _to_data_uri(mime, data)
    except Exception:
        return None


def _normalize_file_from_key(full_key):
    """
    Look up saved file in st.session_state.render_uploads[full_key] and return:
      {"name": <str>, "type": <mime>, "url": <data_uri_if_image_or_None>}
    """
    uploads = st.session_state.get("render_uploads", {})
    info = uploads.get(full_key)
    if not info:
        return None

    path = info.get("path")
    name = info.get("name") or (os.path.basename(path) if path else None)

    # Best-effort MIME detection
    mime, _ = mimetypes.guess_type(name or "")
    # Generate data URI if it's an image and file exists
    url = _file_to_data_uri(path, fallback_mime=mime) if path and os.path.exists(path) else None

    return {"name": name, "type": mime, "url": url}


def _collect_hw_sw_from_state():
    """Collect hw_and_sw_* keys into a nested dict."""
    hw = {}
    prefix = "hw_and_sw_"
    for key, val in st.session_state.items():
        if key.startswith(prefix):
            hw[key[len(prefix):]] = val
    return hw


def _collect_learning_architectures_from_state():
    """
    Collect learning architectures from session_state.
    Supports both key styles:
      - learning_architecture_{i}_{field}
      - technical_specifications_learning_architecture_{i}_{field}
    Respects 'learning_architecture_forms' to pre-register empty indices.
    Normalizes 'architecture_figure' via _normalize_file_from_key(...).
    """
    grouped = {}
    patterns = [
        re.compile(r'^learning_architecture_(\d+)_(.+)$'),
        re.compile(r'^technical_specifications_learning_architecture_(\d+)_(.+)$'),
    ]

    # Gather all keys that match either pattern
    for key, val in st.session_state.items():
        for pat in patterns:
            m = pat.match(key)
            if m:
                idx = int(m.group(1))
                field = m.group(2)
                grouped.setdefault(idx, {})[field] = val
                break

    forms = st.session_state.get("learning_architecture_forms") or {}
    for i in range(len(forms)):
        grouped.setdefault(i, {})

    result = []
    for i in sorted(grouped):
        la = grouped[i]
        la["id"] = i

        for k in (
            f"learning_architecture_{i}_architecture_figure",
            f"technical_specifications_learning_architecture_{i}_architecture_figure",
        ):
            norm = _normalize_file_from_key(k)
            if norm:
                la["architecture_figure"] = norm
                break

        result.append(la)

    return result


def _normalize_render_key_to_fileobj(full_key: str):
    """Return normalized file object from st.session_state.render_uploads[full_key], if present."""
    uploads = st.session_state.get("render_uploads", {})
    info = uploads.get(full_key)
    if not info:
        return None
    path = info.get("path")
    name = info.get("name") or (os.path.basename(path) if path else None)
    mime, _ = mimetypes.guess_type(name or "")
    url = _file_to_data_uri(path, fallback_mime=mime) if path and os.path.exists(path) else None
    return {"name": name, "type": mime, "url": url}

# render_ui.py (or wherever your render helpers live)

def _prime_normalized_uploads():
    uploads = st.session_state.get("render_uploads", {}) or {}
    norm = {}
    for key in uploads.keys():
        try:
            obj = _normalize_render_key_to_fileobj(key)
            if obj:
                norm[key] = obj
        except Exception:
            pass
    st.session_state["normalized_uploads"] = norm



def build_context_for_prefix(prefix: str) -> dict:
    ctx = {}
    try:
        if isinstance(prefix, str):
            for k, v in st.session_state.items():
                if k.startswith(prefix):
                    ctx[k] = v

        if prefix == "card_metadata_":
            if "card_metadata_card_creation_date" in ctx:
                ctx["card_metadata_card_creation_date"] = _format_date(
                    ctx.get("card_metadata_card_creation_date")
                )

        if prefix == "model_basic_information_":
            if "model_basic_information_creation_date" in ctx:
                ctx["model_basic_information_creation_date"] = _format_date(
                    ctx.get("model_basic_information_creation_date")
                )

        if prefix == "technical_specifications_":
            ctx["learning_architectures"] = _collect_learning_architectures_from_state()

            hw = _collect_hw_sw_from_state()
            if hw:
                ctx["hw_and_sw"] = hw

            if "technical_specifications_pre-processing" in ctx:
                ctx["technical_specifications_pre_processing"] = ctx["technical_specifications_pre-processing"]
            if "technical_specifications_post-processing" in ctx:
                ctx["technical_specifications_post_processing"] = ctx["technical_specifications_post-processing"]

            for k in ["technical_specifications_model_pipeline_figure"]:
                norm = _normalize_file_from_key(k)
                if norm:
                    ctx[k] = norm

            for i, la in enumerate(ctx.get("learning_architectures", [])):
                la_key1 = f"learning_architecture_{i}_architecture_figure"
                la_key2 = f"technical_specifications_learning_architecture_{i}_architecture_figure"
                norm = _normalize_file_from_key(la_key1) or _normalize_file_from_key(la_key2)
                if norm:
                    la["architecture_figure"] = norm

        if prefix == "training_data_":
            # Make labels available to the template
            ctx["DATA_INPUT_OUTPUT_TS"] = DATA_INPUT_OUTPUT_TS

            # Normalize the uploaded loss figure
            norm = _normalize_file_from_key("training_data_train_and_validation_loss_curves")
            if norm:
                ctx["training_data_train_and_validation_loss_curves"] = norm
            modality_entries = []
            for key, value in st.session_state.items():
                if key.endswith("model_inputs") and isinstance(value, list):
                    for item in value:
                        modality_entries.append({"modality": item, "source": "model_inputs"})
                elif key.endswith("model_outputs") and isinstance(value, list):
                    for item in value:
                        modality_entries.append({"modality": item, "source": "model_outputs"})
            io_details = []
            for entry in modality_entries:
                clean = entry["modality"].strip().replace(" ", "_").lower()
                source = entry["source"]
                detail = {"entry": entry["modality"], "source": source}
                for field_key in DATA_INPUT_OUTPUT_TS: 
                    per_mod_key = f"training_data_{clean}_{source}_{field_key}"
                    val = (
                        st.session_state.get(per_mod_key)
                        or st.session_state.get(f"_{per_mod_key}")
                        or st.session_state.get(f"__{per_mod_key}")
                        or ""
                    )
                    if not val:
                        global_key = f"training_data_{field_key}"
                        val = st.session_state.get(global_key, "")

                    detail[field_key] = val
                io_details.append(detail)

            ctx["training_data_inputs_outputs_technical_specifications"] = io_details

        if prefix == "evaluations_":
            _prime_normalized_uploads()
            
            ev = extract_evaluations_from_state()
            ctx["evaluations"] = ev if isinstance(ev, list) else []
            for e in ctx["evaluations"]:
                if "evaluation_date" in e:
                    e["evaluation_date"] = _format_date(e.get("evaluation_date"))

            task_val = st.session_state.get("task", "")
            ctx["task"] = task_val

            try:
                from main import TASK_METRIC_MAP
                task_key = (task_val or "").strip()
                ctx["metric_groups"] = TASK_METRIC_MAP.get(task_key, [])
            except Exception:
                ctx["metric_groups"] = []
            
        if prefix == "appendix_":
            appendix_files = []
            for key, info in st.session_state.appendix_uploads.items():
                norm = _normalize_file_from_key(f"appendix_{key}")
                if norm:
                    appendix_files.append({
                        "label": info.get("custom_label") or "",
                        "file": norm,
                    })
            ctx["appendix_files"] = appendix_files



    except Exception:
        pass

    return ctx

""" def _env():
    return Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(enabled_extensions=(), default_for_string=False),
        trim_blocks=True,
        lstrip_blocks=True,
    ) """
def _env():
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(enabled_extensions=(), default_for_string=False),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.globals["DATA_INPUT_OUTPUT_TS"] = DATA_INPUT_OUTPUT_TS

    # Figure field per metric group
    env.globals["FIG_FIELD"] = {
        "type_ism": "figure_ism",
        "type_dose_dm": "figure_dm",
        "type_gm_seg": "figure_gm_seg",
        "type_dose_dm_seg": "figure_dm_seg",
        "type_dose_dm_dp": "figure_dm_dp",
        "type_metrics_other": "figure_other",
    }
    return env

def render_section_md(section_id: str) -> str:
    cfg = SECTION_REGISTRY[section_id]
    ctx = build_context_for_prefix(cfg["prefix"])
    if not isinstance(ctx, dict):
        ctx = {}
    try:
        return _env().get_template(cfg["template"]).render(**ctx)
    except TemplateNotFound:
        raise FileNotFoundError(f"Template not found: {cfg['template']}")


def render_full_model_card_md(master_template: str = "model_card_master.md.j2") -> str:
    sections_md = {sid: render_section_md(sid) for sid in SECTION_REGISTRY}
    appendix_ctx = build_context_for_prefix("appendix_") or {}
    return _env().get_template(master_template).render(
        sections=sections_md,
        appendix_files=appendix_ctx.get("appendix_files", []),
    )


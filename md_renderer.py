import os
from pathlib import Path
import re
import base64
import mimetypes
import streamlit as st
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape, TemplateNotFound
from json_template import DATA_INPUT_OUTPUT_TS
from templates.sections import SECTION_REGISTRY, TEMPLATES_DIR
from main import extract_evaluations_from_state
import markdown
from weasyprint import HTML, CSS

def build_appendix_files_context():
    items = []
    uploads = getattr(st.session_state, "appendix_uploads", {}) or {}
    for original_name, data in uploads.items():
        stored_key = data.get("stored_name")
        norm = _normalize_render_key_to_fileobj(stored_key) if stored_key else None
        mime = (norm or {}).get("type")
        is_image = bool(mime and mime.lower().startswith("image/"))
        items.append(
            {
                "label": (data.get("custom_label") or "").strip(),
                "file": {
                    "name": original_name,
                    "key": stored_key,
                    "type": mime,
                    "url": (norm or {}).get("url"),  # data URI for images
                    "is_image": is_image,
                },
            }
        )
    return items


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
    url = (
        _file_to_data_uri(path, fallback_mime=mime)
        if path and os.path.exists(path)
        else None
    )

    return {"name": name, "type": mime, "url": url}


def _collect_hw_sw_from_state():
    """Collect hw_and_sw_* keys into a nested dict."""
    hw = {}
    prefix = "hw_and_sw_"
    for key, val in st.session_state.items():
        if key.startswith(prefix):
            hw[key[len(prefix) :]] = val
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
        re.compile(r"^learning_architecture_(\d+)_(.+)$"),
        re.compile(r"^technical_specifications_learning_architecture_(\d+)_(.+)$"),
    ]

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
    url = (
        _file_to_data_uri(path, fallback_mime=mime)
        if path and os.path.exists(path)
        else None
    )
    return {"name": name, "type": mime, "url": url}


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

            ctx["model_basic_information_name"] = st.session_state.get(
                "model_basic_information_name", ""
            )

            ctx["task"] = st.session_state.get("task", "")


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
                ctx["technical_specifications_pre_processing"] = ctx[
                    "technical_specifications_pre-processing"
                ]
            if "technical_specifications_post-processing" in ctx:
                ctx["technical_specifications_post_processing"] = ctx[
                    "technical_specifications_post-processing"
                ]

            for k in ["technical_specifications_model_pipeline_figure"]:
                norm = _normalize_file_from_key(k)
                if norm:
                    ctx[k] = norm

            for i, la in enumerate(ctx.get("learning_architectures", [])):
                la_key1 = f"learning_architecture_{i}_architecture_figure"
                la_key2 = f"technical_specifications_learning_architecture_{i}_architecture_figure"
                norm = _normalize_file_from_key(la_key1) or _normalize_file_from_key(
                    la_key2
                )
                if norm:
                    la["architecture_figure"] = norm

        if prefix == "training_data_":
            ctx["DATA_INPUT_OUTPUT_TS"] = DATA_INPUT_OUTPUT_TS

            norm = _normalize_file_from_key(
                "training_data_train_and_validation_loss_curves"
            )
            if norm:
                ctx["training_data_train_and_validation_loss_curves"] = norm
            modality_entries = []
            for key, value in st.session_state.items():
                if key.endswith("model_inputs") and isinstance(value, list):
                    for item in value:
                        modality_entries.append(
                            {"modality": item, "source": "model_inputs"}
                        )
                elif key.endswith("model_outputs") and isinstance(value, list):
                    for item in value:
                        modality_entries.append(
                            {"modality": item, "source": "model_outputs"}
                        )
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

            ctx["normalized_uploads"] = st.session_state.get("normalized_uploads", {})

    except Exception:
        pass

    return ctx


def _env():
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(enabled_extensions=(), default_for_string=False),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.globals["DATA_INPUT_OUTPUT_TS"] = DATA_INPUT_OUTPUT_TS

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
    
    appendix_files = build_appendix_files_context()

    return (
        _env()
        .get_template(master_template)
        .render(
            sections=sections_md,
            appendix_files=appendix_files,
        )
    )



DEFAULT_PDF_CSS = """
/* ============================
   PDF HEADERS: H1 normal, H2 bloque azul
   ============================ */

/* --- Page setup --- */
@page {
  size: A4;
  margin: 18mm 14mm 20mm 14mm;
  @bottom-center {
    content: "Página " counter(page) " de " counter(pages);
    font-size: 8.6px;
    color: #6b7280;
  }
}

/* --- Palette --- */
:root{
  --brand: #0a2e5d;     /* azul corporativo */
  --accent: #c7d6ea;    /* azul claro para acentos */
  --text: #1f2937;
  --muted: #4b5563;
  --muted-2: #6b7280;
  --border: #e5e7eb;
  --bg-soft: #f8fafc;
  --bg-soft-2: #f3f4f6;
}

/* --- Base text (-0.4pt) --- */
html, body {
  font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, "Noto Sans", sans-serif;
  font-size: 9.6pt;  
  line-height: 1.5;
  color: var(--text);
}
p, li { hyphens: auto; margin: 0.35em 0 0.6em; }

/* --- H1 (normal, solo texto) --- */
h1 {
  font-size: 15.6pt;
  font-weight: 700;
  color: var(--brand);
  margin: 1em 0 0.6em;
  string-set: section content();
}

/* --- H2 (bloque sólido azul) --- */
h2 {
  font-size: 13.6pt;
  font-weight: 700;
  color: #fff;
  background: var(--brand);
  border-radius: 4px;
  padding: 6px 10px;
  margin: 0.9em 0 0.55em;
  string-set: section content();
}

/* --- H3–H5 (tipográficos simples) --- */
h3 { font-size: 12.1pt; font-weight: 600; color: var(--text); }
h4 { font-size: 10.9pt; font-weight: 600; color: var(--muted); }
h5 { font-size: 10.1pt; font-weight: 600; color: var(--muted-2); }

/* --- Lists con guiones elegantes --- */
ul { 
  margin: 0.3em 0 0.7em 1.2em; 
  list-style: none;
  padding-left: 0;
}
ul li {
  margin: 0.2em 0;
  padding-left: 1em;
  position: relative;
}
ul li::before {
  content: "–"; 
  position: absolute;
  left: 0;
  color: var(--brand);
  font-weight: 600;
}

/* --- Tables (versión profesional limpia) --- */
table {
  border-collapse: collapse;
  width: 100%;
  margin: 0.5em 0 1em;
  table-layout: fixed;
  font-size: 9.8pt;
  border: 1px solid var(--border);
  border-radius: 6px;
  overflow: hidden;
}

caption { 
  caption-side: top; 
  text-align: left; 
  font-weight: 700; 
  color: var(--brand); 
  padding: 6px 0; 
}

thead th {
  background: var(--brand); /* azul corporativo sólido */
  color: #fff;
  font-weight: 600;
  text-align: left;
}

th, td {
  border: 1px solid var(--border);
  padding: 6px 8px;
  vertical-align: top;
  word-wrap: break-word;
}

tbody tr:nth-child(even) td { 
  background: #f9fafb; /* gris muy claro */
}

tbody tr:hover td { 
  background: #f3f6fb; /* hover suave, solo digital */
}

/* --- Badges con acento --- */
.badge {
  display: inline-block;
  font-size: 8.8pt;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: var(--accent);
  color: var(--brand);
}

"""

def render_markdown_to_html(md_text: str, extra_css: str = None) -> str:
    """
    Convert Markdown to HTML, lightly styled. Returns a complete HTML string.
    You can inline <style>CSS</style> for WeasyPrint consumption.
    """
    # Enable tables and sane Markdown features
    html_body = markdown.markdown(
        md_text,
        extensions=[
            "tables",
            "fenced_code",
            "toc",
            "attr_list",
            "sane_lists",
            # add "md_in_html" if you embed HTML in Markdown
        ],
        output_format="html5",
    )

    css_block = f"<style>{DEFAULT_PDF_CSS}</style>"
    if extra_css:
        css_block += f"<style>{extra_css}</style>"

    # Simple HTML skeleton
    html = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Model Card</title>
{css_block}
</head>
<body>
{html_body}
</body>
</html>"""
    return html


def save_model_card_pdf(
    path: str = "model_card.pdf",
    *,
    css_text: str = DEFAULT_PDF_CSS,
    css_file: str = None,
    base_url: str = None,
) -> str:
    """
    Render the current model card to a styled PDF.

    Args:
        path: output PDF path
        css_text: optional extra CSS string to override/extend DEFAULT_PDF_CSS
        css_file: optional path to a CSS file for additional rules
        base_url: base path for resolving relative images/links, e.g., os.getcwd()

    Returns:
        The output PDF path.
    """
    md = render_full_model_card_md()
    html = render_markdown_to_html(md, extra_css=css_text)

    # Build CSS objects list for WeasyPrint
    css_list = []
    if css_file:
        css_list.append(CSS(filename=css_file))

    if css_text:
        css_list.append(CSS(string=css_text))
    # DEFAULT_PDF_CSS and css_text are already inlined in <style>, so no need to add here.
    # But you can also provide them as external CSS objects if you prefer:
    # css_list.append(CSS(string=DEFAULT_PDF_CSS))
    # if css_text: css_list.append(CSS(string=css_text))

    # base_url lets WeasyPrint resolve relative URLs (e.g., local images)
    HTML(string=html, base_url=base_url).write_pdf(path, stylesheets=css_list)
    return path

import streamlit as st
from jinja2 import Environment, FileSystemLoader, select_autoescape, TemplateNotFound
from datetime import datetime
from pathlib import Path
from templates.sections import SECTION_REGISTRY, TEMPLATES_DIR

def _format_date(raw, in_fmt="%Y%m%d", out_fmt="%Y/%m/%d"):
    if not raw:
        return None
    try:
        return datetime.strptime(raw, in_fmt).strftime(out_fmt)
    except Exception:
        return raw

def build_context_for_prefix(prefix: str) -> dict:
    ctx = {k: v for k, v in st.session_state.items() if k.startswith(prefix)}

    # Ajustes por sección (ambas guardan la fecha como YYYYMMDD → formatear legible)
    # Card Metadata → card_metadata_card_creation_date
    if prefix == "card_metadata_" and "card_metadata_card_creation_date" in ctx:
        # tu card_metadata.py guarda la fecha como YYYYMMDD tras date_input. :contentReference[oaicite:2]{index=2}
        ctx["card_metadata_card_creation_date"] = _format_date(
            ctx.get("card_metadata_card_creation_date")
        )

    # Model Basic Information → model_basic_information_creation_date
    if prefix == "model_basic_information_" and "model_basic_information_creation_date" in ctx:
        # tu model_basic_information.py también la transforma a YYYYMMDD. :contentReference[oaicite:3]{index=3}
        ctx["model_basic_information_creation_date"] = _format_date(
            ctx.get("model_basic_information_creation_date")
        )

    return ctx

def _env():
    return Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(enabled_extensions=(), default_for_string=False),
        trim_blocks=True,
        lstrip_blocks=True,
    )

def render_section_md(section_id: str) -> str:
    cfg = SECTION_REGISTRY[section_id]
    ctx = build_context_for_prefix(cfg["prefix"])
    try:
        return _env().get_template(cfg["template"]).render(**ctx)
    except TemplateNotFound:
        raise FileNotFoundError(f"Plantilla no encontrada: {cfg['template']}")

def render_full_model_card_md(master_template: str = "model_card_master.md.j2") -> str:
    sections_md = {sid: render_section_md(sid) for sid in SECTION_REGISTRY}
    return _env().get_template(master_template).render(sections=sections_md)


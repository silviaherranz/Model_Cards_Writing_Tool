# Drop-in addition for md_renderer.py (no `io`, no `yaml`)
# -----------------------------------------------------------------------------
# This adds a small, dependency-free YAML front-matter builder and a public
# function `render_hf_readme()` that returns a Hugging Face–ready README.md:
#   - YAML metadata at top (pipeline_tag, license, datasets, etc.)
#   - Markdown body rendered via the existing Jinja sections
# You can delete your old `build_readme_from_card` and its `import io, import yaml`.
# -----------------------------------------------------------------------------
from typing import Any, Dict, List, Union
import html

from md_renderer import render_full_model_card_md

# --- Minimal YAML front matter builder (no external deps) ---------------------
Scalar = Union[str, int, float, bool]
YAMLish = Union[Scalar, List[Scalar], Dict[str, Any]]


def _is_nonempty(x: Any) -> bool:
    if x is None:
        return False
    if isinstance(x, str):
        return x.strip() != ""
    if isinstance(x, (list, dict, tuple, set)):
        return len(x) > 0
    return True


def _yaml_escape_scalar(v: Scalar) -> str:
    """Conservative string quoting to avoid YAML pitfalls without a parser."""
    if isinstance(v, bool):
        return "true" if v else "false"
    s = str(v)
    # Quote if it looks like YAML boolean/null/number, starts with special char,
    # contains colon, hash, or leading/trailing whitespace.
    needs_quote = (
        s.strip() != s
        or s == ""
        or any(s.lower() == t for t in ["null", "~", "true", "false", "yes", "no"])
        or s[0] in "-?:@{}[],&*!#|>%'\"`"
        or any(ch in s for ch in [":", "#"])
    )
    if needs_quote:
        # Use double quotes and escape embedded quotes/backslashes
        s = s.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{s}"'
    return s


def _emit_yaml_lines(key: str, value: YAMLish, indent: int = 0) -> List[str]:
    """Emit simple YAML for scalars, lists, and flat dicts."""
    sp = " " * indent
    out: List[str] = []

    if isinstance(value, dict):
        # Only include non-empty children
        items = [(k, v) for k, v in value.items() if _is_nonempty(v)]
        if not items:
            return out
        out.append(f"{sp}{key}:")
        for k, v in items:
            out.extend(_emit_yaml_lines(str(k), v, indent + 2))
        return out

    if isinstance(value, (list, tuple, set)):
        seq = [v for v in value if _is_nonempty(v)]
        if not seq:
            return out
        out.append(f"{sp}{key}:")
        for v in seq:
            if isinstance(v, (list, dict)):
                # flatten nested list/dict under a dash
                out.append(f"{sp}  -")
                if isinstance(v, dict):
                    for k2, v2 in v.items():
                        if _is_nonempty(v2):
                            out.extend(_emit_yaml_lines(str(k2), v2, indent + 4))
                else:
                    for i2, v2 in enumerate(v):
                        out.extend(_emit_yaml_lines(str(i2), v2, indent + 4))
            else:
                out.append(f"{sp}  - {_yaml_escape_scalar(v)}")
        return out

    # scalar
    out.append(f"{sp}{key}: {_yaml_escape_scalar(value)}")
    return out


def _build_front_matter(meta: Dict[str, YAMLish]) -> str:
    # Remove empties + keep insertion order
    compact = {k: v for k, v in meta.items() if _is_nonempty(v)}
    lines: List[str] = ["---"]
    for k, v in compact.items():
        lines.extend(_emit_yaml_lines(k, v))
    lines.append("---\n")
    return "\n".join(lines)


# --- Metadata collection helpers --------------------------------------------

HF_META_KEYS = {
    "pipeline_tag",
    "library_name",
    "license",
    "license_name",
    "license_link",
    "language",
    "tags",
    "thumbnail",
    "datasets",
    "metrics",
    "base_model",
    "base_models",  # if caller prefers plural
    "new_version",
    "model-index",
}


def _norm_list(v):
    if isinstance(v, str):
        parts = [p.strip() for p in v.split(",")]
        return [p for p in parts if p]
    if isinstance(v, (list, tuple, set)):
        return [str(x) for x in v if _is_nonempty(x)]
    return []


def _extract_metrics_from_evaluations(ss) -> List[str]:
    """Return a flat list of metric identifiers from your evaluations state.
    Expected shapes supported:
      - ss['evaluations'] = [{ 'metric' or 'metric_name': 'ai2_arc', 'value': 64.5, ... }, ...]
      - or nested under ss['evaluations'][i]['metrics'] = [{'name': 'ai2_arc', ...}, ...]
    Only the names/identifiers are returned for YAML `metrics:`.
    """
    metrics: List[str] = []
    evals = ss.get("evaluations") or []
    for e in evals:
        if not isinstance(e, dict):
            continue
        # Common shapes
        name = e.get("metric_name") or e.get("metric")
        if name:
            metrics.append(str(name))
        # OpenLLM-like list under 'metrics'
        for m in _norm_list(e.get("metrics") or []):
            if isinstance(m, dict):
                mname = m.get("name") or m.get("type")
                if mname:
                    metrics.append(str(mname))
            elif isinstance(m, str):
                metrics.append(m)
    # Deduplicate while preserving order
    seen = set()
    out = []
    for m in metrics:
        if m not in seen:
            seen.add(m)
            out.append(m)
    return out


def _extract_base_model_from_training_data(ss) -> str | List[str] | None:
    """Pull base model from training data. You said it's `model_name` in training data.
    Supports either a single string or a list.
    """
    td = ss.get("training_data") or {}
    base = td.get("model_name") or ss.get("base_model") or ss.get("base_models")
    if not base:
        return None
    if isinstance(base, (list, tuple, set)):
        return [str(x) for x in base if _is_nonempty(x)]
    return str(base)


def _collect_hf_meta_from_session_state() -> Dict[str, YAMLish]:
    """Collect *your* specific fields based on your note:
    - pipeline_tag comes from your `pipeline_tag` (or `task` fallback)
    - library_name comes from your libraries/dependencies (first item)
    - language is English
    - metrics are extracted from evaluations
    - base_model comes from training_data.model_name
    - new_version left empty unless provided explicitly
    """
    try:
        import streamlit as st
    except Exception:
        return {}

    ss = getattr(st, "session_state", {}) or {}

    # pipeline_tag
    pipeline_tag = (
        ss.get("pipeline_tag")
        or ss.get("task")
        or ""
    )
    if isinstance(pipeline_tag, str):
        pipeline_tag = pipeline_tag.strip().lower().replace(" ", "-") or None

    # library_name (prefer first library from a list), keep others as tags
    libs = _norm_list(ss.get("libraries") or ss.get("dependencies") or ss.get("library_name"))
    library_name = libs[0] if libs else None
    extra_lib_tags = libs[1:] if len(libs) > 1 else []

    # license (optional if you have it elsewhere)
    license_val = ss.get("license") or ss.get("model_basic_information_software_license")

    # language fixed to English as requested
    language = ["en"]

    # tags (merge any provided tags with extra libs)
    tags = _norm_list(ss.get("tags")) + extra_lib_tags

    # datasets (optional; if you already capture them in training_data)
    datasets = _norm_list(ss.get("datasets") or (ss.get("training_data") or {}).get("datasets"))

    # metrics from evaluations
    metrics = _extract_metrics_from_evaluations(ss)

    # base_model from training_data.model_name
    base_model = _extract_base_model_from_training_data(ss)

    # optional fields
    thumbnail = ss.get("thumbnail")
    new_version = ss.get("new_version")  # leave unset if you don't have it

    meta: Dict[str, YAMLish] = {
        "pipeline_tag": pipeline_tag,
        "library_name": library_name,
        "license": license_val,
        "language": language,
        "tags": tags,
        "thumbnail": thumbnail,
        "datasets": datasets,
        "metrics": metrics,
        "base_model": base_model,
        "new_version": new_version,
    }

    # If you already build a proper model-index elsewhere, include it
    if _is_nonempty(ss.get("model-index") or ss.get("model_index")):
        meta["model-index"] = ss.get("model-index") or ss.get("model_index")

    return {k: v for k, v in meta.items() if _is_nonempty(v)}

# --- Public API ---------------------------------------------------------------

def render_hf_readme(
    *,
    meta: Dict[str, YAMLish] | None = None,
    master_template: str = "model_card_master.md.j2",
) -> str:
    """
    Return a complete Hugging Face README.md string consisting of:
      1) YAML metadata front matter (discoverability on the Hub)
      2) Markdown body rendered from your existing Jinja sections

    Args:
        meta: Optional explicit metadata dict following HF keys. If omitted,
              we'll try to extract reasonable defaults from Streamlit state.
              Supported keys include (subset of HF spec):
                - pipeline_tag, library_name, license, license_name, license_link
                - language (list of ISO 639-1 codes)
                - tags (list of strings)
                - thumbnail (URL)
                - datasets (list of hub IDs)
                - metrics (list of metric IDs)
                - base_model (string or list of hub IDs)
                - new_version (hub ID)
                - model-index (structured evals per HF spec)
        master_template: Existing Jinja template used by render_full_model_card_md.

    Returns:
        Complete README.md text (YAML front matter + Markdown body).
    """
    # 1) Collect metadata (caller wins, then session_state fallback)
    session_meta = _collect_hf_meta_from_session_state()
    merged_meta: Dict[str, YAMLish] = {}
    for k in HF_META_KEYS:
        if meta and k in meta and _is_nonempty(meta[k]):
            merged_meta[k] = meta[k]
        elif k in session_meta:
            merged_meta[k] = session_meta[k]

    # Normalize base_model / base_models
    if "base_models" in merged_meta and "base_model" not in merged_meta:
        merged_meta["base_model"] = merged_meta.pop("base_models")

    # 2) Render markdown body with your existing pipeline
    body_md = render_full_model_card_md(master_template=master_template)

    # 3) Build YAML front matter and concatenate
    fm = _build_front_matter(merged_meta)
    return f"{fm}{body_md}"  # final README.md


# --- Convenience: save to disk ------------------------------------------------

def save_hf_readme(
    path: str = "README.md",
    *,
    meta: Dict[str, YAMLish] | None = None,
    master_template: str = "model_card_master.md.j2",
) -> str:
    """Render and write the HF model card README.md to `path`.

    Returns the written path.
    """
    content = render_hf_readme(meta=meta, master_template=master_template)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path

# --- Upload to Hugging Face Hub ----------------------------------------------

def upload_readme_to_hub(
    repo_id: str,
    *,
    token: str | None = None,
    readme_path: str = "README.md",
    create_if_missing: bool = True,
) -> None:
    """Upload README.md to a model repo on the Hugging Face Hub.

    - repo_id: e.g. "your-username/your-model"
    - token: HF token with write access (or rely on cached login)
    - set create_if_missing=False if repo already exists
    """
    try:
        from huggingface_hub import HfApi, create_repo
    except Exception as e:
        raise RuntimeError(
            "huggingface_hub is required. Install with `pip install huggingface_hub`."
        ) from e

    api = HfApi(token=token)

    if create_if_missing:
        try:
            create_repo(repo_id=repo_id, token=token, repo_type="model", exist_ok=True)
        except Exception:
            # Ignore if it already exists or user has no right to create
            pass

    api.upload_file(
        path_or_fileobj=readme_path,
        path_in_repo="README.md",
        repo_id=repo_id,
        repo_type="model",
    )

# --- Optional: build `model-index` from your existing evaluations -------------
# If you want us to auto-build a minimal "model-index" based on the current
# `evaluations` in session_state, you can adapt this helper and inject it into
# `meta` when calling `render_hf_readme(meta=...)`.

def build_model_index_from_evaluations(model_name: str) -> Dict[str, Any] | None:
    """Best-effort conversion of your `evaluations` data into HF model-index.

    Expects `extract_evaluations_from_state()` to return a list of evaluation
    dicts with at least (task, dataset, metric name, value). Adjust mapping to
    your actual schema.
    """
    try:
        from main import extract_evaluations_from_state
        import streamlit as st
    except Exception:
        return None

    evals = extract_evaluations_from_state() or []
    results = []
    for e in evals:
        try:
            task_type = (e.get("task") or "text-generation").strip()
            ds_name = e.get("dataset_name") or e.get("dataset")
            ds_type = e.get("dataset_id") or ds_name
            metric_name = e.get("metric_name") or e.get("metric")
            metric_value = e.get("metric_value") or e.get("value")
            if not (ds_name and metric_name and metric_value is not None):
                continue
            results.append(
                {
                    "task": {"type": task_type},
                    "dataset": {"name": ds_name, "type": ds_type},
                    "metrics": [
                        {"name": metric_name, "type": metric_name, "value": metric_value}
                    ],
                }
            )
        except Exception:
            continue

    if not results:
        return None

    return {"model-index": [{"name": model_name, "results": results}]}
# --- Turn-key usage examples --------------------------------------------------
# 1) Just render based on your current UI state and save locally:
# path = save_hf_readme(path="README.md")
#
# 2) Render with explicit overrides (e.g., force library and tags):
# path = save_hf_readme(
#     path="README.md",
#     meta={
#         "library_name": "transformers",
#         "tags": ["my-model", "demo"],
#     },
# )
#
# 3) Upload to the Hub:
# upload_readme_to_hub(
#     repo_id="your-username/your-model",
#     token="hf_...",  # or None if you've done `huggingface-cli login`
#     readme_path="README.md",
# )


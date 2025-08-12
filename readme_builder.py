import io
import yaml

def build_readme_from_card(card: dict) -> str:
    """
    Build a Hugging Face–friendly README.md (YAML front-matter + Markdown body)
    from the structured card object returned by parse_into_json(),
    rendering lists/dicts as bullet points (no JSON code blocks) and
    handling Training Data IO-TS like Evaluations.
    """

    def _nonempty(x):
        if x is None: return False
        if isinstance(x, str): return x.strip() != ""
        if isinstance(x, (list, dict)): return len(x) > 0
        return True

    def _render_list_or_dict(v, indent_level=2):
        """Render a list or dict into bullet points."""
        lines = []
        indent = " " * indent_level
        if isinstance(v, dict):
            for sub_k, sub_v in v.items():
                if sub_k in ("input_content", "source"):  # skip for later
                    continue
                if _nonempty(sub_v):
                    label = sub_k.replace("_", " ").capitalize()
                    lines.append(f"{indent}- {label}: {sub_v}")
        elif isinstance(v, list):
            if all(isinstance(item, dict) for item in v):
                for idx, item in enumerate(v, 1):
                    title = item.get("input_content") or f"Entry {idx}"
                    lines.append(f"{indent}- {title}:")
                    lines.extend(_render_list_or_dict(item, indent_level + 2))
            else:
                pretty_vals = ", ".join(str(x) for x in v)
                lines.append(f"{indent}- {pretty_vals}")
        return lines

    # --------------------
    # 1) YAML front-matter
    # --------------------
    meta = {}
    task = card.get("task")
    if _nonempty(task):
        meta["pipeline_tag"] = str(task).strip().lower().replace(" ", "-")

    mbi = card.get("model_basic_information", {})
    if _nonempty(mbi.get("software_license")):
        meta["license"] = str(mbi["software_license"]).strip()

    yaml_buf = io.StringIO()
    yaml_buf.write("---\n")
    yaml.safe_dump({k: v for k, v in meta.items() if _nonempty(v)}, yaml_buf, sort_keys=False)
    yaml_buf.write("---\n\n")

    # --------------------
    # 2) Markdown body
    # --------------------
    lines = []

    def add_section(title: str, data, field_order=None, skip_keys=None):
        """Add a Markdown section from a dict or list."""
        if not _nonempty(data):
            return
        skip_keys = set(skip_keys or [])
        lines.append(f"## {title}")
        if isinstance(data, dict):
            items = [(k, v) for k, v in data.items() if k not in skip_keys and _nonempty(v)]
            if field_order:
                ordered, seen = [], set()
                for k in field_order:
                    if k in data and k not in skip_keys and _nonempty(data[k]):
                        ordered.append((k, data[k])); seen.add(k)
                for k, v in items:
                    if k not in seen:
                        ordered.append((k, v))
                items = ordered
            for k, v in items:
                label = k.replace("_", " ").capitalize()
                if isinstance(v, (list, dict)):
                    lines.append(f"- **{label}:**")
                    lines.extend(_render_list_or_dict(v, indent_level=2))
                else:
                    lines.append(f"- **{label}:** {v}")
        elif isinstance(data, list):
            for idx, entry in enumerate(data, 1):
                lines.append(f"### {title} {idx}")
                if isinstance(entry, dict):
                    for k, v in entry.items():
                        if _nonempty(v):
                            label = k.replace("_", " ").capitalize()
                            if isinstance(v, (list, dict)):
                                lines.append(f"- **{label}:**")
                                lines.extend(_render_list_or_dict(v, indent_level=2))
                            else:
                                lines.append(f"- **{label}:** {v}")
        lines.append("")

    def add_training_io(training_data: dict):
        """Render inputs_outputs_technical_specifications grouped by source."""
        ios = (training_data or {}).get("inputs_outputs_technical_specifications", [])
        if not _nonempty(ios):
            return
        groups = {
            "model_inputs": {"title": "Model Inputs", "items": []},
            "model_outputs": {"title": "Model Outputs", "items": []},
        }
        for entry in ios:
            src = (entry or {}).get("source")
            if src in groups:
                groups[src]["items"].append(entry)

        lines.append("## Training Data – Inputs/Outputs Technical Specifications")
        for key in ("model_inputs", "model_outputs"):
            grp = groups[key]
            if not grp["items"]:
                continue
            lines.append(f"### {grp['title']}")
            for i, e in enumerate(grp["items"], 1):
                head = e.get("input_content") or f"Entry {i}"
                lines.append(f"- **{head}**")
                lines.extend(_render_list_or_dict(e, indent_level=2))
            lines.append("")

    # Core sections
    add_section("Card Metadata", card.get("card_metadata", {}))
    add_section("Model Basic Information", mbi)
    add_section("Technical Specifications", card.get("technical_specifications", {}))
    add_section("Learning Architectures", card.get("learning_architectures", []))
    add_section("HW and SW", card.get("hw_and_sw", {}))

    # Training Data: primero lo “normal”, excluyendo IO-TS…
    td = card.get("training_data", {}) or {}
    add_section(
        "Training Data",
        td,
        # si quieres forzar orden, añade field_order=[...]
        skip_keys={"inputs_outputs_technical_specifications"}
    )
    # …y luego IO-TS con formato especial
    add_training_io(td)

    # Evaluations
    evaluations = card.get("evaluations", [])
    if _nonempty(evaluations):
        lines.append("## Evaluations")
        for i, ev in enumerate(evaluations, 1):
            lines.append(f"### Evaluation {i}: {ev.get('name','')}")
            for k, v in ev.items():
                if k == "name" or not _nonempty(v):
                    continue
                label = k.replace("_", " ").capitalize()
                if isinstance(v, (list, dict)):
                    lines.append(f"- **{label}:**")
                    lines.extend(_render_list_or_dict(v, indent_level=2))
                else:
                    lines.append(f"- **{label}:** {v}")
            lines.append("")

    # Other considerations
    add_section("Other Considerations", card.get("other_considerations", {}))

    return yaml_buf.getvalue() + "\n".join(lines).rstrip() + "\n"
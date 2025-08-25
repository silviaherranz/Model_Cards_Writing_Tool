"""Validate required fields in the model card schema."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

import streamlit as st

from json_template import (
    DATA_INPUT_OUTPUT_TS,
    EVALUATION_METRIC_FIELDS,
    LEARNING_ARCHITECTURE,
    TASK_METRIC_MAP,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

MissingItem = tuple[str, str]  # (section, human_readable_label)

_EMPTY_SENTINELS: tuple[Any, ...] = ("", None, [], {})


def is_empty(value: object) -> bool:
    """
    Check if a value is considered 'empty'.

    :param value: The value to check.
    :type value: object
    :return: True if the value is empty, False otherwise.
    :rtype: bool
    """
    return value in _EMPTY_SENTINELS


def _has_required_image(full_key: str) -> bool:
    """
    Check if the uploader for `full_key` has a saved image file on disk.

    :param full_key: The full key to check.
    :type full_key: str
    :return: True if the image file exists, False otherwise.
    :rtype: bool
    """
    rec = st.session_state.get("render_uploads", {}).get(full_key)
    if not rec:
        return False
    try:
        path = rec.get("path", "")
        return Path(path).exists()
    except (TypeError, OSError):
        return False


def _label_for(props: dict[str, Any], key: str) -> str:
    """
    Generate a human-readable label for a field key.

    :param props: The properties of the field.
    :type props: dict[str, Any]
    :param key: The key of the field.
    :type key: str
    :return: A human-readable label for the field.
    :rtype: str
    """
    return (props.get("label") or key).replace("_", " ").title()


def _field_required_for_task(
    props: dict[str, Any],
    current_task: str | None,
) -> bool:
    """
    Check if a field is required for the current task.

    :param props: The properties of the field.
    :type props: dict[str, Any]
    :param current_task: The current task being validated.
    :type current_task: str | None
    :return: True if the field is required for the current task, False otherwise.
    :rtype: bool
    """  # noqa: E501
    if not props.get("required", False):
        return False
    model_types = props.get("model_types")
    return model_types is None or (
        current_task and current_task in model_types
    )


def validate_static_fields(
    schema: dict[str, dict[str, dict[str, Any]]],
    current_task: str | None,
) -> list[MissingItem]:
    """
    Validate all regular required fields outside dynamic/iterative structures,
    respecting the original skip rules.

    :param schema: The schema to validate.
    :type schema: dict[str, dict[str, dict[str, Any]]]
    :param current_task: The current task being validated.
    :type current_task: str | None
    :return: A list of missing items.
    :rtype: list[MissingItem]
    """  # noqa: D205
    missing: list[MissingItem] = []

    skip_fields = set(DATA_INPUT_OUTPUT_TS.keys())  # training/eval IO TS keys
    skip_keys = {
        "input_content_rtstruct_subtype",
        "output_content_rtstruct_subtype",
    }
    skip_sections = {
        "evaluation_data_methodology_results_commisioning",
        "learning_architecture",
        "qualitative_evaluation",
    }

    for section, fields in schema.items():
        if section in skip_sections or not isinstance(fields, dict):
            continue

        for key, props in fields.items():
            # Skip some keys or IO-TS keys under certain sections
            if key in skip_keys or (
                key in skip_fields
                and section
                in [
                    "training_data",
                    "evaluation_data_methodology_results_commisioning",
                ]
            ):
                continue

            if not _field_required_for_task(props, current_task):
                continue

            full_key = f"{section}_{key}"
            field_type = (props.get("type") or "").lower()

            if field_type == "image":
                if not _has_required_image(full_key):
                    missing.append((section, _label_for(props, key)))
                continue

            if is_empty(st.session_state.get(full_key)):
                missing.append((section, _label_for(props, key)))

    return missing


def validate_learning_architectures(
    schema: dict[str, dict[str, dict[str, Any]]],
) -> list[MissingItem]:
    """
    Validate the N repeated 'learning architecture' blocks using the keys
    defined in LEARNING_ARCHITECTURE. Keeps label formatting and numbering.

    :param schema: The schema to validate.
    :type schema: dict[str, dict[str, dict[str, Any]]]
    :return: A list of missing items.
    :rtype: list[MissingItem]
    """  # noqa: D205
    missing: list[MissingItem] = []

    forms = st.session_state.get(
        "learning_architecture_forms",
        {},
    )  # dict keyed by index
    schema_fields = schema.get("learning_architecture", {})

    # We rely on how the UI stores these as `learning_architecture_{i}_<field>`
    for i in range(len(forms)):
        prefix = f"learning_architecture_{i}_"

        for field in LEARNING_ARCHITECTURE:
            props = schema_fields.get(field)
            if not props or not props.get("required", False):
                continue

            full_key = f"{prefix}{field}"
            if is_empty(st.session_state.get(full_key)):
                label = props.get("label", field.replace("_", " ").title())
                missing.append(
                    (
                        "learning_architecture",
                        f"{label} (Learning Architecture {i + 1})",
                    ),
                )

    return missing


def _get_modalities_from_state() -> list[tuple[str, str]]:
    """
    Extract (modality, source) pairs from session state based on
    '*model_inputs' and '*model_outputs' lists, preserving original logic.

    :return: A list of (modality, source) tuples.
    :rtype: list[tuple[str, str]]
    """  # noqa: D205
    modalities: list[tuple[str, str]] = []
    for key, value in st.session_state.items():
        if key.endswith("model_inputs") and isinstance(value, list):
            modalities.extend((item, "model_inputs") for item in value)
        elif key.endswith("model_outputs") and isinstance(value, list):
            modalities.extend((item, "model_outputs") for item in value)
    return modalities


def validate_modalities_fields() -> list[MissingItem]:
    """
    Validate the presence of all required fields for each modality.

    :return: A list of missing items.
    :rtype: list[MissingItem]
    """
    missing: list[MissingItem] = []

    for modality, source in _get_modalities_from_state():
        clean = modality.strip().replace(" ", "_").lower()

        # Training block
        prefix_train = f"training_data_{clean}_{source}_"
        for field, label in DATA_INPUT_OUTPUT_TS.items():
            if is_empty(st.session_state.get(f"{prefix_train}{field}")):
                missing.append(
                    ("training_data", f"{label} ({modality} - {source})"),
                )

        # Evaluation blocks
        eval_forms: Sequence[str] = st.session_state.get(
            "evaluation_forms",
            [],
        )
        for name in eval_forms:
            slug = name.replace(" ", "_")
            prefix_eval = f"evaluation_{slug}_{clean}_"
            for field, label in DATA_INPUT_OUTPUT_TS.items():
                full_key = f"{prefix_eval}{source}_{field}"
                if is_empty(st.session_state.get(full_key)):
                    missing.append(
                        (
                            "evaluation_data_methodology_results_commisioning",
                            f"{label} ({modality} - {source})(Eval: {name})",
                        ),
                    )

    return missing


def _validate_metric_group(
    prefix: str,
    slug: str,
    name: str,
    metric_type: str,
    eval_section: dict[str, dict[str, Any]],
    missing: list[MissingItem],
) -> None:
    """
    Validate the presence of all required fields for a specific metric group.

    :param prefix: The prefix for the session state keys.
    :type prefix: str
    :param slug: The slugified name of the evaluation form.
    :type slug: str
    :param name: The original name of the evaluation form.
    :type name: str
    :param metric_type: The type of metric being validated.
    :type metric_type: str
    :param eval_section: The schema section for the evaluation form.
    :type eval_section: dict[str, dict[str, Any]]
    :param missing: The list to append missing items to.
    :type missing: list[MissingItem]
    """
    entry_list: Sequence[str] = st.session_state.get(
        f"{prefix}{metric_type}_list",
        [],
    )
    if not entry_list:
        return

    for metric_name in entry_list:
        metric_short = metric_name.split(" (")[0]  # preserve original display
        metric_prefix = f"evaluation_{slug}.{metric_name}"

        for field_key in EVALUATION_METRIC_FIELDS.get(metric_type, []):
            props = eval_section.get(field_key)
            if not props or not props.get("required", False):
                continue

            full_key = f"{metric_prefix}_{field_key}"
            if is_empty(st.session_state.get(full_key)):
                label = _label_for(props, field_key)
                missing.append(
                    (
                        "evaluation_data_methodology_results_commisioning",
                        f"{label} (Metric: {metric_short}, Eval: {name})",
                    ),
                )


def validate_evaluation_forms(
    schema: dict[str, dict[str, dict[str, Any]]],
    current_task: str | None,
) -> list[MissingItem]:
    """
    Validate the presence of all required fields for each evaluation form.

    :param schema: The schema to validate.
    :type schema: dict[str, dict[str, dict[str, Any]]]
    :param current_task: The current task context.
    :type current_task: str | None
    :return: A list of missing items.
    :rtype: list[MissingItem]
    """
    missing: list[MissingItem] = []

    skip_fields = set(DATA_INPUT_OUTPUT_TS.keys())
    eval_forms: Sequence[str] = st.session_state.get("evaluation_forms", [])
    eval_section = schema.get(
        "evaluation_data_methodology_results_commisioning",
        {},
    )

    # Figure out which metric field groups apply for this task
    metric_types = TASK_METRIC_MAP.get(current_task, [])
    metric_field_keys: set[str] = set()
    for t in metric_types:
        metric_field_keys.update(EVALUATION_METRIC_FIELDS.get(t, []))

    for name in eval_forms:
        slug = name.replace(" ", "_")
        prefix = f"evaluation_{slug}_"
        approved_same = bool(
            st.session_state.get(f"{prefix}evaluated_same_as_approved", False),
        )

        # Validate non-metric fields with early continues to reduce nesting.
        for key, props in eval_section.items():
            if key in metric_field_keys or key in skip_fields:
                continue
            if approved_same and key in {
                "evaluated_by_name",
                "evaluated_by_institution",
                "evaluated_by_contact_email",
            }:
                continue
            if not _field_required_for_task(props, current_task):
                continue
            if is_empty(st.session_state.get(f"{prefix}{key}")):
                missing.append(
                    (
                        "evaluation_data_methodology_results_commisioning",
                        f"{_label_for(props, key)} (Eval: {name})",
                    ),
                )

        # Delegate per-metric validation to helper to keep complexity low.
        for metric_type in metric_types:
            _validate_metric_group(
                prefix,
                slug,
                name,
                metric_type,
                eval_section,
                missing,
            )

    return missing


def validate_required_fields(
    schema: dict[str, dict[str, dict[str, Any]]],
    current_task: str | None = None,
) -> list[MissingItem]:
    """
    Validate required fields in the schema.

    :param schema: The schema to validate.
    :type schema: dict[str, dict[str, dict[str, Any]]]
    :param current_task: The current task context, defaults to None
    :type current_task: str | None, optional
    :return: A list of missing items.
    :rtype: list[MissingItem]
    """
    return (
        validate_static_fields(schema, current_task)
        + validate_learning_architectures(schema)
        + validate_modalities_fields()
        + validate_evaluation_forms(schema, current_task)
    )
